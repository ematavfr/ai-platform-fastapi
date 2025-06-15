# Service de chargement des modèles ML
import pickle
import joblib
import os
import time
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..config import settings

logger = logging.getLogger(__name__)

class ModelLoader:
    """Service de gestion des modèles ML en mémoire"""
    
    def __init__(self):
        self.loaded_models: Dict[str, Dict[str, Any]] = {}
        self.model_stats: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self):
        """Initialise le service de chargement"""
        # Créer le répertoire de cache s'il n'existe pas
        os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)
        logger.info("ModelLoader initialized")
    
    async def load_model(self, model_id: str, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Charge un modèle en mémoire"""
        
        # Si le modèle est déjà chargé et pas de force reload
        if model_id in self.loaded_models and not force_reload:
            self.model_stats[model_id]["last_access"] = time.time()
            return self.loaded_models[model_id]
        
        try:
            start_time = time.time()
            
            # Simuler le chargement d'un modèle
            # En réalité, ici vous chargeriez depuis MinIO/stockage
            model_path = f"{settings.MODEL_CACHE_DIR}/{model_id}.pkl"
            
            # Si le fichier n'existe pas, créer un modèle de démonstration
            if not os.path.exists(model_path):
                await self._create_demo_model(model_id, model_path)
            
            # Charger le modèle
            with open(model_path, 'rb') as f:
                model_instance = pickle.load(f)
            
            load_time = time.time() - start_time
            
            # Métadonnées du modèle
            model_info = {
                "instance": model_instance,
                "model_id": model_id,
                "load_time": load_time,
                "version": "1.0.0",
                "framework": "scikit-learn",
                "preprocessing_config": {},
                "postprocessing_config": {}
            }
            
            # Stocker en mémoire
            self.loaded_models[model_id] = model_info
            self.model_stats[model_id] = {
                "load_time": load_time,
                "last_access": time.time(),
                "prediction_count": 0
            }
            
            logger.info(f"Model {model_id} loaded successfully in {load_time:.3f}s")
            
            # Gérer la limite de modèles en mémoire
            await self._manage_memory_limit()
            
            return model_info
            
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {str(e)}")
            return None
    
    async def _create_demo_model(self, model_id: str, model_path: str):
        """Crée un modèle de démonstration"""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.datasets import make_classification
        
        # Créer des données d'exemple
        X, y = make_classification(n_samples=1000, n_features=4, n_classes=2, random_state=42)
        
        # Entraîner un modèle simple
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        # Sauvegarder
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(f"Created demo model for {model_id}")
    
    async def unload_model(self, model_id: str) -> bool:
        """Décharge un modèle de la mémoire"""
        if model_id in self.loaded_models:
            del self.loaded_models[model_id]
            del self.model_stats[model_id]
            logger.info(f"Model {model_id} unloaded")
            return True
        return False
    
    async def get_loaded_models_count(self) -> int:
        """Retourne le nombre de modèles chargés"""
        return len(self.loaded_models)
    
    async def list_loaded_models(self) -> List[str]:
        """Liste les IDs des modèles chargés"""
        return list(self.loaded_models.keys())
    
    async def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'un modèle"""
        if model_id in self.loaded_models:
            model_info = self.loaded_models[model_id].copy()
            model_info.update(self.model_stats[model_id])
            # Enlever l'instance du modèle pour la sérialisation
            model_info.pop("instance", None)
            return model_info
        return None
    
    async def preload_deployed_models(self):
        """Pré-charge les modèles déployés au démarrage"""
        # En réalité, ici vous récupéreriez la liste depuis la base de données
        demo_models = ["demo_model_1", "demo_model_2"]
        
        for model_id in demo_models:
            await self.load_model(model_id)
        
        logger.info(f"Preloaded {len(demo_models)} models")
    
    async def _manage_memory_limit(self):
        """Gère la limite de modèles en mémoire"""
        if len(self.loaded_models) > settings.MAX_MODELS_IN_MEMORY:
            # Trouve le modèle le moins récemment utilisé
            oldest_model = min(
                self.model_stats.items(),
                key=lambda x: x[1]["last_access"]
            )[0]
            
            await self.unload_model(oldest_model)
            logger.info(f"Unloaded LRU model: {oldest_model}")
    
    async def cleanup(self):
        """Nettoie les ressources au shutdown"""
        self.loaded_models.clear()
        self.model_stats.clear()
        logger.info("ModelLoader cleaned up")