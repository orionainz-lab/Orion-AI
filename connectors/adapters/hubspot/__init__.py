"""
HubSpot Adapter Package

Supports both direct API and MCP integration.
"""

from .adapter import HubSpotAdapter
from .mcp_helper import HubSpotMCPHelper

__all__ = ["HubSpotAdapter", "HubSpotMCPHelper"]
