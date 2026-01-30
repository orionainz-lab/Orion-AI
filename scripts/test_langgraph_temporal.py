#!/usr/bin/env python
"""
VAN QA Test: LangGraph Inside Temporal Workflow

CRITICAL TEST: Validates that LangGraph reasoning loops can run
inside Temporal ACTIVITIES, with Temporal workflows orchestrating.

KEY INSIGHT: LangGraph must run in activities (not workflows directly)
because LangGraph imports non-deterministic libraries (requests, etc.)
that Temporal's sandbox restricts for workflow determinism.

ARCHITECTURE:
- Temporal Workflow: Orchestrates when to call LangGraph
- Temporal Activity: Executes LangGraph (non-deterministic OK here)
- This provides retry/durability at the activity level

This proves the Phase 2 architecture is feasible.
"""

import asyncio
import sys
from pathlib import Path
from datetime import timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker


# ==============================================================================
# TEMPORAL ACTIVITY: Execute LangGraph (LangGraph imports here, not at top level)
# ==============================================================================

@activity.defn
async def execute_langgraph_loop(input_text: str) -> dict:
    """
    Temporal activity that executes a LangGraph reasoning loop.
    
    KEY: LangGraph imports happen INSIDE the activity, not at module level.
    This avoids Temporal sandbox restrictions on workflow code.
    
    This demonstrates that LangGraph can run inside Temporal activities,
    which provides durability if the activity is retried.
    """
    # Import LangGraph inside the activity (not at top level)
    # This is the correct pattern for Temporal + LangGraph integration
    from typing import TypedDict
    from langgraph.graph import StateGraph, END
    
    # Define state and nodes locally
    class ReasoningState(TypedDict):
        input_text: str
        step: int
        result: str
        is_complete: bool
    
    def step_one(state: ReasoningState) -> ReasoningState:
        state["step"] = 1
        state["result"] = f"Step 1 processed: {state['input_text'][:20]}"
        return state
    
    def step_two(state: ReasoningState) -> ReasoningState:
        state["step"] = 2
        state["result"] = f"Step 2 completed"
        state["is_complete"] = True
        return state
    
    activity.logger.info(f"Executing LangGraph with input: {input_text[:30]}...")
    
    # Build LangGraph
    graph = StateGraph(ReasoningState)
    graph.add_node("step_one", step_one)
    graph.add_node("step_two", step_two)
    graph.set_entry_point("step_one")
    graph.add_edge("step_one", "step_two")
    graph.add_edge("step_two", END)
    compiled = graph.compile()
    
    # Execute
    initial_state = {
        "input_text": input_text,
        "step": 0,
        "result": "",
        "is_complete": False
    }
    final_state = compiled.invoke(initial_state)
    
    activity.logger.info(f"LangGraph completed at step {final_state['step']}")
    
    return {
        "input": input_text,
        "final_step": final_state["step"],
        "result": final_state["result"],
        "is_complete": final_state["is_complete"]
    }


# ==============================================================================
# TEMPORAL WORKFLOW: Orchestrates LangGraph Execution
# ==============================================================================

@workflow.defn
class LangGraphTestWorkflow:
    """
    Temporal workflow that orchestrates LangGraph execution.
    
    This proves Phase 2 architecture: LangGraph runs inside Temporal,
    gaining durability guarantees.
    """
    
    @workflow.run
    async def run(self, input_text: str) -> dict:
        workflow.logger.info(f"Workflow started with input: {input_text[:30]}...")
        
        # Execute LangGraph as a Temporal activity
        # This provides durability - if worker crashes, activity retries
        result = await workflow.execute_activity(
            execute_langgraph_loop,
            input_text,
            start_to_close_timeout=timedelta(seconds=60)
        )
        
        workflow.logger.info(f"LangGraph activity completed: {result['result']}")
        
        return {
            "workflow_id": workflow.info().workflow_id,
            "langgraph_result": result,
            "status": "completed"
        }


# ==============================================================================
# TEST EXECUTION
# ==============================================================================

async def run_test():
    """Run the LangGraph-Temporal integration test."""
    print("\n" + "=" * 60)
    print("LANGGRAPH-TEMPORAL INTEGRATION TEST")
    print("=" * 60)
    
    # Connect to Temporal
    print("\n[1] Connecting to Temporal Server...")
    try:
        client = await Client.connect("localhost:7233", namespace="default")
        print("    [OK] Connected to Temporal Server")
    except Exception as e:
        print(f"    [FAIL] Could not connect: {e}")
        print("    Make sure Temporal Server is running (docker-compose up -d)")
        return False
    
    # Create worker with LangGraph workflow and activity
    print("\n[2] Creating Temporal worker with LangGraph...")
    worker = Worker(
        client,
        task_queue="langgraph-test-queue",
        workflows=[LangGraphTestWorkflow],
        activities=[execute_langgraph_loop]
    )
    print("    [OK] Worker created with LangGraph workflow and activity")
    
    # Run worker and execute workflow
    print("\n[3] Starting worker and executing workflow...")
    
    async def execute_workflow():
        """Execute the workflow while worker runs."""
        # Wait for worker to start
        await asyncio.sleep(1)
        
        # Execute the workflow
        workflow_id = f"langgraph-temporal-test-{asyncio.get_event_loop().time()}"
        
        result = await client.execute_workflow(
            LangGraphTestWorkflow.run,
            "Test input for LangGraph reasoning loop validation",
            id=workflow_id,
            task_queue="langgraph-test-queue"
        )
        
        return result
    
    try:
        # Run worker and workflow concurrently
        worker_task = asyncio.create_task(worker.run())
        workflow_task = asyncio.create_task(execute_workflow())
        
        # Wait for workflow to complete (with timeout)
        result = await asyncio.wait_for(workflow_task, timeout=30)
        
        # Cancel worker
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
        
        print("    [OK] Workflow executed successfully!")
        print(f"\n    Results:")
        print(f"      Workflow ID: {result['workflow_id']}")
        print(f"      LangGraph Result: {result['langgraph_result']['result']}")
        print(f"      Final Step: {result['langgraph_result']['final_step']}")
        print(f"      Is Complete: {result['langgraph_result']['is_complete']}")
        print(f"      Status: {result['status']}")
        
        # Validate results
        assert result['status'] == "completed", "Workflow should be completed"
        assert result['langgraph_result']['is_complete'] == True, "LangGraph should be complete"
        assert result['langgraph_result']['final_step'] == 2, "Should reach step 2"
        
        return True
        
    except asyncio.TimeoutError:
        print("    [FAIL] Workflow timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"    [FAIL] Error: {e}")
        return False


async def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("VAN QA: LANGGRAPH-TEMPORAL INTEGRATION VALIDATION")
    print("=" * 60)
    print("\nThis test validates that LangGraph can run inside Temporal workflows,")
    print("which is CRITICAL for Phase 2 architecture.")
    
    success = await run_test()
    
    print("\n" + "=" * 60)
    print("VALIDATION RESULT")
    print("=" * 60)
    
    if success:
        print("\n[SUCCESS] LANGGRAPH-TEMPORAL INTEGRATION: VALIDATED")
        print("  - LangGraph graphs can execute inside Temporal activities")
        print("  - Temporal workflows can orchestrate LangGraph reasoning")
        print("  - Phase 2 architecture is FEASIBLE")
        print("\n  RECOMMENDATION: Proceed to PLAN mode")
    else:
        print("\n[FAIL] LANGGRAPH-TEMPORAL INTEGRATION: ISSUES DETECTED")
        print("  - Review error messages above")
        print("  - Ensure Temporal Server is running")
        print("  - Consider architectural fallback if integration fails")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
