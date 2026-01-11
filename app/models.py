"""
Database models for Immich-Google Photos sync application
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class AppConfig(Base):
    """Application configuration and credentials"""
    __tablename__ = 'app_config'
    
    id = Column(Integer, primary_key=True, default=1)
    immich_url = Column(String(500))
    immich_api_key_enc = Column(Text)
    immich_album_id = Column(String(100))
    immich_album_name = Column(String(500))
    google_album_id = Column(String(200))
    google_album_name = Column(String(500))
    google_refresh_token_enc = Column(Text)
    google_client_id = Column(String(500))
    google_client_secret_enc = Column(Text)
    sync_enabled = Column(Boolean, default=False)
    sync_interval_minutes = Column(Integer, default=60)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SyncStatus(str, enum.Enum):
    """Sync item status"""
    PENDING = "PENDING"
    OK = "OK"
    FAILED = "FAILED"
    ORPHANED = "ORPHANED"


class SyncItem(Base):
    """Individual asset sync tracking"""
    __tablename__ = 'sync_items'
    
    immich_asset_id = Column(String(100), primary_key=True)
    immich_checksum = Column(String(100))
    immich_updated_at = Column(String(50))
    immich_filename = Column(String(500))
    immich_file_size = Column(Integer)
    google_media_item_id = Column(String(200))
    google_product_url = Column(Text)
    status = Column(Enum(SyncStatus), default=SyncStatus.PENDING)
    error = Column(Text)
    last_synced_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class RunStatus(str, enum.Enum):
    """Sync run status"""
    RUNNING = "RUNNING"
    OK = "OK"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class SyncRun(Base):
    """Sync execution history"""
    __tablename__ = 'sync_runs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)
    status = Column(Enum(RunStatus), default=RunStatus.RUNNING)
    total_assets = Column(Integer, default=0)
    uploaded = Column(Integer, default=0)
    skipped = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    deleted = Column(Integer, default=0)
    log_excerpt = Column(Text)
    log_path = Column(String(500))
