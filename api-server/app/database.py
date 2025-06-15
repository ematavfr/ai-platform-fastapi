from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

# Création du moteur de base de données asynchrone
engine = create_async_engine(
    settings.database_url_async,
    echo=settings.is_development,
    future=True
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base pour les modèles
Base = declarative_base()

# Dependency pour obtenir une session de base de données
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()