"""
Rate Limiting Load Test using Locust

Tests the Redis-backed rate limiting system under load.
Validates tier-based quotas and error responses.
"""

from locust import HttpUser, task, between, events
import os
from dotenv import load_dotenv

load_dotenv()


class RateLimitUser(HttpUser):
    """Simulated user for rate limiting tests."""
    
    wait_time = between(0.01, 0.1)  # Very short wait for load testing
    
    def on_start(self):
        """Called when a user starts."""
        self.api_key = os.getenv("TEST_API_KEY", "test-api-key")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @task(weight=10)
    def test_connector_list(self):
        """
        RATE-001: Test rate limiting on connector list endpoint.
        
        Free tier: 60 req/min
        """
        with self.client.get(
            "/api/connectors",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                # Check rate limit headers
                remaining = response.headers.get("X-RateLimit-Remaining")
                limit = response.headers.get("X-RateLimit-Limit")
                
                if remaining and int(remaining) < 10:
                    print(f"⚠️ Rate limit approaching: {remaining}/{limit}")
                
                response.success()
            
            elif response.status_code == 429:
                # Rate limit exceeded - this is expected
                response.failure("Rate limit exceeded (429)")
            
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(weight=5)
    def test_workflow_list(self):
        """RATE-002: Test rate limiting on workflow endpoint."""
        with self.client.get(
            "/api/workflows",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code in [200, 429]:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task(weight=3)
    def test_analytics_endpoint(self):
        """RATE-003: Test rate limiting on analytics endpoint."""
        with self.client.get(
            "/api/analytics/metrics",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code in [200, 429]:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("=" * 60)
    print("RATE LIMITING LOAD TEST")
    print("=" * 60)
    print("Testing endpoints:")
    print("  - /api/connectors")
    print("  - /api/workflows")
    print("  - /api/analytics/metrics")
    print("")
    print("Rate limits (free tier):")
    print("  - 60 requests/minute")
    print("  - 1,000 requests/hour")
    print("  - 10,000 requests/month")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    stats = environment.stats
    print("")
    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Total Requests: {stats.total.num_requests}")
    print(f"Failed Requests: {stats.total.num_failures}")
    print(f"Success Rate: {(1 - stats.total.fail_ratio) * 100:.2f}%")
    print(f"Median Response Time: {stats.total.median_response_time}ms")
    print(f"95th Percentile: {stats.total.get_response_time_percentile(0.95)}ms")
    print("=" * 60)
    
    # Count 429 responses
    rate_limit_hits = sum(
        stat.num_failures 
        for stat in stats.entries.values() 
        if "429" in str(stat.name)
    )
    
    if rate_limit_hits > 0:
        print(f"✅ Rate limiting working: {rate_limit_hits} requests blocked")
    else:
        print("⚠️ No rate limit hits detected - may need higher load")
