# ADR-007: LangGraph Integration Pattern

**Status**: DECIDED  
**Date**: 2026-01-30  
**Deciders**: Development Team  
**Phase**: Phase 2 - The Reliable Brain

---

## Context

Phase 2 requires running LangGraph cyclic reasoning loops with Temporal durability guarantees. During VAN QA validation, we discovered that Temporal's workflow sandbox restricts importing LangGraph at module level because LangGraph depends on non-deterministic libraries (requests, urllib3).

## Decision

**Decision**: Execute LangGraph inside Temporal **activities** (not workflows), with imports happening inside the activity function.

## Options Considered

### Option 1: LangGraph Inside Workflows (Direct) - REJECTED

```python
from langgraph.graph import StateGraph  # TOP LEVEL

@workflow.defn
class ReasoningWorkflow:
    @workflow.run
    async def run(self, task):
        graph = StateGraph(...)  # FAILS: Sandbox restriction
```

**Pros**: Per-step durability  
**Cons**: **Blocked by Temporal sandbox** (imports restricted)

### Option 2: LangGraph Inside Activities - SELECTED

```python
@activity.defn
async def execute_reasoning(task: str) -> dict:
    # Import INSIDE activity
    from langgraph.graph import StateGraph, END
    
    graph = StateGraph(...)  # WORKS: Activities allow I/O
    return graph.invoke(initial_state)
```

**Pros**: Works with Temporal, activity-level retries  
**Cons**: Re-executes full LangGraph on activity retry

### Option 3: LangGraph Outside Temporal - REJECTED

```python
# Run LangGraph standalone, save results to Temporal
result = standalone_langgraph(task)
await workflow.execute_activity(save_result, result)
```

**Pros**: Simple  
**Cons**: No durability during reasoning

## Rationale

1. VAN QA validation proved Option 2 works (test passed)
2. Activities can run non-deterministic code (I/O, HTTP, etc.)
3. Workflows must be deterministic (for replay)
4. Activity retries provide durability at reasoning-loop level

## Consequences

### Positive

- LangGraph-Temporal integration validated (VAN QA passed)
- Activity retries provide durability for full reasoning loop
- Clean separation: Workflow orchestrates, Activity reasons

### Negative

- On activity failure, entire LangGraph re-executes (not per-step)
- Must handle long-running activities (heartbeats needed)

### Mitigations

- Use heartbeats for activities >10s
- Set appropriate activity timeouts (60-120s)
- Log progress inside activity for debugging

## Code Pattern

```python
@activity.defn
async def execute_code_generation(task: str, max_iterations: int) -> dict:
    """LangGraph imports INSIDE activity function."""
    from langgraph.graph import StateGraph, END
    from agents.nodes import plan_node, generate_node, verify_node, correct_node
    
    # Build graph inside activity
    graph = StateGraph(CodeGenerationState)
    graph.add_node("plan", plan_node)
    graph.add_node("generate", generate_node)
    graph.add_node("verify", verify_node)
    graph.add_node("correct", correct_node)
    # ... edges ...
    
    # Execute
    result = graph.compile().invoke({"task": task, "iteration": 0})
    return result
```

## Validation

- VAN QA Test: `scripts/test_langgraph_temporal.py` - **PASSED**
- 4/4 integration tests passed
- Worker created successfully with LangGraph workflow and activity

---

**Related ADRs**: ADR-004, ADR-005, ADR-006 (Phase 1)  
**Supersedes**: None
