"""
Health Check Endpoints

Provides basic and detailed health checks for the API service.
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
from datetime import datetime
import asyncio
import os

router = APIRouter()

# Service metadata
SERVICE_NAME = "orion-api"
SERVICE_VERSION = "1.0.0"


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        dict: Basic health status
    """
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/detailed", status_code=status.HTTP_200_OK)
async def detailed_health() -> Dict[str, Any]:
    """
    Detailed health check with dependency validation.
    
    Checks:
    - Supabase database connection
    - Temporal workflow engine
    - Redis cache (if configured)
    
    Returns:
        dict: Detailed health status with all checks
    """
    checks = {}
    
    # Check Supabase
    checks["supabase"] = await check_supabase()
    
    # Check Temporal
    checks["temporal"] = await check_temporal()
    
    # Check Redis (optional)
    if os.getenv("REDIS_URL"):
        checks["redis"] = await check_redis()
    
    # Determine overall status
    all_healthy = all(c["healthy"] for c in checks.values())
    overall_status = "healthy" if all_healthy else "degraded"
    
    return {
        "status": overall_status,
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


async def check_supabase() -> Dict[str, Any]:
    """Check Supabase database connection"""
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            return {
                "healthy": False,
                "message": "Supabase credentials not configured"
            }
        
        # Create client and test connection
        supabase = create_client(supabase_url, supabase_key)
        
        # Simple query to test connection
        response = supabase.from_("process_events").select("id").limit(1).execute()
        
        return {
            "healthy": True,
            "message": "Connected to Supabase",
            "latency_ms": 0  # Could add actual latency measurement
        }
        
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Supabase check failed: {str(e)}"
        }


async def check_temporal() -> Dict[str, Any]:
    """Check Temporal workflow engine connection"""
    try:
        from temporalio.client import Client
        
        temporal_address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
        
        # Connect to Temporal
        client = await Client.connect(temporal_address)
        
        # Test connection by getting workflow service
        await client.workflow_service.get_system_info()
        
        return {
            "healthy": True,
            "message": "Connected to Temporal",
            "address": temporal_address
        }
        
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Temporal check failed: {str(e)}"
        }


async def check_redis() -> Dict[str, Any]:
    """Check Redis cache connection (optional)"""
    try:
        import redis.asyncio as redis
        
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            return {
                "healthy": False,
                "message": "Redis URL not configured"
            }
        
        # Connect to Redis
        client = redis.from_url(redis_url)
        
        # Ping Redis
        await client.ping()
        await client.close()
        
        return {
            "healthy": True,
            "message": "Connected to Redis"
        }
        
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Redis check failed: {str(e)}"
        }


@router.get("/health/readiness")
async def readiness_check() -> JSONResponse:
    """
    Kubernetes-style readiness probe.
    
    Returns 200 if service is ready to accept traffic.
    """
    # Check if service is initialized
    # Add any initialization checks here
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"ready": True}
    )


@router.get("/health/liveness")
async def liveness_check() -> JSONResponse:
    """
    Kubernetes-style liveness probe.
    
    Returns 200 if service is alive (even if degraded).
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"alive": True}
    )
