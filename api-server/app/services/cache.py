# Service de cache Redis
import redis.asyncio as redis
import json
import logging
from typing import Any, Optional

from ..config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_client = None
    
    async def initialize(self):
        """Initialise la connexion Redis"""
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            # Test de connexion
            await self.redis_client.ping()
            logger.info("Redis cache service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {str(e)}")
            raise
    
    async def close(self):
        """Ferme la connexion Redis"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def ping(self) -> bool:
        """Test de connectivité Redis"""
        try:
            await self.redis_client.ping()
            return True
        except:
            return False
    
    async def set(self, key: str, value: Any, expire: int = None):
        """Stocke une valeur dans le cache"""
        try:
            serialized_value = json.dumps(value)
            await self.redis_client.set(key, serialized_value, ex=expire)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {str(e)}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {str(e)}")
            return None
    
    async def delete(self, key: str):
        """Supprime une clé du cache"""
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {str(e)}")
    
    async def exists(self, key: str) -> bool:
        """Vérifie si une clé existe"""
        try:
            return await self.redis_client.exists(key)
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {str(e)}")
            return False

# Instance globale
cache_service = CacheService()