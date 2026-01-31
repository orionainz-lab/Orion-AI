#!/bin/bash
set -e

TARGET=${1:-all}

echo "⏪ Rolling back deployment..."
echo "================================================"

if [ "$TARGET" = "all" ] || [ "$TARGET" = "frontend" ]; then
  echo ""
  echo "Rolling back Frontend..."
  echo "------------------------------------------------"
  
  cd frontend
  if command -v vercel &> /dev/null; then
    vercel rollback --token=$VERCEL_TOKEN --yes
    echo "✅ Frontend rolled back"
  else
    echo "⚠️  Vercel CLI not found"
  fi
  cd ..
fi

if [ "$TARGET" = "all" ] || [ "$TARGET" = "backend" ]; then
  echo ""
  echo "Rolling back Backend..."
  echo "------------------------------------------------"
  
  if command -v railway &> /dev/null; then
    railway rollback --service api-prod
    echo "✅ Backend rolled back"
  else
    echo "⚠️  Railway CLI not found"
  fi
fi

# Wait for rollback
echo ""
echo "Waiting for rollback to complete..."
sleep 20

# Verify health
echo ""
echo "Verifying health after rollback..."
echo "------------------------------------------------"

if [ "$TARGET" = "all" ]; then
  ENV="production"
else
  ENV="staging"
fi

./scripts/deploy/smoke-test.sh $ENV

echo ""
echo "================================================"
echo "✅ Rollback complete"
echo "================================================"
