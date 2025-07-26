"""
backend\main.py
FastAPI backend application entry point.
Single responsibility: Configure and start the FastAPI application.
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run Alembic migrations programmatically"""
    try:
        from alembic.config import Config
        from alembic import command
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alembic_cfg = Config(os.path.join(script_dir, "alembic.ini"))
        
        # Set the script location to the alembic directory
        alembic_cfg.set_main_option("script_location", os.path.join(script_dir, "alembic"))
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting WolfAlert backend...")
    
    # Run database migrations on startup
    if os.getenv("DATABASE_URL"):
        try:
            run_migrations()
        except Exception as e:
            logger.error(f"Failed to run migrations: {str(e)}")
            # Don't fail startup for demo purposes, but log the error
    else:
        logger.warning("DATABASE_URL not found - skipping migrations")
    
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
cors_origins = os.getenv("CORS_ORIGINS", "https://wolfalert.app,https://dev.wolfalert.app,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# ✅ USE PROPER DATABASE DEPENDENCY (import from core.database)
from src.core.database import get_db

# Health check endpoint (required by Railway)
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    db_status = "connected" if os.getenv("DATABASE_URL") else "not configured"
    return {
        "status": "healthy", 
        "service": "wolfalert-backend",
        "database": db_status,
        "version": "1.0.0"
    }

# Basic info endpoint
@app.get("/")
async def root():
    """Root endpoint with basic API information"""
    return {
        "name": "WolfAlert API",
        "version": "1.0.0",
        "status": "running",
        "database": "connected" if os.getenv("DATABASE_URL") else "not configured",
        "docs": "/docs"
    }

# Database test endpoint
@app.get("/api/test-db")
async def test_database(db: Session = Depends(get_db)):
    """Test database connection and tables"""
    try:
        from sqlalchemy import text
        result = db.execute(text("SELECT 1"))
        
        # Test if our tables exist
        table_check = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('user_profiles', 'articles', 'rss_sources')
        """))
        tables = [row[0] for row in table_check.fetchall()]
        
        return {
            "database": "connected",
            "test_query": "success",
            "tables_found": tables,
            "tables_expected": ["user_profiles", "articles", "rss_sources"]
        }
    except Exception as e:
        return {"database": "error", "message": str(e)}

# ✅ ENABLE API ROUTES - Fixed import
from src.api.profiles import router as profiles_router
# from src.api.dashboard import router as dashboard_router  # TODO: Create dashboard routes

# Include API routers
app.include_router(profiles_router, prefix="/api", tags=["profiles"])
# app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])  # TODO: Enable when ready

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )