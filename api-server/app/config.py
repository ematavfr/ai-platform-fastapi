# Configuration et Settings FastAPI
from pydantic import BaseSettings, validator
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Configuration de l'application avec validation Pydantic"""
    
    # Application
    PROJECT_NAME: str = "AI Platform API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    
    # Base de données
    DATABASE_URL: str = "postgresql://postgres:postgres123@localhost:5432/ai_platform"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # MinIO/S3
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_SECURE: bool = False
    MODELS_BUCKET: str = "ml-models"
    DATASETS_BUCKET: str = "datasets"
    
    # JWT
    JWT_SECRET_KEY: str = "jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # secondes
    
    # ML Service
    ML_SERVICE_URL: str = "http://localhost:8001"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Upload
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES: List[str] = [".csv", ".json", ".parquet", ".pkl", ".joblib"]
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT must be development, staging, or production")
        return v
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def database_url_async(self) -> str:
        """URL de base de données pour AsyncPG"""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instance globale des settings
settings = Settings()

# Configuration Celery
class CeleryConfig:
    broker_url = settings.CELERY_BROKER_URL
    result_backend = settings.CELERY_RESULT_BACKEND
    task_serializer = "json"
    accept_content = ["json"]
    result_serializer = "json"
    timezone = "UTC"
    enable_utc = True
    
    # Configuration des tâches
    task_routes = {
        "app.tasks.ml_tasks.*": {"queue": "ml_queue"},
        "app.tasks.data_tasks.*": {"queue": "data_queue"},
        "app.tasks.general_tasks.*": {"queue": "general_queue"},
    }
    
    # Retry configuration
    task_default_retry_delay = 60
    task_max_retries = 3
    
    # Monitoring
    worker_send_task_events = True
    task_send_sent_event = True

celery_config = CeleryConfig()