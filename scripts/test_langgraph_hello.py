#!/usr/bin/env python
"""
VAN QA Test: LangGraph Hello World

Tests basic LangGraph functionality:
1. StateGraph creation
2. Node definition and execution
3. Edge configuration
4. State propagation between nodes
5. Conditional edge routing

This validates that LangGraph can be used for Phase 2.
"""

import asyncio
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END


# ==============================================================================
# TEST 1: Simple 2-Node Graph with State Propagation
# ==============================================================================

class SimpleState(TypedDict):
    """Simple state for basic test."""
    value: int
    history: list[str]


def increment_node(state: SimpleState) -> SimpleState:
    """First node: increment value and log."""
    state["value"] += 1
    state["history"].append(f"increment: {state['value']}")
    return state


def double_node(state: SimpleState) -> SimpleState:
    """Second node: double value and log."""
    state["value"] *= 2
    state["history"].append(f"double: {state['value']}")
    return state


def test_simple_graph():
    """Test 1: Basic 2-node linear graph."""
    print("\n" + "=" * 60)
    print("TEST 1: Simple 2-Node Linear Graph")
    print("=" * 60)
    
    # Build graph
    graph = StateGraph(SimpleState)
    graph.add_node("increment", increment_node)
    graph.add_node("double", double_node)
    
    graph.set_entry_point("increment")
    graph.add_edge("increment", "double")
    graph.add_edge("double", END)
    
    # Compile
    compiled = graph.compile()
    print("[OK] Graph compiled successfully")
    
    # Execute
    initial_state = {"value": 5, "history": []}
    result = compiled.invoke(initial_state)
    
    print(f"  Input:  value=5")
    print(f"  Output: value={result['value']}")
    print(f"  History: {result['history']}")
    
    # Validate
    expected_value = (5 + 1) * 2  # 6 * 2 = 12
    assert result["value"] == expected_value, f"Expected {expected_value}, got {result['value']}"
    assert len(result["history"]) == 2, f"Expected 2 history entries, got {len(result['history'])}"
    
    print("[PASS] TEST 1 PASSED: State propagation works correctly")
    return True


# ==============================================================================
# TEST 2: Conditional Edge Routing (Critical for Phase 2)
# ==============================================================================

class LoopState(TypedDict):
    """State for loop/conditional test."""
    counter: int
    max_iterations: int
    status: Literal["running", "complete"]


def process_node(state: LoopState) -> LoopState:
    """Process node: increment counter."""
    state["counter"] += 1
    # Update status based on counter
    if state["counter"] >= state["max_iterations"]:
        state["status"] = "complete"
    print(f"  Process iteration {state['counter']}/{state['max_iterations']} (status={state['status']})")
    return state


def should_continue(state: LoopState) -> str:
    """Conditional edge: decide to continue or end (no state modification here)."""
    if state["counter"] >= state["max_iterations"]:
        return "end"
    else:
        return "continue"


def test_conditional_graph():
    """Test 2: Graph with conditional edges (loop pattern)."""
    print("\n" + "=" * 60)
    print("TEST 2: Conditional Edge Routing (Loop Pattern)")
    print("=" * 60)
    
    # Build graph with conditional edge
    graph = StateGraph(LoopState)
    graph.add_node("process", process_node)
    
    graph.set_entry_point("process")
    graph.add_conditional_edges(
        "process",
        should_continue,
        {
            "continue": "process",  # Loop back
            "end": END              # Exit
        }
    )
    
    # Compile
    compiled = graph.compile()
    print("[OK] Graph with conditional edges compiled successfully")
    
    # Execute with max_iterations=3
    initial_state = {"counter": 0, "max_iterations": 3, "status": "running"}
    result = compiled.invoke(initial_state)
    
    print(f"  Final counter: {result['counter']}")
    print(f"  Final status: {result['status']}")
    
    # Validate
    assert result["counter"] == 3, f"Expected counter=3, got {result['counter']}"
    assert result["status"] == "complete", f"Expected status='complete', got {result['status']}"
    
    print("[PASS] TEST 2 PASSED: Conditional edges work correctly")
    return True


# ==============================================================================
# TEST 3: Async Node Execution (Required for Temporal integration)
# ==============================================================================

class AsyncState(TypedDict):
    """State for async test."""
    message: str
    steps: list[str]


async def async_step_1(state: AsyncState) -> AsyncState:
    """Async node 1."""
    await asyncio.sleep(0.1)  # Simulate async operation
    state["steps"].append("step_1")
    return state


async def async_step_2(state: AsyncState) -> AsyncState:
    """Async node 2."""
    await asyncio.sleep(0.1)  # Simulate async operation
    state["steps"].append("step_2")
    state["message"] = "completed"
    return state


async def test_async_graph():
    """Test 3: Async node execution."""
    print("\n" + "=" * 60)
    print("TEST 3: Async Node Execution")
    print("=" * 60)
    
    # Build async graph
    graph = StateGraph(AsyncState)
    graph.add_node("step_1", async_step_1)
    graph.add_node("step_2", async_step_2)
    
    graph.set_entry_point("step_1")
    graph.add_edge("step_1", "step_2")
    graph.add_edge("step_2", END)
    
    # Compile
    compiled = graph.compile()
    print("[OK] Async graph compiled successfully")
    
    # Execute asynchronously
    initial_state = {"message": "started", "steps": []}
    result = await compiled.ainvoke(initial_state)
    
    print(f"  Steps executed: {result['steps']}")
    print(f"  Final message: {result['message']}")
    
    # Validate
    assert result["steps"] == ["step_1", "step_2"], f"Wrong steps: {result['steps']}"
    assert result["message"] == "completed", f"Wrong message: {result['message']}"
    
    print("[PASS] TEST 3 PASSED: Async execution works correctly")
    return True


# ==============================================================================
# TEST 4: Complex State with Nested Dict (Simulates Code Generation State)
# ==============================================================================

class CodeGenState(TypedDict):
    """State simulating Phase 2 code generation loop."""
    task: str
    code: str
    errors: list[dict]
    iteration: int
    is_valid: bool


def plan_node(state: CodeGenState) -> CodeGenState:
    """Plan step."""
    print(f"  Planning for task: {state['task'][:30]}...")
    return state


def generate_node(state: CodeGenState) -> CodeGenState:
    """Generate code step."""
    state["iteration"] += 1
    # Simulate code generation (first attempt has errors, second is valid)
    if state["iteration"] == 1:
        state["code"] = "def hello():\n  print('Hello'  # Missing closing paren"
        state["is_valid"] = False
        state["errors"] = [{"line": 2, "message": "SyntaxError: missing ')'"}]
    else:
        state["code"] = "def hello():\n    print('Hello')"
        state["is_valid"] = True
        state["errors"] = []
    print(f"  Generated code (iteration {state['iteration']}), valid={state['is_valid']}")
    return state


def verify_node(state: CodeGenState) -> CodeGenState:
    """Verify step (simulated)."""
    print(f"  Verification: is_valid={state['is_valid']}")
    return state


def correct_node(state: CodeGenState) -> CodeGenState:
    """Correct step."""
    print(f"  Generating correction feedback for {len(state['errors'])} errors")
    return state


def should_loop(state: CodeGenState) -> str:
    """Decide to loop or end."""
    if state["is_valid"]:
        return "end"
    elif state["iteration"] >= 3:
        return "end"  # Max iterations
    else:
        return "correct"


def test_complex_state():
    """Test 4: Complex state simulating Phase 2 pattern."""
    print("\n" + "=" * 60)
    print("TEST 4: Complex State (Phase 2 Pattern Simulation)")
    print("=" * 60)
    
    # Build graph matching Phase 2 architecture
    graph = StateGraph(CodeGenState)
    graph.add_node("plan", plan_node)
    graph.add_node("generate", generate_node)
    graph.add_node("verify", verify_node)
    graph.add_node("correct", correct_node)
    
    graph.set_entry_point("plan")
    graph.add_edge("plan", "generate")
    graph.add_edge("generate", "verify")
    graph.add_conditional_edges(
        "verify",
        should_loop,
        {
            "end": END,
            "correct": "correct"
        }
    )
    graph.add_edge("correct", "generate")  # Loop back
    
    # Compile
    compiled = graph.compile()
    print("[OK] Complex graph (Phase 2 pattern) compiled successfully")
    
    # Execute
    initial_state = {
        "task": "Create a hello world function",
        "code": "",
        "errors": [],
        "iteration": 0,
        "is_valid": False
    }
    result = compiled.invoke(initial_state)
    
    print(f"  Final iteration: {result['iteration']}")
    print(f"  Final is_valid: {result['is_valid']}")
    print(f"  Final code:\n{result['code']}")
    
    # Validate
    assert result["is_valid"] == True, "Expected valid code after correction"
    assert result["iteration"] == 2, f"Expected 2 iterations, got {result['iteration']}"
    
    print("[PASS] TEST 4 PASSED: Complex state with loop correction works!")
    return True


# ==============================================================================
# MAIN
# ==============================================================================

async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("LANGGRAPH VAN QA VALIDATION")
    print("=" * 60)
    
    results = []
    
    # Run sync tests
    results.append(("Test 1: Simple Graph", test_simple_graph()))
    results.append(("Test 2: Conditional Edges", test_conditional_graph()))
    results.append(("Test 4: Complex State", test_complex_state()))
    
    # Run async test
    try:
        async_result = await test_async_graph()
        results.append(("Test 3: Async Execution", async_result))
    except Exception as e:
        print(f"[FAIL] Test 3 FAILED: {e}")
        results.append(("Test 3: Async Execution", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] LANGGRAPH VALIDATION: PASSED")
        print("   LangGraph is ready for Phase 2 integration")
    else:
        print("\n[ERROR] LANGGRAPH VALIDATION: FAILED")
        print("   Review failed tests before proceeding")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(main())
