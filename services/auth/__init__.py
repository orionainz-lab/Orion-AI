"""
Phase 6C: Authentication Services
Provides SSO and authentication capabilities.
"""

from .sso import (
    # Managers
    SSOManager,
    SSOProtocol,
    # OIDC
    OIDCProvider,
    OIDCConfig,
    OIDCUserInfo,
    AzureADProvider,
    GoogleProvider,
    Auth0Provider,
    # SAML
    SAMLProvider,
    SAMLConfig,
    SAMLUserInfo,
    OneLoginProvider,
    OktaProvider,
    # JIT
    JITProvisioner,
    JITConfig
)

__all__ = [
    "SSOManager",
    "SSOProtocol",
    "OIDCProvider",
    "OIDCConfig",
    "OIDCUserInfo",
    "AzureADProvider",
    "GoogleProvider",
    "Auth0Provider",
    "SAMLProvider",
    "SAMLConfig",
    "SAMLUserInfo",
    "OneLoginProvider",
    "OktaProvider",
    "JITProvisioner",
    "JITConfig"
]
