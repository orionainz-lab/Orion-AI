"""
Temporal Workflow Definitions for Phase 2

This module defines Temporal workflows that orchestrate code generation.
The workflow calls activities which execute the LangGraph reasoning loop.

Per ADR-007, LangGraph is imported inside activities (not workflows)
to avoid Temporal's workflow sandbox restrictions.

Usage:
    # Register in worker.py:
    from agents.workflows import CodeGenerationWorkflow
    
    worker = Worker(
        client,
        task_queue="default",
        workflows=[CodeGenerationWorkflow],
        activities=[execute_code_generation]
    )
"""

from datetime import timedelta
from temporalio import workflow
from typing import Optional

# Import activities for type hints only (not execution)
with workflow.unsafe.imports_passed_through():
    from agents.activities import execute_code_generation


@workflow.defn
class CodeGenerationWorkflow:
    """
    Temporal workflow that orchestrates AI code generation.
    
    This workflow:
    1. Receives a task description
    2. Calls activity to execute LangGraph reasoning
    3. Returns generated code (valid or partial)
    
    The LangGraph loop (Plan -> Generate -> Verify -> Correct)
    runs inside the activity, not the workflow, per ADR-007.
    """
    
    def __init__(self):
        self._result = None
        self._completed = False
    
    @workflow.run
    async def run(
        self,
        task: str,
        language: str = "python",
        max_iterations: int = 3,
        context: Optional[str] = None
    ) -> dict:
        """
        Execute code generation workflow.
        
        Args:
            task: Code generation task description
            language: Target language (default: python)
            max_iterations: Max correction iterations (default: 3)
            context: Optional additional context
            
        Returns:
            Dictionary with:
                - workflow_id: This workflow's ID
                - task: Original task
                - code: Generated code
                - is_valid: Whether code passed verification
                - iterations: Number of iterations taken
                - errors: List of errors (if any)
                - model_used: LLM model used
                - reasoning_time_ms: Total reasoning time
        """
        workflow.logger.info(
            f"CodeGenerationWorkflow starting: {task[:50]}..."
        )
        
        # Execute LangGraph reasoning as activity
        # Activity handles retries, heartbeats, and sandbox-safe imports
        result = await workflow.execute_activity(
            execute_code_generation,
            args=[task, language, max_iterations, context],
            start_to_close_timeout=timedelta(seconds=120),
            heartbeat_timeout=timedelta(seconds=30)
        )
        
        # Store result for query
        self._result = result
        self._completed = True
        
        # Log outcome
        if result.get("is_valid"):
            workflow.logger.info(
                f"CodeGenerationWorkflow SUCCESS: "
                f"valid code in {result.get('iterations', 0)} iterations"
            )
        else:
            workflow.logger.warning(
                f"CodeGenerationWorkflow PARTIAL: "
                f"invalid code after {result.get('iterations', 0)} iterations"
            )
        
        # Return enriched result
        return {
            "workflow_id": workflow.info().workflow_id,
            "task": task,
            "language": language,
            "code": result.get("code", ""),
            "is_valid": result.get("is_valid", False),
            "iterations": result.get("iterations", 0),
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", []),
            "model_used": result.get("model_used", "unknown"),
            "reasoning_time_ms": result.get("reasoning_time_ms", 0)
        }
    
    @workflow.query
    def get_status(self) -> dict:
        """Query current workflow status."""
        return {
            "completed": self._completed,
            "has_result": self._result is not None,
            "is_valid": self._result.get("is_valid") if self._result else None,
            "iterations": self._result.get("iterations") if self._result else 0
        }
    
    @workflow.query
    def get_result(self) -> Optional[dict]:
        """Query workflow result (after completion)."""
        return self._result
