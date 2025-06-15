# Exemples d'utilisation de l'AI Platform

Ce dossier contient des exemples pratiques pour utiliser l'AI Platform FastAPI.

## 🐍 Client Python Complet

### `python_client_demo.py`

Démonstration complète des fonctionnalités :

```bash
# Installer les dépendances
pip install requests pandas numpy

# Lancer la démonstration
python examples/python_client_demo.py
```

**Fonctionnalités démontrées :**
- Inscription et authentification
- Création de projets ML
- Upload de datasets
- Création et entraînement de modèles
- Prédictions en temps réel
- Prédictions en lot
- Monitoring des métriques

## ⚡ Client de Prédiction Simple

### `simple_predict.py`

Client léger pour des prédictions rapides :

```bash
# Prédiction avec le modèle de démo
python examples/simple_predict.py \
  --model "demo_model_1" \
  --features '{"feature1": 1.5, "feature2": 2.3, "feature3": 0.8, "feature4": 1.2}'

# Avec un autre modèle
python examples/simple_predict.py \
  --model "your_model_id" \
  --features '{"age": 25, "income": 50000}' \
  --url "http://your-ml-service:8001"
```

## 🌐 Exemples cURL

### Authentification

```bash
# Inscription
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "password": "securepass123",
    "full_name": "New User"
  }'

# Connexion
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=newuser&password=securepass123"
```

### Prédictions ML

```bash
# Prédiction simple
curl -X POST "http://localhost:8001/predict/demo_model_1" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {"feature1": 1.5, "feature2": 2.3},
    "return_probabilities": true
  }'

# Prédiction en lot
curl -X POST "http://localhost:8001/predict/demo_model_1/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {"feature1": 1.5, "feature2": 2.3},
      {"feature1": 2.1, "feature2": 1.8}
    ],
    "return_probabilities": true
  }'
```

## 📊 Monitoring

```bash
# Santé des services
curl http://localhost:8000/health
curl http://localhost:8001/health

# Métriques ML
curl http://localhost:8001/metrics

# Modèles chargés
curl http://localhost:8001/models
```

## 🔧 Cas d'Usage

### 1. Classification d'Images
```python
# Upload d'un dataset d'images
client.upload_dataset(
    file_path="images_dataset.csv",
    name="Image Classification Dataset",
    project_id=project_id
)

# Modèle CNN
model = client.create_model(
    name="CNN Classifier",
    model_type="classification",
    framework="tensorflow",
    parameters={
        "architecture": "cnn",
        "input_shape": [224, 224, 3],
        "num_classes": 10
    }
)
```

### 2. Analyse de Sentiment
```python
# Prédiction de sentiment
result = client.predict(
    model_id="sentiment_model",
    input_data={
        "text": "This product is amazing!",
        "length": 25,
        "language": "en"
    }
)
```

### 3. Recommandations
```python
# Système de recommandation
recommendations = client.predict(
    model_id="recommendation_model",
    input_data={
        "user_id": 12345,
        "previous_purchases": [1, 5, 23, 67],
        "demographics": {"age": 30, "location": "Paris"}
    }
)
```

## 🚀 Intégration dans vos Applications

### Application Web

```javascript
// Frontend JavaScript
async function getPrediction(features) {
  const response = await fetch('http://localhost:8001/predict/demo_model_1', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      input_data: features,
      return_probabilities: true
    })
  });
  
  return await response.json();
}
```

### Application Mobile

```python
# SDK Python pour mobile
from ai_platform_sdk import AIPlatformClient

client = AIPlatformClient("https://your-api.com")
client.login("username", "password")

prediction = client.predict(
    model_id="mobile_model",
    input_data=sensor_data
)
```

## 📈 Performance et Optimisation

### Cache des Prédictions

```python
# Utiliser le cache pour des prédictions fréquentes
prediction = client.predict(
    model_id="cached_model",
    input_data=features,
    use_cache=True  # Active le cache Redis
)
```

### Prédictions en Lot

```python
# Optimisé pour le traitement en masse
batch_size = 1000
for i in range(0, len(data), batch_size):
    batch = data[i:i+batch_size]
    results = client.batch_predict(
        model_id="batch_model",
        inputs=batch
    )
```

## 🛠️ Développement

Pour créer vos propres exemples :

1. Copiez un exemple existant
2. Adaptez les paramètres et données
3. Testez avec `make up` (services démarrés)
4. Documentez votre cas d'usage

## 🤝 Contribution

N'hésitez pas à contribuer avec vos propres exemples d'utilisation !