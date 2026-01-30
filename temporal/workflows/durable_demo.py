"""
Durable Demo Workflow
Tests 24-hour sleep/resume capability (configurable for testing)

This workflow demonstrates Temporal's durability guarantees:
- Workflow can sleep for extended periods
- State persists across worker restarts
- Resumes execution from last checkpoint
"""

import asyncio
from datetime import timedelta
from temporalio import workflow

# Import activities
with workflow.unsafe.imports_passed_through():
    from temporal.activities.test_activities import process_step, log_event


@workflow.defn
class DurableDemoWorkflow:
    """
    Workflow that demonstrates durable execution with sleep/resume.
    
    Configurable sleep duration:
    - Default: 5 seconds (for fast testing)
    - Production: 24 hours (86400 seconds)
    
    Tests:
    - Long-running workflows
    - State persistence
    - Worker crash recovery
    """
    
    def __init__(self):
        self._status = "initialized"
        self._step_count = 0
    
    @workflow.run
    async def run(self, test_name: str, sleep_seconds: int = 5) -> dict:
        """
        Main workflow execution.
        
        Args:
            test_name: Identifier for this test run
            sleep_seconds: How long to sleep (default: 5s for testing)
        
        Returns:
            dict with execution details
        """
        self._status = "running"
        workflow.logger.info(
            f"Workflow started: {test_name}, sleep={sleep_seconds}s"
        )
        
        # Step 1: Pre-sleep activity
        self._step_count += 1
        pre_sleep_result = await workflow.execute_activity(
            process_step,
            args=[test_name, "pre-sleep", self._step_count],
            start_to_close_timeout=timedelta(seconds=30),
        )
        workflow.logger.info(f"Pre-sleep step: {pre_sleep_result}")
        
        # Step 2: Durable sleep (THE KEY TEST)
        # This is where workflow state is persisted
        # Worker can crash/restart during this sleep
        self._status = "sleeping"
        workflow.logger.info(f"Entering sleep for {sleep_seconds} seconds...")
        
        await asyncio.sleep(sleep_seconds)
        
        # Step 3: Post-sleep activity (proves recovery)
        self._status = "resumed"
        self._step_count += 1
        workflow.logger.info(f"Resumed after {sleep_seconds}s sleep")
        
        post_sleep_result = await workflow.execute_activity(
            process_step,
            args=[test_name, "post-sleep", self._step_count],
            start_to_close_timeout=timedelta(seconds=30),
        )
        workflow.logger.info(f"Post-sleep step: {post_sleep_result}")
        
        # Step 4: Final logging activity
        await workflow.execute_activity(
            log_event,
            args=[f"Workflow {test_name} completed successfully"],
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        self._status = "completed"
        
        return {
            "test_name": test_name,
            "sleep_seconds": sleep_seconds,
            "steps_executed": self._step_count,
            "final_status": self._status,
            "message": "Workflow completed - durability verified",
        }
    
    @workflow.query
    def get_status(self) -> dict:
        """Query current workflow state (non-blocking)"""
        return {
            "status": self._status,
            "step_count": self._step_count,
        }
