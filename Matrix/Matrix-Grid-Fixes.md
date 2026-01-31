# Phase 4 - Matrix Grid Fixes

**Date:** 2026-01-31  
**Issue:** Matrix Grid showing "0 total proposals" and "Real-time connection lost" errors

---

## 🐛 **Issues Identified**

### 1. **AG Grid Error #272: No Modules Registered**
**Error Message:**
```
AG Grid: error #272 "No AG Grid modules are registered!"
```

**Root Cause:**  
The `ModuleRegistry.registerModules([AllCommunityModule])` was missing from the MatrixGridV2 component.

**Fix Applied:**
```typescript
// Added to MatrixGridV2.tsx
import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community'

// Register AG Grid modules
ModuleRegistry.registerModules([AllCommunityModule])
```

---

### 2. **Status Mapping Mismatch**

**Root Cause:**  
The database schema uses different status values than the frontend expected:

| Database Schema | Frontend Expected |
|----------------|-------------------|
| `started`      | `pending`         |
| `completed`    | `approved`        |
| `failed`       | `rejected`        |
| `cancelled`    | N/A               |

**Fix Applied:**

#### **MatrixGridV2.tsx - Status Badge Renderer:**
```typescript
const colors: Record<string, string> = {
  started: 'bg-yellow-100 text-yellow-700',      // Was: pending
  completed: 'bg-green-100 text-green-700',      // Was: approved
  failed: 'bg-red-100 text-red-700',             // Was: rejected
  cancelled: 'bg-gray-100 text-gray-700',        // Added
  unknown: 'bg-gray-100 text-gray-700',
}
```

#### **MatrixGridV2.tsx - Action Buttons:**
```typescript
// Update local state
await updateProposal(props.data.id, {
  status: action === 'approve' ? 'completed' : 'failed',  // Was: 'approved' : 'rejected'
})

// Check for pending status
const isPending = status === 'started' || !status  // Was: status === 'pending'
```

#### **Dashboard page.tsx - Stats:**
```typescript
interface Stats {
  total: number
  completed: number    // Was: approved
  started: number      // Was: pending
  failed: number       // Was: rejected
}

// Updated all Supabase queries to use correct status values
.eq('status', 'completed')  // Was: 'approved'
.eq('status', 'started')    // Was: 'pending'
.eq('status', 'failed')     // Was: 'rejected'
```

---

### 3. **Supabase Realtime Connection Error**

**Status:** Investigating  
**Symptoms:**
- "Real-time connection lost. Reconnecting..." notification
- Connection errors in browser console

**Potential Causes:**
1. Supabase Realtime may not be enabled for the `process_events` table
2. RLS (Row Level Security) policies may be blocking realtime subscriptions
3. Anon key permissions may be insufficient

**Recommended Actions:**
1. Check Supabase Dashboard → Database → Replication settings
2. Ensure `process_events` table has Realtime enabled
3. Verify RLS policies allow SELECT for anonymous users (if needed for testing)
4. Check browser console for detailed connection errors

---

## ✅ **Files Modified**

1. **`frontend/components/grid/MatrixGridV2.tsx`**
   - Added AG Grid module registration
   - Updated status mapping (started/completed/failed/cancelled)
   - Updated action button logic

2. **`frontend/app/page.tsx`**
   - Updated Dashboard stats interface
   - Fixed Supabase query status filters
   - Updated stat card labels

3. **`build_plan/phase4-manual-testing-guide.md`**
   - Updated test documentation to reflect correct status values

---

## 🧪 **Testing Instructions**

### **Refresh the Frontend:**
1. Stop the dev server (Ctrl+C)
2. Restart: `cd frontend && npm run dev`
3. Wait for compilation to complete

### **Test the Dashboard:**
1. Open http://localhost:3000
2. **Expected Results:**
   - Total: 8 proposals
   - Completed: 2
   - In Progress: 4
   - Failed: 2

### **Test the Matrix Grid:**
1. Open http://localhost:3000/matrix
2. **Expected Results:**
   - All 8 proposals should be displayed
   - Status badges should be color-coded:
     - Yellow: Started (4 proposals)
     - Green: Completed (2 proposals)
     - Red: Failed (2 proposals)
   - Action buttons (Approve/Reject) should only appear for "Started" proposals
   - Sorting and filtering should work

---

## 📊 **Database Schema Reference**

### **process_events Table:**

```sql
-- Status values (CHECK constraint)
status IN ('started', 'completed', 'failed', 'cancelled')

-- Event types (CHECK constraint)
event_type IN (
  'workflow_start', 'workflow_complete', 'workflow_failed',
  'activity_start', 'activity_complete', 'activity_failed',
  'rag_query', 'document_ingest', 'embedding_generate',
  'code_generate', 'code_verify',
  'user_action', 'system_event'
)
```

---

## 🔍 **Next Steps**

1. **Resolve Realtime Connection Error:**
   - Enable Supabase Realtime for `process_events` table
   - Verify RLS policies allow realtime subscriptions
   - Test realtime updates by manually updating a row in Supabase Dashboard

2. **Test Action Buttons:**
   - Click "Approve" on a Started proposal
   - Verify it updates to "Completed" in the grid
   - Check if Temporal signal is sent successfully

3. **Test Real-time Updates:**
   - Open Matrix Grid in browser
   - Manually update a row in Supabase Dashboard SQL Editor
   - Verify the change appears in the grid without refresh

---

## 📝 **Key Learnings**

1. Always check database constraints before seeding test data
2. Status/enum values must match exactly between frontend and backend
3. AG Grid requires explicit module registration in v35+
4. Supabase Realtime requires table-level configuration in the dashboard
