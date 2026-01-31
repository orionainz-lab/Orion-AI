"""
Phase 6C: Enterprise Monitoring - Health Check Service
Monitors system health and service availability.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import httpx
from supabase import Client


class HealthStatus(str, Enum):
    """Health check statuses"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


@dataclass
class HealthCheckResult:
    """Health check result"""
    check_type: str
    check_name: str
    status: HealthStatus
    response_time_ms: int
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    timestamp: datetime = None


class HealthChecker:
    """
    System health checker.
    
    Features:
    - API endpoint health checks
    - Database connectivity checks
    - Redis connectivity checks
    - External service checks
    - Configurable check intervals
    - Persistent health history
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
    
    # ========================================
    # HEALTH CHECKS
    # ========================================
    
    async def check_api_health(
        self,
        endpoint: str,
        expected_status: int = 200
    ) -> HealthCheckResult:
        """Check API endpoint health"""
        start_time = datetime.now()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, timeout=10.0)
                
                response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                if response.status_code == expected_status:
                    status = HealthStatus.HEALTHY
                    error_message = None
                else:
                    status = HealthStatus.DEGRADED
                    error_message = f"Unexpected status code: {response.status_code}"
                
                return HealthCheckResult(
                    check_type="api",
                    check_name=endpoint,
                    status=status,
                    response_time_ms=response_time,
                    error_message=error_message,
                    metadata={"status_code": response.status_code},
                    timestamp=datetime.now()
                )
        
        except Exception as e:
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return HealthCheckResult(
                check_type="api",
                check_name=endpoint,
                status=HealthStatus.DOWN,
                response_time_ms=response_time,
                error_message=str(e),
                timestamp=datetime.now()
            )
    
    async def check_database_health(self) -> HealthCheckResult:
        """Check database connectivity"""
        start_time = datetime.now()
        
        try:
            # Simple query to test connection
            response = self.client.table("organizations").select("id").limit(1).execute()
            
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return HealthCheckResult(
                check_type="database",
                check_name="PostgreSQL",
                status=HealthStatus.HEALTHY,
                response_time_ms=response_time,
                metadata={"connected": True},
                timestamp=datetime.now()
            )
        
        except Exception as e:
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return HealthCheckResult(
                check_type="database",
                check_name="PostgreSQL",
                status=HealthStatus.DOWN,
                response_time_ms=response_time,
                error_message=str(e),
                timestamp=datetime.now()
            )
    
    async def check_redis_health(self, redis_client) -> HealthCheckResult:
        """Check Redis connectivity"""
        start_time = datetime.now()
        
        try:
            await redis_client.ping()
            
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Get memory usage
            info = await redis_client.info("memory")
            memory_used_mb = float(info.get("used_memory", 0)) / (1024 * 1024)
            
            return HealthCheckResult(
                check_type="redis",
                check_name="Upstash Redis",
                status=HealthStatus.HEALTHY,
                response_time_ms=response_time,
                metadata={"memory_used_mb": round(memory_used_mb, 2)},
                timestamp=datetime.now()
            )
        
        except Exception as e:
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return HealthCheckResult(
                check_type="redis",
                check_name="Upstash Redis",
                status=HealthStatus.DOWN,
                response_time_ms=response_time,
                error_message=str(e),
                timestamp=datetime.now()
            )
    
    async def check_external_service(
        self,
        service_name: str,
        check_url: str
    ) -> HealthCheckResult:
        """Check external service health"""
        return await self.check_api_health(check_url)
    
    async def run_all_checks(
        self,
        redis_client=None,
        external_services: Optional[Dict[str, str]] = None
    ) -> List[HealthCheckResult]:
        """Run all health checks"""
        checks = []
        
        # Database
        checks.append(await self.check_database_health())
        
        # Redis (if provided)
        if redis_client:
            checks.append(await self.check_redis_health(redis_client))
        
        # External services
        if external_services:
            for service_name, check_url in external_services.items():
                checks.append(await self.check_external_service(service_name, check_url))
        
        return checks
    
    async def save_check_results(
        self,
        results: List[HealthCheckResult]
    ) -> None:
        """Save health check results to database"""
        for result in results:
            self.client.table("health_checks").insert({
                "check_type": result.check_type,
                "check_name": result.check_name,
                "status": result.status.value,
                "response_time_ms": result.response_time_ms,
                "error_message": result.error_message,
                "metadata": result.metadata or {}
            }).execute()
    
    async def get_recent_checks(
        self,
        check_type: Optional[str] = None,
        check_name: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[HealthCheckResult]:
        """Get recent health check results"""
        start_time = datetime.now() - timedelta(hours=hours)
        
        query = self.client.table("health_checks").select("*")
        
        if check_type:
            query = query.eq("check_type", check_type)
        
        if check_name:
            query = query.eq("check_name", check_name)
        
        response = query.gte(
            "created_at", start_time.isoformat()
        ).order("created_at", desc=True).limit(limit).execute()
        
        if not response.data:
            return []
        
        return [
            HealthCheckResult(
                check_type=r["check_type"],
                check_name=r["check_name"],
                status=HealthStatus(r["status"]),
                response_time_ms=r["response_time_ms"],
                error_message=r.get("error_message"),
                metadata=r.get("metadata", {}),
                timestamp=datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
            )
            for r in response.data
        ]
    
    async def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        # Get recent checks (last hour)
        recent_checks = await self.get_recent_checks(hours=1)
        
        # Group by check type
        by_type = {}
        for check in recent_checks:
            if check.check_type not in by_type:
                by_type[check.check_type] = []
            by_type[check.check_type].append(check)
        
        # Calculate health for each type
        type_health = {}
        for check_type, checks in by_type.items():
            healthy_count = sum(1 for c in checks if c.status == HealthStatus.HEALTHY)
            degraded_count = sum(1 for c in checks if c.status == HealthStatus.DEGRADED)
            down_count = sum(1 for c in checks if c.status == HealthStatus.DOWN)
            
            if down_count > 0:
                overall_status = HealthStatus.DOWN
            elif degraded_count > 0:
                overall_status = HealthStatus.DEGRADED
            else:
                overall_status = HealthStatus.HEALTHY
            
            type_health[check_type] = {
                "status": overall_status.value,
                "healthy": healthy_count,
                "degraded": degraded_count,
                "down": down_count,
                "total_checks": len(checks)
            }
        
        # Overall system health
        if any(h["status"] == "down" for h in type_health.values()):
            system_status = HealthStatus.DOWN
        elif any(h["status"] == "degraded" for h in type_health.values()):
            system_status = HealthStatus.DEGRADED
        else:
            system_status = HealthStatus.HEALTHY
        
        return {
            "system_status": system_status.value,
            "components": type_health,
            "last_check": recent_checks[0].timestamp.isoformat() if recent_checks else None
        }


# Background health checker
class BackgroundHealthChecker:
    """
    Runs health checks in the background at regular intervals.
    """
    
    def __init__(
        self,
        health_checker: HealthChecker,
        check_interval: int = 60  # seconds
    ):
        self.health_checker = health_checker
        self.check_interval = check_interval
        self.running = False
    
    async def start(
        self,
        redis_client=None,
        external_services: Optional[Dict[str, str]] = None
    ):
        """Start background health checking"""
        self.running = True
        
        while self.running:
            try:
                # Run checks
                results = await self.health_checker.run_all_checks(
                    redis_client=redis_client,
                    external_services=external_services
                )
                
                # Save results
                await self.health_checker.save_check_results(results)
                
                # Check for alerts
                # ... (alert checking logic)
                
            except Exception as e:
                print(f"Health check error: {e}")
            
            # Wait for next interval
            await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """Stop background health checking"""
        self.running = False


# FastAPI endpoint for health checks
"""
from fastapi import FastAPI
from services.monitoring.health_checker import HealthChecker, HealthStatus

app = FastAPI()
health_checker = HealthChecker(supabase_client)

@app.get("/health")
async def health_check():
    '''Health check endpoint'''
    summary = await health_checker.get_system_health_summary()
    
    status_code = 200
    if summary["system_status"] == HealthStatus.DOWN.value:
        status_code = 503
    elif summary["system_status"] == HealthStatus.DEGRADED.value:
        status_code = 200  # Still operational
    
    return Response(
        content=json.dumps(summary),
        status_code=status_code,
        media_type="application/json"
    )

@app.get("/health/detailed")
async def detailed_health():
    '''Detailed health status'''
    recent_checks = await health_checker.get_recent_checks(hours=24)
    
    return {
        "checks": [
            {
                "type": c.check_type,
                "name": c.check_name,
                "status": c.status.value,
                "response_time_ms": c.response_time_ms,
                "timestamp": c.timestamp.isoformat()
            }
            for c in recent_checks
        ]
    }
"""
