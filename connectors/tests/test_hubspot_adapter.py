"""
Tests for HubSpot Adapter v2.0

Tests both direct API methods and MCP helper functions.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connectors.adapters.hubspot import HubSpotAdapter, HubSpotMCPHelper
from connectors.adapters.base import AdapterConfig, AdapterCapability
from connectors.unified_schema import UnifiedCustomer, UnifiedAddress


class TestHubSpotAdapterV2:
    """Tests for HubSpot adapter version 2.0"""
    
    def test_adapter_version(self):
        """Test adapter is v2.0 with MCP support"""
        config = AdapterConfig(
            base_url="https://api.hubapi.com",
            timeout=30
        )
        adapter = HubSpotAdapter(config, {"api_key": "test"})
        
        assert adapter.version == "2.0.0"
        assert AdapterCapability.BATCH in adapter.capabilities
    
    def test_object_types_defined(self):
        """Test supported object types"""
        config = AdapterConfig(
            base_url="https://api.hubapi.com",
            timeout=30
        )
        adapter = HubSpotAdapter(config, {"api_key": "test"})
        
        assert "contacts" in adapter.OBJECT_TYPES
        assert "companies" in adapter.OBJECT_TYPES
        assert "deals" in adapter.OBJECT_TYPES
    
    @pytest.mark.asyncio
    async def test_to_unified_transformation(self):
        """Test HubSpot to unified transformation"""
        config = AdapterConfig(
            base_url="https://api.hubapi.com",
            timeout=30
        )
        adapter = HubSpotAdapter(config, {"api_key": "test"})
        
        hubspot_data = {
            "id": "12345",
            "properties": {
                "email": "test@example.com",
                "firstname": "John",
                "lastname": "Doe",
                "phone": "+1234567890",
                "company": "ACME Corp",
                "city": "Boston",
                "state": "MA",
                "hs_lead_status": "qualified"
            }
        }
        
        unified = await adapter.to_unified(hubspot_data)
        
        assert unified.source_id == "12345"
        assert unified.email == "test@example.com"
        assert unified.name == "John Doe"
        assert unified.company == "ACME Corp"
        assert "qualified" in unified.tags
    
    @pytest.mark.asyncio
    async def test_from_unified_transformation(self):
        """Test unified to HubSpot transformation"""
        config = AdapterConfig(
            base_url="https://api.hubapi.com",
            timeout=30
        )
        adapter = HubSpotAdapter(config, {"api_key": "test"})
        
        customer = UnifiedCustomer(
            source_system="hubspot",
            source_id="123",
            email="jane@example.com",
            name="Jane Smith",
            phone="+9876543210",
            company="Tech Inc",
            tags=["new_lead"]
        )
        
        hubspot_format = await adapter.from_unified(customer)
        
        props = hubspot_format["properties"]
        assert props["email"] == "jane@example.com"
        assert props["firstname"] == "Jane"
        assert props["lastname"] == "Smith"
        assert props["hs_lead_status"] == "new_lead"
    
    def test_mcp_list_params(self):
        """Test MCP list parameters generation"""
        config = AdapterConfig(
            base_url="https://api.hubapi.com",
            timeout=30
        )
        adapter = HubSpotAdapter(config, {"api_key": "test"})
        
        params = adapter.get_mcp_list_params(
            object_type="contacts",
            limit=50
        )
        
        assert params["objectType"] == "contacts"
        assert params["limit"] == 50
        assert "email" in params["properties"]
    
    def test_mcp_search_params(self):
        """Test MCP search parameters generation"""
        config = AdapterConfig(
            base_url="https://api.hubapi.com",
            timeout=30
        )
        adapter = HubSpotAdapter(config, {"api_key": "test"})
        
        params = adapter.get_mcp_search_params(
            object_type="contacts",
            query="john@example.com"
        )
        
        assert params["objectType"] == "contacts"
        assert params["query"] == "john@example.com"


class TestHubSpotMCPHelper:
    """Tests for HubSpot MCP helper functions"""
    
    def test_list_contacts_params(self):
        """Test contact list params"""
        params = HubSpotMCPHelper.list_contacts(limit=25)
        
        assert params["objectType"] == "contacts"
        assert params["limit"] == 25
        assert "email" in params["properties"]
        assert "firstname" in params["properties"]
    
    def test_list_companies_params(self):
        """Test company list params"""
        params = HubSpotMCPHelper.list_companies(limit=50)
        
        assert params["objectType"] == "companies"
        assert "name" in params["properties"]
        assert "domain" in params["properties"]
    
    def test_list_deals_params(self):
        """Test deal list params"""
        params = HubSpotMCPHelper.list_deals()
        
        assert params["objectType"] == "deals"
        assert "dealname" in params["properties"]
        assert "amount" in params["properties"]
    
    def test_search_by_email(self):
        """Test search with email filter"""
        params = HubSpotMCPHelper.search_contacts(
            email="test@example.com"
        )
        
        assert params["objectType"] == "contacts"
        assert "filterGroups" in params
        
        filters = params["filterGroups"][0]["filters"]
        assert filters[0]["propertyName"] == "email"
        assert filters[0]["operator"] == "EQ"
        assert filters[0]["value"] == "test@example.com"
    
    def test_search_by_company(self):
        """Test search with company filter"""
        params = HubSpotMCPHelper.search_contacts(
            company="ACME"
        )
        
        filters = params["filterGroups"][0]["filters"]
        assert filters[0]["propertyName"] == "company"
        assert filters[0]["operator"] == "CONTAINS_TOKEN"
    
    def test_batch_create_params(self):
        """Test batch create parameters"""
        contacts = [
            {"email": "a@test.com", "firstname": "Alice"},
            {"email": "b@test.com", "firstname": "Bob"}
        ]
        
        params = HubSpotMCPHelper.create_contacts_batch(contacts)
        
        assert params["objectType"] == "contacts"
        assert len(params["inputs"]) == 2
        assert params["inputs"][0]["properties"]["email"] == "a@test.com"
    
    def test_unified_to_hubspot_conversion(self):
        """Test unified model to HubSpot properties"""
        customer = UnifiedCustomer(
            source_system="hubspot",
            source_id="123",
            email="test@test.com",
            name="Test User",
            phone="+1111111111",
            billing_address=UnifiedAddress(
                source_system="hubspot",
                source_id="addr_1",
                city="NYC",
                state="NY"
            )
        )
        
        props = HubSpotMCPHelper.unified_to_hubspot_props(customer)
        
        assert props["email"] == "test@test.com"
        assert props["firstname"] == "Test"
        assert props["lastname"] == "User"
        assert props["city"] == "NYC"
        assert props["state"] == "NY"
    
    def test_hubspot_to_unified_conversion(self):
        """Test HubSpot response to unified format"""
        hubspot_data = {
            "id": "999",
            "properties": {
                "email": "converted@test.com",
                "firstname": "Converted",
                "lastname": "User",
                "hs_lead_status": "customer"
            }
        }
        
        unified_dict = HubSpotMCPHelper.hubspot_to_unified(hubspot_data)
        
        assert unified_dict["source_id"] == "999"
        assert unified_dict["email"] == "converted@test.com"
        assert unified_dict["name"] == "Converted User"
        assert "customer" in unified_dict["tags"]
    
    def test_limit_enforcement(self):
        """Test max limit is enforced"""
        # List max is 500
        params = HubSpotMCPHelper.list_contacts(limit=1000)
        assert params["limit"] == 500
        
        # Search max is 100
        params = HubSpotMCPHelper.search_contacts(limit=500)
        assert params["limit"] == 100
    
    def test_batch_max_100(self):
        """Test batch operations limited to 100"""
        # Create 150 contacts
        contacts = [
            {"email": f"user{i}@test.com"}
            for i in range(150)
        ]
        
        params = HubSpotMCPHelper.create_contacts_batch(contacts)
        
        # Should be capped at 100
        assert len(params["inputs"]) == 100
