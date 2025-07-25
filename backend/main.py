"""
backend\main.py
FastAPI backend application entry point.
Single responsibility: Configure and start the FastAPI application.
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
    
    # TODO: Initialize database when database connection is ready
    # TODO: Initialize Redis connection
    # TODO: Start background tasks (RSS fetching, AI processing)
    
    yield
    
    # Shutdown
    logger.info("Shutting down WolfAlert backend...")

# Create FastAPI application
app = FastAPI(
    title="WolfAlert API",
    description="AI-powered intelligence dashboard for utility and technology professionals",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "https://wolfalert.app,https://dev.wolfalert.app").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Health check endpoint (required by Railway)
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "service": "wolfalert-backend"}

# Basic info endpoint
@app.get("/")
async def root():
    """Root endpoint with basic API information"""
    return {
        "name": "WolfAlert API",
        "version": "1.0.0",
        "status": "running"
    }

# TODO: Add API routes when database is ready
# from src.api.profiles import router as profiles_router
# from src.api.dashboard import router as dashboard_router
# app.include_router(profiles_router, prefix="/api", tags=["profiles"])
# app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )