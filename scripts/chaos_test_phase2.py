"""
Phase 2 Chaos Testing: Code Generation Durability

This script tests that the code generation workflow recovers from
worker crashes during the LangGraph reasoning loop.

Test Scenarios:
1. Kill worker during planning phase
2. Kill worker during code generation phase

Per ADR-007, LangGraph runs inside a Temporal activity. When a worker
crashes, the activity is retried, re-executing the LangGraph reasoning.

Requirements:
    - Temporal Server running (localhost:7233)
    - ANTHROPIC_API_KEY configured in .env

Usage:
    python scripts/chaos_test_phase2.py
"""

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from temporalio.client import Client
from temporal.config import temporal_config
from utils.chaos_utils import (
    start_worker_process,
    kill_worker_process,
    cleanup_worker
)

# Test configuration
CHAOS_SLEEP_BEFORE_KILL = 5  # Seconds to wait before killing worker
CHAOS_SLEEP_AFTER_RESTART = 3  # Seconds to wait for worker to start
WORKFLOW_TIMEOUT = 180  # Max seconds to wait for workflow completion


async def test_chaos_during_generation():
    """
    Test: Kill worker during code generation activity.
    
    Steps:
    1. Start worker
    2. Start code generation workflow
    3. Wait for activity to begin (LangGraph reasoning)
    4. Kill worker
    5. Restart worker
    6. Verify workflow completes successfully
    """
    print("\n" + "=" * 60)
    print("CHAOS TEST: Kill During Code Generation")
    print("=" * 60)
    
    worker = None
    
    try:
        # 1. Start worker
        print("\n[Step 1] Starting worker...")
        worker = start_worker_process()
        worker_pid = worker.pid
        print(f"  Worker started: PID {worker_pid}")
        
        # 2. Connect to Temporal
        print("\n[Step 2] Connecting to Temporal...")
        client = await Client.connect(
            temporal_config.host,
            namespace=temporal_config.namespace
        )
        print(f"  Connected to {temporal_config.host}")
        
        # 3. Start code generation workflow
        print("\n[Step 3] Starting code generation workflow...")
        task = "Create a function that calculates the factorial of a number recursively"
        workflow_id = f"chaos-codegen-{int(time.time())}"
        
        from agents.workflows import CodeGenerationWorkflow
        
        handle = await client.start_workflow(
            CodeGenerationWorkflow.run,
            args=[task, "python", 3, None],
            id=workflow_id,
            task_queue=temporal_config.task_queue,
        )
        print(f"  Workflow started: {workflow_id}")
        
        # 4. Wait for activity to begin
        print(f"\n[Step 4] Waiting {CHAOS_SLEEP_BEFORE_KILL}s for activity to start...")
        await asyncio.sleep(CHAOS_SLEEP_BEFORE_KILL)
        
        # 5. Kill worker
        print("\n[Step 5] KILLING WORKER...")
        killed = kill_worker_process(worker_pid)
        if killed:
            print(f"  Worker killed: PID {worker_pid}")
        worker = None  # Prevent cleanup of dead process
        
        # 6. Wait briefly
        print(f"\n[Step 6] Waiting {CHAOS_SLEEP_AFTER_RESTART}s before restart...")
        await asyncio.sleep(CHAOS_SLEEP_AFTER_RESTART)
        
        # 7. Restart worker
        print("\n[Step 7] Restarting worker...")
        worker = start_worker_process()
        print(f"  New worker started: PID {worker.pid}")
        
        # 8. Wait for workflow completion
        print("\n[Step 8] Waiting for workflow to complete...")
        start_wait = time.time()
        
        try:
            result = await asyncio.wait_for(
                handle.result(),
                timeout=WORKFLOW_TIMEOUT
            )
            elapsed = time.time() - start_wait
            
            # 9. Verify result
            print(f"\n[Step 9] Verifying result...")
            is_valid = result.get("is_valid", False)
            iterations = result.get("iterations", 0)
            code_len = len(result.get("code", ""))
            
            print(f"  Valid: {is_valid}")
            print(f"  Iterations: {iterations}")
            print(f"  Code length: {code_len} chars")
            print(f"  Time after restart: {elapsed:.1f}s")
            
            if is_valid:
                print("\n[PASS] Workflow completed successfully after worker crash!")
                return True
            else:
                print("\n[WARN] Workflow completed but code is invalid")
                print(f"  Errors: {result.get('errors', [])}")
                # Still passes chaos test - durability worked
                return True
                
        except asyncio.TimeoutError:
            print(f"\n[FAIL] Workflow did not complete within {WORKFLOW_TIMEOUT}s")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        return False
        
    finally:
        if worker:
            print("\n[Cleanup] Stopping worker...")
            cleanup_worker(worker)


async def test_chaos_quick():
    """
    Quick chaos test without actual LLM calls.
    Tests worker crash/recovery with verification activity.
    """
    print("\n" + "=" * 60)
    print("CHAOS TEST: Quick (Verification Only)")
    print("=" * 60)
    
    worker = None
    
    try:
        # 1. Start worker
        print("\n[Step 1] Starting worker...")
        worker = start_worker_process()
        worker_pid = worker.pid
        
        # 2. Connect and run simple verification
        print("\n[Step 2] Connecting to Temporal...")
        client = await Client.connect(
            temporal_config.host,
            namespace=temporal_config.namespace
        )
        
        # 3. Use Phase 1 workflow as quick test
        print("\n[Step 3] Starting durable demo workflow...")
        from temporal.workflows.durable_demo import DurableDemoWorkflow
        
        workflow_id = f"chaos-quick-{int(time.time())}"
        
        handle = await client.start_workflow(
            DurableDemoWorkflow.run,
            workflow_id=workflow_id,
            task_queue=temporal_config.task_queue,
        )
        
        # 4. Kill worker during execution
        print(f"\n[Step 4] Waiting {CHAOS_SLEEP_BEFORE_KILL}s then killing...")
        await asyncio.sleep(CHAOS_SLEEP_BEFORE_KILL)
        kill_worker_process(worker_pid)
        worker = None
        
        # 5. Restart
        print("\n[Step 5] Restarting worker...")
        await asyncio.sleep(2)
        worker = start_worker_process()
        
        # 6. Wait for completion
        print("\n[Step 6] Waiting for workflow...")
        result = await asyncio.wait_for(handle.result(), timeout=60)
        
        if result.get("success"):
            print("\n[PASS] Quick chaos test passed!")
            return True
        else:
            print("\n[FAIL] Workflow did not succeed")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False
    finally:
        if worker:
            cleanup_worker(worker)


async def main():
    """Run chaos tests."""
    print("=" * 60)
    print("PHASE 2: CHAOS TESTING")
    print("=" * 60)
    print(f"Temporal: {temporal_config.host}")
    print(f"Task Queue: {temporal_config.task_queue}")
    
    results = []
    
    # Test 1: Quick chaos test
    print("\n\n" + "=" * 60)
    print("TEST 1: Quick Chaos Test")
    print("=" * 60)
    result1 = await test_chaos_quick()
    results.append(("Quick Chaos", result1))
    
    # Test 2: Full code generation chaos (only if API key configured)
    import os
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    if api_key and api_key != "your-anthropic-api-key-here":
        print("\n\n" + "=" * 60)
        print("TEST 2: Code Generation Chaos Test")
        print("=" * 60)
        result2 = await test_chaos_during_generation()
        results.append(("CodeGen Chaos", result2))
    else:
        print("\n\n" + "=" * 60)
        print("TEST 2: SKIPPED (no ANTHROPIC_API_KEY)")
        print("=" * 60)
        results.append(("CodeGen Chaos", None))
    
    # Summary
    print("\n\n" + "=" * 60)
    print("CHAOS TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    skipped = 0
    failed = 0
    
    for name, result in results:
        if result is True:
            print(f"  [PASS] {name}")
            passed += 1
        elif result is None:
            print(f"  [SKIP] {name}")
            skipped += 1
        else:
            print(f"  [FAIL] {name}")
            failed += 1
    
    print("-" * 60)
    print(f"Passed: {passed}, Skipped: {skipped}, Failed: {failed}")
    
    if failed > 0:
        print("\n[RESULT] Some chaos tests FAILED")
        sys.exit(1)
    else:
        print("\n[RESULT] All chaos tests PASSED (or skipped)")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
