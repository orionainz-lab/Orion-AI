"""
HubSpot Adapter

Connector for HubSpot CRM API with MCP integration.
Supports both direct API calls (httpx) and MCP tools.
"""

from typing import List, Optional, Dict, Any
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


@register_adapter("hubspot")
class HubSpotAdapter(BaseAdapter[UnifiedCustomer]):
    """
    HubSpot CRM adapter with MCP support.
    
    Supports:
    - Contacts, Companies, Deals
    - Direct API via httpx
    - MCP tools (when available)
    
    MCP Tools Available:
    - hubspot-list-objects
    - hubspot-search-objects
    - hubspot-batch-create-objects
    - hubspot-batch-update-objects
    """
    
    name = "hubspot"
    version = "2.0.0"  # Updated for MCP support
    capabilities = [
        AdapterCapability.READ,
        AdapterCapability.WRITE,
        AdapterCapability.WEBHOOK,
        AdapterCapability.BATCH
    ]
    
    # Supported object types
    OBJECT_TYPES = [
        "contacts", "companies", "deals",
        "tickets", "products", "quotes"
    ]
    
    # Default properties to fetch
    CONTACT_PROPERTIES = [
        "email", "firstname", "lastname", "phone",
        "company", "address", "city", "state",
        "zip", "country", "hs_lead_status"
    ]
    
    def _get_auth_headers(self) -> dict[str, str]:
        """Get HubSpot auth headers"""
        api_key = self.credentials.get("api_key", "")
        if not api_key:
            raise AuthenticationError(
                "HubSpot API key not provided"
            )
        
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def to_unified(self, data: dict) -> UnifiedCustomer:
        """Transform HubSpot contact to unified model"""
        props = data.get("properties", {})
        
        # Extract address
        address = None
        if any(props.get(f) for f in ["address", "city", "state"]):
            address = {
                "source_system": "hubspot",
                "source_id": data["id"],
                "street": props.get("address"),
                "city": props.get("city"),
                "state": props.get("state"),
                "postal_code": props.get("zip"),
                "country": props.get("country")
            }
        
        # Extract tags
        tags = []
        if props.get("hs_lead_status"):
            tags.append(props["hs_lead_status"])
        
        return UnifiedCustomer(
            source_system="hubspot",
            source_id=data["id"],
            email=props.get("email", "unknown@example.com"),
            name=(
                f"{props.get('firstname', '')} "
                f"{props.get('lastname', '')}"
            ).strip() or "Unknown",
            phone=props.get("phone"),
            company=props.get("company"),
            billing_address=address,
            tags=tags,
            custom_fields={
                k: v for k, v in props.items()
                if k not in self.CONTACT_PROPERTIES
            },
            raw_data=data
        )
    
    async def from_unified(self, model: UnifiedCustomer) -> dict:
        """Transform unified model to HubSpot format"""
        name_parts = model.name.split(' ', 1)
        firstname = name_parts[0] if name_parts else ""
        lastname = name_parts[1] if len(name_parts) > 1 else ""
        
        properties = {
            "email": str(model.email),
            "firstname": firstname,
            "lastname": lastname,
        }
        
        if model.phone:
            properties["phone"] = model.phone
        
        if model.company:
            properties["company"] = model.company
        
        if model.billing_address:
            properties.update({
                "address": model.billing_address.street,
                "city": model.billing_address.city,
                "state": model.billing_address.state,
                "zip": model.billing_address.postal_code,
                "country": model.billing_address.country
            })
        
        if model.custom_fields:
            properties.update(model.custom_fields)
        
        if model.tags:
            properties["hs_lead_status"] = model.tags[0]
        
        return {"properties": properties}
    
    # ==========================================
    # MCP-Compatible Methods
    # ==========================================
    
    def get_mcp_list_params(
        self,
        object_type: str = "contacts",
        limit: int = 100,
        properties: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get parameters for hubspot-list-objects MCP tool.
        
        Returns dict ready to pass to MCP CallMcpTool.
        """
        return {
            "objectType": object_type,
            "limit": min(limit, 500),
            "properties": properties or self.CONTACT_PROPERTIES
        }
    
    def get_mcp_search_params(
        self,
        object_type: str = "contacts",
        query: str = None,
        filters: List[Dict] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get parameters for hubspot-search-objects MCP tool.
        
        Args:
            object_type: contacts, companies, deals, etc.
            query: Text search across default properties
            filters: Filter groups for advanced search
            limit: Max results
        
        Returns:
            Dict ready for MCP tool call
        """
        params = {
            "objectType": object_type,
            "limit": min(limit, 100),
            "properties": self.CONTACT_PROPERTIES
        }
        
        if query:
            params["query"] = query
        
        if filters:
            params["filterGroups"] = filters
        
        return params
    
    def get_mcp_batch_create_params(
        self,
        customers: List[UnifiedCustomer]
    ) -> Dict[str, Any]:
        """
        Get parameters for hubspot-batch-create-objects MCP.
        
        Args:
            customers: List of unified customers to create
        
        Returns:
            Dict ready for MCP batch create
        """
        inputs = []
        for customer in customers[:100]:  # Max 100 per batch
            name_parts = customer.name.split(' ', 1)
            props = {
                "email": str(customer.email),
                "firstname": name_parts[0] if name_parts else "",
                "lastname": name_parts[1] if len(name_parts) > 1 else ""
            }
            if customer.phone:
                props["phone"] = customer.phone
            if customer.company:
                props["company"] = customer.company
            
            inputs.append({"properties": props})
        
        return {
            "objectType": "contacts",
            "inputs": inputs
        }
    
    # ==========================================
    # Direct API Methods (httpx)
    # ==========================================
    
    async def list_contacts(
        self,
        limit: int = 100,
        properties: List[str] = None
    ) -> List[UnifiedCustomer]:
        """Fetch contacts via direct API"""
        if not self._client:
            await self.connect()
        
        try:
            params = {
                "limit": min(limit, 100),
                "properties": ",".join(
                    properties or self.CONTACT_PROPERTIES
                )
            }
            response = await self._client.get(
                "/crm/v3/objects/contacts",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            return [
                await self.to_unified(c)
                for c in data.get("results", [])
            ]
        except Exception as e:
            raise APIError(f"Failed to list: {str(e)}")
    
    async def search_contacts(
        self,
        query: str = None,
        filters: List[Dict] = None,
        limit: int = 100
    ) -> List[UnifiedCustomer]:
        """
        Search contacts via direct API.
        
        Args:
            query: Text search
            filters: Filter groups
            limit: Max results
        """
        if not self._client:
            await self.connect()
        
        try:
            payload = {
                "limit": min(limit, 100),
                "properties": self.CONTACT_PROPERTIES
            }
            if query:
                payload["query"] = query
            if filters:
                payload["filterGroups"] = filters
            
            response = await self._client.post(
                "/crm/v3/objects/contacts/search",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return [
                await self.to_unified(c)
                for c in data.get("results", [])
            ]
        except Exception as e:
            raise APIError(f"Failed to search: {str(e)}")
    
    async def create_contact(
        self,
        customer: UnifiedCustomer
    ) -> UnifiedCustomer:
        """Create single contact"""
        if not self._client:
            await self.connect()
        
        payload = await self.from_unified(customer)
        
        try:
            response = await self._client.post(
                "/crm/v3/objects/contacts",
                json=payload
            )
            response.raise_for_status()
            return await self.to_unified(response.json())
        except Exception as e:
            raise APIError(f"Failed to create: {str(e)}")
    
    async def batch_create_contacts(
        self,
        customers: List[UnifiedCustomer]
    ) -> List[UnifiedCustomer]:
        """
        Batch create contacts (max 100).
        
        Args:
            customers: List of customers to create
        
        Returns:
            List of created customers with IDs
        """
        if not self._client:
            await self.connect()
        
        inputs = []
        for c in customers[:100]:
            payload = await self.from_unified(c)
            inputs.append(payload)
        
        try:
            response = await self._client.post(
                "/crm/v3/objects/contacts/batch/create",
                json={"inputs": inputs}
            )
            response.raise_for_status()
            data = response.json()
            
            return [
                await self.to_unified(r)
                for r in data.get("results", [])
            ]
        except Exception as e:
            raise APIError(f"Batch create failed: {str(e)}")
    
    async def update_contact(
        self,
        contact_id: str,
        customer: UnifiedCustomer
    ) -> UnifiedCustomer:
        """Update single contact"""
        if not self._client:
            await self.connect()
        
        payload = await self.from_unified(customer)
        
        try:
            response = await self._client.patch(
                f"/crm/v3/objects/contacts/{contact_id}",
                json=payload
            )
            response.raise_for_status()
            return await self.to_unified(response.json())
        except Exception as e:
            raise APIError(f"Failed to update: {str(e)}")
    
    async def delete_contact(self, contact_id: str) -> bool:
        """Delete contact by ID"""
        if not self._client:
            await self.connect()
        
        try:
            response = await self._client.delete(
                f"/crm/v3/objects/contacts/{contact_id}"
            )
            response.raise_for_status()
            return True
        except Exception as e:
            raise APIError(f"Failed to delete: {str(e)}")
