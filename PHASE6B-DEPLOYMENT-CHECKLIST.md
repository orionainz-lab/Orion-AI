# Phase 6B Deployment Checklist

**Deployment Date**: _____________  
**Deployed By**: _____________  
**Start Time**: _____________  
**End Time**: _____________

---

## ✅ Pre-Deployment (Est. 10 min)

### Code Readiness
- [ ] All Phase 6B code merged to `main` branch
- [ ] No uncommitted changes (`git status` is clean)
- [ ] Frontend builds successfully (`cd frontend && npm run build`)
- [ ] No TypeScript errors (`cd frontend && npx tsc --noEmit`)
- [ ] All required files present:
  - [ ] `frontend/app/analytics/page.tsx`
  - [ ] `frontend/app/connectors/marketplace/page.tsx`
  - [ ] `frontend/app/connectors/builder/page.tsx`
  - [ ] `frontend/app/api/marketplace/route.ts`
  - [ ] `supabase/migrations/20260131_phase6b_advanced_features.sql`

### Environment Checks
- [ ] Supabase CLI installed (`supabase --version`)
- [ ] Vercel CLI installed (`vercel --version`)
- [ ] Logged into Vercel (`vercel whoami`)
- [ ] Production Supabase project accessible
- [ ] Environment variables verified in Vercel

### Team Coordination
- [ ] Deployment window scheduled: _______________
- [ ] Team notified in #deployments channel
- [ ] On-call engineer available: _______________
- [ ] Monitoring dashboards open:
  - [ ] Vercel Dashboard
  - [ ] Supabase Dashboard
  - [ ] Browser DevTools Console

### Backup & Rollback
- [ ] Git backup tag created: _______________
- [ ] Database backup created (if possible)
- [ ] Rollback plan reviewed
- [ ] Previous deployment URL noted: _______________

---

## 🗄️ Database Migration (Est. 10 min)

### Backup Production Database
- [ ] Backup created: `supabase db dump -f backup_phase6b.sql`
- [ ] Backup file size verified (not empty)
- [ ] Backup stored safely

### Apply Migration
Choose one method:

**Method 1: Supabase Dashboard (Recommended)**
- [ ] Opened Supabase SQL Editor
- [ ] Copied migration file contents
- [ ] Reviewed SQL statements
- [ ] Executed migration
- [ ] No errors in response

**Method 2: Supabase CLI**
- [ ] Ran `supabase db push`
- [ ] Reviewed changes shown
- [ ] Confirmed migration
- [ ] Migration completed successfully

### Verify Migration
Run these queries in Supabase SQL Editor:

- [ ] **Tables exist**:
  ```sql
  SELECT table_name FROM information_schema.tables 
  WHERE table_schema = 'public' 
  AND table_name IN (
    'connector_marketplace',
    'user_installed_connectors',
    'custom_connectors',
    'schema_mappings_llm',
    'sync_metrics',
    'connector_health'
  );
  ```
  Expected: 6 rows

- [ ] **Indexes created**:
  ```sql
  SELECT COUNT(*) FROM pg_indexes 
  WHERE tablename IN ('connector_marketplace', 'sync_metrics', 'connector_health');
  ```
  Expected: At least 10 indexes

- [ ] **RLS enabled**:
  ```sql
  SELECT tablename, rowsecurity FROM pg_tables 
  WHERE tablename = 'connector_marketplace';
  ```
  Expected: rowsecurity = true

- [ ] **Materialized view exists**:
  ```sql
  SELECT COUNT(*) FROM pg_matviews WHERE matviewname = 'connector_analytics';
  ```
  Expected: 1

### Migration Issues (if any)
- [ ] No issues encountered
- [ ] Issues encountered: _________________________________
- [ ] Issues resolved: ___________________________________

---

## 🌐 Frontend Deployment (Est. 10 min)

### Pre-Deploy Build Test
- [ ] `cd frontend && npm ci` completed
- [ ] `npm run build` succeeded
- [ ] No build warnings (acceptable warnings documented)

### Deploy to Production
Choose one method:

**Method 1: Automatic (Recommended)**
- [ ] Created release tag: `git tag -a v6b-1.0.0 -m "Phase 6B Release"`
- [ ] Pushed tag: `git push origin v6b-1.0.0`
- [ ] Vercel auto-deploy triggered
- [ ] Monitored deployment in Vercel dashboard
- [ ] Deployment status: READY

**Method 2: Manual via CLI**
- [ ] Ran `cd frontend && vercel --prod`
- [ ] Reviewed deployment preview
- [ ] Confirmed deployment
- [ ] Deployment URL: ___________________________

### Deployment Verification
- [ ] Deployment completed without errors
- [ ] Build time: _________ (should be < 5 min)
- [ ] Deployment URL: https://orion-ai.vercel.app
- [ ] DNS propagated (may take 30-60 seconds)

---

## 🧪 Post-Deployment Testing (Est. 15 min)

### HTTP Status Checks
Test all URLs return 200 status:

- [ ] Homepage: `curl -I https://orion-ai.vercel.app`
- [ ] Analytics: `curl -I https://orion-ai.vercel.app/analytics`
- [ ] Marketplace: `curl -I https://orion-ai.vercel.app/connectors/marketplace`
- [ ] Builder: `curl -I https://orion-ai.vercel.app/connectors/builder`
- [ ] Dashboard (existing): `curl -I https://orion-ai.vercel.app/dashboard`
- [ ] Matrix (existing): `curl -I https://orion-ai.vercel.app/matrix`

### API Endpoint Checks
- [ ] Marketplace API: `curl https://orion-ai.vercel.app/api/marketplace`
  - Returns JSON with `connectors` array
  - Status: 200

### Manual Browser Tests

**Analytics Page** (`/analytics`):
- [ ] Page loads without errors
- [ ] No JavaScript console errors
- [ ] Charts display (or empty state if no data)
- [ ] Time range selector visible
- [ ] Loading states work
- [ ] Navigation bar present
- [ ] Responsive on mobile (if testing)

**Marketplace Page** (`/connectors/marketplace`):
- [ ] Page loads without errors
- [ ] No JavaScript console errors
- [ ] Connectors display (or empty state)
- [ ] Search box functional
- [ ] Category filters present
- [ ] Stats bar shows correct counts
- [ ] Connector cards clickable
- [ ] Install modal opens/closes
- [ ] "Build Custom Connector" CTA visible

**Builder Page** (`/connectors/builder`):
- [ ] Page loads without errors
- [ ] No JavaScript console errors
- [ ] Step 1 form visible
- [ ] Progress indicator shows "1 of 3"
- [ ] API URL input field present
- [ ] Sample response textarea present
- [ ] "Analyze API" button present
- [ ] Can navigate between steps

**Existing Pages** (Regression Testing):
- [ ] Dashboard loads correctly
- [ ] Matrix Grid loads correctly
- [ ] Settings page works
- [ ] User profile accessible
- [ ] Authentication still works

### Performance Checks
- [ ] Analytics page load time: ______ (target < 3s)
- [ ] Marketplace page load time: ______ (target < 3s)
- [ ] Builder page load time: ______ (target < 3s)
- [ ] No console warnings about performance
- [ ] No memory leaks detected (DevTools Memory tab)

### Data Verification
- [ ] Marketplace API returns array (empty or with connectors)
- [ ] Analytics page handles empty state gracefully
- [ ] No database connection errors in logs

---

## 📊 Monitoring (Est. 15 min)

### Vercel Analytics Dashboard
Visit: https://vercel.com/dashboard/analytics

- [ ] No spike in errors (< 1% error rate)
- [ ] Page views registering for new pages
- [ ] Average page load time acceptable (< 3s)
- [ ] No 500 errors

### Supabase Dashboard
Visit: https://supabase.com/dashboard

- [ ] Database queries executing normally
- [ ] No error spikes in logs
- [ ] Connection count normal
- [ ] Table storage increased (expected)
- [ ] No RLS policy violations

### Browser Console Monitoring
- [ ] No JavaScript errors on any page
- [ ] No failed network requests (except expected 401s)
- [ ] No React warnings
- [ ] No memory warnings

### Health Monitoring (2-minute intervals for 15 min)
Record status every 2 minutes:

| Time | Analytics Page | Marketplace Page | Builder Page | Notes |
|------|---------------|-----------------|--------------|-------|
| _____| [ ] OK [ ] FAIL | [ ] OK [ ] FAIL | [ ] OK [ ] FAIL | _____ |
| _____| [ ] OK [ ] FAIL | [ ] OK [ ] FAIL | [ ] OK [ ] FAIL | _____ |
| _____| [ ] OK [ ] FAIL | [ ] OK [ ] FAIL | [ ] OK [ ] FAIL | _____ |
| _____| [ ] OK [ ] FAIL | [ ] OK [ ] FAIL | [ ] OK [ ] FAIL | _____ |
| _____| [ ] OK [ ] FAIL | [ ] OK [ ] FAIL | [ ] OK [ ] FAIL | _____ |
| _____| [ ] OK [ ] FAIL | [ ] OK [ ] FAIL | [ ] OK [ ] FAIL | _____ |
| _____| [ ] OK [ ] FAIL | [ ] OK [ ] FAIL | [ ] OK [ ] FAIL | _____ |

---

## 🎯 Optional: Seed Production Data

**Note**: Only if you want sample connectors in production

### Marketplace Connectors
- [ ] Opened Supabase SQL Editor
- [ ] Ran `scripts/seed/seed_marketplace.sql`
- [ ] 6 connectors inserted
- [ ] Verified in marketplace page

### Analytics Sample Data
- [ ] Ran `scripts/seed/seed_analytics.sql` (optional)
- [ ] Sample metrics inserted
- [ ] Charts now display data
- [ ] Refreshed materialized view: `REFRESH MATERIALIZED VIEW connector_analytics;`

---

## 📝 Post-Deployment Tasks

### Documentation
- [ ] Updated `CHANGELOG.md` with Phase 6B release
- [ ] Updated `README.md` (if needed)
- [ ] Updated team wiki/docs
- [ ] Created release notes

### Team Communication
- [ ] Posted success message in #deployments
- [ ] Shared deployment summary
- [ ] Notified stakeholders
- [ ] Documented any issues encountered

### Monitoring Setup
- [ ] Set up alerts for new pages (if using monitoring service)
- [ ] Added new endpoints to uptime monitoring
- [ ] Configured error tracking for new components

---

## 🚨 Rollback (If Issues Occur)

### Criteria for Rollback
Rollback if:
- [ ] Any page returns 500 errors consistently
- [ ] JavaScript errors break core functionality
- [ ] Error rate exceeds 5%
- [ ] Database migration caused data issues
- [ ] Critical user flow broken

### Rollback Procedure
If rollback is needed:

**Frontend Rollback**:
1. [ ] Open Vercel Dashboard → Deployments
2. [ ] Find previous successful deployment: _______________
3. [ ] Click "..." → "Promote to Production"
4. [ ] OR: `vercel rollback [previous-deployment-url]`

**Database Rollback** (if needed):
1. [ ] Restore from backup: `psql $DATABASE_URL < backup_phase6b.sql`
2. [ ] OR: Drop new tables (see PHASE6B-DEPLOYMENT.md)

**Notify Team**:
- [ ] Posted rollback notification
- [ ] Created incident ticket
- [ ] Scheduled post-mortem

### Rollback Completed
- [ ] Rollback executed at: _____________
- [ ] Services restored
- [ ] Team notified
- [ ] Incident documented

---

## ✅ Deployment Sign-Off

### Success Criteria
- [ ] All new pages accessible (200 status)
- [ ] No JavaScript errors
- [ ] API endpoints responding
- [ ] Database migration successful
- [ ] Performance acceptable
- [ ] No rollback needed
- [ ] Monitoring stable for 15 minutes

### Final Verification
- [ ] Deployment marked as successful
- [ ] Backup tag documented
- [ ] Monitoring will continue for 24 hours
- [ ] Team has access to this checklist

### Signatures
- **Deployed By**: _________________ Date: _______
- **Verified By**: _________________ Date: _______
- **Approved By**: _________________ Date: _______

---

## 📊 Deployment Metrics

Fill in after deployment:

| Metric | Value |
|--------|-------|
| Total Deployment Time | ______ minutes |
| Database Migration Time | ______ minutes |
| Frontend Deploy Time | ______ minutes |
| Testing Time | ______ minutes |
| Issues Encountered | ______ |
| Rollback Required | Yes / No |
| Overall Status | Success / Failed / Partial |

### Issues Encountered
List any issues and resolutions:

1. _________________________________________________
2. _________________________________________________
3. _________________________________________________

### Lessons Learned
Document for future deployments:

1. _________________________________________________
2. _________________________________________________
3. _________________________________________________

---

## 🎉 Deployment Complete!

**Status**: ⬜ Pending ⬜ In Progress ⬜ Complete ⬜ Rolled Back

**Notes**: 
_________________________________________________________
_________________________________________________________
_________________________________________________________

**Phase 6B is now live! 🚀**

---

**Document Version**: 1.0.0  
**Phase**: 6B  
**Created**: 2026-01-31
