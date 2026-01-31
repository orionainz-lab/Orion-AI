"""
Phase 6C: Multi-Tenancy - Tenant Resolution
Middleware to identify and resolve tenant context from requests.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .tenant_manager import TenantManager, Organization, Tier


@dataclass
class TenantContext:
    """
    Tenant context resolved from request.
    Attached to request.state for downstream use.
    """
    org_id: str
    org_slug: str
    org_name: str
    tier: Tier
    quotas: Dict[str, Any]
    settings: Dict[str, Any]
    user_id: Optional[str] = None
    user_role: Optional[str] = None


class TenantResolver:
    """
    Resolves tenant context from incoming requests.
    
    Resolution order:
    1. Custom domain (custom.company.com)
    2. Subdomain (company.orion-ai.com)
    3. API key (x-api-key header)
    4. JWT token (Authorization header)
    5. Query parameter (?org_id=xxx)
    """
    
    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
        self.security = HTTPBearer(auto_error=False)
    
    async def resolve_from_request(self, request: Request) -> TenantContext:
        """
        Main resolution method - tries all strategies in order.
        
        Args:
            request: FastAPI Request object
        
        Returns:
            TenantContext with org and user info
        
        Raises:
            HTTPException: If tenant cannot be resolved
        """
        # Try custom domain
        org = await self._resolve_from_domain(request)
        
        # Try subdomain
        if not org:
            org = await self._resolve_from_subdomain(request)
        
        # Try API key
        if not org:
            org = await self._resolve_from_api_key(request)
        
        # Try JWT token
        if not org:
            org, user_id = await self._resolve_from_jwt(request)
        
        # Try query parameter (development/testing only)
        if not org:
            org = await self._resolve_from_query(request)
        
        if not org:
            raise HTTPException(
                status_code=401,
                detail="Tenant not found. Please provide valid credentials or domain."
            )
        
        # Build tenant context
        context = TenantContext(
            org_id=org.id,
            org_slug=org.slug,
            org_name=org.name,
            tier=org.tier,
            quotas=org.quotas,
            settings=org.settings,
            user_id=getattr(org, '_user_id', None)
        )
        
        # Attach to request state
        request.state.tenant = context
        
        return context
    
    async def _resolve_from_domain(self, request: Request) -> Optional[Organization]:
        """
        Resolve from custom domain.
        Example: integrations.company.com -> company org
        """
        host = request.headers.get("host", "").split(":")[0]
        
        # Skip if it's the main domain
        if "orion-ai.com" in host or "localhost" in host or "127.0.0.1" in host:
            return None
        
        # Look up organization by custom domain
        response = self.tenant_manager.client.table("domain_verifications").select(
            "org_id, organizations(*)"
        ).eq("domain", host).eq("verification_status", "verified").execute()
        
        if response.data and len(response.data) > 0:
            org_data = response.data[0].get("organizations")
            if org_data:
                return self.tenant_manager._dict_to_organization(org_data)
        
        return None
    
    async def _resolve_from_subdomain(self, request: Request) -> Optional[Organization]:
        """
        Resolve from subdomain.
        Example: acme-demo.orion-ai.com -> acme-demo org
        """
        host = request.headers.get("host", "").split(":")[0]
        
        # Check if it's a subdomain of orion-ai.com
        if ".orion-ai.com" not in host:
            return None
        
        # Extract subdomain
        subdomain = host.split(".orion-ai.com")[0]
        
        # Skip www, api, app, etc.
        if subdomain in ["www", "api", "app", "admin"]:
            return None
        
        # Look up by slug
        return await self.tenant_manager.get_organization_by_slug(subdomain)
    
    async def _resolve_from_api_key(self, request: Request) -> Optional[Organization]:
        """
        Resolve from API key.
        Header: X-API-Key: xxx
        
        Note: Requires api_keys table (to be implemented in Phase 6C)
        """
        api_key = request.headers.get("x-api-key")
        
        if not api_key:
            return None
        
        # Look up API key and get associated org
        # TODO: Implement api_keys table lookup
        # For now, return None
        return None
    
    async def _resolve_from_jwt(self, request: Request) -> tuple[Optional[Organization], Optional[str]]:
        """
        Resolve from JWT token.
        Header: Authorization: Bearer xxx
        
        Returns tuple of (Organization, user_id)
        """
        # Get Authorization header
        auth_header = request.headers.get("authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return None, None
        
        token = auth_header.split(" ")[1]
        
        # Verify JWT with Supabase
        try:
            # Get user from token
            user_response = self.tenant_manager.client.auth.get_user(token)
            
            if not user_response or not user_response.user:
                return None, None
            
            user_id = user_response.user.id
            
            # Get user's primary organization
            orgs = await self.tenant_manager.get_user_organizations(user_id)
            
            if not orgs:
                return None, user_id
            
            # Get primary org or first org
            primary_org = next((o for o in orgs if o.get("is_primary")), orgs[0])
            org_id = primary_org["org_id"]
            
            org = await self.tenant_manager.get_organization(org_id)
            
            if org:
                # Attach user_id to org for context
                org._user_id = user_id
            
            return org, user_id
        
        except Exception as e:
            print(f"JWT verification failed: {e}")
            return None, None
    
    async def _resolve_from_query(self, request: Request) -> Optional[Organization]:
        """
        Resolve from query parameter (development/testing only).
        Example: ?org_id=xxx or ?org_slug=xxx
        
        SECURITY WARNING: Should be disabled in production!
        """
        org_id = request.query_params.get("org_id")
        org_slug = request.query_params.get("org_slug")
        
        if org_id:
            return await self.tenant_manager.get_organization(org_id)
        elif org_slug:
            return await self.tenant_manager.get_organization_by_slug(org_slug)
        
        return None


# FastAPI dependency for automatic tenant resolution
async def get_tenant_context(request: Request) -> TenantContext:
    """
    FastAPI dependency to inject tenant context into route handlers.
    
    Usage:
        @app.get("/api/data")
        async def get_data(tenant: TenantContext = Depends(get_tenant_context)):
            # tenant.org_id, tenant.tier, etc. available
            pass
    """
    # Check if already resolved
    if hasattr(request.state, "tenant"):
        return request.state.tenant
    
    # Resolve tenant
    from services.tenancy.tenant_manager import TenantManager
    tenant_manager = TenantManager()
    resolver = TenantResolver(tenant_manager)
    
    return await resolver.resolve_from_request(request)


# Middleware to automatically resolve tenant for all requests
class TenantMiddleware:
    """
    Middleware to automatically resolve tenant context for all requests.
    Attaches TenantContext to request.state.tenant
    """
    
    def __init__(self, app, tenant_manager: TenantManager):
        self.app = app
        self.tenant_manager = tenant_manager
        self.resolver = TenantResolver(tenant_manager)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Create request object
            request = Request(scope, receive)
            
            # Resolve tenant (non-blocking, won't raise exceptions)
            try:
                await self.resolver.resolve_from_request(request)
            except HTTPException:
                # Tenant resolution failed - will be caught by route handler
                pass
        
        await self.app(scope, receive, send)


# Example usage in FastAPI app
"""
from fastapi import FastAPI, Depends
from services.tenancy.tenant_resolver import get_tenant_context, TenantContext, TenantMiddleware
from services.tenancy.tenant_manager import TenantManager

app = FastAPI()

# Add middleware (optional - auto-resolves tenant for all requests)
tenant_manager = TenantManager()
app.add_middleware(TenantMiddleware, tenant_manager=tenant_manager)

# Use as dependency in routes
@app.get("/api/data")
async def get_data(tenant: TenantContext = Depends(get_tenant_context)):
    # Tenant context available
    print(f"Organization: {tenant.org_name} ({tenant.org_slug})")
    print(f"Tier: {tenant.tier}")
    print(f"Quotas: {tenant.quotas}")
    
    # Use org_id for data isolation
    data = await fetch_data_for_org(tenant.org_id)
    return {"data": data}
"""
