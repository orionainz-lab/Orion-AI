#!/usr/bin/env python3
"""
Chaos Testing Framework
Tests workflow durability by killing worker mid-execution
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent))

from temporalio.client import Client
from temporal.config import temporal_config
from temporal.workflows.durable_demo import DurableDemoWorkflow
from utils.chaos_utils import (
    start_worker_process,
    kill_worker_process,
    cleanup_worker,
)


class ChaosTest:
    """Chaos testing orchestrator"""
    
    def __init__(self):
        self.client = None
        self.test_results = []
    
    async def connect(self):
        """Connect to Temporal Server"""
        self.client = await Client.connect(
            temporal_config.host, namespace=temporal_config.namespace
        )
        print(f"Connected to Temporal: {temporal_config.host}")
    
    async def test_scenario_1_kill_during_sleep(self):
        """
        Chaos Test 1: Kill worker during workflow sleep
        
        Steps:
        1. Start workflow with 10s sleep
        2. Wait 2s (workflow enters sleep)
        3. Kill worker
        4. Restart worker
        5. Verify workflow completes
        """
        print("\n" + "=" * 60)
        print("CHAOS TEST 1: Kill Worker During Sleep")
        print("=" * 60)
        
        # Start worker
        worker = start_worker_process()
        await asyncio.sleep(2)
        
        # Start workflow
        workflow_id = f"chaos-sleep-{uuid4()}"
        print(f"\nStarting workflow: {workflow_id}")
        
        handle = await self.client.start_workflow(
            DurableDemoWorkflow.run,
            args=["chaos_sleep_test", 10],
            id=workflow_id,
            task_queue=temporal_config.task_queue,
        )
        print(f"  Workflow started: {handle.id}")
        
        # Wait for workflow to enter sleep state
        print(f"  Waiting 3s for workflow to checkpoint...")
        await asyncio.sleep(3)
        
        # CHAOS: Kill worker mid-sleep
        kill_worker_process(worker.pid)
        await asyncio.sleep(1)
        
        # Restart worker
        print(f"\nRestarting worker...")
        worker = start_worker_process()
        
        # Wait for workflow to complete
        print(f"  Waiting for workflow to resume and complete...")
        result = await handle.result()
        
        print(f"\n  SUCCESS: Workflow completed after crash!")
        print(f"  Result: {result}")
        
        # Cleanup
        cleanup_worker(worker)
        
        self.test_results.append(("Scenario 1: Kill During Sleep", True, result))
        return True
    
    async def test_scenario_2_kill_during_activity(self):
        """
        Chaos Test 2: Kill worker during long activity
        
        Tests activity retry after worker crash.
        """
        print("\n" + "=" * 60)
        print("CHAOS TEST 2: Kill Worker During Activity")
        print("=" * 60)
        # Start worker
        worker = start_worker_process()
        await asyncio.sleep(2)
        
        # Start workflow
        workflow_id = f"chaos-activity-{uuid4()}"
        print(f"\nStarting workflow: {workflow_id}")
        
        handle = await self.client.start_workflow(
            DurableDemoWorkflow.run,
            args=["chaos_activity_test", 8],
            id=workflow_id,
            task_queue=temporal_config.task_queue,
        )
        
        # Wait briefly
        await asyncio.sleep(2)
        
        # CHAOS: Kill worker
        kill_worker_process(worker.pid)
        await asyncio.sleep(1)
        
        # Restart worker
        print(f"\nRestarting worker...")
        worker = start_worker_process()
        
        # Wait for completion
        result = await handle.result()
        
        print(f"\n  SUCCESS: Workflow recovered and completed!")
        print(f"  Result: {result}")
        
        # Cleanup
        cleanup_worker(worker)
        
        self.test_results.append(("Scenario 2: Kill During Activity", True, result))
        return True
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("CHAOS TEST SUMMARY")
        print("=" * 60)
        
        for test_name, passed, result in self.test_results:
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {test_name}")
        
        total = len(self.test_results)
        passed = sum(1 for _, p, _ in self.test_results if p)
        
        print(f"\nResults: {passed}/{total} passed ({100*passed//total}%)")
        
        if passed == total:
            print("\nALL CHAOS TESTS PASSED - Durability Verified!")
            return True
        else:
            print("\nSOME TESTS FAILED - Review logs")
            return False


async def main():
    """Run all chaos tests"""
    tester = ChaosTest()
    
    try:
        await tester.connect()
        
        # Run test scenarios
        await tester.test_scenario_1_kill_during_sleep()
        await asyncio.sleep(2)
        
        await tester.test_scenario_2_kill_during_activity()
        
        # Summary
        success = tester.print_summary()
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\nChaos test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
