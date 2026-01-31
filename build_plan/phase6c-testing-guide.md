# Phase 6C: Enterprise Features - Testing Guide

**Version**: 1.0.0  
**Date**: 2026-02-01  
**Status**: Ready for Testing

---

## 📋 Pre-Testing Setup

### 1. Apply Database Migration

**Option A: Via Supabase MCP** (Recommended)
```bash
# Use Supabase MCP tools to execute the migration
```

**Option B: Via Supabase Dashboard**
1. Go to Supabase Dashboard → SQL Editor
2. Copy contents of `supabase/migrations/20260201_phase6c_enterprise_features.sql`
3. Execute the migration
4. Verify: Check Tables section for new tables

**Option C: Via Supabase CLI**
```bash
supabase db push
```

### 2. Seed Test Data
```bash
# Via Supabase Dashboard SQL Editor
# Copy and execute: scripts/seed/seed_phase6c.sql
```

**Test Organizations Created**:
1. **Acme Corp Demo** (`acme-demo`) - Free tier
2. **TechStart Inc** (`techstart`) - Professional tier
3. **Global Enterprises Ltd** (`global-enterprises`) - Enterprise tier

### 3. Create Storage Bucket
```bash
# In Supabase Dashboard:
# Storage → New Bucket → "brand-assets"
# Access: Public
# File size limit: 50MB
```

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
```bash
# Add to .env.local
SUPABASE_URL=<your-url>
SUPABASE_SERVICE_ROLE_KEY=<your-key>
REDIS_URL=rediss://default:xxx@xxx.upstash.io:6379
AUDIT_SIGNATURE_SECRET=<generate-random-32-chars>

# SSO Credentials (from Checklist.md)
AZURE_AD_TENANT_ID=22116407-6817-4c85-96ce-1b6d4e631844
AZURE_AD_CLIENT_ID=de01844a-115d-4789-8b5f-eab412c6089e
AZURE_AD_CLIENT_SECRET=ISD8Q~dypu1jXm33lD71uTerp5fWAWHqGhvmCahN
# ... (add others from Checklist.md)
```

---

## 🧪 Testing Workstreams

### Workstream 1: Multi-Tenancy Foundation

#### Test 1.1: Tenant Manager - Create Organization
```python
from services.tenancy import TenantManager, Tier

manager = TenantManager()

# Create new organization
org = await manager.create_organization(
    name="Test Corp",
    slug="test-corp",
    tier=Tier.PROFESSIONAL
)

print(f"✓ Created org: {org.name} ({org.slug})")

# Verify quotas
assert org.quotas["monthlyApiCalls"] == 100000
print("✓ Quotas set correctly")
```

#### Test 1.2: Tenant Resolver - Resolve from Subdomain
```python
from services.tenancy import TenantResolver
from fastapi import Request

resolver = TenantResolver(manager)

# Mock request with subdomain
request = Request({
    "type": "http",
    "headers": [[b"host", b"acme-demo.orion-ai.com"]]
})

context = await resolver.resolve_from_request(request)

print(f"✓ Resolved tenant: {context.org_name}")
assert context.org_slug == "acme-demo"
print("✓ Tenant resolution works")
```

#### Test 1.3: Teams - Create and List
```python
# Create team
team = await manager.create_team(
    org_id=org.id,
    name="Engineering",
    description="Engineering team"
)

print(f"✓ Created team: {team.name}")

# List teams
teams = await manager.list_teams(org.id)
print(f"✓ Found {len(teams)} teams")
```

---

### Workstream 2: SSO Integration

#### Test 2.1: OIDC - Azure AD Authorization
```python
from services.auth.sso import AzureADProvider

provider = AzureADProvider.from_credentials(
    tenant_id="22116407-6817-4c85-96ce-1b6d4e631844",
    client_id="de01844a-115d-4789-8b5f-eab412c6089e",
    client_secret="ISD8Q~dypu1jXm33lD71uTerp5fWAWHqGhvmCahN",
    redirect_uri="https://orion-ai.vercel.app/api/auth/callback/azure-ad"
)

# Generate authorization URL
auth_url, state = await provider.get_authorization_url()

print(f"✓ Authorization URL generated")
print(f"  URL: {auth_url[:80]}...")
print(f"  State: {state[:20]}...")
```

#### Test 2.2: SSO Manager - Get Configuration
```python
from services.auth.sso import SSOManager

sso_manager = SSOManager(supabase_client, "https://orion-ai.vercel.app")

# Get Azure AD config for Global Enterprises
config = await sso_manager.get_sso_config(
    org_id="33333333-3333-3333-3333-333333333333",  # Global Enterprises
    provider="azure-ad"
)

print(f"✓ SSO config loaded")
assert config["enabled"] == True
print("✓ SSO is enabled")
```

#### Test 2.3: JIT Provisioning - Simulate User Creation
```python
from services.auth.sso import JITProvisioner, JITConfig, OIDCUserInfo

provisioner = JITProvisioner(supabase_client)

jit_config = JITConfig(
    enabled=True,
    default_role_id="00000000-0000-0000-0000-000000000004",  # Member
    group_mapping={},
    auto_create_users=True,
    auto_update_profile=True
)

# Simulate OIDC user
user_info = OIDCUserInfo(
    sub="test-user-123",
    email="test@example.com",
    name="Test User",
    email_verified=True
)

# Note: This creates a real user - use test org
result = await provisioner.provision_oidc_user(
    org_id=org.id,
    user_info=user_info,
    jit_config=jit_config
)

print(f"✓ JIT provisioned user: {result['email']}")
```

---

### Workstream 3: RBAC System

#### Test 3.1: Permission Checker - Check Permission
```python
from services.rbac import PermissionChecker, Scope

checker = PermissionChecker(supabase_client)

# Check if user can read connectors
has_permission = await checker.has_permission(
    user_id="user-id",
    org_id=org.id,
    resource="connectors",
    action="read",
    required_scope=Scope.ORG
)

print(f"✓ Permission check: {has_permission}")
```

#### Test 3.2: Role Manager - Create Custom Role
```python
from services.rbac import RoleManager

role_manager = RoleManager(supabase_client)

# Create data analyst role
role = await role_manager.create_role(
    org_id=org.id,
    name="Data Analyst",
    description="Can view and export analytics",
    permissions=[
        "analytics:read:org",
        "analytics:export:org",
        "connectors:read:org"
    ]
)

print(f"✓ Created custom role: {role['name']}")
```

#### Test 3.3: Role Assignment
```python
# Assign role to user
await role_manager.assign_org_role(
    org_id=org.id,
    user_id="user-id",
    role_id=role["id"]
)

print(f"✓ Assigned role to user")
```

---

### Workstream 4: Audit Logging

#### Test 4.1: Log Event
```python
from services.audit import AuditLogger, AuditAction, RetentionPolicy

logger = AuditLogger(supabase_client)

# Log connector creation
event = await logger.log_event(
    org_id=org.id,
    action=AuditAction.CREATE,
    resource_type="connector",
    user_id="user-id",
    resource_id="conn-123",
    details={"name": "Salesforce", "status": "active"},
    ip_address="192.168.1.1",
    compliance_tags=["soc2"]
)

print(f"✓ Logged audit event: {event.id}")
assert event.signature is not None
print(f"✓ Event signature: {event.signature[:20]}...")
```

#### Test 4.2: Verify Signature
```python
# Verify event integrity
is_valid = logger.verify_signature(event)

print(f"✓ Signature verification: {'PASS' if is_valid else 'FAIL'}")
assert is_valid
```

#### Test 4.3: Query Events
```python
# Get recent events
events = await logger.get_events(
    org_id=org.id,
    limit=10
)

print(f"✓ Retrieved {len(events)} audit events")

for e in events[:3]:
    print(f"  - {e.action} on {e.resource_type} at {e.created_at}")
```

---

### Workstream 5: White-Label Branding

#### Test 5.1: Create Brand Configuration
```python
from services.branding import BrandManager

brand_manager = BrandManager(
    supabase_client,
    cdn_base_url="https://[project].supabase.co/storage/v1/object/public/brand-assets"
)

# Create branding
brand = await brand_manager.create_or_update_brand_config(
    org_id=org.id,
    primary_color="#FF6B6B",
    secondary_color="#4ECDC4",
    show_powered_by=False,
    custom_support_email="support@test-corp.com"
)

print(f"✓ Created brand config")
print(f"  Primary: {brand.primary_color}")
print(f"  Show 'Powered by': {brand.show_powered_by}")
```

#### Test 5.2: Generate Theme CSS
```python
# Get theme CSS
theme_css = await brand_manager.get_theme_css(org.id)

print(f"✓ Generated theme CSS ({len(theme_css)} chars)")
print(theme_css[:200])
```

#### Test 5.3: Add Custom Domain
```python
# Add custom domain
domain = await brand_manager.add_custom_domain(
    org_id=org.id,
    domain="integrations.test-corp.com"
)

print(f"✓ Added custom domain: {domain.domain}")
print(f"  Status: {domain.verification_status}")
print(f"  Token: {domain.verification_token[:30]}...")

# Get verification instructions
instructions = await brand_manager.get_domain_verification_instructions(domain.domain)

print(f"✓ Verification method: {instructions['method']}")
```

---

### Workstream 6: API Rate Limiting

#### Test 6.1: Redis Connection
```python
import redis.asyncio as redis

redis_client = redis.from_url(os.getenv("REDIS_URL"))

# Test connection
await redis_client.ping()
print("✓ Redis connection successful")
```

#### Test 6.2: Rate Limit Check
```python
from services.rate_limit import RateLimiter, RateLimitTier

rate_limiter = RateLimiter(redis_client, supabase_client)

# Check rate limit
state = await rate_limiter.check_rate_limit(
    org_id=org.id,
    tier=RateLimitTier.PROFESSIONAL,
    identifier="user-123",
    endpoint="/api/connectors"
)

print(f"✓ Rate limit check")
print(f"  Allowed: {state.allowed}")
print(f"  Remaining: {state.remaining}")
print(f"  Reset at: {state.reset_at}")
```

#### Test 6.3: Consume Tokens
```python
# Consume tokens
for i in range(5):
    state = await rate_limiter.consume(
        org_id=org.id,
        tier=RateLimitTier.PROFESSIONAL,
        identifier="user-123",
        endpoint="/api/connectors"
    )
    print(f"  Request {i+1}: {state.remaining} remaining")
```

#### Test 6.4: Get Usage Stats
```python
# Get usage statistics
stats = await rate_limiter.get_usage_stats(
    org_id=org.id,
    identifier="user-123",
    endpoint="/api/connectors"
)

print(f"✓ Usage stats:")
for window, data in stats.items():
    print(f"  {window}: {data['used']} used, resets in {data['reset_in_seconds']}s")
```

---

### Workstream 7: Enterprise Monitoring

#### Test 7.1: Health Checks
```python
from services.monitoring import HealthChecker, HealthStatus

health_checker = HealthChecker(supabase_client)

# Check database
result = await health_checker.check_database_health()

print(f"✓ Database health: {result.status.value}")
print(f"  Response time: {result.response_time_ms}ms")

# Check Redis
result = await health_checker.check_redis_health(redis_client)

print(f"✓ Redis health: {result.status.value}")
print(f"  Response time: {result.response_time_ms}ms")
print(f"  Memory: {result.metadata.get('memory_used_mb')}MB")
```

#### Test 7.2: Run All Health Checks
```python
# Run comprehensive health check
results = await health_checker.run_all_checks(
    redis_client=redis_client,
    external_services={
        "Salesforce API": "https://login.salesforce.com",
        "QuickBooks API": "https://appcenter.intuit.com"
    }
)

print(f"✓ Ran {len(results)} health checks:")
for r in results:
    icon = "✓" if r.status == HealthStatus.HEALTHY else "✗"
    print(f"  {icon} {r.check_type}/{r.check_name}: {r.status.value}")
```

#### Test 7.3: Alert Manager - Create Alert
```python
from services.monitoring import AlertManager, AlertType, Severity

alert_manager = AlertManager(supabase_client)

# Create threshold alert
alert = await alert_manager.create_alert(
    org_id=org.id,
    alert_name="High API Usage",
    alert_type=AlertType.THRESHOLD,
    metric_name="api_calls_per_hour",
    condition={"operator": ">", "value": 50000},
    severity=Severity.WARNING,
    notification_channels=["email"]
)

print(f"✓ Created alert: {alert.alert_name}")
print(f"  Severity: {alert.severity.value}")
print(f"  Condition: {alert.condition}")
```

#### Test 7.4: Record Metric and Evaluate
```python
# Record metric
await alert_manager.record_metric(
    org_id=org.id,
    metric_name="api_calls_per_hour",
    metric_value=55000  # Above threshold
)

print(f"✓ Recorded metric: 55000 calls/hour")

# Evaluate alerts
triggered = await alert_manager.evaluate_alerts(org.id)

print(f"✓ Evaluated alerts: {len(triggered)} triggered")
for event in triggered:
    print(f"  - {event.metric_name}: {event.condition_met}")
```

---

## 📊 Verification Checklist

### Database
- [ ] All 15 tables created
- [ ] 30+ indexes exist
- [ ] 10+ RLS policies active
- [ ] 5 triggers functional
- [ ] 2 functions exist (get_user_orgs, user_has_permission)
- [ ] Seed data loaded (3 organizations)

### Backend Services
- [ ] Tenant manager works
- [ ] Tenant resolver works
- [ ] SSO providers initialize
- [ ] RBAC permissions check
- [ ] Audit logging persists events
- [ ] Branding configuration saves
- [ ] Rate limiter connects to Redis
- [ ] Health checks run

### Infrastructure
- [ ] Redis connection successful
- [ ] Supabase Storage bucket created
- [ ] Environment variables set
- [ ] Dependencies installed

---

## 🐛 Common Issues & Solutions

### Issue: Redis Connection Failed
**Solution**: Check REDIS_URL format and network access
```python
# Test Redis connection
import redis.asyncio as redis
redis_client = redis.from_url(os.getenv("REDIS_URL"))
await redis_client.ping()  # Should not raise exception
```

### Issue: SSO Provider Not Found
**Solution**: Ensure SSO configuration is seeded and enabled
```sql
SELECT * FROM sso_configurations WHERE org_id = '<org-id>';
-- Should show enabled=true
```

### Issue: Audit Signature Missing
**Solution**: Check AUDIT_SIGNATURE_SECRET is set
```python
# Verify environment variable
import os
assert os.getenv("AUDIT_SIGNATURE_SECRET") is not None
```

### Issue: Permission Denied in RLS
**Solution**: Check user has org_member entry
```sql
SELECT * FROM org_members WHERE user_id = '<user-id>';
-- Should have at least one row
```

---

## 🎯 Success Criteria

Phase 6C testing is successful if:

✅ **All 7 workstreams test successfully**  
✅ **Database migration applies without errors**  
✅ **Seed data creates 3 test organizations**  
✅ **Redis connection established**  
✅ **SSO providers initialize**  
✅ **RBAC permissions evaluate correctly**  
✅ **Audit events log with signatures**  
✅ **Rate limiting enforces quotas**  
✅ **Health checks return status**  

---

**Testing Complete**: 2026-02-01  
**Status**: ✅ Ready for Integration Testing  
**Next Step**: End-to-end integration testing with frontend
