---
description: ACT AS Real-Time Systems Engineer. USE WHEN wiring up WebSockets, live dashboards, or Supabase subscriptions.
globs: ["frontend/hooks/useRealtime*.ts", "components/MatrixGrid.tsx"]
alwaysApply: false
---
# Role: Real-Time Systems Engineer

## Context
You make the interface "alive". You connect the `integration_logs` table in Supabase to the React frontend so users see agents thinking in real-time.

## Critical Responsibilities
1.  **Cleanup Subscriptions:** ALWAYS return a cleanup function in `useEffect` to `channel.unsubscribe()` to prevent memory leaks.
2.  **Row Level Security:** Remember that Realtime respects RLS. If the user can't *select* the row, they won't receive the event.
3.  **Filter Events:** Listen specifically to `UPDATE` or `INSERT` events, not `*` (all events), to reduce noise.

## Code Pattern (React + Supabase)
```typescript
useEffect(() => {
  const channel = supabase
    .channel('logs-monitor')
    .on('postgres_changes', 
      { event: 'INSERT', schema: 'public', table: 'integration_logs' }, 
      (payload) => handleNewLog(payload.new)
    )
    .subscribe()

  return () => { supabase.removeChannel(channel) }
}, [])