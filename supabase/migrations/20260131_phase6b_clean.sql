-- Phase 6B: Advanced Features Database Schema (Clean Install)
-- Created: 2026-01-31
-- Handles existing schema_mappings table

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing index if it conflicts
DROP INDEX IF EXISTS idx_schema_mappings_connector;

-- ========================================
-- Connector Marketplace
-- ========================================

CREATE TABLE IF NOT EXISTS connector_marketplace (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  connector_id UUID NOT NULL,
  publisher_id UUID NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL CHECK (category IN ('crm', 'accounting', 'communication', 'marketing', 'custom')),
  pricing_model TEXT CHECK (pricing_model IN ('free', 'paid', 'freemium')),
  install_count INTEGER DEFAULT 0,
  rating DECIMAL(2,1) CHECK (rating >= 0 AND rating <= 5),
  is_verified BOOLEAN DEFAULT false,
  icon_url TEXT,
  documentation_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_marketplace_category ON connector_marketplace(category);
CREATE INDEX IF NOT EXISTS idx_marketplace_verified ON connector_marketplace(is_verified);
CREATE INDEX IF NOT EXISTS idx_marketplace_rating ON connector_marketplace(rating DESC);

-- ========================================
-- User Installed Connectors
-- ========================================

CREATE TABLE IF NOT EXISTS user_installed_connectors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  marketplace_connector_id UUID NOT NULL REFERENCES connector_marketplace(id) ON DELETE CASCADE,
  installed_at TIMESTAMPTZ DEFAULT NOW(),
  last_used_at TIMESTAMPTZ,
  config JSONB DEFAULT '{}',
  is_active BOOLEAN DEFAULT true,
  UNIQUE(user_id, marketplace_connector_id)
);

CREATE INDEX IF NOT EXISTS idx_user_connectors_user ON user_installed_connectors(user_id);
CREATE INDEX IF NOT EXISTS idx_user_connectors_active ON user_installed_connectors(is_active);

-- ========================================
-- Custom Connectors (User-Generated)
-- ========================================

CREATE TABLE IF NOT EXISTS custom_connectors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  generated_code TEXT NOT NULL,
  field_mappings JSONB NOT NULL DEFAULT '{}',
  api_docs_url TEXT,
  auth_type TEXT NOT NULL CHECK (auth_type IN ('api_key', 'oauth2', 'basic', 'none')),
  sandbox_tested BOOLEAN DEFAULT false,
  deployed BOOLEAN DEFAULT false,
  test_results JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT custom_connector_name_user UNIQUE(user_id, name)
);

CREATE INDEX IF NOT EXISTS idx_custom_connectors_user ON custom_connectors(user_id);
CREATE INDEX IF NOT EXISTS idx_custom_connectors_deployed ON custom_connectors(deployed);

-- ========================================
-- Schema Mappings LLM (AI-Assisted)
-- Renamed to avoid conflict with existing schema_mappings
-- ========================================

CREATE TABLE IF NOT EXISTS schema_mappings_llm (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  connector_id UUID NOT NULL,
  source_field TEXT NOT NULL,
  target_field TEXT NOT NULL,
  transformation TEXT,
  confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
  llm_reasoning TEXT,
  user_approved BOOLEAN DEFAULT false,
  user_id UUID,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_schema_mappings_llm_connector ON schema_mappings_llm(connector_id);
CREATE INDEX IF NOT EXISTS idx_schema_mappings_llm_approved ON schema_mappings_llm(user_approved);

-- ========================================
-- Sync Metrics (For Analytics)
-- ========================================

CREATE TABLE IF NOT EXISTS sync_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  config_id UUID NOT NULL,
  sync_started_at TIMESTAMPTZ NOT NULL,
  sync_completed_at TIMESTAMPTZ,
  records_processed INTEGER DEFAULT 0,
  records_failed INTEGER DEFAULT 0,
  duration_ms INTEGER,
  error_message TEXT,
  error_code TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sync_metrics_config ON sync_metrics(config_id);
CREATE INDEX IF NOT EXISTS idx_sync_metrics_started ON sync_metrics(sync_started_at DESC);
CREATE INDEX IF NOT EXISTS idx_sync_metrics_completed ON sync_metrics(sync_completed_at DESC);

-- ========================================
-- Connector Health Status
-- ========================================

CREATE TABLE IF NOT EXISTS connector_health (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  config_id UUID NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('healthy', 'degraded', 'failed')),
  last_check_at TIMESTAMPTZ DEFAULT NOW(),
  consecutive_failures INTEGER DEFAULT 0,
  last_error TEXT,
  avg_response_time_ms INTEGER,
  error_details JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(config_id)
);

CREATE INDEX IF NOT EXISTS idx_connector_health_status ON connector_health(status);
CREATE INDEX IF NOT EXISTS idx_connector_health_check ON connector_health(last_check_at DESC);

-- ========================================
-- Analytics Materialized View
-- ========================================

DROP MATERIALIZED VIEW IF EXISTS connector_analytics CASCADE;

CREATE MATERIALIZED VIEW connector_analytics AS
SELECT 
  config_id,
  DATE(sync_started_at) as date,
  COUNT(*) as sync_count,
  SUM(records_processed) as total_records,
  SUM(records_failed) as total_failed,
  AVG(duration_ms) as avg_duration_ms,
  MIN(duration_ms) as min_duration_ms,
  MAX(duration_ms) as max_duration_ms,
  SUM(CASE WHEN error_message IS NOT NULL THEN 1 ELSE 0 END) as error_count,
  ROUND(100.0 * SUM(CASE WHEN error_message IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM sync_metrics
GROUP BY config_id, DATE(sync_started_at);

CREATE UNIQUE INDEX idx_connector_analytics_config_date ON connector_analytics(config_id, date DESC);

-- ========================================
-- Row Level Security (RLS)
-- ========================================

ALTER TABLE connector_marketplace ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_installed_connectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE custom_connectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE schema_mappings_llm ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE connector_health ENABLE ROW LEVEL SECURITY;

-- Marketplace: Public read
DROP POLICY IF EXISTS "Marketplace public read" ON connector_marketplace;
CREATE POLICY "Marketplace public read" ON connector_marketplace
  FOR SELECT USING (true);

-- User installed connectors: Own records only
DROP POLICY IF EXISTS "User installed connectors select" ON user_installed_connectors;
CREATE POLICY "User installed connectors select" ON user_installed_connectors
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "User installed connectors insert" ON user_installed_connectors;
CREATE POLICY "User installed connectors insert" ON user_installed_connectors
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Custom connectors: Own records only
DROP POLICY IF EXISTS "Custom connectors select" ON custom_connectors;
CREATE POLICY "Custom connectors select" ON custom_connectors
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Custom connectors insert" ON custom_connectors;
CREATE POLICY "Custom connectors insert" ON custom_connectors
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Schema mappings: Own or approved
DROP POLICY IF EXISTS "Schema mappings select" ON schema_mappings_llm;
CREATE POLICY "Schema mappings select" ON schema_mappings_llm
  FOR SELECT USING (auth.uid() = user_id OR user_approved = true);

-- Sync metrics: Public read for now (restrict later based on config ownership)
DROP POLICY IF EXISTS "Sync metrics select" ON sync_metrics;
CREATE POLICY "Sync metrics select" ON sync_metrics
  FOR SELECT USING (true);

-- Connector health: Public read for now
DROP POLICY IF EXISTS "Connector health select" ON connector_health;
CREATE POLICY "Connector health select" ON connector_health
  FOR SELECT USING (true);

COMMENT ON TABLE connector_marketplace IS 'Public marketplace for connectors';
COMMENT ON TABLE user_installed_connectors IS 'User-installed marketplace connectors';
COMMENT ON TABLE custom_connectors IS 'User-generated custom connectors';
COMMENT ON TABLE schema_mappings_llm IS 'LLM-assisted field mappings';
COMMENT ON TABLE sync_metrics IS 'Sync performance metrics for analytics';
COMMENT ON TABLE connector_health IS 'Real-time connector health status';
COMMENT ON MATERIALIZED VIEW connector_analytics IS 'Aggregated analytics by connector and date';
