"""
API routes for configuration management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.utils.config import ConfigManager
from app.clients.immich import ImmichClient

router = APIRouter(prefix="/api/config", tags=["config"])


class ImmichConfigRequest(BaseModel):
    immich_url: str
    immich_api_key: str


class AlbumSelectRequest(BaseModel):
    album_id: str
    album_name: str


class SyncSettingsRequest(BaseModel):
    enabled: bool
    interval_minutes: Optional[int] = None


@router.post("/immich")
async def update_immich_config(
    request: ImmichConfigRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update Immich configuration"""
    config = await ConfigManager.update_immich_config(
        db,
        request.immich_url,
        request.immich_api_key
    )
    
    return {
        "success": True,
        "immich_url": config.immich_url
    }


@router.post("/immich/test")
async def test_immich_connection(
    request: ImmichConfigRequest,
    db: AsyncSession = Depends(get_db)
):
    """Test Immich connection"""
    client = ImmichClient(request.immich_url, request.immich_api_key)
    result = await client.test_connection()
    return result


@router.post("/album")
async def select_album(
    request: AlbumSelectRequest,
    db: AsyncSession = Depends(get_db)
):
    """Select Immich album to sync"""
    config = await ConfigManager.update_album(
        db,
        request.album_id,
        request.album_name
    )
    
    return {
        "success": True,
        "album_id": config.immich_album_id,
        "album_name": config.immich_album_name
    }


@router.post("/sync")
async def update_sync_settings(
    request: SyncSettingsRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update sync schedule settings"""
    config = await ConfigManager.update_sync_settings(
        db,
        request.enabled,
        request.interval_minutes
    )
    
    return {
        "success": True,
        "sync_enabled": config.sync_enabled,
        "sync_interval_minutes": config.sync_interval_minutes
    }


@router.get("/status")
async def get_config_status(db: AsyncSession = Depends(get_db)):
    """Get configuration status"""
    config = await ConfigManager.get_config(db)
    
    return {
        "immich_configured": bool(config.immich_url and config.immich_api_key_enc),
        "immich_url": config.immich_url,
        "album_selected": bool(config.immich_album_id),
        "album_name": config.immich_album_name,
        "google_authenticated": bool(config.google_refresh_token_enc),
        "google_album_id": config.google_album_id,
        "google_album_name": config.google_album_name,
        "sync_enabled": config.sync_enabled,
        "sync_interval_minutes": config.sync_interval_minutes
    }
