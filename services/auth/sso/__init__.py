"""
Phase 6C: SSO Authentication Services
Provides SSO authentication with OIDC and SAML support.
"""

from .oidc_provider import (
    OIDCProvider, OIDCConfig, OIDCUserInfo,
    AzureADProvider, GoogleProvider, Auth0Provider
)
from .saml_provider import (
    SAMLProvider, SAMLConfig, SAMLUserInfo,
    OneLoginProvider, OktaProvider
)
from .jit_provisioning import JITProvisioner, JITConfig
from .sso_manager import SSOManager, SSOProtocol

__all__ = [
    # OIDC
    "OIDCProvider",
    "OIDCConfig",
    "OIDCUserInfo",
    "AzureADProvider",
    "GoogleProvider",
    "Auth0Provider",
    # SAML
    "SAMLProvider",
    "SAMLConfig",
    "SAMLUserInfo",
    "OneLoginProvider",
    "OktaProvider",
    # JIT Provisioning
    "JITProvisioner",
    "JITConfig",
    # Manager
    "SSOManager",
    "SSOProtocol"
]
