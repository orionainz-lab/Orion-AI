"""
Connector Sync Activities

Temporal activities for connector operations.
"""

from temporalio import activity
from typing import Dict, Any
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from connectors.adapters import AdapterFactory
from connectors.services import ConnectorRegistry, CredentialManager
from supabase import create_client


@activity.defn
async def sync_connector_data(
    config_id: str,
    connector_name: str
) -> Dict[str, Any]:
    """
    Sync data from external connector.
    
    Args:
        config_id: Config UUID
        connector_name: Connector type
    
    Returns:
        Sync result with record count
    """
    activity.logger.info(
        f"Syncing {connector_name} config {config_id}"
    )
    
    # Initialize services
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase not configured")
    
    db = create_client(supabase_url, supabase_key)
    cred_manager = CredentialManager()
    registry = ConnectorRegistry(db, cred_manager)
    
    # Get config and credentials
    config = await registry.get_config(config_id)
    if not config:
        raise ValueError(f"Config not found: {config_id}")
    
    credentials = await registry.get_credentials(config_id)
    
    # Create adapter
    factory = AdapterFactory(registry)
    adapter = await factory.create(
        connector_name,
        config_dict=config["config"],
        credentials=credentials
    )
    
    # Sync data (example: customers)
    records_synced = 0
    
    async with adapter:
        if connector_name == "stripe":
            # Fetch customers
            customers = await adapter.list_customers(limit=100)
            
            # Store in Supabase (simplified)
            for customer in customers:
                # Here you would store in a unified_customers table
                records_synced += 1
            
            activity.logger.info(
                f"Synced {records_synced} customers"
            )
    
    return {
        "records_synced": records_synced,
        "connector": connector_name,
        "config_id": config_id
    }


@activity.defn
async def update_sync_status(
    config_id: str,
    status: str,
    error_message: str = None
) -> None:
    """
    Update sync status in database.
    
    Args:
        config_id: Config UUID
        status: idle/syncing/error/success
        error_message: Error if status=error
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        return
    
    db = create_client(supabase_url, supabase_key)
    cred_manager = CredentialManager()
    registry = ConnectorRegistry(db, cred_manager)
    
    await registry.update_sync_status(
        config_id,
        status,
        error_message
    )
    
    activity.logger.info(
        f"Updated config {config_id} status to {status}"
    )


@activity.defn
async def transform_webhook_event(
    event_data: Dict[str, Any],
    connector_name: str
) -> Dict[str, Any]:
    """
    Transform webhook to unified format.
    
    Args:
        event_data: Raw webhook payload
        connector_name: Source connector
    
    Returns:
        Unified event data
    """
    from connectors.unified_schema import UnifiedEvent
    
    # Create unified event
    unified = UnifiedEvent(
        source_system=connector_name,
        source_id=event_data.get("id", "unknown"),
        event_type=event_data.get("type", "unknown"),
        event_category="webhook",
        payload=event_data,
        raw_data=event_data
    )
    
    return unified.model_dump()


@activity.defn
async def store_webhook_event(
    unified_event: Dict[str, Any]
) -> None:
    """
    Store event in Supabase.
    
    Args:
        unified_event: Unified event data
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        return
    
    db = create_client(supabase_url, supabase_key)
    
    # Store in process_events table
    db.table("process_events").insert({
        "event_type": "webhook",
        "event_name": unified_event.get("event_type"),
        "status": "completed",
        "metadata": {
            "source_system": unified_event.get("source_system"),
            "source_id": unified_event.get("source_id")
        }
    }).execute()
    
    activity.logger.info("Stored webhook event")
