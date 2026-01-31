# Matrix Grid - Final Fix (created_at → event_timestamp)

**Date:** 2026-01-31  
**Critical Issue:** Matrix Grid showing "No Rows To Show" despite data existing in database

---

## 🔴 **Root Cause**

The frontend was querying for a column named `created_at`, but the actual database column is `event_timestamp`.

### **Error Chain:**
1. `useProposalStore.fetchProposals()` queries `.order('created_at', { ascending: false })`
2. Supabase returns error: `column "created_at" does not exist`
3. Error is caught, but no data is returned
4. Grid displays "No Rows To Show"

---

## ✅ **Fixes Applied**

### **1. useProposalStore.ts - Query Fix**

**Before:**
```typescript
let query = supabase
  .from('process_events')
  .select('*')
  .order('created_at', { ascending: false })  // ❌ Wrong column
  .limit(1000)
```

**After:**
```typescript
let query = supabase
  .from('process_events')
  .select('*')
  .order('event_timestamp', { ascending: false })  // ✅ Correct column
  .limit(1000)
```

---

### **2. MatrixGridV2.tsx - Column Definition Fix**

**Before:**
```typescript
{
  field: 'created_at',  // ❌ Wrong field
  headerName: 'Created',
  width: 180,
  cellRenderer: TimestampCellRenderer,
  sortable: true,
  sort: 'desc',
},
```

**After:**
```typescript
{
  field: 'event_timestamp',  // ✅ Correct field
  headerName: 'Created',
  width: 180,
  cellRenderer: TimestampCellRenderer,
  sortable: true,
  sort: 'desc',
},
```

---

### **3. MatrixGridV2.tsx - Realtime Disabled (Temporary)**

**Issue:** Supabase Realtime connection is timing out due to missing replication configuration.

**Temporary Fix:**
```typescript
// Subscribe to realtime updates (disabled temporarily due to connection issues)
// useRealtimeProposals()

// Initial fetch on mount
useEffect(() => {
  useProposalStore.getState().fetchProposals()
}, [])
```

**Benefit:**
- Grid will now load data successfully
- No more "Real-time connection lost" errors
- Grid will still work, just without live updates

---

## 📊 **Database Schema Reference**

### **Actual Column Names in `process_events` Table:**

| Column Name | Data Type | Notes |
|------------|-----------|-------|
| `id` | UUID | Primary key |
| `event_type` | TEXT | Required, CHECK constraint |
| `event_name` | TEXT | Event identifier |
| `workflow_id` | TEXT | Workflow reference |
| `user_id` | UUID | FK to auth.users, nullable |
| `status` | TEXT | Required, CHECK constraint |
| **`event_timestamp`** | TIMESTAMP WITH TIME ZONE | ✅ **This is the correct column** |
| `metadata` | JSONB | Additional data |

**NOT `created_at`!**

---

## 🧪 **Testing Instructions**

### **Step 1: Refresh the Browser**
1. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
2. Refresh the Matrix Grid page: http://localhost:3000/matrix

### **Step 2: Expected Results**

**✅ Grid Should Display:**
- **8 total proposals** (shown in header)
- All 8 rows visible in the grid
- Status badges color-coded:
  - **Yellow** = Started (4 proposals)
  - **Green** = Completed (2 proposals)
  - **Red** = Failed (2 proposals)
- Timestamps in the "Created" column
- Action buttons (Approve/Reject) on "Started" proposals

**✅ No More Errors:**
- No "Real-time connection lost" errors
- No console errors
- Grid loads immediately

---

## 🔍 **Verification Queries**

To confirm data is accessible:

```sql
-- Count total rows (should return 8)
SELECT COUNT(*) FROM process_events;

-- View all proposals with correct column
SELECT 
  id, 
  event_name, 
  status, 
  workflow_id,
  event_timestamp
FROM process_events
ORDER BY event_timestamp DESC;

-- Test as anon role (simulates frontend query)
SET ROLE anon;
SELECT COUNT(*) FROM process_events;  -- Should return 8
RESET ROLE;
```

---

## 📝 **Files Modified**

1. **`frontend/store/useProposalStore.ts`**
   - Changed `.order('created_at')` → `.order('event_timestamp')`

2. **`frontend/components/grid/MatrixGridV2.tsx`**
   - Changed `field: 'created_at'` → `field: 'event_timestamp'`
   - Disabled `useRealtimeProposals()` temporarily
   - Added explicit `fetchProposals()` call on mount

---

## 🚀 **Next Steps**

### **To Re-enable Realtime:**

1. **Enable Supabase Realtime for `process_events` table:**
   - Go to Supabase Dashboard → Database → Replication
   - Enable replication for `process_events` table
   - Enable all events: INSERT, UPDATE, DELETE

2. **Test Realtime Connection:**
   - Uncomment `useRealtimeProposals()` in MatrixGridV2.tsx
   - Refresh browser
   - Check browser console for "Realtime connected" message
   - Manually update a row in Supabase Dashboard
   - Verify change appears in grid without refresh

3. **If Still Failing:**
   - Check RLS policies allow SELECT for anon role
   - Verify `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` in `.env.local`
   - Check Supabase project settings for Realtime configuration

---

## 🎯 **Key Learnings**

1. **Always verify actual column names** before writing queries
2. **Check database schema** using `information_schema.columns`
3. **Test with anon role** to simulate frontend permissions
4. **Silent failures** can occur when queries fail but errors aren't displayed
5. **Supabase Realtime** requires explicit table-level configuration

---

## ✅ **Expected Final State**

After applying these fixes:

- ✅ Matrix Grid displays 8 proposals
- ✅ All columns populated with data
- ✅ Sorting works
- ✅ Filtering works (Status, Event Type)
- ✅ Action buttons functional
- ✅ CSV export works
- ✅ No console errors
- ⚠️ Realtime disabled (to be re-enabled after configuration)

---

**The grid should now be fully functional!** 🎉
