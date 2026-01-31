-- =============================================
-- Phase 6C: Enterprise Features - Seed Data
-- Version: 1.0.0
-- Date: 2026-02-01
-- =============================================
-- Purpose: Seed realistic test data for Phase 6C
-- - Sample organizations (different tiers)
-- - SSO configurations (Azure AD, Google, Auth0, OneLogin)
-- - Brand configurations
-- - Sample audit events
-- - Health check data
-- =============================================

-- =============================================
-- 1. SAMPLE ORGANIZATIONS
-- =============================================

-- Demo Organization (Free Tier)
INSERT INTO organizations (id, name, slug, tier, isolation_level, quotas, billing_status) VALUES
(
  '11111111-1111-1111-1111-111111111111',
  'Acme Corp Demo',
  'acme-demo',
  'free',
  'row',
  '{
    "monthlyApiCalls": 10000,
    "concurrentConnections": 5,
    "dataVolumeGB": 1,
    "maxUsers": 5,
    "maxConnectors": 10
  }'::jsonb,
  'active'
);

-- Professional Organization
INSERT INTO organizations (id, name, slug, tier, isolation_level, data_residency, quotas, billing_status) VALUES
(
  '22222222-2222-2222-2222-222222222222',
  'TechStart Inc',
  'techstart',
  'professional',
  'row',
  'us',
  '{
    "monthlyApiCalls": 100000,
    "concurrentConnections": 25,
    "dataVolumeGB": 10,
    "maxUsers": 25,
    "maxConnectors": 50
  }'::jsonb,
  'active'
);

-- Enterprise Organization
INSERT INTO organizations (id, name, slug, tier, isolation_level, data_residency, quotas, billing_status) VALUES
(
  '33333333-3333-3333-3333-333333333333',
  'Global Enterprises Ltd',
  'global-enterprises',
  'enterprise',
  'schema',
  'eu',
  '{
    "monthlyApiCalls": 1000000,
    "concurrentConnections": 100,
    "dataVolumeGB": 100,
    "maxUsers": -1,
    "maxConnectors": -1
  }'::jsonb,
  'active'
);

-- =============================================
-- 2. SAMPLE TEAMS
-- =============================================

-- Teams for TechStart Inc
INSERT INTO teams (id, org_id, name, description) VALUES
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '22222222-2222-2222-2222-222222222222', 'Engineering', 'Engineering team'),
  ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '22222222-2222-2222-2222-222222222222', 'Sales', 'Sales team'),
  ('cccccccc-cccc-cccc-cccc-cccccccccccc', '22222222-2222-2222-2222-222222222222', 'Marketing', 'Marketing team');

-- Teams for Global Enterprises Ltd
INSERT INTO teams (id, org_id, name, description) VALUES
  ('dddddddd-dddd-dddd-dddd-dddddddddddd', '33333333-3333-3333-3333-333333333333', 'Platform', 'Platform engineering'),
  ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '33333333-3333-3333-3333-333333333333', 'Data Science', 'Data science team'),
  ('ffffffff-ffff-ffff-ffff-ffffffffffff', '33333333-3333-3333-3333-333333333333', 'Operations', 'Operations team');

-- =============================================
-- 3. SSO CONFIGURATIONS (From Checklist.md)
-- =============================================

-- Azure AD (OIDC) - For Global Enterprises
INSERT INTO sso_configurations (
  org_id,
  provider,
  protocol,
  enabled,
  oidc_issuer,
  oidc_client_id,
  oidc_client_secret,
  oidc_scopes,
  jit_enabled,
  jit_default_role_id
) VALUES (
  '33333333-3333-3333-3333-333333333333',
  'azure-ad',
  'oidc',
  true,
  'https://login.microsoftonline.com/22116407-6817-4c85-96ce-1b6d4e631844/v2.0',
  'de01844a-115d-4789-8b5f-eab412c6089e',
  'ISD8Q~dypu1jXm33lD71uTerp5fWAWHqGhvmCahN',  -- In production, encrypt this!
  ARRAY['openid', 'profile', 'email'],
  true,
  '00000000-0000-0000-0000-000000000004'  -- Member role
);

-- Google Workspace (OIDC) - For TechStart Inc
INSERT INTO sso_configurations (
  org_id,
  provider,
  protocol,
  enabled,
  oidc_issuer,
  oidc_client_id,
  oidc_client_secret,
  oidc_scopes,
  jit_enabled,
  jit_default_role_id
) VALUES (
  '22222222-2222-2222-2222-222222222222',
  'google',
  'oidc',
  true,
  'https://accounts.google.com',
  '27144313651-o4jt3m20kg43f96g35phgk7v224tkqqm.apps.googleusercontent.com',
  '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',
  ARRAY['openid', 'profile', 'email'],
  true,
  '00000000-0000-0000-0000-000000000004'  -- Member role
);

-- Auth0 (OIDC) - For Acme Demo
INSERT INTO sso_configurations (
  org_id,
  provider,
  protocol,
  enabled,
  oidc_issuer,
  oidc_client_id,
  oidc_client_secret,
  oidc_scopes,
  jit_enabled,
  jit_default_role_id
) VALUES (
  '11111111-1111-1111-1111-111111111111',
  'auth0',
  'oidc',
  true,
  'https://dev-46h61t2r8joe5aoc.au.auth0.com',
  'mC1CAFbMsAcat0Uqnyr5NV5ljHOvQjQQ',
  'GmdY_3ZDiogh8vHC2zBsn9tf_7CDxGpI0W0tgiAV8Wv0tVdTnz606qxKuDptOACf',
  ARRAY['openid', 'profile', 'email'],
  true,
  '00000000-0000-0000-0000-000000000004'  -- Member role
);

-- OneLogin (SAML) - For Global Enterprises (as secondary)
INSERT INTO sso_configurations (
  org_id,
  provider,
  protocol,
  enabled,
  saml_entity_id,
  saml_sso_url,
  saml_slo_url,
  saml_certificate,
  saml_sign_requests,
  jit_enabled,
  jit_default_role_id
) VALUES (
  '33333333-3333-3333-3333-333333333333',
  'onelogin',
  'saml',
  false,  -- Disabled initially, can be enabled later
  'https://app.onelogin.com/saml/metadata/a156d5fe-9b16-4613-a498-ae8dcacc33a3',
  'https://orion-ai.onelogin.com/trust/saml2/http-post/sso/a156d5fe-9b16-4613-a498-ae8dcacc33a3',
  'https://orion-ai.onelogin.com/trust/saml2/http-redirect/slo/4357754',
  '-----BEGIN CERTIFICATE-----
MIID3zCCAsegAwIBAgIUcMgJSu/6RI7im9Pv5ESNuH8R+xQwDQYJKoZIhvcNAQEF
BQAwRjERMA8GA1UECgwIT3Jpb24gQUkxFTATBgNVBAsMDE9uZUxvZ2luIElkUDEa
MBgGA1UEAwwRT25lTG9naW4gQWNjb3VudCAwHhcNMjYwMTMxMDg0MzUyWhcNMzEw
MTMxMDg0MzUyWjBGMREwDwYDVQQKDAhPcmlvbiBBSTEVMBMGA1UECwwMT25lTG9n
aW4gSWRQMRowGAYDVQQDDBFPbmVMb2dpbiBBY2NvdW50IDCCASIwDQYJKoZIhvcN
AQEBBQADggEPADCCAQoCggEBAL2oBJyLy9udfpI8aYWBQIndbdlPZQ4uZrNjHK0w
wus6rbVImZtkStmSapL9jIfFxS5/d1aMlAvw25FzdSKPtIcmrqRRE4TTosmmEtOB
jXncfT2gHgN3Cl7aXgnRRId7AfRjz67Pw5FOhlcoRUfE8NxKQlqnrESBa4Qx1XFC
h7g8x0T86Pqfp9D69nX5SIyCX1aOeVU+BLf5EeuIiHvyr9LZPPO70Bj+QgzB9/4d
B/qet+7D4PEBXOjxvQl6z0voVCjTQgC4mmu0foeU+F8aybezhu6xzuxfX3AzDv30
KFXZru2WNv4acJU+/EboAGLGmJjGrfUPx/G5QFfPzr7TudUCAwEAAaOBxDCBwTAM
BgNVHRMBAf8EAjAAMB0GA1UdDgQWBBSQWdiyvxjQRndtCuqpIGyAuFtH1TCBgQYD
VR0jBHoweIAUkFnYsr8Y0EZ3bQrqqSBsgLhbR9WhSqRIMEYxETAPBgNVBAoMCE9y
aW9uIEFJMRUwEwYDVQQLDAxPbmVMb2dpbiBJZFAxGjAYBgNVBAMMEU9uZUxvZ2lu
IEFjY291bnQgghRwyAlK7/pEjuKb0+/kRI24fxH7FDAOBgNVHQ8BAf8EBAMCB4Aw
DQYJKoZIhvcNAQEFBQADggEBAGcBx+Z052mwglu6JT78YtL6XKb/XzVK3chmQVai
l9uR/4WY45h0VxGPCLnzEpwCzbPgRMXaS6vXEiI8ACjExrRvoOIsIttjWZZUH6RY
jvIh3likLNpwnwULbclvlm63VTFeaiwqHplmddcaJdCr1DmmGG72z++PAN6eM58j
gXexsyV+9lzr9Sz2Ybqb06c5XnFQvqYPt611WGER7Qc3W2tKvEL/fF5mRuByhBqF
fHQ29uukRHyp2VmiOPGL2gGD4bSC8fcJAAGZMn0DGZGh7G4FGF3GBE4/KVYrk8Q5
NDEGw918F7DnOyoGkf/jgPZyZhSNwCFxaLQnjpVvCogxz4s=
-----END CERTIFICATE-----',
  false,
  true,
  '00000000-0000-0000-0000-000000000004'  -- Member role
);

-- =============================================
-- 4. BRAND CONFIGURATIONS
-- =============================================

-- Acme Corp Demo Branding
INSERT INTO brand_configs (
  org_id,
  logo_url,
  favicon_url,
  primary_color,
  secondary_color,
  accent_color,
  email_from_name,
  email_from_address,
  custom_support_email,
  show_powered_by
) VALUES (
  '11111111-1111-1111-1111-111111111111',
  'https://placehold.co/200x60/3B82F6/FFF?text=Acme+Corp',
  'https://placehold.co/32x32/3B82F6/FFF?text=A',
  '#3B82F6',
  '#10B981',
  '#8B5CF6',
  'Acme Corp',
  'noreply@acme-demo.orion-ai.com',
  'support@acme-demo.com',
  true
);

-- TechStart Inc Branding
INSERT INTO brand_configs (
  org_id,
  logo_url,
  favicon_url,
  primary_color,
  secondary_color,
  accent_color,
  email_from_name,
  email_from_address,
  custom_support_email,
  show_powered_by
) VALUES (
  '22222222-2222-2222-2222-222222222222',
  'https://placehold.co/200x60/10B981/FFF?text=TechStart',
  'https://placehold.co/32x32/10B981/FFF?text=T',
  '#10B981',
  '#3B82F6',
  '#F59E0B',
  'TechStart',
  'noreply@techstart.orion-ai.com',
  'support@techstart.com',
  false
);

-- Global Enterprises Ltd Branding (Enterprise - Full customization)
INSERT INTO brand_configs (
  org_id,
  logo_url,
  favicon_url,
  primary_color,
  secondary_color,
  accent_color,
  email_from_name,
  email_from_address,
  custom_help_link,
  custom_support_email,
  show_powered_by
) VALUES (
  '33333333-3333-3333-3333-333333333333',
  'https://placehold.co/200x60/6366F1/FFF?text=Global+Ent',
  'https://placehold.co/32x32/6366F1/FFF?text=G',
  '#6366F1',
  '#EC4899',
  '#F59E0B',
  'Global Enterprises',
  'noreply@global-enterprises.com',
  'https://help.global-enterprises.com',
  'enterprise-support@global-enterprises.com',
  false
);

-- =============================================
-- 5. SAMPLE AUDIT EVENTS
-- =============================================

-- Sample audit events for demonstration (signatures will be auto-generated by trigger)
INSERT INTO audit_events (org_id, user_id, action, resource_type, resource_id, details, ip_address, user_agent, retention_policy, compliance_tags) VALUES
  (
    '11111111-1111-1111-1111-111111111111',
    NULL,  -- System event
    'create',
    'organization',
    '11111111-1111-1111-1111-111111111111',
    '{"name": "Acme Corp Demo", "tier": "free"}'::jsonb,
    '192.168.1.1',
    'Mozilla/5.0',
    'standard',
    ARRAY['gdpr']
  ),
  (
    '22222222-2222-2222-2222-222222222222',
    NULL,
    'create',
    'organization',
    '22222222-2222-2222-2222-222222222222',
    '{"name": "TechStart Inc", "tier": "professional"}'::jsonb,
    '192.168.1.2',
    'Mozilla/5.0',
    'extended',
    ARRAY['gdpr', 'soc2']
  ),
  (
    '33333333-3333-3333-3333-333333333333',
    NULL,
    'create',
    'organization',
    '33333333-3333-3333-3333-333333333333',
    '{"name": "Global Enterprises Ltd", "tier": "enterprise"}'::jsonb,
    '192.168.1.3',
    'Mozilla/5.0',
    'permanent',
    ARRAY['gdpr', 'soc2', 'hipaa']
  );

-- =============================================
-- 6. MONTHLY QUOTAS (Current month)
-- =============================================

INSERT INTO monthly_quotas (org_id, month, api_calls_used, data_volume_gb_used, quota_exceeded) VALUES
  ('11111111-1111-1111-1111-111111111111', DATE_TRUNC('month', CURRENT_DATE), 2547, 0.34, false),
  ('22222222-2222-2222-2222-222222222222', DATE_TRUNC('month', CURRENT_DATE), 45632, 4.21, false),
  ('33333333-3333-3333-3333-333333333333', DATE_TRUNC('month', CURRENT_DATE), 234567, 23.45, false);

-- =============================================
-- 7. HEALTH CHECKS (Sample recent checks)
-- =============================================

INSERT INTO health_checks (check_type, check_name, status, response_time_ms, metadata) VALUES
  ('api', 'Main API', 'healthy', 45, '{"version": "6.3.0"}'::jsonb),
  ('database', 'PostgreSQL', 'healthy', 12, '{"connections": 23, "max_connections": 100}'::jsonb),
  ('redis', 'Upstash Redis', 'healthy', 8, '{"memory_used_mb": 12.5}'::jsonb),
  ('external_service', 'Salesforce API', 'healthy', 234, '{"region": "us-west"}'::jsonb),
  ('external_service', 'QuickBooks API', 'healthy', 187, '{"region": "us-east"}'::jsonb);

-- =============================================
-- 8. ALERTS (Sample alerting rules)
-- =============================================

INSERT INTO alerts (org_id, alert_name, alert_type, metric_name, condition, severity, notification_channels, enabled) VALUES
  (
    '33333333-3333-3333-3333-333333333333',
    'High API Usage',
    'threshold',
    'api_calls_per_hour',
    '{"operator": ">", "value": 50000}'::jsonb,
    'warning',
    ARRAY['email', 'slack'],
    true
  ),
  (
    '22222222-2222-2222-2222-222222222222',
    'Connector Failure',
    'threshold',
    'failed_syncs',
    '{"operator": ">=", "value": 3}'::jsonb,
    'critical',
    ARRAY['email'],
    true
  ),
  (
    '33333333-3333-3333-3333-333333333333',
    'Quota Near Limit',
    'threshold',
    'quota_usage_percent',
    '{"operator": ">", "value": 90}'::jsonb,
    'warning',
    ARRAY['email', 'webhook'],
    true
  );

-- =============================================
-- 9. DOMAIN VERIFICATIONS
-- =============================================

-- Sample custom domain for Enterprise org
INSERT INTO domain_verifications (org_id, domain, verification_status, verification_token, verification_method, ssl_status) VALUES
  (
    '33333333-3333-3333-3333-333333333333',
    'integrations.global-enterprises.com',
    'pending',
    'verify_' || encode(gen_random_bytes(16), 'hex'),
    'dns',
    'pending'
  );

-- =============================================
-- SEED COMPLETE
-- =============================================

DO $$
BEGIN
  RAISE NOTICE '✅ Phase 6C Seed Data Complete!';
  RAISE NOTICE '   - 3 Organizations (Free, Professional, Enterprise)';
  RAISE NOTICE '   - 6 Teams';
  RAISE NOTICE '   - 4 SSO Configurations (Azure AD, Google, Auth0, OneLogin)';
  RAISE NOTICE '   - 3 Brand Configurations';
  RAISE NOTICE '   - Sample audit events, quotas, health checks';
  RAISE NOTICE '';
  RAISE NOTICE '📌 Test Organizations:';
  RAISE NOTICE '   1. acme-demo (Free tier)';
  RAISE NOTICE '   2. techstart (Professional tier)';
  RAISE NOTICE '   3. global-enterprises (Enterprise tier)';
END $$;
