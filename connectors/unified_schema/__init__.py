"""
Unified Schema Package

Canonical data models for N-to-N integration.
"""

from .base import UnifiedBase, SchemaVersion
from .customer import UnifiedCustomer, UnifiedAddress
from .invoice import UnifiedInvoice, UnifiedLineItem
from .event import UnifiedEvent

__all__ = [
    "UnifiedBase",
    "SchemaVersion",
    "UnifiedCustomer",
    "UnifiedAddress",
    "UnifiedInvoice",
    "UnifiedLineItem",
    "UnifiedEvent",
]
