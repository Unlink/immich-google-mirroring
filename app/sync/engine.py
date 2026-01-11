"""
Sync engine for Immich to Google Photos synchronization
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO

from app.models import AppConfig, SyncItem, SyncRun, SyncStatus, RunStatus, SyncRunLog, SyncRunAction
from app.clients.immich import ImmichClient
from app.clients.google import GooglePhotosClient
from app.utils.config import ConfigManager
from app.utils.encryption import encryption

logger = logging.getLogger(__name__)

# In-memory cancel flags per run. Routes can request cancellation
# and the running engine instance will observe this event.
cancel_events: Dict[int, asyncio.Event] = {}

def request_cancel(run_id: int) -> None:
    """Signal cancellation for a specific sync run."""
    evt = cancel_events.setdefault(run_id, asyncio.Event())
    evt.set()

def clear_cancel(run_id: int) -> None:
    """Clear and remove cancellation signal for a run (cleanup)."""
    evt = cancel_events.pop(run_id, None)
    if evt:
        evt.clear()


class SyncEngine:
    """Engine for synchronizing Immich albums to Google Photos"""
    
    def __init__(self, db: AsyncSession, run_id: int):
        self.db = db
        self.run_id = run_id
        self.run: Optional[SyncRun] = None
        self.config: Optional[AppConfig] = None
        self.immich_client: Optional[ImmichClient] = None
        self.google_client: Optional[GooglePhotosClient] = None
        self.log_messages = []
        # Cancellation event associated with this run
        self.cancel_event = cancel_events.setdefault(run_id, asyncio.Event())
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"
        self.log_messages.append(log_line)
        
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)
    
    async def initialize(self) -> bool:
        """Initialize sync run and clients"""
        try:
            # Get run record
            result = await self.db.execute(select(SyncRun).where(SyncRun.id == self.run_id))
            self.run = result.scalar_one_or_none()
            
            if not self.run:
                logger.error(f"Sync run {self.run_id} not found")
                return False
            
            # Get config
            self.config = await ConfigManager.get_config(self.db)
            
            if not self.config.immich_url or not self.config.immich_api_key_enc:
                self.log("Immich not configured", "ERROR")
                return False
            
            if not self.config.immich_album_id:
                self.log("No Immich album selected", "ERROR")
                return False
            
            if not self.config.google_refresh_token_enc:
                self.log("Google Photos not authenticated", "ERROR")
                return False
            
            # Initialize clients
            immich_api_key = ConfigManager.get_immich_api_key(self.config)
            self.immich_client = ImmichClient(self.config.immich_url, immich_api_key)
            
            google_refresh_token = ConfigManager.get_google_refresh_token(self.config)
            
            # Get Google client credentials from config or env
            google_client_id = self.config.google_client_id or os.getenv("GOOGLE_CLIENT_ID")
            google_client_secret = ConfigManager.get_google_client_secret(self.config) or os.getenv("GOOGLE_CLIENT_SECRET")
            
            if not google_client_id or not google_client_secret:
                self.log("Google OAuth client credentials not configured", "ERROR")
                return False
            
            self.google_client = GooglePhotosClient(
                google_refresh_token,
                google_client_id,
                google_client_secret
            )
            
            self.log(f"Initialized sync for album: {self.config.immich_album_name}")
            return True
            
        except Exception as e:
            self.log(f"Initialization failed: {e}", "ERROR")
            return False
    
    async def ensure_google_album(self) -> Optional[str]:
        """Ensure Google Photos album exists"""
        try:
            if self.config.google_album_id:
                self.log(f"Using existing Google album: {self.config.google_album_name}")
                return self.config.google_album_id
            
            # Create album with same name as Immich album
            album_name = f"Immich - {self.config.immich_album_name}"
            self.log(f"Creating Google Photos album: {album_name}")
            
            album_id = await self.google_client.ensure_album(album_name)
            
            # Save to config
            await ConfigManager.update_google_album(self.db, album_id, album_name)
            self.config.google_album_id = album_id
            self.config.google_album_name = album_name
            
            self.log(f"Google album created: {album_id}")
            return album_id
            
        except Exception as e:
            self.log(f"Failed to ensure Google album: {e}", "ERROR")
            return None
    
    async def sync_asset(self, asset: Dict[str, Any]) -> bool:
        """Sync a single asset"""
        asset_id = asset["id"]
        filename = asset["originalFileName"]
        
        try:
            # Check if already synced
            result = await self.db.execute(
                select(SyncItem).where(SyncItem.immich_asset_id == asset_id)
            )
            sync_item = result.scalar_one_or_none()
            
            # Create fingerprint
            fingerprint = asset.get("checksum") or f"{asset.get('updatedAt', '')}_{filename}"
            
            if sync_item:
                # Check if changed
                if sync_item.immich_checksum == fingerprint and sync_item.status == SyncStatus.OK:
                    self.log(f"Skipping unchanged: {filename}")
                    self.run.skipped += 1
                    
                    # Log skipped action
                    log_entry = SyncRunLog(
                        sync_run_id=self.run_id,
                        action=SyncRunAction.SKIPPED,
                        immich_asset_id=asset_id,
                        immich_filename=filename,
                        google_media_item_id=sync_item.google_media_item_id
                    )
                    self.db.add(log_entry)
                    
                    return True
            
            # Download from Immich
            self.log(f"Downloading: {filename}")
            content = BytesIO()
            async for chunk in self.immich_client.download_original(asset_id):
                content.write(chunk)
            
            content_bytes = content.getvalue()
            self.log(f"Downloaded {len(content_bytes)} bytes")
            
            # Upload to Google Photos
            self.log(f"Uploading to Google Photos: {filename}")
            upload_token = await self.google_client.upload_bytes(
                filename,
                content_bytes
            )
            
            # Create media item
            results = await self.google_client.batch_create(
                [{"uploadToken": upload_token, "fileName": filename}],
                self.config.google_album_id
            )
            
            if not results or not results[0].get("mediaItem"):
                raise Exception("Failed to create media item")
            
            media_item = results[0]["mediaItem"]
            media_item_id = media_item["id"]
            product_url = media_item.get("productUrl", "")
            
            self.log(f"Created media item: {media_item_id}")
            
            # Update sync item
            if not sync_item:
                sync_item = SyncItem(immich_asset_id=asset_id)
                self.db.add(sync_item)
            
            sync_item.immich_checksum = fingerprint
            sync_item.immich_updated_at = asset.get("updatedAt", "")
            sync_item.immich_filename = filename
            sync_item.google_media_item_id = media_item_id
            sync_item.google_product_url = product_url
            sync_item.status = SyncStatus.OK
            sync_item.error = None
            sync_item.last_synced_at = datetime.utcnow()
            
            await self.db.commit()
            
            # Log uploaded action
            log_entry = SyncRunLog(
                sync_run_id=self.run_id,
                action=SyncRunAction.UPLOADED,
                immich_asset_id=asset_id,
                immich_filename=filename,
                google_media_item_id=media_item_id
            )
            self.db.add(log_entry)
            await self.db.commit()
            
            self.run.uploaded += 1
            return True
            
        except Exception as e:
            self.log(f"Failed to sync {filename}: {e}", "ERROR")
            
            # Log failed action
            log_entry = SyncRunLog(
                sync_run_id=self.run_id,
                action=SyncRunAction.FAILED,
                immich_asset_id=asset_id,
                immich_filename=filename,
                error_message=str(e)
            )
            self.db.add(log_entry)
            
            # Update sync item with error
            if not sync_item:
                sync_item = SyncItem(immich_asset_id=asset_id)
                self.db.add(sync_item)
            
            sync_item.immich_filename = filename
            sync_item.status = SyncStatus.FAILED
            sync_item.error = str(e)
            
            await self.db.commit()
            
            self.run.failed += 1
            return False
    
    async def delete_orphaned_assets(self, current_immich_assets: List[Dict[str, Any]]) -> None:
        """
        Delete assets from Google Photos that no longer exist in Immich album
        
        Args:
            current_immich_assets: List of current assets from Immich album
        """
        try:
            # Check for cancel request
            if self.cancel_event.is_set():
                self.log("Cancellation requested; skipping orphan deletion")
                return
            
            self.log("Checking for orphaned assets in Google Photos...")
            
            # Get all media items from Google Photos album
            google_media_items = await self.google_client.list_album_media_items(
                self.config.google_album_id
            )
            
            if not google_media_items:
                self.log("No media items found in Google Photos album")
                return
            
            # Create set of current Immich asset IDs
            current_immich_ids = {asset["id"] for asset in current_immich_assets}
            
            # Find orphaned items (in Google but not in Immich)
            orphaned_items = []
            
            # Get all sync items from database
            result = await self.db.execute(select(SyncItem))
            sync_items = result.scalars().all()
            
            # Create mapping of google_media_item_id -> sync_item
            google_to_sync = {
                item.google_media_item_id: item 
                for item in sync_items 
                if item.google_media_item_id
            }
            
            # Identify orphaned items
            for google_item in google_media_items:
                google_id = google_item["id"]
                
                # Find corresponding sync item
                sync_item = google_to_sync.get(google_id)
                
                if sync_item:
                    # Check if the Immich asset still exists in the album
                    if sync_item.immich_asset_id not in current_immich_ids:
                        orphaned_items.append({
                            "google_id": google_id,
                            "sync_item": sync_item,
                            "filename": sync_item.immich_filename or "unknown"
                        })
                else:
                    # Media item in Google Photos but no sync record
                    # This could be a photo that was uploaded manually or from another source
                    # Only mark as orphan if we have a risk of deleting user photos
                    # For safety, we skip items without sync records
                    self.log(f"Skipping media item without sync record: {google_id}", "DEBUG")
            
            if not orphaned_items:
                self.log("No orphaned assets found")
                return
            
            self.log(f"Found {len(orphaned_items)} orphaned asset(s) to delete")
            
            # Delete orphaned items from Google Photos album
            google_ids_to_delete = [item["google_id"] for item in orphaned_items]
            
            self.log(f"Removing {len(google_ids_to_delete)} orphaned asset(s) from Google Photos album...")
            
            result = await self.google_client.delete_media_items(
                google_ids_to_delete,
                self.config.google_album_id
            )
            
            self.log(f"Removed {result['deleted']} asset(s) from album, {result['failed']} failed")
            
            if result["errors"]:
                for error in result["errors"][:10]:  # Log first 10 errors
                    self.log(f"Removal error: {error}", "WARNING")
            
            # Update sync items in database
            for orphan in orphaned_items:
                sync_item = orphan["sync_item"]
                google_id = orphan["google_id"]
                
                # Check if removal was successful
                was_removed = google_id not in [
                    err.split(":")[0].replace("Item ", "").strip() 
                    for err in result.get("errors", [])
                ]
                
                if was_removed:
                    # Log deleted action
                    log_entry = SyncRunLog(
                        sync_run_id=self.run_id,
                        action=SyncRunAction.DELETED,
                        immich_asset_id=sync_item.immich_asset_id,
                        immich_filename=orphan["filename"],
                        google_media_item_id=google_id
                    )
                    self.db.add(log_entry)
                    
                    # Remove the sync item from database
                    await self.db.delete(sync_item)
                    self.run.deleted += 1
                else:
                    # Mark as orphaned but keep the record
                    sync_item.status = SyncStatus.ORPHANED
                    sync_item.error = "Failed to remove from Google Photos album"
            
            await self.db.commit()
            
        except Exception as e:
            self.log(f"Error during orphan deletion: {e}", "ERROR")
            # Don't fail the entire sync if orphan deletion fails
    
    async def run_sync(self) -> bool:
        """Execute the sync process"""
        try:
            # Initialize first to ensure self.run is loaded
            if not await self.initialize():
                # If run couldn't be loaded or initialization failed, guard against None
                if self.run:
                    self.run.status = RunStatus.FAILED
                    self.run.finished_at = datetime.utcnow()
                    self.run.log_excerpt = "\n".join(self.log_messages[-50:])
                    await self.db.commit()
                return False

            # Mark as running only after successful initialization
            self.run.status = RunStatus.RUNNING
            await self.db.commit()
            
            # Early cancellation check
            if self.cancel_event.is_set():
                self.log("Cancellation requested before start")
                self.run.status = RunStatus.CANCELLED
                self.run.finished_at = datetime.utcnow()
                self.run.log_excerpt = "\n".join(self.log_messages[-50:])
                await self.db.commit()
                return False
            
            # Ensure Google album
            google_album_id = await self.ensure_google_album()
            if not google_album_id:
                self.run.status = RunStatus.FAILED
                await self.db.commit()
                return False
            
            # Get Immich assets
            self.log("Fetching assets from Immich...")
            assets = await self.immich_client.get_album_assets(self.config.immich_album_id)
            
            self.run.total_assets = len(assets)
            await self.db.commit()
            
            self.log(f"Found {len(assets)} assets in Immich album")
            
            # Sync each asset
            for i, asset in enumerate(assets, 1):
                # Check for cancel request on each iteration
                if self.cancel_event.is_set():
                    self.log("Cancellation requested; stopping sync")
                    self.run.status = RunStatus.CANCELLED
                    self.run.finished_at = datetime.utcnow()
                    self.run.log_excerpt = "\n".join(self.log_messages[-50:])
                    await self.db.commit()
                    return False
                self.log(f"Processing asset {i}/{len(assets)}: {asset['originalFileName']}")
                await self.sync_asset(asset)
                
                # Update run progress
                await self.db.commit()
            
            # Delete orphaned assets (exist in Google Photos but not in Immich)
            await self.delete_orphaned_assets(assets)
            
            # Mark run as complete
            self.run.status = RunStatus.OK
            self.run.finished_at = datetime.utcnow()
            self.run.log_excerpt = "\n".join(self.log_messages[-50:])  # Last 50 lines
            
            await self.db.commit()
            
            self.log(f"Sync completed: {self.run.uploaded} uploaded, {self.run.skipped} skipped, {self.run.failed} failed, {self.run.deleted} deleted")
            return True
            
        except Exception as e:
            self.log(f"Sync failed: {e}", "ERROR")
            if self.run:
                self.run.status = RunStatus.FAILED
                self.run.finished_at = datetime.utcnow()
                self.run.log_excerpt = "\n".join(self.log_messages[-50:])
                await self.db.commit()
            return False
        finally:
            # Cleanup cancel flag for this run
            clear_cancel(self.run_id)


async def create_and_run_sync(db: AsyncSession) -> int:
    """Create a new sync run and execute it"""
    # Create run record
    run = SyncRun()
    db.add(run)
    await db.commit()
    await db.refresh(run)
    
    # Execute sync
    engine = SyncEngine(db, run.id)
    await engine.run_sync()
    
    return run.id
