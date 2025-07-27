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
        return database_url
    
    # Fallback to config file setting
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
    logger.info("🔄 Starting online migrations with simplified approach...")
    
    # Override the sqlalchemy.url in the config with our environment variable
    config_dict = config.get_section(config.config_ini_section)
    config_dict["sqlalchemy.url"] = get_database_url()
    
    # Create engine with simplified configuration - avoid complex pooling during migrations
    connectable = engine_from_config(
        config_dict,
        prefix="sqlalchemy.",
        poolclass=pool.StaticPool,  # Use StaticPool instead of NullPool for better Railway compatibility
        pool_pre_ping=True,         # Verify connections before use
        pool_recycle=300,          # Recycle connections every 5 minutes
        connect_args={
            "connect_timeout": 10,  # 10 second connection timeout
            "options": "-c timezone=UTC"
        }
    )
    
    logger.info("✅ Migration engine created with StaticPool")

    try:
        with connectable.connect() as connection:
            logger.info("✅ Database connection established for migrations")
            
            context.configure(
                connection=connection, 
                target_metadata=target_metadata
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


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()