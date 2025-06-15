# Makefile pour AI Platform FastAPI
.PHONY: help build up down restart logs shell test clean

# Variables
COMPOSE_FILE = docker-compose.yml
API_SERVICE = api-server
ML_SERVICE = ml-service

help: ## Affiche cette aide
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Construit toutes les images Docker
	docker-compose -f $(COMPOSE_FILE) build

up: ## Lance tous les services
	docker-compose -f $(COMPOSE_FILE) up -d

down: ## Arrête tous les services
	docker-compose -f $(COMPOSE_FILE) down

restart: ## Redémarre tous les services
	docker-compose -f $(COMPOSE_FILE) restart

logs: ## Affiche les logs de tous les services
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-api: ## Affiche les logs de l'API server
	docker-compose -f $(COMPOSE_FILE) logs -f $(API_SERVICE)

logs-ml: ## Affiche les logs du ML service
	docker-compose -f $(COMPOSE_FILE) logs -f $(ML_SERVICE)

shell-api: ## Ouvre un shell dans le conteneur API
	docker-compose -f $(COMPOSE_FILE) exec $(API_SERVICE) /bin/bash

shell-ml: ## Ouvre un shell dans le conteneur ML
	docker-compose -f $(COMPOSE_FILE) exec $(ML_SERVICE) /bin/bash

ps: ## Affiche le statut des services
	docker-compose -f $(COMPOSE_FILE) ps

health: ## Vérifie la santé des services
	@echo "=== API Server Health ==="
	@curl -s http://localhost:8000/health | jq . || echo "API Server unavailable"
	@echo "\n=== ML Service Health ==="
	@curl -s http://localhost:8001/health | jq . || echo "ML Service unavailable"

test-api: ## Lance les tests de l'API
	docker-compose -f $(COMPOSE_FILE) exec $(API_SERVICE) python -m pytest

clean: ## Nettoie les volumes et images inutilisés
	docker-compose -f $(COMPOSE_FILE) down -v
	docker system prune -f

clean-all: ## Nettoie tout (ATTENTION: supprime les données)
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all
	docker system prune -af

dev-setup: ## Configuration initiale pour le développement
	cp .env.example .env
	make build
	make up
	@echo "✅ Environment ready! Visit http://localhost:8000/docs"

prod-deploy: ## Déploiement production (à adapter selon l'environnement)
	@echo "🚀 Production deployment"
	docker-compose -f docker-compose.prod.yml up -d

backup-db: ## Sauvegarde la base de données
	docker-compose exec postgres pg_dump -U postgres ai_platform > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restaure la base de données (spécifier BACKUP_FILE=filename.sql)
	@if [ -z "$(BACKUP_FILE)" ]; then echo "Usage: make restore-db BACKUP_FILE=backup.sql"; exit 1; fi
	docker-compose exec -T postgres psql -U postgres ai_platform < $(BACKUP_FILE)

scale-ml: ## Scale le service ML (spécifier REPLICAS=number)
	@if [ -z "$(REPLICAS)" ]; then echo "Usage: make scale-ml REPLICAS=3"; exit 1; fi
	docker-compose -f $(COMPOSE_FILE) up -d --scale $(ML_SERVICE)=$(REPLICAS)