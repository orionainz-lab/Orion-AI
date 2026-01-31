# Phase 6B Production Deployment Plan

**Version**: Phase 6B v1.0.0  
**Date**: 2026-01-31  
**Status**: Ready for Deployment  
**Risk Level**: Medium (new features, database migration required)

---

## 📋 Deployment Overview

### What's Being Deployed

**Phase 6B: Advanced Features**
- ✅ Analytics Dashboard with real-time metrics
- ✅ Connector Marketplace with 6 pre-built connectors
- ✅ Custom Connector Builder with AI-powered mapping
- ✅ 6 new database tables with RLS policies
- ✅ 3 new API endpoints
- ✅ 16 new React components
- ✅ Materialized view for analytics aggregation

### Deployment Method
- **Database**: Supabase migration (via Supabase CLI or Dashboard)
- **Frontend**: Vercel (automatic from main branch or manual)
- **Backend**: Railway (if backend changes required)

---

## ⚠️ Pre-Deployment Checklist

### Code Readiness
- [ ] All Phase 6B code merged to `main` branch
- [ ] No uncommitted changes
- [ ] Frontend build passing locally (`npm run build`)
- [ ] No TypeScript errors (`npx tsc --noEmit`)
- [ ] No linter errors

### Database Readiness
- [ ] Migration script tested in local environment
- [ ] Migration script tested in staging environment
- [ ] Backup of production database taken
- [ ] RLS policies reviewed and approved
- [ ] Seed data prepared (optional for production)

### Environment Variables
- [ ] `NEXT_PUBLIC_SUPABASE_URL` configured in Vercel
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY` configured in Vercel
- [ ] All Supabase secrets rotated for production
- [ ] Environment variables verified in staging

### Testing
- [ ] All features tested in local environment
- [ ] All features tested in staging environment
- [ ] Manual smoke tests passed
- [ ] No critical bugs in issue tracker
- [ ] Performance acceptable (load time < 3s)

### Team Coordination
- [ ] Deployment window scheduled
- [ ] Team notified of deployment
- [ ] On-call engineer available
- [ ] Rollback plan reviewed
- [ ] Monitoring dashboards open

---

## 🗄️ Database Migration Strategy

### Option 1: Supabase Dashboard (Recommended for First Time)

**Steps**:

1. **Backup Production Database**
   ```bash
   # Via Supabase CLI
   supabase db dump -f backup_before_phase6b.sql --db-url $PROD_DATABASE_URL
   ```

2. **Open Supabase SQL Editor**
   - Navigate to: https://supabase.com/dashboard/project/[your-project]/sql
   - Create new query

3. **Apply Migration**
   - Copy contents of `supabase/migrations/20260131_phase6b_advanced_features.sql`
   - Paste into SQL Editor
   - Review the SQL
   - Click "Run" button

4. **Verify Tables Created**
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
     AND table_name IN (
       'connector_marketplace',
       'user_installed_connectors',
       'custom_connectors',
       'schema_mappings_llm',
       'sync_metrics',
       'connector_health'
     )
   ORDER BY table_name;
   ```

5. **Verify Indexes**
   ```sql
   SELECT indexname 
   FROM pg_indexes 
   WHERE tablename IN (
     'connector_marketplace',
     'sync_metrics',
     'connector_health'
   );
   ```

6. **Verify RLS Policies**
   ```sql
   SELECT schemaname, tablename, policyname, permissive, roles, cmd
   FROM pg_policies
   WHERE tablename IN (
     'connector_marketplace',
     'user_installed_connectors',
     'custom_connectors'
   );
   ```

7. **Test Materialized View**
   ```sql
   SELECT COUNT(*) FROM connector_analytics;
   REFRESH MATERIALIZED VIEW connector_analytics;
   ```

### Option 2: Supabase CLI (Automated)

**Prerequisites**:
```bash
# Install/Update Supabase CLI
npm install -g supabase

# Login
supabase login

# Link to production project
supabase link --project-ref [your-prod-project-ref]
```

**Steps**:

1. **Backup**
   ```bash
   supabase db dump -f backup_before_phase6b_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Apply Migration**
   ```bash
   supabase db push
   ```
   
   This will:
   - Compare local migrations with production
   - Show diff of changes
   - Ask for confirmation
   - Apply migration

3. **Verify**
   ```bash
   supabase db diff --schema public
   ```

### Option 3: Manual MCP Tools (What We Used for Testing)

```bash
# Use Supabase MCP execute_sql tool
# Split migration into smaller chunks
# Apply each section separately
# Verify after each step
```

---

## 🌐 Frontend Deployment

### Option 1: Automatic via Git (Recommended)

**Steps**:

1. **Merge to Main**
   ```bash
   git checkout main
   git pull origin main
   git merge feature/phase6b
   git push origin main
   ```

2. **Vercel Auto-Deploy**
   - Vercel automatically detects push to `main`
   - Build starts automatically
   - Monitor at: https://vercel.com/dashboard/deployments

3. **Monitor Build**
   - Check build logs in Vercel dashboard
   - Verify no TypeScript errors
   - Wait for "Ready" status (~2-3 minutes)

4. **Verify Deployment**
   ```bash
   curl -I https://orion-ai.vercel.app
   curl https://orion-ai.vercel.app/analytics
   curl https://orion-ai.vercel.app/connectors/marketplace
   ```

### Option 2: Manual via Vercel CLI

**Steps**:

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd frontend
   vercel --prod
   ```

4. **Confirm**
   - Review deployment URL
   - Test in browser

### Option 3: GitHub Actions (Existing Workflow)

**Steps**:

1. **Create Release Tag**
   ```bash
   git tag -a v6b-1.0.0 -m "Phase 6B Production Release"
   git push origin v6b-1.0.0
   ```

2. **Trigger Workflow**
   - Go to: https://github.com/[your-org]/orion-ai/actions
   - Select "Deploy to Production"
   - Click "Run workflow"
   - Enter tag: `v6b-1.0.0`
   - Confirm

3. **Monitor**
   - Watch workflow progress
   - Check for any failures
   - Review deployment logs

---

## 🧪 Post-Deployment Testing

### 1. Database Verification

```sql
-- Verify table counts
SELECT 
  'connector_marketplace' as table_name, COUNT(*) as count FROM connector_marketplace
UNION ALL
SELECT 'user_installed_connectors', COUNT(*) FROM user_installed_connectors
UNION ALL
SELECT 'custom_connectors', COUNT(*) FROM custom_connectors
UNION ALL
SELECT 'sync_metrics', COUNT(*) FROM sync_metrics
UNION ALL
SELECT 'connector_health', COUNT(*) FROM connector_health;

-- Test RLS policies
-- Log in as test user and verify access
```

### 2. Frontend Smoke Tests

**Analytics Page**:
- [ ] Visit https://orion-ai.vercel.app/analytics
- [ ] Page loads without errors
- [ ] Charts render (may be empty if no data yet)
- [ ] Loading states work
- [ ] No console errors

**Marketplace Page**:
- [ ] Visit https://orion-ai.vercel.app/connectors/marketplace
- [ ] Page loads without errors
- [ ] Connectors display (will be empty until seeded)
- [ ] Search box works
- [ ] Category filters work
- [ ] No console errors

**Builder Page**:
- [ ] Visit https://orion-ai.vercel.app/connectors/builder
- [ ] Page loads without errors
- [ ] Step 1 form renders
- [ ] Navigation works
- [ ] No console errors

### 3. API Endpoint Tests

```bash
# Test marketplace API
curl https://orion-ai.vercel.app/api/marketplace

# Test analytics API (requires auth)
curl -H "Authorization: Bearer [token]" https://orion-ai.vercel.app/api/analytics

# Test analyze API (requires auth)
curl -X POST https://orion-ai.vercel.app/api/connectors/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer [token]" \
  -d '{"sampleResponse": "{\"test\": \"data\"}"}'
```

### 4. User Flow Tests

**End-to-End Tests**:

1. **Analytics Flow**:
   - [ ] Login to app
   - [ ] Navigate to Analytics
   - [ ] Verify page loads
   - [ ] Check time range selector works
   - [ ] Verify data displays (if seeded)

2. **Marketplace Flow**:
   - [ ] Login to app
   - [ ] Navigate to Marketplace
   - [ ] Search for a connector
   - [ ] Click on a connector card
   - [ ] Open install modal
   - [ ] Close modal

3. **Builder Flow**:
   - [ ] Login to app
   - [ ] Navigate to Builder
   - [ ] Enter API URL
   - [ ] Enter sample response
   - [ ] Click "Analyze API"
   - [ ] Navigate through steps
   - [ ] Verify field mappings display

---

## 📊 Monitoring & Metrics

### Health Checks

```bash
# Frontend health
curl -I https://orion-ai.vercel.app

# Check new pages
curl -I https://orion-ai.vercel.app/analytics
curl -I https://orion-ai.vercel.app/connectors/marketplace
curl -I https://orion-ai.vercel.app/connectors/builder

# API endpoints
curl https://orion-ai.vercel.app/api/marketplace
```

### Dashboards to Monitor

1. **Vercel Analytics**
   - URL: https://vercel.com/dashboard/analytics
   - Watch for:
     - Page load times (should be < 3s)
     - Error rates (should be < 1%)
     - Traffic patterns

2. **Supabase Dashboard**
   - URL: https://supabase.com/dashboard
   - Watch for:
     - Query performance
     - Connection count
     - Database size increase
     - RLS policy violations

3. **Browser Console**
   - Open DevTools on production site
   - Watch for:
     - JavaScript errors
     - Failed network requests
     - React warnings
     - Performance issues

### Key Metrics to Track

| Metric | Target | Alert If |
|--------|--------|----------|
| Page Load Time | < 3s | > 5s |
| API Response Time | < 500ms | > 2s |
| Error Rate | < 1% | > 5% |
| Database Queries | < 100ms | > 500ms |
| Uptime | 99.9% | < 99% |

---

## 🔄 Rollback Plan

### If Database Migration Fails

**Option 1: Restore from Backup**
```bash
# Restore full database
psql $PROD_DATABASE_URL < backup_before_phase6b.sql
```

**Option 2: Drop New Tables**
```sql
-- Drop in reverse order of creation
DROP MATERIALIZED VIEW IF EXISTS connector_analytics CASCADE;
DROP TABLE IF EXISTS connector_health CASCADE;
DROP TABLE IF EXISTS sync_metrics CASCADE;
DROP TABLE IF EXISTS schema_mappings_llm CASCADE;
DROP TABLE IF EXISTS custom_connectors CASCADE;
DROP TABLE IF EXISTS user_installed_connectors CASCADE;
DROP TABLE IF EXISTS connector_marketplace CASCADE;
```

### If Frontend Deployment Fails

**Option 1: Revert in Vercel**
```bash
# Via Vercel Dashboard
1. Go to Deployments
2. Find previous successful deployment
3. Click "..." menu
4. Select "Promote to Production"
```

**Option 2: Revert via Git**
```bash
git revert HEAD
git push origin main
# Vercel auto-deploys the revert
```

### If Critical Bug Found Post-Deployment

**Immediate Actions**:
1. Assess impact (how many users affected?)
2. Check if issue is frontend or backend
3. Decide: hotfix or full rollback?

**Hotfix Process**:
```bash
git checkout main
git pull
# Fix the bug
git add .
git commit -m "hotfix: [description]"
git push origin main
# Vercel auto-deploys
```

**Full Rollback**:
```bash
# Rollback frontend
cd frontend
vercel rollback [previous-deployment-url]

# Rollback database (if needed)
# Restore from backup (see above)
```

---

## 📝 Deployment Runbook

### Step-by-Step Production Deployment

**Estimated Time**: 30-45 minutes

#### Phase 1: Pre-Deployment (10 min)

1. **Final Checks**
   ```bash
   # Ensure on main branch
   git checkout main
   git pull origin main
   
   # Verify no uncommitted changes
   git status
   
   # Run local build
   cd frontend && npm run build && cd ..
   ```

2. **Create Backup Tag**
   ```bash
   git tag -a phase6b-backup-$(date +%Y%m%d-%H%M%S) -m "Backup before Phase 6B deployment"
   git push origin --tags
   ```

3. **Notify Team**
   - Post in #deployments channel
   - Inform users of brief downtime (if any)
   - Have rollback contact ready

#### Phase 2: Database Migration (10 min)

1. **Backup Production Database**
   ```bash
   supabase db dump -f backup_phase6b_$(date +%Y%m%d-%H%M%S).sql
   ```

2. **Apply Migration** (Choose one method)
   
   **Method A: Supabase Dashboard**
   - Open SQL Editor
   - Paste migration script
   - Review carefully
   - Click "Run"
   
   **Method B: Supabase CLI**
   ```bash
   supabase db push
   ```

3. **Verify Migration**
   ```sql
   -- Check tables exist
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_name LIKE '%connector%' 
   OR table_name LIKE '%sync%';
   
   -- Check indexes
   SELECT tablename, indexname FROM pg_indexes 
   WHERE tablename IN ('connector_marketplace', 'sync_metrics');
   
   -- Check RLS
   SELECT tablename, policyname FROM pg_policies 
   WHERE tablename = 'connector_marketplace';
   ```

#### Phase 3: Frontend Deployment (10 min)

1. **Deploy via Vercel**
   ```bash
   cd frontend
   vercel --prod
   ```
   
   OR let GitHub Actions handle it:
   ```bash
   git tag -a v6b-1.0.0 -m "Phase 6B Release"
   git push origin v6b-1.0.0
   # Trigger GitHub Actions workflow
   ```

2. **Monitor Build**
   - Watch Vercel dashboard
   - Check for build errors
   - Wait for "Ready" status

#### Phase 4: Verification (10 min)

1. **Test New Pages**
   ```bash
   # Check HTTP status
   curl -I https://orion-ai.vercel.app/analytics
   curl -I https://orion-ai.vercel.app/connectors/marketplace
   curl -I https://orion-ai.vercel.app/connectors/builder
   ```

2. **Manual Browser Tests**
   - Visit analytics page
   - Visit marketplace page
   - Visit builder page
   - Check browser console for errors
   - Verify navigation works

3. **API Tests**
   ```bash
   curl https://orion-ai.vercel.app/api/marketplace
   ```

#### Phase 5: Monitoring (5 min)

1. **Check Dashboards**
   - Vercel Analytics (no spike in errors)
   - Supabase Dashboard (queries running)
   - Browser Console (no errors)

2. **Run Full Smoke Test**
   ```bash
   ./scripts/deploy/smoke-test.sh production
   ```

3. **Monitor for 15 Minutes**
   - Watch error rates
   - Check performance metrics
   - Monitor user reports

#### Phase 6: Post-Deployment (5 min)

1. **Seed Production Data** (Optional)
   - If you want sample connectors in production
   - Use Supabase SQL Editor
   - Run seed scripts from `scripts/seed/`

2. **Update Documentation**
   - Mark Phase 6B as deployed
   - Update CHANGELOG
   - Update team wiki

3. **Notify Team**
   - Post success message
   - Share deployment metrics
   - Document any issues

---

## 🚨 Common Issues & Solutions

### Issue: Migration Fails Due to Missing Foreign Key

**Error**: `relation "connectors" does not exist`

**Solution**:
```sql
-- If connectors table doesn't exist, create it first
-- Or remove foreign key constraints temporarily
ALTER TABLE connector_marketplace 
DROP CONSTRAINT IF EXISTS connector_marketplace_connector_id_fkey;
```

### Issue: RLS Prevents Data Access

**Error**: `new row violates row-level security policy`

**Solution**:
```sql
-- Temporarily disable RLS for testing
ALTER TABLE connector_marketplace DISABLE ROW LEVEL SECURITY;

-- Re-enable after fixing policy
ALTER TABLE connector_marketplace ENABLE ROW LEVEL SECURITY;

-- Or use service role key for inserts
```

### Issue: Materialized View Won't Create

**Error**: `relation already exists`

**Solution**:
```sql
-- Drop and recreate
DROP MATERIALIZED VIEW IF EXISTS connector_analytics CASCADE;

-- Then run CREATE MATERIALIZED VIEW again
```

### Issue: Frontend Shows 404 for New Pages

**Cause**: Build cache issue

**Solution**:
```bash
# Clear Vercel cache
vercel --prod --force

# Or in Vercel Dashboard:
# Settings → Deployments → Clear Cache
```

### Issue: API Returns Empty Data

**Cause**: No data seeded yet

**Solution**:
```sql
-- Run seed scripts
-- See scripts/seed/seed_marketplace.sql
-- Or wait for users to create data organically
```

---

## 📈 Success Criteria

Deployment is considered successful when:

- [ ] All 6 new tables exist in production
- [ ] RLS policies are enabled and working
- [ ] Materialized view exists and is queryable
- [ ] All 3 new pages load without errors (200 status)
- [ ] Navigation to new pages works
- [ ] API endpoints return valid responses
- [ ] No JavaScript errors in browser console
- [ ] No spike in error rates in monitoring
- [ ] Performance metrics within acceptable range
- [ ] Team confirms deployment success

---

## 📞 Support Contacts

### During Deployment

- **DevOps Lead**: [Contact]
- **Database Admin**: [Contact]
- **Frontend Lead**: [Contact]
- **On-Call Engineer**: [Contact]

### Post-Deployment

- **Bug Reports**: GitHub Issues
- **User Support**: support@orion-ai.com
- **Emergency**: [On-call number]

---

## 📚 Additional Resources

- **Phase 6B Architecture**: `build_plan/phase6b-architecture.md`
- **Phase 6B Testing**: `build_plan/phase6b-tests-complete.md`
- **Migration Script**: `supabase/migrations/20260131_phase6b_advanced_features.sql`
- **General Deployment Guide**: `DEPLOYMENT.md`
- **Rollback Guide**: `scripts/deploy/rollback.sh`

---

## ✅ Final Checklist

Before you begin deployment:

- [ ] Read this entire document
- [ ] Understand rollback procedures
- [ ] Have backup contacts available
- [ ] Monitoring dashboards open
- [ ] Backup created and verified
- [ ] Team notified
- [ ] Clear 1-hour window allocated
- [ ] Coffee/energy drink ready ☕

---

**Ready to deploy? Let's go! 🚀**

**Recommended Command**:
```bash
# For automated deployment
./scripts/deploy/deploy-production.sh

# Or follow manual steps above
```

---

**Document Version**: 1.0.0  
**Created**: 2026-01-31  
**Phase**: 6B  
**Status**: Ready for Production
