# ADR-005: Workflow State Persistence Strategy

**Status**: Accepted  
**Date**: 2026-01-30  
**Context**: Phase 1 - The Durable Foundation  
**Deciders**: AI + Developer (Distributed Systems Engineer persona)

---

## Context

Our platform has TWO persistence layers:
1. **Temporal.io**: Event sourcing for workflow execution state
2. **Supabase**: Relational database for business data

We need clear guidelines on:
- What data goes where
- When to write to Supabase vs. rely on Temporal
- How to maintain consistency between systems

This decision impacts durability guarantees, query patterns, and system complexity.

---

## Decision

**Temporal-First with Selective Supabase Persistence**

### Data Ownership Model

| Data Type | Primary Storage | Reason |
|-----------|-----------------|--------|
| **Workflow execution state** | Temporal | Durability, replay, consistency |
| **Business entities** | Supabase | Queryability, relationships, reporting |
| **Approval decisions** | Supabase | Audit trail, compliance, user queries |
| **Temporary computation** | Temporal | Ephemeral, no long-term persistence needed |
| **Process logs/audit** | Supabase | Long-term retention, analytics |

### Key Principle

**Workflows orchestrate, Activities write business data**

---

## Rationale

### Why Not Other Options?

**❌ Explicit Supabase Persistence Everywhere**
- Duplicates Temporal's built-in durability
- Increases complexity (two sources of truth)
- Risk of inconsistency between systems
- Manual state management (defeats Temporal's purpose)

**❌ Dual Persistence (Write Everything to Both)**
- Massive complexity overhead
- Consistency guarantees difficult
- Performance penalty (double writes)
- Maintenance burden (sync issues)

### Why Temporal-First Works

✅ **Leverage Temporal's Core Strength**
- Temporal is designed for workflow state durability
- Event sourcing provides automatic audit trail
- Replay guarantees consistency

✅ **Clear Separation of Concerns**
- Temporal: Execution state, coordination, durability
- Supabase: Business data, queries, relationships

✅ **Simpler Mental Model**
- Workflows = pure orchestration logic
- Activities = side effects (including database writes)
- No workflow code touches database directly

---

## Consequences

### Positive
- ✅ Leverage Temporal's durability guarantees
- ✅ Clear data ownership model
- ✅ Simpler workflow code (no manual state management)
- ✅ Better testability (workflows are deterministic)

### Negative
- ⚠️ Need clear guidelines on what goes to Supabase
  - **Mitigation**: Document decision tree (see below)
- ⚠️ Activities must be idempotent
  - **Mitigation**: Use Supabase upsert, transactions
- ⚠️ No direct SQL queries on workflow state
  - **Mitigation**: Use Temporal queries for workflow data

### Neutral
- Business logic in activities, not workflows
- Temporal UI shows execution history, not business data

---

## Implementation Guidelines

### ✅ CORRECT: Activity Writes to Supabase

```python
from temporalio import workflow, activity
from supabase import create_client

# Activity can do I/O
@activity.defn
async def save_order(order_data: dict) -> str:
    supabase = create_client(...)
    result = await supabase.table("orders").insert(order_data).execute()
    return result.data[0]["id"]

# Workflow orchestrates
@workflow.defn
class OrderWorkflow:
    @workflow.run
    async def run(self, order_data: dict) -> str:
        # Workflow state in Temporal
        self._status = "processing"
        
        # Business data to Supabase via activity
        order_id = await workflow.execute_activity(
            save_order,
            order_data,
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        self._status = "completed"
        return order_id
```

### ❌ INCORRECT: Workflow Writes to Supabase

```python
# DON'T DO THIS - Workflows can't do I/O
@workflow.defn
class BadWorkflow:
    @workflow.run
    async def run(self, order_data: dict):
        # NEVER do this - violates Temporal's determinism
        supabase = create_client(...)
        await supabase.table("orders").insert(order_data).execute()
```

### Decision Tree: Where Does Data Go?

```
Question: Does this data need to...
│
├─ Survive workflow completion? 
│  ├─ Yes → Supabase (business data, audit logs)
│  └─ No  → Temporal (workflow state only)
│
├─ Be queried outside workflow execution?
│  ├─ Yes → Supabase (reports, dashboards, user queries)
│  └─ No  → Temporal (internal coordination state)
│
├─ Relate to other business entities?
│  ├─ Yes → Supabase (foreign keys, joins)
│  └─ No  → Temporal (isolated workflow state)
│
└─ Need long-term retention (compliance)?
   ├─ Yes → Supabase (regulatory requirements)
   └─ No  → Temporal (until workflow retention expires)
```

---

## Examples by Data Type

### Workflow Execution State (Temporal)
```python
@workflow.defn
class ApprovalWorkflow:
    def __init__(self):
        self._approved = False  # Temporal manages this
        self._retry_count = 0    # Temporal manages this
```

### Business Entities (Supabase)
```python
@activity.defn
async def create_order(order: dict) -> str:
    # Business data persisted in Supabase
    result = await supabase.table("orders").insert({
        "customer_id": order["customer_id"],
        "total": order["total"],
        "status": "pending"
    }).execute()
    return result.data[0]["id"]
```

### Approval Decisions (Supabase)
```python
@activity.defn
async def record_approval(workflow_id: str, decision: str) -> None:
    # Audit trail in Supabase
    await supabase.table("approvals").insert({
        "workflow_id": workflow_id,
        "decision": decision,
        "approved_by": get_current_user(),
        "timestamp": datetime.utcnow()
    }).execute()
```

### Temporary Computation (Temporal)
```python
@workflow.defn
class DataProcessingWorkflow:
    def __init__(self):
        self._temp_results = []  # Only needed during execution
    
    @workflow.run
    async def run(self):
        # Intermediate results stored in Temporal
        for item in data:
            result = await workflow.execute_activity(process_item, item)
            self._temp_results.append(result)
        
        # Final result written to Supabase via activity
        await workflow.execute_activity(save_final_result, self._temp_results)
```

---

## Alternatives Considered

| Option | Pros | Cons | Complexity | Consistency |
|--------|------|------|------------|-------------|
| **Temporal-First (CHOSEN)** | Simple, leverages Temporal | Guidelines needed | Low | High |
| Explicit Supabase | Full control | Duplicates Temporal | High | Medium |
| Dual Persistence | Maximum safety | Very complex | Very High | Low |
| Temporal Only | Simplest | Can't query business data | Very Low | N/A |

---

## Related Decisions

- **ADR-004**: Temporal Deployment Strategy
  - Temporal's persistence layer uses PostgreSQL
- **ADR-006**: Worker Deployment Pattern
  - Workers execute activities that write to Supabase

---

## Testing Strategy

### Validate Durability
```python
async def test_workflow_survives_crash():
    # Start workflow
    handle = await client.start_workflow(OrderWorkflow.run, ...)
    
    # Kill worker (chaos test)
    kill_worker()
    
    # Restart worker
    restart_worker()
    
    # Verify workflow completes (Temporal state recovered)
    result = await handle.result()
    assert result is not None
    
    # Verify business data in Supabase
    order = await supabase.table("orders").select("*").eq("id", result).execute()
    assert order.data[0]["status"] == "completed"
```

---

## References

- [Temporal Durability Guarantees](https://docs.temporal.io/concepts/what-is-temporal)
- [Workflow Determinism Requirements](https://docs.temporal.io/workflows#deterministic-constraints)
- Phase 1 Architecture: `build_plan/phase1-architecture.md`
- Supabase Integration: `memory-bank/techContext.md`

---

**Status**: ✅ Accepted and Ready for Implementation
