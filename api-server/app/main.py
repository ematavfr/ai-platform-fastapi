# api-server/app/main.py
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import logging
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import multiprocess, CollectorRegistry

from .config import settings
from .database import engine, Base
from .routers import auth, users, projects, models, datasets, predictions
from .middleware import log_requests, rate_limit_middleware
from .exceptions import setup_exception_handlers
from .celery_app import celery_app

# Métriques Prometheus
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    # Startup
    logging.info("🚀 Starting AI Platform API Server")
    
    # Création des tables de base de données
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialisation des services externes
    await initialize_external_services()
    
    yield
    
    # Shutdown
    logging.info("🔥 Shutting down AI Platform API Server")
    await cleanup_resources()

async def initialize_external_services():
    """Initialise les services externes (MinIO, Redis, etc.)"""
    from .services.storage import storage_service
    from .services.cache import cache_service
    
    await storage_service.initialize()
    await cache_service.initialize()

async def cleanup_resources():
    """Nettoie les ressources avant arrêt"""
    from .services.cache import cache_service
    await cache_service.close()

def create_application() -> FastAPI:
    """Factory pour créer l'application FastAPI"""
    
    app = FastAPI(
        title="AI Platform API",
        description="API pour plateforme d'intelligence artificielle d'entreprise",
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
        lifespan=lifespan
    )

    # Configuration CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Compression GZIP
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Middleware custom
    app.middleware("http")(log_requests)
    app.middleware("http")(rate_limit_middleware)

    # Gestionnaires d'exceptions
    setup_exception_handlers(app)

    # Routes principales
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
    app.include_router(models.router, prefix="/api/v1/models", tags=["ML Models"])
    app.include_router(datasets.router, prefix="/api/v1/datasets", tags=["Datasets"])
    app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["Predictions"])

    @app.get("/health")
    async def health_check():
        """Health check endpoint pour Kubernetes"""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT
        }

    @app.get("/metrics")
    async def get_metrics():
        """Endpoint Prometheus metrics"""
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        data = generate_latest(registry)
        return Response(data, media_type=CONTENT_TYPE_LATEST)

    @app.get("/")
    async def root():
        """Endpoint racine"""
        return {
            "message": "AI Platform API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }

    return app

# Création de l'instance
app = create_application()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        workers=1 if settings.ENVIRONMENT == "development" else 4
    )