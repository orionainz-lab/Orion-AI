# Phase 7: Integration Testing & Additional Features

**Date**: 2026-01-31  
**Status**: PLANNING  
**Estimated Duration**: 3-5 days

---

## Executive Summary

This phase covers two parallel workstreams:
- **Option B**: Integration Testing (SSO, RBAC, Rate Limiting)
- **Option C**: Additional Features (Admin Portal, Billing, Documentation)

---

## Option B: Integration Testing

### B1. SSO End-to-End Testing (4-6 hours)

#### Test Matrix

| Provider | Protocol | Test Cases | Priority |
|----------|----------|------------|----------|
| **Azure AD** | OIDC | Login, Logout, Token Refresh, JIT Provisioning | P0 |
| **Google Workspace** | OIDC | Login, Logout, Domain Restriction | P0 |
| **Auth0** | OIDC | Login, Logout, MFA Flow | P1 |
| **OneLogin** | SAML | Login, Logout, Attribute Mapping | P1 |

#### Test Scenarios

```
SSO-001: Fresh user login via Azure AD
  1. User clicks "Sign in with Microsoft"
  2. Redirected to Azure AD login
  3. User authenticates
  4. Redirected back to Orion
  5. JIT provisioning creates user in org
  6. User lands on dashboard
  Expected: User created with correct org_id, role assigned

SSO-002: Existing user login
  1. Existing user clicks "Sign in with Google"
  2. Authenticates with Google
  3. Session established
  4. Previous settings preserved
  Expected: No duplicate user, session works

SSO-003: Token refresh
  1. User authenticated
  2. Wait for token expiry (or simulate)
  3. User performs action
  4. Token silently refreshed
  Expected: No interruption, new token obtained

SSO-004: Logout flow
  1. User clicks logout
  2. Session terminated locally
  3. Optional: SLO to IdP
  Expected: Cannot access protected routes

SSO-005: Domain restriction (Google)
  1. Configure org to only allow @company.com
  2. User with @gmail.com tries to login
  Expected: Access denied with clear message

SSO-006: SAML assertion validation
  1. User logs in via OneLogin
  2. SAML response received
  3. Signature validated
  4. Attributes extracted
  Expected: User attributes mapped correctly
```

#### Implementation Tasks

- [ ] Create `tests/integration/test_sso_flows.py`
- [ ] Mock IdP responses for unit tests
- [ ] Set up test accounts in each IdP
- [ ] Create SSO test runner script
- [ ] Document test results

#### Files to Create

```
tests/
  integration/
    sso/
      __init__.py
      test_azure_ad.py      (~100 lines)
      test_google.py        (~80 lines)
      test_auth0.py         (~80 lines)
      test_onelogin.py      (~100 lines)
      conftest.py           (~50 lines) - fixtures
      mock_responses.py     (~150 lines) - mock IdP responses
```

---

### B2. RBAC UI Validation (3-4 hours)

#### Test Matrix

| Role | Dashboard | Connectors | Settings | Admin | Billing |
|------|-----------|------------|----------|-------|---------|
| **viewer** | Read | Read | None | None | None |
| **member** | Read | Read/Write | Read | None | None |
| **admin** | Full | Full | Full | Full | Read |
| **owner** | Full | Full | Full | Full | Full |
| **super_admin** | Full | Full | Full | Full | Full |

#### Test Scenarios

```
RBAC-001: Viewer cannot create connectors
  1. Login as viewer
  2. Navigate to Connectors
  3. Try to click "Add Connector"
  Expected: Button disabled or hidden

RBAC-002: Member can edit own connectors
  1. Login as member
  2. Navigate to Connectors
  3. Edit connector they created
  Expected: Edit succeeds

RBAC-003: Admin can access all org connectors
  1. Login as admin
  2. Navigate to Connectors
  3. View all org connectors
  Expected: Full list visible

RBAC-004: Permission denied shows clear message
  1. Login as viewer
  2. Direct URL to /settings/billing
  Expected: 403 page with upgrade prompt

RBAC-005: Role change takes effect immediately
  1. Admin changes user role viewer -> member
  2. User refreshes page
  Expected: New permissions active
```

#### Implementation Tasks

- [ ] Create `tests/integration/test_rbac_ui.py`
- [ ] Create test users with each role
- [ ] Implement permission check assertions
- [ ] Screenshot on failure for debugging
- [ ] Create RBAC test report generator

#### Files to Create

```
tests/
  integration/
    rbac/
      __init__.py
      test_viewer_permissions.py   (~80 lines)
      test_member_permissions.py   (~80 lines)
      test_admin_permissions.py    (~80 lines)
      test_owner_permissions.py    (~60 lines)
      fixtures.py                  (~100 lines) - test users
```

---

### B3. Rate Limiting Load Test (2-3 hours)

#### Test Configuration

| Tier | Requests/min | Requests/hour | Monthly Quota |
|------|--------------|---------------|---------------|
| **free** | 60 | 1,000 | 10,000 |
| **starter** | 300 | 10,000 | 100,000 |
| **professional** | 1,000 | 50,000 | 500,000 |
| **enterprise** | 5,000 | 200,000 | Unlimited |

#### Test Scenarios

```
RATE-001: Under limit - requests succeed
  1. Send 50 requests in 1 minute (free tier)
  Expected: All 200 OK

RATE-002: At limit - warning header
  1. Send 55 requests in 1 minute
  Expected: X-RateLimit-Remaining: 5

RATE-003: Over limit - 429 response
  1. Send 65 requests in 1 minute (free tier = 60)
  Expected: 429 Too Many Requests after 60

RATE-004: Rate limit resets
  1. Hit rate limit
  2. Wait 60 seconds
  3. Send request
  Expected: Request succeeds

RATE-005: Monthly quota tracking
  1. Check monthly usage endpoint
  2. Verify count accurate
  Expected: Usage matches actual calls

RATE-006: Tier upgrade takes effect
  1. User on free tier hits limit
  2. Admin upgrades to starter
  3. User retries
  Expected: Higher limit now applies
```

#### Implementation Tasks

- [ ] Create `scripts/load_test_rate_limiting.py`
- [ ] Use `locust` or `httpx` for load testing
- [ ] Verify Redis counters update correctly
- [ ] Test quota rollover at month boundary
- [ ] Generate load test report

#### Files to Create

```
scripts/
  load_tests/
    rate_limiting.py      (~150 lines) - locust scenarios
    run_load_test.sh      (~30 lines) - runner script
    report_generator.py   (~80 lines) - generate HTML report
tests/
  integration/
    test_rate_limiting.py (~120 lines) - unit tests
```

---

## Option C: Additional Features

### C1. Admin Portal (8-12 hours)

#### Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **Org Management** | Create, edit, delete organizations | P0 |
| **User Management** | Invite, remove, change roles | P0 |
| **Team Management** | Create teams, assign members | P1 |
| **SSO Configuration** | Configure IdP settings per org | P0 |
| **Quota Management** | View/adjust org quotas | P1 |
| **Audit Log Viewer** | Search and filter audit events | P1 |
| **System Health** | View system status, alerts | P2 |

#### Pages to Create

```
frontend/app/admin/
  layout.tsx              (~50 lines) - admin layout with nav
  page.tsx                (~80 lines) - admin dashboard
  organizations/
    page.tsx              (~120 lines) - org list
    [id]/page.tsx         (~150 lines) - org details
    new/page.tsx          (~100 lines) - create org
  users/
    page.tsx              (~120 lines) - user list
    [id]/page.tsx         (~100 lines) - user details
  teams/
    page.tsx              (~100 lines) - team list
  sso/
    page.tsx              (~150 lines) - SSO config
  audit/
    page.tsx              (~120 lines) - audit log viewer
  health/
    page.tsx              (~100 lines) - system health
```

#### API Routes to Create

```
frontend/app/api/admin/
  organizations/
    route.ts              (~80 lines) - CRUD organizations
    [id]/route.ts         (~60 lines) - single org
  users/
    route.ts              (~80 lines) - CRUD users
    [id]/route.ts         (~60 lines) - single user
  teams/
    route.ts              (~60 lines) - CRUD teams
  sso/
    route.ts              (~100 lines) - SSO configuration
  audit/
    route.ts              (~80 lines) - audit log queries
```

#### Database Access

Uses existing tables:
- `organizations`
- `org_members`
- `teams`
- `team_members`
- `roles`
- `permissions`
- `sso_configurations`
- `audit_logs`

---

### C2. Billing System (6-8 hours)

#### Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **Plan Selection** | Choose free/starter/pro/enterprise | P0 |
| **Stripe Integration** | Payment processing | P0 |
| **Usage Dashboard** | View API usage, quota remaining | P0 |
| **Invoice History** | View past invoices | P1 |
| **Upgrade/Downgrade** | Change plans | P1 |
| **Payment Methods** | Add/remove cards | P2 |

#### Pages to Create

```
frontend/app/settings/billing/
  page.tsx                (~150 lines) - billing overview
  plans/page.tsx          (~120 lines) - plan selection
  usage/page.tsx          (~100 lines) - usage dashboard
  invoices/page.tsx       (~80 lines) - invoice history
  payment-methods/page.tsx (~100 lines) - manage cards
```

#### API Routes

```
frontend/app/api/billing/
  subscription/
    route.ts              (~100 lines) - manage subscription
  checkout/
    route.ts              (~80 lines) - create Stripe checkout
  portal/
    route.ts              (~40 lines) - Stripe customer portal
  usage/
    route.ts              (~60 lines) - usage stats
  webhooks/
    stripe/route.ts       (~120 lines) - Stripe webhook handler
```

#### Database Tables to Add

```sql
-- Billing tables
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id),
  stripe_subscription_id TEXT,
  stripe_customer_id TEXT,
  plan_id TEXT NOT NULL,  -- 'free', 'starter', 'pro', 'enterprise'
  status TEXT NOT NULL,   -- 'active', 'past_due', 'canceled'
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE invoices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id),
  stripe_invoice_id TEXT,
  amount_cents INTEGER,
  currency TEXT DEFAULT 'usd',
  status TEXT,  -- 'paid', 'open', 'void'
  pdf_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE payment_methods (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id),
  stripe_payment_method_id TEXT,
  type TEXT,  -- 'card', 'bank'
  last_four TEXT,
  brand TEXT,
  is_default BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Stripe Integration

```python
# services/billing/stripe_service.py (~150 lines)

class StripeService:
    def __init__(self):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    
    async def create_checkout_session(
        self, org_id: str, plan_id: str, success_url: str, cancel_url: str
    ) -> str:
        """Create Stripe Checkout session for plan upgrade."""
        pass
    
    async def create_customer_portal(self, org_id: str) -> str:
        """Create Stripe Customer Portal session."""
        pass
    
    async def handle_webhook(self, payload: bytes, signature: str) -> None:
        """Handle Stripe webhook events."""
        pass
    
    async def get_usage(self, org_id: str) -> dict:
        """Get current usage for billing display."""
        pass
```

---

### C3. Documentation (4-6 hours)

#### Documentation Structure

```
docs/
  index.md                    - Home page
  getting-started/
    quickstart.md             - 5-minute setup
    installation.md           - Full installation
    configuration.md          - Environment variables
  user-guide/
    dashboard.md              - Dashboard overview
    connectors.md             - Managing connectors
    workflows.md              - Using workflows
    matrix-grid.md            - Matrix Grid UI
  admin-guide/
    organizations.md          - Org management
    users-roles.md            - User and role management
    sso-configuration.md      - SSO setup
    billing.md                - Billing and plans
  api-reference/
    authentication.md         - Auth endpoints
    connectors.md             - Connector API
    workflows.md              - Workflow API
    webhooks.md               - Webhook handling
  runbooks/
    deployment.md             - Deployment procedures
    monitoring.md             - Monitoring and alerts
    incident-response.md      - Incident handling
    backup-restore.md         - Backup procedures
```

#### Tools

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **Docusaurus** | React-based, versioning, search | Learning curve | Best for API docs |
| **GitBook** | Beautiful, easy | External service | Good for user docs |
| **MkDocs** | Python, simple, Material theme | Less features | Good for runbooks |
| **Nextra** | Next.js native, MDX | Newer | Best if using Next.js |

**Recommendation**: Use **Nextra** (Next.js native) for seamless integration.

#### Pages Per Section

| Section | Pages | Est. Lines |
|---------|-------|------------|
| Getting Started | 3 | 600 |
| User Guide | 4 | 1,200 |
| Admin Guide | 4 | 1,000 |
| API Reference | 4 | 1,500 |
| Runbooks | 4 | 1,000 |
| **Total** | **19** | **~5,300** |

---

## Implementation Schedule

### Week 1: Integration Testing (Option B)

| Day | Tasks | Hours |
|-----|-------|-------|
| **Day 1** | SSO test framework + Azure AD tests | 4h |
| **Day 2** | Google + Auth0 + OneLogin tests | 4h |
| **Day 3** | RBAC UI tests (all roles) | 4h |
| **Day 4** | Rate limiting load tests | 3h |
| **Day 5** | Test reports + bug fixes | 3h |

**Total**: ~18 hours

### Week 2: Additional Features (Option C)

| Day | Tasks | Hours |
|-----|-------|-------|
| **Day 1** | Admin portal layout + org management | 4h |
| **Day 2** | Admin portal users + teams | 4h |
| **Day 3** | Admin portal SSO + audit | 4h |
| **Day 4** | Billing system + Stripe integration | 6h |
| **Day 5** | Documentation setup + core pages | 4h |
| **Day 6** | Documentation completion | 4h |

**Total**: ~26 hours

---

## Dependencies

### External Services Needed

| Service | Purpose | Setup Required |
|---------|---------|----------------|
| **Stripe** | Payment processing | Create account, get API keys |
| **Test IdP Accounts** | SSO testing | Create test users in Azure/Google/Auth0 |

### Environment Variables to Add

```env
# Billing (Stripe)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_STARTER=price_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_ENTERPRISE=price_...
```

---

## Success Criteria

### Option B: Integration Testing

- [ ] 100% SSO test coverage (all 4 providers)
- [ ] 100% RBAC permission coverage (all 5 roles)
- [ ] Rate limiting verified under load (1000+ req/min)
- [ ] All tests automated and runnable in CI
- [ ] Test report generated with pass/fail summary

### Option C: Additional Features

- [ ] Admin portal functional (8+ pages)
- [ ] Billing system integrated with Stripe
- [ ] Documentation site deployed
- [ ] 19+ documentation pages written
- [ ] All new code under 200 lines per file

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SSO test accounts not available | Medium | High | Create dedicated test IdP tenants |
| Stripe integration complexity | Medium | Medium | Use Stripe's test mode extensively |
| Documentation takes longer | High | Low | Prioritize core pages first |
| Rate limit tests affect prod Redis | Low | High | Use separate Redis instance for tests |

---

## File Count Summary

### Option B: Integration Testing

| Directory | Files | Est. Lines |
|-----------|-------|------------|
| `tests/integration/sso/` | 6 | ~560 |
| `tests/integration/rbac/` | 5 | ~400 |
| `scripts/load_tests/` | 3 | ~260 |
| **Total** | **14** | **~1,220** |

### Option C: Additional Features

| Directory | Files | Est. Lines |
|-----------|-------|------------|
| `frontend/app/admin/` | 10 | ~1,050 |
| `frontend/app/api/admin/` | 8 | ~520 |
| `frontend/app/settings/billing/` | 5 | ~550 |
| `frontend/app/api/billing/` | 5 | ~400 |
| `services/billing/` | 2 | ~200 |
| `docs/` | 19 | ~5,300 |
| **Total** | **49** | **~8,020** |

---

## Recommended Order

```
1. [18h] Option B: Integration Testing
   - Validates existing enterprise features
   - Catches bugs before adding more code
   - Required for production confidence

2. [26h] Option C: Additional Features
   - Admin Portal (12h) - enables org management
   - Billing System (8h) - enables monetization
   - Documentation (6h) - enables adoption
```

**Total Estimated Time**: ~44 hours (1.5-2 weeks)

---

## Quick Start Commands

### After Approval

```bash
# Create test directories
mkdir -p tests/integration/sso tests/integration/rbac scripts/load_tests

# Install test dependencies
pip install locust pytest-playwright

# Create admin portal structure
mkdir -p frontend/app/admin/{organizations,users,teams,sso,audit,health}
mkdir -p frontend/app/settings/billing/{plans,usage,invoices,payment-methods}

# Create docs structure
mkdir -p docs/{getting-started,user-guide,admin-guide,api-reference,runbooks}
```

---

**Ready to proceed?** Let me know which option to start with:
- **Option B first** (Integration Testing)
- **Option C first** (Additional Features)
- **Both in parallel** (if you have capacity)
