"""
Google Photos OAuth and API client
"""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import httpx
import os
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Google OAuth scopes for Photos
SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary.appendonly',
    'https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


class GoogleOAuthHelper:
    """Helper for Google OAuth flow"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, state: str = None) -> tuple[str, str]:
        """Generate OAuth authorization URL"""
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        auth_url, state = flow.authorization_url(
            access_type='offline',
            prompt='consent',
            state=state,
            include_granted_scopes='false'
        )
        
        return auth_url, state
    
    async def exchange_code(self, code: str) -> Dict[str, str]:
        """Exchange authorization code for tokens"""
        import warnings
        
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        # Suppress scope mismatch warnings (Google may add openid or reorder scopes)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }


class GooglePhotosClient:
    """Client for Google Photos API"""
    
    def __init__(self, refresh_token: str, client_id: str, client_secret: str):
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.credentials = None
        self._initialize_credentials()
    
    def _initialize_credentials(self):
        """Initialize credentials from refresh token"""
        self.credentials = Credentials(
            token=None,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=SCOPES
        )
    
    def _refresh_token_if_needed(self):
        """Refresh access token if expired"""
        if not self.credentials.valid:
            if not self.credentials.token:
                # Force refresh if no token exists
                request = Request()
                self.credentials.refresh(request)
            elif self.credentials.expired:
                # Refresh if token is expired
                request = Request()
                self.credentials.refresh(request)
    
    def get_access_token(self) -> str:
        """Get valid access token"""
        self._refresh_token_if_needed()
        return self.credentials.token
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user info"""
        self._refresh_token_if_needed()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {self.credentials.token}"}
            )
            response.raise_for_status()
            return response.json()
    
    async def list_albums(self) -> List[Dict[str, Any]]:
        """List albums created by this app"""
        self._refresh_token_if_needed()
        
        albums = []
        page_token = None
        
        async with httpx.AsyncClient() as client:
            while True:
                params = {"pageSize": 50}
                if page_token:
                    params["pageToken"] = page_token
                
                response = await client.get(
                    "https://photoslibrary.googleapis.com/v1/albums",
                    headers={"Authorization": f"Bearer {self.credentials.token}"},
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                if "albums" in data:
                    albums.extend(data["albums"])
                
                page_token = data.get("nextPageToken")
                if not page_token:
                    break
        
        return albums
    
    async def create_album(self, title: str) -> Dict[str, Any]:
        """Create a new album"""
        self._refresh_token_if_needed()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://photoslibrary.googleapis.com/v1/albums",
                headers={
                    "Authorization": f"Bearer {self.credentials.token}",
                    "Content-Type": "application/json"
                },
                json={"album": {"title": title}}
            )
            response.raise_for_status()
            return response.json()
    
    async def ensure_album(self, album_name: str) -> str:
        """Get or create album, return album ID"""
        albums = await self.list_albums()
        
        # Look for existing album
        for album in albums:
            if album.get("title") == album_name:
                return album["id"]
        
        # Create new album
        album = await self.create_album(album_name)
        return album["id"]
    
    async def upload_bytes(
        self,
        filename: str,
        content: bytes,
        mime_type: str = "application/octet-stream"
    ) -> str:
        """Upload file bytes and return upload token"""
        self._refresh_token_if_needed()
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                "https://photoslibrary.googleapis.com/v1/uploads",
                headers={
                    "Authorization": f"Bearer {self.credentials.token}",
                    "Content-Type": "application/octet-stream",
                    "X-Goog-Upload-File-Name": filename,
                    "X-Goog-Upload-Protocol": "raw"
                },
                content=content
            )
            response.raise_for_status()
            upload_token = response.text
            return upload_token
    
    async def batch_create(
        self,
        upload_tokens: List[Dict[str, str]],
        album_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Create media items from upload tokens
        
        Args:
            upload_tokens: List of dicts with 'uploadToken', 'fileName', 'description'
            album_id: Optional album ID to add items to
        
        Returns:
            List of created media items
        """
        self._refresh_token_if_needed()
        
        new_media_items = []
        for token_info in upload_tokens:
            item = {
                "simpleMediaItem": {
                    "uploadToken": token_info["uploadToken"],
                    "fileName": token_info.get("fileName", "")
                }
            }
            if token_info.get("description"):
                item["description"] = token_info["description"]
            new_media_items.append(item)
        
        request_body = {"newMediaItems": new_media_items}
        if album_id:
            request_body["albumId"] = album_id
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate",
                headers={
                    "Authorization": f"Bearer {self.credentials.token}",
                    "Content-Type": "application/json"
                },
                json=request_body
            )
            response.raise_for_status()
            result = response.json()
            return result.get("newMediaItemResults", [])
