"""
Approval Workflow
Human-in-the-Loop pattern with signal handling

Demonstrates signal-based workflow pausing for human approval.
Can wait hours/days for approval signal.
"""

from datetime import timedelta
from temporalio import workflow
from temporalio.exceptions import TimeoutError

with workflow.unsafe.imports_passed_through():
    from temporal.activities.test_activities import (
        process_request,
        record_decision,
        send_notification,
    )


@workflow.defn
class ApprovalWorkflow:
    """Workflow that pauses for human approval via signal"""
    
    def __init__(self):
        self._approved = False
        self._rejected = False
        self._decision_received = False
        self._approver = None
        self._reason = None
    
    @workflow.run
    async def run(
        self,
        request_id: str,
        requester: str,
        timeout_seconds: int = None,
    ) -> dict:
        """
        Main workflow execution with approval gate.
        
        Args:
            request_id: Unique identifier for this request
            requester: Who initiated the request
            timeout_seconds: Optional auto-reject timeout (None = wait forever)
        
        Returns:
            dict with approval decision and execution details
        """
        workflow.logger.info(
            f"Approval workflow started: {request_id} by {requester}"
        )
        
        # Step 1: Process the request
        process_result = await workflow.execute_activity(
            process_request,
            args=[request_id, requester],
            start_to_close_timeout=timedelta(seconds=30),
        )
        workflow.logger.info(f"Request processed: {process_result}")
        
        # Step 2: Send notification (optional)
        await workflow.execute_activity(
            send_notification,
            args=[f"Approval request {request_id} awaiting decision"],
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        # Step 3: Wait for approval signal
        workflow.logger.info("Waiting for approval signal...")
        
        try:
            timeout_delta = (
                timedelta(seconds=timeout_seconds) if timeout_seconds else None
            )
            await workflow.wait_condition(
                lambda: self._decision_received, timeout=timeout_delta
            )
        except TimeoutError:
            workflow.logger.warning(f"Timeout - auto-rejecting")
            self._rejected = True
            self._reason = "Timeout"
        
        # Step 4: Record decision
        decision = "approved" if self._approved else "rejected"
        workflow.logger.info(
            f"Decision: {decision} by {self._approver or 'system'}"
        )
        
        await workflow.execute_activity(
            record_decision,
            args=[request_id, decision, self._approver, self._reason],
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        # Step 5: Execute based on decision
        if self._approved:
            workflow.logger.info("Executing approved actions...")
        else:
            workflow.logger.info("Request rejected")
        
        return {
            "request_id": request_id,
            "requester": requester,
            "approved": self._approved,
            "rejected": self._rejected,
            "approver": self._approver,
            "reason": self._reason,
            "message": f"Request {decision}",
        }
    
    @workflow.signal
    async def approve(self, decision_data: dict = None):
        """
        Signal to approve the request.
        
        Args:
            decision_data: dict with 'approver' and optional 'reason'
        """
        data = decision_data or {}
        approver = data.get("approver", "unknown")
        reason = data.get("reason", "Approved")
        
        workflow.logger.info(f"Approval signal received from {approver}")
        self._approved = True
        self._decision_received = True
        self._approver = approver
        self._reason = reason
    
    @workflow.signal
    async def reject(self, decision_data: dict = None):
        """
        Signal to reject the request.
        
        Args:
            decision_data: dict with 'approver' and optional 'reason'
        """
        data = decision_data or {}
        approver = data.get("approver", "unknown")
        reason = data.get("reason", "Rejected")
        
        workflow.logger.info(f"Rejection signal received from {approver}")
        self._rejected = True
        self._decision_received = True
        self._approver = approver
        self._reason = reason
    
    @workflow.query
    def get_status(self) -> dict:
        """Query current approval state"""
        return {
            "decision_received": self._decision_received,
            "approved": self._approved,
            "rejected": self._rejected,
            "approver": self._approver,
        }
