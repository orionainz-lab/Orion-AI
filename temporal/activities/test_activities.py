"""
Test Activities for Phase 1
Idempotent operations for testing workflow durability

Activities can be retried and must be idempotent.
"""

import asyncio
import logging
from datetime import datetime
from temporalio import activity

logger = logging.getLogger(__name__)


@activity.defn
async def process_step(
    test_name: str, step_name: str, step_number: int
) -> str:
    """
    Process a workflow step (used in durable_demo).
    
    Idempotent: Safe to retry multiple times.
    
    Args:
        test_name: Test identifier
        step_name: Name of this step
        step_number: Step sequence number
    
    Returns:
        Confirmation message
    """
    activity.logger.info(
        f"Processing step {step_number}: {step_name} for test {test_name}"
    )
    
    # Simulate some processing
    await asyncio.sleep(0.5)
    
    timestamp = datetime.utcnow().isoformat()
    result = f"Step {step_number} ({step_name}) completed at {timestamp}"
    
    activity.logger.info(result)
    return result


@activity.defn
async def log_event(message: str) -> None:
    """
    Log an event (idempotent).
    
    Args:
        message: Event message to log
    """
    activity.logger.info(f"EVENT: {message}")
    
    # In production, this would write to database/logging service
    # For now, just log to stdout
    print(f"[{datetime.utcnow().isoformat()}] {message}")


@activity.defn
async def process_request(request_id: str, requester: str) -> dict:
    """
    Process an approval request (used in approval_workflow).
    
    Idempotent: Can be retried safely.
    
    Args:
        request_id: Request identifier
        requester: Who made the request
    
    Returns:
        dict with processing results
    """
    activity.logger.info(f"Processing request {request_id} from {requester}")
    
    # Simulate request validation
    await asyncio.sleep(0.3)
    
    return {
        "request_id": request_id,
        "requester": requester,
        "status": "pending_approval",
        "timestamp": datetime.utcnow().isoformat(),
    }


@activity.defn
async def record_decision(
    request_id: str,
    decision: str,
    approver: str = None,
    reason: str = None,
) -> None:
    """
    Record approval decision (idempotent).
    
    In production, writes to Supabase approval_decisions table.
    For Phase 1, just logs the decision.
    
    Args:
        request_id: Request identifier
        decision: 'approved' or 'rejected'
        approver: Who made the decision
        reason: Optional reason for decision
    """
    activity.logger.info(
        f"Recording decision for {request_id}: "
        f"{decision} by {approver or 'system'}"
    )
    
    # Simulate database write
    await asyncio.sleep(0.2)
    
    decision_record = {
        "request_id": request_id,
        "decision": decision,
        "approver": approver,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    activity.logger.info(f"Decision recorded: {decision_record}")
    
    # In production:
    # await supabase.table("approval_decisions").insert(decision_record)


@activity.defn
async def send_notification(message: str) -> None:
    """
    Send notification (idempotent).
    
    Args:
        message: Notification message
    """
    activity.logger.info(f"NOTIFICATION: {message}")
    print(f"[NOTIFICATION] {message}")


@activity.defn
async def long_running_task(task_id: str, duration_seconds: int = 10) -> str:
    """
    Long-running activity for chaos testing.
    
    Sends heartbeats during execution.
    Used to test worker crashes during activity execution.
    
    Args:
        task_id: Task identifier
        duration_seconds: How long to run
    
    Returns:
        Completion message
    """
    activity.logger.info(
        f"Long-running task {task_id} starting ({duration_seconds}s)"
    )
    
    # Simulate long-running work with heartbeats
    for i in range(duration_seconds):
        await asyncio.sleep(1)
        
        # Send heartbeat to Temporal (proves we're still alive)
        activity.heartbeat(f"Progress: {i+1}/{duration_seconds}")
        
        activity.logger.debug(
            f"Task {task_id} progress: {i+1}/{duration_seconds}"
        )
    
    result = f"Task {task_id} completed after {duration_seconds}s"
    activity.logger.info(result)
    return result
