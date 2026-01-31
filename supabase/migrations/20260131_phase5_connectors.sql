-- ================================================================
-- Phase 5: Connector Framework Database Schema
-- ================================================================
-- Description: Tables for N-to-N connector registry
-- Created: 2026-01-31
-- ================================================================

-- Connector definitions (system-level)
CREATE TABLE IF NOT EXISTS connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK (type IN ('inbound', 'outbound', 'bidirectional')),
    description TEXT,
    version TEXT NOT NULL DEFAULT '1.0.0',
    schema_version TEXT NOT NULL DEFAULT '1.0.0',
    capabilities JSONB DEFAULT '[]'::jsonb,
    status TEXT NOT NULL DEFAULT 'active' 
        CHECK (status IN ('active', 'deprecated', 'disabled')),
    icon_url TEXT,
    documentation_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- User-specific connector configurations
CREATE TABLE IF NOT EXISTS connector_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_id UUID NOT NULL REFERENCES connectors(id),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    name TEXT NOT NULL,
    config JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMPTZ,
    sync_status TEXT DEFAULT 'idle' 
        CHECK (sync_status IN ('idle', 'syncing', 'error', 'success')),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(connector_id, user_id, name)
);

-- Encrypted credentials
CREATE TABLE IF NOT EXISTS connector_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID NOT NULL REFERENCES connector_configs(id) 
        ON DELETE CASCADE,
    credential_type TEXT NOT NULL 
        CHECK (credential_type IN (
            'api_key', 'oauth_token', 'basic_auth', 'bearer_token'
        )),
    encrypted_value TEXT NOT NULL,
    expires_at TIMESTAMPTZ,
    refresh_token_encrypted TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Schema mappings (LLM-generated)
CREATE TABLE IF NOT EXISTS schema_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_id UUID NOT NULL REFERENCES connectors(id),
    source_schema TEXT NOT NULL,
    target_schema TEXT NOT NULL,
    mapping_rules JSONB NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT true,
    confidence_score FLOAT,
    human_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Webhook configurations
CREATE TABLE IF NOT EXISTS webhook_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_id UUID NOT NULL REFERENCES connectors(id),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    endpoint_path TEXT NOT NULL,
    secret_key TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    event_types JSONB DEFAULT '["*"]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, endpoint_path)
);

-- ================================================================
-- Indexes for Performance
-- ================================================================

CREATE INDEX IF NOT EXISTS idx_connector_configs_user 
    ON connector_configs(user_id);

CREATE INDEX IF NOT EXISTS idx_connector_configs_connector 
    ON connector_configs(connector_id);

CREATE INDEX IF NOT EXISTS idx_connector_configs_active 
    ON connector_configs(is_active) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_schema_mappings_connector 
    ON schema_mappings(connector_id);

CREATE INDEX IF NOT EXISTS idx_webhook_configs_user 
    ON webhook_configs(user_id);

CREATE INDEX IF NOT EXISTS idx_webhook_configs_path 
    ON webhook_configs(endpoint_path);

-- ================================================================
-- Row Level Security Policies
-- ================================================================

-- Enable RLS
ALTER TABLE connector_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE connector_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_configs ENABLE ROW LEVEL SECURITY;

-- connector_configs: Users see only their own
CREATE POLICY "Users can view own connector configs"
    ON connector_configs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own connector configs"
    ON connector_configs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own connector configs"
    ON connector_configs FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own connector configs"
    ON connector_configs FOR DELETE
    USING (auth.uid() = user_id);

-- connector_credentials: Access via config ownership
CREATE POLICY "Users can view own credentials"
    ON connector_credentials FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM connector_configs
            WHERE connector_configs.id = connector_credentials.config_id
            AND connector_configs.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own credentials"
    ON connector_credentials FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM connector_configs
            WHERE connector_configs.id = connector_credentials.config_id
            AND connector_configs.user_id = auth.uid()
        )
    );

-- webhook_configs: Users manage own webhooks
CREATE POLICY "Users can manage own webhooks"
    ON webhook_configs FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ================================================================
-- Seed Data: Stripe Connector
-- ================================================================

INSERT INTO connectors (
    name, type, description, version,
    capabilities, status, documentation_url
) VALUES (
    'stripe',
    'bidirectional',
    'Stripe payment processing and customer management',
    '1.0.0',
    '["read", "write", "webhook"]'::jsonb,
    'active',
    'https://stripe.com/docs/api'
) ON CONFLICT (name) DO NOTHING;

-- ================================================================
-- Comments for Documentation
-- ================================================================

COMMENT ON TABLE connectors IS 
    'System-level connector definitions (Stripe, HubSpot, etc.)';

COMMENT ON TABLE connector_configs IS 
    'User-specific connector configurations and settings';

COMMENT ON TABLE connector_credentials IS 
    'Encrypted API keys and OAuth tokens';

COMMENT ON TABLE schema_mappings IS 
    'LLM-generated field mappings between systems';

COMMENT ON TABLE webhook_configs IS 
    'Inbound webhook endpoint configurations';
