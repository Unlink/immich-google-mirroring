"""
API routes for Google OAuth
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
import secrets

from app.database import get_db
from app.utils.config import ConfigManager
from app.clients.google import GoogleOAuthHelper, GooglePhotosClient

router = APIRouter(prefix="/auth/google", tags=["auth"])

# Store state temporarily (in production use Redis/DB)
_oauth_states = {}


def get_oauth_helper() -> GoogleOAuthHelper:
    """Get OAuth helper instance"""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    base_url = os.getenv("BASE_URL", "http://localhost:8080")
    redirect_uri = f"{base_url}/auth/google/callback"
    
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"
        )
    
    return GoogleOAuthHelper(client_id, client_secret, redirect_uri)


@router.get("/start")
async def start_oauth():
    """Start Google OAuth flow"""
    helper = get_oauth_helper()
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = True
    
    auth_url, _ = helper.get_authorization_url(state)
    
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def oauth_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db)
):
    """Handle OAuth callback"""
    # Verify state
    if state not in _oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    del _oauth_states[state]
    
    # Exchange code for tokens
    helper = get_oauth_helper()
    tokens = await helper.exchange_code(code)
    
    if not tokens.get("refresh_token"):
        raise HTTPException(
            status_code=400,
            detail="No refresh token received. Try disconnecting and reconnecting."
        )
    
    # Save refresh token
    await ConfigManager.update_google_token(db, tokens["refresh_token"])
    
    # Redirect to success page
    return RedirectResponse(url="/?auth_success=1")


@router.get("/status")
async def get_auth_status(db: AsyncSession = Depends(get_db)):
    """Get Google authentication status"""
    config = await ConfigManager.get_config(db)
    
    if not config.google_refresh_token_enc:
        return {
            "authenticated": False
        }
    
    try:
        # Try to get user info
        refresh_token = ConfigManager.get_google_refresh_token(config)
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        
        client = GooglePhotosClient(refresh_token, client_id, client_secret)
        user_info = await client.get_user_info()
        
        return {
            "authenticated": True,
            "email": user_info.get("email"),
            "name": user_info.get("name")
        }
    except Exception as e:
        return {
            "authenticated": False,
            "error": str(e)
        }


@router.post("/disconnect")
async def disconnect_google(db: AsyncSession = Depends(get_db)):
    """Disconnect Google account"""
    config = await ConfigManager.get_config(db)
    config.google_refresh_token_enc = None
    config.google_album_id = None
    config.google_album_name = None
    await db.commit()
    
    return {"success": True}
