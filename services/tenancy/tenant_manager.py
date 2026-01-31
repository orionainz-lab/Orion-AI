"""
Phase 6C: Multi-Tenancy - Tenant Manager Service
Handles CRUD operations for organizations (tenants), teams, and members.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
from dataclasses import dataclass
from enum import Enum

from supabase import create_client, Client
import os


class Tier(str, Enum):
    """Organization tier levels"""
    FREE = "free"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class IsolationLevel(str, Enum):
    """Data isolation strategies"""
    ROW = "row"  # Row-level (shared schema)
    SCHEMA = "schema"  # Schema-level (dedicated schema)
    DATABASE = "database"  # Database-level (dedicated database)


@dataclass
class Organization:
    """Organization (tenant) model"""
    id: str
    name: str
    slug: str
    tier: Tier
    isolation_level: IsolationLevel
    data_residency: Optional[str]
    settings: Dict[str, Any]
    quotas: Dict[str, Any]
    billing_status: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Team:
    """Team model"""
    id: str
    org_id: str
    name: str
    description: Optional[str]
    parent_team_id: Optional[str]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class TenantManager:
    """
    Manages organizations (tenants), teams, and member assignments.
    
    Features:
    - Create/read/update/delete organizations
    - Manage teams and hierarchies
    - Handle member assignments
    - Enforce quotas and tier limits
    """
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """Initialize TenantManager with Supabase client"""
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and key required")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    # ========================================
    # ORGANIZATION OPERATIONS
    # ========================================
    
    async def create_organization(
        self,
        name: str,
        slug: str,
        tier: Tier = Tier.FREE,
        isolation_level: IsolationLevel = IsolationLevel.ROW,
        data_residency: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        quotas: Optional[Dict[str, Any]] = None
    ) -> Organization:
        """
        Create a new organization (tenant).
        
        Args:
            name: Organization display name
            slug: URL-friendly identifier (unique)
            tier: Subscription tier
            isolation_level: Data isolation strategy
            data_residency: Data location (us, eu, asia)
            settings: Custom settings
            quotas: Resource quotas (defaults based on tier)
        
        Returns:
            Created organization
        """
        # Default quotas based on tier
        if quotas is None:
            quotas = self._get_default_quotas(tier)
        
        org_data = {
            "name": name,
            "slug": slug,
            "tier": tier.value,
            "isolation_level": isolation_level.value,
            "data_residency": data_residency,
            "settings": settings or {},
            "quotas": quotas,
            "billing_status": "active"
        }
        
        response = self.client.table("organizations").insert(org_data).execute()
        
        if not response.data:
            raise Exception(f"Failed to create organization: {response}")
        
        org_dict = response.data[0]
        return self._dict_to_organization(org_dict)
    
    async def get_organization(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID"""
        response = self.client.table("organizations").select("*").eq("id", org_id).execute()
        
        if not response.data:
            return None
        
        return self._dict_to_organization(response.data[0])
    
    async def get_organization_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug"""
        response = self.client.table("organizations").select("*").eq("slug", slug).execute()
        
        if not response.data:
            return None
        
        return self._dict_to_organization(response.data[0])
    
    async def update_organization(
        self,
        org_id: str,
        **updates
    ) -> Organization:
        """Update organization fields"""
        response = self.client.table("organizations").update(updates).eq("id", org_id).execute()
        
        if not response.data:
            raise Exception(f"Failed to update organization: {org_id}")
        
        return self._dict_to_organization(response.data[0])
    
    async def delete_organization(self, org_id: str) -> bool:
        """
        Delete organization (soft delete by updating status).
        Hard delete should be done manually after data export.
        """
        response = self.client.table("organizations").update({
            "billing_status": "cancelled"
        }).eq("id", org_id).execute()
        
        return bool(response.data)
    
    async def list_organizations(
        self,
        tier: Optional[Tier] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Organization]:
        """List organizations with optional filtering"""
        query = self.client.table("organizations").select("*")
        
        if tier:
            query = query.eq("tier", tier.value)
        
        response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        
        return [self._dict_to_organization(org) for org in response.data]
    
    # ========================================
    # TEAM OPERATIONS
    # ========================================
    
    async def create_team(
        self,
        org_id: str,
        name: str,
        description: Optional[str] = None,
        parent_team_id: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Team:
        """Create a team within an organization"""
        team_data = {
            "org_id": org_id,
            "name": name,
            "description": description,
            "parent_team_id": parent_team_id,
            "settings": settings or {}
        }
        
        response = self.client.table("teams").insert(team_data).execute()
        
        if not response.data:
            raise Exception(f"Failed to create team: {response}")
        
        return self._dict_to_team(response.data[0])
    
    async def get_team(self, team_id: str) -> Optional[Team]:
        """Get team by ID"""
        response = self.client.table("teams").select("*").eq("id", team_id).execute()
        
        if not response.data:
            return None
        
        return self._dict_to_team(response.data[0])
    
    async def list_teams(self, org_id: str) -> List[Team]:
        """List all teams in an organization"""
        response = self.client.table("teams").select("*").eq("org_id", org_id).order("name").execute()
        
        return [self._dict_to_team(team) for team in response.data]
    
    async def update_team(self, team_id: str, **updates) -> Team:
        """Update team fields"""
        response = self.client.table("teams").update(updates).eq("id", team_id).execute()
        
        if not response.data:
            raise Exception(f"Failed to update team: {team_id}")
        
        return self._dict_to_team(response.data[0])
    
    async def delete_team(self, team_id: str) -> bool:
        """Delete team (cascades to team_members)"""
        response = self.client.table("teams").delete().eq("id", team_id).execute()
        return bool(response.data)
    
    # ========================================
    # MEMBER OPERATIONS
    # ========================================
    
    async def add_org_member(
        self,
        org_id: str,
        user_id: str,
        role_id: str,
        invited_by: Optional[str] = None,
        is_primary: bool = False
    ) -> Dict[str, Any]:
        """Add a user to an organization"""
        member_data = {
            "org_id": org_id,
            "user_id": user_id,
            "role_id": role_id,
            "invited_by": invited_by,
            "is_primary": is_primary
        }
        
        response = self.client.table("org_members").insert(member_data).execute()
        
        if not response.data:
            raise Exception(f"Failed to add member: {response}")
        
        return response.data[0]
    
    async def add_team_member(
        self,
        team_id: str,
        user_id: str,
        role_id: str
    ) -> Dict[str, Any]:
        """Add a user to a team"""
        member_data = {
            "team_id": team_id,
            "user_id": user_id,
            "role_id": role_id
        }
        
        response = self.client.table("team_members").insert(member_data).execute()
        
        if not response.data:
            raise Exception(f"Failed to add team member: {response}")
        
        return response.data[0]
    
    async def remove_org_member(self, org_id: str, user_id: str) -> bool:
        """Remove a user from an organization"""
        response = self.client.table("org_members").delete().eq("org_id", org_id).eq("user_id", user_id).execute()
        return bool(response.data)
    
    async def remove_team_member(self, team_id: str, user_id: str) -> bool:
        """Remove a user from a team"""
        response = self.client.table("team_members").delete().eq("team_id", team_id).eq("user_id", user_id).execute()
        return bool(response.data)
    
    async def get_user_organizations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all organizations a user belongs to"""
        response = self.client.rpc(
            "get_user_orgs",
            {"user_uuid": user_id}
        ).execute()
        
        return response.data if response.data else []
    
    async def get_user_teams(self, user_id: str, org_id: str) -> List[Team]:
        """Get all teams a user belongs to in an organization"""
        response = self.client.table("team_members").select(
            "teams(*)"
        ).eq("user_id", user_id).execute()
        
        if not response.data:
            return []
        
        teams = []
        for item in response.data:
            if item.get("teams"):
                team_dict = item["teams"]
                if team_dict.get("org_id") == org_id:
                    teams.append(self._dict_to_team(team_dict))
        
        return teams
    
    # ========================================
    # QUOTA ENFORCEMENT
    # ========================================
    
    async def check_quota(
        self,
        org_id: str,
        quota_type: str
    ) -> Dict[str, Any]:
        """
        Check if organization is within quota limits.
        
        Args:
            org_id: Organization ID
            quota_type: Type of quota ('monthlyApiCalls', 'maxUsers', etc.)
        
        Returns:
            Dict with 'within_limit', 'used', 'limit', 'remaining'
        """
        org = await self.get_organization(org_id)
        
        if not org:
            raise Exception(f"Organization not found: {org_id}")
        
        limit = org.quotas.get(quota_type)
        
        if limit == -1:  # Unlimited
            return {
                "within_limit": True,
                "used": 0,
                "limit": -1,
                "remaining": -1
            }
        
        # Get current usage based on quota type
        used = await self._get_quota_usage(org_id, quota_type)
        
        return {
            "within_limit": used < limit,
            "used": used,
            "limit": limit,
            "remaining": max(0, limit - used)
        }
    
    async def _get_quota_usage(self, org_id: str, quota_type: str) -> int:
        """Get current quota usage for an organization"""
        if quota_type == "maxUsers":
            response = self.client.table("org_members").select("id", count="exact").eq("org_id", org_id).execute()
            return response.count or 0
        
        elif quota_type == "maxConnectors":
            response = self.client.table("user_installed_connectors").select("id", count="exact").eq("org_id", org_id).execute()
            return response.count or 0
        
        elif quota_type == "monthlyApiCalls":
            # Get from monthly_quotas table
            from datetime import date
            current_month = date.today().replace(day=1)
            response = self.client.table("monthly_quotas").select("api_calls_used").eq("org_id", org_id).eq("month", current_month.isoformat()).execute()
            if response.data:
                return response.data[0].get("api_calls_used", 0)
            return 0
        
        return 0
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _get_default_quotas(self, tier: Tier) -> Dict[str, Any]:
        """Get default quotas based on tier"""
        quotas = {
            Tier.FREE: {
                "monthlyApiCalls": 10000,
                "concurrentConnections": 5,
                "dataVolumeGB": 1,
                "maxUsers": 5,
                "maxConnectors": 10
            },
            Tier.PROFESSIONAL: {
                "monthlyApiCalls": 100000,
                "concurrentConnections": 25,
                "dataVolumeGB": 10,
                "maxUsers": 25,
                "maxConnectors": 50
            },
            Tier.ENTERPRISE: {
                "monthlyApiCalls": 1000000,
                "concurrentConnections": 100,
                "dataVolumeGB": 100,
                "maxUsers": -1,  # Unlimited
                "maxConnectors": -1  # Unlimited
            }
        }
        
        return quotas[tier]
    
    def _dict_to_organization(self, data: Dict[str, Any]) -> Organization:
        """Convert dict to Organization object"""
        return Organization(
            id=data["id"],
            name=data["name"],
            slug=data["slug"],
            tier=Tier(data["tier"]),
            isolation_level=IsolationLevel(data["isolation_level"]),
            data_residency=data.get("data_residency"),
            settings=data.get("settings", {}),
            quotas=data.get("quotas", {}),
            billing_status=data["billing_status"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        )
    
    def _dict_to_team(self, data: Dict[str, Any]) -> Team:
        """Convert dict to Team object"""
        return Team(
            id=data["id"],
            org_id=data["org_id"],
            name=data["name"],
            description=data.get("description"),
            parent_team_id=data.get("parent_team_id"),
            settings=data.get("settings", {}),
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        )


# Example usage
if __name__ == "__main__":
    async def main():
        manager = TenantManager()
        
        # Create organization
        org = await manager.create_organization(
            name="Test Company",
            slug="test-company",
            tier=Tier.PROFESSIONAL
        )
        print(f"Created org: {org.name} ({org.slug})")
        
        # Create team
        team = await manager.create_team(
            org_id=org.id,
            name="Engineering",
            description="Engineering team"
        )
        print(f"Created team: {team.name}")
        
        # Check quotas
        quota_check = await manager.check_quota(org.id, "maxUsers")
        print(f"User quota: {quota_check}")
    
    asyncio.run(main())
