"""
HubSpot MCP Helper

Utilities for using HubSpot via MCP tools.
"""

from typing import List, Dict, Any, Optional
from connectors.unified_schema.customer import UnifiedCustomer


class HubSpotMCPHelper:
    """
    Helper class for HubSpot MCP tool integration.
    
    Use this when calling HubSpot via Cursor's MCP system
    instead of direct API calls.
    
    MCP Tools Available:
    - hubspot-list-objects
    - hubspot-search-objects  
    - hubspot-batch-create-objects
    - hubspot-batch-update-objects
    - hubspot-batch-read-objects
    - hubspot-create-engagement
    - hubspot-list-workflows
    """
    
    # Default contact properties
    CONTACT_PROPS = [
        "email", "firstname", "lastname", "phone",
        "company", "address", "city", "state",
        "zip", "country", "hs_lead_status",
        "lifecyclestage", "createdate", "lastmodifieddate"
    ]
    
    # Company properties
    COMPANY_PROPS = [
        "name", "domain", "industry", "phone",
        "city", "state", "country", "numberofemployees"
    ]
    
    # Deal properties
    DEAL_PROPS = [
        "dealname", "amount", "dealstage", "pipeline",
        "closedate", "createdate"
    ]
    
    @staticmethod
    def list_contacts(
        limit: int = 100,
        properties: List[str] = None
    ) -> Dict[str, Any]:
        """
        Build params for hubspot-list-objects (contacts).
        
        Usage with MCP:
            params = HubSpotMCPHelper.list_contacts(limit=50)
            # Then call: CallMcpTool(
            #   server="user-hubspot",
            #   toolName="hubspot-list-objects",
            #   arguments=params
            # )
        """
        return {
            "objectType": "contacts",
            "limit": min(limit, 500),
            "properties": properties or HubSpotMCPHelper.CONTACT_PROPS
        }
    
    @staticmethod
    def list_companies(
        limit: int = 100,
        properties: List[str] = None
    ) -> Dict[str, Any]:
        """Build params for listing companies"""
        return {
            "objectType": "companies",
            "limit": min(limit, 500),
            "properties": properties or HubSpotMCPHelper.COMPANY_PROPS
        }
    
    @staticmethod
    def list_deals(
        limit: int = 100,
        properties: List[str] = None
    ) -> Dict[str, Any]:
        """Build params for listing deals"""
        return {
            "objectType": "deals",
            "limit": min(limit, 500),
            "properties": properties or HubSpotMCPHelper.DEAL_PROPS
        }
    
    @staticmethod
    def search_contacts(
        query: str = None,
        email: str = None,
        company: str = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Build params for hubspot-search-objects.
        
        Args:
            query: Text search across all searchable fields
            email: Filter by exact email
            company: Filter by company name contains
            limit: Max results (1-100)
        """
        params = {
            "objectType": "contacts",
            "limit": min(limit, 100),
            "properties": HubSpotMCPHelper.CONTACT_PROPS
        }
        
        if query:
            params["query"] = query
        
        # Build filter groups
        filters = []
        
        if email:
            filters.append({
                "propertyName": "email",
                "operator": "EQ",
                "value": email
            })
        
        if company:
            filters.append({
                "propertyName": "company",
                "operator": "CONTAINS_TOKEN",
                "value": company
            })
        
        if filters:
            params["filterGroups"] = [{"filters": filters}]
        
        return params
    
    @staticmethod
    def create_contacts_batch(
        contacts: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Build params for hubspot-batch-create-objects.
        
        Args:
            contacts: List of dicts with contact properties
                     e.g., [{"email": "...", "firstname": "..."}]
        
        Returns:
            Params for MCP batch create call
        """
        inputs = [
            {"properties": contact}
            for contact in contacts[:100]
        ]
        
        return {
            "objectType": "contacts",
            "inputs": inputs
        }
    
    @staticmethod
    def update_contacts_batch(
        updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build params for hubspot-batch-update-objects.
        
        Args:
            updates: List of dicts with 'id' and 'properties'
                    e.g., [{"id": "123", "properties": {...}}]
        """
        return {
            "objectType": "contacts",
            "inputs": updates[:100]
        }
    
    @staticmethod
    def unified_to_hubspot_props(
        customer: UnifiedCustomer
    ) -> Dict[str, str]:
        """
        Convert UnifiedCustomer to HubSpot properties dict.
        
        Useful for batch operations.
        """
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
        
        if customer.billing_address:
            addr = customer.billing_address
            if addr.street:
                props["address"] = addr.street
            if addr.city:
                props["city"] = addr.city
            if addr.state:
                props["state"] = addr.state
            if addr.postal_code:
                props["zip"] = addr.postal_code
            if addr.country:
                props["country"] = addr.country
        
        return props
    
    @staticmethod
    def hubspot_to_unified(
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert HubSpot response to unified format.
        
        Returns dict that can be passed to UnifiedCustomer().
        """
        props = data.get("properties", {})
        
        return {
            "source_system": "hubspot",
            "source_id": data.get("id", "unknown"),
            "email": props.get("email", "unknown@example.com"),
            "name": f"{props.get('firstname', '')} {props.get('lastname', '')}".strip() or "Unknown",
            "phone": props.get("phone"),
            "company": props.get("company"),
            "tags": [props["hs_lead_status"]] if props.get("hs_lead_status") else []
        }
