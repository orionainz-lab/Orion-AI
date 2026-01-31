# Phase 6C Architecture: Enterprise Features

**Created**: 2026-01-31  
**Complexity**: Level 5 (Very Complex) - Enterprise Scale  
**Estimated Duration**: 20-30 hours  
**Prerequisites**: Phase 6B Complete ✅

---

## Executive Summary

Phase 6C transforms Orion AI into a **true enterprise-grade platform** with:
- Multi-tenancy and organizational hierarchies
- Single Sign-On (SSO) with SAML/OIDC
- Advanced RBAC with custom roles
- Audit logging and compliance
- White-label branding capabilities
- API rate limiting and quotas
- Advanced monitoring and alerting
- Data residency and compliance tools

### Success Criteria
- ✅ Multi-tenant architecture supports 1000+ organizations
- ✅ SSO integration with major providers (Okta, Azure AD, Google Workspace)
- ✅ Role-based access control with custom permissions
- ✅ Complete audit trail for compliance (SOC 2, GDPR)
- ✅ White-label deployment in < 30 minutes
- ✅ API quotas and rate limiting per organization
- ✅ 99.99% uptime with auto-scaling

---

## Architecture Decisions (ADRs)

### ADR-029: Multi-Tenancy Strategy
**Decision**: Hybrid Row-Level + Schema-Level Multi-Tenancy

**Problem**: Need to support both small teams and large enterprises with different isolation requirements.

**Solution**: Tiered multi-tenancy approach
```
┌────────────────────────────────────────────┐
│         Multi-Tenancy Architecture          │
├────────────────────────────────────────────┤
│ Tier 1: Row-Level (RLS)                   │
│   • Shared tables with org_id             │
│   • Supabase RLS policies                 │
│   • Use: < 100 organizations               │
│                                             │
│ Tier 2: Schema-Level                       │
│   • Dedicated schema per org              │
│   • Complete data isolation               │
│   • Use: Enterprise customers              │
│                                             │
│ Tier 3: Database-Level                     │
│   • Dedicated database instance           │
│   • Custom infrastructure                 │
│   • Use: Regulated industries             │
└────────────────────────────────────────────┘
```

**Implementation**:
```typescript
interface TenantConfig {
  orgId: string;
  tier: 'row' | 'schema' | 'database';
  isolationLevel: 'shared' | 'dedicated' | 'private';
  dataResidency: 'us' | 'eu' | 'asia' | 'custom';
  features: string[];
  quotas: {
    users: number;
    connectors: number;
    apiCalls: number;
    storage: number;
  };
}
```

**Benefits**:
- Flexible scaling from startups to enterprises
- Cost-effective for small organizations
- Strong isolation for enterprises
- Compliance-ready architecture

**Alternatives Considered**:
1. **Row-level only**: Doesn't meet enterprise isolation needs
2. **Schema-level only**: Too expensive for small teams
3. **Microservices per tenant**: Excessive complexity

---

### ADR-030: SSO Authentication Strategy
**Decision**: Multiple SSO Protocol Support via SAML + OIDC

**Rationale**:
- SAML required for enterprise (Okta, Azure AD, OneLogin)
- OIDC preferred for modern apps (Google, Auth0)
- Must support Just-In-Time (JIT) provisioning
- Graceful fallback to email/password

**Architecture**:
```
┌────────────────────────────────────────────┐
│          SSO Authentication Flow            │
├────────────────────────────────────────────┤
│  1. User clicks "Login with SSO"           │
│  2. Identify organization by domain        │
│  3. Redirect to SSO provider               │
│  4. Provider authenticates user            │
│  5. SAML/OIDC callback to Orion            │
│  6. JIT provision user if new              │
│  7. Map roles from SSO groups              │
│  8. Create session token                   │
│  9. Redirect to dashboard                  │
└────────────────────────────────────────────┘
```

**Supported Providers**:
- Okta (SAML 2.0)
- Azure AD (OIDC + SAML)
- Google Workspace (OIDC)
- OneLogin (SAML 2.0)
- Auth0 (OIDC)
- Generic SAML 2.0
- Generic OIDC

**JIT Provisioning**:
```typescript
interface SSOUser {
  email: string;
  firstName: string;
  lastName: string;
  groups: string[];  // Map to roles
  attributes: Record<string, any>;
}

async function provisionUser(ssoUser: SSOUser, orgId: string) {
  // 1. Create user in auth.users
  // 2. Create org_members entry
  // 3. Map SSO groups to roles
  // 4. Apply default permissions
  // 5. Trigger welcome workflow
}
```

---

### ADR-031: Role-Based Access Control (RBAC) Model
**Decision**: Hierarchical RBAC with Custom Permissions

**Model**:
```typescript
interface Permission {
  resource: 'connectors' | 'analytics' | 'users' | 'settings';
  action: 'read' | 'write' | 'delete' | 'admin';
  scope: 'self' | 'team' | 'org' | 'all';
}

interface Role {
  id: string;
  name: string;
  permissions: Permission[];
  inheritsFrom?: string[];  // Role hierarchy
  isCustom: boolean;
}

// Built-in Roles
const ROLES = {
  SUPER_ADMIN: {
    name: 'Super Admin',
    permissions: [{ resource: '*', action: '*', scope: 'all' }]
  },
  ORG_ADMIN: {
    name: 'Organization Admin',
    permissions: [
      { resource: '*', action: '*', scope: 'org' }
    ]
  },
  TEAM_LEAD: {
    name: 'Team Lead',
    permissions: [
      { resource: 'connectors', action: '*', scope: 'team' },
      { resource: 'analytics', action: 'read', scope: 'team' }
    ]
  },
  MEMBER: {
    name: 'Member',
    permissions: [
      { resource: 'connectors', action: 'read', scope: 'self' },
      { resource: 'connectors', action: 'write', scope: 'self' },
      { resource: 'analytics', action: 'read', scope: 'self' }
    ]
  },
  VIEWER: {
    name: 'Viewer',
    permissions: [
      { resource: '*', action: 'read', scope: 'self' }
    ]
  }
};
```

**Custom Roles**:
- Organizations can create custom roles
- Combine granular permissions
- Test roles before deployment
- Audit role changes

---

### ADR-032: Audit Logging Strategy
**Decision**: Comprehensive Event Sourcing with Retention Policies

**Logged Events**:
```typescript
interface AuditEvent {
  id: string;
  timestamp: Date;
  orgId: string;
  userId: string;
  action: string;  // 'user.login', 'connector.create', 'data.export'
  resource: string;
  resourceId?: string;
  changes?: {
    before: any;
    after: any;
  };
  metadata: {
    ipAddress: string;
    userAgent: string;
    location?: string;
    sessionId: string;
  };
  compliance: {
    gdpr: boolean;
    hipaa: boolean;
    sox: boolean;
  };
}
```

**Retention Policies**:
- Security events: 7 years (SOX requirement)
- User actions: 3 years (GDPR maximum)
- Data access: 1 year (standard compliance)
- System events: 90 days (operational)

**Compliance Features**:
- Tamper-proof audit log
- Cryptographic signing
- External backup to immutable storage
- GDPR right-to-deletion support
- Automated compliance reports

---

### ADR-033: White-Label Architecture
**Decision**: Dynamic Theming with CDN-Hosted Assets

**Architecture**:
```
┌────────────────────────────────────────────┐
│        White-Label Components               │
├────────────────────────────────────────────┤
│ Frontend Theming                           │
│   • Custom CSS variables                   │
│   • Logo and favicon                       │
│   • Color schemes                          │
│   • Typography                             │
│                                             │
│ Custom Domain                               │
│   • CNAME configuration                    │
│   • SSL certificate (Let's Encrypt)        │
│   • Email domain matching                  │
│                                             │
│ Branded Communications                      │
│   • Email templates                        │
│   • PDF reports                            │
│   • Notification styles                    │
│                                             │
│ Custom Features                             │
│   • Feature flags per org                  │
│   • Custom connector visibility            │
│   • Tailored onboarding                    │
└────────────────────────────────────────────┘
```

**Theme Configuration**:
```typescript
interface BrandConfig {
  orgId: string;
  domain: string;  // custom.domain.com
  theme: {
    primaryColor: string;
    secondaryColor: string;
    accentColor: string;
    logoUrl: string;
    faviconUrl: string;
    fontFamily: string;
    customCss?: string;
  };
  email: {
    fromName: string;
    fromAddress: string;
    headerLogoUrl: string;
    footerText: string;
  };
  features: {
    showPoweredBy: boolean;
    customHelpLink: string;
    customSupportEmail: string;
  };
}
```

---

### ADR-034: API Rate Limiting Strategy
**Decision**: Token Bucket Algorithm with Tiered Quotas

**Implementation**:
```typescript
interface RateLimitConfig {
  tier: 'free' | 'professional' | 'enterprise';
  limits: {
    requestsPerSecond: number;
    requestsPerHour: number;
    requestsPerDay: number;
    burstSize: number;
  };
  quotas: {
    monthlyApiCalls: number;
    concurrentConnections: number;
    dataVolume: number;  // GB per month
  };
}

const RATE_LIMITS = {
  free: {
    requestsPerSecond: 10,
    requestsPerHour: 1000,
    requestsPerDay: 10000,
    burstSize: 20
  },
  professional: {
    requestsPerSecond: 100,
    requestsPerHour: 50000,
    requestsPerDay: 500000,
    burstSize: 200
  },
  enterprise: {
    requestsPerSecond: 1000,
    requestsPerHour: 1000000,
    requestsPerDay: 10000000,
    burstSize: 2000
  }
};
```

**Rate Limit Response**:
```typescript
// HTTP 429 Too Many Requests
{
  error: 'rate_limit_exceeded',
  message: 'API rate limit exceeded',
  limit: 1000,
  remaining: 0,
  resetAt: '2026-01-31T12:00:00Z',
  retryAfter: 3600  // seconds
}
```

---

## Implementation Plan

### Workstream 1: Multi-Tenancy Foundation (6-8 hours)

**Files to Create**:
```
supabase/migrations/
└── 20260201_multi_tenancy.sql

backend/services/
├── tenancy/
│   ├── __init__.py
│   ├── tenant_manager.py          # Tenant CRUD operations
│   ├── tenant_isolation.py        # Data isolation logic
│   ├── tenant_resolver.py         # Identify tenant from request
│   └── tenant_migration.py        # Schema migration per tenant

config/
└── tenant_tiers.json              # Tier configurations

supabase/functions/
└── tenant-provisioning/           # Automated tenant setup
    └── index.ts
```

**Database Schema**:
```sql
-- Organizations (tenants)
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  tier TEXT NOT NULL CHECK (tier IN ('free', 'professional', 'enterprise')),
  isolation_level TEXT NOT NULL CHECK (isolation_level IN ('row', 'schema', 'database')),
  data_residency TEXT CHECK (data_residency IN ('us', 'eu', 'asia')),
  settings JSONB DEFAULT '{}',
  quotas JSONB NOT NULL,
  billing_status TEXT DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Organization Members
CREATE TABLE org_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role_id UUID NOT NULL REFERENCES roles(id),
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  invited_by UUID REFERENCES auth.users(id),
  UNIQUE(org_id, user_id)
);

-- Teams (sub-organizations)
CREATE TABLE teams (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  parent_team_id UUID REFERENCES teams(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Team Members
CREATE TABLE team_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role_id UUID NOT NULL REFERENCES roles(id),
  UNIQUE(team_id, user_id)
);

-- Add org_id to all existing tables
ALTER TABLE connectors ADD COLUMN org_id UUID REFERENCES organizations(id);
ALTER TABLE connector_configs ADD COLUMN org_id UUID REFERENCES organizations(id);
ALTER TABLE sync_metrics ADD COLUMN org_id UUID REFERENCES organizations(id);
-- ... (all other tables)

-- RLS Policies for multi-tenancy
ALTER TABLE connectors ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their org's connectors"
  ON connectors
  FOR ALL
  USING (
    org_id IN (
      SELECT org_id FROM org_members WHERE user_id = auth.uid()
    )
  );
```

**Tenant Resolution Middleware**:
```python
from fastapi import Request, HTTPException
from typing import Optional

class TenantContext:
    def __init__(self, org_id: str, tier: str, quotas: dict):
        self.org_id = org_id
        self.tier = tier
        self.quotas = quotas

async def resolve_tenant(request: Request) -> TenantContext:
    """
    Resolve tenant from:
    1. Custom domain (custom.company.com)
    2. Subdomain (company.orion-ai.com)
    3. API key org_id
    4. JWT token org_id
    """
    # Try custom domain
    host = request.headers.get('host')
    org = await get_org_by_domain(host)
    
    if not org:
        # Try subdomain
        if '.orion-ai.com' in host:
            subdomain = host.split('.')[0]
            org = await get_org_by_slug(subdomain)
    
    if not org:
        # Try API key
        api_key = request.headers.get('x-api-key')
        if api_key:
            org = await get_org_by_api_key(api_key)
    
    if not org:
        # Try JWT
        user = request.state.user
        org = await get_user_primary_org(user.id)
    
    if not org:
        raise HTTPException(401, "Tenant not found")
    
    return TenantContext(
        org_id=org.id,
        tier=org.tier,
        quotas=org.quotas
    )
```

---

### Workstream 2: SSO Integration (5-7 hours)

**Files to Create**:
```
backend/services/auth/
├── sso/
│   ├── __init__.py
│   ├── saml_provider.py           # SAML 2.0 implementation
│   ├── oidc_provider.py           # OIDC implementation
│   ├── sso_config.py              # SSO configuration per org
│   └── jit_provisioning.py        # Just-in-time user creation

frontend/app/auth/
├── sso/
│   ├── page.tsx                   # SSO login page
│   ├── callback/page.tsx          # OAuth callback
│   └── setup/page.tsx             # SSO config UI (admin)

supabase/migrations/
└── 20260202_sso_config.sql
```

**SSO Configuration Table**:
```sql
CREATE TABLE sso_configurations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  provider TEXT NOT NULL CHECK (provider IN ('saml', 'oidc')),
  enabled BOOLEAN DEFAULT false,
  
  -- SAML Configuration
  saml_entity_id TEXT,
  saml_sso_url TEXT,
  saml_certificate TEXT,
  saml_sign_requests BOOLEAN DEFAULT false,
  
  -- OIDC Configuration
  oidc_issuer TEXT,
  oidc_client_id TEXT,
  oidc_client_secret TEXT,
  oidc_scopes TEXT[] DEFAULT ARRAY['openid', 'profile', 'email'],
  
  -- JIT Provisioning
  jit_enabled BOOLEAN DEFAULT true,
  jit_default_role_id UUID REFERENCES roles(id),
  jit_group_mapping JSONB DEFAULT '{}',
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(org_id, provider)
);

-- SSO Login Events
CREATE TABLE sso_login_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  user_id UUID REFERENCES auth.users(id),
  provider TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('success', 'failure')),
  error_message TEXT,
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**SAML Handler**:
```python
from onelogin.saml2.auth import OneLogin_Saml2_Auth

async def handle_saml_login(request: Request, org_slug: str):
    """Handle SAML SSO login"""
    # 1. Get org SSO config
    org = await get_org_by_slug(org_slug)
    sso_config = await get_sso_config(org.id, 'saml')
    
    # 2. Prepare SAML request
    saml_auth = OneLogin_Saml2_Auth(
        request,
        saml_settings={
            'idp': {
                'entityId': sso_config.saml_entity_id,
                'singleSignOnService': {
                    'url': sso_config.saml_sso_url
                },
                'x509cert': sso_config.saml_certificate
            },
            'sp': {
                'entityId': f'https://orion-ai.com/sso/{org_slug}',
                'assertionConsumerService': {
                    'url': f'https://orion-ai.com/auth/sso/callback'
                }
            }
        }
    )
    
    # 3. Redirect to IdP
    return RedirectResponse(saml_auth.login())

async def handle_saml_callback(request: Request):
    """Handle SAML callback from IdP"""
    # 1. Parse SAML response
    saml_auth = OneLogin_Saml2_Auth(request, settings)
    saml_auth.process_response()
    
    # 2. Validate response
    if not saml_auth.is_authenticated():
        raise HTTPException(401, "SAML authentication failed")
    
    # 3. Extract user attributes
    attributes = saml_auth.get_attributes()
    user_data = {
        'email': attributes['email'][0],
        'first_name': attributes['firstName'][0],
        'last_name': attributes['lastName'][0],
        'groups': attributes.get('groups', [])
    }
    
    # 4. JIT provision user
    user = await provision_user(user_data, org_id)
    
    # 5. Create session
    token = create_jwt_token(user.id, org_id)
    
    return {
        'token': token,
        'redirect_url': '/dashboard'
    }
```

---

### Workstream 3: RBAC System (4-6 hours)

**Files to Create**:
```
supabase/migrations/
└── 20260203_rbac.sql

backend/services/auth/
├── permissions.py                 # Permission checking logic
├── roles.py                       # Role management
└── rbac_middleware.py             # Request authorization

frontend/app/settings/roles/
├── page.tsx                       # Role management UI
├── RoleEditor.tsx                 # Create/edit roles
└── PermissionMatrix.tsx           # Visual permission editor
```

**RBAC Schema**:
```sql
-- Roles
CREATE TABLE roles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  is_system BOOLEAN DEFAULT false,  -- Can't be deleted
  is_custom BOOLEAN DEFAULT true,
  inherits_from UUID[] DEFAULT ARRAY[]::UUID[],
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(org_id, name)
);

-- Permissions
CREATE TABLE permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  resource TEXT NOT NULL,  -- 'connectors', 'analytics', 'users', 'settings', 'billing'
  action TEXT NOT NULL,    -- 'read', 'write', 'delete', 'admin'
  scope TEXT NOT NULL CHECK (scope IN ('self', 'team', 'org', 'all')),
  conditions JSONB DEFAULT '{}',  -- Additional conditions
  UNIQUE(role_id, resource, action, scope)
);

-- Insert system roles
INSERT INTO roles (name, is_system, is_custom) VALUES
('Super Admin', true, false),
('Organization Admin', true, false),
('Team Lead', true, false),
('Member', true, false),
('Viewer', true, false);

-- Insert default permissions for each role
-- (See detailed permissions in schema above)
```

**Permission Checker**:
```python
from typing import List
from enum import Enum

class Resource(str, Enum):
    CONNECTORS = 'connectors'
    ANALYTICS = 'analytics'
    USERS = 'users'
    SETTINGS = 'settings'
    BILLING = 'billing'

class Action(str, Enum):
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'
    ADMIN = 'admin'

class Scope(str, Enum):
    SELF = 'self'
    TEAM = 'team'
    ORG = 'org'
    ALL = 'all'

class PermissionChecker:
    def __init__(self, user_id: str, org_id: str):
        self.user_id = user_id
        self.org_id = org_id
        self._permissions = None
    
    async def load_permissions(self):
        """Load all permissions for user"""
        roles = await get_user_roles(self.user_id, self.org_id)
        self._permissions = []
        
        for role in roles:
            perms = await get_role_permissions(role.id)
            self._permissions.extend(perms)
            
            # Handle role inheritance
            if role.inherits_from:
                for parent_role_id in role.inherits_from:
                    parent_perms = await get_role_permissions(parent_role_id)
                    self._permissions.extend(parent_perms)
    
    def can(
        self,
        resource: Resource,
        action: Action,
        scope: Scope = Scope.SELF,
        resource_id: str = None
    ) -> bool:
        """Check if user has permission"""
        if not self._permissions:
            return False
        
        for perm in self._permissions:
            # Check wildcard permissions
            if perm.resource == '*' and perm.action == '*':
                return True
            
            # Check resource match
            if perm.resource != resource and perm.resource != '*':
                continue
            
            # Check action match
            if perm.action != action and perm.action != '*':
                continue
            
            # Check scope
            if perm.scope == Scope.ALL:
                return True
            elif perm.scope == Scope.ORG and scope in [Scope.ORG, Scope.TEAM, Scope.SELF]:
                return True
            elif perm.scope == Scope.TEAM and scope in [Scope.TEAM, Scope.SELF]:
                return True
            elif perm.scope == Scope.SELF and scope == Scope.SELF:
                # Verify resource belongs to user
                if resource_id:
                    return await verify_resource_ownership(
                        resource_id, self.user_id
                    )
                return True
        
        return False

# Usage in API route
@app.get("/api/connectors/{connector_id}")
async def get_connector(
    connector_id: str,
    user: User = Depends(get_current_user),
    tenant: TenantContext = Depends(resolve_tenant)
):
    checker = PermissionChecker(user.id, tenant.org_id)
    await checker.load_permissions()
    
    if not checker.can(Resource.CONNECTORS, Action.READ, resource_id=connector_id):
        raise HTTPException(403, "Permission denied")
    
    return await get_connector_by_id(connector_id, tenant.org_id)
```

---

### Workstream 4: Audit Logging (3-4 hours)

**Files to Create**:
```
backend/services/audit/
├── __init__.py
├── audit_logger.py                # Audit event creation
├── audit_viewer.py                # Query audit logs
└── compliance_reporter.py         # Generate compliance reports

supabase/migrations/
└── 20260204_audit_logging.sql

frontend/app/audit/
├── page.tsx                       # Audit log viewer
├── AuditLogTable.tsx              # Event list
└── EventDetails.tsx               # Event detail modal
```

**Audit Log Schema**:
```sql
-- Audit Events
CREATE TABLE audit_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  action TEXT NOT NULL,  -- 'user.login', 'connector.create', etc.
  resource TEXT NOT NULL,
  resource_id TEXT,
  status TEXT NOT NULL CHECK (status IN ('success', 'failure')),
  
  -- Change tracking
  changes JSONB,  -- { before: {...}, after: {...} }
  
  -- Request metadata
  ip_address INET,
  user_agent TEXT,
  session_id TEXT,
  request_id TEXT,
  
  -- Compliance tags
  compliance_tags TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ['gdpr', 'hipaa', 'sox']
  retention_until DATE,  -- Auto-delete after this date
  
  -- Signature for tamper-proofing
  signature TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_audit_org_created ON audit_events(org_id, created_at DESC);
CREATE INDEX idx_audit_user ON audit_events(user_id, created_at DESC);
CREATE INDEX idx_audit_action ON audit_events(action, created_at DESC);
CREATE INDEX idx_audit_resource ON audit_events(resource, resource_id);
CREATE INDEX idx_audit_compliance ON audit_events USING GIN(compliance_tags);

-- Retention policy trigger
CREATE OR REPLACE FUNCTION set_audit_retention()
RETURNS TRIGGER AS $$
BEGIN
  -- Set retention based on compliance tags
  IF 'sox' = ANY(NEW.compliance_tags) THEN
    NEW.retention_until := CURRENT_DATE + INTERVAL '7 years';
  ELSIF 'gdpr' = ANY(NEW.compliance_tags) THEN
    NEW.retention_until := CURRENT_DATE + INTERVAL '3 years';
  ELSIF 'hipaa' = ANY(NEW.compliance_tags) THEN
    NEW.retention_until := CURRENT_DATE + INTERVAL '6 years';
  ELSE
    NEW.retention_until := CURRENT_DATE + INTERVAL '1 year';
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_retention_before_insert
  BEFORE INSERT ON audit_events
  FOR EACH ROW
  EXECUTE FUNCTION set_audit_retention();
```

**Audit Logger**:
```python
import hashlib
import hmac
from typing import Optional, Dict, Any

class AuditLogger:
    def __init__(self, org_id: str, user_id: Optional[str] = None):
        self.org_id = org_id
        self.user_id = user_id
    
    async def log(
        self,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        status: str = 'success',
        changes: Optional[Dict[str, Any]] = None,
        compliance_tags: Optional[List[str]] = None,
        request: Optional[Request] = None
    ):
        """Log an audit event"""
        event = {
            'org_id': self.org_id,
            'user_id': self.user_id,
            'action': action,
            'resource': resource,
            'resource_id': resource_id,
            'status': status,
            'changes': changes,
            'compliance_tags': compliance_tags or [],
            'ip_address': request.client.host if request else None,
            'user_agent': request.headers.get('user-agent') if request else None,
            'session_id': request.state.session_id if request else None,
            'request_id': request.state.request_id if request else None
        }
        
        # Generate tamper-proof signature
        event['signature'] = self._generate_signature(event)
        
        # Insert into database
        await supabase.table('audit_events').insert(event).execute()
    
    def _generate_signature(self, event: dict) -> str:
        """Generate HMAC signature for tamper-proofing"""
        message = json.dumps(event, sort_keys=True)
        secret = os.getenv('AUDIT_SIGNATURE_SECRET')
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

# Usage examples
audit = AuditLogger(org_id='org-123', user_id='user-456')

# Log user login
await audit.log(
    action='user.login',
    resource='auth',
    compliance_tags=['sox', 'gdpr'],
    request=request
)

# Log data export
await audit.log(
    action='data.export',
    resource='connectors',
    resource_id='conn-789',
    changes={'records_exported': 1000, 'format': 'csv'},
    compliance_tags=['gdpr', 'hipaa']
)

# Log permission change
await audit.log(
    action='permission.update',
    resource='users',
    resource_id='user-999',
    changes={
        'before': {'role': 'member'},
        'after': {'role': 'admin'}
    },
    compliance_tags=['sox']
)
```

---

### Workstream 5: White-Label System (4-5 hours)

**Files to Create**:
```
backend/services/branding/
├── __init__.py
├── theme_manager.py               # Theme CRUD
├── domain_manager.py              # Custom domain setup
└── asset_uploader.py              # Logo/favicon upload

frontend/app/settings/branding/
├── page.tsx                       # Branding settings UI
├── ThemeEditor.tsx                # Color/font editor
├── LogoUploader.tsx               # Asset upload
└── DomainConfig.tsx               # Custom domain setup

supabase/migrations/
└── 20260205_white_label.sql

cdn/
└── themes/                        # CDN-hosted theme assets
    ├── [org-id]/
    │   ├── logo.png
    │   ├── favicon.ico
    │   └── custom.css
```

**Branding Schema**:
```sql
-- Brand Configurations
CREATE TABLE brand_configs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  
  -- Custom Domain
  custom_domain TEXT UNIQUE,
  domain_verified BOOLEAN DEFAULT false,
  ssl_certificate TEXT,
  
  -- Theme
  theme JSONB NOT NULL DEFAULT '{
    "primaryColor": "#3B82F6",
    "secondaryColor": "#8B5CF6",
    "accentColor": "#10B981",
    "backgroundColor": "#FFFFFF",
    "textColor": "#1F2937",
    "fontFamily": "Inter"
  }',
  
  -- Assets
  logo_url TEXT,
  favicon_url TEXT,
  background_url TEXT,
  custom_css TEXT,
  
  -- Email Branding
  email_from_name TEXT,
  email_from_address TEXT,
  email_header_logo_url TEXT,
  email_footer_text TEXT,
  
  -- Features
  show_powered_by BOOLEAN DEFAULT true,
  custom_help_link TEXT,
  custom_support_email TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(org_id)
);

-- Domain Verification Tokens
CREATE TABLE domain_verifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  domain TEXT NOT NULL,
  verification_token TEXT NOT NULL UNIQUE,
  verified_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Dynamic Theme Loading**:
```typescript
// frontend/lib/theme.ts
export async function loadOrgTheme(orgSlug: string) {
  const { data: brand } = await supabase
    .from('brand_configs')
    .select('*')
    .eq('org_id', (await getOrgBySlug(orgSlug)).id)
    .single();
  
  if (!brand) return DEFAULT_THEME;
  
  // Apply CSS variables
  const root = document.documentElement;
  const theme = brand.theme;
  
  root.style.setProperty('--color-primary', theme.primaryColor);
  root.style.setProperty('--color-secondary', theme.secondaryColor);
  root.style.setProperty('--color-accent', theme.accentColor);
  root.style.setProperty('--color-background', theme.backgroundColor);
  root.style.setProperty('--color-text', theme.textColor);
  root.style.setProperty('--font-family', theme.fontFamily);
  
  // Load custom CSS
  if (brand.custom_css) {
    const style = document.createElement('style');
    style.textContent = brand.custom_css;
    document.head.appendChild(style);
  }
  
  // Update logo and favicon
  if (brand.logo_url) {
    const logo = document.querySelector('[data-logo]') as HTMLImageElement;
    if (logo) logo.src = brand.logo_url;
  }
  
  if (brand.favicon_url) {
    const favicon = document.querySelector('link[rel="icon"]') as HTMLLinkElement;
    if (favicon) favicon.href = brand.favicon_url;
  }
  
  return brand;
}
```

---

### Workstream 6: API Rate Limiting (3-4 hours)

**Files to Create**:
```
backend/middleware/
├── rate_limiter.py                # Token bucket implementation
└── quota_tracker.py               # Monthly quota tracking

backend/services/monitoring/
├── usage_metrics.py               # Track API usage
└── quota_alerting.py              # Alert when near quota

supabase/migrations/
└── 20260206_rate_limiting.sql

frontend/app/settings/usage/
├── page.tsx                       # Usage dashboard
└── QuotaDisplay.tsx               # Current usage display
```

**Rate Limiting Schema**:
```sql
-- Rate Limit Buckets (in-memory via Redis preferred)
-- Fallback to database for persistence

CREATE TABLE rate_limit_state (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  bucket_key TEXT NOT NULL,  -- 'api:org-123:second'
  tokens_remaining INTEGER NOT NULL,
  last_refill TIMESTAMPTZ NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  UNIQUE(org_id, bucket_key)
);

-- API Usage Tracking
CREATE TABLE api_usage (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  date DATE NOT NULL DEFAULT CURRENT_DATE,
  endpoint TEXT NOT NULL,
  method TEXT NOT NULL,
  count INTEGER NOT NULL DEFAULT 0,
  bytes_transferred BIGINT DEFAULT 0,
  UNIQUE(org_id, date, endpoint, method)
);

CREATE INDEX idx_api_usage_org_date ON api_usage(org_id, date DESC);

-- Monthly Quota Tracking
CREATE TABLE monthly_quotas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  month DATE NOT NULL,  -- First day of month
  api_calls_used INTEGER DEFAULT 0,
  data_volume_used BIGINT DEFAULT 0,  -- bytes
  quotas JSONB NOT NULL,  -- Tier quotas
  overage_charges DECIMAL(10,2) DEFAULT 0,
  UNIQUE(org_id, month)
);
```

**Rate Limiter Implementation**:
```python
from datetime import datetime, timedelta
from typing import Tuple
import redis

class TokenBucketRateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def check_limit(
        self,
        org_id: str,
        tier: str,
        bucket_type: str = 'second'
    ) -> Tuple[bool, dict]:
        """
        Check rate limit using token bucket algorithm.
        
        Returns:
            (allowed, info) tuple where info contains:
            - limit: max requests
            - remaining: tokens remaining
            - resetAt: when bucket refills
        """
        # Get tier limits
        config = RATE_LIMITS[tier]
        limit = getattr(config, f'requestsPer{bucket_type.capitalize()}')
        burst_size = config.burstSize if bucket_type == 'second' else limit
        
        # Redis key
        key = f'rate_limit:{org_id}:{bucket_type}'
        
        # Get current state
        pipeline = self.redis.pipeline()
        pipeline.get(f'{key}:tokens')
        pipeline.get(f'{key}:last_refill')
        tokens_str, last_refill_str = pipeline.execute()
        
        now = datetime.utcnow()
        
        # Initialize if not exists
        if tokens_str is None:
            tokens = burst_size
            last_refill = now
        else:
            tokens = int(tokens_str)
            last_refill = datetime.fromisoformat(last_refill_str)
        
        # Calculate refill
        if bucket_type == 'second':
            refill_interval = timedelta(seconds=1)
            refill_rate = limit  # Tokens per interval
        elif bucket_type == 'hour':
            refill_interval = timedelta(hours=1)
            refill_rate = limit
        else:  # day
            refill_interval = timedelta(days=1)
            refill_rate = limit
        
        # Refill tokens based on time elapsed
        elapsed = now - last_refill
        intervals_passed = elapsed / refill_interval
        tokens_to_add = int(intervals_passed * refill_rate)
        
        if tokens_to_add > 0:
            tokens = min(burst_size, tokens + tokens_to_add)
            last_refill = now
        
        # Check if request allowed
        allowed = tokens > 0
        
        if allowed:
            tokens -= 1
        
        # Update state in Redis
        pipeline = self.redis.pipeline()
        pipeline.set(f'{key}:tokens', tokens, ex=86400)  # 24h expiry
        pipeline.set(f'{key}:last_refill', last_refill.isoformat(), ex=86400)
        pipeline.execute()
        
        # Calculate reset time
        if tokens == 0:
            reset_at = last_refill + refill_interval
        else:
            reset_at = now
        
        return allowed, {
            'limit': limit,
            'remaining': tokens,
            'resetAt': reset_at.isoformat(),
            'retryAfter': max(0, (reset_at - now).total_seconds())
        }

# Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    tenant = await resolve_tenant(request)
    limiter = TokenBucketRateLimiter(redis_client)
    
    # Check second-level limit
    allowed, info = await limiter.check_limit(
        tenant.org_id,
        tenant.tier,
        'second'
    )
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                'error': 'rate_limit_exceeded',
                'message': 'API rate limit exceeded',
                **info
            },
            headers={
                'X-RateLimit-Limit': str(info['limit']),
                'X-RateLimit-Remaining': str(info['remaining']),
                'X-RateLimit-Reset': info['resetAt'],
                'Retry-After': str(int(info['retryAfter']))
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers['X-RateLimit-Limit'] = str(info['limit'])
    response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
    response.headers['X-RateLimit-Reset'] = info['resetAt']
    
    return response
```

---

### Workstream 7: Monitoring & Alerting (3-4 hours)

**Files to Create**:
```
backend/services/monitoring/
├── __init__.py
├── health_checker.py              # Service health monitoring
├── metric_collector.py            # Custom metrics
└── alert_manager.py               # Alert rules and notifications

config/
└── alert_rules.yaml               # Alert configurations

frontend/app/admin/monitoring/
├── page.tsx                       # Monitoring dashboard
├── HealthStatus.tsx               # Service health
├── MetricsChart.tsx               # Time-series metrics
└── AlertsList.tsx                 # Active alerts
```

**Monitoring Schema**:
```sql
-- Health Checks
CREATE TABLE health_checks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  service TEXT NOT NULL,  -- 'api', 'database', 'temporal', 'supabase'
  status TEXT NOT NULL CHECK (status IN ('healthy', 'degraded', 'down')),
  response_time_ms INTEGER,
  error_message TEXT,
  metadata JSONB DEFAULT '{}',
  checked_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_health_service_time ON health_checks(service, checked_at DESC);

-- Custom Metrics
CREATE TABLE custom_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  metric_name TEXT NOT NULL,
  metric_value NUMERIC NOT NULL,
  tags JSONB DEFAULT '{}',
  recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_metrics_org_name_time ON custom_metrics(org_id, metric_name, recorded_at DESC);

-- Alerts
CREATE TABLE alerts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  rule_name TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
  status TEXT NOT NULL CHECK (status IN ('firing', 'resolved')),
  message TEXT NOT NULL,
  details JSONB DEFAULT '{}',
  fired_at TIMESTAMPTZ DEFAULT NOW(),
  resolved_at TIMESTAMPTZ,
  notified_at TIMESTAMPTZ
);

CREATE INDEX idx_alerts_org_status ON alerts(org_id, status, fired_at DESC);
```

**Alert Rules Example**:
```yaml
# config/alert_rules.yaml
rules:
  - name: high_error_rate
    condition: error_rate > 0.05  # 5%
    duration: 5m
    severity: critical
    message: "Error rate exceeded 5% for {{ org_name }}"
    notifications:
      - email
      - slack
      - pagerduty
  
  - name: api_quota_exceeded
    condition: api_usage > quota * 0.9  # 90% of quota
    duration: 1m
    severity: warning
    message: "API quota at {{ usage_percent }}% for {{ org_name }}"
    notifications:
      - email
  
  - name: slow_api_response
    condition: p95_response_time > 2000  # 2 seconds
    duration: 10m
    severity: warning
    message: "API response time degraded: P95 = {{ p95_ms }}ms"
    notifications:
      - slack
  
  - name: connector_sync_failure
    condition: sync_success_rate < 0.95  # 95%
    duration: 5m
    severity: warning
    message: "Connector sync failures for {{ connector_name }}"
    notifications:
      - email
      - slack
```

---

## Database Schema Complete

### Schema Migration Summary

**Total New Tables**: 15
- `organizations`
- `org_members`
- `teams`
- `team_members`
- `sso_configurations`
- `sso_login_events`
- `roles`
- `permissions`
- `audit_events`
- `brand_configs`
- `domain_verifications`
- `rate_limit_state`
- `api_usage`
- `monthly_quotas`
- `health_checks`
- `custom_metrics`
- `alerts`

**Total Indexes**: 25+
**Total RLS Policies**: 30+
**Total Triggers**: 5

---

## Integration Points

### With Previous Phases

**Phase 1 (Temporal)**:
- Tenant-aware workflows
- Audit logging integration
- Health monitoring

**Phase 2 (LangGraph)**:
- Multi-tenant agent isolation
- Organization-specific AI settings

**Phase 3 (Supabase)**:
- Extended RLS policies
- Multi-schema support

**Phase 4 (Frontend)**:
- Dynamic theming
- SSO login flows
- Admin dashboards

**Phase 5 (Connectors)**:
- Per-organization connector configs
- Usage tracking per tenant

**Phase 6A & 6B**:
- Multi-tenant analytics
- Organization-specific marketplace
- White-label custom connectors

---

## Testing Strategy

### Test Categories

**1. Multi-Tenancy Tests** (20 tests)
- Tenant isolation verification
- Cross-tenant data leakage prevention
- Schema-level isolation
- RLS policy enforcement

**2. SSO Integration Tests** (15 tests)
- SAML authentication flow
- OIDC authentication flow
- JIT provisioning
- Group mapping
- SSO failure handling

**3. RBAC Tests** (18 tests)
- Permission checking
- Role inheritance
- Custom role creation
- Permission scope enforcement

**4. Audit Logging Tests** (12 tests)
- Event logging
- Tamper-proof verification
- Retention policies
- Compliance reporting

**5. White-Label Tests** (10 tests)
- Theme application
- Custom domain routing
- Asset upload
- Email branding

**6. Rate Limiting Tests** (12 tests)
- Token bucket algorithm
- Quota enforcement
- Burst handling
- Tier-based limits

**7. Monitoring Tests** (10 tests)
- Health checks
- Metric collection
- Alert firing
- Alert resolution

**Total New Tests**: 97+ tests

---

## Performance Considerations

### Multi-Tenancy Performance

|| Metric | Target |
||--------|--------|
|| Tenant resolution | < 10ms |
|| RLS query overhead | < 5% |
|| Cross-tenant query | Prevented (fail-safe) |

### SSO Performance

|| Metric | Target |
||--------|--------|
|| SAML redirect | < 200ms |
|| JIT provisioning | < 500ms |
|| SSO callback | < 1s |

### RBAC Performance

|| Metric | Target |
||--------|--------|
|| Permission check | < 5ms (cached) |
|| Role lookup | < 10ms |
|| Permission load | < 50ms |

### Audit Performance

|| Metric | Target |
||--------|--------|
|| Event logging | < 10ms (async) |
|| Audit query | < 500ms |
|| Compliance report | < 10s |

---

## Cost Analysis

### Additional Infrastructure

|| Service | Component | Monthly Cost |
||---------|-----------|--------------|
|| Redis | Rate limiting cache | $30-50 |
|| CDN | White-label assets | $20-40 |
|| Certificate | SSL for custom domains | $0 (Let's Encrypt) |
|| Storage | Audit logs (5 years) | $50-100 |
|| Monitoring | Health checks & alerts | $30-50 |
|| **Phase 6C Total** | | **~$130-240** |

**Combined Cost (6A + 6B + 6C)**: ~$430-610/month

### Cost Optimization

- Use Redis caching for rate limits (cheaper than DB)
- CDN for white-label assets (reduce bandwidth)
- Compress audit logs (reduce storage)
- Archive old audits to cold storage

---

## Timeline

|| Week | Deliverables |
||------|--------------|
|| **Week 1** | • Multi-tenancy foundation<br>• SSO integration (SAML + OIDC) |
|| **Week 2** | • RBAC system<br>• Audit logging |
|| **Week 3** | • White-label system<br>• Rate limiting |
|| **Week 4** | • Monitoring & alerting<br>• Testing & polish<br>• Documentation |

**Total Duration**: 20-30 hours over 3-4 weeks

---

## Risk Register

|| Risk | Probability | Impact | Mitigation |
||------|-------------|--------|------------|
|| Multi-tenancy data leakage | Low | Critical | Comprehensive RLS testing, security audits |
|| SSO misconfiguration | Medium | High | Wizard-based setup, validation checks |
|| RBAC complexity | Medium | Medium | Clear UI, permission templates |
|| Audit log volume | High | Medium | Retention policies, log compression |
|| Rate limit bypass | Low | Medium | Multiple check layers, Redis fallback |
|| White-label asset abuse | Low | Low | File type validation, size limits |
|| Performance degradation | Medium | High | Caching, indexing, query optimization |
|| Compliance gaps | Low | Critical | Legal review, automated compliance checks |

---

## Success Metrics

|| Metric | Target |
||--------|--------|
|| Organizations supported | 1000+ |
|| SSO providers | 6+ |
|| Permission checks/sec | 10,000+ |
|| Audit events/day | 1M+ |
|| White-label deployments | 50+ |
|| API rate limit accuracy | 99.9% |
|| System uptime | 99.99% |
|| Compliance audit pass | 100% |

---

## Compliance Certifications

### Target Certifications
- ✅ SOC 2 Type II
- ✅ GDPR Compliant
- ✅ HIPAA Ready
- ✅ ISO 27001
- ✅ PCI DSS (if handling payments)

### Required Features (All Included)
- [x] Multi-tenant data isolation
- [x] Audit logging (7-year retention)
- [x] Encryption at rest
- [x] Encryption in transit
- [x] SSO/SAML support
- [x] Role-based access control
- [x] Data residency options
- [x] Right to deletion (GDPR)
- [x] Data export capabilities
- [x] Incident response procedures

---

## Next Steps After Phase 6C

1. **Phase 7**: Mobile Apps (iOS/Android)
2. **Phase 8**: AI/ML Features (anomaly detection, predictions)
3. **Phase 9**: Advanced Workflows (visual builder)
4. **Phase 10**: Public API & Developer Platform
5. **IPO Readiness**: Scale to 10,000+ organizations

---

## Documentation Deliverables

### For Developers
- Multi-tenancy implementation guide
- SSO integration cookbook
- RBAC pattern examples
- Audit logging best practices
- White-label setup guide

### For Operations
- Tenant provisioning runbook
- SSO troubleshooting guide
- Performance optimization guide
- Monitoring setup guide
- Incident response procedures

### For Compliance
- Security architecture document
- Data processing agreements
- Privacy policy templates
- Audit report generators
- Compliance checklist

---

**Status**: READY FOR PLAN REVIEW  
**Prerequisites**: Phase 6B Complete ✅  
**Estimated Start**: After Phase 6B deployment

**This is enterprise-ready architecture. Let's build it! 🚀**
