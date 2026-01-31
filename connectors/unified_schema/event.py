"""
Unified Event Model

Canonical event representation for webhooks and notifications.
Maps to: Stripe Event, HubSpot Webhook, Generic Webhook, etc.
"""

from pydantic import Field
from typing import Optional, Any
from datetime import datetime
from .base import UnifiedBase


class UnifiedEvent(UnifiedBase):
    """
    Canonical event model.
    
    Represents webhook events and system notifications.
    
    Schema Version: 1.0.0
    """
    
    __schema_version__ = "1.0.0"
    
    # Core fields
    event_type: str = Field(
        ...,
        description="Event type (e.g., 'customer.created')"
    )
    event_category: str = Field(
        default="system",
        description="Category: system, user, webhook, etc."
    )
    
    # Payload
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Event data payload"
    )
    
    # Context
    user_id: Optional[str] = Field(
        None,
        description="User who triggered event"
    )
    resource_type: Optional[str] = Field(
        None,
        description="Resource type (customer, invoice, etc.)"
    )
    resource_id: Optional[str] = Field(
        None,
        description="Resource ID"
    )
    
    # Timestamps
    occurred_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When event occurred"
    )
    
    # Status
    processed: bool = Field(
        False,
        description="Whether event has been processed"
    )
    processed_at: Optional[datetime] = Field(
        None,
        description="When event was processed"
    )
    
    def mark_processed(self) -> None:
        """Mark event as processed"""
        self.processed = True
        self.processed_at = datetime.utcnow()
    
    def is_customer_event(self) -> bool:
        """Check if event relates to customer"""
        return self.resource_type == "customer" or \
               "customer" in self.event_type.lower()
    
    def is_invoice_event(self) -> bool:
        """Check if event relates to invoice"""
        return self.resource_type == "invoice" or \
               "invoice" in self.event_type.lower()
