"""
Phase 6C: SSO Integration - JIT Provisioning
Just-In-Time user provisioning from SSO providers.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from supabase import Client

from .oidc_provider import OIDCUserInfo
from .saml_provider import SAMLUserInfo


@dataclass
class JITConfig:
    """JIT provisioning configuration"""
    enabled: bool
    default_role_id: str
    group_mapping: Dict[str, str]  # IdP group -> Role ID
    auto_create_users: bool = True
    auto_update_profile: bool = True


class JITProvisioner:
    """
    Just-In-Time user provisioning.
    
    Automatically creates/updates users on first SSO login:
    - Creates user in auth.users if not exists
    - Assigns to organization
    - Maps IdP groups to roles
    - Updates profile information
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
    
    async def provision_oidc_user(
        self,
        org_id: str,
        user_info: OIDCUserInfo,
        jit_config: JITConfig
    ) -> Dict[str, Any]:
        """
        Provision user from OIDC user info.
        
        Args:
            org_id: Organization ID
            user_info: User info from OIDC provider
            jit_config: JIT configuration
        
        Returns:
            User record with org membership
        """
        if not jit_config.enabled:
            raise Exception("JIT provisioning is disabled")
        
        # Check if user exists
        user = await self._find_user_by_email(user_info.email)
        
        if not user and jit_config.auto_create_users:
            # Create new user
            user = await self._create_user(
                email=user_info.email,
                name=user_info.name,
                picture=user_info.picture
            )
        
        if not user:
            raise Exception(f"User not found and auto-create disabled: {user_info.email}")
        
        user_id = user["id"]
        
        # Determine role from groups
        role_id = self._map_groups_to_role(
            user_info.groups or [],
            jit_config.group_mapping,
            jit_config.default_role_id
        )
        
        # Add to organization (if not already member)
        await self._ensure_org_membership(org_id, user_id, role_id)
        
        # Update profile if configured
        if jit_config.auto_update_profile:
            await self._update_user_profile(
                user_id,
                name=user_info.name,
                picture=user_info.picture
            )
        
        return {
            "user_id": user_id,
            "email": user_info.email,
            "org_id": org_id,
            "role_id": role_id
        }
    
    async def provision_saml_user(
        self,
        org_id: str,
        user_info: SAMLUserInfo,
        jit_config: JITConfig
    ) -> Dict[str, Any]:
        """
        Provision user from SAML user info.
        
        Args:
            org_id: Organization ID
            user_info: User info from SAML provider
            jit_config: JIT configuration
        
        Returns:
            User record with org membership
        """
        if not jit_config.enabled:
            raise Exception("JIT provisioning is disabled")
        
        # Check if user exists
        user = await self._find_user_by_email(user_info.email)
        
        if not user and jit_config.auto_create_users:
            # Create new user
            full_name = None
            if user_info.first_name and user_info.last_name:
                full_name = f"{user_info.first_name} {user_info.last_name}"
            elif user_info.display_name:
                full_name = user_info.display_name
            
            user = await self._create_user(
                email=user_info.email,
                name=full_name
            )
        
        if not user:
            raise Exception(f"User not found and auto-create disabled: {user_info.email}")
        
        user_id = user["id"]
        
        # Determine role from groups
        role_id = self._map_groups_to_role(
            user_info.groups or [],
            jit_config.group_mapping,
            jit_config.default_role_id
        )
        
        # Add to organization (if not already member)
        await self._ensure_org_membership(org_id, user_id, role_id)
        
        # Update profile if configured
        if jit_config.auto_update_profile:
            full_name = None
            if user_info.first_name and user_info.last_name:
                full_name = f"{user_info.first_name} {user_info.last_name}"
            elif user_info.display_name:
                full_name = user_info.display_name
            
            await self._update_user_profile(user_id, name=full_name)
        
        return {
            "user_id": user_id,
            "email": user_info.email,
            "org_id": org_id,
            "role_id": role_id
        }
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    async def _find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email in auth.users"""
        try:
            # Query auth.users (requires service role key)
            response = self.client.auth.admin.list_users()
            
            if response:
                for user in response:
                    if user.email == email:
                        return {
                            "id": user.id,
                            "email": user.email,
                            "user_metadata": user.user_metadata
                        }
        except Exception as e:
            print(f"Error finding user: {e}")
        
        return None
    
    async def _create_user(
        self,
        email: str,
        name: Optional[str] = None,
        picture: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new user in auth.users"""
        # Generate temporary password (user won't use it - SSO only)
        import secrets
        temp_password = secrets.token_urlsafe(32)
        
        user_metadata = {}
        if name:
            user_metadata["full_name"] = name
        if picture:
            user_metadata["avatar_url"] = picture
        
        # Create user via Supabase Admin API
        response = self.client.auth.admin.create_user({
            "email": email,
            "password": temp_password,
            "email_confirm": True,  # Auto-confirm since SSO verified
            "user_metadata": user_metadata
        })
        
        if not response or not response.user:
            raise Exception(f"Failed to create user: {email}")
        
        return {
            "id": response.user.id,
            "email": response.user.email,
            "user_metadata": response.user.user_metadata
        }
    
    async def _ensure_org_membership(
        self,
        org_id: str,
        user_id: str,
        role_id: str
    ) -> None:
        """Ensure user is a member of the organization"""
        # Check if already a member
        response = self.client.table("org_members").select("id").eq(
            "org_id", org_id
        ).eq("user_id", user_id).execute()
        
        if response.data:
            # Already a member - update role if changed
            self.client.table("org_members").update({
                "role_id": role_id
            }).eq("org_id", org_id).eq("user_id", user_id).execute()
        else:
            # Add as new member
            self.client.table("org_members").insert({
                "org_id": org_id,
                "user_id": user_id,
                "role_id": role_id,
                "is_primary": False
            }).execute()
    
    async def _update_user_profile(
        self,
        user_id: str,
        name: Optional[str] = None,
        picture: Optional[str] = None
    ) -> None:
        """Update user profile metadata"""
        updates = {}
        
        if name:
            updates["full_name"] = name
        if picture:
            updates["avatar_url"] = picture
        
        if updates:
            self.client.auth.admin.update_user_by_id(
                user_id,
                {"user_metadata": updates}
            )
    
    def _map_groups_to_role(
        self,
        user_groups: list[str],
        group_mapping: Dict[str, str],
        default_role_id: str
    ) -> str:
        """
        Map IdP groups to role ID.
        
        Args:
            user_groups: List of groups from IdP
            group_mapping: Mapping of group name -> role ID
            default_role_id: Default role if no groups match
        
        Returns:
            Role ID to assign
        """
        # Check each user group against mapping
        for group in user_groups:
            if group in group_mapping:
                return group_mapping[group]
        
        # Return default role
        return default_role_id


# Example usage
"""
from services.auth.sso.jit_provisioning import JITProvisioner, JITConfig

provisioner = JITProvisioner(supabase_client)

jit_config = JITConfig(
    enabled=True,
    default_role_id="00000000-0000-0000-0000-000000000004",  # Member
    group_mapping={
        "Admins": "00000000-0000-0000-0000-000000000002",  # Org Admin
        "Engineering": "00000000-0000-0000-0000-000000000003",  # Team Lead
    },
    auto_create_users=True,
    auto_update_profile=True
)

# After OIDC authentication
result = await provisioner.provision_oidc_user(org_id, oidc_user_info, jit_config)
print(f"Provisioned user: {result['user_id']}")
"""
