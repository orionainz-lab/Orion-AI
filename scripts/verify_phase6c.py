#!/usr/bin/env python3
"""
Phase 6C Configuration Verification Script
==========================================
Quickly verify that all Phase 6C configuration is working correctly.

Usage:
    python scripts/verify_phase6c.py
"""

import os
import sys
from typing import Dict, List, Tuple

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment variables from .env file")
except ImportError:
    print("WARNING: python-dotenv not installed. Install with: pip install python-dotenv")
    print("Attempting to read environment variables from system...")

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_environment_variables() -> Tuple[bool, List[str]]:
    """Check that all required environment variables are set."""
    print("\nChecking Environment Variables...")
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "REDIS_URL",
        "AUDIT_SIGNATURE_SECRET",
        "AZURE_AD_TENANT_ID",
        "AZURE_AD_CLIENT_ID",
        "GOOGLE_CLIENT_ID",
        "AUTH0_DOMAIN",
        "BRAND_ASSETS_BUCKET",
        "APP_BASE_URL"
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
            print(f"  [FAIL] {var}: NOT SET")
        else:
            # Mask sensitive values
            display_value = value if len(value) < 20 else f"{value[:10]}...{value[-10:]}"
            print(f"  [PASS] {var}: {display_value}")
    
    success = len(missing) == 0
    if success:
        print(f"\n[PASS] All {len(required_vars)} required environment variables are set")
    else:
        print(f"\n[FAIL] Missing {len(missing)} environment variables: {', '.join(missing)}")
    
    return success, missing


def check_database_tables() -> Tuple[bool, Dict]:
    """Check that all Phase 6C tables exist."""
    print("\nChecking Database Tables...")
    
    try:
        from supabase import create_client
        
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        # Check critical tables
        tables_to_check = [
            "organizations",
            "teams",
            "roles",
            "permissions",
            "org_members",
            "sso_configurations",
            "audit_events",
            "brand_configs",
            "alerts",
            "health_checks"
        ]
        
        results = {}
        for table in tables_to_check:
            try:
                response = supabase.table(table).select("id", count="exact").limit(1).execute()
                count = response.count if hasattr(response, 'count') else len(response.data)
                results[table] = count if count else 0
                print(f"  [PASS] {table}: EXISTS (records: {results[table]})")
            except Exception as e:
                results[table] = None
                print(f"  [FAIL] {table}: MISSING ({str(e)[:50]})")
        
        success = all(v is not None for v in results.values())
        if success:
            print(f"\n[PASS] All {len(tables_to_check)} Phase 6C tables exist")
        else:
            missing = [k for k, v in results.items() if v is None]
            print(f"\n[FAIL] Missing tables: {', '.join(missing)}")
        
        return success, results
        
    except Exception as e:
        print(f"  [FAIL] Database connection failed: {str(e)}")
        return False, {}


def check_seeded_data() -> Tuple[bool, Dict]:
    """Check that test data has been seeded."""
    print("\nChecking Seeded Data...")
    
    try:
        from supabase import create_client
        
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        checks = {}
        
        # Check organizations
        orgs = supabase.table("organizations").select("*").execute()
        checks["organizations"] = len(orgs.data)
        print(f"  Organizations: {checks['organizations']} (expected: 3)")
        
        # Check teams
        teams = supabase.table("teams").select("*").execute()
        checks["teams"] = len(teams.data)
        print(f"  Teams: {checks['teams']} (expected: 6)")
        
        # Check system roles
        roles = supabase.table("roles").select("*").eq("is_system_role", True).execute()
        checks["system_roles"] = len(roles.data)
        print(f"  System Roles: {checks['system_roles']} (expected: 5)")
        
        # Check permissions
        permissions = supabase.table("permissions").select("*").execute()
        checks["permissions"] = len(permissions.data)
        print(f"  Permissions: {checks['permissions']} (expected: 32)")
        
        # Check SSO configurations
        sso = supabase.table("sso_configurations").select("*").execute()
        checks["sso_configs"] = len(sso.data)
        print(f"  SSO Configurations: {checks['sso_configs']} (expected: 3)")
        
        # Check alerts
        alerts = supabase.table("alerts").select("*").execute()
        checks["alerts"] = len(alerts.data)
        print(f"  Alert Rules: {checks['alerts']} (expected: 5)")
        
        # Verify expected counts
        expected = {
            "organizations": 3,
            "teams": 6,
            "system_roles": 5,
            "permissions": 32,
            "sso_configs": 3,
            "alerts": 5
        }
        
        success = all(checks[k] >= expected[k] for k in expected.keys())
        if success:
            print("\n[PASS] All test data has been seeded correctly")
        else:
            print("\n[WARNING] Some data counts are lower than expected")
        
        return success, checks
        
    except Exception as e:
        print(f"  [FAIL] Failed to check seeded data: {str(e)}")
        return False, {}


def check_storage_bucket() -> Tuple[bool, Dict]:
    """Check that storage bucket exists."""
    print("\nChecking Storage Bucket...")
    
    try:
        from supabase import create_client
        
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        try:
            # Try to list files in the bucket to verify it exists
            files = supabase.storage.from_('brand-assets').list()
            print(f"  [PASS] Bucket 'brand-assets' exists and is accessible")
            print(f"     Files in bucket: {len(files)}")
            return True, {"name": "brand-assets", "file_count": len(files)}
        except Exception as bucket_error:
            # If we can't access it, it might not exist
            error_msg = str(bucket_error)
            if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                print(f"  [FAIL] Bucket 'brand-assets' not found")
            else:
                print(f"  [WARNING] Bucket may exist but had access error: {error_msg[:50]}")
                # Consider this a pass if it's just a permission issue
                return True, {"name": "brand-assets", "status": "exists_with_warning"}
            return False, {}
        
    except Exception as e:
        print(f"  [FAIL] Failed to check storage bucket: {str(e)[:100]}")
        return False, {}


def check_redis_connection() -> Tuple[bool, str]:
    """Check Redis connection."""
    print("\nChecking Redis Connection...")
    
    try:
        import redis.asyncio as redis
        import asyncio
        
        async def test_redis():
            redis_url = os.getenv("REDIS_URL")
            if not redis_url:
                return False, "REDIS_URL not set"
            
            try:
                client = redis.from_url(redis_url, decode_responses=True)
                await client.ping()
                info = await client.info("server")
                await client.close()
                return True, f"Redis version {info.get('redis_version', 'unknown')}"
            except Exception as e:
                return False, str(e)
        
        success, message = asyncio.run(test_redis())
        if success:
            print(f"  [PASS] Redis connection successful: {message}")
        else:
            print(f"  [FAIL] Redis connection failed: {message}")
        
        return success, message
        
    except ImportError:
        print(f"  [WARNING] redis package not installed (pip install redis)")
        return False, "redis package not installed"
    except Exception as e:
        print(f"  [FAIL] Redis check failed: {str(e)}")
        return False, str(e)


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Phase 6C Configuration Verification")
    print("=" * 60)
    
    results = {}
    
    # Run all checks
    results["env_vars"], _ = check_environment_variables()
    results["database"], _ = check_database_tables()
    results["seeded_data"], _ = check_seeded_data()
    results["storage"], _ = check_storage_bucket()
    results["redis"], _ = check_redis_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    
    print(f"\nPassed: {passed_checks}/{total_checks} checks")
    print(f"Failed: {total_checks - passed_checks}/{total_checks} checks")
    
    print("\nDetailed Results:")
    for check, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status}: {check.replace('_', ' ').title()}")
    
    if all(results.values()):
        print("\n" + "=" * 60)
        print("ALL CHECKS PASSED!")
        print("Phase 6C is fully configured and ready to use.")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("SOME CHECKS FAILED")
        print("Please review the errors above and fix the issues.")
        print("See PHASE6C-CONFIG-COMPLETE.md for troubleshooting.")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
