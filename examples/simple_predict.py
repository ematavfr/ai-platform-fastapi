#!/usr/bin/env python3
"""
Client simple pour les prédictions ML
"""

import requests
import json
import argparse

def predict_single(model_id: str, features: dict, ml_url: str = "http://localhost:8001"):
    """Effectue une prédiction simple"""
    
    payload = {
        "input_data": features,
        "return_probabilities": True
    }
    
    response = requests.post(f"{ml_url}/predict/{model_id}", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"🔮 Prediction: {result['prediction']}")
        
        if 'confidence_score' in result:
            print(f"📊 Confidence: {result['confidence_score']:.3f}")
        
        if 'probabilities' in result:
            print(f"📈 Probabilities: {result['probabilities']}")
        
        print(f"⏱️  Processing time: {result['processing_time']:.2f}ms")
        
        return result
    else:
        print(f"❌ Error: {response.text}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Client de prédiction ML")
    parser.add_argument("--model", required=True, help="ID du modèle")
    parser.add_argument("--features", required=True, help="Features JSON (ex: '{\"f1\": 1.5, \"f2\": 2.3}')")
    parser.add_argument("--url", default="http://localhost:8001", help="URL du service ML")
    
    args = parser.parse_args()
    
    try:
        features = json.loads(args.features)
        predict_single(args.model, features, args.url)
    except json.JSONDecodeError:
        print("❌ Erreur: Features doit être un JSON valide")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()