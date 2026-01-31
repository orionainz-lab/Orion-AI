"""
Connector Registry Service

CRUD operations for connectors, configs, and credentials.
Integrates with Supabase for persistence.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from supabase import Client
from .credential_manager import CredentialManager


class ConnectorRegistry:
    """
    Service for managing connector configurations.
    
    Handles:
    - Connector CRUD
    - Config management
    - Credential storage (encrypted)
    - Sync status tracking
    """
    
    def __init__(
        self,
        supabase_client: Client,
        credential_manager: CredentialManager
    ):
        """
        Initialize registry.
        
        Args:
            supabase_client: Authenticated Supabase client
            credential_manager: For encrypting credentials
        """
        self.db = supabase_client
        self.creds = credential_manager
    
    # ============================================
    # Connector Operations (System-Level)
    # ============================================
    
    async def list_connectors(
        self,
        status: str = "active"
    ) -> List[Dict[str, Any]]:
        """
        List available connectors.
        
        Args:
            status: Filter by status (active/deprecated/disabled)
        
        Returns:
            List of connector definitions
        """
        response = self.db.table("connectors") \
            .select("*") \
            .eq("status", status) \
            .execute()
        
        return response.data
    
    async def get_connector(
        self,
        connector_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get connector by name.
        
        Args:
            connector_name: Connector name (e.g., "stripe")
        
        Returns:
            Connector definition or None
        """
        response = self.db.table("connectors") \
            .select("*") \
            .eq("name", connector_name) \
            .single() \
            .execute()
        
        return response.data if response.data else None
    
    # ============================================
    # Config Operations (User-Level)
    # ============================================
    
    async def create_config(
        self,
        connector_name: str,
        user_id: str,
        config_name: str,
        config_data: Dict[str, Any],
        credentials: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Create user connector configuration.
        
        Args:
            connector_name: Connector to configure
            user_id: User UUID
            config_name: Human-readable name
            config_data: Configuration settings
            credentials: API keys/tokens (will be encrypted)
        
        Returns:
            Created config with ID
        """
        # Get connector ID
        connector = await self.get_connector(connector_name)
        if not connector:
            raise ValueError(f"Unknown connector: {connector_name}")
        
        # Create config
        config_response = self.db.table("connector_configs") \
            .insert({
                "connector_id": connector["id"],
                "user_id": user_id,
                "name": config_name,
                "config": config_data,
                "is_active": True
            }) \
            .execute()
        
        config_id = config_response.data[0]["id"]
        
        # Store encrypted credentials
        for cred_type, cred_value in credentials.items():
            encrypted = self.creds.encrypt(cred_value)
            
            self.db.table("connector_credentials") \
                .insert({
                    "config_id": config_id,
                    "credential_type": cred_type,
                    "encrypted_value": encrypted
                }) \
                .execute()
        
        return config_response.data[0]
    
    async def list_configs(
        self,
        user_id: str,
        connector_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List user's connector configs.
        
        Args:
            user_id: User UUID
            connector_name: Optional filter by connector
        
        Returns:
            List of configs
        """
        query = self.db.table("connector_configs") \
            .select("*, connectors(name, type, description)") \
            .eq("user_id", user_id)
        
        if connector_name:
            # Need to join to filter by connector name
            connector = await self.get_connector(connector_name)
            if connector:
                query = query.eq("connector_id", connector["id"])
        
        response = query.execute()
        return response.data
    
    async def get_config(
        self,
        config_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get config by ID.
        
        Args:
            config_id: Config UUID
        
        Returns:
            Config with connector info
        """
        response = self.db.table("connector_configs") \
            .select("*, connectors(*)") \
            .eq("id", config_id) \
            .single() \
            .execute()
        
        return response.data if response.data else None
    
    async def update_config(
        self,
        config_id: str,
        config_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update config settings.
        
        Args:
            config_id: Config UUID
            config_data: New settings
        
        Returns:
            Updated config
        """
        response = self.db.table("connector_configs") \
            .update({"config": config_data}) \
            .eq("id", config_id) \
            .execute()
        
        return response.data[0]
    
    async def delete_config(self, config_id: str) -> bool:
        """
        Delete config and credentials.
        
        Args:
            config_id: Config UUID
        
        Returns:
            True if deleted
        """
        # Credentials deleted via CASCADE
        self.db.table("connector_configs") \
            .delete() \
            .eq("id", config_id) \
            .execute()
        
        return True
    
    # ============================================
    # Credential Operations
    # ============================================
    
    async def get_credentials(
        self,
        config_id: str
    ) -> Dict[str, str]:
        """
        Get decrypted credentials for config.
        
        Args:
            config_id: Config UUID
        
        Returns:
            Dict of credential_type -> plaintext_value
        """
        response = self.db.table("connector_credentials") \
            .select("credential_type, encrypted_value") \
            .eq("config_id", config_id) \
            .execute()
        
        credentials = {}
        for row in response.data:
            plaintext = self.creds.decrypt(
                row["encrypted_value"]
            )
            credentials[row["credential_type"]] = plaintext
        
        return credentials
    
    # ============================================
    # Sync Status Tracking
    # ============================================
    
    async def update_sync_status(
        self,
        config_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update sync status for config.
        
        Args:
            config_id: Config UUID
            status: idle/syncing/error/success
            error_message: Error if status=error
        """
        self.db.table("connector_configs") \
            .update({
                "sync_status": status,
                "last_sync_at": datetime.utcnow().isoformat(),
                "error_message": error_message
            }) \
            .eq("id", config_id) \
            .execute()
