"""
Immich API client
"""
import httpx
from typing import List, Dict, Any, AsyncIterator
import logging

logger = logging.getLogger(__name__)


class ImmichClient:
    """Client for Immich API"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "x-api-key": api_key,
            "Accept": "application/json"
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Immich server"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/server/ping",
                    headers=self.headers
                )
                response.raise_for_status()
                
                # Try to get user info
                user_response = await client.get(
                    f"{self.base_url}/api/users/me",
                    headers=self.headers
                )
                user_response.raise_for_status()
                user_data = user_response.json()
                
                return {
                    "success": True,
                    "user": user_data.get("email", user_data.get("name", "Unknown")),
                    "server": "Immich"
                }
            except httpx.HTTPStatusError as e:
                logger.error(f"Immich connection failed: {e}")
                return {
                    "success": False,
                    "error": f"HTTP {e.response.status_code}: {e.response.text}"
                }
            except Exception as e:
                logger.error(f"Immich connection error: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def list_albums(self) -> List[Dict[str, Any]]:
        """List all albums"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/albums",
                    headers=self.headers
                )
                response.raise_for_status()
                albums = response.json()
                
                # Format album data
                return [
                    {
                        "id": album["id"],
                        "name": album.get("albumName", "Untitled"),
                        "assetCount": album.get("assetCount", 0),
                        "description": album.get("description", "")
                    }
                    for album in albums
                ]
            except Exception as e:
                logger.error(f"Failed to list albums: {e}")
                raise
    
    async def get_album_assets(self, album_id: str) -> List[Dict[str, Any]]:
        """Get all assets in an album"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/albums/{album_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                album_data = response.json()
                
                assets = album_data.get("assets", [])
                
                # Format asset data
                return [
                    {
                        "id": asset["id"],
                        "type": asset.get("type", "IMAGE"),
                        "originalFileName": asset.get("originalFileName", "unknown"),
                        "fileCreatedAt": asset.get("fileCreatedAt"),
                        "fileModifiedAt": asset.get("fileModifiedAt"),
                        "updatedAt": asset.get("updatedAt"),
                        "checksum": asset.get("checksum"),
                        "exifInfo": asset.get("exifInfo", {}),
                    }
                    for asset in assets
                ]
            except Exception as e:
                logger.error(f"Failed to get album assets: {e}")
                raise
    
    async def download_original(self, asset_id: str) -> AsyncIterator[bytes]:
        """Download original asset as streaming bytes"""
        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                async with client.stream(
                    "GET",
                    f"{self.base_url}/api/assets/{asset_id}/original",
                    headers=self.headers
                ) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        yield chunk
            except Exception as e:
                logger.error(f"Failed to download asset {asset_id}: {e}")
                raise
    
    async def get_asset_info(self, asset_id: str) -> Dict[str, Any]:
        """Get detailed asset information"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/assets/{asset_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Failed to get asset info: {e}")
                raise
