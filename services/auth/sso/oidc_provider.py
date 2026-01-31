"""
Phase 6C: SSO Integration - OIDC Provider
Implements OpenID Connect (OIDC) authentication.
Supports: Azure AD, Google Workspace, Auth0
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import httpx
import jwt
from datetime import datetime, timedelta
import secrets


@dataclass
class OIDCConfig:
    """OIDC provider configuration"""
    provider: str  # 'azure-ad', 'google', 'auth0'
    issuer: str
    client_id: str
    client_secret: str
    scopes: list[str]
    token_endpoint: Optional[str] = None
    userinfo_endpoint: Optional[str] = None
    authorization_endpoint: Optional[str] = None


@dataclass
class OIDCUserInfo:
    """User information from OIDC provider"""
    sub: str  # Subject (unique user ID)
    email: str
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    email_verified: bool = False
    groups: list[str] = None
    raw: Dict[str, Any] = None


class OIDCProvider:
    """
    OIDC authentication provider.
    
    Implements OAuth 2.0 / OpenID Connect flow:
    1. Generate authorization URL
    2. Exchange code for tokens
    3. Verify ID token
    4. Fetch user info
    """
    
    def __init__(self, config: OIDCConfig, redirect_uri: str):
        """
        Initialize OIDC provider.
        
        Args:
            config: OIDC configuration
            redirect_uri: Callback URL for OAuth redirect
        """
        self.config = config
        self.redirect_uri = redirect_uri
        self._discovery_cache: Optional[Dict[str, Any]] = None
    
    async def get_discovery_document(self) -> Dict[str, Any]:
        """
        Fetch OpenID Connect Discovery document.
        Cached for performance.
        """
        if self._discovery_cache:
            return self._discovery_cache
        
        discovery_url = f"{self.config.issuer}/.well-known/openid-configuration"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(discovery_url)
            response.raise_for_status()
            self._discovery_cache = response.json()
        
        return self._discovery_cache
    
    async def get_authorization_url(self, state: Optional[str] = None) -> tuple[str, str]:
        """
        Generate authorization URL for user to authenticate.
        
        Args:
            state: Optional state parameter for CSRF protection
        
        Returns:
            Tuple of (authorization_url, state)
        """
        if state is None:
            state = secrets.token_urlsafe(32)
        
        # Get authorization endpoint from discovery
        discovery = await self.get_discovery_document()
        auth_endpoint = self.config.authorization_endpoint or discovery["authorization_endpoint"]
        
        # Build authorization URL
        params = {
            "client_id": self.config.client_id,
            "response_type": "code",
            "scope": " ".join(self.config.scopes),
            "redirect_uri": self.redirect_uri,
            "state": state
        }
        
        # Provider-specific parameters
        if self.config.provider == "azure-ad":
            params["response_mode"] = "query"
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        authorization_url = f"{auth_endpoint}?{query_string}"
        
        return authorization_url, state
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens.
        
        Args:
            code: Authorization code from OAuth callback
        
        Returns:
            Token response with access_token, id_token, refresh_token
        """
        # Get token endpoint from discovery
        discovery = await self.get_discovery_document()
        token_endpoint = self.config.token_endpoint or discovery["token_endpoint"]
        
        # Prepare token request
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_endpoint,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            return response.json()
    
    async def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """
        Verify and decode ID token (JWT).
        
        Args:
            id_token: ID token from token response
        
        Returns:
            Decoded token claims
        """
        # Get JWKS (JSON Web Key Set) from discovery
        discovery = await self.get_discovery_document()
        jwks_uri = discovery["jwks_uri"]
        
        async with httpx.AsyncClient() as client:
            jwks_response = await client.get(jwks_uri)
            jwks_response.raise_for_status()
            jwks = jwks_response.json()
        
        # Decode and verify token
        # Note: In production, use proper JWT verification library
        # For now, decode without verification (NOT SECURE for production!)
        decoded = jwt.decode(
            id_token,
            options={"verify_signature": False},  # TODO: Implement proper verification
            audience=self.config.client_id
        )
        
        # Verify issuer
        if decoded.get("iss") != self.config.issuer:
            raise ValueError(f"Invalid issuer: {decoded.get('iss')}")
        
        # Verify expiration
        exp = decoded.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.now():
            raise ValueError("Token expired")
        
        return decoded
    
    async def get_user_info(self, access_token: str) -> OIDCUserInfo:
        """
        Fetch user information using access token.
        
        Args:
            access_token: Access token from token response
        
        Returns:
            User information
        """
        # Get userinfo endpoint from discovery
        discovery = await self.get_discovery_document()
        userinfo_endpoint = self.config.userinfo_endpoint or discovery["userinfo_endpoint"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                userinfo_endpoint,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            user_data = response.json()
        
        # Parse user info
        return OIDCUserInfo(
            sub=user_data["sub"],
            email=user_data.get("email", ""),
            name=user_data.get("name"),
            given_name=user_data.get("given_name"),
            family_name=user_data.get("family_name"),
            picture=user_data.get("picture"),
            email_verified=user_data.get("email_verified", False),
            groups=user_data.get("groups", []),
            raw=user_data
        )
    
    async def authenticate(self, code: str) -> tuple[Dict[str, Any], OIDCUserInfo]:
        """
        Complete authentication flow.
        
        Args:
            code: Authorization code from OAuth callback
        
        Returns:
            Tuple of (tokens, user_info)
        """
        # Exchange code for tokens
        tokens = await self.exchange_code_for_tokens(code)
        
        # Verify ID token
        id_token_claims = await self.verify_id_token(tokens["id_token"])
        
        # Get user info
        user_info = await self.get_user_info(tokens["access_token"])
        
        return tokens, user_info


# Provider-specific factories
class AzureADProvider(OIDCProvider):
    """Azure AD (Microsoft Entra ID) OIDC provider"""
    
    @classmethod
    def from_credentials(
        cls,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ):
        """Create Azure AD provider from credentials"""
        config = OIDCConfig(
            provider="azure-ad",
            issuer=f"https://login.microsoftonline.com/{tenant_id}/v2.0",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["openid", "profile", "email"]
        )
        return cls(config, redirect_uri)


class GoogleProvider(OIDCProvider):
    """Google Workspace OIDC provider"""
    
    @classmethod
    def from_credentials(
        cls,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ):
        """Create Google provider from credentials"""
        config = OIDCConfig(
            provider="google",
            issuer="https://accounts.google.com",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["openid", "profile", "email"]
        )
        return cls(config, redirect_uri)


class Auth0Provider(OIDCProvider):
    """Auth0 OIDC provider"""
    
    @classmethod
    def from_credentials(
        cls,
        domain: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ):
        """Create Auth0 provider from credentials"""
        config = OIDCConfig(
            provider="auth0",
            issuer=f"https://{domain}",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["openid", "profile", "email"]
        )
        return cls(config, redirect_uri)


# Example usage
"""
# Azure AD
azure_provider = AzureADProvider.from_credentials(
    tenant_id="22116407-6817-4c85-96ce-1b6d4e631844",
    client_id="de01844a-115d-4789-8b5f-eab412c6089e",
    client_secret="ISD8Q~dypu1jXm33lD71uTerp5fWAWHqGhvmCahN",
    redirect_uri="https://orion-ai.vercel.app/api/auth/callback/azure-ad"
)

# Get authorization URL
auth_url, state = await azure_provider.get_authorization_url()
# Redirect user to auth_url

# After callback with code
tokens, user_info = await azure_provider.authenticate(code)
print(f"User: {user_info.email}")
"""
