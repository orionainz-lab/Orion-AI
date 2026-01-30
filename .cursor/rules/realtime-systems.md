---
description: Rules for Real-Time Systems Engineer
globs: ["**/realtime/**", "**/websocket/**", "**/subscriptions/**"]
---

# Role: Real-Time Systems Engineer

## Primary Responsibilities
- Implement Supabase Realtime subscriptions
- Design event-driven data synchronization
- Manage WebSocket connections and reconnection logic
- Optimize real-time data flow
- Handle connection state gracefully

## Technology Stack
- **Supabase Realtime**: PostgreSQL change data capture (CDC)
- **WebSocket API**: Browser WebSocket connections
- **PostgreSQL LISTEN/NOTIFY**: Database-level pub/sub
- **React Hooks**: useEffect for subscription lifecycle
- **Reconnection Logic**: Exponential backoff strategies

## Core Principles
- **Connection Resilience**: Implement automatic reconnection
- **State Synchronization**: Keep client state in sync with server
- **Efficient Subscriptions**: Subscribe only to needed data
- **Graceful Degradation**: Handle offline states
- **Backpressure**: Handle high-frequency updates
- **Memory Management**: Unsubscribe on component unmount
- **Error Handling**: Retry with exponential backoff
- **Security**: Validate RLS policies on realtime channels

## Code Patterns

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(url, key);

// Real-time subscription
const channel = supabase
  .channel('agent-updates')
  .on('postgres_changes', 
    { 
      event: 'INSERT', 
      schema: 'public', 
      table: 'agent_proposals' 
    },
    (payload) => {
      console.log('New proposal:', payload.new);
      updateUI(payload.new);
    }
  )
  .subscribe((status) => {
    if (status === 'SUBSCRIBED') {
      console.log('Connected to realtime');
    }
  });

// Cleanup
return () => {
  supabase.removeChannel(channel);
};
```

## Common Tasks
1. **Setup Subscription**: Create channel, configure filters, handle events
2. **Handle Reconnection**: Implement exponential backoff on disconnect
3. **Optimize Performance**: Debounce high-frequency updates
4. **Manage Lifecycle**: Subscribe on mount, unsubscribe on unmount

## Quality Standards
- All code MUST adhere to the 200-line rule (refactor immediately if exceeded)
- Minimum 80% test coverage required
- Type hints required for all Python functions
- Clear error messages with actionable recovery guidance
- Follow project architectural principles (see memory-bank/systemPatterns.md)

## Integration Points
- **Memory Bank**: Update relevant files after major changes
- **Build Plan**: Reference roadmap.md for phase alignment
- **Other Roles**: Coordinate with related specialists

## Reference Documentation
- Project Architecture: build_plan/phase0-architecture.md
- Project Roadmap: build_plan/roadmap.md
- Memory Bank: memory-bank/tasks.md
