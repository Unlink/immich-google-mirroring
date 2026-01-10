"""
API routes for sync operations
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models import SyncRun, SyncItem, RunStatus
from app.sync.engine import create_and_run_sync
from app.utils.config import ConfigManager

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/run")
async def trigger_sync(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Trigger a sync run"""
    # Check if sync is already running
    result = await db.execute(
        select(SyncRun)
        .where(SyncRun.status == RunStatus.RUNNING)
        .order_by(desc(SyncRun.started_at))
        .limit(1)
    )
    running = result.scalar_one_or_none()
    
    if running:
        raise HTTPException(status_code=409, detail="Sync already running")
    
    # Create and run sync in background
    run = SyncRun()
    db.add(run)
    await db.commit()
    await db.refresh(run)
    
    # Run sync in background
    from app.sync.engine import SyncEngine
    
    async def run_sync_task():
        async for session in get_db():
            engine = SyncEngine(session, run.id)
            await engine.run_sync()
            break
    
    background_tasks.add_task(run_sync_task)
    
    return {
        "success": True,
        "run_id": run.id,
        "message": "Sync started"
    }


@router.get("/runs")
async def get_sync_runs(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get recent sync runs"""
    result = await db.execute(
        select(SyncRun)
        .order_by(desc(SyncRun.started_at))
        .limit(limit)
    )
    runs = result.scalars().all()
    
    return [
        {
            "id": run.id,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            "status": run.status.value,
            "total_assets": run.total_assets,
            "uploaded": run.uploaded,
            "skipped": run.skipped,
            "failed": run.failed,
            "duration_seconds": (
                (run.finished_at - run.started_at).total_seconds()
                if run.finished_at and run.started_at
                else None
            )
        }
        for run in runs
    ]


@router.get("/runs/{run_id}")
async def get_sync_run(
    run_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed info about a sync run"""
    result = await db.execute(
        select(SyncRun).where(SyncRun.id == run_id)
    )
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return {
        "id": run.id,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
        "status": run.status.value,
        "total_assets": run.total_assets,
        "uploaded": run.uploaded,
        "skipped": run.skipped,
        "failed": run.failed,
        "log_excerpt": run.log_excerpt,
        "log_path": run.log_path
    }


@router.get("/status")
async def get_sync_status(db: AsyncSession = Depends(get_db)):
    """Get current sync status"""
    # Get last run
    result = await db.execute(
        select(SyncRun)
        .order_by(desc(SyncRun.started_at))
        .limit(1)
    )
    last_run = result.scalar_one_or_none()
    
    # Get config
    config = await ConfigManager.get_config(db)
    
    # Get stats
    total_result = await db.execute(select(SyncItem))
    total_items = len(total_result.scalars().all())
    
    synced_result = await db.execute(
        select(SyncItem).where(SyncItem.status == "OK")
    )
    synced_items = len(synced_result.scalars().all())
    
    return {
        "sync_enabled": config.sync_enabled,
        "sync_interval_minutes": config.sync_interval_minutes,
        "last_run": {
            "id": last_run.id,
            "started_at": last_run.started_at.isoformat() if last_run.started_at else None,
            "finished_at": last_run.finished_at.isoformat() if last_run.finished_at else None,
            "status": last_run.status.value,
            "total_assets": last_run.total_assets,
            "uploaded": last_run.uploaded,
            "skipped": last_run.skipped,
            "failed": last_run.failed
        } if last_run else None,
        "total_items": total_items,
        "synced_items": synced_items
    }


@router.get("/items")
async def get_sync_items(
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get sync items"""
    result = await db.execute(
        select(SyncItem)
        .order_by(desc(SyncItem.last_synced_at))
        .limit(limit)
    )
    items = result.scalars().all()
    
    return [
        {
            "immich_asset_id": item.immich_asset_id,
            "filename": item.immich_filename,
            "status": item.status.value,
            "google_media_item_id": item.google_media_item_id,
            "last_synced_at": item.last_synced_at.isoformat() if item.last_synced_at else None,
            "error": item.error
        }
        for item in items
    ]
