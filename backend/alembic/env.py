"""Alembic environment configuration for WolfAlert database migrations."""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
import logging

# Add the src directory to the path so we can import our models
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import your models here - DO NOT import database config to avoid circular imports
from src.models.database import Base

# Setup logging
logger = logging.getLogger(__name__)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

def get_database_url():
    """Get database URL from environment variable or config."""
    # First try environment variable (Railway provides this)
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Railway's DATABASE_URL sometimes uses postgres:// which SQLAlchemy 2.0+ doesn't support
        # Convert to postgresql:// if needed
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            logger.info("✅ Converted postgres:// to postgresql:// for migrations")
        
        # Add debug logging
        logger.info(f"🔍 Database URL prefix: {database_url[:30]}...")
        return database_url
    
    # Fallback to config file setting
    logger.warning("⚠️ DATABASE_URL not found in environment, falling back to alembic.ini")
    return config.get_main_option("sqlalchemy.url")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    logger.info("🔄 Starting online migrations...")
    
    # Override the sqlalchemy.url in the config with our environment variable
    database_url = get_database_url()
    
    if not database_url:
        raise ValueError("❌ DATABASE_URL is required for migrations")
    
    logger.info(f"🔗 Using database URL: {database_url[:30]}...")
    
    config_dict = config.get_section(config.config_ini_section) or {}
    config_dict["sqlalchemy.url"] = database_url
    
    # Use QueuePool to match the main application configuration
    # This ensures consistency between migrations and runtime
    connectable = engine_from_config(
        config_dict,
        prefix="sqlalchemy.",
        poolclass=pool.QueuePool,  # Changed from StaticPool to QueuePool
        pool_size=5,               # Match main app configuration
        max_overflow=10,           # Match main app configuration
        pool_timeout=30,           # Match main app configuration
        pool_recycle=3600,         # Match main app configuration
        pool_pre_ping=True,        # Verify connections before use
        echo=True,                 # Enable SQL logging for debugging
        connect_args={
            "connect_timeout": 10,
            "options": "-c timezone=UTC"
        }
    )
    
    logger.info("✅ Migration engine created with QueuePool")

    try:
        with connectable.connect() as connection:
            logger.info("✅ Database connection established for migrations")
            
            # Log current database info
            result = connection.execute("SELECT current_database(), current_user, version()")
            db_info = result.fetchone()
            logger.info(f"📊 Connected to: {db_info[0]} as {db_info[1]}")
            logger.info(f"📊 PostgreSQL version: {db_info[2]}")
            
            context.configure(
                connection=connection, 
                target_metadata=target_metadata,
                compare_type=True,        # Detect column type changes
                compare_server_default=True  # Detect default value changes
            )
            logger.info("✅ Migration context configured")

            with context.begin_transaction():
                logger.info("🚀 Beginning migration transaction...")
                context.run_migrations()
                logger.info("✅ Migrations executed successfully")
                
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise
    finally:
        logger.info("🏁 Migration process completed")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()