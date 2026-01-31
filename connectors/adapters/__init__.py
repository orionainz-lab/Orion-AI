"""
Adapters Package

Connector adapter framework for external API integration.
"""

from .base import BaseAdapter, AdapterConfig, AdapterCapability
from .registry import register_adapter, get_adapter, list_adapters
from .factory import AdapterFactory
from .exceptions import (
    ConnectorError,
    AuthenticationError,
    RateLimitError,
    ValidationError as AdapterValidationError
)

__all__ = [
    "BaseAdapter",
    "AdapterConfig",
    "AdapterCapability",
    "register_adapter",
    "get_adapter",
    "list_adapters",
    "AdapterFactory",
    "ConnectorError",
    "AuthenticationError",
    "RateLimitError",
    "AdapterValidationError",
]
