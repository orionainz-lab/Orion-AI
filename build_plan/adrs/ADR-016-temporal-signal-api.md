# ADR-016: Temporal Signal API Approach

**Status**: ACCEPTED  
**Date**: 2026-01-30  
**Phase**: Phase 4 - Frontend  
**Deciders**: System Architect, Backend API Architect

---

## Context

The frontend needs to send approval/rejection signals to Temporal workflows when users click "Approve" or "Reject" buttons. However, browsers cannot directly connect to Temporal's gRPC server.

### Technical Constraint

**Temporal Protocol**: gRPC over HTTP/2  
**Browser Limitation**: No native gRPC support (requires gRPC-Web + Envoy proxy)  
**Security**: Temporal credentials must not be exposed to browser

---

## Decision

Create a **Next.js API Route** (`/api/temporal/signal`) as a server-side proxy to Temporal.

**Architecture**:
```
Browser → POST /api/temporal/signal → Temporal gRPC
```

---

## Rationale

### 1. Security

**Temporal Credentials Protected**:
- `@temporalio/client` runs on Next.js server (not browser)
- No Temporal address/credentials exposed to client
- Server validates user session before forwarding signal

**Example**:
```typescript
// app/api/temporal/signal/route.ts
export async function POST(request: NextRequest) {
  // Verify user session (Supabase Auth)
  const supabase = createServerClient();
  const { data: { session } } = await supabase.auth.getSession();
  
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  // Connect to Temporal (credentials on server)
  const connection = await Connection.connect({
    address: process.env.TEMPORAL_ADDRESS, // Not exposed to browser
  });
  
  // Send signal
  const client = new WorkflowClient({ connection });
  const handle = client.getHandle(workflowId);
  await handle.signal(signalName, signalArgs);
  
  return NextResponse.json({ success: true });
}
```

### 2. Simplicity

**No Extra Infrastructure**:
- No Envoy proxy needed (gRPC-Web)
- No separate FastAPI service
- No CORS configuration
- All in Next.js app

**Development**:
- Single codebase (frontend + API routes)
- Easy debugging (console logs in terminal)
- Fast iteration

### 3. Flexibility

**Middleware Capabilities**:
- Request validation (Zod schemas)
- Rate limiting
- Error handling
- Logging/monitoring
- Retry logic

**Example Validation**:
```typescript
const SignalRequestSchema = z.object({
  workflowId: z.string().uuid(),
  signalName: z.string().min(1),
  signalArgs: z.record(z.any()),
});

const body = await request.json();
const { workflowId, signalName, signalArgs } = SignalRequestSchema.parse(body);
```

### 4. Performance

**Latency**:
- Frontend → Next.js API: ~10-20ms (localhost)
- Next.js API → Temporal: ~20-30ms (gRPC)
- **Total**: ~30-50ms (acceptable for user action)

**Comparison**:
- Direct gRPC-Web: ~20-30ms (but requires Envoy proxy)
- Separate FastAPI service: ~50-70ms (extra network hop)

**Benefit**: API Route adds minimal latency while maximizing simplicity.

---

## Implementation

### API Route

**File**: `app/api/temporal/signal/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { Connection, WorkflowClient } from '@temporalio/client';
import { z } from 'zod';
import { createServerClient } from '@/lib/supabase/server';

const SignalRequestSchema = z.object({
  workflowId: z.string().uuid(),
  signalName: z.string().min(1),
  signalArgs: z.record(z.any()),
});

export async function POST(request: NextRequest) {
  try {
    // 1. Verify authentication
    const supabase = createServerClient();
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    
    // 2. Parse and validate request
    const body = await request.json();
    const { workflowId, signalName, signalArgs } = SignalRequestSchema.parse(body);
    
    // 3. Connect to Temporal
    const connection = await Connection.connect({
      address: process.env.TEMPORAL_ADDRESS || 'localhost:7233',
    });
    
    const client = new WorkflowClient({ connection });
    
    // 4. Send signal
    const handle = client.getHandle(workflowId);
    await handle.signal(signalName, signalArgs);
    
    // 5. Close connection
    await connection.close();
    
    return NextResponse.json({
      success: true,
      message: 'Signal sent successfully',
    });
  } catch (error) {
    console.error('Temporal signal error:', error);
    
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 }
      );
    }
    
    return NextResponse.json(
      { error: 'Failed to send signal', message: error.message },
      { status: 500 }
    );
  }
}
```

### Frontend Usage

```typescript
// hooks/use-approval.ts
export function useApproval() {
  const handleApprove = async (id: string, workflowId: string) => {
    const response = await fetch('/api/temporal/signal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        workflowId,
        signalName: 'approve_signal',
        signalArgs: { approved: true, proposalId: id },
      }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to approve proposal');
    }
  };
  
  return { handleApprove };
}
```

---

## Consequences

### Positive

✅ **Secure**: Temporal credentials never exposed to browser  
✅ **Simple**: No extra infrastructure (Envoy, separate service)  
✅ **Flexible**: Middleware for validation, logging, rate limiting  
✅ **Debuggable**: Server logs in terminal, easy to trace  
✅ **Fast**: <50ms latency (acceptable for user action)

### Negative

⚠️ **Extra Hop**: Frontend → Next.js → Temporal (~20-30ms overhead)  
⚠️ **Single Point of Failure**: If Next.js down, signals fail  
⚠️ **Scaling**: Next.js server must handle signal throughput

### Mitigation

**Latency**:
- Acceptable for user-initiated actions (not time-critical)
- Optimistic UI updates mask latency

**Availability**:
- Next.js deployed on Vercel (99.99% uptime SLA)
- Error handling with retries (client-side)

**Scaling**:
- Next.js API routes scale horizontally (serverless)
- Temporal client connection pooling

---

## Alternatives Considered

### Alternative 1: gRPC-Web + Envoy Proxy

**Architecture**:
```
Browser → gRPC-Web → Envoy Proxy → Temporal gRPC
```

**Pros**:
- Direct browser-to-Temporal communication
- Lower latency (~20-30ms)

**Cons**:
- Requires Envoy proxy (extra infrastructure)
- Complex configuration (gRPC-Web, CORS, TLS)
- Security risk (Temporal endpoint exposed)
- More moving parts (reliability concerns)

**Rejected Because**: Complexity outweighs latency benefit (30ms difference negligible for user actions).

### Alternative 2: Separate FastAPI Service

**Architecture**:
```
Browser → Next.js → FastAPI → Temporal gRPC
```

**Pros**:
- Python-native Temporal client
- Separation of concerns

**Cons**:
- Extra service to deploy/maintain
- Higher latency (~50-70ms)
- More complex architecture
- CORS configuration needed

**Rejected Because**: Unnecessary infrastructure, Next.js API routes sufficient.

### Alternative 3: Supabase Edge Function

**Architecture**:
```
Browser → Supabase Edge Function → Temporal gRPC
```

**Pros**:
- Globally distributed (low latency)
- Managed infrastructure

**Cons**:
- Deno runtime (not Node.js)
- `@temporalio/client` may not work in Deno
- Harder to debug than Next.js
- Additional dependency

**Rejected Because**: Uncertain Temporal client compatibility, harder debugging.

---

## Success Criteria

| Metric | Target | Validation |
|--------|--------|------------|
| **Latency** | <100ms | Browser DevTools Network tab |
| **Error Rate** | <1% | Monitoring logs |
| **Auth Check** | 100% | Security audit |
| **Type Safety** | 0 errors | `tsc --noEmit` |

---

## References

- [Temporal Signals Documentation](https://docs.temporal.io/workflows#signals)
- [Next.js API Routes](https://nextjs.org/docs/app/building-your-application/routing/route-handlers)
- [Temporal TypeScript SDK](https://docs.temporal.io/typescript)

---

**Status**: ACCEPTED  
**Last Reviewed**: 2026-01-30  
**Next Review**: Phase 4 BUILD (test latency and reliability)
