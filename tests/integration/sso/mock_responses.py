"""
Mock Identity Provider Responses for Testing
"""

from typing import Dict, Any
from datetime import datetime, timedelta
import base64
import json


class MockAzureAD:
    """Mock Azure AD responses."""
    
    @staticmethod
    def authorization_url(
        client_id: str,
        redirect_uri: str,
        state: str
    ) -> str:
        """Mock Azure AD authorization URL."""
        return (
            f"https://login.microsoftonline.com/test-tenant/oauth2/v2.0/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope=openid profile email"
            f"&state={state}"
        )
    
    @staticmethod
    def token_response(
        sub: str = "azure-user-123",
        email: str = "test@microsoft.com",
        name: str = "Azure Test User"
    ) -> Dict[str, Any]:
        """Mock Azure AD token response."""
        return {
            "token_type": "Bearer",
            "expires_in": 3600,
            "access_token": f"mock_azure_access_{sub}",
            "refresh_token": f"mock_azure_refresh_{sub}",
            "id_token": create_mock_jwt({
                "iss": "https://login.microsoftonline.com/test-tenant/v2.0",
                "sub": sub,
                "aud": "azure-client-id",
                "exp": int((datetime.now() + timedelta(hours=1)).timestamp()),
                "iat": int(datetime.now().timestamp()),
                "email": email,
                "name": name,
                "preferred_username": email,
                "tid": "test-tenant-id"
            })
        }
    
    @staticmethod
    def user_info(email: str, name: str) -> Dict[str, Any]:
        """Mock Azure AD user info."""
        return {
            "sub": f"azure-{email}",
            "email": email,
            "name": name,
            "preferred_username": email,
            "given_name": name.split()[0],
            "family_name": name.split()[-1]
        }


class MockGoogle:
    """Mock Google OAuth responses."""
    
    @staticmethod
    def authorization_url(
        client_id: str,
        redirect_uri: str,
        state: str
    ) -> str:
        """Mock Google authorization URL."""
        return (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope=openid email profile"
            f"&state={state}"
        )
    
    @staticmethod
    def token_response(
        sub: str = "google-user-456",
        email: str = "test@company.com",
        name: str = "Google Test User"
    ) -> Dict[str, Any]:
        """Mock Google token response."""
        return {
            "access_token": f"mock_google_access_{sub}",
            "expires_in": 3600,
            "token_type": "Bearer",
            "scope": "openid email profile",
            "id_token": create_mock_jwt({
                "iss": "https://accounts.google.com",
                "sub": sub,
                "aud": "google-client-id",
                "exp": int((datetime.now() + timedelta(hours=1)).timestamp()),
                "iat": int(datetime.now().timestamp()),
                "email": email,
                "email_verified": True,
                "name": name,
                "picture": f"https://lh3.googleusercontent.com/{sub}",
                "given_name": name.split()[0],
                "family_name": name.split()[-1],
                "hd": "company.com"
            })
        }


class MockAuth0:
    """Mock Auth0 responses."""
    
    @staticmethod
    def authorization_url(
        domain: str,
        client_id: str,
        redirect_uri: str,
        state: str
    ) -> str:
        """Mock Auth0 authorization URL."""
        return (
            f"https://{domain}/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope=openid profile email"
            f"&state={state}"
        )
    
    @staticmethod
    def token_response(
        sub: str = "auth0|user789",
        email: str = "test@auth0.com",
        name: str = "Auth0 Test User"
    ) -> Dict[str, Any]:
        """Mock Auth0 token response."""
        return {
            "access_token": f"mock_auth0_access_{sub}",
            "id_token": create_mock_jwt({
                "iss": "https://test-domain.auth0.com/",
                "sub": sub,
                "aud": "auth0-client-id",
                "exp": int((datetime.now() + timedelta(hours=1)).timestamp()),
                "iat": int(datetime.now().timestamp()),
                "email": email,
                "email_verified": True,
                "name": name,
                "nickname": email.split("@")[0],
                "picture": f"https://s.gravatar.com/avatar/{sub}"
            }),
            "token_type": "Bearer",
            "expires_in": 3600
        }


class MockOneLogin:
    """Mock OneLogin SAML responses."""
    
    @staticmethod
    def saml_response(
        email: str = "test@onelogin.com",
        name: str = "OneLogin Test User"
    ) -> str:
        """Mock OneLogin SAML response."""
        saml_assertion = f"""
        <saml:Assertion>
            <saml:Subject>
                <saml:NameID>{email}</saml:NameID>
            </saml:Subject>
            <saml:AttributeStatement>
                <saml:Attribute Name="email">
                    <saml:AttributeValue>{email}</saml:AttributeValue>
                </saml:Attribute>
                <saml:Attribute Name="firstName">
                    <saml:AttributeValue>{name.split()[0]}</saml:AttributeValue>
                </saml:Attribute>
                <saml:Attribute Name="lastName">
                    <saml:AttributeValue>{name.split()[-1]}</saml:AttributeValue>
                </saml:Attribute>
            </saml:AttributeStatement>
        </saml:Assertion>
        """
        
        return base64.b64encode(saml_assertion.encode()).decode()


def create_mock_jwt(payload: Dict[str, Any]) -> str:
    """Create a mock JWT token (not cryptographically signed)."""
    header = {
        "alg": "RS256",
        "typ": "JWT",
        "kid": "mock-key-id"
    }
    
    header_b64 = base64.urlsafe_b64encode(
        json.dumps(header).encode()
    ).decode().rstrip("=")
    
    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).decode().rstrip("=")
    
    signature = "mock_signature_not_real"
    
    return f"{header_b64}.{payload_b64}.{signature}"
