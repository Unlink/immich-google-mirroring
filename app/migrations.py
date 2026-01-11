"""
Database migration utilities
"""
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def migrate_database(db: AsyncSession) -> None:
    """
    Apply database migrations for schema changes
    """
    try:
        # Migration: Add 'deleted' column to sync_runs table if it doesn't exist
        await migrate_add_deleted_column(db)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


async def migrate_add_deleted_column(db: AsyncSession) -> None:
    """
    Add 'deleted' column to sync_runs table if it doesn't exist
    """
    try:
        # Check if column exists
        result = await db.execute(text("PRAGMA table_info(sync_runs)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'deleted' not in columns:
            logger.info("Adding 'deleted' column to sync_runs table")
            await db.execute(text("ALTER TABLE sync_runs ADD COLUMN deleted INTEGER DEFAULT 0"))
            await db.commit()
            logger.info("Successfully added 'deleted' column")
        else:
            logger.debug("'deleted' column already exists in sync_runs table")
    except Exception as e:
        logger.error(f"Failed to add 'deleted' column: {e}")
        raise
