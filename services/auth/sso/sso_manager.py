"""
Phase 6C: SSO Integration - SSO Manager
Centralized SSO configuration and authentication manager.
"""

from typing import Optional, Dict, Any, Union
from enum import Enum
from supabase import Client

from .oidc_provider import (
    OIDCProvider, OIDCUserInfo, OIDCConfig,
    AzureADProvider, GoogleProvider, Auth0Provider
)
from .saml_provider import (
    SAMLProvider, SAMLUserInfo, SAMLConfig,
    OneLoginProvider, OktaProvider
)
from .jit_provisioning import JITProvisioner, JITConfig


class SSOProtocol(str, Enum):
    """SSO Protocol types"""
    OIDC = "oidc"
    SAML = "saml"


class SSOManager:
    """
    Centralized SSO management.
    
    Features:
    - Load SSO configuration from database
    - Initialize provider (OIDC or SAML)
    - Handle authentication flow
    - JIT user provisioning
    - Track login events
    """
    
    def __init__(self, supabase_client: Client, base_url: str):
        """
        Initialize SSO Manager.
        
        Args:
            supabase_client: Supabase client
            base_url: Base URL for callbacks (e.g., https://orion-ai.vercel.app)
        """
        self.client = supabase_client
        self.base_url = base_url
        self.jit_provisioner = JITProvisioner(supabase_client)
    
    async def get_sso_config(
        self,
        org_id: str,
        provider: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get SSO configuration for organization and provider.
        
        Args:
            org_id: Organization ID
            provider: Provider name (azure-ad, google, auth0, onelogin, okta)
        
        Returns:
            SSO configuration dict or None
        """
        response = self.client.table("sso_configurations").select("*").eq(
            "org_id", org_id
        ).eq("provider", provider).eq("enabled", True).execute()
        
        if not response.data:
            return None
        
        return response.data[0]
    
    async def initialize_oidc_provider(
        self,
        config: Dict[str, Any]
    ) -> OIDCProvider:
        """Initialize OIDC provider from config"""
        provider_name = config["provider"]
        callback_path = f"/api/auth/callback/{provider_name}"
        redirect_uri = f"{self.base_url}{callback_path}"
        
        if provider_name == "azure-ad":
            # Extract tenant ID from issuer
            issuer = config["oidc_issuer"]
            tenant_id = issuer.split("/")[3]
            
            return AzureADProvider.from_credentials(
                tenant_id=tenant_id,
                client_id=config["oidc_client_id"],
                client_secret=config["oidc_client_secret"],
                redirect_uri=redirect_uri
            )
        
        elif provider_name == "google":
            return GoogleProvider.from_credentials(
                client_id=config["oidc_client_id"],
                client_secret=config["oidc_client_secret"],
                redirect_uri=redirect_uri
            )
        
        elif provider_name == "auth0":
            # Extract domain from issuer
            issuer = config["oidc_issuer"]
            domain = issuer.replace("https://", "").replace("http://", "")
            
            return Auth0Provider.from_credentials(
                domain=domain,
                client_id=config["oidc_client_id"],
                client_secret=config["oidc_client_secret"],
                redirect_uri=redirect_uri
            )
        
        else:
            # Generic OIDC provider
            oidc_config = OIDCConfig(
                provider=provider_name,
                issuer=config["oidc_issuer"],
                client_id=config["oidc_client_id"],
                client_secret=config["oidc_client_secret"],
                scopes=config.get("oidc_scopes", ["openid", "profile", "email"]),
                token_endpoint=config.get("oidc_token_endpoint"),
                userinfo_endpoint=config.get("oidc_userinfo_endpoint")
            )
            return OIDCProvider(oidc_config, redirect_uri)
    
    async def initialize_saml_provider(
        self,
        config: Dict[str, Any]
    ) -> SAMLProvider:
        """Initialize SAML provider from config"""
        provider_name = config["provider"]
        callback_path = f"/api/auth/callback/{provider_name}"
        acs_url = f"{self.base_url}{callback_path}"
        sp_entity_id = self.base_url
        
        if provider_name == "onelogin":
            return OneLoginProvider.from_credentials(
                entity_id=config["saml_entity_id"],
                sso_url=config["saml_sso_url"],
                slo_url=config.get("saml_slo_url"),
                certificate=config["saml_certificate"],
                sp_entity_id=sp_entity_id,
                acs_url=acs_url
            )
        
        elif provider_name == "okta":
            return OktaProvider.from_credentials(
                entity_id=config["saml_entity_id"],
                sso_url=config["saml_sso_url"],
                certificate=config["saml_certificate"],
                sp_entity_id=sp_entity_id,
                acs_url=acs_url
            )
        
        else:
            # Generic SAML provider
            saml_config = SAMLConfig(
                provider=provider_name,
                entity_id=config["saml_entity_id"],
                sso_url=config["saml_sso_url"],
                slo_url=config.get("saml_slo_url"),
                certificate=config["saml_certificate"],
                sign_requests=config.get("saml_sign_requests", False),
                attribute_mapping=config.get("saml_attribute_mapping")
            )
            return SAMLProvider(saml_config, sp_entity_id, acs_url)
    
    async def start_authentication(
        self,
        org_id: str,
        provider: str
    ) -> tuple[str, str]:
        """
        Start SSO authentication flow.
        
        Args:
            org_id: Organization ID
            provider: Provider name
        
        Returns:
            Tuple of (redirect_url, state/request_id)
        """
        # Get SSO config
        config = await self.get_sso_config(org_id, provider)
        
        if not config:
            raise Exception(f"SSO not configured for org {org_id} provider {provider}")
        
        protocol = config["protocol"]
        
        if protocol == SSOProtocol.OIDC:
            # Initialize OIDC provider
            oidc_provider = await self.initialize_oidc_provider(config)
            
            # Get authorization URL
            auth_url, state = await oidc_provider.get_authorization_url()
            
            return auth_url, state
        
        elif protocol == SSOProtocol.SAML:
            # Initialize SAML provider
            saml_provider = await self.initialize_saml_provider(config)
            
            # Generate SAML AuthnRequest
            redirect_url, request_id = saml_provider.generate_authn_request()
            
            return redirect_url, request_id
        
        else:
            raise Exception(f"Unsupported protocol: {protocol}")
    
    async def complete_authentication(
        self,
        org_id: str,
        provider: str,
        code: Optional[str] = None,
        saml_response: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete SSO authentication and provision user.
        
        Args:
            org_id: Organization ID
            provider: Provider name
            code: Authorization code (OIDC)
            saml_response: SAML Response (SAML)
        
        Returns:
            Authentication result with user info
        """
        # Get SSO config
        config = await self.get_sso_config(org_id, provider)
        
        if not config:
            raise Exception(f"SSO not configured for org {org_id} provider {provider}")
        
        protocol = config["protocol"]
        user_info = None
        
        try:
            if protocol == SSOProtocol.OIDC:
                # Initialize OIDC provider
                oidc_provider = await self.initialize_oidc_provider(config)
                
                # Complete authentication
                tokens, user_info = await oidc_provider.authenticate(code)
                
                # JIT provision user
                jit_config = self._get_jit_config(config)
                result = await self.jit_provisioner.provision_oidc_user(
                    org_id, user_info, jit_config
                )
            
            elif protocol == SSOProtocol.SAML:
                # Initialize SAML provider
                saml_provider = await self.initialize_saml_provider(config)
                
                # Parse SAML Response
                user_info = saml_provider.parse_saml_response(saml_response)
                
                # JIT provision user
                jit_config = self._get_jit_config(config)
                result = await self.jit_provisioner.provision_saml_user(
                    org_id, user_info, jit_config
                )
            
            else:
                raise Exception(f"Unsupported protocol: {protocol}")
            
            # Log successful login event
            await self._log_login_event(
                org_id=org_id,
                user_id=result["user_id"],
                provider=provider,
                protocol=protocol,
                status="success"
            )
            
            return result
        
        except Exception as e:
            # Log failed login event
            await self._log_login_event(
                org_id=org_id,
                user_id=None,
                provider=provider,
                protocol=protocol,
                status="failure",
                error_message=str(e)
            )
            
            raise
    
    def _get_jit_config(self, sso_config: Dict[str, Any]) -> JITConfig:
        """Extract JIT configuration from SSO config"""
        return JITConfig(
            enabled=sso_config.get("jit_enabled", True),
            default_role_id=sso_config.get("jit_default_role_id"),
            group_mapping=sso_config.get("jit_group_mapping", {}),
            auto_create_users=True,
            auto_update_profile=True
        )
    
    async def _log_login_event(
        self,
        org_id: str,
        user_id: Optional[str],
        provider: str,
        protocol: str,
        status: str,
        error_message: Optional[str] = None
    ) -> None:
        """Log SSO login event for audit"""
        self.client.table("sso_login_events").insert({
            "org_id": org_id,
            "user_id": user_id,
            "provider": provider,
            "protocol": protocol,
            "status": status,
            "error_message": error_message
        }).execute()


# Example usage with FastAPI
"""
from fastapi import FastAPI, Request, HTTPException
from services.auth.sso.sso_manager import SSOManager

app = FastAPI()
sso_manager = SSOManager(supabase_client, "https://orion-ai.vercel.app")

@app.get("/api/auth/sso/{provider}")
async def sso_login(provider: str, org_id: str):
    '''Start SSO login flow'''
    try:
        redirect_url, state = await sso_manager.start_authentication(org_id, provider)
        
        # Store state in session
        # ...
        
        return {"redirect_url": redirect_url}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/auth/callback/{provider}")
async def sso_callback(provider: str, org_id: str, code: str = None, SAMLResponse: str = None):
    '''Handle SSO callback'''
    try:
        result = await sso_manager.complete_authentication(
            org_id=org_id,
            provider=provider,
            code=code,
            saml_response=SAMLResponse
        )
        
        # Create session/JWT for user
        # ...
        
        return result
    except Exception as e:
        raise HTTPException(500, str(e))
"""
