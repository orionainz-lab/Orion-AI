"""
Base Adapter

Abstract base class for all connector adapters.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Any
from pydantic import BaseModel
import httpx
from ..unified_schema.base import UnifiedBase

T = TypeVar('T', bound=UnifiedBase)


class AdapterConfig(BaseModel):
    """Configuration for adapter instances"""
    
    base_url: str
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    
    class Config:
        extra = "allow"  # Allow connector-specific fields


class AdapterCapability:
    """Capability flags for adapters"""
    
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    WEBHOOK = "webhook"
    BATCH = "batch"


class BaseAdapter(ABC, Generic[T]):
    """
    Abstract base class for all connector adapters.
    
    Implements the Adapter pattern for external API integration.
    Subclasses must implement:
    - _get_auth_headers()
    - to_unified()
    - from_unified()
    """
    
    # Adapter metadata (override in subclasses)
    name: str = "base"
    version: str = "1.0.0"
    capabilities: List[str] = []
    
    def __init__(
        self,
        config: AdapterConfig,
        credentials: dict[str, Any]
    ):
        self.config = config
        self.credentials = credentials
        self._client: Optional[httpx.AsyncClient] = None
    
    async def connect(self) -> None:
        """Initialize HTTP client with authentication"""
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers=self._get_auth_headers()
        )
    
    async def disconnect(self) -> None:
        """Cleanup resources"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    @abstractmethod
    def _get_auth_headers(self) -> dict[str, str]:
        """
        Get authentication headers.
        
        Override in subclasses to provide auth.
        """
        pass
    
    @abstractmethod
    async def to_unified(self, data: dict) -> T:
        """
        Transform external data to unified model.
        
        Args:
            data: Raw API response data
        
        Returns:
            Unified model instance
        """
        pass
    
    @abstractmethod
    async def from_unified(self, model: T) -> dict:
        """
        Transform unified model to external format.
        
        Args:
            model: Unified model instance
        
        Returns:
            Dict ready for API submission
        """
        pass
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, *args):
        """Context manager exit"""
        await self.disconnect()
