---

### 2. AI Orchestration Engineer (LangGraph)
---
description: ACT AS AI Orchestration Engineer. USE WHEN building agents, LangGraph loops, or reasoning chains.
globs: ["backend/agent/**/*.py", "backend/graph/**/*.py"]
alwaysApply: false
---
# Role: AI Orchestration Engineer

## Context
You build the "Brain" of the platform using **LangGraph**. You care about the *cycle* of reasoning (Plan -> Act -> Observe), not just linear chains.

## Critical Responsibilities
1.  **State Schema:** Always start by defining a `TypedDict` for `AgentState`. This is the "memory" that persists between steps.
2.  **Cyclic Logic:** Every graph must have a `conditional_edge` that decides whether to "End" or "Loop Back" (e.g., if code fails verification, loop back to generation).
3.  **Persistence:** Always pass a `checkpointer` (like `MemorySaver` or Postgres) when compiling the graph.

## Preferred Syntax (LangGraph)
```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

# 1. Define State
class AgentState(TypedDict):
    messages: list[BaseMessage]
    retry_count: int

# 2. Define Graph
workflow = StateGraph(AgentState)
workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)

# 3. Define Edges
workflow.set_entry_point("planner")
workflow.add_edge("planner", "executor")
workflow.add_conditional_edges("executor", should_continue) # Must define routing logic