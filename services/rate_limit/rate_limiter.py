"""
Phase 6C: API Rate Limiting - Token Bucket Implementation
Redis-backed token bucket rate limiter with tiered quotas.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
import redis.asyncio as redis
from supabase import Client


class RateLimitTier(str, Enum):
    """Rate limit tiers"""
    FREE = "free"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class RateLimit:
    """Rate limit configuration"""
    requests_per_second: int
    requests_per_hour: int
    requests_per_day: int
    burst_size: int


@dataclass
class RateLimitState:
    """Current rate limit state"""
    allowed: bool
    remaining: int
    reset_at: int  # Unix timestamp
    retry_after: Optional[int] = None  # Seconds


# Tier-based rate limits
RATE_LIMITS = {
    RateLimitTier.FREE: RateLimit(
        requests_per_second=10,
        requests_per_hour=1000,
        requests_per_day=10000,
        burst_size=20
    ),
    RateLimitTier.PROFESSIONAL: RateLimit(
        requests_per_second=100,
        requests_per_hour=50000,
        requests_per_day=500000,
        burst_size=200
    ),
    RateLimitTier.ENTERPRISE: RateLimit(
        requests_per_second=1000,
        requests_per_hour=1000000,
        requests_per_day=10000000,
        burst_size=2000
    )
}


class RateLimiter:
    """
    Redis-backed token bucket rate limiter.
    
    Features:
    - Token bucket algorithm for burst handling
    - Tiered rate limits
    - Multiple time windows (second, hour, day)
    - Monthly quota tracking
    - Redis for distributed rate limiting
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        supabase_client: Client
    ):
        """
        Initialize rate limiter.
        
        Args:
            redis_client: Redis client (async)
            supabase_client: Supabase client for quota tracking
        """
        self.redis = redis_client
        self.supabase = supabase_client
    
    async def check_rate_limit(
        self,
        org_id: str,
        tier: RateLimitTier,
        identifier: str,  # user_id, api_key, ip_address
        endpoint: str = "global"
    ) -> RateLimitState:
        """
        Check if request is allowed under rate limit.
        
        Args:
            org_id: Organization ID
            tier: Rate limit tier
            identifier: Unique identifier (user_id, api_key, IP)
            endpoint: API endpoint (for endpoint-specific limits)
        
        Returns:
            RateLimitState indicating if allowed and remaining tokens
        """
        limits = RATE_LIMITS[tier]
        
        # Check all time windows
        per_second = await self._check_window(
            org_id, identifier, endpoint, "second",
            limits.requests_per_second, 1
        )
        
        per_hour = await self._check_window(
            org_id, identifier, endpoint, "hour",
            limits.requests_per_hour, 3600
        )
        
        per_day = await self._check_window(
            org_id, identifier, endpoint, "day",
            limits.requests_per_day, 86400
        )
        
        # All windows must allow
        if not (per_second.allowed and per_hour.allowed and per_day.allowed):
            # Find which window is blocking
            if not per_second.allowed:
                return per_second
            elif not per_hour.allowed:
                return per_hour
            else:
                return per_day
        
        # Check monthly quota
        quota_ok = await self._check_monthly_quota(org_id)
        
        if not quota_ok:
            return RateLimitState(
                allowed=False,
                remaining=0,
                reset_at=self._get_next_month_timestamp(),
                retry_after=None
            )
        
        # All checks passed
        return RateLimitState(
            allowed=True,
            remaining=min(per_second.remaining, per_hour.remaining, per_day.remaining),
            reset_at=per_second.reset_at
        )
    
    async def consume(
        self,
        org_id: str,
        tier: RateLimitTier,
        identifier: str,
        endpoint: str = "global",
        tokens: int = 1
    ) -> RateLimitState:
        """
        Consume tokens and check rate limit.
        
        Args:
            org_id: Organization ID
            tier: Rate limit tier
            identifier: Unique identifier
            endpoint: API endpoint
            tokens: Number of tokens to consume (default 1)
        
        Returns:
            RateLimitState after consumption
        """
        # Check first
        state = await self.check_rate_limit(org_id, tier, identifier, endpoint)
        
        if not state.allowed:
            return state
        
        # Consume tokens from all windows
        limits = RATE_LIMITS[tier]
        
        await self._consume_window(org_id, identifier, endpoint, "second", tokens, 1)
        await self._consume_window(org_id, identifier, endpoint, "hour", tokens, 3600)
        await self._consume_window(org_id, identifier, endpoint, "day", tokens, 86400)
        
        # Track usage in database
        await self._track_usage(org_id, endpoint, tokens)
        
        # Return updated state
        return await self.check_rate_limit(org_id, tier, identifier, endpoint)
    
    async def _check_window(
        self,
        org_id: str,
        identifier: str,
        endpoint: str,
        window: str,
        limit: int,
        window_seconds: int
    ) -> RateLimitState:
        """Check rate limit for a specific time window"""
        key = f"ratelimit:{org_id}:{identifier}:{endpoint}:{window}"
        
        # Get current count
        current = await self.redis.get(key)
        current_count = int(current) if current else 0
        
        # Get TTL for reset time
        ttl = await self.redis.ttl(key)
        if ttl == -1:  # No expiration set
            ttl = window_seconds
        
        reset_at = int(time.time()) + ttl
        remaining = max(0, limit - current_count)
        
        allowed = current_count < limit
        retry_after = ttl if not allowed else None
        
        return RateLimitState(
            allowed=allowed,
            remaining=remaining,
            reset_at=reset_at,
            retry_after=retry_after
        )
    
    async def _consume_window(
        self,
        org_id: str,
        identifier: str,
        endpoint: str,
        window: str,
        tokens: int,
        window_seconds: int
    ) -> None:
        """Consume tokens from a time window"""
        key = f"ratelimit:{org_id}:{identifier}:{endpoint}:{window}"
        
        # Increment counter
        await self.redis.incr(key, tokens)
        
        # Set expiration if not already set
        ttl = await self.redis.ttl(key)
        if ttl == -1:
            await self.redis.expire(key, window_seconds)
    
    async def _check_monthly_quota(self, org_id: str) -> bool:
        """Check if organization has exceeded monthly quota"""
        from datetime import date
        current_month = date.today().replace(day=1)
        
        response = self.supabase.table("monthly_quotas").select("*").eq(
            "org_id", org_id
        ).eq("month", current_month.isoformat()).execute()
        
        if not response.data:
            return True  # No quota record = OK
        
        quota_data = response.data[0]
        return not quota_data.get("quota_exceeded", False)
    
    async def _track_usage(
        self,
        org_id: str,
        endpoint: str,
        tokens: int = 1
    ) -> None:
        """Track API usage in database"""
        # Update monthly quota
        from datetime import date
        current_month = date.today().replace(day=1)
        
        # Upsert monthly quota
        self.supabase.table("monthly_quotas").upsert({
            "org_id": org_id,
            "month": current_month.isoformat(),
            "api_calls_used": tokens
        }, on_conflict="org_id,month").execute()
    
    def _get_next_month_timestamp(self) -> int:
        """Get Unix timestamp of next month"""
        from datetime import date, timedelta
        today = date.today()
        next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        return int(next_month.strftime("%s"))
    
    async def reset_limits(
        self,
        org_id: str,
        identifier: str,
        endpoint: str = "global"
    ) -> None:
        """Reset rate limits for identifier (admin function)"""
        keys = [
            f"ratelimit:{org_id}:{identifier}:{endpoint}:second",
            f"ratelimit:{org_id}:{identifier}:{endpoint}:hour",
            f"ratelimit:{org_id}:{identifier}:{endpoint}:day"
        ]
        
        for key in keys:
            await self.redis.delete(key)
    
    async def get_usage_stats(
        self,
        org_id: str,
        identifier: str,
        endpoint: str = "global"
    ) -> Dict[str, Any]:
        """Get current usage statistics for identifier"""
        stats = {}
        
        for window in ["second", "hour", "day"]:
            key = f"ratelimit:{org_id}:{identifier}:{endpoint}:{window}"
            current = await self.redis.get(key)
            ttl = await self.redis.ttl(key)
            
            stats[window] = {
                "used": int(current) if current else 0,
                "reset_in_seconds": ttl if ttl > 0 else 0
            }
        
        return stats


# FastAPI middleware for automatic rate limiting
class RateLimitMiddleware:
    """
    Middleware to automatically rate limit requests.
    
    Usage:
        app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)
    """
    
    def __init__(self, app, rate_limiter: RateLimiter):
        self.app = app
        self.rate_limiter = rate_limiter
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        from fastapi import Request, HTTPException
        from services.tenancy.tenant_resolver import TenantContext
        
        request = Request(scope, receive)
        
        # Get tenant context (must be resolved first)
        if not hasattr(request.state, "tenant"):
            # No tenant = skip rate limiting
            await self.app(scope, receive, send)
            return
        
        tenant: TenantContext = request.state.tenant
        
        # Determine identifier (user_id or IP)
        identifier = tenant.user_id or request.client.host
        
        # Check rate limit
        state = await self.rate_limiter.consume(
            org_id=tenant.org_id,
            tier=tenant.tier,
            identifier=identifier,
            endpoint=request.url.path
        )
        
        if not state.allowed:
            # Rate limit exceeded
            from fastapi.responses import JSONResponse
            
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "API rate limit exceeded",
                    "limit": 0,
                    "remaining": state.remaining,
                    "reset_at": state.reset_at,
                    "retry_after": state.retry_after
                },
                headers={
                    "X-RateLimit-Limit": "0",
                    "X-RateLimit-Remaining": str(state.remaining),
                    "X-RateLimit-Reset": str(state.reset_at),
                    "Retry-After": str(state.retry_after) if state.retry_after else "0"
                }
            )
            
            await response(scope, receive, send)
            return
        
        # Add rate limit headers to response
        # ... (implementation for adding headers)
        
        await self.app(scope, receive, send)


# Example usage
"""
import redis.asyncio as redis
from services.rate_limit.rate_limiter import RateLimiter, RateLimitTier, RateLimitMiddleware

# Initialize Redis
redis_client = redis.from_url("rediss://default:xxx@xxx.upstash.io:6379")

# Initialize rate limiter
rate_limiter = RateLimiter(redis_client, supabase_client)

# Check rate limit
state = await rate_limiter.consume(
    org_id="org-123",
    tier=RateLimitTier.PROFESSIONAL,
    identifier="user-456",
    endpoint="/api/connectors"
)

if state.allowed:
    # Process request
    pass
else:
    # Return 429 Too Many Requests
    print(f"Rate limited. Retry after {state.retry_after}s")

# Add middleware to FastAPI
app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)
"""
