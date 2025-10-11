# Main FastAPI application
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn

from .core.config import settings
from .core.database import async_engine, Base
from .core.redis import close_redis
from .core.logging import configure_logging, get_logger
from .api import keywords, blogs, targets, results, dashboard, auth


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Naver Monitor API", version=settings.app_version)
    
    # Create database tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Naver Monitor API")
    await close_redis()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Advanced Naver blog monitoring system with real-time crawling",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
    )

# Configure logging
configure_logging()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(keywords.router, prefix="/api/keywords", tags=["keywords"])
app.include_router(blogs.router, prefix="/api/blogs", tags=["blogs"])
app.include_router(targets.router, prefix="/api/targets", tags=["targets"])
app.include_router(results.router, prefix="/api/results", tags=["results"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Naver Monitor API",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.app_version}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )

