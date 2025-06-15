# Modèles Pydantic pour les prédictions
from pydantic import BaseModel, validator
from typing import Dict, Any, List, Optional
from datetime import datetime

class PredictionRequest(BaseModel):
    """Requête de prédiction"""
    input_data: Dict[str, Any]
    return_probabilities: bool = False
    use_cache: bool = True
    
    @validator('input_data')
    def validate_input_data(cls, v):
        if not v:
            raise ValueError('input_data cannot be empty')
        return v

class BatchPredictionRequest(BaseModel):
    """Requête de prédiction en lot"""
    inputs: List[Dict[str, Any]]
    return_probabilities: bool = False
    use_cache: bool = False
    
    @validator('inputs')
    def validate_inputs(cls, v):
        if not v:
            raise ValueError('inputs cannot be empty')
        if len(v) > 1000:  # Limite configurable
            raise ValueError('batch size too large')
        return v

class PredictionResponse(BaseModel):
    """Réponse de prédiction"""
    model_id: str
    prediction: Any
    confidence_score: Optional[float] = None
    probabilities: Optional[List[float]] = None
    processing_time: float  # en millisecondes
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None

class ModelInfo(BaseModel):
    """Informations sur un modèle"""
    model_id: str
    name: str
    version: str
    framework: str
    model_type: str
    is_loaded: bool
    load_time: Optional[float] = None
    last_prediction: Optional[float] = None
    prediction_count: int = 0