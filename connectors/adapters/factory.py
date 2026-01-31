"""
Adapter Factory

Creates adapter instances with configuration and credentials.
"""

from typing import Optional
from .base import BaseAdapter, AdapterConfig
from .registry import get_adapter
from .exceptions import ConnectorError


class AdapterFactory:
    """
    Factory for creating configured adapter instances.
    
    Usage:
        factory = AdapterFactory()
        adapter = await factory.create("stripe", config_id)
        async with adapter:
            customers = await adapter.list_customers()
    """
    
    def __init__(self, registry_service=None):
        """
        Initialize factory.
        
        Args:
            registry_service: Service to fetch configs/credentials
        """
        self.registry = registry_service
    
    async def create(
        self,
        connector_name: str,
        config_id: str = None,
        config_dict: dict = None,
        credentials: dict = None
    ) -> Optional[BaseAdapter]:
        """
        Create adapter instance.
        
        Args:
            connector_name: Adapter name (e.g., "stripe")
            config_id: Config ID to fetch from registry
            config_dict: Direct config dict (alternative)
            credentials: Direct credentials (alternative)
        
        Returns:
            Configured adapter instance
        
        Raises:
            ConnectorError: If adapter not found or config missing
        """
        # Get adapter class
        adapter_class = get_adapter(connector_name)
        if not adapter_class:
            raise ConnectorError(
                f"Unknown connector: {connector_name}",
                code="unknown_connector"
            )
        
        # Get config and credentials
        if config_id and self.registry:
            # Fetch from database
            config_data = await self.registry.get_config(config_id)
            creds = await self.registry.get_credentials(config_id)
        elif config_dict and credentials:
            # Use provided values
            config_data = config_dict
            creds = credentials
        else:
            raise ConnectorError(
                "Must provide either config_id or config_dict+credentials",
                code="missing_config"
            )
        
        # Create adapter config
        adapter_config = AdapterConfig(**config_data)
        
        # Instantiate adapter
        return adapter_class(adapter_config, creds)
    
    def create_from_env(
        self,
        connector_name: str,
        env_prefix: str = None
    ) -> BaseAdapter:
        """
        Create adapter from environment variables.
        
        Useful for development/testing.
        
        Args:
            connector_name: Adapter name
            env_prefix: Env var prefix (default: connector_name.upper())
        
        Returns:
            Configured adapter
        """
        import os
        
        if not env_prefix:
            env_prefix = connector_name.upper()
        
        # Build config from env
        config_data = {
            "base_url": os.getenv(
                f"{env_prefix}_BASE_URL",
                ""
            ),
            "timeout": int(os.getenv(
                f"{env_prefix}_TIMEOUT",
                "30"
            ))
        }
        
        credentials = {
            "api_key": os.getenv(f"{env_prefix}_API_KEY", "")
        }
        
        adapter_class = get_adapter(connector_name)
        if not adapter_class:
            raise ConnectorError(
                f"Unknown connector: {connector_name}"
            )
        
        return adapter_class(
            AdapterConfig(**config_data),
            credentials
        )
