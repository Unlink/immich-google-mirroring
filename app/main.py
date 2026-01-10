"""
Main FastAPI application
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from app.database import init_db
from app.scheduler import start_scheduler, stop_scheduler, update_scheduler
from app.routes import pages, config, auth, sync, immich

# Configure logging
LOG_PATH = os.getenv("LOG_PATH", "/data/logs")
os.makedirs(LOG_PATH, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_PATH, "app.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Immich-Google Photos Sync application")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Start scheduler
    start_scheduler()
    await update_scheduler()
    logger.info("Scheduler started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    stop_scheduler()


# Create FastAPI app
app = FastAPI(
    title="Immich → Google Photos Sync",
    description="Synchronize Immich albums to Google Photos",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pages.router)
app.include_router(config.router)
app.include_router(auth.router)
app.include_router(sync.router)
app.include_router(immich.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8080")),
        reload=False
    )
