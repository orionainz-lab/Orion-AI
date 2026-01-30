#!/usr/bin/env python3
"""
Test Temporal Signal API Integration
Purpose: Create a test workflow and verify signal sending works
"""

import asyncio
import os
from datetime import timedelta
from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker

# Test Workflow Definition
@workflow.defn
class ApprovalTestWorkflow:
    def __init__(self):
        self.status = "pending"
        self.approved = False
        self.rejected = False
    
    @workflow.run
    async def run(self, proposal_id: str) -> dict:
        print(f"[Workflow] Started for proposal: {proposal_id}")
        self.status = "waiting_for_approval"
        
        # Wait for either approve or reject signal (with timeout)
        try:
            await workflow.wait_condition(
                lambda: self.approved or self.rejected,
                timeout=timedelta(seconds=300)  # 5 minute timeout
            )
            
            if self.approved:
                self.status = "approved"
                print(f"[Workflow] Proposal {proposal_id} APPROVED")
                return {"status": "approved", "proposal_id": proposal_id}
            elif self.rejected:
                self.status = "rejected"
                print(f"[Workflow] Proposal {proposal_id} REJECTED")
                return {"status": "rejected", "proposal_id": proposal_id}
        except asyncio.TimeoutError:
            self.status = "timeout"
            print(f"[Workflow] Proposal {proposal_id} TIMEOUT")
            return {"status": "timeout", "proposal_id": proposal_id}
    
    @workflow.signal
    async def approve_signal(self, data: dict):
        print(f"[Workflow] Received APPROVE signal: {data}")
        self.approved = True
    
    @workflow.signal
    async def reject_signal(self, data: dict):
        print(f"[Workflow] Received REJECT signal: {data}")
        self.rejected = True

# Test Activity
@activity.defn
async def log_activity(message: str) -> str:
    print(f"[Activity] {message}")
    return f"Logged: {message}"

async def main():
    print("=" * 70)
    print("TEMPORAL SIGNAL API TEST")
    print("=" * 70)
    
    # Connect to Temporal
    temporal_address = os.getenv('TEMPORAL_ADDRESS', 'localhost:7233')
    print(f"\n[INFO] Connecting to Temporal: {temporal_address}")
    
    try:
        client = await Client.connect(temporal_address)
        print("[SUCCESS] Connected to Temporal")
    except Exception as e:
        print(f"[ERROR] Failed to connect: {str(e)}")
        print("\n[HINT] Make sure Temporal is running:")
        print("  docker-compose up -d")
        return
    
    # Start worker in background
    print("\n[INFO] Starting Temporal worker...")
    task_queue = "approval-test-queue"
    
    async with Worker(
        client,
        task_queue=task_queue,
        workflows=[ApprovalTestWorkflow],
        activities=[log_activity],
    ):
        # Start test workflow
        print(f"\n[TEST] Starting approval workflow...")
        workflow_id = "approval-test-workflow-001"
        
        try:
            handle = await client.start_workflow(
                ApprovalTestWorkflow.run,
                "test-proposal-001",
                id=workflow_id,
                task_queue=task_queue,
            )
            print(f"[SUCCESS] Workflow started: {workflow_id}")
            print(f"[INFO] Workflow URL: http://localhost:8080/workflows/{workflow_id}")
        except Exception as e:
            print(f"[ERROR] Failed to start workflow: {str(e)}")
            return
        
        # Test workflow query
        print(f"\n[TEST] Querying workflow status...")
        try:
            # Get workflow handle
            handle = client.get_workflow_handle(workflow_id)
            print(f"[SUCCESS] Retrieved workflow handle")
        except Exception as e:
            print(f"[ERROR] Failed to query workflow: {str(e)}")
        
        print("\n" + "=" * 70)
        print("TEMPORAL WORKFLOW READY FOR SIGNAL TESTING")
        print("=" * 70)
        print(f"\nWorkflow ID: {workflow_id}")
        print(f"Task Queue: {task_queue}")
        print(f"Status: Waiting for approval/rejection")
        print("\n[NEXT STEP] Test the signal API:")
        print("  1. Start frontend: cd frontend && npm run dev")
        print("  2. Open: http://localhost:3000/matrix")
        print("  3. Click Approve or Reject on a pending proposal")
        print("  4. Watch this console for signal reception")
        print("\n[ALTERNATIVE] Test via curl:")
        print(f"""
  curl -X POST http://localhost:3000/api/temporal/signal \\
    -H "Content-Type: application/json" \\
    -d '{{
      "workflowId": "{workflow_id}",
      "signalName": "approve_signal",
      "signalArgs": {{"proposalId": "test-proposal-001"}}
    }}'
        """)
        
        # Wait for workflow to complete or timeout
        print("\n[INFO] Waiting for workflow completion (5 min timeout)...")
        try:
            result = await handle.result()
            print(f"\n[SUCCESS] Workflow completed: {result}")
        except asyncio.TimeoutError:
            print("\n[TIMEOUT] Workflow did not complete within timeout")
        except Exception as e:
            print(f"\n[ERROR] Workflow failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
