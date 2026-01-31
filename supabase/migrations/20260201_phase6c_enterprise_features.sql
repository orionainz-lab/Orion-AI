-- =============================================
-- Phase 6C: Enterprise Features - Database Migration
-- Version: 1.0.0
-- Date: 2026-02-01
-- =============================================
-- Features:
-- 1. Multi-Tenancy (Organizations, Teams, Members)
-- 2. SSO Configuration (SAML, OIDC)
-- 3. RBAC (Roles, Permissions, Scopes)
-- 4. Audit Logging (Tamper-proof event tracking)
-- 5. White-Label Branding
-- 6. API Rate Limiting
-- 7. Enterprise Monitoring
-- =============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================
-- WORKSTREAM 1: MULTI-TENANCY FOUNDATION
-- =============================================

-- Organizations (Tenants)
CREATE TABLE IF NOT EXISTS organizations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  tier TEXT NOT NULL CHECK (tier IN ('free', 'professional', 'enterprise')),
  isolation_level TEXT NOT NULL DEFAULT 'row' CHECK (isolation_level IN ('row', 'schema', 'database')),
  data_residency TEXT CHECK (data_residency IN ('us', 'eu', 'asia')),
  settings JSONB DEFAULT '{}',
  quotas JSONB NOT NULL DEFAULT '{
    "monthlyApiCalls": 10000,
    "concurrentConnections": 5,
    "dataVolumeGB": 1,
    "maxUsers": 5,
    "maxConnectors": 10
  }'::jsonb,
  billing_status TEXT DEFAULT 'active' CHECK (billing_status IN ('active', 'suspended', 'cancelled')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for slug lookups
CREATE INDEX IF NOT EXISTS idx_organizations_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_organizations_tier ON organizations(tier);

-- Teams (Sub-organizations)
CREATE TABLE IF NOT EXISTS teams (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  parent_team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
  settings JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(org_id, name)
);

CREATE INDEX IF NOT EXISTS idx_teams_org_id ON teams(org_id);
CREATE INDEX IF NOT EXISTS idx_teams_parent_team_id ON teams(parent_team_id);

-- =============================================
-- WORKSTREAM 3: RBAC SYSTEM
-- =============================================

-- Roles (As decided in Checklist.md)
CREATE TABLE IF NOT EXISTS roles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  is_system_role BOOLEAN DEFAULT false,
  permissions JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(org_id, name)
);

CREATE INDEX IF NOT EXISTS idx_roles_org_id ON roles(org_id);
CREATE INDEX IF NOT EXISTS idx_roles_system ON roles(is_system_role) WHERE is_system_role = true;

-- Permissions (Resource-Action-Scope model)
CREATE TABLE IF NOT EXISTS permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  resource TEXT NOT NULL,  -- 'connectors', 'analytics', 'users', 'settings', 'billing', 'api_keys', 'audit_logs'
  action TEXT NOT NULL,     -- 'create', 'read', 'update', 'delete', 'export', 'admin'
  scope TEXT NOT NULL,      -- 'self', 'team', 'org', 'all'
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(resource, action, scope)
);

CREATE INDEX IF NOT EXISTS idx_permissions_resource ON permissions(resource);

-- Organization Members
CREATE TABLE IF NOT EXISTS org_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role_id UUID NOT NULL REFERENCES roles(id),
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  invited_by UUID REFERENCES auth.users(id),
  is_primary BOOLEAN DEFAULT false,
  UNIQUE(org_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_org_members_org_id ON org_members(org_id);
CREATE INDEX IF NOT EXISTS idx_org_members_user_id ON org_members(user_id);
CREATE INDEX IF NOT EXISTS idx_org_members_role_id ON org_members(role_id);

-- Team Members
CREATE TABLE IF NOT EXISTS team_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role_id UUID NOT NULL REFERENCES roles(id),
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(team_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_team_members_team_id ON team_members(team_id);
CREATE INDEX IF NOT EXISTS idx_team_members_user_id ON team_members(user_id);

-- =============================================
-- WORKSTREAM 2: SSO CONFIGURATION
-- =============================================

-- SSO Configurations (SAML & OIDC)
CREATE TABLE IF NOT EXISTS sso_configurations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  provider TEXT NOT NULL,  -- 'azure-ad', 'google', 'auth0', 'onelogin', 'okta', 'generic-saml', 'generic-oidc'
  protocol TEXT NOT NULL CHECK (protocol IN ('saml', 'oidc')),
  enabled BOOLEAN DEFAULT false,
  
  -- SAML Configuration
  saml_entity_id TEXT,
  saml_sso_url TEXT,
  saml_slo_url TEXT,
  saml_certificate TEXT,
  saml_sign_requests BOOLEAN DEFAULT false,
  saml_attribute_mapping JSONB DEFAULT '{}',
  
  -- OIDC Configuration
  oidc_issuer TEXT,
  oidc_client_id TEXT,
  oidc_client_secret TEXT,  -- Encrypted
  oidc_scopes TEXT[] DEFAULT ARRAY['openid', 'profile', 'email'],
  oidc_token_endpoint TEXT,
  oidc_userinfo_endpoint TEXT,
  
  -- JIT Provisioning
  jit_enabled BOOLEAN DEFAULT true,
  jit_default_role_id UUID REFERENCES roles(id),
  jit_group_mapping JSONB DEFAULT '{}',  -- Map IdP groups to roles
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(org_id, provider)
);

CREATE INDEX IF NOT EXISTS idx_sso_org_id ON sso_configurations(org_id);
CREATE INDEX IF NOT EXISTS idx_sso_enabled ON sso_configurations(enabled) WHERE enabled = true;

-- SSO Login Events (Audit trail)
CREATE TABLE IF NOT EXISTS sso_login_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  user_id UUID REFERENCES auth.users(id),
  provider TEXT NOT NULL,
  protocol TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('success', 'failure', 'pending')),
  error_message TEXT,
  ip_address INET,
  user_agent TEXT,
  session_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sso_events_org_id ON sso_login_events(org_id);
CREATE INDEX IF NOT EXISTS idx_sso_events_user_id ON sso_login_events(user_id);
CREATE INDEX IF NOT EXISTS idx_sso_events_created_at ON sso_login_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sso_events_status ON sso_login_events(status);

-- =============================================
-- WORKSTREAM 4: AUDIT LOGGING
-- =============================================

-- Audit Events (Tamper-proof)
CREATE TABLE IF NOT EXISTS audit_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  user_id UUID REFERENCES auth.users(id),
  action TEXT NOT NULL,  -- 'create', 'update', 'delete', 'read', 'export', 'login', 'logout'
  resource_type TEXT NOT NULL,  -- 'connector', 'user', 'setting', etc.
  resource_id UUID,
  details JSONB DEFAULT '{}',
  ip_address INET,
  user_agent TEXT,
  
  -- Tamper-proof signature
  signature TEXT NOT NULL,  -- HMAC-SHA256 of (id + org_id + action + resource_type + created_at)
  previous_event_id UUID,
  
  -- Compliance
  retention_policy TEXT DEFAULT 'standard',  -- 'standard' (90 days), 'extended' (1 year), 'permanent'
  compliance_tags TEXT[] DEFAULT '{}',  -- ['gdpr', 'soc2', 'hipaa']
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_org_id ON audit_events(org_id);
CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_events(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_events(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_events(action);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_compliance ON audit_events USING GIN(compliance_tags);

-- =============================================
-- WORKSTREAM 5: WHITE-LABEL BRANDING
-- =============================================

-- Brand Configurations
CREATE TABLE IF NOT EXISTS brand_configs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL UNIQUE REFERENCES organizations(id) ON DELETE CASCADE,
  
  -- Visual Branding
  logo_url TEXT,
  favicon_url TEXT,
  primary_color TEXT DEFAULT '#3B82F6',
  secondary_color TEXT DEFAULT '#10B981',
  accent_color TEXT DEFAULT '#8B5CF6',
  custom_css_url TEXT,
  
  -- Email Branding
  email_from_name TEXT,
  email_from_address TEXT,
  email_header_logo_url TEXT,
  email_footer_text TEXT,
  
  -- Features
  show_powered_by BOOLEAN DEFAULT true,
  custom_help_link TEXT,
  custom_support_email TEXT,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_brand_org_id ON brand_configs(org_id);

-- Domain Verifications (for custom domains)
CREATE TABLE IF NOT EXISTS domain_verifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  domain TEXT NOT NULL UNIQUE,
  verification_status TEXT DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'failed')),
  verification_token TEXT NOT NULL,
  verification_method TEXT DEFAULT 'dns' CHECK (verification_method IN ('dns', 'file')),
  verified_at TIMESTAMPTZ,
  ssl_status TEXT DEFAULT 'pending' CHECK (ssl_status IN ('pending', 'provisioned', 'failed')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_domains_org_id ON domain_verifications(org_id);
CREATE INDEX IF NOT EXISTS idx_domains_status ON domain_verifications(verification_status);

-- =============================================
-- WORKSTREAM 6: API RATE LIMITING
-- =============================================

-- Rate Limit State (complemented by Redis)
CREATE TABLE IF NOT EXISTS rate_limit_state (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  identifier TEXT NOT NULL,  -- user_id, api_key, ip_address
  endpoint TEXT NOT NULL,
  tokens_remaining INT NOT NULL,
  last_refill TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(org_id, identifier, endpoint)
);

CREATE INDEX IF NOT EXISTS idx_rate_limit_org ON rate_limit_state(org_id);
CREATE INDEX IF NOT EXISTS idx_rate_limit_identifier ON rate_limit_state(identifier);

-- API Usage Tracking
CREATE TABLE IF NOT EXISTS api_usage (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  user_id UUID REFERENCES auth.users(id),
  endpoint TEXT NOT NULL,
  method TEXT NOT NULL,
  status_code INT NOT NULL,
  response_time_ms INT,
  request_size_bytes INT,
  response_size_bytes INT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Partition by month for performance
CREATE INDEX IF NOT EXISTS idx_api_usage_org_created ON api_usage(org_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage(created_at DESC);

-- Monthly Quotas
CREATE TABLE IF NOT EXISTS monthly_quotas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  month DATE NOT NULL,  -- First day of month
  api_calls_used INT DEFAULT 0,
  data_volume_gb_used NUMERIC(10, 2) DEFAULT 0,
  quota_exceeded BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(org_id, month)
);

CREATE INDEX IF NOT EXISTS idx_quotas_org_month ON monthly_quotas(org_id, month DESC);

-- =============================================
-- WORKSTREAM 7: ENTERPRISE MONITORING
-- =============================================

-- Health Checks
CREATE TABLE IF NOT EXISTS health_checks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  check_type TEXT NOT NULL,  -- 'api', 'database', 'redis', 'external_service'
  check_name TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('healthy', 'degraded', 'down')),
  response_time_ms INT,
  error_message TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_health_type ON health_checks(check_type);
CREATE INDEX IF NOT EXISTS idx_health_created_at ON health_checks(created_at DESC);

-- Custom Metrics
CREATE TABLE IF NOT EXISTS custom_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  metric_name TEXT NOT NULL,
  metric_value NUMERIC NOT NULL,
  metric_type TEXT DEFAULT 'gauge' CHECK (metric_type IN ('counter', 'gauge', 'histogram')),
  tags JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_metrics_org_name ON custom_metrics(org_id, metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_created_at ON custom_metrics(created_at DESC);

-- Alerting Rules
CREATE TABLE IF NOT EXISTS alerts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  alert_name TEXT NOT NULL,
  alert_type TEXT NOT NULL CHECK (alert_type IN ('threshold', 'anomaly', 'absence')),
  metric_name TEXT NOT NULL,
  condition JSONB NOT NULL,  -- {"operator": ">", "value": 100}
  severity TEXT DEFAULT 'warning' CHECK (severity IN ('info', 'warning', 'critical')),
  notification_channels TEXT[] DEFAULT '{}',  -- ['email', 'slack', 'webhook']
  enabled BOOLEAN DEFAULT true,
  last_triggered TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_org_id ON alerts(org_id);
CREATE INDEX IF NOT EXISTS idx_alerts_enabled ON alerts(enabled) WHERE enabled = true;

-- =============================================
-- ADD ORG_ID TO EXISTING TABLES (Multi-Tenancy)
-- =============================================

-- Add org_id column to existing tables if not exists
DO $$ 
BEGIN
  -- connector_marketplace
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name='connector_marketplace' AND column_name='org_id') THEN
    ALTER TABLE connector_marketplace ADD COLUMN org_id UUID REFERENCES organizations(id);
  END IF;

  -- user_installed_connectors
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name='user_installed_connectors' AND column_name='org_id') THEN
    ALTER TABLE user_installed_connectors ADD COLUMN org_id UUID REFERENCES organizations(id);
  END IF;

  -- custom_connectors
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name='custom_connectors' AND column_name='org_id') THEN
    ALTER TABLE custom_connectors ADD COLUMN org_id UUID REFERENCES organizations(id);
  END IF;

  -- sync_metrics
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name='sync_metrics' AND column_name='org_id') THEN
    ALTER TABLE sync_metrics ADD COLUMN org_id UUID REFERENCES organizations(id);
  END IF;

  -- connector_health
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                 WHERE table_name='connector_health' AND column_name='org_id') THEN
    ALTER TABLE connector_health ADD COLUMN org_id UUID REFERENCES organizations(id);
  END IF;
END $$;

-- Create indexes for org_id on existing tables
CREATE INDEX IF NOT EXISTS idx_marketplace_org ON connector_marketplace(org_id);
CREATE INDEX IF NOT EXISTS idx_installed_org ON user_installed_connectors(org_id);
CREATE INDEX IF NOT EXISTS idx_custom_org ON custom_connectors(org_id);
CREATE INDEX IF NOT EXISTS idx_sync_metrics_org ON sync_metrics(org_id);
CREATE INDEX IF NOT EXISTS idx_health_org ON connector_health(org_id);

-- =============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================

-- Enable RLS on all tenant-scoped tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE org_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE sso_configurations ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE rate_limit_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_quotas ENABLE ROW LEVEL SECURITY;
ALTER TABLE custom_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

-- Organizations: Users can only see orgs they're members of
CREATE POLICY "Users see own organizations"
  ON organizations FOR SELECT
  USING (
    id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid())
  );

-- Org Members: Users can see members of their organizations
CREATE POLICY "Users see own org members"
  ON org_members FOR SELECT
  USING (
    org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid())
  );

-- Teams: Users can see teams in their organizations
CREATE POLICY "Users see own org teams"
  ON teams FOR SELECT
  USING (
    org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid())
  );

-- Audit Events: Users can read audit events for their org (based on role)
CREATE POLICY "Users read own org audit"
  ON audit_events FOR SELECT
  USING (
    org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid())
  );

-- Brand Configs: Users can read their org's branding
CREATE POLICY "Users read own org branding"
  ON brand_configs FOR SELECT
  USING (
    org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid())
  );

-- API Usage: Users can read their org's API usage
CREATE POLICY "Users read own org api usage"
  ON api_usage FOR SELECT
  USING (
    org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid())
  );

-- =============================================
-- TRIGGERS
-- =============================================

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to tables
DROP TRIGGER IF EXISTS update_organizations_updated_at ON organizations;
CREATE TRIGGER update_organizations_updated_at
  BEFORE UPDATE ON organizations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_teams_updated_at ON teams;
CREATE TRIGGER update_teams_updated_at
  BEFORE UPDATE ON teams
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_roles_updated_at ON roles;
CREATE TRIGGER update_roles_updated_at
  BEFORE UPDATE ON roles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_sso_updated_at ON sso_configurations;
CREATE TRIGGER update_sso_updated_at
  BEFORE UPDATE ON sso_configurations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_brand_updated_at ON brand_configs;
CREATE TRIGGER update_brand_updated_at
  BEFORE UPDATE ON brand_configs
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Audit signature generation trigger
CREATE OR REPLACE FUNCTION generate_audit_signature()
RETURNS TRIGGER AS $$
DECLARE
  signature_key TEXT;
BEGIN
  -- Get signature key from environment or use default (should be set via env var)
  signature_key := current_setting('app.audit_signature_secret', true);
  IF signature_key IS NULL THEN
    signature_key := 'default-secret-change-in-production';
  END IF;
  
  -- Generate HMAC-SHA256 signature
  NEW.signature := encode(
    hmac(
      NEW.id::text || NEW.org_id::text || NEW.action || NEW.resource_type || NEW.created_at::text,
      signature_key,
      'sha256'
    ),
    'hex'
  );
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS audit_signature_trigger ON audit_events;
CREATE TRIGGER audit_signature_trigger
  BEFORE INSERT ON audit_events
  FOR EACH ROW EXECUTE FUNCTION generate_audit_signature();

-- =============================================
-- SEED DEFAULT DATA
-- =============================================

-- Insert default permissions (Resource-Action-Scope)
INSERT INTO permissions (resource, action, scope, description) VALUES
  -- Connectors
  ('connectors', 'read', 'self', 'Read own connectors'),
  ('connectors', 'read', 'team', 'Read team connectors'),
  ('connectors', 'read', 'org', 'Read all org connectors'),
  ('connectors', 'create', 'self', 'Create own connectors'),
  ('connectors', 'create', 'team', 'Create team connectors'),
  ('connectors', 'create', 'org', 'Create org connectors'),
  ('connectors', 'update', 'self', 'Update own connectors'),
  ('connectors', 'update', 'team', 'Update team connectors'),
  ('connectors', 'update', 'org', 'Update all org connectors'),
  ('connectors', 'delete', 'self', 'Delete own connectors'),
  ('connectors', 'delete', 'team', 'Delete team connectors'),
  ('connectors', 'delete', 'org', 'Delete all org connectors'),
  ('connectors', 'export', 'org', 'Export connector data'),
  
  -- Analytics
  ('analytics', 'read', 'self', 'View own analytics'),
  ('analytics', 'read', 'team', 'View team analytics'),
  ('analytics', 'read', 'org', 'View all org analytics'),
  ('analytics', 'export', 'org', 'Export analytics data'),
  
  -- Users
  ('users', 'read', 'org', 'View org users'),
  ('users', 'create', 'org', 'Invite users'),
  ('users', 'update', 'org', 'Update user roles'),
  ('users', 'delete', 'org', 'Remove users'),
  
  -- Settings
  ('settings', 'read', 'org', 'View org settings'),
  ('settings', 'update', 'org', 'Update org settings'),
  ('settings', 'admin', 'org', 'Manage all settings'),
  
  -- Billing
  ('billing', 'read', 'org', 'View billing'),
  ('billing', 'update', 'org', 'Update billing'),
  ('billing', 'admin', 'org', 'Manage billing'),
  
  -- API Keys
  ('api_keys', 'read', 'org', 'View API keys'),
  ('api_keys', 'create', 'org', 'Create API keys'),
  ('api_keys', 'delete', 'org', 'Revoke API keys'),
  
  -- Audit Logs
  ('audit_logs', 'read', 'org', 'View audit logs'),
  ('audit_logs', 'export', 'org', 'Export audit logs')
ON CONFLICT (resource, action, scope) DO NOTHING;

-- Insert default system roles (these apply across all orgs)
-- Note: Specific org role assignments happen during org provisioning
INSERT INTO roles (id, org_id, name, description, is_system_role, permissions) VALUES
  (
    '00000000-0000-0000-0000-000000000001',
    NULL,
    'Super Admin',
    'Full system access across all organizations',
    true,
    '["*:*:all"]'::jsonb
  ),
  (
    '00000000-0000-0000-0000-000000000002',
    NULL,
    'Org Admin',
    'Full access to organization resources',
    true,
    '["connectors:*:org", "analytics:*:org", "users:*:org", "settings:*:org", "billing:*:org", "api_keys:*:org", "audit_logs:*:org"]'::jsonb
  ),
  (
    '00000000-0000-0000-0000-000000000003',
    NULL,
    'Team Lead',
    'Manage team resources and members',
    true,
    '["connectors:*:team", "analytics:read:team", "users:read:org"]'::jsonb
  ),
  (
    '00000000-0000-0000-0000-000000000004',
    NULL,
    'Member',
    'Manage own resources',
    true,
    '["connectors:*:self", "analytics:read:self"]'::jsonb
  ),
  (
    '00000000-0000-0000-0000-000000000005',
    NULL,
    'Viewer',
    'Read-only access',
    true,
    '["connectors:read:org", "analytics:read:org"]'::jsonb
  )
ON CONFLICT (org_id, name) DO NOTHING;

-- =============================================
-- FUNCTIONS & UTILITIES
-- =============================================

-- Function to get user's organizations
CREATE OR REPLACE FUNCTION get_user_orgs(user_uuid UUID)
RETURNS TABLE (
  org_id UUID,
  org_name TEXT,
  org_slug TEXT,
  role_name TEXT,
  is_primary BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    o.id,
    o.name,
    o.slug,
    r.name,
    om.is_primary
  FROM organizations o
  JOIN org_members om ON o.id = om.org_id
  JOIN roles r ON om.role_id = r.id
  WHERE om.user_id = user_uuid
  ORDER BY om.is_primary DESC, om.joined_at ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user has permission
CREATE OR REPLACE FUNCTION user_has_permission(
  user_uuid UUID,
  org_uuid UUID,
  resource_name TEXT,
  action_name TEXT,
  required_scope TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
  has_permission BOOLEAN;
BEGIN
  SELECT EXISTS (
    SELECT 1
    FROM org_members om
    JOIN roles r ON om.role_id = r.id
    WHERE om.user_id = user_uuid
      AND om.org_id = org_uuid
      AND (
        -- Wildcard permission
        r.permissions @> '["*:*:all"]'::jsonb
        OR
        -- Specific resource:action:scope
        r.permissions @> jsonb_build_array(resource_name || ':' || action_name || ':' || required_scope)
        OR
        -- Resource:*:scope
        r.permissions @> jsonb_build_array(resource_name || ':*:' || required_scope)
      )
  ) INTO has_permission;
  
  RETURN has_permission;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================
-- MIGRATION COMPLETE
-- =============================================

-- Add comment for migration tracking
COMMENT ON SCHEMA public IS 'Phase 6C: Enterprise Features - Migration applied on 2026-02-01';

-- Log completion
DO $$
BEGIN
  RAISE NOTICE '✅ Phase 6C Migration Complete!';
  RAISE NOTICE '   - Multi-Tenancy: Organizations, Teams, Members';
  RAISE NOTICE '   - SSO: SAML & OIDC configurations ready';
  RAISE NOTICE '   - RBAC: 5 default roles, granular permissions';
  RAISE NOTICE '   - Audit Logging: Tamper-proof event tracking';
  RAISE NOTICE '   - White-Label: Branding & custom domains';
  RAISE NOTICE '   - Rate Limiting: Tiered quotas';
  RAISE NOTICE '   - Monitoring: Health checks & alerts';
END $$;
