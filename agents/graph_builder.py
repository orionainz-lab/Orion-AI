"""
LangGraph StateGraph Builder

This module constructs the LangGraph StateGraph for code generation.
The graph implements the Plan -> Generate -> Verify -> Correct loop.

Graph Structure:
    START -> plan -> generate -> verify -> [conditional]
                                             |-> END (valid)
                                             |-> correct -> generate (loop)

Per ADR-007, this module is imported INSIDE Temporal activities,
not at module level, to avoid workflow sandbox restrictions.

Usage:
    # Inside a Temporal activity:
    from agents.graph_builder import build_code_generation_graph
    
    graph = build_code_generation_graph()
    result = graph.invoke(initial_state)
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def build_code_generation_graph() -> Any:
    """
    Build the code generation StateGraph.
    
    Returns:
        Compiled LangGraph ready for invocation
        
    Note:
        LangGraph is imported inside this function per ADR-007.
        This allows the function to be called from Temporal activities
        without triggering workflow sandbox restrictions.
    """
    logger.info("Building code generation graph...")
    
    # Import LangGraph inside function (ADR-007)
    from langgraph.graph import StateGraph, END
    
    # Import nodes
    from agents.nodes import (
        plan_node,
        generate_node,
        verify_node,
        correct_node,
        should_continue
    )
    from agents.state import CodeGenerationState
    
    # Create graph with state schema
    graph = StateGraph(CodeGenerationState)
    
    # ========== ADD NODES ==========
    graph.add_node("plan", plan_node)
    graph.add_node("generate", generate_node)
    graph.add_node("verify", verify_node)
    graph.add_node("correct", correct_node)
    
    # ========== DEFINE EDGES ==========
    
    # Entry point
    graph.set_entry_point("plan")
    
    # Linear edges
    graph.add_edge("plan", "generate")
    graph.add_edge("generate", "verify")
    
    # Conditional edge after verify
    graph.add_conditional_edges(
        "verify",
        should_continue,
        {
            "end": END,
            "correct": "correct"
        }
    )
    
    # Loop back from correct to generate
    graph.add_edge("correct", "generate")
    
    # ========== COMPILE ==========
    compiled = graph.compile()
    
    logger.info("Code generation graph built successfully")
    logger.info("  Nodes: plan -> generate -> verify -> [end | correct]")
    logger.info("  Max iterations controlled by state.max_iterations")
    
    return compiled


def visualize_graph() -> str:
    """
    Generate ASCII visualization of the graph.
    
    Returns:
        ASCII art representation of the graph structure
    """
    return """
    Code Generation Graph (Plan -> Generate -> Verify -> Correct Loop)
    
    +-------------------------------------------------------------+
    |                                                               |
    |   +-------+    +----------+    +----------+                 |
    |   | START |--->|   plan   |--->| generate |                 |
    |   +-------+    +----------+    +----------+                 |
    |                                      |                       |
    |                                      v                       |
    |                                +----------+                 |
    |                                |  verify  |                 |
    |                                +----------+                 |
    |                                      |                       |
    |                         +------------+------------+         |
    |                         v                         v         |
    |                   +----------+              +----------+    |
    |                   | is_valid |              | !is_valid|    |
    |                   |  = True  |              | && iter  |    |
    |                   |   OR     |              | < max    |    |
    |                   |iter>=max |              +----------+    |
    |                   +----------+                    |          |
    |                         |                         v          |
    |                         v                  +----------+     |
    |                   +----------+             | correct  |     |
    |                   |   END    |             +----------+     |
    |                   +----------+                    |          |
    |                                                   |          |
    |                    +------------------------------ +         |
    |                    |                                         |
    |                    v                                         |
    |              +----------+                                   |
    |              | generate | (loop back)                       |
    |              +----------+                                   |
    |                                                               |
    +-------------------------------------------------------------+
    
    Node Functions:
    - plan: Analyze task, create execution plan (LLM call)
    - generate: Generate code based on plan (LLM call)
    - verify: Check syntax with ast.parse()
    - correct: Generate error feedback for retry
    
    Loop Control:
    - Max iterations: state.max_iterations (default: 3)
    - Exit conditions: is_valid=True OR iteration >= max_iterations
    """


def get_graph_metadata() -> dict:
    """
    Get metadata about the graph for logging/monitoring.
    
    Returns:
        Dictionary with graph configuration
    """
    return {
        "name": "CodeGenerationGraph",
        "version": "0.2.0",
        "nodes": ["plan", "generate", "verify", "correct"],
        "entry_point": "plan",
        "conditional_edges": {
            "verify": ["end", "correct"]
        },
        "loop_edge": "correct -> generate",
        "default_max_iterations": 3
    }


# ========== TEST ==========
if __name__ == "__main__":
    print(visualize_graph())
    print("\nGraph Metadata:")
    for k, v in get_graph_metadata().items():
        print(f"  {k}: {v}")
