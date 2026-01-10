"""
Web UI routes (server-rendered pages)
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import SyncRun, SyncItem
from app.utils.config import ConfigManager
import os

router = APIRouter(tags=["pages"])

# Setup templates
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    """Main dashboard"""
    config = await ConfigManager.get_config(db)
    
    # Get last run
    result = await db.execute(
        select(SyncRun).order_by(desc(SyncRun.started_at)).limit(1)
    )
    last_run = result.scalar_one_or_none()
    
    # Get stats
    total_result = await db.execute(select(SyncItem))
    total_items = len(total_result.scalars().all())
    
    synced_result = await db.execute(
        select(SyncItem).where(SyncItem.status == "OK")
    )
    synced_items = len(synced_result.scalars().all())
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "config": config,
        "last_run": last_run,
        "total_items": total_items,
        "synced_items": synced_items
    })


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Settings page"""
    config = await ConfigManager.get_config(db)
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "config": config
    })


@router.get("/albums", response_class=HTMLResponse)
async def albums_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Album selection page"""
    config = await ConfigManager.get_config(db)
    
    return templates.TemplateResponse("albums.html", {
        "request": request,
        "config": config
    })


@router.get("/google", response_class=HTMLResponse)
async def google_auth_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Google authentication page"""
    config = await ConfigManager.get_config(db)
    
    return templates.TemplateResponse("google.html", {
        "request": request,
        "config": config
    })


@router.get("/sync", response_class=HTMLResponse)
async def sync_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Sync control page"""
    config = await ConfigManager.get_config(db)
    
    # Get recent runs
    result = await db.execute(
        select(SyncRun).order_by(desc(SyncRun.started_at)).limit(10)
    )
    runs = result.scalars().all()
    
    return templates.TemplateResponse("sync.html", {
        "request": request,
        "config": config,
        "runs": runs
    })
