# Phase 4.2/4.3 Manual Testing Guide

## Prerequisites

✅ **Services Running:**
- Frontend: http://localhost:3000 ✅ RUNNING
- Temporal: http://localhost:7233 ✅ RUNNING
- Temporal UI: http://localhost:8080 ✅ RUNNING

## Test Data Setup

Since we're using a cloud Supabase instance with RLS, you'll need to seed test data through the Supabase Dashboard:

1. Open Supabase Dashboard: https://supabase.com/dashboard
2. Go to SQL Editor
3. Run this SQL:

```sql
-- Insert test proposals
INSERT INTO process_events (
  id, event_name, event_type, event_metadata, user_id, workflow_id
) VALUES 
  ('test-pending-001', 'code_generation', 'ai_event', '{"status": "pending"}'::jsonb, 'test-user-1', 'wf-001'),
  ('test-pending-002', 'code_review', 'ai_event', '{"status": "pending"}'::jsonb, 'test-user-2', 'wf-002'),
  ('test-approved-001', 'deployment', 'ai_event', '{"status": "approved"}'::jsonb, 'test-user-3', 'wf-003'),
  ('test-rejected-001', 'quality_check', 'ai_event', '{"status": "rejected"}'::jsonb, 'test-user-4', 'wf-004');
```

---

## Test 1: Dashboard Stats

**URL:** http://localhost:3000

**Test Steps:**
1. Open the dashboard
2. Verify stat cards show numbers:
   - Total Proposals
   - Approved count
   - Pending count
   - Rejected count
3. Verify "System Status" shows all green indicators

**Expected Result:**
- ✅ Stats display correctly
- ✅ Numbers match Supabase data
- ✅ Loading states work
- ✅ System status shows "Connected"

---

## Test 2: Matrix Grid Data Loading

**URL:** http://localhost:3000/matrix

**Test Steps:**
1. Open the Matrix Grid page
2. Verify proposals are displayed in the grid
3. Check status badges (color-coded):
   - Pending = Yellow
   - Approved = Green
   - Rejected = Red
4. Verify all columns display data:
   - ID
   - Workflow
   - Status
   - Event
   - User
   - Created
   - Actions
5. Try sorting by clicking column headers
6. Try filtering using the filter icons
7. Click "Export CSV" button

**Expected Result:**
- ✅ Grid displays all proposals
- ✅ Status badges are color-coded
- ✅ Sorting works
- ✅ Filtering works
- ✅ CSV export works

---

## Test 3: Proposal Modal (Logic Card)

**Test Steps:**
1. In the Matrix Grid, click on any proposal row
2. Modal should open with:
   - Status badge
   - Event Information section
   - Metadata (JSON format)
   - Close button
3. Click outside the modal (on the dark overlay)
4. Click the close button (X)

**Expected Result:**
- ✅ Modal opens on row click
- ✅ All data displays correctly
- ✅ JSON metadata is formatted
- ✅ Can close by clicking outside
- ✅ Can close with X button

---

## Test 4: Realtime Subscriptions

**Test Steps:**
1. Open Matrix Grid: http://localhost:3000/matrix
2. Keep the page open
3. In Supabase Dashboard SQL Editor, run:

```sql
-- INSERT test (should appear instantly in grid)
INSERT INTO process_events (
  id, event_name, event_type, event_metadata, user_id, workflow_id
) VALUES 
  ('realtime-test-1', 'test_insert', 'test', '{"status": "pending"}'::jsonb, 'realtime-user', 'wf-test');

-- Wait 2 seconds, then UPDATE (status should change)
UPDATE process_events 
SET event_metadata = '{"status": "approved"}'::jsonb 
WHERE id = 'realtime-test-1';

-- Wait 2 seconds, then DELETE (should disappear)
DELETE FROM process_events WHERE id = 'realtime-test-1';
```

**Expected Result:**
- ✅ New proposal appears instantly (no page refresh)
- ✅ Toast notification: "New proposal: test_insert"
- ✅ Status changes to "approved" (updates in real-time)
- ✅ Toast notification: "Proposal ... updated"
- ✅ Proposal disappears after delete
- ✅ No manual refresh needed

---

## Test 5: Approve/Reject Actions

**Test Steps:**
1. Find a proposal with status = "pending"
2. Click the green checkmark icon (Approve)
3. Watch for:
   - Loading spinner on button
   - Toast notification
   - Status badge changes to "approved"
4. Find another pending proposal
5. Click the red X icon (Reject)
6. Watch for:
   - Loading spinner
   - Toast notification
   - Status badge changes to "rejected"

**Expected Result:**
- ✅ Approve button works
- ✅ Loading state shows during API call
- ✅ Toast shows "Proposal approved successfully"
- ✅ Status updates to "approved"
- ✅ Reject button works
- ✅ Toast shows "Proposal rejected successfully"
- ✅ Status updates to "rejected"

**Note:** If you see an error, it means:
- Temporal workflow doesn't exist yet (expected)
- The signal API still works (returns proper error)
- Local state still updates correctly

---

## Test 6: Temporal Signal API

**Test Steps:**
1. Start a test workflow in Python:

```python
# In a terminal:
cd scripts/phase4/testing
python test_temporal_signal.py
```

2. The script will:
   - Start an approval workflow
   - Wait for signals
   - Print the workflow ID

3. Copy the workflow ID

4. In Matrix Grid, use browser DevTools console:

```javascript
// Test approve signal
fetch('/api/temporal/signal', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    workflowId: 'approval-test-workflow-001',  // Use the ID from Python script
    signalName: 'approve_signal',
    signalArgs: { proposalId: 'test-001', action: 'approve' }
  })
}).then(r => r.json()).then(console.log)
```

5. Check Python terminal for signal reception

**Expected Result:**
- ✅ API returns 200 success
- ✅ Python script prints "Received APPROVE signal"
- ✅ Workflow completes with approved status

---

## Test 7: Notification Toast System

**Test Steps:**
1. Trigger various actions:
   - Approve a proposal
   - Reject a proposal
   - Export CSV
   - Cause an error (click action on non-existent workflow)
2. For each action, verify:
   - Toast appears in top-right corner
   - Correct color (green/red/blue/yellow)
   - Correct icon
   - Message is clear
   - Auto-dismisses after 5 seconds
   - Can manually close with X button

**Expected Result:**
- ✅ Success toasts are green
- ✅ Error toasts are red
- ✅ Info toasts are blue
- ✅ Toasts auto-dismiss
- ✅ Can manually close
- ✅ Multiple toasts stack vertically

---

## Test 8: Authentication (OAuth)

**Test Steps:**
1. Open: http://localhost:3000/login
2. Click "Sign in with Google" button
3. Complete OAuth flow
4. Verify redirect back to dashboard
5. Check header shows user profile
6. Click logout in profile dropdown

**Expected Result:**
- ✅ Google OAuth works
- ✅ GitHub OAuth works
- ✅ User session persists
- ✅ Protected routes work
- ✅ Logout works

---

## Test 9: Responsive Design

**Test Steps:**
1. Open DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test on:
   - Mobile (375px)
   - Tablet (768px)
   - Desktop (1920px)
4. Verify:
   - Sidebar collapses on mobile
   - Hamburger menu appears
   - Grid adapts
   - Dashboard cards reflow

**Expected Result:**
- ✅ Mobile layout works
- ✅ Sidebar is collapsible
- ✅ No horizontal scroll
- ✅ Touch-friendly buttons

---

## Test 10: Error Handling

**Test Steps:**
1. Disconnect from network
2. Try to load Matrix Grid
3. Verify error message
4. Reconnect
5. Try invalid workflow ID in action
6. Verify error toast

**Expected Result:**
- ✅ Network errors handled gracefully
- ✅ Error messages are user-friendly
- ✅ Retry mechanisms work
- ✅ No unhandled exceptions

---

## Checklist Summary

### Core Features
- [ ] Dashboard stats loading
- [ ] Matrix Grid data display
- [ ] Proposal modal opens
- [ ] Realtime INSERT updates
- [ ] Realtime UPDATE updates
- [ ] Realtime DELETE updates
- [ ] Approve action works
- [ ] Reject action works
- [ ] Temporal signal API
- [ ] Toast notifications

### UI/UX
- [ ] Status badges color-coded
- [ ] Loading states show
- [ ] Sorting works
- [ ] Filtering works
- [ ] CSV export works
- [ ] Modal closes correctly
- [ ] Responsive on mobile
- [ ] Error handling graceful

### Integration
- [ ] Supabase queries work
- [ ] Realtime subscriptions work
- [ ] Temporal signals work
- [ ] Auth session persists
- [ ] RLS enforced (if enabled)

---

## Common Issues & Solutions

### Issue: "Realtime not updating"
**Solution:**
1. Check browser console for errors
2. Verify Realtime is enabled in Supabase Dashboard
3. Check RLS policies allow reading
4. Refresh the page

### Issue: "Approve/Reject returns 404"
**Solution:**
- Expected if no workflow exists
- Start a test workflow first
- API error handling is working correctly

### Issue: "Dashboard shows 0 for all stats"
**Solution:**
- Check if test data was inserted
- Verify RLS policies allow reading
- Check browser console for errors

### Issue: "Toast notifications not appearing"
**Solution:**
- Check z-index conflicts
- Verify NotificationToast is in layout
- Check browser console for React errors

---

## Next Steps After Testing

Once all tests pass:
1. Mark Phase 4.2 as complete ✅
2. Begin Phase 4.3 enhancements
3. Add pagination to grid
4. Build analytics dashboard
5. Write unit tests

---

## Testing Status

**Last Updated:** 2026-01-30  
**Phase:** 4.2 - Real-time & Actions  
**Status:** Ready for Manual Testing  

Frontend: http://localhost:3000  
Matrix Grid: http://localhost:3000/matrix  
Temporal UI: http://localhost:8080
