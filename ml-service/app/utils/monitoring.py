# Collecteur de métriques pour le service ML
import time
from typing import Dict, Any
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collecteur de métriques pour le service ML"""
    
    def __init__(self):
        self.prediction_metrics = defaultdict(lambda: {
            "total_predictions": 0,
            "successful_predictions": 0,
            "failed_predictions": 0,
            "avg_response_time": 0,
            "response_times": deque(maxlen=1000),  # Garder les 1000 derniers temps
            "last_prediction": None
        })
        
        self.global_metrics = {
            "service_start_time": time.time(),
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    async def record_prediction(self, model_id: str, response_time: float, success: bool):
        """Enregistre les métriques d'une prédiction"""
        try:
            metrics = self.prediction_metrics[model_id]
            
            metrics["total_predictions"] += 1
            metrics["last_prediction"] = time.time()
            
            if success:
                metrics["successful_predictions"] += 1
            else:
                metrics["failed_predictions"] += 1
            
            # Enregistrer le temps de réponse
            metrics["response_times"].append(response_time)
            
            # Calculer la moyenne mobile
            if metrics["response_times"]:
                metrics["avg_response_time"] = sum(metrics["response_times"]) / len(metrics["response_times"])
            
            self.global_metrics["total_requests"] += 1
            
            logger.debug(f"Recorded prediction metrics for model {model_id}")
            
        except Exception as e:
            logger.error(f"Error recording prediction metrics: {str(e)}")
    
    async def record_batch_prediction(self, model_id: str, batch_size: int, total_time: float, success: bool):
        """Enregistre les métriques d'une prédiction en lot"""
        try:
            avg_time_per_prediction = total_time / batch_size if batch_size > 0 else total_time
            
            for _ in range(batch_size):
                await self.record_prediction(model_id, avg_time_per_prediction, success)
            
            logger.debug(f"Recorded batch prediction metrics for model {model_id}")
            
        except Exception as e:
            logger.error(f"Error recording batch prediction metrics: {str(e)}")
    
    async def record_cache_hit(self):
        """Enregistre un cache hit"""
        self.global_metrics["cache_hits"] += 1
    
    async def record_cache_miss(self):
        """Enregistre un cache miss"""
        self.global_metrics["cache_misses"] += 1
    
    async def get_model_metrics(self, model_id: str) -> Dict[str, Any]:
        """Récupère les métriques d'un modèle spécifique"""
        if model_id not in self.prediction_metrics:
            return {}
        
        metrics = self.prediction_metrics[model_id].copy()
        
        # Convertir deque en liste pour la sérialisation
        metrics["response_times"] = list(metrics["response_times"])
        
        # Calculer des statistiques supplémentaires
        if metrics["response_times"]:
            response_times = metrics["response_times"]
            metrics["min_response_time"] = min(response_times)
            metrics["max_response_time"] = max(response_times)
            metrics["median_response_time"] = sorted(response_times)[len(response_times) // 2]
        
        # Calculer le taux de succès
        if metrics["total_predictions"] > 0:
            metrics["success_rate"] = metrics["successful_predictions"] / metrics["total_predictions"]
        else:
            metrics["success_rate"] = 0
        
        return metrics
    
    async def get_global_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques globales"""
        uptime = time.time() - self.global_metrics["service_start_time"]
        
        metrics = self.global_metrics.copy()
        metrics["uptime_seconds"] = uptime
        
        # Calculer le taux de cache hit
        total_cache_requests = metrics["cache_hits"] + metrics["cache_misses"]
        if total_cache_requests > 0:
            metrics["cache_hit_rate"] = metrics["cache_hits"] / total_cache_requests
        else:
            metrics["cache_hit_rate"] = 0
        
        return metrics
    
    async def get_all_metrics(self) -> Dict[str, Any]:
        """Récupère toutes les métriques"""
        all_metrics = {
            "global": await self.get_global_metrics(),
            "models": {}
        }
        
        for model_id in self.prediction_metrics:
            all_metrics["models"][model_id] = await self.get_model_metrics(model_id)
        
        return all_metrics