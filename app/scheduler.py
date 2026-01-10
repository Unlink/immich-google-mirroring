"""
Background job scheduler
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.models import AppConfig, SyncRun, RunStatus
from app.database import async_session_maker

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
current_job = None


async def scheduled_sync_job():
    """Job that runs on schedule"""
    logger.info("Running scheduled sync job")
    
    async with async_session_maker() as db:
        try:
            # Get config
            result = await db.execute(select(AppConfig).where(AppConfig.id == 1))
            config = result.scalar_one_or_none()
            
            if not config or not config.sync_enabled:
                logger.info("Sync not enabled, skipping")
                return
            
            # Check if already running
            result = await db.execute(
                select(SyncRun)
                .where(SyncRun.status == RunStatus.RUNNING)
                .limit(1)
            )
            running = result.scalar_one_or_none()
            
            if running:
                logger.warning("Sync already running, skipping")
                return
            
            # Run sync
            from app.sync.engine import SyncEngine
            
            run = SyncRun()
            db.add(run)
            await db.commit()
            await db.refresh(run)
            
            engine = SyncEngine(db, run.id)
            await engine.run_sync()
            
            logger.info(f"Scheduled sync completed: run_id={run.id}")
            
        except Exception as e:
            logger.error(f"Scheduled sync failed: {e}", exc_info=True)


async def update_scheduler():
    """Update scheduler based on current config"""
    global current_job
    
    async with async_session_maker() as db:
        try:
            result = await db.execute(select(AppConfig).where(AppConfig.id == 1))
            config = result.scalar_one_or_none()
            
            # Remove existing job
            if current_job:
                try:
                    scheduler.remove_job(current_job.id)
                    current_job = None
                    logger.info("Removed existing scheduled job")
                except:
                    pass
            
            # Add new job if enabled
            if config and config.sync_enabled and config.sync_interval_minutes > 0:
                current_job = scheduler.add_job(
                    scheduled_sync_job,
                    trigger=IntervalTrigger(minutes=config.sync_interval_minutes),
                    id='sync_job',
                    replace_existing=True,
                    max_instances=1
                )
                logger.info(f"Scheduled sync job every {config.sync_interval_minutes} minutes")
            else:
                logger.info("Sync scheduling disabled")
                
        except Exception as e:
            logger.error(f"Failed to update scheduler: {e}")


def start_scheduler():
    """Start the background scheduler"""
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
