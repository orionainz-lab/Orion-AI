#!/bin/bash
set -e

# Configuration
ENV=${1:-staging}

if [ "$ENV" = "production" ]; then
  FRONTEND_URL="https://orion-ai.vercel.app"
  API_URL="https://api-prod.railway.app"
elif [ "$ENV" = "staging" ]; then
  FRONTEND_URL="https://orion-ai-staging.vercel.app"
  API_URL="https://api-staging.railway.app"
else
  echo "❌ Invalid environment: $ENV"
  echo "Usage: ./smoke-test.sh [staging|production]"
  exit 1
fi

echo "🧪 Running smoke tests for $ENV..."
echo "================================================"

FAILED=0

# Test 1: Frontend Homepage
echo ""
echo "Test 1: Frontend homepage loads"
echo "------------------------------------------------"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL)
if [ $RESPONSE -eq 200 ]; then
  echo "✅ Frontend homepage: $RESPONSE"
else
  echo "❌ Frontend homepage failed: $RESPONSE"
  FAILED=$((FAILED + 1))
fi

# Test 2: API Health Check
echo ""
echo "Test 2: API health check"
echo "------------------------------------------------"
HEALTH=$(curl -sf $API_URL/health)
if [ $? -eq 0 ]; then
  STATUS=$(echo $HEALTH | jq -r '.status')
  if [ "$STATUS" = "healthy" ]; then
    echo "✅ API health: $STATUS"
  else
    echo "❌ API health check degraded: $STATUS"
    FAILED=$((FAILED + 1))
  fi
else
  echo "❌ API health check failed to connect"
  FAILED=$((FAILED + 1))
fi

# Test 3: Detailed Health Check
echo ""
echo "Test 3: Detailed health with dependencies"
echo "------------------------------------------------"
DETAILED=$(curl -sf $API_URL/health/detailed)
if [ $? -eq 0 ]; then
  echo "$DETAILED" | jq '.'
  
  # Check Supabase
  SUPABASE=$(echo $DETAILED | jq -r '.checks.supabase.healthy')
  if [ "$SUPABASE" = "true" ]; then
    echo "✅ Supabase: healthy"
  else
    echo "❌ Supabase: unhealthy"
    FAILED=$((FAILED + 1))
  fi
  
  # Check Temporal
  TEMPORAL=$(echo $DETAILED | jq -r '.checks.temporal.healthy')
  if [ "$TEMPORAL" = "true" ]; then
    echo "✅ Temporal: healthy"
  else
    echo "⚠️  Temporal: unhealthy (non-critical)"
  fi
else
  echo "❌ Detailed health check failed"
  FAILED=$((FAILED + 1))
fi

# Test 4: Matrix Grid Page
echo ""
echo "Test 4: Matrix Grid page"
echo "------------------------------------------------"
MATRIX_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL/matrix)
if [ $MATRIX_RESPONSE -eq 200 ]; then
  echo "✅ Matrix Grid page: $MATRIX_RESPONSE"
else
  echo "❌ Matrix Grid page failed: $MATRIX_RESPONSE"
  FAILED=$((FAILED + 1))
fi

# Test 5: API Root Endpoint
echo ""
echo "Test 5: API root endpoint"
echo "------------------------------------------------"
ROOT=$(curl -sf $API_URL/)
if [ $? -eq 0 ]; then
  NAME=$(echo $ROOT | jq -r '.name')
  echo "✅ API root: $NAME"
else
  echo "❌ API root endpoint failed"
  FAILED=$((FAILED + 1))
fi

# Summary
echo ""
echo "================================================"
if [ $FAILED -eq 0 ]; then
  echo "✅ All smoke tests passed!"
  echo "================================================"
  exit 0
else
  echo "❌ $FAILED test(s) failed"
  echo "================================================"
  exit 1
fi
