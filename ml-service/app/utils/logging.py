# Utilitaire de logging
import logging
import sys
from typing import Optional

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Configure et retourne un logger"""
    
    # Nom du logger
    logger_name = name or __name__
    logger = logging.getLogger(logger_name)
    
    # Éviter la duplication des handlers
    if logger.handlers:
        return logger
    
    # Configuration du niveau
    logger.setLevel(logging.INFO)
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Ajouter le handler
    logger.addHandler(console_handler)
    
    return logger