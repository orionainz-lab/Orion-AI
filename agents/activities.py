"""
Temporal Activity Definitions for Phase 2

This module defines Temporal activities for code generation.
The key activity is execute_code_generation, which runs the
LangGraph reasoning loop inside an activity context.

Per ADR-007, LangGraph is imported INSIDE activities to avoid
Temporal's workflow sandbox restrictions on non-deterministic code.

Usage:
    # Register in worker.py:
    from agents.activities import execute_code_generation
    
    worker = Worker(
        client,
        task_queue="default",
        workflows=[CodeGenerationWorkflow],
        activities=[execute_code_generation]
    )
"""

import time
import logging
from typing import Optional

from temporalio import activity

logger = logging.getLogger(__name__)


@activity.defn
async def execute_code_generation(
    task: str,
    language: str = "python",
    max_iterations: int = 3,
    context: Optional[str] = None
) -> dict:
    """
    Execute LangGraph code generation reasoning loop.
    
    CRITICAL: LangGraph imports happen INSIDE this activity to avoid
    Temporal's workflow sandbox restrictions (per ADR-007).
    
    This activity:
    1. Builds the LangGraph StateGraph
    2. Initializes state from parameters
    3. Invokes the graph (Plan -> Generate -> Verify -> Correct loop)
    4. Returns the final state as result
    
    Args:
        task: Code generation task description
        language: Target programming language
        max_iterations: Maximum correction iterations
        context: Optional additional context
        
    Returns:
        Dictionary with:
            - code: Generated code (may be invalid if max iterations)
            - is_valid: Whether code passed AST verification
            - iterations: Number of iterations taken
            - errors: List of errors (empty if valid)
            - warnings: List of warnings
            - model_used: LLM model used
            - reasoning_time_ms: Total execution time
    """
    activity.logger.info(
        f"Starting code generation activity: {task[:50]}..."
    )
    start_time = time.time()
    
    # ========== IMPORT LANGGRAPH INSIDE ACTIVITY (ADR-007) ==========
    # This is the critical pattern: LangGraph and its dependencies
    # (requests, urllib3, etc.) are imported here, not at module level.
    # Activities can safely run non-deterministic code.
    
    from agents.graph_builder import build_code_generation_graph
    from agents.state import create_initial_state
    
    # ========== BUILD GRAPH ==========
    activity.heartbeat("Building LangGraph...")
    graph = build_code_generation_graph()
    
    # ========== INITIALIZE STATE ==========
    initial_state = create_initial_state(
        task=task,
        language=language,
        context=context,
        max_iterations=max_iterations
    )
    
    activity.logger.info(
        f"Graph built, starting reasoning loop "
        f"(max {max_iterations} iterations)"
    )
    
    # ========== EXECUTE GRAPH ==========
    activity.heartbeat("Executing reasoning loop...")
    
    try:
        # Invoke the graph - this runs the full reasoning loop
        final_state = graph.invoke(initial_state)
        
        # Calculate timing
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        activity.logger.info(
            f"Reasoning loop complete: "
            f"valid={final_state.get('is_valid', False)}, "
            f"iterations={final_state.get('iteration', 0)}, "
            f"time={elapsed_ms}ms"
        )
        
        # ========== RETURN RESULT ==========
        return {
            "code": final_state.get("code", ""),
            "is_valid": final_state.get("is_valid", False),
            "iterations": final_state.get("iteration", 0),
            "errors": final_state.get("errors", []),
            "warnings": final_state.get("warnings", []),
            "model_used": final_state.get("model_used", "unknown"),
            "reasoning_time_ms": elapsed_ms,
            "plan": final_state.get("plan", ""),
            "feedback": final_state.get("feedback", "")
        }
        
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        activity.logger.error(f"Reasoning loop failed: {e}")
        
        return {
            "code": "",
            "is_valid": False,
            "iterations": 0,
            "errors": [{"line": 0, "message": f"Activity error: {str(e)}"}],
            "warnings": [],
            "model_used": "error",
            "reasoning_time_ms": elapsed_ms,
            "plan": "",
            "feedback": ""
        }


@activity.defn
async def verify_code_syntax(code: str) -> dict:
    """
    Standalone activity for code verification.
    
    This activity can be called independently to verify code
    without running the full reasoning loop.
    
    Args:
        code: Python code to verify
        
    Returns:
        Verification result dictionary
    """
    activity.logger.info(f"Verifying code ({len(code)} chars)")
    
    from verification.ast_verifier import verify_and_feedback
    
    result = verify_and_feedback(code)
    
    if result["is_valid"]:
        activity.logger.info("Code verification PASSED")
    else:
        activity.logger.warning(
            f"Code verification FAILED: {len(result['errors'])} errors"
        )
    
    return result


# ========== ACTIVITY REGISTRY ==========
# For easy import in worker.py

PHASE2_ACTIVITIES = [
    execute_code_generation,
    verify_code_syntax
]
