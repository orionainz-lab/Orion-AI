"""
Connector Management API Routes

FastAPI endpoints for connector configuration and management.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from connectors.services import ConnectorRegistry, CredentialManager
from supabase import create_client, Client
import os

router = APIRouter(prefix="/api/connectors", tags=["connectors"])


# ============================================
# Dependency Injection
# ============================================

def get_supabase_client() -> Client:
    """Get authenticated Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise HTTPException(
            status_code=500,
            detail="Supabase not configured"
        )
    return create_client(url, key)


def get_credential_manager() -> CredentialManager:
    """Get credential manager"""
    return CredentialManager()


def get_registry(
    db: Client = Depends(get_supabase_client),
    creds: CredentialManager = Depends(get_credential_manager)
) -> ConnectorRegistry:
    """Get connector registry"""
    return ConnectorRegistry(db, creds)


# ============================================
# Request/Response Models
# ============================================

class ConnectorResponse(BaseModel):
    """Connector definition"""
    id: str
    name: str
    type: str
    description: Optional[str]
    version: str
    capabilities: List[str]
    status: str
    documentation_url: Optional[str]


class CreateConfigRequest(BaseModel):
    """Request to create connector config"""
    connector_name: str
    config_name: str
    config: Dict[str, Any]
    credentials: Dict[str, str]


class ConfigResponse(BaseModel):
    """Connector configuration"""
    id: str
    connector_id: str
    name: str
    config: Dict[str, Any]
    is_active: bool
    sync_status: str
    last_sync_at: Optional[str]
    error_message: Optional[str]


# ============================================
# Connector Endpoints (System-Level)
# ============================================

@router.get("/", response_model=List[ConnectorResponse])
async def list_connectors(
    status: str = "active",
    registry: ConnectorRegistry = Depends(get_registry)
):
    """
    List available connectors.
    
    Query params:
    - status: Filter by status (active/deprecated/disabled)
    """
    try:
        connectors = await registry.list_connectors(status)
        return connectors
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list connectors: {str(e)}"
        )


@router.get("/{connector_name}", response_model=ConnectorResponse)
async def get_connector(
    connector_name: str,
    registry: ConnectorRegistry = Depends(get_registry)
):
    """Get connector details"""
    try:
        connector = await registry.get_connector(connector_name)
        if not connector:
            raise HTTPException(
                status_code=404,
                detail=f"Connector not found: {connector_name}"
            )
        return connector
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get connector: {str(e)}"
        )


# ============================================
# Config Endpoints (User-Level)
# ============================================

@router.post("/configs", response_model=ConfigResponse)
async def create_config(
    request: CreateConfigRequest,
    user_id: str,  # TODO: Get from JWT
    registry: ConnectorRegistry = Depends(get_registry)
):
    """
    Create connector configuration.
    
    Body:
    - connector_name: Which connector to configure
    - config_name: Human-readable name
    - config: Configuration settings
    - credentials: API keys (will be encrypted)
    """
    try:
        config = await registry.create_config(
            connector_name=request.connector_name,
            user_id=user_id,
            config_name=request.config_name,
            config_data=request.config,
            credentials=request.credentials
        )
        return config
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create config: {str(e)}"
        )


@router.get("/configs", response_model=List[ConfigResponse])
async def list_configs(
    user_id: str,  # TODO: Get from JWT
    connector_name: Optional[str] = None,
    registry: ConnectorRegistry = Depends(get_registry)
):
    """
    List user's connector configurations.
    
    Query params:
    - connector_name: Optional filter by connector
    """
    try:
        configs = await registry.list_configs(
            user_id=user_id,
            connector_name=connector_name
        )
        return configs
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list configs: {str(e)}"
        )


@router.get("/configs/{config_id}", response_model=ConfigResponse)
async def get_config(
    config_id: str,
    registry: ConnectorRegistry = Depends(get_registry)
):
    """Get configuration details"""
    try:
        config = await registry.get_config(config_id)
        if not config:
            raise HTTPException(
                status_code=404,
                detail=f"Config not found: {config_id}"
            )
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get config: {str(e)}"
        )


@router.delete("/configs/{config_id}")
async def delete_config(
    config_id: str,
    registry: ConnectorRegistry = Depends(get_registry)
):
    """Delete configuration and credentials"""
    try:
        await registry.delete_config(config_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete config: {str(e)}"
        )
