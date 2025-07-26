"""
Application configuration management.
Single responsibility: Centralize all application configuration and settings.
"""
import os
from typing import List, Optional
from functools import lru_cache
from pydantic import BaseModel, field_validator

class Settings(BaseModel):
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
    database_url: str = ""
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 10
    redis_retry_on_timeout: bool = True
    
    # Security
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    session_secret_key: str = "your-session-secret-here"
    session_expire_hours: int = 24
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "https://wolfalert.app", 
        "https://dev.wolfalert.app"
    ]
    cors_allow_credentials: bool = True
    
    # OpenAI
    openai_api_key: str = ""
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
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        """Validate environment value"""
        valid_environments = ['development', 'staging', 'production']
        if v not in valid_environments:
            raise ValueError(f'Environment must be one of: {valid_environments}')
        return v
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    @field_validator('source_reliability_threshold')
    @classmethod
    def validate_reliability_threshold(cls, v):
        """Validate source reliability threshold"""
        valid_thresholds = ['high', 'medium', 'community']
        if v not in valid_thresholds:
            raise ValueError(f'Reliability threshold must be one of: {valid_thresholds}')
        return v
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    # Load settings from environment variables
    settings = Settings(
        database_url=os.getenv("DATABASE_URL", ""),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY", "your-secret-key-here"),
        session_secret_key=os.getenv("SESSION_SECRET_KEY", "your-session-secret-here"),
        environment=os.getenv("ENVIRONMENT", "development"),
        debug=os.getenv("DEBUG", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,https://wolfalert.app,https://dev.wolfalert.app")
    )
    return settings