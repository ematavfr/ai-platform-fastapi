# Service de préprocessing et postprocessing
import numpy as np
import pandas as pd
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class PreprocessingService:
    """Service de préprocessing des données"""
    
    async def preprocess(self, input_data: Dict[str, Any], config: Dict[str, Any]) -> Any:
        """
        Applique le préprocessing aux données d'entrée
        """
        try:
            # Conversion basique - ici vous ajouteriez votre logique de préprocessing
            processed_data = input_data.copy()
            
            # Exemple de normalisation si configurée
            if config.get("normalize", False):
                for key, value in processed_data.items():
                    if isinstance(value, (int, float)):
                        processed_data[key] = (value - config.get("mean", 0)) / config.get("std", 1)
            
            # Exemple de gestion des valeurs manquantes
            if config.get("fill_na", False):
                fill_value = config.get("fill_value", 0)
                for key, value in processed_data.items():
                    if value is None:
                        processed_data[key] = fill_value
            
            logger.debug(f"Preprocessing applied with config: {config}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Preprocessing error: {str(e)}")
            return input_data
    
    async def postprocess(self, prediction_result: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applique le postprocessing aux résultats de prédiction
        """
        try:
            processed_result = prediction_result.copy()
            
            # Exemple de mapping des classes
            if config.get("class_mapping"):
                mapping = config["class_mapping"]
                if "prediction" in processed_result:
                    pred = processed_result["prediction"]
                    if pred in mapping:
                        processed_result["prediction"] = mapping[pred]
            
            # Exemple de seuillage pour la confiance
            if config.get("confidence_threshold"):
                threshold = config["confidence_threshold"]
                if "confidence" in processed_result:
                    if processed_result["confidence"] < threshold:
                        processed_result["low_confidence"] = True
            
            logger.debug(f"Postprocessing applied with config: {config}")
            return processed_result
            
        except Exception as e:
            logger.error(f"Postprocessing error: {str(e)}")
            return prediction_result