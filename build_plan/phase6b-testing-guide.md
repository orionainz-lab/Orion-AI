# Phase 6B Testing & Integration Guide

**Date**: 2026-01-31  
**Purpose**: Test UI, Apply Database Migration, Connect Real Data

---

## Prerequisites Checklist

- [x] Frontend built with Phase 6B components
- [x] Backend Phase 6B complete (connectors, LLM services)
- [x] Supabase project configured
- [x] Environment variables set (`.env.local` exists)
- [ ] Database migration applied
- [ ] Real data connected

---

## Part 1: Database Migration

### Step 1: Review Migration File

**File**: `supabase/migrations/20260131_phase6b_advanced_features.sql`

**Tables to be created**:
1. `connector_marketplace` - Public marketplace connectors
2. `user_installed_connectors` - User installations
3. `custom_connectors` - User-built connectors
4. `schema_mappings_llm` - AI-suggested mappings
5. `sync_metrics` - Sync performance data
6. `connector_health` - Real-time health status

**Materialized View**: `connector_analytics` (aggregated metrics)

### Step 2: Apply Migration

#### Option A: Using Supabase CLI (Recommended)

```bash
# Navigate to project root
cd "f:/New folder (22)/OrionAi/Orion-AI"

# Check Supabase status
supabase status

# Apply migration
supabase db push

# Or apply specific migration
supabase migration up
```

#### Option B: Using Supabase Dashboard

1. Go to https://supabase.com/dashboard
2. Select your project
3. Navigate to **SQL Editor**
4. Copy contents of `supabase/migrations/20260131_phase6b_advanced_features.sql`
5. Paste and click **Run**

#### Option C: Using Supabase MCP Tool

```bash
# List available MCP tools
# Use CallMcpTool to execute SQL migration
```

### Step 3: Verify Migration

```sql
-- Check if tables exist
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
  );

-- Check materialized view
SELECT * FROM connector_analytics LIMIT 1;

-- Verify indexes
SELECT indexname 
FROM pg_indexes 
WHERE tablename IN ('connector_marketplace', 'sync_metrics', 'connector_health');
```

---

## Part 2: Seed Marketplace Data

### Step 1: Create Seed Script

**File**: `scripts/seed_marketplace.sql`

```sql
-- Seed marketplace connectors
INSERT INTO connector_marketplace (
  connector_id, 
  publisher_id, 
  name, 
  description, 
  category, 
  pricing_model, 
  install_count, 
  rating, 
  is_verified
) VALUES
  -- Salesforce
  (
    uuid_generate_v4(),
    (SELECT id FROM auth.users LIMIT 1),
    'Salesforce',
    'Connect to Salesforce CRM for customer data synchronization. Supports Accounts, Contacts, Leads, and Opportunities.',
    'crm',
    'free',
    12543,
    4.8,
    true
  ),
  -- HubSpot
  (
    uuid_generate_v4(),
    (SELECT id FROM auth.users LIMIT 1),
    'HubSpot',
    'Integrate with HubSpot CRM to sync contacts, companies, and deals. Real-time webhook support included.',
    'crm',
    'free',
    9876,
    4.7,
    true
  ),
  -- Stripe
  (
    uuid_generate_v4(),
    (SELECT id FROM auth.users LIMIT 1),
    'Stripe',
    'Payment processing integration with Stripe. Sync customers, invoices, and payment events automatically.',
    'accounting',
    'free',
    15678,
    4.9,
    true
  ),
  -- QuickBooks
  (
    uuid_generate_v4(),
    (SELECT id FROM auth.users LIMIT 1),
    'QuickBooks',
    'QuickBooks Online integration for accounting data. Sync customers, invoices, and payments with OAuth 2.0.',
    'accounting',
    'free',
    8432,
    4.6,
    true
  ),
  -- Slack
  (
    uuid_generate_v4(),
    (SELECT id FROM auth.users LIMIT 1),
    'Slack',
    'Send notifications and alerts to Slack channels. Support for interactive components and file uploads.',
    'communication',
    'free',
    11234,
    4.8,
    true
  ),
  -- Shopify (Community)
  (
    uuid_generate_v4(),
    (SELECT id FROM auth.users LIMIT 1),
    'Shopify',
    'E-commerce integration with Shopify. Sync products, orders, and customers in real-time.',
    'custom',
    'freemium',
    6789,
    4.5,
    false
  );
```

### Step 2: Seed Sample Metrics

```sql
-- Create sample sync metrics
INSERT INTO sync_metrics (
  config_id,
  sync_started_at,
  sync_completed_at,
  records_processed,
  records_failed,
  duration_ms
)
SELECT 
  (SELECT id FROM connector_configs LIMIT 1),
  NOW() - (random() * interval '7 days'),
  NOW() - (random() * interval '6 days'),
  floor(random() * 1000 + 100)::int,
  floor(random() * 10)::int,
  floor(random() * 5000 + 1000)::int
FROM generate_series(1, 50);

-- Create sample connector health
INSERT INTO connector_health (
  config_id,
  status,
  last_check_at,
  consecutive_failures,
  avg_response_time_ms
)
SELECT 
  id,
  CASE 
    WHEN random() < 0.8 THEN 'healthy'
    WHEN random() < 0.95 THEN 'degraded'
    ELSE 'failed'
  END,
  NOW(),
  0,
  floor(random() * 500 + 100)::int
FROM connector_configs;
```

---

## Part 3: Connect Real Data to Frontend

### Step 1: Create Analytics Data Hook

**File**: `frontend/hooks/useAnalytics.ts`

```typescript
'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'

export interface AnalyticsData {
  connectorHealth: {
    healthy: number
    degraded: number
    failed: number
  }
  syncMetrics: {
    last24h: number
    last7d: number
    last30d: number
    successRate: number
  }
  performanceMetrics: {
    avgResponseTime: number
    p95ResponseTime: number
    errorRate: number
  }
}

export function useAnalytics(timeRange: '7d' | '30d' | '90d' = '7d') {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true)
        const supabase = createClient()

        // Get connector health
        const { data: healthData } = await supabase
          .from('connector_health')
          .select('status')
        
        const healthCounts = {
          healthy: healthData?.filter(h => h.status === 'healthy').length || 0,
          degraded: healthData?.filter(h => h.status === 'degraded').length || 0,
          failed: healthData?.filter(h => h.status === 'failed').length || 0
        }

        // Get sync metrics
        const daysAgo = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90
        const startDate = new Date()
        startDate.setDate(startDate.getDate() - daysAgo)

        const { data: syncData } = await supabase
          .from('sync_metrics')
          .select('records_processed, error_message, sync_started_at')
          .gte('sync_started_at', startDate.toISOString())

        const totalRecords = syncData?.reduce((sum, s) => sum + (s.records_processed || 0), 0) || 0
        const totalSyncs = syncData?.length || 0
        const failedSyncs = syncData?.filter(s => s.error_message).length || 0
        const successRate = totalSyncs > 0 ? ((totalSyncs - failedSyncs) / totalSyncs) * 100 : 0

        // Get performance metrics
        const { data: healthMetrics } = await supabase
          .from('connector_health')
          .select('avg_response_time_ms')
        
        const avgResponseTime = healthMetrics?.reduce((sum, h) => sum + (h.avg_response_time_ms || 0), 0) / (healthMetrics?.length || 1)

        setData({
          connectorHealth: healthCounts,
          syncMetrics: {
            last24h: totalRecords,
            last7d: totalRecords,
            last30d: totalRecords,
            successRate
          },
          performanceMetrics: {
            avgResponseTime: Math.round(avgResponseTime),
            p95ResponseTime: Math.round(avgResponseTime * 1.5),
            errorRate: totalSyncs > 0 ? (failedSyncs / totalSyncs) * 100 : 0
          }
        })
      } catch (err) {
        setError(err as Error)
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [timeRange])

  return { data, loading, error }
}
```

### Step 2: Create Marketplace Data Hook

**File**: `frontend/hooks/useMarketplace.ts`

```typescript
'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'
import type { ConnectorMarketplace } from '@/types/database'

export function useMarketplace() {
  const [connectors, setConnectors] = useState<ConnectorMarketplace[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchConnectors = async () => {
      try {
        setLoading(true)
        const supabase = createClient()

        const { data, error: fetchError } = await supabase
          .from('connector_marketplace')
          .select('*')
          .order('install_count', { ascending: false })

        if (fetchError) throw fetchError
        setConnectors(data || [])
      } catch (err) {
        setError(err as Error)
      } finally {
        setLoading(false)
      }
    }

    fetchConnectors()
  }, [])

  return { connectors, loading, error }
}
```

### Step 3: Update Analytics Page

**File**: `frontend/app/analytics/page.tsx`

```typescript
// Add at top of component
import { useAnalytics } from '@/hooks/useAnalytics'

// Inside component
export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('7d')
  const { data: analytics, loading, error } = useAnalytics(timeRange)

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-96">
          <div className="text-gray-600">Loading analytics...</div>
        </div>
      </AppLayout>
    )
  }

  if (error || !analytics) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-96">
          <div className="text-red-600">Error loading analytics</div>
        </div>
      </AppLayout>
    )
  }

  // Use analytics.connectorHealth, analytics.syncMetrics, etc.
  // instead of hardcoded values
}
```

### Step 4: Update Marketplace Page

```typescript
// Add at top
import { useMarketplace } from '@/hooks/useMarketplace'

// Inside component
export default function MarketplacePage() {
  const { connectors: marketplaceConnectors, loading, error } = useMarketplace()
  
  // Use marketplaceConnectors instead of hardcoded array
}
```

---

## Part 4: Testing Checklist

### UI Testing

- [ ] **Analytics Dashboard**
  - [ ] Page loads without errors
  - [ ] Metrics display correctly
  - [ ] Time range filtering works
  - [ ] Charts render with data
  - [ ] Export button functional
  - [ ] Responsive on mobile/tablet

- [ ] **Connector Builder**
  - [ ] Step 1: API analyzer accepts input
  - [ ] Step 2: Field mappings display
  - [ ] Step 3: Test sandbox connects
  - [ ] Navigation between steps works
  - [ ] Save/deploy buttons functional

- [ ] **Marketplace**
  - [ ] Connectors load from database
  - [ ] Search filtering works
  - [ ] Category filtering works
  - [ ] Install modal opens
  - [ ] Verified badges show correctly

### Data Verification

```sql
-- Verify marketplace data
SELECT COUNT(*) as total_connectors FROM connector_marketplace;
SELECT category, COUNT(*) FROM connector_marketplace GROUP BY category;

-- Verify metrics data
SELECT COUNT(*) as total_metrics FROM sync_metrics;
SELECT status, COUNT(*) FROM connector_health GROUP BY status;

-- Verify materialized view
SELECT * FROM connector_analytics ORDER BY date DESC LIMIT 10;
```

### Performance Testing

- [ ] Analytics page loads in <1 second
- [ ] Marketplace search is instant
- [ ] Charts render smoothly
- [ ] No memory leaks (check with React DevTools)

---

## Part 5: Troubleshooting

### Issue: Migration Fails

**Solution**:
- Check if `connectors` and `connector_configs` tables exist (from Phase 5)
- Ensure auth.users table has at least one user
- Run migration step-by-step

### Issue: Frontend Can't Connect to Supabase

**Solution**:
- Verify `.env.local` has correct Supabase URL and anon key
- Check Supabase project is running
- Test connection with simple query

### Issue: No Data Showing

**Solution**:
- Run seed scripts first
- Check RLS policies allow read access
- Verify user is authenticated
- Check browser console for errors

### Issue: Charts Not Rendering

**Solution**:
- Ensure recharts is installed (`npm install recharts`)
- Check data format matches chart requirements
- Verify data is not empty array

---

## Part 6: Next Steps After Testing

1. **Fix any bugs discovered**
2. **Optimize slow queries**
3. **Add loading skeletons**
4. **Implement error boundaries**
5. **Add user feedback (toasts)**
6. **Setup monitoring (Sentry, LogRocket)**
7. **Deploy to staging**
8. **User acceptance testing**
9. **Deploy to production**

---

## Command Reference

```bash
# Start frontend dev server
cd frontend && npm run dev

# Apply database migration
supabase db push

# Generate TypeScript types
supabase gen types typescript --local > frontend/types/database.ts

# Run tests
npm run test

# Build for production
npm run build

# Check for errors
npm run lint
```

---

**Status**: Ready for Testing  
**Estimated Time**: 1-2 hours  
**Next**: Apply migration → Seed data → Test UI → Fix bugs → Deploy
