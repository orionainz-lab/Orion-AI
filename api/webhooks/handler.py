"""
Webhook Handler for Connector Events

Handles incoming webhooks from external systems (Stripe, HubSpot, etc.).
Verifies signatures and processes events.
"""

from fastapi import APIRouter, HTTPException, Request, Header
from typing import Optional
import hmac
import hashlib
from connectors.unified_schema import UnifiedEvent
from connectors.services import ConnectorRegistry
import json

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class WebhookVerifier:
    """Webhook signature verification"""
    
    @staticmethod
    def verify_stripe(
        payload: bytes,
        signature: str,
        secret: str
    ) -> bool:
        """
        Verify Stripe webhook signature.
        
        Args:
            payload: Raw request body
            signature: Stripe-Signature header
            secret: Webhook secret
        
        Returns:
            True if signature is valid
        """
        try:
            # Parse signature header
            parts = {}
            for item in signature.split(','):
                key, value = item.split('=')
                parts[key] = value
            
            timestamp = parts.get('t')
            signatures = [
                parts.get(k) 
                for k in parts.keys() 
                if k.startswith('v1')
            ]
            
            # Compute expected signature
            signed_payload = f"{timestamp}.{payload.decode()}"
            expected = hmac.new(
                secret.encode(),
                signed_payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare
            return any(
                hmac.compare_digest(expected, sig)
                for sig in signatures
            )
        
        except Exception:
            return False
    
    @staticmethod
    def verify_hubspot(
        payload: bytes,
        signature: str,
        secret: str
    ) -> bool:
        """
        Verify HubSpot webhook signature.
        
        Args:
            payload: Raw request body
            signature: X-HubSpot-Signature header
            secret: Webhook secret
        
        Returns:
            True if signature is valid
        """
        expected = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)


# ============================================
# Stripe Webhook Endpoint
# ============================================

@router.post("/stripe")
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None)
):
    """
    Handle Stripe webhook events.
    
    Headers:
    - Stripe-Signature: Webhook signature
    
    Events processed:
    - customer.created
    - customer.updated
    - customer.deleted
    - invoice.paid
    - payment_intent.succeeded
    """
    # Get raw body
    body = await request.body()
    
    # TODO: Get webhook secret from DB
    webhook_secret = "whsec_test"
    
    # Verify signature
    if stripe_signature:
        is_valid = WebhookVerifier.verify_stripe(
            body,
            stripe_signature,
            webhook_secret
        )
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Invalid signature"
            )
    
    # Parse event
    try:
        event_data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON"
        )
    
    # Create unified event
    event = UnifiedEvent(
        source_system="stripe",
        source_id=event_data.get("id", "unknown"),
        event_type=event_data.get("type", "unknown"),
        event_category="webhook",
        payload=event_data.get("data", {}),
        resource_type=_extract_resource_type(
            event_data.get("type", "")
        ),
        occurred_at=event_data.get("created")
    )
    
    # Process event (async via Temporal)
    # TODO: Trigger Temporal workflow
    print(f"[WEBHOOK] Received {event.event_type}")
    
    return {"received": True}


# ============================================
# HubSpot Webhook Endpoint
# ============================================

@router.post("/hubspot")
async def handle_hubspot_webhook(
    request: Request,
    x_hubspot_signature: Optional[str] = Header(None)
):
    """
    Handle HubSpot webhook events.
    
    Headers:
    - X-HubSpot-Signature: Webhook signature
    
    Events processed:
    - contact.creation
    - contact.propertyChange
    - company.creation
    - deal.creation
    """
    body = await request.body()
    
    # TODO: Get webhook secret from DB
    webhook_secret = "hubspot_secret"
    
    # Verify signature
    if x_hubspot_signature:
        is_valid = WebhookVerifier.verify_hubspot(
            body,
            x_hubspot_signature,
            webhook_secret
        )
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Invalid signature"
            )
    
    # Parse event
    try:
        event_data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON"
        )
    
    # Create unified event
    event = UnifiedEvent(
        source_system="hubspot",
        source_id=event_data.get("eventId", "unknown"),
        event_type=event_data.get("subscriptionType", "unknown"),
        event_category="webhook",
        payload=event_data,
        occurred_at=event_data.get("occurredAt")
    )
    
    print(f"[WEBHOOK] Received {event.event_type}")
    
    return {"received": True}


# ============================================
# Helper Functions
# ============================================

def _extract_resource_type(event_type: str) -> Optional[str]:
    """Extract resource type from event type"""
    if not event_type:
        return None
    
    parts = event_type.split('.')
    return parts[0] if parts else None
