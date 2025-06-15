# Schémas Pydantic pour validation des données
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    DATA_SCIENTIST = "data_scientist"
    ADMIN = "admin"

class ModelStatus(str, Enum):
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"

class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"

# Schémas de base
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    config: Optional[Dict[str, Any]] = {}

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    tags: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None

class Project(ProjectBase):
    id: UUID
    status: ProjectStatus
    owner_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = []

class DatasetCreate(DatasetBase):
    project_id: Optional[UUID] = None

class Dataset(DatasetBase):
    id: UUID
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    project_id: Optional[UUID] = None
    owner_id: UUID
    created_at: datetime
    
    class Config:
        orm_mode = True

class MLModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    model_type: Optional[str] = None
    framework: Optional[str] = None
    version: str = "1.0.0"

class MLModelCreate(MLModelBase):
    project_id: Optional[UUID] = None
    dataset_id: Optional[UUID] = None
    parameters: Optional[Dict[str, Any]] = {}

class MLModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    status: Optional[ModelStatus] = None
    metrics: Optional[Dict[str, Any]] = None
    is_deployed: Optional[bool] = None

class MLModel(MLModelBase):
    id: UUID
    model_path: str
    status: ModelStatus
    is_deployed: bool
    metrics: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    project_id: Optional[UUID] = None
    owner_id: UUID
    created_at: datetime
    
    class Config:
        orm_mode = True

class PredictionRequest(BaseModel):
    input_data: Dict[str, Any]
    model_id: Optional[UUID] = None
    return_confidence: bool = True

class PredictionResponse(BaseModel):
    prediction: Dict[str, Any]
    confidence_score: Optional[float] = None
    processing_time: float
    model_id: UUID
    timestamp: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    scopes: List[str] = []