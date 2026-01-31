"""
Shared Test Fixtures for Integration Tests

Provides fixtures for Supabase connection, test organizations, and test users.
"""

import os
import pytest
import asyncio
from typing import Dict, Any
from datetime import datetime
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
    """
    Create Supabase client for tests.
    Uses SERVICE_ROLE_KEY to bypass RLS for test setup.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        pytest.skip("Supabase credentials not configured")
    
    return create_client(url, key)


@pytest.fixture
def test_organization(supabase_client: Client) -> Dict[str, Any]:
    """
    Create a test organization.
    Automatically cleaned up after test.
    """
    timestamp = datetime.now().timestamp()
    org_data = {
        "name": f"Test Organization {timestamp}",
        "slug": f"test-org-{int(timestamp)}",
        "tier": "professional",
        "isolation_level": "row",
        "quotas": {
            "monthlyApiCalls": 100000,
            "maxUsers": 50,
            "maxConnectors": 25
        },
        "billing_status": "active"
    }
    
    result = supabase_client.table("organizations").insert(org_data).execute()
    org = result.data[0]
    
    yield org
    
    # Cleanup: Delete test organization
    try:
        supabase_client.table("organizations").delete().eq("id", org["id"]).execute()
    except Exception as e:
        print(f"Warning: Failed to cleanup test org: {e}")


@pytest.fixture
def test_user(supabase_client: Client, test_organization: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a test user in the organization.
    Note: This creates an org_member record, not an auth.users record.
    """
    member_data = {
        "org_id": test_organization["id"],
        "user_id": f"test-user-{datetime.now().timestamp()}",
        "role": "member"
    }
    
    result = supabase_client.table("org_members").insert(member_data).execute()
    member = result.data[0]
    
    yield member
    
    # Cleanup
    try:
        supabase_client.table("org_members").delete().eq("id", member["id"]).execute()
    except Exception as e:
        print(f"Warning: Failed to cleanup test user: {e}")


@pytest.fixture
def test_admin(supabase_client: Client, test_organization: Dict[str, Any]) -> Dict[str, Any]:
    """Create a test admin user."""
    admin_data = {
        "org_id": test_organization["id"],
        "user_id": f"test-admin-{datetime.now().timestamp()}",
        "role": "admin"
    }
    
    result = supabase_client.table("org_members").insert(admin_data).execute()
    admin = result.data[0]
    
    yield admin
    
    # Cleanup
    try:
        supabase_client.table("org_members").delete().eq("id", admin["id"]).execute()
    except Exception as e:
        print(f"Warning: Failed to cleanup test admin: {e}")


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
        "jit_enabled": True,
        "jit_default_role_id": None
    }
    
    result = supabase_client.table("sso_configurations").insert(config).execute()
    sso_config = result.data[0]
    
    yield sso_config
    
    # Cleanup
    try:
        supabase_client.table("sso_configurations").delete().eq(
            "id", sso_config["id"]
        ).execute()
    except Exception as e:
        print(f"Warning: Failed to cleanup SSO config: {e}")


@pytest.fixture
def api_base_url() -> str:
    """Get API base URL from environment."""
    return os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture
def test_api_key() -> str:
    """Get test API key from environment."""
    return os.getenv("TEST_API_KEY", "test-api-key-for-integration-tests")


def cleanup_test_data(supabase_client: Client):
    """
    Cleanup all test data.
    Call this at the end of test session.
    """
    # Find and delete test organizations
    try:
        orgs = supabase_client.table("organizations").select(
            "id"
        ).like("slug", "test-org-%").execute()
        
        for org in orgs.data:
            supabase_client.table("organizations").delete().eq(
                "id", org["id"]
            ).execute()
        
        print(f"Cleaned up {len(orgs.data)} test organizations")
    except Exception as e:
        print(f"Warning: Cleanup failed: {e}")


@pytest.fixture(scope="session", autouse=True)
def cleanup(request, supabase_client):
    """Auto-cleanup at end of test session."""
    def finalizer():
        cleanup_test_data(supabase_client)
    
    request.addfinalizer(finalizer)
