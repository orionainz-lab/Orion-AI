"""
End-to-End Integration Tests

Tests the complete connector framework flow.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connectors.adapters.stripe import StripeAdapter
from connectors.adapters.hubspot import HubSpotAdapter
from connectors.adapters.base import AdapterConfig
from connectors.unified_schema import UnifiedCustomer


class TestAdapterTransformations:
    """Test data transformations for all adapters"""
    
    @pytest.mark.asyncio
    async def test_stripe_roundtrip(self):
        """Test Stripe to unified and back"""
        # Create adapter
        config = AdapterConfig(
            base_url="https://api.stripe.com",
            timeout=30
        )
        adapter = StripeAdapter(config, {"api_key": "test"})
        
        # Sample Stripe customer
        stripe_data = {
            "id": "cus_test",
            "email": "test@example.com",
            "name": "Test User",
            "phone": "+1234567890",
            "address": {
                "line1": "123 Main St",
                "city": "Boston",
                "state": "MA",
                "postal_code": "02101",
                "country": "US"
            },
            "metadata": {"tier": "premium"}
        }
        
        # Transform to unified
        unified = await adapter.to_unified(stripe_data)
        
        assert unified.source_id == "cus_test"
        assert unified.email == "test@example.com"
        assert unified.name == "Test User"
        assert unified.billing_address is not None
        assert unified.billing_address.city == "Boston"
        
        # Transform back to Stripe format
        back_to_stripe = await adapter.from_unified(unified)
        
        assert back_to_stripe["email"] == "test@example.com"
        assert back_to_stripe["name"] == "Test User"
        assert "address" in back_to_stripe
    
    @pytest.mark.asyncio
    async def test_hubspot_roundtrip(self):
        """Test HubSpot to unified and back"""
        config = AdapterConfig(
            base_url="https://api.hubapi.com",
            timeout=30
        )
        adapter = HubSpotAdapter(config, {"api_key": "test"})
        
        # Sample HubSpot contact
        hubspot_data = {
            "id": "123",
            "properties": {
                "email": "contact@example.com",
                "firstname": "Jane",
                "lastname": "Doe",
                "phone": "+9876543210",
                "company": "ACME Corp",
                "city": "New York",
                "state": "NY",
                "zip": "10001"
            }
        }
        
        # Transform to unified
        unified = await adapter.to_unified(hubspot_data)
        
        assert unified.source_id == "123"
        assert unified.email == "contact@example.com"
        assert unified.name == "Jane Doe"
        assert unified.company == "ACME Corp"
        
        # Transform back
        back_to_hubspot = await adapter.from_unified(unified)
        
        props = back_to_hubspot["properties"]
        assert props["email"] == "contact@example.com"
        assert props["firstname"] == "Jane"
        assert props["lastname"] == "Doe"


class TestWebhookVerification:
    """Test webhook signature verification"""
    
    def test_stripe_signature_verification(self):
        """Test Stripe webhook verification"""
        from api.webhooks.handler import WebhookVerifier
        
        # This would require real Stripe test data
        # For now, test the structure
        assert hasattr(WebhookVerifier, 'verify_stripe')
        assert hasattr(WebhookVerifier, 'verify_hubspot')
    
    def test_hubspot_signature_verification(self):
        """Test HubSpot webhook verification"""
        from api.webhooks.handler import WebhookVerifier
        import hmac
        import hashlib
        
        payload = b'{"test": "data"}'
        secret = "test_secret"
        
        # Generate signature
        signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Verify
        is_valid = WebhookVerifier.verify_hubspot(
            payload,
            signature,
            secret
        )
        
        assert is_valid is True


class TestUnifiedSchemaValidation:
    """Test unified schema validation"""
    
    def test_customer_email_validation(self):
        """Test email validation"""
        with pytest.raises(Exception):
            UnifiedCustomer(
                source_system="test",
                source_id="123",
                email="invalid-email",
                name="Test"
            )
    
    def test_customer_required_fields(self):
        """Test required fields"""
        with pytest.raises(Exception):
            UnifiedCustomer(
                source_system="test",
                source_id="123"
                # Missing email and name
            )
    
    def test_customer_with_full_address(self):
        """Test customer with complete address"""
        from connectors.unified_schema import UnifiedAddress
        
        customer = UnifiedCustomer(
            source_system="test",
            source_id="123",
            email="test@example.com",
            name="Test User",
            billing_address=UnifiedAddress(
                source_system="test",
                source_id="addr_123",
                street="123 Main St",
                city="Boston",
                postal_code="02101",
                country="US"
            )
        )
        
        assert customer.has_complete_billing_address() is True


class TestAdapterRegistry:
    """Test adapter registration system"""
    
    def test_stripe_registered(self):
        """Test Stripe adapter is registered"""
        from connectors.adapters.registry import get_adapter
        
        adapter_class = get_adapter("stripe")
        assert adapter_class is not None
        assert adapter_class.name == "stripe"
    
    def test_hubspot_registered(self):
        """Test HubSpot adapter is registered"""
        from connectors.adapters.registry import get_adapter
        
        adapter_class = get_adapter("hubspot")
        assert adapter_class is not None
        assert adapter_class.name == "hubspot"
    
    def test_list_all_adapters(self):
        """Test listing all adapters"""
        from connectors.adapters.registry import list_adapters
        
        adapters = list_adapters()
        assert len(adapters) >= 2  # At least Stripe and HubSpot
        assert "stripe" in adapters
        assert "hubspot" in adapters


@pytest.mark.integration
class TestDatabaseIntegration:
    """
    Integration tests requiring Supabase.
    Run with: pytest -m integration
    """
    
    @pytest.mark.asyncio
    async def test_connector_listing(self, registry):
        """Test listing connectors from database"""
        connectors = await registry.list_connectors()
        
        assert len(connectors) >= 1
        assert any(c["name"] == "stripe" for c in connectors)
    
    @pytest.mark.asyncio
    async def test_config_lifecycle(self, registry, test_user_id):
        """Test create, read, update, delete config"""
        # Create
        config = await registry.create_config(
            connector_name="stripe",
            user_id=test_user_id,
            config_name="E2E Test Config",
            config_data={"test": True},
            credentials={"api_key": "test_key"}
        )
        
        config_id = config["id"]
        
        try:
            # Read
            retrieved = await registry.get_config(config_id)
            assert retrieved["name"] == "E2E Test Config"
            
            # Update
            updated = await registry.update_config(
                config_id,
                {"test": False, "updated": True}
            )
            assert updated["config"]["updated"] is True
            
            # Credentials
            creds = await registry.get_credentials(config_id)
            assert creds["api_key"] == "test_key"
        
        finally:
            # Delete
            await registry.delete_config(config_id)


# Fixtures
@pytest.fixture
def registry():
    """Create registry for testing"""
    from supabase import create_client
    from connectors.services import (
        ConnectorRegistry,
        CredentialManager
    )
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        pytest.skip("Supabase not configured")
    
    db = create_client(url, key)
    manager = CredentialManager()
    
    return ConnectorRegistry(db, manager)


@pytest.fixture
def test_user_id():
    """Get test user ID"""
    return os.getenv("TEST_USER_ID", "e2e-test-user-uuid")
