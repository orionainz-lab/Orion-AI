"""
Phase 6C: RBAC System - Role Manager
Manages roles and role assignments.
"""

from typing import List, Dict, Any, Optional
from supabase import Client

from .permission_checker import Permission, Scope


class RoleManager:
    """
    Manages roles and role assignments.
    
    Features:
    - Create/update/delete custom roles
    - Assign roles to users
    - Get role hierarchy
    - Clone roles
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
    
    # ========================================
    # ROLE OPERATIONS
    # ========================================
    
    async def create_role(
        self,
        org_id: str,
        name: str,
        description: str,
        permissions: List[str],
        is_system_role: bool = False
    ) -> Dict[str, Any]:
        """
        Create a custom role.
        
        Args:
            org_id: Organization ID (None for system roles)
            name: Role name
            description: Role description
            permissions: List of permission strings (resource:action:scope)
            is_system_role: Whether this is a system-wide role
        
        Returns:
            Created role
        """
        role_data = {
            "org_id": org_id if not is_system_role else None,
            "name": name,
            "description": description,
            "permissions": permissions,
            "is_system_role": is_system_role
        }
        
        response = self.client.table("roles").insert(role_data).execute()
        
        if not response.data:
            raise Exception(f"Failed to create role: {name}")
        
        return response.data[0]
    
    async def get_role(self, role_id: str) -> Optional[Dict[str, Any]]:
        """Get role by ID"""
        response = self.client.table("roles").select("*").eq("id", role_id).execute()
        
        if not response.data:
            return None
        
        return response.data[0]
    
    async def get_role_by_name(
        self,
        name: str,
        org_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get role by name"""
        query = self.client.table("roles").select("*").eq("name", name)
        
        if org_id:
            query = query.eq("org_id", org_id)
        else:
            query = query.is_("org_id", "null")  # System roles
        
        response = query.execute()
        
        if not response.data:
            return None
        
        return response.data[0]
    
    async def list_roles(
        self,
        org_id: Optional[str] = None,
        include_system_roles: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List roles.
        
        Args:
            org_id: Organization ID (None for system roles only)
            include_system_roles: Whether to include system roles
        
        Returns:
            List of roles
        """
        query = self.client.table("roles").select("*")
        
        if org_id:
            if include_system_roles:
                # Get both org-specific and system roles
                response_org = query.eq("org_id", org_id).execute()
                response_sys = self.client.table("roles").select("*").is_("org_id", "null").execute()
                
                all_roles = []
                if response_org.data:
                    all_roles.extend(response_org.data)
                if response_sys.data:
                    all_roles.extend(response_sys.data)
                
                return all_roles
            else:
                # Only org-specific roles
                query = query.eq("org_id", org_id)
        else:
            # Only system roles
            query = query.is_("org_id", "null")
        
        response = query.order("name").execute()
        
        return response.data if response.data else []
    
    async def update_role(
        self,
        role_id: str,
        **updates
    ) -> Dict[str, Any]:
        """Update role fields"""
        # Don't allow updating system roles
        role = await self.get_role(role_id)
        if role and role.get("is_system_role"):
            raise Exception("Cannot update system roles")
        
        response = self.client.table("roles").update(updates).eq("id", role_id).execute()
        
        if not response.data:
            raise Exception(f"Failed to update role: {role_id}")
        
        return response.data[0]
    
    async def delete_role(self, role_id: str) -> bool:
        """
        Delete role.
        Cannot delete system roles or roles with assigned users.
        """
        # Don't allow deleting system roles
        role = await self.get_role(role_id)
        if role and role.get("is_system_role"):
            raise Exception("Cannot delete system roles")
        
        # Check if role is assigned to users
        org_members = self.client.table("org_members").select("id", count="exact").eq("role_id", role_id).execute()
        team_members = self.client.table("team_members").select("id", count="exact").eq("role_id", role_id).execute()
        
        total_assignments = (org_members.count or 0) + (team_members.count or 0)
        
        if total_assignments > 0:
            raise Exception(f"Cannot delete role: {total_assignments} users assigned")
        
        response = self.client.table("roles").delete().eq("id", role_id).execute()
        return bool(response.data)
    
    async def clone_role(
        self,
        source_role_id: str,
        new_name: str,
        new_description: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Clone an existing role with new name"""
        source_role = await self.get_role(source_role_id)
        
        if not source_role:
            raise Exception(f"Source role not found: {source_role_id}")
        
        return await self.create_role(
            org_id=org_id,
            name=new_name,
            description=new_description or f"Cloned from {source_role['name']}",
            permissions=source_role["permissions"],
            is_system_role=False
        )
    
    # ========================================
    # ROLE ASSIGNMENT
    # ========================================
    
    async def assign_org_role(
        self,
        org_id: str,
        user_id: str,
        role_id: str
    ) -> Dict[str, Any]:
        """Assign role to user in organization"""
        # Check if already a member
        existing = self.client.table("org_members").select("id").eq(
            "org_id", org_id
        ).eq("user_id", user_id).execute()
        
        if existing.data:
            # Update existing membership
            response = self.client.table("org_members").update({
                "role_id": role_id
            }).eq("org_id", org_id).eq("user_id", user_id).execute()
        else:
            # Create new membership
            response = self.client.table("org_members").insert({
                "org_id": org_id,
                "user_id": user_id,
                "role_id": role_id
            }).execute()
        
        if not response.data:
            raise Exception(f"Failed to assign role")
        
        return response.data[0]
    
    async def assign_team_role(
        self,
        team_id: str,
        user_id: str,
        role_id: str
    ) -> Dict[str, Any]:
        """Assign role to user in team"""
        # Check if already a member
        existing = self.client.table("team_members").select("id").eq(
            "team_id", team_id
        ).eq("user_id", user_id).execute()
        
        if existing.data:
            # Update existing membership
            response = self.client.table("team_members").update({
                "role_id": role_id
            }).eq("team_id", team_id).eq("user_id", user_id).execute()
        else:
            # Create new membership
            response = self.client.table("team_members").insert({
                "team_id": team_id,
                "user_id": user_id,
                "role_id": role_id
            }).execute()
        
        if not response.data:
            raise Exception(f"Failed to assign team role")
        
        return response.data[0]
    
    async def get_user_roles(
        self,
        user_id: str,
        org_id: str
    ) -> Dict[str, Any]:
        """Get all roles for user in organization"""
        # Get org role
        org_role = self.client.table("org_members").select(
            "roles(*)"
        ).eq("org_id", org_id).eq("user_id", user_id).execute()
        
        # Get team roles
        team_roles = self.client.table("team_members").select(
            "teams(org_id), roles(*)"
        ).eq("user_id", user_id).execute()
        
        # Filter team roles for this org
        org_team_roles = []
        if team_roles.data:
            for item in team_roles.data:
                if item.get("teams") and item["teams"].get("org_id") == org_id:
                    org_team_roles.append(item.get("roles"))
        
        return {
            "org_role": org_role.data[0].get("roles") if org_role.data else None,
            "team_roles": org_team_roles
        }
    
    # ========================================
    # PERMISSION MANAGEMENT
    # ========================================
    
    async def add_permission_to_role(
        self,
        role_id: str,
        permission: str
    ) -> Dict[str, Any]:
        """Add permission to role"""
        role = await self.get_role(role_id)
        
        if not role:
            raise Exception(f"Role not found: {role_id}")
        
        if role.get("is_system_role"):
            raise Exception("Cannot modify system roles")
        
        permissions = role.get("permissions", [])
        
        if permission not in permissions:
            permissions.append(permission)
            return await self.update_role(role_id, permissions=permissions)
        
        return role
    
    async def remove_permission_from_role(
        self,
        role_id: str,
        permission: str
    ) -> Dict[str, Any]:
        """Remove permission from role"""
        role = await self.get_role(role_id)
        
        if not role:
            raise Exception(f"Role not found: {role_id}")
        
        if role.get("is_system_role"):
            raise Exception("Cannot modify system roles")
        
        permissions = role.get("permissions", [])
        
        if permission in permissions:
            permissions.remove(permission)
            return await self.update_role(role_id, permissions=permissions)
        
        return role


# Helper functions for common role operations
async def get_default_role_id(role_name: str, client: Client) -> Optional[str]:
    """Get ID of default system role by name"""
    response = client.table("roles").select("id").eq("name", role_name).eq("is_system_role", True).execute()
    
    if response.data:
        return response.data[0]["id"]
    
    return None


# Example usage
"""
from services.rbac.role_manager import RoleManager

role_manager = RoleManager(supabase_client)

# Create custom role
custom_role = await role_manager.create_role(
    org_id="org-123",
    name="Data Analyst",
    description="Can view analytics and export data",
    permissions=[
        "analytics:read:org",
        "analytics:export:org",
        "connectors:read:org"
    ]
)

# Assign role to user
await role_manager.assign_org_role(
    org_id="org-123",
    user_id="user-456",
    role_id=custom_role["id"]
)

# Get user's roles
user_roles = await role_manager.get_user_roles("user-456", "org-123")
"""
