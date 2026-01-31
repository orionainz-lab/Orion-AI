#!/bin/bash
set -e

echo "🚀 Deploying to Production Environment..."
echo "================================================"
echo ""
echo "⚠️  WARNING: This will deploy to PRODUCTION!"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRMATION

if [ "$CONFIRMATION" != "yes" ]; then
  echo "❌ Deployment cancelled"
  exit 1
fi

# Configuration
PROD_URL="https://orion-ai.vercel.app"
API_URL="https://api-prod.railway.app"
STAGING_URL="https://orion-ai-staging.vercel.app"

# Pre-deployment checks
echo ""
echo "1️⃣ Pre-deployment checks..."
echo "------------------------------------------------"

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "❌ Error: Must be on main branch for production deployment"
  exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
  echo "❌ Error: You have uncommitted changes"
  exit 1
fi

# Verify staging is healthy
echo "Checking staging health..."
if ! ./scripts/deploy/smoke-test.sh staging > /dev/null 2>&1; then
  echo "❌ Error: Staging environment is not healthy"
  echo "Please fix staging before deploying to production"
  exit 1
fi

echo "✅ Pre-deployment checks passed"

# Create backup tag
echo ""
echo "2️⃣ Creating backup tag..."
echo "------------------------------------------------"

BACKUP_TAG="production-backup-$(date +%Y%m%d-%H%M%S)"
git tag -a "$BACKUP_TAG" -m "Backup before production deployment"
git push origin "$BACKUP_TAG"
echo "✅ Backup tag created: $BACKUP_TAG"

# Deploy Backend
echo ""
echo "3️⃣ Deploying Backend API to Railway Production..."
echo "------------------------------------------------"

railway up --service api-prod --environment production

# Wait for backend
echo ""
echo "4️⃣ Waiting for backend to be ready..."
echo "------------------------------------------------"
sleep 30

# Health check with retries
for i in {1..10}; do
  if curl -sf "$API_URL/health/detailed" > /dev/null; then
    echo "✅ Backend is healthy"
    break
  fi
  
  if [ $i -eq 10 ]; then
    echo "❌ Backend health check failed!"
    echo "Rolling back..."
    ./scripts/deploy/rollback.sh backend
    exit 1
  fi
  
  echo "Waiting for backend... (attempt $i/10)"
  sleep 10
done

# Deploy Frontend
echo ""
echo "5️⃣ Deploying Frontend to Vercel Production..."
echo "------------------------------------------------"

cd frontend
vercel --prod --token=$VERCEL_TOKEN
cd ..

echo "✅ Frontend deployed"

# Wait for DNS propagation
echo ""
echo "6️⃣ Waiting for deployment to stabilize..."
sleep 15

# Run comprehensive smoke tests
echo ""
echo "7️⃣ Running production smoke tests..."
echo "------------------------------------------------"

if ! ./scripts/deploy/smoke-test.sh production; then
  echo "❌ Smoke tests failed!"
  echo "Rolling back..."
  ./scripts/deploy/rollback.sh all
  exit 1
fi

# Monitor for 2 minutes
echo ""
echo "8️⃣ Monitoring deployment..."
echo "------------------------------------------------"

for i in {1..8}; do
  HEALTH=$(curl -sf "$API_URL/health")
  STATUS=$(echo $HEALTH | jq -r '.status')
  
  if [ "$STATUS" != "healthy" ]; then
    echo "❌ Health degraded during monitoring!"
    echo "Rolling back..."
    ./scripts/deploy/rollback.sh all
    exit 1
  fi
  
  echo "Check $i/8: Status = $STATUS ✅"
  sleep 15
done

# Success
echo ""
echo "================================================"
echo "✅ Production Deployment Complete!"
echo ""
echo "🔗 Frontend: $PROD_URL"
echo "🔗 API: $API_URL"
echo "🔗 Health: $API_URL/health/detailed"
echo ""
echo "Backup tag: $BACKUP_TAG"
echo ""
echo "Next steps:"
echo "  1. Monitor Better Stack dashboard"
echo "  2. Check Vercel Analytics"
echo "  3. Watch Railway logs"
echo "  4. Test critical user flows manually"
echo "================================================"
