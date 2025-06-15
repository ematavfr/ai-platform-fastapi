# Middleware personnalisés
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import time
import logging
from ..services.cache import cache_service

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    """Middleware pour logger toutes les requêtes"""
    start_time = time.time()
    
    # Log de la requête entrante
    logger.info(f"Incoming request: {request.method} {request.url}")
    
    # Traitement de la requête
    response = await call_next(request)
    
    # Calcul du temps de traitement
    process_time = time.time() - start_time
    
    # Log de la réponse
    logger.info(
        f"Request completed: {request.method} {request.url} - "
        f"Status: {response.status_code} - Time: {process_time:.3f}s"
    )
    
    # Ajouter le temps de traitement dans les headers
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

async def rate_limit_middleware(request: Request, call_next):
    """Middleware basique de rate limiting"""
    client_ip = request.client.host
    
    # Clé pour le rate limiting
    rate_limit_key = f"rate_limit:{client_ip}"
    
    try:
        # Vérifier le nombre de requêtes dans la fenêtre
        current_requests = await cache_service.get(rate_limit_key) or 0
        
        if current_requests >= 100:  # Limite basique
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )
        
        # Incrémenter le compteur
        await cache_service.set(rate_limit_key, current_requests + 1, expire=60)
        
    except Exception as e:
        logger.warning(f"Rate limiting failed: {str(e)}")
    
    # Continuer le traitement
    response = await call_next(request)
    return response