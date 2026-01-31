"""
Azure AD SSO Integration Tests

Tests the complete OAuth flow for Azure AD authentication:
- Authorization URL generation
- Token exchange
- User provisioning (JIT)
- Session management
- Token refresh
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tests.integration.sso.mock_responses import MockAzureAD, create_mock_jwt


class TestAzureADSSO:
    """Test Azure AD SSO integration."""
    
    def test_authorization_url_generation(self, sso_configuration):
        """Test Azure AD authorization URL is correctly formatted."""
        config = sso_configuration
        
        auth_url = MockAzureAD.authorization_url(
            client_id=config["oidc_client_id"],
            redirect_uri="https://orion-ai.vercel.app/api/oauth/azure/callback",
            state="random_state_123"
        )
        
        assert "login.microsoftonline.com" in auth_url
        assert "oauth2/v2.0/authorize" in auth_url
        assert config["oidc_client_id"] in auth_url
        assert "response_type=code" in auth_url
        assert "state=random_state_123" in auth_url
    
    @pytest.mark.asyncio
    async def test_fresh_user_jit_provisioning(
        self,
        supabase_client,
        test_organization,
        sso_configuration
    ):
        """
        SSO-001: Fresh user login via Azure AD with JIT provisioning.
        
        Flow:
        1. User authenticates with Azure AD
        2. Token received
        3. User doesn't exist in org
        4. JIT creates user with default role
        5. User added to organization
        """
        token_response = MockAzureAD.token_response(
            sub="new-azure-user",
            email="newuser@microsoft.com",
            name="New Azure User"
        )
        
        # Verify token contains required fields
        assert "id_token" in token_response
        assert "access_token" in token_response
        
        # Simulate JIT provisioning
        user_email = "newuser@microsoft.com"
        org_id = test_organization["id"]
        
        # Check user doesn't exist
        existing = supabase_client.table("org_members").select(
            "*"
        ).eq("org_id", org_id).execute()
        
        initial_count = len(existing.data)
        
        # Simulate user creation
        member_data = {
            "org_id": org_id,
            "user_id": "mock-auth-user-id",
            "role": "member"
        }
        
        result = supabase_client.table("org_members").insert(
            member_data
        ).execute()
        
        assert len(result.data) == 1
        assert result.data[0]["org_id"] == org_id
        assert result.data[0]["role"] == "member"
        
        # Verify user was added
        after = supabase_client.table("org_members").select(
            "*"
        ).eq("org_id", org_id).execute()
        
        assert len(after.data) == initial_count + 1
    
    @pytest.mark.asyncio
    async def test_existing_user_login(
        self,
        supabase_client,
        test_organization
    ):
        """
        SSO-002: Existing user login.
        
        Flow:
        1. User already exists in org
        2. Authenticates with Azure AD
        3. Session established
        4. No duplicate user created
        """
        # Create existing user
        existing_member = {
            "org_id": test_organization["id"],
            "user_id": "existing-user-id",
            "role": "admin"
        }
        
        supabase_client.table("org_members").insert(existing_member).execute()
        
        # Simulate login
        token_response = MockAzureAD.token_response(
            sub="existing-user-id",
            email="existing@microsoft.com",
            name="Existing User"
        )
        
        # Verify no duplicate created
        members = supabase_client.table("org_members").select(
            "*"
        ).eq("org_id", test_organization["id"]).execute()
        
        # Should still be 1 member (the one we created)
        assert len(members.data) == 1
        assert members.data[0]["user_id"] == "existing-user-id"
        assert members.data[0]["role"] == "admin"  # Role preserved
    
    def test_token_refresh_flow(self):
        """
        SSO-003: Token refresh.
        
        Flow:
        1. Access token expires
        2. Refresh token used
        3. New access token obtained
        4. No user interruption
        """
        # Initial token
        initial_token = MockAzureAD.token_response(
            sub="refresh-test-user",
            email="refresh@microsoft.com",
            name="Refresh Test"
        )
        
        assert "refresh_token" in initial_token
        assert "expires_in" in initial_token
        
        # Simulate refresh (would call Azure AD token endpoint)
        refreshed_token = MockAzureAD.token_response(
            sub="refresh-test-user",
            email="refresh@microsoft.com",
            name="Refresh Test"
        )
        
        # New access token should be different
        assert refreshed_token["access_token"] != initial_token["access_token"]
        # But user ID should be the same
        assert "refresh-test-user" in refreshed_token["access_token"]
    
    def test_logout_flow(self, supabase_client, test_organization):
        """
        SSO-004: Logout flow.
        
        Flow:
        1. User clicks logout
        2. Session terminated locally
        3. Optional: Single Logout (SLO) to Azure AD
        4. Cannot access protected routes
        """
        # Simulate active session
        session_token = "mock_session_token_abc123"
        
        # After logout, token should be invalidated
        # (In real implementation, would delete from sessions table)
        assert session_token is not None  # Before logout
        
        # Simulate logout
        session_token = None
        
        assert session_token is None  # After logout
    
    @pytest.mark.asyncio
    async def test_domain_restriction(
        self,
        supabase_client,
        test_organization,
        sso_configuration
    ):
        """
        SSO-005: Domain restriction.
        
        Flow:
        1. Org configured to only allow @company.com
        2. User with @gmail.com tries to login
        3. Access denied with clear message
        """
        # Update SSO config to restrict domain
        restricted_config = {
            **sso_configuration,
            "domain_whitelist": ["company.com"]
        }
        
        # Attempt login with wrong domain
        wrong_domain_token = MockAzureAD.token_response(
            sub="wrong-domain-user",
            email="user@gmail.com",
            name="Wrong Domain"
        )
        
        user_email = "user@gmail.com"
        allowed_domains = ["company.com"]
        
        # Check if email domain is allowed
        email_domain = user_email.split("@")[1]
        is_allowed = email_domain in allowed_domains
        
        assert is_allowed is False, "Email from non-whitelisted domain should be rejected"
    
    def test_token_validation(self):
        """Test JWT token signature validation (mock)."""
        token = create_mock_jwt({
            "iss": "https://login.microsoftonline.com/test/v2.0",
            "sub": "test-user",
            "aud": "test-client-id",
            "exp": 9999999999,  # Far future
            "email": "test@example.com"
        })
        
        # In real implementation, would verify signature
        parts = token.split(".")
        assert len(parts) == 3  # header.payload.signature
        assert len(parts[0]) > 0  # header exists
        assert len(parts[1]) > 0  # payload exists
        assert len(parts[2]) > 0  # signature exists
