#!/usr/bin/env python3
"""
Phase 1 Integration Tests
Comprehensive test suite for Temporal infrastructure

Tests:
1. Worker connection
2. Simple workflow execution
3. Signal handling
4. Workflow state persistence
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent))

from temporalio.client import Client, WorkflowExecutionStatus
from temporal.config import temporal_config
from temporal.workflows.durable_demo import DurableDemoWorkflow
from temporal.workflows.approval_workflow import ApprovalWorkflow


class Phase1Tests:
    """Integration test suite for Phase 1"""
    
    def __init__(self):
        self.client = None
        self.passed = 0
        self.failed = 0
    
    async def setup(self):
        """Connect to Temporal"""
        self.client = await Client.connect(
            temporal_config.host, namespace=temporal_config.namespace
        )
        print(f"Connected to Temporal: {temporal_config.host}\n")
    
    async def test_simple_workflow(self):
        """Test 1: Simple workflow execution"""
        print("[TEST 1] Simple Workflow Execution")
        
        try:
            result = await self.client.execute_workflow(
                DurableDemoWorkflow.run,
                args=["test_simple", 1],
                id=f"test-simple-{uuid4()}",
                task_queue=temporal_config.task_queue,
            )
            
            assert result["final_status"] == "completed"
            assert result["steps_executed"] == 2
            
            print(f"  PASS: Workflow executed successfully")
            print(f"  Result: {result}")
            self.passed += 1
            
        except Exception as e:
            print(f"  FAIL: {e}")
            self.failed += 1
    
    async def test_workflow_with_sleep(self):
        """Test 2: Workflow with sleep (durability)"""
        print("\n[TEST 2] Workflow with Sleep (5s)")
        
        try:
            handle = await self.client.start_workflow(
                DurableDemoWorkflow.run,
                args=["test_sleep", 5],
                id=f"test-sleep-{uuid4()}",
                task_queue=temporal_config.task_queue,
            )
            
            print(f"  Started: {handle.id}")
            print(f"  Waiting 2s...")
            await asyncio.sleep(2)
            
            # Check it's still running
            desc = await handle.describe()
            assert desc.status == WorkflowExecutionStatus.RUNNING
            print(f"  Status during sleep: RUNNING (good!)")
            
            # Wait for completion
            result = await handle.result()
            assert result["final_status"] == "completed"
            
            print(f"  PASS: Workflow completed after sleep")
            self.passed += 1
            
        except Exception as e:
            print(f"  FAIL: {e}")
            self.failed += 1
    
    async def test_signal_handling(self):
        """Test 3: Signal handling (human-in-the-loop)"""
        print("\n[TEST 3] Signal Handling (Approval Workflow)")
        
        try:
            workflow_id = f"test-signal-{uuid4()}"
            
            handle = await self.client.start_workflow(
                ApprovalWorkflow.run,
                args=["REQ-TEST", "test_user", 30],
                id=workflow_id,
                task_queue=temporal_config.task_queue,
            )
            
            print(f"  Started: {handle.id}")
            print(f"  Waiting 1s before sending signal...")
            await asyncio.sleep(1)
            
            # Send approval signal
            await handle.signal(
                ApprovalWorkflow.approve, "tester", "Automated test"
            )
            print(f"  Approval signal sent")
            
            # Wait for completion
            result = await handle.result()
            assert result["approved"] is True
            assert result["approver"] == "tester"
            
            print(f"  PASS: Signal handled correctly")
            print(f"  Result: {result}")
            self.passed += 1
            
        except Exception as e:
            print(f"  FAIL: {e}")
            self.failed += 1
    
    async def test_workflow_query(self):
        """Test 4: Workflow query (read state)"""
        print("\n[TEST 4] Workflow Query")
        
        try:
            handle = await self.client.start_workflow(
                DurableDemoWorkflow.run,
                args=["test_query", 3],
                id=f"test-query-{uuid4()}",
                task_queue=temporal_config.task_queue,
            )
            
            # Query workflow state mid-execution
            await asyncio.sleep(1)
            status = await handle.query(DurableDemoWorkflow.get_status)
            
            print(f"  Queried status: {status}")
            assert "status" in status
            
            # Wait for completion
            await handle.result()
            
            print(f"  PASS: Query functionality working")
            self.passed += 1
            
        except Exception as e:
            print(f"  FAIL: {e}")
            self.failed += 1
    
    def print_summary(self):
        """Print test results summary"""
        total = self.passed + self.failed
        pass_rate = (self.passed * 100 // total) if total > 0 else 0
        
        print("\n" + "=" * 60)
        print("PHASE 1 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"  Total Tests: {total}")
        print(f"  Passed: {self.passed}")
        print(f"  Failed: {self.failed}")
        print(f"  Pass Rate: {pass_rate}%")
        print("=" * 60)
        
        if self.failed == 0:
            print("\nALL TESTS PASSED!")
            return True
        else:
            print(f"\n{self.failed} TEST(S) FAILED")
            return False


async def main():
    """Run all integration tests"""
    print("=" * 60)
    print("PHASE 1 INTEGRATION TESTS")
    print("=" * 60)
    print("NOTE: Worker must be running in separate terminal")
    print("Start with: python temporal/workers/worker.py")
    print("=" * 60)
    
    tests = Phase1Tests()
    
    try:
        await tests.setup()
        
        # Run all tests
        await tests.test_simple_workflow()
        await tests.test_workflow_with_sleep()
        await tests.test_signal_handling()
        await tests.test_workflow_query()
        
        # Summary
        success = tests.print_summary()
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\nTest suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
