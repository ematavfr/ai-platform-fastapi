# Routeur pour les modèles ML
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import json
import io

from ..database import get_db
from ..schemas.schemas import MLModel, MLModelCreate, MLModelUpdate, User
from ..services.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[MLModel])
async def list_models(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Liste tous les modèles ML avec filtres optionnels
    
    - **skip**: Nombre d'éléments à ignorer (pagination)
    - **limit**: Nombre maximum d'éléments à retourner
    - **project_id**: Filtrer par projet
    - **status**: Filtrer par statut (training, trained, deployed, deprecated)
    """
    # Implémentation basique - à compléter avec le service ML
    return []

@router.post("/", response_model=MLModel, status_code=201)
async def create_model(
    model_data: MLModelCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Crée un nouveau modèle ML
    
    Le modèle sera créé en statut 'training' et l'entraînement
    sera lancé en arrière-plan si un dataset est spécifié.
    """
    # Implémentation basique
    return {"message": "Model creation endpoint"}

@router.get("/{model_id}", response_model=MLModel)
async def get_model(
    model_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère un modèle spécifique par son ID"""
    return {"message": f"Get model {model_id}"}

@router.post("/{model_id}/upload")
async def upload_model_file(
    model_id: UUID,
    file: UploadFile = File(...),
    metadata: str = Form("{}"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload d'un fichier de modèle pré-entraîné
    
    - **file**: Fichier du modèle (.pkl, .joblib, .h5, .pt, etc.)
    - **metadata**: Métadonnées du modèle au format JSON
    """
    try:
        metadata_dict = json.loads(metadata)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON metadata")
    
    return {
        "message": "Model file uploaded successfully",
        "filename": file.filename,
        "metadata": metadata_dict
    }

@router.post("/{model_id}/deploy")
async def deploy_model(
    model_id: UUID,
    background_tasks: BackgroundTasks,
    deployment_config: dict = {},
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Déploie un modèle pour les prédictions en temps réel
    """
    return {
        "message": "Model deployment started",
        "model_id": model_id,
        "status": "deploying"
    }