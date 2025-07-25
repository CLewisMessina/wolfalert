"""
FastAPI backend application entry point.
Single responsibility: Configure and start the FastAPI application.
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from src.core.database import init_database, check_database_health
from src.core.config import get_settings
from src.api.profiles import router as profiles_router
from src.api.dashboard import router as dashboard_router
from src.api.sources import router as sources_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting WolfAlert backend...")
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    # TODO: Initialize Redis connection
    # TODO: Start background tasks (RSS fetching, AI processing)
    
    yield
    
    # Shutdown
    logger.info("Shutting down WolfAlert backend...")

# Get application settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="WolfAlert API",
    description="AI-powered intelligence dashboard for utility and technology professionals",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Configure trusted hosts (security)
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["wolfalert.app", "*.wolfalert.app", "api.wolfalert.app"]
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway and monitoring"""
    try:
        db_healthy = check_database_health()
        # TODO: Add Redis health check
        # TODO: Add other service health checks
        
        if not db_healthy:
            raise HTTPException(status_code=503, detail="Database unhealthy")
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "database": "connected",
            "environment": settings.environment
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "environment": settings.environment
            }
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "WolfAlert API",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "health": "/health"
    }

# Include API routers
app.include_router(profiles_router, prefix="/api", tags=["profiles"])
app.include_router(dashboard_router, prefix="/api", tags=["dashboard"]) 
app.include_router(sources_router, prefix="/api", tags=["sources"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred" if not settings.debug else str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    workers = int(os.getenv("API_WORKERS", "1"))
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=settings.reload,
        workers=workers if not settings.reload else 1,
        log_level=settings.log_level.lower()
    )