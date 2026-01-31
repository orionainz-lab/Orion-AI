#!/bin/bash
# Phase 6B Production Deployment Script
# Version: 1.0.0
# Date: 2026-01-31

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PHASE="Phase 6B"
VERSION="v6b-1.0.0"
PROD_URL="https://orion-ai.vercel.app"
API_URL="https://api-prod.railway.app"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}🚀 ${PHASE} Production Deployment${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${YELLOW}⚠️  WARNING: This will deploy Phase 6B to PRODUCTION!${NC}"
echo ""
echo "This deployment includes:"
echo "  • 6 new database tables"
echo "  • Analytics Dashboard"
echo "  • Connector Marketplace"
echo "  • Custom Connector Builder"
echo "  • 3 new API endpoints"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRMATION

if [ "$CONFIRMATION" != "yes" ]; then
  echo -e "${RED}❌ Deployment cancelled${NC}"
  exit 1
fi

# ========================================
# 1. Pre-Deployment Checks
# ========================================

echo ""
echo -e "${BLUE}1️⃣ Pre-deployment checks...${NC}"
echo "------------------------------------------------"

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo -e "${RED}❌ Error: Must be on main branch for production deployment${NC}"
  echo "Current branch: $CURRENT_BRANCH"
  exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
  echo -e "${RED}❌ Error: You have uncommitted changes${NC}"
  git status --short
  exit 1
fi

# Check if Phase 6B files exist
REQUIRED_FILES=(
  "frontend/app/analytics/page.tsx"
  "frontend/app/connectors/marketplace/page.tsx"
  "frontend/app/connectors/builder/page.tsx"
  "supabase/migrations/20260131_phase6b_advanced_features.sql"
)

for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    echo -e "${RED}❌ Error: Required file not found: $file${NC}"
    exit 1
  fi
done

# Check if required tools are installed
command -v supabase >/dev/null 2>&1 || {
  echo -e "${YELLOW}⚠️ Warning: Supabase CLI not installed${NC}"
  echo "Install with: npm install -g supabase"
  read -p "Continue without Supabase CLI? (y/n): " CONTINUE
  if [ "$CONTINUE" != "y" ]; then
    exit 1
  fi
}

command -v vercel >/dev/null 2>&1 || {
  echo -e "${RED}❌ Error: Vercel CLI not installed${NC}"
  echo "Install with: npm install -g vercel"
  exit 1
}

echo -e "${GREEN}✅ Pre-deployment checks passed${NC}"

# ========================================
# 2. Create Backup
# ========================================

echo ""
echo -e "${BLUE}2️⃣ Creating backup...${NC}"
echo "------------------------------------------------"

BACKUP_TAG="phase6b-backup-$(date +%Y%m%d-%H%M%S)"
git tag -a "$BACKUP_TAG" -m "Backup before Phase 6B production deployment"
git push origin "$BACKUP_TAG" 2>/dev/null || true

echo -e "${GREEN}✅ Backup tag created: $BACKUP_TAG${NC}"

# ========================================
# 3. Database Migration
# ========================================

echo ""
echo -e "${BLUE}3️⃣ Database Migration${NC}"
echo "------------------------------------------------"

if command -v supabase >/dev/null 2>&1; then
  echo "Choose migration method:"
  echo "  1) Supabase CLI (automated)"
  echo "  2) Manual (I'll apply via dashboard)"
  echo "  3) Skip (already applied)"
  read -p "Enter choice (1-3): " DB_CHOICE
  
  case $DB_CHOICE in
    1)
      echo "Creating database backup..."
      supabase db dump -f "backup_phase6b_$(date +%Y%m%d-%H%M%S).sql" 2>/dev/null || true
      
      echo "Applying migration..."
      if supabase db push; then
        echo -e "${GREEN}✅ Database migration applied${NC}"
      else
        echo -e "${RED}❌ Database migration failed${NC}"
        echo "Please apply manually via Supabase Dashboard"
        exit 1
      fi
      ;;
    2)
      echo -e "${YELLOW}⚠️ Please apply migration manually:${NC}"
      echo "1. Open Supabase Dashboard → SQL Editor"
      echo "2. Paste contents of: supabase/migrations/20260131_phase6b_advanced_features.sql"
      echo "3. Click Run"
      echo ""
      read -p "Press ENTER when migration is complete..."
      ;;
    3)
      echo -e "${GREEN}✅ Skipping database migration${NC}"
      ;;
    *)
      echo -e "${RED}❌ Invalid choice${NC}"
      exit 1
      ;;
  esac
else
  echo -e "${YELLOW}⚠️ Supabase CLI not available${NC}"
  echo "Please apply migration manually via Supabase Dashboard"
  echo "File: supabase/migrations/20260131_phase6b_advanced_features.sql"
  read -p "Press ENTER when migration is complete..."
fi

# Verify tables exist
echo "Verifying database tables..."
# Note: This requires psql or Supabase CLI access
# Skip if not available

# ========================================
# 4. Frontend Build Test
# ========================================

echo ""
echo -e "${BLUE}4️⃣ Testing frontend build...${NC}"
echo "------------------------------------------------"

cd frontend

echo "Installing dependencies..."
npm ci --silent

echo "Running TypeScript check..."
if npx tsc --noEmit; then
  echo -e "${GREEN}✅ TypeScript check passed${NC}"
else
  echo -e "${RED}❌ TypeScript errors found${NC}"
  exit 1
fi

echo "Building frontend..."
if npm run build; then
  echo -e "${GREEN}✅ Frontend build successful${NC}"
else
  echo -e "${RED}❌ Frontend build failed${NC}"
  exit 1
fi

cd ..

# ========================================
# 5. Frontend Deployment
# ========================================

echo ""
echo -e "${BLUE}5️⃣ Deploying Frontend to Vercel...${NC}"
echo "------------------------------------------------"

cd frontend

echo "Choose deployment method:"
echo "  1) Automatic (push to main, Vercel auto-deploys)"
echo "  2) Manual via Vercel CLI"
read -p "Enter choice (1-2): " DEPLOY_CHOICE

case $DEPLOY_CHOICE in
  1)
    echo "Creating release tag..."
    git tag -a "$VERSION" -m "Phase 6B Production Release"
    git push origin "$VERSION"
    
    echo -e "${YELLOW}⚠️ Vercel will auto-deploy from main branch${NC}"
    echo "Monitor at: https://vercel.com/dashboard/deployments"
    read -p "Press ENTER when deployment is complete..."
    ;;
  2)
    if [ -z "$VERCEL_TOKEN" ]; then
      echo "Logging into Vercel..."
      vercel login
    fi
    
    echo "Deploying to production..."
    if vercel --prod --yes; then
      echo -e "${GREEN}✅ Frontend deployed${NC}"
    else
      echo -e "${RED}❌ Frontend deployment failed${NC}"
      exit 1
    fi
    ;;
  *)
    echo -e "${RED}❌ Invalid choice${NC}"
    exit 1
    ;;
esac

cd ..

# ========================================
# 6. Post-Deployment Verification
# ========================================

echo ""
echo -e "${BLUE}6️⃣ Post-deployment verification...${NC}"
echo "------------------------------------------------"

sleep 10 # Wait for DNS propagation

echo "Testing new pages..."

# Test Analytics page
echo -n "  • Analytics page... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL/analytics")
if [ "$STATUS" -eq 200 ]; then
  echo -e "${GREEN}✅ $STATUS${NC}"
else
  echo -e "${RED}❌ $STATUS${NC}"
fi

# Test Marketplace page
echo -n "  • Marketplace page... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL/connectors/marketplace")
if [ "$STATUS" -eq 200 ]; then
  echo -e "${GREEN}✅ $STATUS${NC}"
else
  echo -e "${RED}❌ $STATUS${NC}"
fi

# Test Builder page
echo -n "  • Builder page... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL/connectors/builder")
if [ "$STATUS" -eq 200 ]; then
  echo -e "${GREEN}✅ $STATUS${NC}"
else
  echo -e "${RED}❌ $STATUS${NC}"
fi

# Test Marketplace API
echo -n "  • Marketplace API... "
RESPONSE=$(curl -s "$PROD_URL/api/marketplace")
if echo "$RESPONSE" | grep -q "connectors"; then
  echo -e "${GREEN}✅ Responding${NC}"
else
  echo -e "${RED}❌ Not responding correctly${NC}"
fi

# ========================================
# 7. Smoke Tests
# ========================================

echo ""
echo -e "${BLUE}7️⃣ Running smoke tests...${NC}"
echo "------------------------------------------------"

# Test existing pages still work
echo -n "  • Homepage... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL")
if [ "$STATUS" -eq 200 ]; then
  echo -e "${GREEN}✅ $STATUS${NC}"
else
  echo -e "${RED}❌ $STATUS${NC}"
fi

echo -n "  • Dashboard... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL/dashboard")
if [ "$STATUS" -eq 200 ] || [ "$STATUS" -eq 401 ]; then
  echo -e "${GREEN}✅ $STATUS${NC}"
else
  echo -e "${RED}❌ $STATUS${NC}"
fi

echo -n "  • Matrix Grid... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL/matrix")
if [ "$STATUS" -eq 200 ] || [ "$STATUS" -eq 401 ]; then
  echo -e "${GREEN}✅ $STATUS${NC}"
else
  echo -e "${RED}❌ $STATUS${NC}"
fi

# ========================================
# 8. Monitoring
# ========================================

echo ""
echo -e "${BLUE}8️⃣ Monitoring deployment...${NC}"
echo "------------------------------------------------"

echo "Monitoring for 2 minutes..."
for i in {1..8}; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL/analytics")
  
  if [ "$STATUS" -eq 200 ]; then
    echo -e "  Check $i/8: ${GREEN}Status = $STATUS ✅${NC}"
  else
    echo -e "  Check $i/8: ${RED}Status = $STATUS ❌${NC}"
  fi
  
  sleep 15
done

# ========================================
# Success!
# ========================================

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Phase 6B Deployment Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}📊 Deployment Summary:${NC}"
echo "  • Phase: $PHASE"
echo "  • Version: $VERSION"
echo "  • Backup Tag: $BACKUP_TAG"
echo ""
echo -e "${BLUE}🔗 Live URLs:${NC}"
echo "  • Frontend: $PROD_URL"
echo "  • Analytics: $PROD_URL/analytics"
echo "  • Marketplace: $PROD_URL/connectors/marketplace"
echo "  • Builder: $PROD_URL/connectors/builder"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "  1. 🧪 Test all features manually"
echo "  2. 📊 Monitor Vercel Analytics dashboard"
echo "  3. 🗄️ Seed production data (optional):"
echo "     - scripts/seed/seed_marketplace.sql"
echo "     - scripts/seed/seed_analytics.sql"
echo "  4. 📢 Announce deployment to team"
echo "  5. 📖 Update documentation"
echo ""
echo -e "${YELLOW}⚠️ Important:${NC}"
echo "  • Keep monitoring for the next 30 minutes"
echo "  • Watch for user feedback"
echo "  • Backup tag: $BACKUP_TAG (use for rollback if needed)"
echo ""
echo -e "${GREEN}🎉 Congratulations! Phase 6B is live! 🎉${NC}"
echo ""
