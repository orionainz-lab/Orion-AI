"""
Adapter Registry

Plugin-style registration system for connectors.
"""

from typing import Dict, Type, Optional
from .base import BaseAdapter
import importlib
import pkgutil


# Global adapter registry
_adapter_registry: Dict[str, Type[BaseAdapter]] = {}


def register_adapter(name: str):
    """
    Decorator to register an adapter.
    
    Usage:
        @register_adapter("stripe")
        class StripeAdapter(BaseAdapter):
            ...
    """
    def decorator(cls: Type[BaseAdapter]):
        cls.name = name
        _adapter_registry[name] = cls
        return cls
    return decorator


def get_adapter(name: str) -> Optional[Type[BaseAdapter]]:
    """
    Get adapter class by name.
    
    Args:
        name: Adapter name (e.g., "stripe")
    
    Returns:
        Adapter class or None if not found
    """
    return _adapter_registry.get(name)


def list_adapters() -> Dict[str, Type[BaseAdapter]]:
    """
    List all registered adapters.
    
    Returns:
        Dict of adapter name -> adapter class
    """
    return _adapter_registry.copy()


def discover_adapters(package_path: str = "connectors.adapters"):
    """
    Auto-discover and register adapters from package.
    
    Imports all modules in the adapters package to trigger
    @register_adapter decorators.
    
    Args:
        package_path: Package path to scan
    """
    try:
        package = importlib.import_module(package_path)
    except ImportError:
        return
    
    # Skip base modules
    skip_modules = {"base", "registry", "factory", "exceptions"}
    
    for _, module_name, is_pkg in pkgutil.iter_modules(
        package.__path__
    ):
        if module_name not in skip_modules:
            try:
                importlib.import_module(
                    f"{package_path}.{module_name}"
                )
            except Exception:
                # Silently skip modules that fail to import
                pass
