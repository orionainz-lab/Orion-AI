"""
Phase 6C: RBAC (Role-Based Access Control) System
Provides role and permission management.
"""

from .permission_checker import (
    PermissionChecker,
    Permission,
    Scope,
    PermissionDeniedError,
    require_permission
)
from .role_manager import RoleManager, get_default_role_id

__all__ = [
    "PermissionChecker",
    "Permission",
    "Scope",
    "PermissionDeniedError",
    "require_permission",
    "RoleManager",
    "get_default_role_id"
]
