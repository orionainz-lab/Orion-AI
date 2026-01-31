"""
Integration Tests for Connector Registry

Tests credential encryption and registry operations.
"""

import pytest
from connectors.services import CredentialManager, CredentialType


class TestCredentialManager:
    """Tests for CredentialManager"""
    
    def test_generate_key(self):
        """Test key generation"""
        key = CredentialManager.generate_key()
        assert len(key) == 44  # Fernet key length
    
    def test_encryption_decryption(self):
        """Test encrypt/decrypt cycle"""
        key = CredentialManager.generate_key()
        manager = CredentialManager(key)
        
        plaintext = "sk_test_1234567890"
        encrypted = manager.encrypt(plaintext)
        
        assert encrypted != plaintext
        assert len(encrypted) > len(plaintext)
        
        decrypted = manager.decrypt(encrypted)
        assert decrypted == plaintext
    
    def test_empty_string_encryption(self):
        """Test that empty strings raise error"""
        key = CredentialManager.generate_key()
        manager = CredentialManager(key)
        
        with pytest.raises(ValueError):
            manager.encrypt("")
    
    def test_empty_string_decryption(self):
        """Test that empty strings raise error"""
        key = CredentialManager.generate_key()
        manager = CredentialManager(key)
        
        with pytest.raises(ValueError):
            manager.decrypt("")
    
    def test_invalid_decryption(self):
        """Test decryption with wrong key fails"""
        key1 = CredentialManager.generate_key()
        key2 = CredentialManager.generate_key()
        
        manager1 = CredentialManager(key1)
        manager2 = CredentialManager(key2)
        
        encrypted = manager1.encrypt("secret")
        
        with pytest.raises(ValueError):
            manager2.decrypt(encrypted)
    
    def test_key_rotation(self):
        """Test key rotation"""
        old_key = CredentialManager.generate_key()
        new_key = CredentialManager.generate_key()
        
        manager = CredentialManager(old_key)
        
        plaintext = "sk_test_old_key"
        encrypted_old = manager.encrypt(plaintext)
        
        # Rotate
        encrypted_new = manager.rotate_key(
            old_key,
            new_key,
            encrypted_old
        )
        
        # Verify with new key
        new_manager = CredentialManager(new_key)
        decrypted = new_manager.decrypt(encrypted_new)
        
        assert decrypted == plaintext
    
    def test_no_key_provided(self):
        """Test that missing key raises error"""
        import os
        os.environ.pop("ENCRYPTION_KEY", None)
        
        with pytest.raises(ValueError):
            CredentialManager()
    
    def test_invalid_key_format(self):
        """Test invalid key format"""
        with pytest.raises(ValueError):
            CredentialManager("not-a-valid-key")


class TestCredentialTypes:
    """Tests for credential type constants"""
    
    def test_credential_types_defined(self):
        """Test all credential types are defined"""
        assert CredentialType.API_KEY == "api_key"
        assert CredentialType.OAUTH_TOKEN == "oauth_token"
        assert CredentialType.BASIC_AUTH == "basic_auth"
        assert CredentialType.BEARER_TOKEN == "bearer_token"


class TestConnectorRegistry:
    """
    Integration tests for ConnectorRegistry.
    
    Note: These require actual Supabase connection.
    Run with: pytest -m integration
    """
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_list_connectors(self, registry):
        """Test listing connectors"""
        connectors = await registry.list_connectors()
        
        assert len(connectors) >= 1  # At least Stripe
        stripe = next(c for c in connectors if c["name"] == "stripe")
        assert stripe["type"] == "bidirectional"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_connector(self, registry):
        """Test getting connector by name"""
        stripe = await registry.get_connector("stripe")
        
        assert stripe is not None
        assert stripe["name"] == "stripe"
        assert "read" in stripe["capabilities"]
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_and_delete_config(self, registry, test_user_id):
        """Test config lifecycle"""
        # Create
        config = await registry.create_config(
            connector_name="stripe",
            user_id=test_user_id,
            config_name="Test Config",
            config_data={"base_url": "https://api.stripe.com"},
            credentials={"api_key": "sk_test_12345"}
        )
        
        assert config["name"] == "Test Config"
        config_id = config["id"]
        
        # Get credentials
        creds = await registry.get_credentials(config_id)
        assert creds["api_key"] == "sk_test_12345"
        
        # Delete
        result = await registry.delete_config(config_id)
        assert result is True


# Fixtures for integration tests
@pytest.fixture
def registry():
    """Create registry for testing"""
    from supabase import create_client
    import os
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        pytest.skip("Supabase not configured")
    
    db = create_client(url, key)
    manager = CredentialManager()
    
    from connectors.services import ConnectorRegistry
    return ConnectorRegistry(db, manager)


@pytest.fixture
def test_user_id():
    """Get test user ID"""
    import os
    return os.getenv("TEST_USER_ID", "test-user-uuid")
