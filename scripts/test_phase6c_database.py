#!/usr/bin/env python3
"""
Phase 6C Database Integration Tests
====================================
Simple database-focused tests to verify Phase 6C setup.

Usage:
    python scripts/test_phase6c_database.py
"""

import os
import sys
from datetime import datetime, date

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("WARNING: python-dotenv not installed")

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_test(name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {name}")
    if details:
        print(f"      {details}")

def main():
    """Run all Phase 6C database tests."""
    print_section("PHASE 6C DATABASE INTEGRATION TESTS")
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        from supabase import create_client
        
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        results = {}
        
        # ===== TEST 1: Organizations =====
        print_section("TEST 1: Organizations & Multi-Tenancy")
        
        orgs = supabase.table("organizations").select("*").execute()
        results['orgs'] = len(orgs.data) >= 3
        print_test("Organizations exist", results['orgs'], 
                   f"Found {len(orgs.data)} organizations")
        
        if orgs.data:
            for org in orgs.data:
                print(f"      - {org['name']} ({org['slug']}, tier: {org['tier']})")
        
        # ===== TEST 2: Teams =====
        print_section("TEST 2: Teams")
        
        teams = supabase.table("teams").select("*").execute()
        results['teams'] = len(teams.data) >= 6
        print_test("Teams exist", results['teams'],
                   f"Found {len(teams.data)} teams")
        
        # ===== TEST 3: RBAC System =====
        print_section("TEST 3: RBAC System")
        
        roles = supabase.table("roles").select("*").eq("is_system_role", True).execute()
        results['roles'] = len(roles.data) == 5
        print_test("System roles", results['roles'],
                   f"Found {len(roles.data)} system roles")
        
        if roles.data:
            for role in roles.data:
                perm_count = len(role.get('permissions', []))
                print(f"      - {role['name']}: {perm_count} permissions")
        
        permissions = supabase.table("permissions").select("*").execute()
        results['permissions'] = len(permissions.data) >= 32
        print_test("Permissions defined", results['permissions'],
                   f"Found {len(permissions.data)} permissions")
        
        # ===== TEST 4: SSO Configurations =====
        print_section("TEST 4: SSO Integration")
        
        sso_configs = supabase.table("sso_configurations").select("*").execute()
        results['sso'] = len(sso_configs.data) >= 3
        print_test("SSO configurations", results['sso'],
                   f"Found {len(sso_configs.data)} SSO providers")
        
        if sso_configs.data:
            for config in sso_configs.data:
                org_name = next((o['name'] for o in orgs.data if o['id'] == config['org_id']), 'Unknown')
                print(f"      - {config['provider']} ({config['protocol']}) for {org_name}")
        
        # ===== TEST 5: Audit Events Table =====
        print_section("TEST 5: Audit Logging")
        
        # Test audit event creation
        test_org_id = orgs.data[0]['id'] if orgs.data else None
        if test_org_id:
            audit_event = supabase.table("audit_events").insert({
                "org_id": test_org_id,
                "action": "test",
                "resource_type": "system",
                "details": {"test": "Phase 6C database test"},
                "compliance_tags": ["test"]
            }).execute()
            
            results['audit'] = len(audit_event.data) > 0
            has_signature = audit_event.data[0].get('signature') is not None if audit_event.data else False
            print_test("Create audit event", results['audit'],
                       f"Event created with signature: {has_signature}")
            
            if audit_event.data and audit_event.data[0].get('signature'):
                sig_len = len(audit_event.data[0]['signature'])
                print(f"      Signature length: {sig_len} characters (HMAC-SHA256)")
        else:
            results['audit'] = False
            print_test("Create audit event", False, "No test organization found")
        
        # ===== TEST 6: Brand Configurations =====
        print_section("TEST 6: White-Label Branding")
        
        # Test brand config creation
        if test_org_id:
            # Check if config already exists
            existing_brand = supabase.table("brand_configs").select("*").eq("org_id", test_org_id).execute()
            
            if not existing_brand.data:
                brand_config = supabase.table("brand_configs").insert({
                    "org_id": test_org_id,
                    "primary_color": "#3B82F6",
                    "secondary_color": "#10B981",
                    "accent_color": "#8B5CF6",
                    "email_from_name": "Orion AI Test"
                }).execute()
                results['branding'] = len(brand_config.data) > 0
                print_test("Create brand config", results['branding'],
                           f"Brand config created for org")
            else:
                results['branding'] = True
                print_test("Brand config exists", True,
                           f"Found existing brand config")
        else:
            results['branding'] = False
            print_test("Create brand config", False, "No test organization found")
        
        # Check storage bucket
        try:
            bucket_name = os.getenv("BRAND_ASSETS_BUCKET", "brand-assets")
            files = supabase.storage.from_(bucket_name).list()
            print_test("Storage bucket accessible", True,
                       f"Bucket '{bucket_name}' contains {len(files)} files")
        except Exception as e:
            print_test("Storage bucket accessible", False,
                       f"Error: {str(e)[:50]}")
        
        # ===== TEST 7: Rate Limiting & Quotas =====
        print_section("TEST 7: API Rate Limiting")
        
        # Create monthly quota
        if test_org_id:
            current_month = date.today().replace(day=1)
            existing_quota = supabase.table("monthly_quotas").select("*").eq("org_id", test_org_id).eq("month", current_month.isoformat()).execute()
            
            if not existing_quota.data:
                quota = supabase.table("monthly_quotas").insert({
                    "org_id": test_org_id,
                    "month": current_month.isoformat(),
                    "api_calls_used": 100,
                    "data_volume_gb_used": 0.5,
                    "quota_exceeded": False
                }).execute()
                results['quotas'] = len(quota.data) > 0
                print_test("Create quota tracking", results['quotas'],
                           f"Quota record created")
            else:
                results['quotas'] = True
                quota_data = existing_quota.data[0]
                print_test("Quota tracking exists", True,
                           f"API calls: {quota_data['api_calls_used']}")
        
        # Test Redis connection
        try:
            import redis.asyncio as redis
            import asyncio
            
            async def test_redis():
                redis_url = os.getenv("REDIS_URL")
                client = redis.from_url(redis_url, decode_responses=True)
                await client.ping()
                await client.aclose()
                return True
            
            redis_ok = asyncio.run(test_redis())
            print_test("Redis connection", redis_ok,
                       "Connected to Upstash Redis")
        except Exception as e:
            print_test("Redis connection", False,
                       f"Error: {str(e)[:50]}")
        
        # ===== TEST 8: Monitoring & Alerts =====
        print_section("TEST 8: Enterprise Monitoring")
        
        # Check alert rules
        alerts = supabase.table("alerts").select("*").eq("enabled", True).execute()
        results['alerts'] = len(alerts.data) >= 5
        print_test("Alert rules configured", results['alerts'],
                   f"Found {len(alerts.data)} active alert rules")
        
        if alerts.data:
            for alert in alerts.data[:3]:  # Show first 3
                print(f"      - {alert['alert_name']} ({alert['alert_type']}, {alert['severity']})")
        
        # Check health checks
        health_checks = supabase.table("health_checks").select("*").limit(10).execute()
        results['health'] = len(health_checks.data) > 0
        print_test("Health checks recorded", results['health'],
                   f"Found {len(health_checks.data)} health check records")
        
        # Create a test health check
        test_health = supabase.table("health_checks").insert({
            "check_type": "api",
            "check_name": "Test Health Check",
            "status": "healthy",
            "response_time_ms": 42,
            "metadata": {"test": True}
        }).execute()
        print_test("Create health check", len(test_health.data) > 0,
                   "Test health check created")
        
        # ===== SUMMARY =====
        print_section("TEST SUMMARY")
        
        total = len(results)
        passed = sum(1 for v in results.values() if v)
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, passed in results.items():
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if all(results.values()):
            print("\n" + "=" * 60)
            print("  ALL DATABASE TESTS PASSED!")
            print("  Phase 6C database is fully functional.")
            print("=" * 60)
            return 0
        else:
            print("\n" + "=" * 60)
            print("  SOME TESTS FAILED")
            print("  Review the errors above.")
            print("=" * 60)
            return 1
            
    except Exception as e:
        print(f"\n[FATAL ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
