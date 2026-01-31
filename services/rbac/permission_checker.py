"""
Phase 6C: RBAC System - Permission Checker
Role-Based Access Control with resource-action-scope permissions.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass
from supabase import Client


class Scope(str, Enum):
    """Permission scopes"""
    SELF = "self"  # Own resources only
    TEAM = "team"  # Team resources
    ORG = "org"  # Organization resources
    ALL = "all"  # Super admin access


@dataclass
class Permission:
    """Permission model"""
    resource: str  # 'connectors', 'analytics', 'users', etc.
    action: str  # 'create', 'read', 'update', 'delete', 'export', 'admin'
    scope: Scope
    
    def to_string(self) -> str:
        """Convert to permission string format"""
        return f"{self.resource}:{self.action}:{self.scope.value}"
    
    @classmethod
    def from_string(cls, perm_str: str) -> 'Permission':
        """Parse permission from string"""
        parts = perm_str.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid permission string: {perm_str}")
        
        return cls(
            resource=parts[0],
            action=parts[1],
            scope=Scope(parts[2])
        )


class PermissionChecker:
    """
    RBAC permission checker.
    
    Features:
    - Check if user has permission for resource-action-scope
    - Support wildcard permissions (*:*:all)
    - Check against user's roles in org/team
    - Cache permission lookups for performance
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self._permission_cache: Dict[str, List[Permission]] = {}
    
    async def has_permission(
        self,
        user_id: str,
        org_id: str,
        resource: str,
        action: str,
        required_scope: Scope = Scope.SELF,
        team_id: Optional[str] = None
    ) -> bool:
        """
        Check if user has permission.
        
        Args:
            user_id: User ID
            org_id: Organization ID
            resource: Resource name ('connectors', 'analytics', etc.)
            action: Action name ('read', 'create', 'update', 'delete', 'export', 'admin')
            required_scope: Required scope level
            team_id: Team ID (for team-scoped resources)
        
        Returns:
            True if user has permission
        """
        # Get user's permissions for this org
        permissions = await self._get_user_permissions(user_id, org_id, team_id)
        
        # Check for wildcard permission (super admin)
        if any(p.resource == "*" and p.action == "*" and p.scope == Scope.ALL for p in permissions):
            return True
        
        # Check for specific permission
        required_perm = Permission(resource, action, required_scope)
        
        if required_perm in permissions:
            return True
        
        # Check for resource:*:scope (action wildcard)
        resource_wildcard = Permission(resource, "*", required_scope)
        if resource_wildcard in permissions:
            return True
        
        # Check for resource:action:all (higher scope)
        if required_scope != Scope.ALL:
            all_scope_perm = Permission(resource, action, Scope.ALL)
            if all_scope_perm in permissions:
                return True
            
            # Check resource:*:all
            resource_all_wildcard = Permission(resource, "*", Scope.ALL)
            if resource_all_wildcard in permissions:
                return True
        
        return False
    
    async def check_permission_or_raise(
        self,
        user_id: str,
        org_id: str,
        resource: str,
        action: str,
        required_scope: Scope = Scope.SELF,
        team_id: Optional[str] = None
    ) -> None:
        """
        Check permission and raise exception if denied.
        
        Raises:
            PermissionDeniedError: If user doesn't have permission
        """
        has_perm = await self.has_permission(
            user_id, org_id, resource, action, required_scope, team_id
        )
        
        if not has_perm:
            raise PermissionDeniedError(
                f"Permission denied: {resource}:{action}:{required_scope.value}"
            )
    
    async def get_user_role(
        self,
        user_id: str,
        org_id: str,
        team_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get user's role in organization or team"""
        if team_id:
            # Get team role
            response = self.client.table("team_members").select(
                "role_id, roles(*)"
            ).eq("team_id", team_id).eq("user_id", user_id).execute()
        else:
            # Get org role
            response = self.client.table("org_members").select(
                "role_id, roles(*)"
            ).eq("org_id", org_id).eq("user_id", user_id).execute()
        
        if not response.data:
            return None
        
        return response.data[0]
    
    async def _get_user_permissions(
        self,
        user_id: str,
        org_id: str,
        team_id: Optional[str] = None
    ) -> List[Permission]:
        """
        Get all permissions for user in org/team.
        Combines org-level and team-level permissions.
        """
        cache_key = f"{user_id}:{org_id}:{team_id}"
        
        # Check cache
        if cache_key in self._permission_cache:
            return self._permission_cache[cache_key]
        
        permissions = []
        
        # Get org-level role permissions
        org_role = await self.get_user_role(user_id, org_id)
        if org_role and org_role.get("roles"):
            role_perms = org_role["roles"].get("permissions", [])
            permissions.extend(self._parse_permissions(role_perms))
        
        # Get team-level role permissions (if team_id provided)
        if team_id:
            team_role = await self.get_user_role(user_id, org_id, team_id)
            if team_role and team_role.get("roles"):
                role_perms = team_role["roles"].get("permissions", [])
                permissions.extend(self._parse_permissions(role_perms))
        
        # Cache permissions
        self._permission_cache[cache_key] = permissions
        
        return permissions
    
    def _parse_permissions(self, perm_list: List[str]) -> List[Permission]:
        """Parse list of permission strings"""
        permissions = []
        
        for perm_str in perm_list:
            try:
                perm = Permission.from_string(perm_str)
                permissions.append(perm)
            except ValueError:
                # Skip invalid permissions
                continue
        
        return permissions
    
    def clear_cache(self, user_id: Optional[str] = None) -> None:
        """Clear permission cache (call when roles change)"""
        if user_id:
            # Clear cache for specific user
            keys_to_remove = [k for k in self._permission_cache.keys() if k.startswith(f"{user_id}:")]
            for key in keys_to_remove:
                del self._permission_cache[key]
        else:
            # Clear entire cache
            self._permission_cache.clear()


class PermissionDeniedError(Exception):
    """Raised when user doesn't have required permission"""
    pass


# FastAPI dependency for permission checking
async def require_permission(
    resource: str,
    action: str,
    scope: Scope = Scope.SELF
):
    """
    FastAPI dependency to require permission.
    
    Usage:
        @app.get("/api/connectors")
        async def get_connectors(
            _: None = Depends(require_permission("connectors", "read", Scope.ORG))
        ):
            # User has permission
            pass
    """
    from fastapi import Request, HTTPException, Depends
    from services.tenancy.tenant_resolver import get_tenant_context, TenantContext
    
    async def check(
        request: Request,
        tenant: TenantContext = Depends(get_tenant_context)
    ):
        if not tenant.user_id:
            raise HTTPException(401, "Not authenticated")
        
        checker = PermissionChecker(request.app.state.supabase_client)
        
        try:
            await checker.check_permission_or_raise(
                user_id=tenant.user_id,
                org_id=tenant.org_id,
                resource=resource,
                action=action,
                required_scope=scope
            )
        except PermissionDeniedError as e:
            raise HTTPException(403, str(e))
    
    return check


# Example usage
"""
from services.rbac.permission_checker import PermissionChecker, Scope, require_permission

# Manual check
checker = PermissionChecker(supabase_client)

has_access = await checker.has_permission(
    user_id="user-123",
    org_id="org-456",
    resource="connectors",
    action="create",
    required_scope=Scope.ORG
)

if has_access:
    # User can create connectors
    pass

# FastAPI route with permission requirement
@app.get("/api/connectors")
async def get_connectors(
    _: None = Depends(require_permission("connectors", "read", Scope.ORG))
):
    # Only users with connectors:read:org permission can access
    return {"connectors": []}
"""
