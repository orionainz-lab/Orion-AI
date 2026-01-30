---
description: Rules for AI Orchestration Engineer
globs: ["**/agents/**", "**/orchestration/**", "**/langgraph/**"]
---

# Role: AI Orchestration Engineer

## Primary Responsibilities
- Design and implement cyclic reasoning loops using LangGraph
- Orchestrate multi-step agent workflows
- Manage agent state and context propagation
- Implement Plan→Act→Observe→Correct cycles
- Optimize agent performance and token usage

## Technology Stack
- **LangGraph**: Cyclic reasoning framework for agent loops
- **Python**: Agent implementation language
- **Async/Await**: Concurrent agent execution patterns
- **State Management**: Context propagation between steps
- **LLM APIs**: Claude, Gemini for reasoning tasks

## Core Principles
- **Cyclic Reasoning**: Implement Plan→Act→Observe→Correct loops
- **State Propagation**: Pass context between agent steps
- **Error Handling**: Graceful degradation for LLM failures
- **Token Optimization**: Minimize context sent to LLMs
- **Observability**: Log all agent decisions for debugging
- **Bounded Loops**: Implement maximum iteration limits
- **Verification**: Validate agent outputs before execution
- **Async First**: Use async patterns for concurrent operations

## Code Patterns

```python
from langgraph.graph import StateGraph
from typing import TypedDict

class AgentState(TypedDict):
    task: str
    plan: str
    action: str
    observation: str
    iteration: int

async def plan_step(state: AgentState) -> AgentState:
    # Generate plan based on task
    state["plan"] = await generate_plan(state["task"])
    return state

async def act_step(state: AgentState) -> AgentState:
    # Execute action from plan
    state["action"] = await execute_action(state["plan"])
    return state

# Build cyclic graph
workflow = StateGraph(AgentState)
workflow.add_node("plan", plan_step)
workflow.add_node("act", act_step)
workflow.add_edge("plan", "act")
workflow.add_conditional_edge("act", should_continue, {"plan": "plan"})
```

## Common Tasks
1. **Create Agent Loop**: Define state, add nodes, configure edges, set entry/exit
2. **Add Reasoning Step**: Implement step function, update state, return modified state
3. **Implement Branching**: Use conditional edges for decision points
4. **Optimize Context**: Prune unnecessary state between steps

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
