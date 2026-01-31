-- Phase 6B Analytics Seed Data
-- Created: 2026-01-31
-- Purpose: Generate sample analytics data for testing

-- Note: This requires connector_configs table from Phase 5
-- Adjust the queries based on your actual config IDs

-- Create sample sync metrics (last 7 days)
INSERT INTO sync_metrics (
  config_id,
  sync_started_at,
  sync_completed_at,
  records_processed,
  records_failed,
  duration_ms,
  error_message
)
SELECT 
  (SELECT id FROM connector_configs ORDER BY created_at LIMIT 1 OFFSET floor(random() * (SELECT COUNT(*) FROM connector_configs))::int),
  NOW() - (random() * interval '7 days'),
  NOW() - (random() * interval '6 days' + interval '1 hour'),
  floor(random() * 1000 + 100)::int,
  floor(random() * 10)::int,
  floor(random() * 5000 + 1000)::int,
  CASE WHEN random() < 0.9 THEN NULL ELSE 'Connection timeout' END
FROM generate_series(1, 50);

-- Create sample connector health status
INSERT INTO connector_health (
  config_id,
  status,
  last_check_at,
  consecutive_failures,
  avg_response_time_ms,
  error_details
)
SELECT 
  id,
  CASE 
    WHEN random() < 0.85 THEN 'healthy'
    WHEN random() < 0.95 THEN 'degraded'
    ELSE 'failed'
  END,
  NOW() - (random() * interval '1 hour'),
  CASE WHEN random() < 0.9 THEN 0 ELSE floor(random() * 3)::int END,
  floor(random() * 500 + 100)::int,
  CASE WHEN random() < 0.9 THEN NULL 
       ELSE '{"error": "Rate limit exceeded", "timestamp": "2026-01-31T00:00:00Z"}'::jsonb 
  END
FROM connector_configs
ON CONFLICT (config_id) DO UPDATE SET
  status = EXCLUDED.status,
  last_check_at = EXCLUDED.last_check_at,
  consecutive_failures = EXCLUDED.consecutive_failures,
  avg_response_time_ms = EXCLUDED.avg_response_time_ms;

-- Refresh materialized view
REFRESH MATERIALIZED VIEW connector_analytics;

-- Verify data
SELECT 
  status, 
  COUNT(*) as count,
  AVG(avg_response_time_ms) as avg_response_time
FROM connector_health 
GROUP BY status;

SELECT 
  COUNT(*) as total_syncs,
  SUM(records_processed) as total_records,
  AVG(duration_ms) as avg_duration,
  COUNT(CASE WHEN error_message IS NOT NULL THEN 1 END) as failed_syncs
FROM sync_metrics;
