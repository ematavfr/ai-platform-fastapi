# Routeur pour les datasets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from ..database import get_db
from ..schemas.schemas import Dataset, DatasetCreate, User
from ..services.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[Dataset])
async def list_datasets(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Liste tous les datasets"""
    return []

@router.post("/", response_model=Dataset, status_code=201)
async def create_dataset(
    dataset_data: DatasetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crée un nouveau dataset"""
    return {"message": "Dataset creation endpoint"}