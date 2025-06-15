# Service d'authentification
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional

from ..database import get_db
from ..models.database import User
from ..schemas.schemas import UserCreate
from ..config import settings

# Configuration des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash un mot de passe"""
        return pwd_context.hash(password)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Récupère un utilisateur par nom d'utilisateur"""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Récupère un utilisateur par ID"""
        result = await self.db.execute(select(User).where(User.id == UUID(user_id)))
        return result.scalars().first()
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur"""
        user = await self.get_user_by_username(username)
        if not user:
            user = await self.get_user_by_email(username)
        
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Crée un nouvel utilisateur"""
        hashed_password = self.get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        return db_user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Crée un token d'accès JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        return encoded_jwt
    
    def create_refresh_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Crée un refresh token JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        return encoded_jwt
    
    def verify_token(self, token: str):
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None

# Dependency pour obtenir l'utilisateur actuel
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    auth_service = AuthService(db)
    payload = auth_service.verify_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = await auth_service.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user

# Dependency pour obtenir l'utilisateur actuel actif
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user