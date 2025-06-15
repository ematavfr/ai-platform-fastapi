# Configuration du service ML
from pydantic import BaseSettings
from typing import List

class MLSettings(BaseSettings):
    """Configuration spécifique au service ML"""
    
    # Application
    SERVICE_NAME: str = "AI Platform ML Service"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Redis pour cache et communication
    REDIS_URL: str = "redis://localhost:6379"
    
    # MinIO pour stockage des modèles
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_SECURE: bool = False
    
    # Cache des modèles
    MODEL_CACHE_DIR: str = "/app/model_cache"
    MAX_MODELS_IN_MEMORY: int = 10
    MODEL_CACHE_TTL: int = 3600  # 1 heure
    
    # Prédictions
    MAX_BATCH_SIZE: int = 1000
    PREDICTION_TIMEOUT: int = 30  # secondes
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instance globale
settings = MLSettings()