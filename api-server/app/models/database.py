# Modèles de données SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class TimestampMixin:
    """Mixin pour ajouter des timestamps automatiques"""
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base, TimestampMixin):
    """Modèle utilisateur"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String(50), default="user")  # user, data_scientist, admin
    
    # Relations
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="owner", cascade="all, delete-orphan")
    models = relationship("MLModel", back_populates="owner", cascade="all, delete-orphan")

class Project(Base, TimestampMixin):
    """Modèle projet ML"""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active")  # active, archived, completed
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Métadonnées
    tags = Column(JSON, default=list)
    config = Column(JSON, default=dict)
    
    # Relations
    owner = relationship("User", back_populates="projects")
    datasets = relationship("Dataset", back_populates="project", cascade="all, delete-orphan")
    models = relationship("MLModel", back_populates="project", cascade="all, delete-orphan")

class Dataset(Base, TimestampMixin):
    """Modèle dataset"""
    __tablename__ = "datasets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    
    # Métadonnées
    schema = Column(JSON)  # Structure des données
    statistics = Column(JSON)  # Statistiques descriptives
    tags = Column(JSON, default=list)
    
    # Relations
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    project = relationship("Project", back_populates="datasets")
    owner = relationship("User", back_populates="datasets")

class MLModel(Base, TimestampMixin):
    """Modèle ML"""
    __tablename__ = "ml_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    model_type = Column(String(100))  # classification, regression, clustering, etc.
    framework = Column(String(50))  # sklearn, tensorflow, pytorch, etc.
    version = Column(String(50), default="1.0.0")
    
    # Fichiers et chemins
    model_path = Column(String(500), nullable=False)
    artifacts_path = Column(String(500))
    
    # Métriques et performances
    metrics = Column(JSON, default=dict)
    parameters = Column(JSON, default=dict)
    
    # Status
    status = Column(String(50), default="training")  # training, trained, deployed, deprecated
    is_deployed = Column(Boolean, default=False)
    deployment_url = Column(String(500))
    
    # Relations
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"))
    
    project = relationship("Project", back_populates="models")
    owner = relationship("User", back_populates="models")
    dataset = relationship("Dataset")
    predictions = relationship("Prediction", back_populates="model", cascade="all, delete-orphan")

class Prediction(Base, TimestampMixin):
    """Modèle prédiction"""
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=False)
    confidence_score = Column(Float)
    processing_time = Column(Float)  # en millisecondes
    
    # Métadonnées
    client_ip = Column(String(45))
    user_agent = Column(Text)
    api_version = Column(String(20))
    
    # Relations
    model_id = Column(UUID(as_uuid=True), ForeignKey("ml_models.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    model = relationship("MLModel", back_populates="predictions")
    user = relationship("User")

class APIKey(Base, TimestampMixin):
    """Modèle clé API"""
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True))
    
    # Limitations
    rate_limit = Column(Integer, default=1000)  # requêtes par heure
    allowed_endpoints = Column(JSON, default=list)
    
    # Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User")