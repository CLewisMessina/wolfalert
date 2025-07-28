# backend\main.py
"""
FastAPI backend application entry point.
Single responsibility: Configure and start the FastAPI application.
"""
import os
import logging
import subprocess
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run Alembic migrations with timeout and enhanced error handling"""
    try:
        logger.info("🚀 Starting Alembic migrations...")
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Option 1: Try programmatic approach with timeout detection
        try:
            from alembic.config import Config
            from alembic import command
            
            alembic_cfg = Config(os.path.join(script_dir, "alembic.ini"))
            alembic_cfg.set_main_option("script_location", os.path.join(script_dir, "alembic"))
            
            logger.info("📋 Running migrations programmatically...")
            command.upgrade(alembic_cfg, "head")
            logger.info("✅ Alembic migrations completed successfully (programmatic)")
            return True
            
        except Exception as programmatic_error:
            logger.warning(f"⚠️ Programmatic migration failed: {str(programmatic_error)}")
            logger.info("🔄 Falling back to subprocess approach...")
            
            # Option 2: Subprocess with timeout as fallback
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd=script_dir,
                check=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.stdout:
                logger.info(f"✅ Alembic output:\n{result.stdout}")
            if result.stderr:
                logger.warning(f"⚠️ Alembic warnings:\n{result.stderr}")
            
            logger.info("✅ Alembic migrations completed successfully (subprocess)")
            return True
            
    except subprocess.TimeoutExpired:
        logger.error("⏳ Alembic migration timed out after 30 seconds")
        logger.error("💡 This suggests migrations are hanging - check database connectivity")
        return False
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Alembic subprocess failed with exit code {e.returncode}")
        if e.stdout:
            logger.error(f"Stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"Stderr: {e.stderr}")
        return False
        
    except FileNotFoundError:
        logger.error("❌ Alembic command not found - ensure alembic is installed")
        return False
        
    except Exception as e:
        logger.error(f"❌ Unexpected migration error: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🐺 Starting WolfAlert backend...")
    
    # Run database migrations on startup
    if os.getenv("DATABASE_URL"):
        logger.info("🔗 DATABASE_URL found, running migrations...")
        migration_success = run_migrations()
        
        if migration_success:
            logger.info("✅ Migration phase completed successfully")
        else:
            logger.error("❌ Migration phase failed")
            # Continue startup anyway for debugging purposes
            logger.info("🔄 Continuing startup despite migration issues...")
    else:
        logger.warning("⚠️ DATABASE_URL not found - skipping migrations")
    
    logger.info("🚀 Application startup completed")
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down WolfAlert backend...")

# Create FastAPI application
app = FastAPI(
    title="WolfAlert API",
    description="AI-powered intelligence dashboard for utility and technology professionals",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configure CORS - FIXED to properly read environment variable
cors_origins_raw = os.getenv("CORS_ORIGINS", "https://wolfalert.app,https://dev.wolfalert.app,http://localhost:3000")
cors_origins = [origin.strip() for origin in cors_origins_raw.split(",")]

# Log CORS origins for debugging
logger.info(f"🔧 CORS Origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Added OPTIONS for preflight
    allow_headers=["*"],
)

# Import database dependency with error handling
try:
    from src.core.database import get_db
    logger.info("✅ Database dependency imported successfully")
except Exception as e:
    logger.error(f"❌ Failed to import database dependency: {str(e)}")
    logger.error(f"Full traceback:\n{traceback.format_exc()}")
    # Create a fallback dependency that returns an error
    def get_db():
        raise HTTPException(status_code=503, detail="Database not available")

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

# ✅ FIXED: Import and register profile routes 
try:
    from src.api.profiles import router as profiles_router
    app.include_router(profiles_router, prefix="/api", tags=["profiles"])
    logger.info("✅ Profile routes registered successfully")
except Exception as e:
    logger.error(f"❌ Failed to register profile routes: {str(e)}")
    logger.error(f"Full traceback:\n{traceback.format_exc()}")
    # Continue without profile routes for debugging

# TODO: Add dashboard routes when ready
# try:
#     from src.api.dashboard import router as dashboard_router
#     app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])
#     logger.info("✅ Dashboard routes registered successfully")
# except Exception as e:
#     logger.error(f"❌ Failed to register dashboard routes: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"🚀 Starting server on port {port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )