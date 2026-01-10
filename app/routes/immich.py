"""
API routes for Immich operations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.utils.config import ConfigManager
from app.clients.immich import ImmichClient

router = APIRouter(prefix="/api/immich", tags=["immich"])


@router.get("/albums")
async def list_albums(db: AsyncSession = Depends(get_db)):
    """List Immich albums"""
    config = await ConfigManager.get_config(db)
    
    if not config.immich_url or not config.immich_api_key_enc:
        raise HTTPException(status_code=400, detail="Immich not configured")
    
    api_key = ConfigManager.get_immich_api_key(config)
    client = ImmichClient(config.immich_url, api_key)
    
    try:
        albums = await client.list_albums()
        return {"albums": albums}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
