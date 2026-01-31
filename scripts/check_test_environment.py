#!/usr/bin/env python3
"""
API Server Health Check

Verifies the API server is running and accessible before running integration tests.
"""

import httpx
import sys
import os
from dotenv import load_dotenv

load_dotenv()


def check_api_health(base_url: str) -> bool:
    """Check if API server is responding."""
    try:
        response = httpx.get(f"{base_url}/health", timeout=5.0)
        
        if response.status_code == 200:
            print(f"[PASS] API server is healthy at {base_url}")
            print(f"       Response: {response.json()}")
            return True
        else:
            print(f"[FAIL] API returned status {response.status_code}")
            return False
    
    except httpx.ConnectError:
        print(f"[FAIL] Cannot connect to API at {base_url}")
        print("       Make sure the API server is running:")
        print("       uvicorn api.main:app --reload")
        return False
    
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def check_supabase() -> bool:
    """Check Supabase connection."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("[FAIL] Supabase credentials not configured")
        return False
    
    try:
        from supabase import create_client
        client = create_client(url, key)
        
        # Test query
        result = client.table("organizations").select("id").limit(1).execute()
        
        print(f"[PASS] Supabase connected")
        return True
    
    except Exception as e:
        print(f"[FAIL] Supabase connection failed: {e}")
        return False


def check_redis() -> bool:
    """Check Redis connection."""
    redis_url = os.getenv("REDIS_URL")
    
    if not redis_url:
        print("[WARN] Redis URL not configured")
        return False
    
    try:
        import redis
        r = redis.from_url(redis_url)
        r.ping()
        
        print(f"[PASS] Redis connected")
        return True
    
    except Exception as e:
        print(f"[FAIL] Redis connection failed: {e}")
        return False


def main():
    """Run all health checks."""
    print("=" * 60)
    print("  INTEGRATION TEST ENVIRONMENT CHECK")
    print("=" * 60)
    print()
    
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    results = {
        "api": check_api_health(api_url),
        "supabase": check_supabase(),
        "redis": check_redis()
    }
    
    print()
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"Checks Passed: {passed}/{total}")
    
    if passed == total:
        print("\n[PASS] Environment ready for integration tests")
        sys.exit(0)
    else:
        print("\n[FAIL] Environment not ready. Fix issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
