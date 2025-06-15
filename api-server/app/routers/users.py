# Routeur simple pour les utilisateurs
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from ..database import get_db
from ..schemas.schemas import User, UserUpdate
from ..services.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Liste des utilisateurs (admin seulement)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Implémentation basique - à compléter avec le service
    return []

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère un utilisateur par ID"""
    # Implémentation basique
    if str(user_id) != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return current_user