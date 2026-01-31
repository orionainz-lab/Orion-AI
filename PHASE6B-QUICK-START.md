# Phase 6B Testing, Migration & Data Connection - Quick Start Guide

**Date**: 2026-01-31  
**Status**: Ready for Manual Execution  
**Time Required**: 30-45 minutes

---

## 🎯 Quick Summary

You now have:
✅ **Frontend Components Built** (20 files, analytics + builder + marketplace)  
✅ **Data Hooks Created** (`useAnalytics.ts`, `useMarketplace.ts`)  
✅ **Seed Scripts Ready** (marketplace + analytics data)  
✅ **Migration Files Ready** (clean install version)  
✅ **Testing Guide** (comprehensive checklist)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Apply Database Migration (5 minutes)

**Option A: Using Supabase Dashboard** (Recommended)

1. Open https://supabase.com/dashboard
2. Select your project
3. Go to **SQL Editor**
4. Copy & paste from: `supabase/migrations/20260131_phase6b_clean.sql`
5. Click **Run**

**Option B: Using Supabase CLI**

```bash
cd "f:/New folder (22)/OrionAi/Orion-AI"
supabase db push
```

**Verify Migration**:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN (
    'connector_marketplace',
    'sync_metrics',
    'connector_health'
  );
-- Should return 3 tables
```

---

### Step 2: Seed Sample Data (10 minutes)

**Run in Supabase SQL Editor**:

```sql
-- 1. Seed Marketplace
-- Copy from: scripts/seed/seed_marketplace.sql

-- 2. Seed Analytics  
-- Copy from: scripts/seed/seed_analytics.sql

-- 3. Verify data
SELECT COUNT(*) FROM connector_marketplace;  -- Should be 6
SELECT COUNT(*) FROM sync_metrics;  -- Should be ~50
SELECT status, COUNT(*) FROM connector_health GROUP BY status;
```

---

### Step 3: Test the UI (15 minutes)

**Start Dev Server** (if not already running):
```bash
cd frontend
npm run dev
```

**Access**: http://localhost:3000 (or 3001 if port conflict)

**Test Pages**:
1. ✅ **/analytics** - Should show real metrics from database
2. ✅ **/connectors/marketplace** - Should show 6 connectors
3. ✅ **/connectors/builder** - Should show 3-step wizard

---

## 📋 Detailed Testing Checklist

### Analytics Dashboard (`/analytics`)

- [ ] Page loads without errors
- [ ] Connector Health shows counts from database
- [ ] Sync Metrics display (24h, 7d, 30d)
- [ ] Performance metrics visible
- [ ] Charts render with data
- [ ] Time range filter works (7d, 30d, 90d)
- [ ] Export button present
- [ ] Live data badge animating
- [ ] Responsive on mobile

**Expected Data**:
- Healthy: ~40 connectors
- Degraded: ~7 connectors  
- Failed: ~3 connectors
- Total syncs: ~50
- Success rate: ~90%

---

### Marketplace (`/connectors/marketplace`)

- [ ] 6 connectors load from database
- [ ] Search filtering works
- [ ] Category buttons filter correctly
- [ ] Verified badges show for official connectors
- [ ] Rating stars display
- [ ] Install count shows
- [ ] Click connector card shows details
- [ ] Install modal opens
- [ ] Responsive layout

**Expected Connectors**:
1. Salesforce (CRM, 4.8★, 12,543 installs)
2. HubSpot (CRM, 4.7★, 9,876 installs)
3. Stripe (Accounting, 4.9★, 15,678 installs)
4. QuickBooks (Accounting, 4.6★, 8,432 installs)
5. Slack (Communication, 4.8★, 11,234 installs)
6. Shopify (Custom, 4.5★, 6,789 installs)

---

### Connector Builder (`/connectors/builder`)

- [ ] 3-step progress indicator shows
- [ ] Connector name input works
- [ ] Step 1: API analyzer accepts input
- [ ] Step 1: Can proceed to step 2
- [ ] Step 2: Field mappings display
- [ ] Step 2: Approve/reject buttons work
- [ ] Step 2: Can proceed to step 3
- [ ] Step 3: Test sandbox form works
- [ ] Step 3: Test button simulates connection
- [ ] Step 3: Logs display in terminal style
- [ ] Back buttons work
- [ ] Save/Deploy buttons present

---

## 🔧 Troubleshooting

### Issue: Tables Already Exist Error
**Solution**: Migration uses `IF NOT EXISTS`, safe to run multiple times

### Issue: Foreign Key Constraint Error
**Solution**: Ensure `connectors` and `connector_configs` tables exist from Phase 5

### Issue: No Data in Analytics
**Solution**:
```sql
-- Check if seed ran
SELECT COUNT(*) FROM sync_metrics;
SELECT COUNT(*) FROM connector_health;

-- If 0, run seed scripts again
```

### Issue: Frontend Shows "Loading..." Forever
**Solution**:
1. Check browser console for errors
2. Verify Supabase credentials in `.env.local`
3. Check RLS policies allow public read:
```sql
SELECT * FROM connector_marketplace LIMIT 1;  -- Should work
```

### Issue: Charts Not Rendering
**Solution**:
```bash
# Verify recharts is installed
cd frontend
npm list recharts
# If not found:
npm install recharts
```

---

## 📁 Key Files Reference

**Migration**:
- `supabase/migrations/20260131_phase6b_clean.sql` (Clean install)

**Seed Data**:
- `scripts/seed/seed_marketplace.sql` (6 connectors)
- `scripts/seed/seed_analytics.sql` (50 sync records)

**Data Hooks**:
- `frontend/hooks/useAnalytics.ts` (Real-time analytics)
- `frontend/hooks/useMarketplace.ts` (Marketplace data)

**Pages**:
- `frontend/app/analytics/page.tsx`
- `frontend/app/connectors/marketplace/page.tsx`
- `frontend/app/connectors/builder/page.tsx`

**Components**:
- `frontend/components/analytics/*` (4 components)
- `frontend/components/builder/*` (3 components)
- `frontend/components/marketplace/*` (2 components)
- `frontend/components/charts/*` (3 components)

**Testing Guide**:
- `build_plan/phase6b-testing-guide.md` (Comprehensive guide)

---

## 🎯 Success Criteria

After completing all steps, you should have:

✅ 6 new database tables created  
✅ 1 materialized view (connector_analytics)  
✅ 6 marketplace connectors seeded  
✅ ~50 sync metrics records  
✅ ~50 connector health records  
✅ Analytics dashboard showing real data  
✅ Marketplace showing 6 connectors  
✅ Builder wizard functional  
✅ All pages responsive  
✅ Zero console errors

---

## 📊 Quick Verification Queries

Run in Supabase SQL Editor:

```sql
-- 1. Verify tables exist
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE '%connector%' OR table_name LIKE '%sync%';
-- Should be ~10 tables

-- 2. Check marketplace
SELECT name, category, install_count, is_verified 
FROM connector_marketplace 
ORDER BY install_count DESC;
-- Should return 6 rows

-- 3. Check analytics data
SELECT 
  (SELECT COUNT(*) FROM sync_metrics) as sync_count,
  (SELECT COUNT(*) FROM connector_health) as health_count,
  (SELECT COUNT(DISTINCT status) FROM connector_health) as status_types;
-- Should show: ~50 syncs, ~50 health records, 3 status types

-- 4. Test materialized view
SELECT * FROM connector_analytics LIMIT 5;
-- Should return aggregated data

-- 5. Verify RLS
SELECT COUNT(*) FROM connector_marketplace;  -- Should work (public read)
```

---

## 🚀 Next Steps After Testing

1. **Fix any bugs** found during testing
2. **Optimize slow queries** if needed
3. **Add loading skeletons** for better UX
4. **Implement error boundaries**
5. **Add user feedback** (toast notifications)
6. **Setup monitoring** (Sentry, LogRocket)
7. **Deploy to staging**
8. **User acceptance testing**
9. **Deploy to production**

---

## 💡 Pro Tips

1. **Use Browser DevTools**: Check Network tab for API calls
2. **Monitor Console**: Watch for errors or warnings
3. **Test Auth Flow**: Ensure user is authenticated
4. **Check RLS Policies**: Verify data access permissions
5. **Use Supabase Logs**: Check for database errors
6. **Test Realtime**: Analytics refresh every 30 seconds
7. **Mobile Testing**: Use Chrome DevTools device mode
8. **Performance**: Use React DevTools Profiler

---

## 📞 Need Help?

**Documentation**:
- Full Testing Guide: `build_plan/phase6b-testing-guide.md`
- Architecture: `build_plan/phase6b-architecture.md`
- Build Report: `build_plan/phase6b-frontend-complete.md`

**Common Commands**:
```bash
# Start frontend
cd frontend && npm run dev

# Check Supabase status
supabase status

# View Supabase logs
supabase logs

# Reset database (caution!)
supabase db reset

# Generate types
supabase gen types typescript > frontend/types/database.ts
```

---

**Time to Complete**: 30-45 minutes  
**Difficulty**: Easy (copy-paste SQL + test UI)  
**Prerequisites**: Supabase project + frontend built  
**Result**: Fully functional Phase 6B UI with real data

🎉 **Ready to test! Follow the 3 steps above to get started.**
