# AI Platform FastAPI

## 🚀 Plateforme d'Intelligence Artificielle d'Entreprise

Cette plateforme permet l'intégration complète de l'IA en entreprise en utilisant **FastAPI** comme framework principal, avec une architecture microservices moderne et des principes DevOps.

## 📋 Table des Matières

- [Architecture](#architecture)
- [Technologies](#technologies)
- [Démarrage Rapide](#démarrage-rapide)
- [Services](#services)
- [API Documentation](#api-documentation)
- [Monitoring](#monitoring)
- [DevOps & Déploiement](#devops--déploiement)
- [Exemples d'Utilisation](#exemples-dutilisation)

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Nginx Gateway │────▶│   API Server    │
│   (React)       │     │   (Load Balancer)│     │   (FastAPI)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   ML Service    │◀────│   PostgreSQL    │────▶│   Redis Cache   │
│   (FastAPI)     │     │   (Database)    │     │   & Queues      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
          │                                               │
          ▼                                               ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   MinIO S3      │     │   Celery Worker │     │   Monitoring    │
│   (Storage)     │     │   (Async Tasks) │     │   (Prometheus)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 🛠️ Technologies

### Backend
- **FastAPI** - Framework web moderne et performant
- **SQLAlchemy** - ORM avec support async
- **PostgreSQL** - Base de données relationnelle
- **Redis** - Cache et message broker
- **Celery** - Tâches asynchrones
- **MinIO** - Stockage S3-compatible

### ML & IA
- **Scikit-learn** - Machine Learning classique
- **XGBoost/LightGBM** - Gradient boosting
- **TensorFlow/PyTorch** - Deep Learning (extensible)
- **Pandas/NumPy** - Traitement de données

### DevOps & Monitoring
- **Docker & Docker Compose** - Containerisation
- **Nginx** - Load balancer et reverse proxy
- **Prometheus & Grafana** - Monitoring et métriques
- **ELK Stack** - Logs centralisés

## 🚀 Démarrage Rapide

### Prérequis
- Docker et Docker Compose
- Git
- 8GB RAM minimum

### Installation

1. **Cloner le repository**
```bash
git clone git@github.com:ematavfr/ai-platform-fastapi.git
cd ai-platform-fastapi
```

2. **Lancer l'infrastructure complète**
```bash
docker-compose up -d
```

3. **Vérifier que tous les services sont actifs**
```bash
docker-compose ps
```

### 🌐 Accès aux Services

| Service | URL | Description |
|---------|-----|-------------|
| API Documentation | http://localhost:8000/docs | Swagger UI de l'API principale |
| ML Service Docs | http://localhost:8001/docs | Documentation du service ML |
| Frontend | http://localhost:3000 | Interface utilisateur React |
| Grafana | http://localhost:3001 | Dashboards (admin/admin123) |
| Flower (Celery) | http://localhost:5555 | Monitoring des tâches |
| MinIO Console | http://localhost:9001 | Interface de stockage |
| Kibana | http://localhost:5601 | Visualisation des logs |

## 📊 Services

### 1. API Server (Port 8000)
Service principal gérant :
- **Authentification JWT** avec refresh tokens
- **Gestion des utilisateurs** et permissions
- **Projets ML** et cycles de vie
- **Datasets** avec upload et validation
- **Modèles ML** avec versioning
- **API REST complète** avec documentation automatique

**Fonctionnalités clés :**
- Rate limiting intelligent
- Validation Pydantic
- Gestion d'erreurs centralisée
- Métriques Prometheus
- Tâches asynchrones Celery

### 2. ML Service (Port 8001)
Service spécialisé pour :
- **Prédictions temps réel** avec cache Redis
- **Chargement dynamique** des modèles
- **Preprocessing/Postprocessing** configurable
- **Prédictions en lot** optimisées
- **Gestion mémoire** des modèles

**Optimisations :**
- LRU cache des modèles
- Pool de connexions
- Métriques de performance
- Fallback graceful

### 3. Base de Données & Stockage
- **PostgreSQL** : Métadonnées, utilisateurs, projets
- **Redis** : Cache, sessions, queues Celery
- **MinIO** : Modèles ML, datasets, artifacts

## 📚 API Documentation

### Authentification
```bash
# Inscription
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "password": "securepassword123",
    "full_name": "New User"
  }'

# Connexion
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=newuser&password=securepassword123"
```

### Création d'un Modèle
```bash
# Créer un projet
curl -X POST "http://localhost:8000/api/v1/projects/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Classification Project",
    "description": "Projet de classification d'images"
  }'

# Créer un modèle
curl -X POST "http://localhost:8000/api/v1/models/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Random Forest Classifier",
    "model_type": "classification",
    "framework": "scikit-learn",
    "project_id": "PROJECT_UUID"
  }'
```

### Prédictions
```bash
# Prédiction simple
curl -X POST "http://localhost:8001/predict/model_id" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {"feature1": 1.5, "feature2": 2.3},
    "return_probabilities": true
  }'

# Prédiction en lot
curl -X POST "http://localhost:8001/predict/model_id/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {"feature1": 1.5, "feature2": 2.3},
      {"feature1": 2.1, "feature2": 1.8}
    ]
  }'
```

## 📈 Monitoring

### Métriques Disponibles
- **Performance API** : Latence, throughput, erreurs
- **Utilisation ML** : Prédictions/sec, cache hit rate
- **Infrastructure** : CPU, mémoire, stockage
- **Business** : Utilisateurs actifs, modèles déployés

### Dashboards Grafana
1. **API Performance** - Métriques temps réel de l'API
2. **ML Service** - Performance des prédictions
3. **Infrastructure** - Santé des services
4. **Business Intelligence** - KPIs métier

## 🔧 DevOps & Déploiement

### Variables d'Environnement
Créer un fichier `.env` :
```bash
# API Server
DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/ai_platform
REDIS_URL=redis://redis:6379
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123

# Environment
ENVIRONMENT=production
DEBUG=false
```

### Déploiement Production
Pour un déploiement en production :

1. **Kubernetes** (recommandé)
```bash
# Utiliser les manifests Kubernetes (à créer)
kubectl apply -f k8s/
```

2. **Docker Swarm**
```bash
docker stack deploy -c docker-compose.prod.yml ai-platform
```

### Sécurité
- SSL/TLS terminaison sur Nginx
- Secrets gérés via Docker Secrets ou Kubernetes Secrets
- Rate limiting et protection DDoS
- Authentification JWT sécurisée
- Validation stricte des inputs

## 🧪 Exemples d'Utilisation

### 1. Classification d'Images
```python
import requests

# Upload d'un dataset
files = {'file': open('dataset.csv', 'rb')}
response = requests.post(
    'http://localhost:8000/api/v1/datasets/',
    files=files,
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

# Entraînement d'un modèle
model_data = {
    "name": "Image Classifier",
    "model_type": "classification",
    "framework": "tensorflow",
    "dataset_id": response.json()["id"]
}
model_response = requests.post(
    'http://localhost:8000/api/v1/models/',
    json=model_data,
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
```

### 2. Prédiction en Temps Réel
```python
# Prédiction
prediction_data = {
    "input_data": {
        "feature1": 1.5,
        "feature2": 2.3,
        "feature3": 0.8
    },
    "return_probabilities": True
}

response = requests.post(
    f'http://localhost:8001/predict/{model_id}',
    json=prediction_data
)

result = response.json()
print(f"Prédiction: {result['prediction']}")
print(f"Confiance: {result['confidence_score']}")
```

### 3. Pipeline ML Complet
```python
# Workflow complet automatisé
class MLPipeline:
    def __init__(self, api_base_url, token):
        self.api_url = api_base_url
        self.headers = {'Authorization': f'Bearer {token}'}
    
    def create_project(self, name, description):
        """Créer un nouveau projet"""
        return requests.post(
            f'{self.api_url}/projects/',
            json={'name': name, 'description': description},
            headers=self.headers
        ).json()
    
    def upload_dataset(self, file_path, project_id):
        """Upload dataset"""
        files = {'file': open(file_path, 'rb')}
        data = {'project_id': project_id}
        return requests.post(
            f'{self.api_url}/datasets/',
            files=files,
            data=data,
            headers=self.headers
        ).json()
    
    def train_model(self, model_config):
        """Entraîner un modèle"""
        return requests.post(
            f'{self.api_url}/models/',
            json=model_config,
            headers=self.headers
        ).json()
    
    def deploy_model(self, model_id):
        """Déployer un modèle"""
        return requests.post(
            f'{self.api_url}/models/{model_id}/deploy',
            headers=self.headers
        ).json()
```

## 🔍 Cas d'Usage Entreprise

### 1. Équipe Data Science
- Upload et versioning des datasets
- Expérimentation avec différents algorithmes
- Suivi des métriques de performance
- Collaboration sur les projets

### 2. Équipe Développement
- API REST standardisée
- Intégration facile dans les applications
- Documentation automatique
- Tests et monitoring

### 3. Équipe Ops
- Déploiement containerisé
- Monitoring complet
- Gestion des ressources
- Sécurité et compliance

## 🚨 Troubleshooting

### Problèmes Courants

**Services qui ne démarrent pas**
```bash
# Vérifier les logs
docker-compose logs api-server
docker-compose logs ml-service

# Redémarrer un service
docker-compose restart api-server
```

**Problèmes de base de données**
```bash
# Réinitialiser la DB
docker-compose down -v
docker-compose up -d postgres
```

**Problèmes de cache Redis**
```bash
# Vider le cache
docker-compose exec redis redis-cli FLUSHALL
```

## 🤝 Contributing

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

- 📧 Email: support@aiplatform.com
- 📖 Documentation: [docs.aiplatform.com](https://docs.aiplatform.com)
- 🐛 Issues: [GitHub Issues](https://github.com/ematavfr/ai-platform-fastapi/issues)

---

**Développé avec ❤️ pour l'intégration de l'IA en entreprise**