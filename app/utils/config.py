"""
Configuration manager for app settings
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AppConfig
from app.utils.encryption import encryption
from typing import Optional


class ConfigManager:
    """Manage application configuration"""
    
    @staticmethod
    async def get_config(db: AsyncSession) -> Optional[AppConfig]:
        """Get or create app config"""
        result = await db.execute(select(AppConfig).where(AppConfig.id == 1))
        config = result.scalar_one_or_none()
        
        if not config:
            config = AppConfig(id=1)
            db.add(config)
            await db.commit()
            await db.refresh(config)
        
        return config
    
    @staticmethod
    async def update_immich_config(
        db: AsyncSession,
        immich_url: str,
        immich_api_key: str
    ) -> AppConfig:
        """Update Immich configuration"""
        config = await ConfigManager.get_config(db)
        config.immich_url = immich_url.rstrip('/')
        config.immich_api_key_enc = encryption.encrypt(immich_api_key)
        await db.commit()
        await db.refresh(config)
        return config
    
    @staticmethod
    async def update_album(
        db: AsyncSession,
        album_id: str,
        album_name: str
    ) -> AppConfig:
        """Update selected Immich album"""
        config = await ConfigManager.get_config(db)
        config.immich_album_id = album_id
        config.immich_album_name = album_name
        await db.commit()
        await db.refresh(config)
        return config
    
    @staticmethod
    async def update_google_token(
        db: AsyncSession,
        refresh_token: str
    ) -> AppConfig:
        """Update Google refresh token"""
        config = await ConfigManager.get_config(db)
        config.google_refresh_token_enc = encryption.encrypt(refresh_token)
        await db.commit()
        await db.refresh(config)
        return config
    
    @staticmethod
    async def update_google_album(
        db: AsyncSession,
        album_id: str,
        album_name: str
    ) -> AppConfig:
        """Update Google Photos album"""
        config = await ConfigManager.get_config(db)
        config.google_album_id = album_id
        config.google_album_name = album_name
        await db.commit()
        await db.refresh(config)
        return config
    
    @staticmethod
    async def update_sync_settings(
        db: AsyncSession,
        enabled: bool,
        interval_minutes: int = None
    ) -> AppConfig:
        """Update sync schedule settings"""
        config = await ConfigManager.get_config(db)
        config.sync_enabled = enabled
        if interval_minutes is not None:
            config.sync_interval_minutes = interval_minutes
        await db.commit()
        await db.refresh(config)
        return config
    
    @staticmethod
    def get_immich_api_key(config: AppConfig) -> str:
        """Decrypt and return Immich API key"""
        if not config.immich_api_key_enc:
            return ""
        return encryption.decrypt(config.immich_api_key_enc)
    
    @staticmethod
    def get_google_refresh_token(config: AppConfig) -> str:
        """Decrypt and return Google refresh token"""
        if not config.google_refresh_token_enc:
            return ""
        return encryption.decrypt(config.google_refresh_token_enc)
    
    @staticmethod
    def get_google_client_secret(config: AppConfig) -> str:
        """Decrypt and return Google client secret"""
        if not config.google_client_secret_enc:
            return ""
        return encryption.decrypt(config.google_client_secret_enc)
