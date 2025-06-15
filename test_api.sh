#!/bin/bash

# Script de test de l'API Platform
set -e

BASE_URL="http://localhost:8000"
ML_URL="http://localhost:8001"

echo "🧪 Tests de l'AI Platform FastAPI"
echo "================================="

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function test_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    echo -n "Testing $description... "
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$status" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} ($status)"
        return 0
    else
        echo -e "${RED}✗${NC} (got $status, expected $expected_status)"
        return 1
    fi
}

function test_json_endpoint() {
    local url=$1
    local description=$2
    
    echo -n "Testing $description... "
    
    response=$(curl -s "$url")
    
    if echo "$response" | jq . >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} (valid JSON)"
        return 0
    else
        echo -e "${RED}✗${NC} (invalid JSON)"
        echo "Response: $response"
        return 1
    fi
}

echo ""
echo "🔍 1. Health Checks"
echo "------------------"

test_json_endpoint "$BASE_URL/health" "API Server Health"
test_json_endpoint "$ML_URL/health" "ML Service Health"

echo ""
echo "📚 2. Documentation Endpoints"
echo "----------------------------"

test_endpoint "$BASE_URL/docs" 200 "API Documentation"
test_endpoint "$ML_URL/docs" 200 "ML Service Documentation"

echo ""
echo "🔐 3. Authentication Endpoints"
echo "-----------------------------"

test_endpoint "$BASE_URL/api/v1/auth/register" 422 "Auth Register (no data)"

echo ""
echo "🤖 4. ML Service Endpoints"
echo "-------------------------"

test_json_endpoint "$ML_URL/models" "ML Models List"

echo ""
echo "📊 5. Metrics Endpoints"
echo "----------------------"

test_json_endpoint "$ML_URL/metrics" "ML Service Metrics"

echo ""
echo "🎯 6. Integration Test - User Registration & Login"
echo "================================================="

# Test d'inscription
echo -n "User registration... "
register_response=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User"
    }')

if echo "$register_response" | jq -e '.id' >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
    
    # Test de connexion
    echo -n "User login... "
    login_response=$(curl -s -X POST "$BASE_URL/api/v1/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=testuser&password=testpassword123")
    
    if echo "$login_response" | jq -e '.access_token' >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        
        # Extraire le token
        token=$(echo "$login_response" | jq -r '.access_token')
        
        # Test d'endpoint authentifié
        echo -n "Authenticated endpoint... "
        auth_response=$(curl -s -H "Authorization: Bearer $token" "$BASE_URL/api/v1/auth/me")
        
        if echo "$auth_response" | jq -e '.email' >/dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
        fi
    else
        echo -e "${RED}✗${NC}"
        echo "Login response: $login_response"
    fi
else
    echo -e "${RED}✗${NC}"
    echo "Registration response: $register_response"
fi

echo ""
echo "🎯 7. ML Prediction Test"
echo "======================="

echo -n "Demo model prediction... "
prediction_response=$(curl -s -X POST "$ML_URL/predict/demo_model_1" \
    -H "Content-Type: application/json" \
    -d '{
        "input_data": {"feature1": 1.5, "feature2": 2.3, "feature3": 0.8, "feature4": 1.2},
        "return_probabilities": true
    }')

if echo "$prediction_response" | jq -e '.prediction' >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
    echo "Prediction result:"
    echo "$prediction_response" | jq '.'
else
    echo -e "${RED}✗${NC}"
    echo "Prediction response: $prediction_response"
fi

echo ""
echo "📈 8. Service Status Summary"
echo "==========================="

# Résumé des services
services=("postgres:5432" "redis:6379" "minio:9000" "grafana:3001" "prometheus:9090")

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    echo -n "Checking $name:$port... "
    
    if nc -z localhost "$port" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
done

echo ""
echo "🎉 Tests completed!"
echo "=================="
echo ""
echo "📊 Access your services:"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • ML Docs:  http://localhost:8001/docs" 
echo "  • Grafana:  http://localhost:3001 (admin/admin123)"
echo "  • MinIO:    http://localhost:9001 (minioadmin/minioadmin123)"
echo "  • Flower:   http://localhost:5555"
echo ""