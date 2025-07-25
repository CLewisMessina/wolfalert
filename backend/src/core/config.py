"""
Application configuration management.
Single responsibility: Centralize all application configuration and settings.
"""
import os
from typing import List, Optional
from functools import lru_cache
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Environment
    environment: str = "development"
    debug: bool = True
    reload: bool = True
    log_level: str = "INFO"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    
    # Database
    database_url: str
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 10
    redis_retry_on_timeout: bool = True
    
    # Security
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    session_secret_key: str
    session_expire_hours: int = 24
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "https://wolfalert.app", 
        "https://dev.wolfalert.app"
    ]
    cors_allow_credentials: bool = True
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.3
    openai_max_requests_per_hour: int = 1000
    
    # RSS Processing
    rss_fetch_interval_hours: int = 4
    rss_fetch_timeout_seconds: int = 30
    rss_max_articles_per_source: int = 50
    
    # Content Management
    article_expiry_days: int = 30
    ai_analysis_timeout_seconds: int = 30
    ai_relevance_threshold: float = 0.40
    ai_cache_ttl_hours: int = 24
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_minutes: int = 15
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    sentry_dsn: Optional[str] = None
    
    # Celery Background Tasks
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    celery_task_serializer: str = "json"
    celery_result_serializer: str = "json"
    
    # Content Sources
    enable_community_sources: bool = True
    enable_github_releases: bool = True
    source_reliability_threshold: str = "medium"
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment value"""
        valid_environments = ['development', 'staging', 'production']
        if v not in valid_environments:
            raise ValueError(f'Environment must be one of: {valid_environments}')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    @validator('source_reliability_threshold')
    def validate_reliability_threshold(cls, v):
        """Validate source reliability threshold"""
        valid_thresholds = ['high', 'medium', 'community']
        if v not in valid_thresholds:
            raise ValueError(f'Reliability threshold must be one of: {valid_thresholds}')
        return v
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        case_sensitive = False
        
        # Example values for documentation
        schema_extra = {
            "example": {
                "environment": "development",
                "database_url": "postgresql://user:pass@localhost:5432/wolfalert",
                "redis_url": "redis://localhost:6379/0",
                "openai_api_key": "sk-your-openai-key-here",
                "jwt_secret_key": "your-super-secret-jwt-key",
                "session_secret_key": "your-session-secret-key"
            }
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()


# Configuration constants
class Config:
    """Static configuration constants"""
    
    # Application
    APP_NAME = "WolfAlert"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "AI-powered intelligence dashboard for utility and technology professionals"
    
    # Database
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # AI Processing
    MIN_ARTICLE_LENGTH = 100  # Minimum characters for AI processing
    MAX_ARTICLE_LENGTH = 50000  # Maximum characters to prevent token overflow
    
    # Cache Keys
    CACHE_KEY_PREFIX = "wolfalert:"
    DASHBOARD_CACHE_KEY = f"{CACHE_KEY_PREFIX}dashboard:"
    ARTICLE_CACHE_KEY = f"{CACHE_KEY_PREFIX}article:"
    PROFILE_CACHE_KEY = f"{CACHE_KEY_PREFIX}profile:"
    
    # Time Constants (in seconds)
    CACHE_TTL_SHORT = 300  # 5 minutes
    CACHE_TTL_MEDIUM = 3600  # 1 hour
    CACHE_TTL_LONG = 86400  # 24 hours
    
    # Content Processing
    RSS_USER_AGENT = f"{APP_NAME}/{APP_VERSION} (+https://wolfalert.app)"
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    
    # Impact Score Ranges
    IMPACT_SCORE_HIGH = 0.75
    IMPACT_SCORE_MEDIUM = 0.50
    IMPACT_SCORE_LOW = 0.25