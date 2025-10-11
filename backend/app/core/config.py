# Environment Configuration
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App settings
    app_name: str = "Naver Monitor API"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # Database settings
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/naver_monitor"
    database_url_sync: str = "postgresql://postgres:password@localhost:5432/naver_monitor"
    
    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    
    # Celery settings
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/1"
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Crawler settings
    crawl_timeout_ms: int = 60000
    max_concurrent_crawls: int = 5
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    
    # Monitoring settings
    enable_metrics: bool = True
    metrics_port: int = 8001
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

