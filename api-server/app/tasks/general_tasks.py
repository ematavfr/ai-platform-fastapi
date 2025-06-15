# Tâches générales
from ..celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def cleanup_expired_tokens():
    """
    Nettoie les tokens expirés de la base de données
    """
    logger.info("Cleaning up expired tokens...")
    # Implémentation du nettoyage
    return {"status": "cleanup_completed"}

@celery_app.task
def send_notification_email(email: str, subject: str, content: str):
    """
    Envoie un email de notification
    """
    logger.info(f"Sending notification email to {email}")
    # Implémentation de l'envoi d'email
    return {"status": "email_sent", "recipient": email}