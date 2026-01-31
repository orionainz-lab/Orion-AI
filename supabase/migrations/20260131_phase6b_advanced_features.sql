-- Phase 6B: Advanced Features Database Schema
-- Created: 2026-01-31

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- Connector Marketplace
-- ========================================

CREATE TABLE IF NOT EXISTS connector_marketplace (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  connector_id UUID NOT NULL REFERENCES connectors(id) ON DELETE CASCADE,
  publisher_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
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

CREATE INDEX idx_marketplace_category ON connector_marketplace(category);
CREATE INDEX idx_marketplace_verified ON connector_marketplace(is_verified);
CREATE INDEX idx_marketplace_rating ON connector_marketplace(rating DESC);

-- ========================================
-- User Installed Connectors
-- ========================================

CREATE TABLE IF NOT EXISTS user_installed_connectors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  marketplace_connector_id UUID NOT NULL REFERENCES connector_marketplace(id) ON DELETE CASCADE,
  installed_at TIMESTAMPTZ DEFAULT NOW(),
  last_used_at TIMESTAMPTZ,
  config JSONB DEFAULT '{}',
  is_active BOOLEAN DEFAULT true,
  UNIQUE(user_id, marketplace_connector_id)
);

CREATE INDEX idx_user_connectors_user ON user_installed_connectors(user_id);
CREATE INDEX idx_user_connectors_active ON user_installed_connectors(is_active);

-- ========================================
-- Custom Connectors (User-Generated)
-- ========================================

CREATE TABLE IF NOT EXISTS custom_connectors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
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

CREATE INDEX idx_custom_connectors_user ON custom_connectors(user_id);
CREATE INDEX idx_custom_connectors_deployed ON custom_connectors(deployed);

-- ========================================
-- Schema Mappings (LLM-Assisted)
-- ========================================

CREATE TABLE IF NOT EXISTS schema_mappings_llm (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  connector_id UUID NOT NULL REFERENCES connectors(id) ON DELETE CASCADE,
  source_field TEXT NOT NULL,
  target_field TEXT NOT NULL,
  transformation TEXT,
  confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
  llm_reasoning TEXT,
  user_approved BOOLEAN DEFAULT false,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_schema_mappings_connector ON schema_mappings_llm(connector_id);
CREATE INDEX idx_schema_mappings_approved ON schema_mappings_llm(user_approved);

-- ========================================
-- Sync Metrics (For Analytics)
-- ========================================

CREATE TABLE IF NOT EXISTS sync_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  config_id UUID NOT NULL REFERENCES connector_configs(id) ON DELETE CASCADE,
  sync_started_at TIMESTAMPTZ NOT NULL,
  sync_completed_at TIMESTAMPTZ,
  records_processed INTEGER DEFAULT 0,
  records_failed INTEGER DEFAULT 0,
  duration_ms INTEGER,
  error_message TEXT,
  error_code TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sync_metrics_config ON sync_metrics(config_id);
CREATE INDEX idx_sync_metrics_started ON sync_metrics(sync_started_at DESC);
CREATE INDEX idx_sync_metrics_completed ON sync_metrics(sync_completed_at DESC);

-- ========================================
-- Connector Health Status
-- ========================================

CREATE TABLE IF NOT EXISTS connector_health (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  config_id UUID NOT NULL REFERENCES connector_configs(id) ON DELETE CASCADE,
  status TEXT NOT NULL CHECK (status IN ('healthy', 'degraded', 'failed')),
  last_check_at TIMESTAMPTZ DEFAULT NOW(),
  consecutive_failures INTEGER DEFAULT 0,
  last_error TEXT,
  response_time_ms INTEGER,
  metadata JSONB DEFAULT '{}',
  UNIQUE(config_id)
);

CREATE INDEX idx_connector_health_status ON connector_health(status);
CREATE INDEX idx_connector_health_check ON connector_health(last_check_at DESC);

-- ========================================
-- Analytics Materialized View
-- ========================================

CREATE MATERIALIZED VIEW IF NOT EXISTS connector_analytics AS
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

-- Refresh function for materialized view
CREATE OR REPLACE FUNCTION refresh_connector_analytics()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY connector_analytics;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- Row Level Security (RLS)
-- ========================================

-- Enable RLS on new tables
ALTER TABLE connector_marketplace ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_installed_connectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE custom_connectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE schema_mappings_llm ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE connector_health ENABLE ROW LEVEL SECURITY;

-- Marketplace: Public read, admin write
CREATE POLICY "Marketplace public read" ON connector_marketplace
  FOR SELECT USING (true);

CREATE POLICY "Marketplace admin write" ON connector_marketplace
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM auth.users
      WHERE id = auth.uid()
      AND (metadata->>'role')::text = 'admin'
    )
  );

-- User installed connectors: Own records only
CREATE POLICY "User installed connectors select" ON user_installed_connectors
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "User installed connectors insert" ON user_installed_connectors
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "User installed connectors update" ON user_installed_connectors
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "User installed connectors delete" ON user_installed_connectors
  FOR DELETE USING (auth.uid() = user_id);

-- Custom connectors: Own records only
CREATE POLICY "Custom connectors select" ON custom_connectors
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Custom connectors insert" ON custom_connectors
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Custom connectors update" ON custom_connectors
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Custom connectors delete" ON custom_connectors
  FOR DELETE USING (auth.uid() = user_id);

-- Schema mappings: User can see their own or approved mappings
CREATE POLICY "Schema mappings select" ON schema_mappings_llm
  FOR SELECT USING (
    auth.uid() = user_id OR user_approved = true
  );

CREATE POLICY "Schema mappings insert" ON schema_mappings_llm
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Schema mappings update" ON schema_mappings_llm
  FOR UPDATE USING (auth.uid() = user_id);

-- Sync metrics: Own configs only
CREATE POLICY "Sync metrics select" ON sync_metrics
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM connector_configs
      WHERE id = sync_metrics.config_id
      AND user_id = auth.uid()
    )
  );

CREATE POLICY "Sync metrics insert" ON sync_metrics
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM connector_configs
      WHERE id = sync_metrics.config_id
      AND user_id = auth.uid()
    )
  );

-- Connector health: Own configs only
CREATE POLICY "Connector health select" ON connector_health
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM connector_configs
      WHERE id = connector_health.config_id
      AND user_id = auth.uid()
    )
  );

CREATE POLICY "Connector health upsert" ON connector_health
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM connector_configs
      WHERE id = connector_health.config_id
      AND user_id = auth.uid()
    )
  );

-- ========================================
-- Functions and Triggers
-- ========================================

-- Update marketplace install count
CREATE OR REPLACE FUNCTION increment_install_count()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE connector_marketplace
  SET install_count = install_count + 1
  WHERE id = NEW.marketplace_connector_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_increment_install_count
  AFTER INSERT ON user_installed_connectors
  FOR EACH ROW
  EXECUTE FUNCTION increment_install_count();

-- Update last_used_at on sync
CREATE OR REPLACE FUNCTION update_connector_last_used()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE connector_configs
  SET updated_at = NOW()
  WHERE id = NEW.config_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_last_used
  AFTER INSERT ON sync_metrics
  FOR EACH ROW
  EXECUTE FUNCTION update_connector_last_used();

-- Update connector health based on sync results
CREATE OR REPLACE FUNCTION update_connector_health()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO connector_health (config_id, status, last_check_at, consecutive_failures, last_error, response_time_ms)
  VALUES (
    NEW.config_id,
    CASE 
      WHEN NEW.error_message IS NOT NULL THEN 'failed'
      WHEN NEW.records_failed > NEW.records_processed * 0.1 THEN 'degraded'
      ELSE 'healthy'
    END,
    NEW.sync_completed_at,
    CASE WHEN NEW.error_message IS NOT NULL THEN 1 ELSE 0 END,
    NEW.error_message,
    NEW.duration_ms
  )
  ON CONFLICT (config_id) DO UPDATE SET
    status = CASE 
      WHEN NEW.error_message IS NOT NULL THEN 'failed'
      WHEN NEW.records_failed > NEW.records_processed * 0.1 THEN 'degraded'
      ELSE 'healthy'
    END,
    last_check_at = NEW.sync_completed_at,
    consecutive_failures = CASE 
      WHEN NEW.error_message IS NOT NULL THEN connector_health.consecutive_failures + 1
      ELSE 0
    END,
    last_error = NEW.error_message,
    response_time_ms = NEW.duration_ms;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_connector_health
  AFTER INSERT ON sync_metrics
  FOR EACH ROW
  EXECUTE FUNCTION update_connector_health();

-- ========================================
-- Sample Data (Optional)
-- ========================================

-- Insert sample marketplace connectors
INSERT INTO connector_marketplace (connector_id, publisher_id, name, description, category, pricing_model, is_verified, rating)
SELECT 
  c.id,
  c.user_id,
  c.name,
  'Official ' || c.name || ' connector',
  CASE 
    WHEN c.name IN ('salesforce', 'hubspot') THEN 'crm'
    WHEN c.name = 'quickbooks' THEN 'accounting'
    WHEN c.name = 'slack' THEN 'communication'
    ELSE 'custom'
  END,
  'free',
  true,
  5.0
FROM connectors c
WHERE c.name IN ('salesforce', 'quickbooks', 'slack')
ON CONFLICT DO NOTHING;

COMMENT ON TABLE connector_marketplace IS 'Public marketplace for connectors';
COMMENT ON TABLE user_installed_connectors IS 'User-installed marketplace connectors';
COMMENT ON TABLE custom_connectors IS 'User-generated custom connectors';
COMMENT ON TABLE schema_mappings_llm IS 'LLM-assisted field mappings';
COMMENT ON TABLE sync_metrics IS 'Sync performance metrics for analytics';
COMMENT ON TABLE connector_health IS 'Real-time connector health status';
COMMENT ON MATERIALIZED VIEW connector_analytics IS 'Aggregated analytics by connector and date';
