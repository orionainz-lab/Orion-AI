# ADR-006: Worker Deployment Pattern

**Status**: Accepted  
**Date**: 2026-01-30  
**Context**: Phase 1 - The Durable Foundation  
**Deciders**: AI + Developer (Distributed Systems Engineer persona)

---

## Context

Temporal workers execute workflows and activities. We need to decide how workers are organized:
- Single monolithic worker (all workflows + activities)
- Multiple specialized workers (per domain or task queue)
- Dynamic worker pools (auto-scaling)

This decision impacts:
- Development complexity (now)
- Operational simplicity (Phase 1)
- Scalability (future phases)
- Resource utilization

---

## Decision

**Single Monolithic Worker for Phase 1, Specialize Later**

### Phase 1 (Now)
- One worker process
- Handles all workflows and activities
- Single task queue: "default"
- Simple deployment, easy debugging

### Phase 2-3 (Future)
- Split into domain-specific workers
- Separate task queues per domain
- Example: verification_queue, integration_queue

### Phase 4+ (Production)
- Auto-scaling worker pools
- Kubernetes deployment
- Load-based scaling

---

## Rationale

### Why Not Other Options?

**❌ Multiple Specialized Workers from Start**
- Premature optimization
- Added complexity without benefit
- Phase 1 has only 1-2 workflows
- Harder to debug (multiple processes)

**❌ Dynamic Worker Pools**
- Requires Kubernetes or orchestration
- Overkill for local development
- Adds operational burden too early

### Why Monolithic Works (For Now)

✅ **Simplicity**
- One process to start/stop/debug
- No inter-worker coordination needed
- Clear logs from single source

✅ **Phase 1 Scope is Small**
- Only 2 workflows (DurableDemo, Approval)
- Minimal activities (~5 total)
- Low execution volume (development testing)

✅ **Easy Migration Path**
- Task queue is just a string
- Refactoring is trivial (change task_queue parameter)
- No architectural rework needed

✅ **Resource Efficient**
- Lower memory footprint
- Fewer Docker containers
- Faster local development

---

## Consequences

### Positive
- ✅ Faster Phase 1 implementation
- ✅ Simpler debugging (one worker to watch)
- ✅ Lower resource usage on dev machines
- ✅ Easy to test end-to-end locally

### Negative
- ⚠️ All activities share resources
  - **Mitigation**: Acceptable for Phase 1 volume
- ⚠️ One worker failure stops all execution
  - **Mitigation**: Acceptable for development, fix in production
- ⚠️ Need refactoring for production scale
  - **Mitigation**: Expected, migration path is clear

### Neutral
- Phase 2+ will require worker split (planned)
- Production deployment will differ (expected)

---

## Implementation

### Phase 1: Monolithic Worker

```python
# temporal/workers/worker.py

import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

# Import all workflows
from temporal.workflows.durable_demo import DurableDemoWorkflow
from temporal.workflows.approval_workflow import ApprovalWorkflow

# Import all activities
from temporal.activities.test_activities import (
    process_data,
    long_running_task,
    send_notification
)

async def main():
    client = await Client.connect("localhost:7233")
    
    # Single worker, single task queue
    worker = Worker(
        client,
        task_queue="default",
        workflows=[DurableDemoWorkflow, ApprovalWorkflow],
        activities=[process_data, long_running_task, send_notification]
    )
    
    print("Worker started on task_queue='default'")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Phase 2-3: Specialized Workers

```python
# temporal/workers/verification_worker.py
async def main():
    client = await Client.connect(...)
    
    verification_worker = Worker(
        client,
        task_queue="verification",
        workflows=[VerificationWorkflow],
        activities=[validate_syntax, check_ast]
    )
    
    await verification_worker.run()

# temporal/workers/integration_worker.py
async def main():
    client = await Client.connect(...)
    
    integration_worker = Worker(
        client,
        task_queue="integration",
        workflows=[IntegrationWorkflow],
        activities=[call_api, transform_data]
    )
    
    await integration_worker.run()
```

### Phase 4+: Kubernetes Deployment

```yaml
# k8s/worker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: temporal-worker
spec:
  replicas: 3  # Auto-scaled by HPA
  template:
    spec:
      containers:
      - name: worker
        image: platform/worker:latest
        env:
        - name: TEMPORAL_HOST
          value: "temporal.default.svc.cluster.local:7233"
        - name: TASK_QUEUE
          value: "default"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

---

## Migration Strategy

### Step 1: Phase 1 (Now) - Monolithic
- **Task Queue**: `default`
- **Workers**: 1
- **Workflows**: DurableDemo, Approval
- **Activities**: ~5 basic activities

### Step 2: Phase 2 (Verification Layer) - First Split
- **Task Queues**: `default`, `verification`
- **Workers**: 2 (general, verification)
- **Reason**: AST verification is compute-intensive, isolate

### Step 3: Phase 3 (Integration Layer) - Domain Split
- **Task Queues**: `default`, `verification`, `integration`
- **Workers**: 3
- **Reason**: API calls have different retry/timeout needs

### Step 4: Phase 4+ (Production) - Auto-Scaling
- **Task Queues**: Multiple per domain
- **Workers**: N (auto-scaled)
- **Reason**: Production load requires horizontal scaling

### Code Changes Required for Migration

```python
# Phase 1 (current)
await client.start_workflow(
    MyWorkflow.run,
    task_queue="default"  # ← Only change needed
)

# Phase 2+ (after split)
await client.start_workflow(
    VerificationWorkflow.run,
    task_queue="verification"  # ← Changed to specialized queue
)
```

**Impact**: Minimal - just string parameter changes

---

## Monitoring Strategy

### Phase 1 (Local Development)
- **Logs**: Console output from single worker
- **UI**: Temporal UI (localhost:8080)
- **Metrics**: None (manual observation)

### Phase 2-3 (Staging)
- **Logs**: Structured JSON logs per worker
- **Metrics**: Worker poll count, activity execution time
- **Alerts**: Worker crash detection

### Phase 4+ (Production)
- **Logs**: Centralized (ELK/Datadog)
- **Metrics**: Prometheus + Grafana dashboards
- **Alerts**: PagerDuty integration
- **Tracing**: OpenTelemetry

---

## Performance Characteristics

### Monolithic Worker (Phase 1)

| Metric | Target | Actual (TBD) |
|--------|--------|--------------|
| Startup Time | < 2s | _To be measured_ |
| Memory Usage | < 256MB | _To be measured_ |
| Workflow Start Latency | < 500ms | _To be measured_ |
| Activity Execution | < 1s avg | _To be measured_ |

### Specialized Workers (Phase 2+)

| Worker Type | Workflows | Activities | Task Queue |
|-------------|-----------|------------|------------|
| General | DurableDemo, Approval | process_data, send_notification | default |
| Verification | VerificationWorkflow | validate_syntax, check_ast | verification |
| Integration | IntegrationWorkflow | call_api, transform_data | integration |

---

## Alternatives Considered

| Option | Pros | Cons | Phase 1 Fit | Future Fit |
|--------|------|------|-------------|------------|
| **Monolithic (CHOSEN)** | Simple, fast dev | No isolation | ✅ Perfect | ⚠️ Refactor |
| Specialized from Start | Clean separation | Premature complexity | ❌ Overkill | ✅ Good |
| Dynamic Pools | Auto-scales | Requires K8s | ❌ Too complex | ✅ Ideal |
| Serverless Workers | No infra | Cold starts, limits | ❌ Immature | ⚠️ Maybe |

---

## Decision Rationale Summary

**Choose simplicity now, scale later**

- Phase 1 is about proving durability, not scale
- Monolithic worker is fastest path to validation
- Migration to specialized workers is straightforward
- Clear evolution path to production

**Key Principle**: Don't optimize what you haven't measured yet.

---

## Related Decisions

- **ADR-004**: Temporal Deployment Strategy
  - Workers connect to local Temporal (dev) or Cloud (prod)
- **ADR-005**: Workflow State Persistence
  - Workers execute activities that write to Supabase

---

## Testing Strategy

```python
# test_worker.py

async def test_monolithic_worker_handles_multiple_workflow_types():
    """Verify single worker can execute different workflows."""
    client = await Client.connect(...)
    
    # Start workflows of different types
    handle1 = await client.start_workflow(
        DurableDemoWorkflow.run,
        task_queue="default"
    )
    handle2 = await client.start_workflow(
        ApprovalWorkflow.run,
        task_queue="default"
    )
    
    # Both should execute successfully
    result1 = await handle1.result()
    result2 = await handle2.result()
    
    assert result1 is not None
    assert result2 is not None

async def test_worker_restart_recovery():
    """Verify worker restart doesn't lose executions."""
    # Start workflow
    handle = await client.start_workflow(...)
    
    # Kill worker
    kill_worker()
    
    # Restart worker
    restart_worker()
    
    # Verify workflow completes
    result = await handle.result()
    assert result is not None
```

---

## References

- [Temporal Worker Documentation](https://docs.temporal.io/workers)
- [Task Queues Guide](https://docs.temporal.io/tasks#task-queues)
- Phase 1 Architecture: `build_plan/phase1-architecture.md`

---

**Status**: ✅ Accepted and Ready for Implementation

**Next Review**: After Phase 2 begins (reassess need for worker split)
