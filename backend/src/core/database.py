"""
Database configuration and connection management.
Single responsibility: Handle database connections, sessions, and configuration.
"""
import os
import logging
from typing import Generator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

from ..models.database import Base

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # 🔧 FIX: Convert postgres:// to postgresql:// for SQLAlchemy 2.0+ compatibility
        logger.info(f"Raw DATABASE_URL prefix: {self.database_url[:20]}...")
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
            logger.info("✅ Converted postgres:// to postgresql:// for SQLAlchemy 2.0+ compatibility")
        else:
            logger.info("✅ DATABASE_URL already uses postgresql:// format")
        
        # Database pool configuration
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        
        # 🔧 FIX: Add enhanced logging for database engine creation
        logger.info(f"Creating database engine with pool_size={self.pool_size}, max_overflow={self.max_overflow}")
        
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                echo=os.getenv("DEBUG", "false").lower() == "true",
                future=True
            )
            logger.info("✅ Database engine created successfully")
        except Exception as e:
            logger.error(f"❌ Database engine creation failed: {str(e)}")
            logger.error(f"Database URL format: {self.database_url[:30]}...")
            raise
        
        # Create session factory
        try:
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            logger.info("✅ Database session factory created successfully")
        except Exception as e:
            logger.error(f"❌ Session factory creation failed: {str(e)}")
            raise
        
        logger.info(f"✅ Database configuration completed successfully")
    
    def create_all_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("All database tables created")
    
    def drop_all_tables(self):
        """Drop all database tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped")
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    @contextmanager
    def get_session_context(self) -> Generator[Session, None, None]:
        """Get a database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()
    
    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            with self.get_session_context() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False


# Global database instance - with enhanced error handling
try:
    db_config = DatabaseConfig()
    logger.info("✅ Global database configuration initialized successfully")
except Exception as e:
    logger.error(f"❌ CRITICAL: Global database configuration failed: {str(e)}")
    # Re-raise the exception to fail fast and provide clear error messages
    raise

# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """Database dependency for FastAPI endpoints"""
    try:
        with db_config.get_session_context() as session:
            yield session
    except Exception as e:
        logger.error(f"❌ Database dependency error: {str(e)}")
        raise

# Utility functions
def init_database():
    """Initialize database tables"""
    db_config.create_all_tables()

def check_database_health() -> bool:
    """Check if database is healthy"""
    return db_config.health_check()