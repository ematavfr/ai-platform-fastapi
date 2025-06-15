# Routeur pour les prédictions
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from ..database import get_db
from ..schemas.schemas import PredictionRequest, PredictionResponse, User
from ..services.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=PredictionResponse)
async def make_prediction(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Effectue une prédiction avec un modèle
    """
    return {
        "message": "Prediction endpoint",
        "input": request.input_data
    }

@router.get("/")
async def list_predictions(
    skip: int = 0,
    limit: int = 100,
    model_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Liste l'historique des prédictions"""
    return []