# Service de stockage MinIO
import aiofiles
from minio import Minio
from minio.error import S3Error
import io
from typing import Optional
import logging

from ..config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.client = None
    
    async def initialize(self):
        """Initialise la connexion MinIO"""
        try:
            self.client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            
            # Créer les buckets s'ils n'existent pas
            await self._ensure_bucket_exists(settings.MODELS_BUCKET)
            await self._ensure_bucket_exists(settings.DATASETS_BUCKET)
            
            logger.info("MinIO storage service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize MinIO: {str(e)}")
            raise
    
    async def _ensure_bucket_exists(self, bucket_name: str):
        """Vérifie et crée un bucket si nécessaire"""
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"Created bucket: {bucket_name}")
        except S3Error as e:
            logger.error(f"Error creating bucket {bucket_name}: {str(e)}")
    
    async def upload_file(self, bucket_name: str, object_name: str, data: bytes, content_type: str = None):
        """Upload un fichier vers MinIO"""
        try:
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=io.BytesIO(data),
                length=len(data),
                content_type=content_type
            )
            logger.info(f"Uploaded file: {bucket_name}/{object_name}")
            
        except S3Error as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise
    
    async def get_file(self, bucket_name: str, object_name: str) -> bytes:
        """Récupère un fichier depuis MinIO"""
        try:
            response = self.client.get_object(bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
            
        except S3Error as e:
            logger.error(f"Error getting file: {str(e)}")
            raise
    
    async def delete_file(self, bucket_name: str, object_name: str):
        """Supprime un fichier de MinIO"""
        try:
            self.client.remove_object(bucket_name, object_name)
            logger.info(f"Deleted file: {bucket_name}/{object_name}")
            
        except S3Error as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise

# Instance globale
storage_service = StorageService()