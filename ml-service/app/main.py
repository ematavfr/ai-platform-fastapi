# Service ML principal avec FastAPI
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import pickle
import joblib
import time
import io
from contextlib import asynccontextmanager

from .config import settings
from .models.prediction import PredictionRequest, PredictionResponse, BatchPredictionRequest
from .services.model_loader import ModelLoader
from .services.preprocessing import PreprocessingService
from .services.cache import CacheService
from .utils.monitoring import MetricsCollector
from .utils.logging import get_logger

logger = get_logger(__name__)

# Services globaux
model_loader = ModelLoader()
preprocessing_service = PreprocessingService()
cache_service = CacheService()
metrics_collector = MetricsCollector()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie pour le service ML"""
    # Startup
    logger.info("🚀 Starting ML Service")
    
    # Initialiser les services
    await cache_service.initialize()
    await model_loader.initialize()
    
    # Pré-charger les modèles en cache
    await model_loader.preload_deployed_models()
    
    yield
    
    # Shutdown
    logger.info("🔥 Shutting down ML Service")
    await cache_service.close()
    await model_loader.cleanup()

def create_ml_app() -> FastAPI:
    """Factory pour créer l'application ML FastAPI"""
    
    app = FastAPI(
        title="AI Platform ML Service",
        description="Service de Machine Learning pour prédictions temps réel",
        version="1.0.0",
        docs_url="/docs",
        lifespan=lifespan
    )

    # Configuration CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Plus restrictif en production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health_check():
        """Health check pour Kubernetes"""
        loaded_models = await model_loader.get_loaded_models_count()
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "loaded_models": loaded_models,
            "cache_status": await cache_service.ping()
        }

    @app.get("/models")
    async def list_loaded_models():
        """Liste des modèles chargés en mémoire"""
        models = await model_loader.list_loaded_models()
        return {"loaded_models": models}

    @app.post("/predict/{model_id}", response_model=PredictionResponse)
    async def predict(
        model_id: str,
        request: PredictionRequest,
        background_tasks: BackgroundTasks
    ):
        """
        Effectue une prédiction avec un modèle spécifique
        
        - **model_id**: ID du modèle à utiliser
        - **request**: Données d'entrée pour la prédiction
        """
        start_time = time.time()
        
        try:
            # Vérifier le cache
            cache_key = f"pred:{model_id}:{hash(str(request.input_data))}"
            cached_result = await cache_service.get(cache_key)
            
            if cached_result and request.use_cache:
                logger.info(f"Cache hit for prediction {cache_key}")
                return PredictionResponse(**cached_result)

            # Charger le modèle
            model = await model_loader.load_model(model_id)
            if not model:
                raise HTTPException(status_code=404, detail="Model not found")

            # Préprocessing
            processed_input = await preprocessing_service.preprocess(
                request.input_data, 
                model.get("preprocessing_config", {})
            )

            # Prédiction
            prediction_result = await _make_prediction(
                model["instance"], 
                processed_input,
                request.return_probabilities
            )

            # Post-processing
            final_result = await preprocessing_service.postprocess(
                prediction_result,
                model.get("postprocessing_config", {})
            )

            processing_time = (time.time() - start_time) * 1000

            response = PredictionResponse(
                model_id=model_id,
                prediction=final_result["prediction"],
                confidence_score=final_result.get("confidence"),
                processing_time=processing_time,
                timestamp=time.time(),
                metadata={
                    "model_version": model.get("version"),
                    "preprocessing_applied": bool(model.get("preprocessing_config")),
                    "cache_used": False
                }
            )

            # Mettre en cache si demandé
            if request.use_cache:
                background_tasks.add_task(
                    cache_service.set,
                    cache_key,
                    response.dict(),
                    expire=300  # 5 minutes
                )

            # Métriques
            background_tasks.add_task(
                metrics_collector.record_prediction,
                model_id,
                processing_time,
                True
            )

            return response

        except Exception as e:
            logger.error(f"Prediction error for model {model_id}: {str(e)}")
            
            # Métriques d'erreur
            background_tasks.add_task(
                metrics_collector.record_prediction,
                model_id,
                (time.time() - start_time) * 1000,
                False
            )
            
            raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    @app.get("/metrics")
    async def get_metrics():
        """Récupère les métriques du service ML"""
        return await metrics_collector.get_all_metrics()

    return app

async def _make_prediction(model, input_data: Dict[str, Any], return_probabilities: bool = False):
    """Effectue une prédiction avec gestion d'erreur"""
    try:
        # Convertir en format approprié selon le type de modèle
        if hasattr(model, 'predict_proba') and return_probabilities:
            probabilities = model.predict_proba([list(input_data.values())])[0]
            prediction = model.predict([list(input_data.values())])[0]
            
            return {
                "prediction": prediction,
                "confidence": float(max(probabilities)),
                "probabilities": probabilities.tolist() if hasattr(probabilities, 'tolist') else probabilities
            }
        else:
            prediction = model.predict([list(input_data.values())])[0]
            return {
                "prediction": prediction.tolist() if hasattr(prediction, 'tolist') else prediction
            }
            
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise

# Création de l'instance
app = create_ml_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.ENVIRONMENT == "development"
    )