"""
Stripe Adapter

Connector for Stripe API using MCP integration.
"""

from typing import List
from connectors.adapters.base import (
    BaseAdapter,
    AdapterConfig,
    AdapterCapability
)
from connectors.adapters.registry import register_adapter
from connectors.adapters.exceptions import (
    AuthenticationError,
    APIError
)
from connectors.unified_schema.customer import UnifiedCustomer


@register_adapter("stripe")
class StripeAdapter(BaseAdapter[UnifiedCustomer]):
    """
    Stripe API adapter.
    
    Uses Stripe MCP for operations.
    Docs: https://stripe.com/docs/api
    """
    
    name = "stripe"
    version = "1.0.0"
    capabilities = [
        AdapterCapability.READ,
        AdapterCapability.WRITE,
        AdapterCapability.WEBHOOK
    ]
    
    def _get_auth_headers(self) -> dict[str, str]:
        """Get Stripe auth headers"""
        api_key = self.credentials.get("api_key", "")
        if not api_key:
            raise AuthenticationError("Stripe API key not provided")
        
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
    async def to_unified(self, data: dict) -> UnifiedCustomer:
        """Transform Stripe customer to unified model"""
        address = data.get("address") or {}
        
        return UnifiedCustomer(
            source_system="stripe",
            source_id=data["id"],
            email=data.get("email", "unknown@example.com"),
            name=data.get("name") or data.get("email", "Unknown"),
            phone=data.get("phone"),
            billing_address={
                "source_system": "stripe",
                "source_id": data["id"],
                "street": address.get("line1"),
                "street2": address.get("line2"),
                "city": address.get("city"),
                "state": address.get("state"),
                "postal_code": address.get("postal_code"),
                "country": address.get("country")
            } if address else None,
            tags=data.get("metadata", {}).get("tags", "").split(",") \
                if data.get("metadata", {}).get("tags") else [],
            custom_fields=data.get("metadata", {}),
            raw_data=data
        )
    
    async def from_unified(self, model: UnifiedCustomer) -> dict:
        """Transform unified model to Stripe format"""
        data = {
            "email": str(model.email),
            "name": model.name,
        }
        
        if model.phone:
            data["phone"] = model.phone
        
        if model.billing_address:
            data["address"] = {
                "line1": model.billing_address.street,
                "line2": model.billing_address.street2,
                "city": model.billing_address.city,
                "state": model.billing_address.state,
                "postal_code": model.billing_address.postal_code,
                "country": model.billing_address.country
            }
        
        if model.tags or model.custom_fields:
            data["metadata"] = {
                **model.custom_fields,
                "tags": ",".join(model.tags) if model.tags else ""
            }
        
        return data
    
    async def list_customers(
        self,
        limit: int = 100
    ) -> List[UnifiedCustomer]:
        """
        Fetch customers from Stripe.
        
        Args:
            limit: Max customers to fetch (1-100)
        
        Returns:
            List of unified customers
        """
        if not self._client:
            await self.connect()
        
        try:
            response = await self._client.get(
                "/v1/customers",
                params={"limit": min(limit, 100)}
            )
            response.raise_for_status()
            data = response.json()
            
            return [
                await self.to_unified(c)
                for c in data.get("data", [])
            ]
        
        except Exception as e:
            raise APIError(
                f"Failed to list customers: {str(e)}",
                status_code=getattr(e, "status_code", None)
            )
    
    async def create_customer(
        self,
        customer: UnifiedCustomer
    ) -> UnifiedCustomer:
        """
        Create customer in Stripe.
        
        Args:
            customer: Unified customer model
        
        Returns:
            Created customer with Stripe ID
        """
        if not self._client:
            await self.connect()
        
        payload = await self.from_unified(customer)
        
        try:
            response = await self._client.post(
                "/v1/customers",
                data=payload
            )
            response.raise_for_status()
            return await self.to_unified(response.json())
        
        except Exception as e:
            raise APIError(
                f"Failed to create customer: {str(e)}",
                status_code=getattr(e, "status_code", None)
            )
