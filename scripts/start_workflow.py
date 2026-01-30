#!/usr/bin/env python3
"""
Start Workflow - Manual Test Script
Starts a workflow execution for testing purposes
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from temporalio.client import Client
from temporal.config import temporal_config
from temporal.workflows.durable_demo import DurableDemoWorkflow
from temporal.workflows.approval_workflow import ApprovalWorkflow


async def start_durable_demo(sleep_seconds: int = 5):
    """Start DurableDemoWorkflow"""
    client = await Client.connect(
        temporal_config.host, namespace=temporal_config.namespace
    )
    
    workflow_id = f"durable-demo-{uuid4()}"
    
    print(f"Starting DurableDemoWorkflow...")
    print(f"  Workflow ID: {workflow_id}")
    print(f"  Sleep duration: {sleep_seconds}s")
    
    handle = await client.start_workflow(
        DurableDemoWorkflow.run,
        args=["manual_test", sleep_seconds],
        id=workflow_id,
        task_queue=temporal_config.task_queue,
    )
    
    print(f"  Started: {handle.id}")
    print(f"  Monitor: http://localhost:8080/namespaces/default/workflows/{workflow_id}")
    print(f"\nWaiting for result...")
    
    result = await handle.result()
    print(f"\nWorkflow completed!")
    print(f"  Result: {result}")


async def start_approval_workflow(timeout: int = None):
    """Start ApprovalWorkflow"""
    client = await Client.connect(
        temporal_config.host, namespace=temporal_config.namespace
    )
    
    workflow_id = f"approval-{uuid4()}"
    
    print(f"Starting ApprovalWorkflow...")
    print(f"  Workflow ID: {workflow_id}")
    print(f"  Timeout: {timeout}s" if timeout else "  Timeout: None (wait forever)")
    
    handle = await client.start_workflow(
        ApprovalWorkflow.run,
        args=["REQ-001", "test_user", timeout],
        id=workflow_id,
        task_queue=temporal_config.task_queue,
    )
    
    print(f"  Started: {handle.id}")
    print(f"  Monitor: http://localhost:8080/namespaces/default/workflows/{workflow_id}")
    print(f"\nWorkflow is waiting for approval signal...")
    print(f"Send signal: python scripts/send_signal.py {workflow_id} approve")


async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/start_workflow.py durable [sleep_seconds]")
        print("  python scripts/start_workflow.py approval [timeout_seconds]")
        sys.exit(1)
    
    workflow_type = sys.argv[1].lower()
    
    if workflow_type == "durable":
        sleep_seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        await start_durable_demo(sleep_seconds)
    elif workflow_type == "approval":
        timeout = int(sys.argv[2]) if len(sys.argv) > 2 else None
        await start_approval_workflow(timeout)
    else:
        print(f"Unknown workflow type: {workflow_type}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
