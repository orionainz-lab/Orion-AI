#!/bin/bash
set -e

echo "🚢 Deploying to Staging Environment..."
echo "================================================"

# Configuration
STAGING_URL="https://orion-ai-staging.vercel.app"
API_URL="https://api-staging.railway.app"

# Pre-deployment checks
echo ""
echo "1️⃣ Pre-deployment checks..."
echo "------------------------------------------------"

# Check if we're on the right branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "⚠️  Warning: Not on main branch (currently on $CURRENT_BRANCH)"
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
  echo "❌ Error: You have uncommitted changes"
  echo "Please commit or stash your changes before deploying"
  exit 1
fi

echo "✅ Pre-deployment checks passed"

# Deploy Backend
echo ""
echo "2️⃣ Deploying Backend API to Railway..."
echo "------------------------------------------------"

if command -v railway &> /dev/null; then
  railway up --service api-staging --environment staging
  echo "✅ Backend deployed"
else
  echo "⚠️  Railway CLI not found. Install with: npm install -g @railway/cli"
  echo "Skipping backend deployment..."
fi

# Wait for backend
echo ""
echo "3️⃣ Waiting for backend to be ready..."
echo "------------------------------------------------"
sleep 15

# Health check
for i in {1..10}; do
  if curl -sf "$API_URL/health" > /dev/null; then
    echo "✅ Backend is healthy"
    break
  fi
  
  if [ $i -eq 10 ]; then
    echo "❌ Backend health check failed after 10 attempts"
    exit 1
  fi
  
  echo "Waiting for backend... (attempt $i/10)"
  sleep 5
done

# Deploy Frontend
echo ""
echo "4️⃣ Deploying Frontend to Vercel..."
echo "------------------------------------------------"

cd frontend

if command -v vercel &> /dev/null; then
  vercel --token=$VERCEL_TOKEN
  echo "✅ Frontend deployed"
else
  echo "⚠️  Vercel CLI not found. Install with: npm install -g vercel"
  echo "Skipping frontend deployment..."
fi

cd ..

# Run smoke tests
echo ""
echo "5️⃣ Running smoke tests..."
echo "------------------------------------------------"

./scripts/deploy/smoke-test.sh staging

# Success
echo ""
echo "================================================"
echo "✅ Staging Deployment Complete!"
echo ""
echo "🔗 Frontend: $STAGING_URL"
echo "🔗 API: $API_URL"
echo "🔗 Health: $API_URL/health/detailed"
echo ""
echo "Next steps:"
echo "  1. Test manually at $STAGING_URL"
echo "  2. Run integration tests"
echo "  3. If all looks good, deploy to production"
echo "================================================"
