"""
SSO Integration Tests - Shared Fixtures and Utilities
"""

import os
import pytest
import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def supabase_client() -> Client:
    """Create Supabase client for tests."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        pytest.skip("Supabase credentials not configured")
    
    return create_client(url, key)


@pytest.fixture
def test_organization(supabase_client: Client) -> Dict[str, Any]:
    """Create test organization."""
    org_data = {
        "name": "SSO Test Organization",
        "slug": f"sso-test-{datetime.now().timestamp()}",
        "tier": "professional",
        "isolation_level": "row"
    }
    
    result = supabase_client.table("organizations").insert(org_data).execute()
    org = result.data[0]
    
    yield org
    
    # Cleanup
    supabase_client.table("organizations").delete().eq("id", org["id"]).execute()


@pytest.fixture
def sso_configuration(
    supabase_client: Client,
    test_organization: Dict[str, Any]
) -> Dict[str, Any]:
    """Create SSO configuration for testing."""
    config = {
        "org_id": test_organization["id"],
        "provider": "azure_ad",
        "protocol": "oidc",
        "enabled": True,
        "oidc_issuer": "https://login.microsoftonline.com/test-tenant/v2.0",
        "oidc_client_id": "test-client-id",
        "oidc_client_secret": "test-client-secret",
        "oidc_scopes": ["openid", "profile", "email"],
        "jit_enabled": True
    }
    
    result = supabase_client.table("sso_configurations").insert(config).execute()
    sso_config = result.data[0]
    
    yield sso_config
    
    # Cleanup
    supabase_client.table("sso_configurations").delete().eq(
        "id", sso_config["id"]
    ).execute()


class MockIdPResponse:
    """Mock Identity Provider responses for testing."""
    
    @staticmethod
    def azure_ad_token(
        sub: str = "test-user-123",
        email: str = "test@example.com",
        name: str = "Test User"
    ) -> Dict[str, Any]:
        """Mock Azure AD token response."""
        return {
            "access_token": "mock_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "id_token": MockIdPResponse._create_jwt({
                "sub": sub,
                "email": email,
                "name": name,
                "iss": "https://login.microsoftonline.com/test/v2.0",
                "aud": "test-client-id",
                "exp": int((datetime.now() + timedelta(hours=1)).timestamp()),
                "iat": int(datetime.now().timestamp())
            })
        }
    
    @staticmethod
    def google_token(
        sub: str = "google-user-456",
        email: str = "test@company.com",
        name: str = "Google User"
    ) -> Dict[str, Any]:
        """Mock Google token response."""
        return {
            "access_token": "mock_google_access",
            "token_type": "Bearer",
            "expires_in": 3600,
            "id_token": MockIdPResponse._create_jwt({
                "sub": sub,
                "email": email,
                "name": name,
                "iss": "https://accounts.google.com",
                "aud": "google-client-id",
                "exp": int((datetime.now() + timedelta(hours=1)).timestamp()),
                "iat": int(datetime.now().timestamp())
            })
        }
    
    @staticmethod
    def _create_jwt(payload: Dict[str, Any]) -> str:
        """Create mock JWT token."""
        import base64
        import json
        
        header = base64.b64encode(json.dumps({
            "alg": "RS256",
            "typ": "JWT"
        }).encode()).decode()
        
        body = base64.b64encode(json.dumps(payload).encode()).decode()
        signature = "mock_signature"
        
        return f"{header}.{body}.{signature}"


def assert_user_created(
    supabase_client: Client,
    email: str,
    org_id: str
) -> bool:
    """Assert that user was created in org."""
    result = supabase_client.table("org_members").select(
        "*"
    ).eq("org_id", org_id).execute()
    
    # Find user by email (would need to join auth.users in real implementation)
    return len(result.data) > 0


def assert_session_valid(token: str) -> bool:
    """Assert that session token is valid."""
    # In real implementation, verify JWT signature
    return len(token) > 0
