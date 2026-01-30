#!/usr/bin/env python3
"""
Send Signal to Workflow
Manual tool for sending signals to running workflows
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from temporalio.client import Client
from temporal.config import temporal_config
from temporal.workflows.approval_workflow import ApprovalWorkflow


async def send_approval_signal(
    workflow_id: str, approver: str = "manual_tester", reason: str = None
):
    """Send approval signal to workflow"""
    client = await Client.connect(
        temporal_config.host, namespace=temporal_config.namespace
    )
    
    handle = client.get_workflow_handle(workflow_id)
    
    print(f"Sending approval signal to workflow: {workflow_id}")
    print(f"  Approver: {approver}")
    print(f"  Reason: {reason or 'Manual approval'}")
    
    # Signal takes workflow method name and single argument (dict)
    await handle.signal("approve", {"approver": approver, "reason": reason or "Manual approval"})
    
    print(f"  Signal sent successfully!")


async def send_rejection_signal(
    workflow_id: str, approver: str = "manual_tester", reason: str = None
):
    """Send rejection signal to workflow"""
    client = await Client.connect(
        temporal_config.host, namespace=temporal_config.namespace
    )
    
    handle = client.get_workflow_handle(workflow_id)
    
    print(f"Sending rejection signal to workflow: {workflow_id}")
    print(f"  Approver: {approver}")
    print(f"  Reason: {reason or 'Manual rejection'}")
    
    # Signal takes workflow method name and single argument (dict)
    await handle.signal("reject", {"approver": approver, "reason": reason or "Manual rejection"})
    
    print(f"  Signal sent successfully!")


async def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python scripts/send_signal.py <workflow_id> approve [reason]")
        print("  python scripts/send_signal.py <workflow_id> reject [reason]")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    signal_type = sys.argv[2].lower()
    reason = sys.argv[3] if len(sys.argv) > 3 else None
    
    if signal_type == "approve":
        await send_approval_signal(workflow_id, reason=reason)
    elif signal_type == "reject":
        await send_rejection_signal(workflow_id, reason=reason)
    else:
        print(f"Unknown signal type: {signal_type}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
