# Routeur pour les projets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from ..database import get_db
from ..schemas.schemas import Project, ProjectCreate, ProjectUpdate, User
from ..services.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[Project])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Liste tous les projets de l'utilisateur"""
    # Implémentation basique - à compléter
    return []

@router.post("/", response_model=Project, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crée un nouveau projet"""
    # Implémentation basique
    return {"message": "Project creation endpoint"}

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère un projet spécifique"""
    return {"message": f"Get project {project_id}"}