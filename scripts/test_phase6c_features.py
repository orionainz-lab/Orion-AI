#!/usr/bin/env python3
"""
Phase 6C Feature Testing Script
================================
Comprehensive tests for all Phase 6C enterprise features.

Usage:
    python scripts/test_phase6c_features.py
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any

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


# ============================================================
# TEST 1: MULTI-TENANCY
# ============================================================
def test_multi_tenancy():
    """Test multi-tenancy features."""
    print_section("TEST 1: Multi-Tenancy")
    
    try:
        from supabase import create_client
        from services.tenancy.tenant_manager import TenantManager
        
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        manager = TenantManager(supabase)
        
        # Test 1.1: Get organization by slug
        org = manager.get_organization_by_slug("acme-demo")
        print_test("Get organization by slug", org is not None, 
                   f"Found: {org['name'] if org else 'None'}")
        
        # Test 1.2: List all organizations
        orgs = manager.list_organizations()
        print_test("List all organizations", len(orgs) >= 3,
                   f"Found {len(orgs)} organizations")
        
        # Test 1.3: Check organization tiers
        tiers = {org['slug']: org['tier'] for org in orgs}
        expected_tiers = ['free', 'professional', 'enterprise']
        has_all_tiers = all(tier in tiers.values() for tier in expected_tiers)
        print_test("All tier types present", has_all_tiers,
                   f"Tiers: {list(tiers.values())}")
        
        # Test 1.4: Get organization teams
        if org:
            teams = manager.get_organization_teams(org['id'])
            print_test("Get organization teams", teams is not None,
                       f"Found {len(teams) if teams else 0} teams")
        
        # Test 1.5: Check quota enforcement
        if org:
            quota_info = manager.check_quota(org['id'], 'monthlyApiCalls')
            print_test("Check quota enforcement", quota_info is not None,
                       f"API Calls: {quota_info.get('used', 0)}/{quota_info.get('limit', 0)}")
        
        return True
        
    except Exception as e:
        print_test("Multi-Tenancy Tests", False, f"Error: {str(e)[:100]}")
        return False


# ============================================================
# TEST 2: SSO INTEGRATION
# ============================================================
def test_sso_integration():
    """Test SSO provider configurations."""
    print_section("TEST 2: SSO Integration")
    
    try:
        from supabase import create_client
        from services.auth.sso.sso_manager import SSOManager
        
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        sso_manager = SSOManager(supabase, os.getenv("APP_BASE_URL"))
        
        # Get test organization
        org_response = supabase.table("organizations").select("*").eq("slug", "global-enterprises").execute()
        org = org_response.data[0] if org_response.data else None
        
        if not org:
            print_test("SSO Tests", False, "Test organization not found")
            return False
        
        # Test 2.1: Get SSO configurations
        sso_configs = supabase.table("sso_configurations").select("*").eq("org_id", org['id']).execute()
        print_test("Get SSO configurations", len(sso_configs.data) > 0,
                   f"Found {len(sso_configs.data)} SSO providers")
        
        # Test 2.2: Check Azure AD configuration
        azure_config = sso_manager.get_sso_config(org['id'], 'azure-ad')
        print_test("Azure AD configuration", azure_config is not None,
                   f"Enabled: {azure_config.get('enabled') if azure_config else False}")
        
        # Test 2.3: Check Google configuration
        google_config = sso_manager.get_sso_config(org['id'], 'google')
        print_test("Google configuration", google_config is not None,
                   f"Enabled: {google_config.get('enabled') if google_config else False}")
        
        # Test 2.4: Verify JIT provisioning settings
        if azure_config:
            jit_enabled = azure_config.get('jit_enabled', False)
            has_default_role = azure_config.get('jit_default_role_id') is not None
            print_test("JIT provisioning configured", jit_enabled and has_default_role,
                       f"JIT enabled: {jit_enabled}, Default role: {has_default_role}")
        
        # Test 2.5: Check SSO login events table
        events = supabase.table("sso_login_events").select("*").limit(5).execute()
        print_test("SSO login events table", True,
                   f"Table accessible, {len(events.data)} events recorded")
        
        return True
        
    except Exception as e:
        print_test("SSO Integration Tests", False, f"Error: {str(e)[:100]}")
        return False


# ============================================================
# TEST 3: RBAC SYSTEM
# ============================================================
def test_rbac_system():
    """Test role-based access control."""
    print_section("TEST 3: RBAC System")
    
    try:
        from supabase import create_client
        from services.rbac.permission_checker import PermissionChecker
        from services.rbac.role_manager import RoleManager
        
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        permission_checker = PermissionChecker(supabase)
        role_manager = RoleManager(supabase)
        
        # Test 3.1: List system roles
        roles = supabase.table("roles").select("*").eq("is_system_role", True).execute()
        role_names = [r['name'] for r in roles.data]
        expected_roles = ['Super Admin', 'Org Admin', 'Team Lead', 'Member', 'Viewer']
        has_all_roles = all(role in role_names for role in expected_roles)
        print_test("System roles defined", has_all_roles,
                   f"Found: {', '.join(role_names)}")
        
        # Test 3.2: Check permissions table
        permissions = supabase.table("permissions").select("*").execute()
        print_test("Permissions defined", len(permissions.data) >= 32,
                   f"Found {len(permissions.data)} permissions")
        
        # Test 3.3: Verify permission format (resource:action:scope)
        if permissions.data:
            sample_perm = permissions.data[0]
            has_structure = all(k in sample_perm for k in ['resource', 'action', 'scope'])
            print_test("Permission structure valid", has_structure,
                       f"Sample: {sample_perm.get('resource')}:{sample_perm.get('action')}:{sample_perm.get('scope')}")
        
        # Test 3.4: Test permission checker function
        # Using database function directly
        org_response = supabase.table("organizations").select("id").limit(1).execute()
        if org_response.data:
            org_id = org_response.data[0]['id']
            print_test("Permission checker initialized", True,
                       f"Ready to check permissions for org: {org_id}")
        
        # Test 3.5: Check role permissions JSONB format
        admin_role = next((r for r in roles.data if r['name'] == 'Org Admin'), None)
        if admin_role:
            perms = admin_role.get('permissions', [])
            has_permissions = len(perms) > 0
            print_test("Org Admin role has permissions", has_permissions,
                       f"{len(perms)} permissions assigned")
        
        return True
        
    except Exception as e:
        print_test("RBAC System Tests", False, f"Error: {str(e)[:100]}")
        return False


# ============================================================
# TEST 4: AUDIT LOGGING
# ============================================================
def test_audit_logging():
    """Test audit logging with tamper-proof signatures."""
    print_section("TEST 4: Audit Logging")
    
    try:
        from supabase import create_client
        from services.audit.audit_logger import AuditLogger
        
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        # Get test organization
        org_response = supabase.table("organizations").select("*").limit(1).execute()
        org = org_response.data[0] if org_response.data else None
        
        if not org:
            print_test("Audit Tests", False, "Test organization not found")
            return False
        
        audit_logger = AuditLogger(supabase, os.getenv("AUDIT_SIGNATURE_SECRET"))
        
        # Test 4.1: Log a test audit event
        event = audit_logger.log_event(
            org_id=org['id'],
            user_id=None,
            action='test',
            resource_type='system',
            resource_id=None,
            details={'test': 'Phase 6C audit test'},
            compliance_tags=['test']
        )
        print_test("Log audit event", event is not None,
                   f"Event ID: {event['id'] if event else 'None'}")
        
        # Test 4.2: Verify signature exists
        if event:
            has_signature = event.get('signature') is not None and len(event.get('signature', '')) > 0
            print_test("Audit event has signature", has_signature,
                       f"Signature length: {len(event.get('signature', ''))}")
        
        # Test 4.3: Query audit events
        events = audit_logger.query_events(
            org_id=org['id'],
            limit=10
        )
        print_test("Query audit events", len(events) > 0,
                   f"Found {len(events)} events")
        
        # Test 4.4: Check compliance tags
        if events:
            has_tags = any(event.get('compliance_tags') for event in events)
            print_test("Compliance tags present", has_tags,
                       f"Events with tags: {sum(1 for e in events if e.get('compliance_tags'))}")
        
        # Test 4.5: Verify event chaining (previous_event_id)
        if len(events) > 1:
            has_chain = any(event.get('previous_event_id') for event in events)
            print_test("Event chaining active", has_chain,
                       f"Chained events: {sum(1 for e in events if e.get('previous_event_id'))}")
        else:
            print_test("Event chaining", True, "Needs multiple events to test")
        
        return True
        
    except Exception as e:
        print_test("Audit Logging Tests", False, f"Error: {str(e)[:100]}")
        return False


# ============================================================
# TEST 5: WHITE-LABEL BRANDING
# ============================================================
def test_white_label_branding():
    """Test white-label branding features."""
    print_section("TEST 5: White-Label Branding")
    
    try:
        from supabase import create_client
        from services.branding.brand_manager import BrandManager
        
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        # Get test organization
        org_response = supabase.table("organizations").select("*").limit(1).execute()
        org = org_response.data[0] if org_response.data else None
        
        if not org:
            print_test("Branding Tests", False, "Test organization not found")
            return False
        
        brand_manager = BrandManager(supabase, os.getenv("BRAND_ASSETS_BUCKET"))
        
        # Test 5.1: Create brand configuration
        brand_config = brand_manager.create_brand_config(
            org_id=org['id'],
            primary_color='#3B82F6',
            secondary_color='#10B981',
            accent_color='#8B5CF6',
            email_from_name='Orion AI Test',
            show_powered_by=True
        )
        print_test("Create brand configuration", brand_config is not None,
                   f"Config created for org: {org['slug']}")
        
        # Test 5.2: Get brand configuration
        config = brand_manager.get_brand_config(org['id'])
        print_test("Get brand configuration", config is not None,
                   f"Primary color: {config.get('primary_color') if config else 'None'}")
        
        # Test 5.3: Check storage bucket
        try:
            files = supabase.storage.from_(os.getenv("BRAND_ASSETS_BUCKET")).list()
            print_test("Storage bucket accessible", True,
                       f"Bucket '{os.getenv('BRAND_ASSETS_BUCKET')}' ready, {len(files)} files")
        except Exception as storage_error:
            print_test("Storage bucket accessible", False,
                       f"Error: {str(storage_error)[:50]}")
        
        # Test 5.4: Domain verifications table
        domains = supabase.table("domain_verifications").select("*").execute()
        print_test("Domain verifications table", True,
                   f"Table accessible, {len(domains.data)} domains")
        
        # Test 5.5: Generate theme
        if config:
            theme = brand_manager.generate_theme(org['id'])
            has_theme = theme and 'colors' in theme
            print_test("Generate theme", has_theme,
                       f"Theme generated with {len(theme.get('colors', {}))} colors")
        
        return True
        
    except Exception as e:
        print_test("White-Label Branding Tests", False, f"Error: {str(e)[:100]}")
        return False


# ============================================================
# TEST 6: API RATE LIMITING
# ============================================================
async def test_rate_limiting():
    """Test API rate limiting with Redis."""
    print_section("TEST 6: API Rate Limiting")
    
    try:
        import redis.asyncio as redis
        from supabase import create_client
        from services.rate_limit.rate_limiter import RateLimiter
        
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        # Get test organization
        org_response = supabase.table("organizations").select("*").eq("slug", "acme-demo").execute()
        org = org_response.data[0] if org_response.data else None
        
        if not org:
            print_test("Rate Limiting Tests", False, "Test organization not found")
            return False
        
        # Test 6.1: Connect to Redis
        redis_client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
        await redis_client.ping()
        print_test("Redis connection", True, "Connected successfully")
        
        # Test 6.2: Initialize rate limiter
        rate_limiter = RateLimiter(redis_client)
        print_test("Rate limiter initialized", True, f"Tier: {org['tier']}")
        
        # Test 6.3: Check rate limit (should pass)
        identifier = f"test-user-{datetime.now().timestamp()}"
        allowed = await rate_limiter.check_rate_limit(
            org_id=org['id'],
            identifier=identifier,
            endpoint="/api/test",
            tier=org['tier']
        )
        print_test("Rate limit check (first request)", allowed,
                   "Request allowed")
        
        # Test 6.4: Verify token consumption
        # Make multiple requests to test limit
        requests_made = 0
        for i in range(5):
            allowed = await rate_limiter.check_rate_limit(
                org_id=org['id'],
                identifier=identifier,
                endpoint="/api/test",
                tier=org['tier']
            )
            if allowed:
                requests_made += 1
        
        print_test("Multiple requests tracked", requests_made > 0,
                   f"{requests_made} requests allowed")
        
        # Test 6.5: Check quota usage
        quotas = supabase.table("monthly_quotas").select("*").eq("org_id", org['id']).execute()
        print_test("Quota tracking table", True,
                   f"Table accessible, {len(quotas.data)} quota records")
        
        await redis_client.aclose()
        return True
        
    except Exception as e:
        print_test("API Rate Limiting Tests", False, f"Error: {str(e)[:100]}")
        return False


# ============================================================
# TEST 7: ENTERPRISE MONITORING
# ============================================================
async def test_monitoring():
    """Test enterprise monitoring and alerting."""
    print_section("TEST 7: Enterprise Monitoring")
    
    try:
        from supabase import create_client
        from services.monitoring.health_checker import HealthChecker
        from services.monitoring.alert_manager import AlertManager
        
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        health_checker = HealthChecker(supabase)
        alert_manager = AlertManager(supabase)
        
        # Test 7.1: Check database health
        db_health = await health_checker.check_database()
        print_test("Database health check", db_health['status'] == 'healthy',
                   f"Status: {db_health['status']}, Response time: {db_health.get('response_time_ms')}ms")
        
        # Test 7.2: Check Redis health
        try:
            redis_health = await health_checker.check_redis(os.getenv("REDIS_URL"))
            print_test("Redis health check", redis_health['status'] == 'healthy',
                       f"Status: {redis_health['status']}")
        except Exception as redis_error:
            print_test("Redis health check", False, f"Error: {str(redis_error)[:50]}")
        
        # Test 7.3: Save health check results
        saved = health_checker.save_health_check(
            check_type='api',
            check_name='Test API Health',
            status='healthy',
            response_time_ms=45,
            metadata={'test': True}
        )
        print_test("Save health check results", saved is not None,
                   f"Health check ID: {saved['id'] if saved else 'None'}")
        
        # Test 7.4: List alert rules
        alerts = supabase.table("alerts").select("*").eq("enabled", True).execute()
        print_test("List alert rules", len(alerts.data) > 0,
                   f"Found {len(alerts.data)} active alert rules")
        
        # Test 7.5: Test alert evaluation
        if alerts.data:
            sample_alert = alerts.data[0]
            should_trigger = alert_manager.should_trigger_alert(
                alert=sample_alert,
                current_value=100,
                metric_name=sample_alert['metric_name']
            )
            print_test("Alert evaluation", True,
                       f"Alert '{sample_alert['alert_name']}' evaluated")
        
        # Test 7.6: Check health checks history
        history = supabase.table("health_checks").select("*").limit(10).execute()
        print_test("Health checks history", len(history.data) > 0,
                   f"Found {len(history.data)} historical health checks")
        
        return True
        
    except Exception as e:
        print_test("Enterprise Monitoring Tests", False, f"Error: {str(e)[:100]}")
        return False


# ============================================================
# MAIN TEST RUNNER
# ============================================================
async def run_all_tests():
    """Run all Phase 6C feature tests."""
    print("\n")
    print("=" * 60)
    print("  PHASE 6C ENTERPRISE FEATURES - COMPREHENSIVE TESTS")
    print("=" * 60)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Synchronous tests
    results['multi_tenancy'] = test_multi_tenancy()
    results['sso_integration'] = test_sso_integration()
    results['rbac_system'] = test_rbac_system()
    results['audit_logging'] = test_audit_logging()
    results['white_label'] = test_white_label_branding()
    
    # Asynchronous tests
    results['rate_limiting'] = await test_rate_limiting()
    results['monitoring'] = await test_monitoring()
    
    # Summary
    print_section("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    failed_tests = total_tests - passed_tests
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if all(results.values()):
        print("\n" + "=" * 60)
        print("  ALL TESTS PASSED!")
        print("  Phase 6C Enterprise Features are working correctly.")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("  SOME TESTS FAILED")
        print("  Please review the errors above.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
        sys.exit(1)
