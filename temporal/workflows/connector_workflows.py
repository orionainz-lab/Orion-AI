"""
Connector Sync Workflow

Temporal workflow for syncing data from external connectors.
Handles periodic sync, retries, and error tracking.
"""

from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta
from typing import Dict, Any
import asyncio


@workflow.defn
class ConnectorSyncWorkflow:
    """
    Durable workflow for connector synchronization.
    
    Features:
    - Periodic sync (configurable interval)
    - Automatic retries with backoff
    - Status tracking in Supabase
    - Signal handling for manual sync
    """
    
    def __init__(self):
        self._manual_sync_requested = False
    
    @workflow.run
    async def run(
        self,
        config_id: str,
        connector_name: str,
        sync_interval_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Main workflow execution.
        
        Args:
            config_id: Connector config UUID
            connector_name: Connector type (stripe, hubspot)
            sync_interval_minutes: Sync frequency
        
        Returns:
            Sync summary stats
        """
        workflow.logger.info(
            f"Starting sync workflow for {connector_name} "
            f"config {config_id}"
        )
        
        sync_count = 0
        total_synced = 0
        
        while True:
            try:
                # Execute sync activity
                result = await workflow.execute_activity(
                    sync_connector_data,
                    args=[config_id, connector_name],
                    start_to_close_timeout=timedelta(minutes=10),
                    retry_policy=RetryPolicy(
                        maximum_attempts=3,
                        initial_interval=timedelta(seconds=10),
                        maximum_interval=timedelta(minutes=5),
                        backoff_coefficient=2.0
                    )
                )
                
                sync_count += 1
                total_synced += result.get("records_synced", 0)
                
                workflow.logger.info(
                    f"Sync completed: {result.get('records_synced', 0)} "
                    f"records"
                )
                
                # Update status activity
                await workflow.execute_activity(
                    update_sync_status,
                    args=[config_id, "success", None],
                    start_to_close_timeout=timedelta(seconds=30)
                )
            
            except Exception as e:
                workflow.logger.error(
                    f"Sync failed: {str(e)}"
                )
                
                # Update error status
                await workflow.execute_activity(
                    update_sync_status,
                    args=[config_id, "error", str(e)],
                    start_to_close_timeout=timedelta(seconds=30)
                )
            
            # Wait for next sync or manual trigger
            if await workflow.wait_condition(
                lambda: self._manual_sync_requested,
                timeout=timedelta(minutes=sync_interval_minutes)
            ):
                workflow.logger.info("Manual sync triggered")
                self._manual_sync_requested = False
            else:
                workflow.logger.info(
                    f"Scheduled sync after {sync_interval_minutes}m"
                )
        
        return {
            "sync_count": sync_count,
            "total_synced": total_synced
        }
    
    @workflow.signal
    def trigger_sync(self):
        """Signal to trigger manual sync"""
        self._manual_sync_requested = True


@workflow.defn
class WebhookProcessingWorkflow:
    """
    Process incoming webhook events.
    
    Transforms external events to unified format and
    stores in Supabase.
    """
    
    @workflow.run
    async def run(
        self,
        event_data: Dict[str, Any],
        connector_name: str
    ) -> Dict[str, Any]:
        """
        Process webhook event.
        
        Args:
            event_data: Raw webhook payload
            connector_name: Source connector
        
        Returns:
            Processing result
        """
        workflow.logger.info(
            f"Processing webhook from {connector_name}"
        )
        
        # Transform to unified format
        result = await workflow.execute_activity(
            transform_webhook_event,
            args=[event_data, connector_name],
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        # Store in database
        await workflow.execute_activity(
            store_webhook_event,
            args=[result],
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        workflow.logger.info("Webhook processed successfully")
        
        return {"status": "processed", "event_id": result.get("id")}


# ============================================
# Activity Definitions (implemented separately)
# ============================================

# These would be implemented in temporal/activities/connector_activities.py

async def sync_connector_data(
    config_id: str,
    connector_name: str
) -> Dict[str, Any]:
    """
    Activity: Sync data from external connector.
    
    This would:
    1. Load config and credentials from DB
    2. Create adapter instance
    3. Fetch data from external API
    4. Transform to unified format
    5. Store in Supabase
    """
    pass  # Implemented in activities


async def update_sync_status(
    config_id: str,
    status: str,
    error_message: str = None
) -> None:
    """
    Activity: Update sync status in database.
    """
    pass  # Implemented in activities


async def transform_webhook_event(
    event_data: Dict[str, Any],
    connector_name: str
) -> Dict[str, Any]:
    """
    Activity: Transform webhook to unified format.
    """
    pass  # Implemented in activities


async def store_webhook_event(
    unified_event: Dict[str, Any]
) -> None:
    """
    Activity: Store event in Supabase.
    """
    pass  # Implemented in activities
