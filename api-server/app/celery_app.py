# Configuration Celery pour tâches asynchrones
from celery import Celery
from .config import celery_config

# Création de l'instance Celery
celery_app = Celery("ai_platform")

# Configuration
celery_app.config_from_object(celery_config)

# Auto-découverte des tâches
celery_app.autodiscover_tasks(['app.tasks'])

# Configuration des tâches périodiques (optionnel)
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'cleanup-expired-tokens': {
        'task': 'app.tasks.general_tasks.cleanup_expired_tokens',
        'schedule': crontab(minute=0, hour=0),  # Tous les jours à minuit
    },
    'update-model-metrics': {
        'task': 'app.tasks.ml_tasks.update_model_metrics',
        'schedule': crontab(minute=0, hour='*/6'),  # Toutes les 6 heures
    },
}