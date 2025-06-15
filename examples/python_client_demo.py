#!/usr/bin/env python3
"""
Exemple d'utilisation du client Python pour l'AI Platform FastAPI

Cet exemple montre comment :
1. S'authentifier auprès de l'API
2. Créer un projet ML
3. Uploader un dataset  
4. Créer et entraîner un modèle
5. Effectuer des prédictions
6. Monitorer les performances
"""

import requests
import json
import time
import pandas as pd
from typing import Optional, Dict, Any
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIPlatformClient:
    """Client Python pour l'AI Platform FastAPI"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000", ml_base_url: str = "http://localhost:8001"):
        self.api_url = api_base_url
        self.ml_url = ml_base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
    
    def register(self, email: str, username: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """Inscription d'un nouvel utilisateur"""
        data = {
            "email": email,
            "username": username,
            "password": password,
            "full_name": full_name or username
        }
        
        response = requests.post(f"{self.api_url}/api/v1/auth/register", json=data)
        
        if response.status_code == 201:
            logger.info(f"✅ User {username} registered successfully")
            return response.json()
        else:
            logger.error(f"❌ Registration failed: {response.text}")
            response.raise_for_status()
    
    def login(self, username: str, password: str) -> str:
        """Connexion et récupération du token JWT"""
        data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(
            f"{self.api_url}/api/v1/auth/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            self.headers["Authorization"] = f"Bearer {self.token}"
            logger.info("✅ Login successful")
            return self.token
        else:
            logger.error(f"❌ Login failed: {response.text}")
            response.raise_for_status()
    
    def get_profile(self) -> Dict[str, Any]:
        """Récupère le profil de l'utilisateur connecté"""
        if not self.token:
            raise ValueError("Must be logged in")
        
        response = requests.get(f"{self.api_url}/api/v1/auth/me", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_project(self, name: str, description: str = None, tags: list = None) -> Dict[str, Any]:
        """Crée un nouveau projet ML"""
        data = {
            "name": name,
            "description": description or f"Project {name}",
            "tags": tags or []
        }
        
        response = requests.post(f"{self.api_url}/api/v1/projects/", json=data, headers=self.headers)
        
        if response.status_code == 201:
            project = response.json()
            logger.info(f"✅ Project '{name}' created with ID: {project.get('id')}")
            return project
        else:
            logger.error(f"❌ Project creation failed: {response.text}")
            response.raise_for_status()
    
    def upload_dataset(self, file_path: str, name: str, description: str = None, project_id: str = None) -> Dict[str, Any]:
        """Upload un dataset"""
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'text/csv')}
            data = {
                "name": name,
                "description": description or f"Dataset {name}",
                "project_id": project_id
            }
            
            # Retirer l'Authorization du header pour cette requête multipart
            headers = {"Authorization": self.headers["Authorization"]}
            
            response = requests.post(
                f"{self.api_url}/api/v1/datasets/",
                files=files,
                data=data,
                headers=headers
            )
        
        if response.status_code == 201:
            dataset = response.json()
            logger.info(f"✅ Dataset '{name}' uploaded with ID: {dataset.get('id')}")
            return dataset
        else:
            logger.error(f"❌ Dataset upload failed: {response.text}")
            response.raise_for_status()
    
    def create_model(self, name: str, model_type: str, framework: str = "scikit-learn", 
                    project_id: str = None, dataset_id: str = None, **kwargs) -> Dict[str, Any]:
        """Crée un nouveau modèle ML"""
        data = {
            "name": name,
            "model_type": model_type,
            "framework": framework,
            "project_id": project_id,
            "dataset_id": dataset_id,
            **kwargs
        }
        
        response = requests.post(f"{self.api_url}/api/v1/models/", json=data, headers=self.headers)
        
        if response.status_code == 201:
            model = response.json()
            logger.info(f"✅ Model '{name}' created with ID: {model.get('id')}")
            return model
        else:
            logger.error(f"❌ Model creation failed: {response.text}")
            response.raise_for_status()
    
    def deploy_model(self, model_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Déploie un modèle pour les prédictions"""
        response = requests.post(
            f"{self.api_url}/api/v1/models/{model_id}/deploy",
            json=config or {},
            headers=self.headers
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Model {model_id} deployment started")
            return result
        else:
            logger.error(f"❌ Model deployment failed: {response.text}")
            response.raise_for_status()
    
    def predict(self, model_id: str, input_data: Dict[str, Any], return_probabilities: bool = False) -> Dict[str, Any]:
        """Effectue une prédiction"""
        data = {
            "input_data": input_data,
            "return_probabilities": return_probabilities
        }
        
        response = requests.post(f"{self.ml_url}/predict/{model_id}", json=data)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Prediction completed in {result.get('processing_time', 0):.2f}ms")
            return result
        else:
            logger.error(f"❌ Prediction failed: {response.text}")
            response.raise_for_status()
    
    def batch_predict(self, model_id: str, inputs: list, return_probabilities: bool = False) -> Dict[str, Any]:
        """Effectue des prédictions en lot"""
        data = {
            "inputs": inputs,
            "return_probabilities": return_probabilities
        }
        
        response = requests.post(f"{self.ml_url}/predict/{model_id}/batch", json=data)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Batch prediction completed: {len(inputs)} predictions in {result.get('total_processing_time', 0):.2f}ms")
            return result
        else:
            logger.error(f"❌ Batch prediction failed: {response.text}")
            response.raise_for_status()
    
    def get_ml_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques du service ML"""
        response = requests.get(f"{self.ml_url}/metrics")
        response.raise_for_status()
        return response.json()
    
    def check_health(self) -> Dict[str, bool]:
        """Vérifie la santé des services"""
        health = {"api": False, "ml": False}
        
        try:
            api_response = requests.get(f"{self.api_url}/health", timeout=5)
            health["api"] = api_response.status_code == 200
        except:
            pass
        
        try:
            ml_response = requests.get(f"{self.ml_url}/health", timeout=5)
            health["ml"] = ml_response.status_code == 200
        except:
            pass
        
        return health

def create_sample_dataset() -> str:
    """Crée un dataset d'exemple pour les tests"""
    import numpy as np
    
    # Générer des données d'exemple
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'feature1': np.random.normal(0, 1, n_samples),
        'feature2': np.random.normal(1, 1.5, n_samples),
        'feature3': np.random.uniform(-2, 2, n_samples),
        'feature4': np.random.exponential(1, n_samples),
        'target': np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
    }
    
    df = pd.DataFrame(data)
    filename = "/tmp/sample_dataset.csv"
    df.to_csv(filename, index=False)
    
    logger.info(f"✅ Sample dataset created: {filename}")
    return filename

def main():
    """Exemple d'utilisation complète de l'API"""
    
    print("🚀 AI Platform FastAPI - Exemple d'utilisation")
    print("=" * 50)
    
    # Initialiser le client
    client = AIPlatformClient()
    
    # 1. Vérifier la santé des services
    print("\n1. 🏥 Health Check")
    health = client.check_health()
    print(f"   API Server: {'✅' if health['api'] else '❌'}")
    print(f"   ML Service: {'✅' if health['ml'] else '❌'}")
    
    if not all(health.values()):
        print("❌ Some services are down. Please start them with: make up")
        return
    
    # 2. Inscription et connexion
    print("\n2. 🔐 Authentication")
    username = f"demo_user_{int(time.time())}"
    email = f"{username}@example.com"
    password = "demopassword123"
    
    try:
        # Inscription
        user = client.register(email, username, password, "Demo User")
        print(f"   ✅ User registered: {user.get('username')}")
        
        # Connexion
        token = client.login(username, password)
        print(f"   ✅ Login successful")
        
        # Profil
        profile = client.get_profile()
        print(f"   ✅ Profile: {profile.get('full_name')} ({profile.get('role')})")
        
    except requests.exceptions.HTTPError as e:
        if "already registered" in str(e):
            print(f"   ℹ️  User already exists, logging in...")
            client.login(username, password)
        else:
            raise
    
    # 3. Créer un projet
    print("\n3. 📁 Project Creation")
    project = client.create_project(
        name=f"Demo Project {int(time.time())}",
        description="Projet de démonstration de l'API",
        tags=["demo", "test", "classification"]
    )
    project_id = project.get("id")
    
    # 4. Upload dataset
    print("\n4. 📊 Dataset Upload")
    dataset_file = create_sample_dataset()
    dataset = client.upload_dataset(
        file_path=dataset_file,
        name="Demo Dataset",
        description="Dataset de démonstration avec 4 features",
        project_id=project_id
    )
    dataset_id = dataset.get("id")
    
    # 5. Créer un modèle
    print("\n5. 🤖 Model Creation")
    model = client.create_model(
        name="Demo Random Forest",
        model_type="classification",
        framework="scikit-learn",
        project_id=project_id,
        dataset_id=dataset_id,
        parameters={
            "n_estimators": 100,
            "max_depth": 10,
            "random_state": 42
        }
    )
    model_id = model.get("id")
    
    # 6. Simuler l'entraînement (déploiement du modèle démo)
    print("\n6. 🚀 Model Deployment")
    deployment = client.deploy_model(model_id)
    print(f"   ✅ Deployment status: {deployment.get('status')}")
    
    # 7. Prédictions
    print("\n7. 🔮 Predictions")
    
    # Prédiction simple
    single_prediction = client.predict(
        model_id="demo_model_1",  # Utiliser le modèle de démo préchargé
        input_data={
            "feature1": 1.5,
            "feature2": 2.3,
            "feature3": 0.8,
            "feature4": 1.2
        },
        return_probabilities=True
    )
    
    print(f"   ✅ Single prediction: {single_prediction.get('prediction')}")
    print(f"   ⏱️  Processing time: {single_prediction.get('processing_time'):.2f}ms")
    
    # Prédictions en lot
    batch_inputs = [
        {"feature1": 1.5, "feature2": 2.3, "feature3": 0.8, "feature4": 1.2},
        {"feature1": -0.5, "feature2": 1.1, "feature3": -1.2, "feature4": 0.8},
        {"feature1": 2.1, "feature2": 0.9, "feature3": 1.5, "feature4": 2.1}
    ]
    
    batch_predictions = client.batch_predict(
        model_id="demo_model_1",
        inputs=batch_inputs,
        return_probabilities=True
    )
    
    print(f"   ✅ Batch predictions: {len(batch_predictions.get('predictions', []))} results")
    print(f"   ⏱️  Total time: {batch_predictions.get('total_processing_time'):.2f}ms")
    print(f"   ⚡ Avg per prediction: {batch_predictions.get('average_time_per_prediction'):.2f}ms")
    
    # 8. Métriques
    print("\n8. 📊 Metrics")
    metrics = client.get_ml_metrics()
    
    global_metrics = metrics.get("global", {})
    print(f"   🕐 Uptime: {global_metrics.get('uptime_seconds', 0):.0f}s")
    print(f"   📈 Total requests: {global_metrics.get('total_requests', 0)}")
    print(f"   💾 Cache hit rate: {global_metrics.get('cache_hit_rate', 0)*100:.1f}%")
    
    print("\n🎉 Démonstration terminée avec succès!")
    print("\n📊 Accédez aux interfaces web:")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • ML Docs:  http://localhost:8001/docs")
    print("   • Grafana:  http://localhost:3001 (admin/admin123)")
    print("   • Flower:   http://localhost:5555")

if __name__ == "__main__":
    main()