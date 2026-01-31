-- ================================================================
-- Test Data Seeding Script for Phase 4.2/4.3 Testing
-- ================================================================
-- Purpose: Create test proposals for manual testing
-- Usage: Run this in Supabase SQL Editor or via psql
-- ================================================================

-- Clear existing test data (optional)
-- DELETE FROM process_events WHERE user_id LIKE 'test-user-%';

-- Insert Pending Proposals (for Approve/Reject testing)
INSERT INTO process_events (
  event_name,
  event_type,
  status,
  metadata,
  user_id,
  workflow_id,
  event_timestamp
) VALUES 
(
  'code_generation_requested',
  'ai_event',
  'pending',
  '{"description": "Generate authentication service", "language": "python", "priority": "high"}'::jsonb,
  'test-user-001',
  'workflow-pending-001',
  NOW() - INTERVAL '2 hours'
),
(
  'code_review_requested',
  'ai_event',
  'pending',
  '{"description": "Review API endpoints", "language": "typescript", "files": 15}'::jsonb,
  'test-user-002',
  'workflow-pending-002',
  NOW() - INTERVAL '1 hour'
),
(
  'refactor_requested',
  'ai_event',
  'pending',
  '{"description": "Optimize database queries", "language": "sql", "tables": 5}'::jsonb,
  'test-user-003',
  'workflow-pending-003',
  NOW() - INTERVAL '30 minutes'
);

-- Insert Approved Proposals
INSERT INTO process_events (
  event_name,
  event_type,
  status,
  metadata,
  user_id,
  workflow_id,
  event_timestamp
) VALUES 
(
  'deployment_completed',
  'ai_event',
  'approved',
  '{"description": "Deploy to production", "environment": "production", "version": "1.2.0"}'::jsonb,
  'test-user-004',
  'workflow-approved-001',
  NOW() - INTERVAL '3 hours'
),
(
  'test_suite_passed',
  'ai_event',
  'approved',
  '{"description": "All unit tests passed", "coverage": "95%", "tests": 142}'::jsonb,
  'test-user-005',
  'workflow-approved-002',
  NOW() - INTERVAL '4 hours'
);

-- Insert Rejected Proposals
INSERT INTO process_events (
  event_name,
  event_type,
  status,
  metadata,
  user_id,
  workflow_id,
  event_timestamp
) VALUES 
(
  'code_quality_check_failed',
  'ai_event',
  'rejected',
  '{"description": "Linting errors detected", "errors": 15, "severity": "high"}'::jsonb,
  'test-user-006',
  'workflow-rejected-001',
  NOW() - INTERVAL '5 hours'
),
(
  'security_scan_failed',
  'ai_event',
  'rejected',
  '{"description": "Security vulnerabilities found", "vulnerabilities": 3, "critical": 1}'::jsonb,
  'test-user-007',
  'workflow-rejected-002',
  NOW() - INTERVAL '6 hours'
);

-- Insert Processing Proposals
INSERT INTO process_events (
  event_name,
  event_type,
  status,
  metadata,
  user_id,
  workflow_id,
  event_timestamp
) VALUES 
(
  'ai_model_inference',
  'ai_event',
  'processing',
  '{"description": "Running AI model", "progress": "50%", "model": "claude-4-sonnet"}'::jsonb,
  'test-user-008',
  'workflow-processing-001',
  NOW() - INTERVAL '10 minutes'
),
(
  'data_analysis',
  'ai_event',
  'processing',
  '{"description": "Analyzing codebase", "progress": "75%", "files_analyzed": 450}'::jsonb,
  'test-user-009',
  'workflow-processing-002',
  NOW() - INTERVAL '5 minutes'
);

-- Verify insertion
SELECT 
  status,
  COUNT(*) as count
FROM process_events
WHERE user_id SIMILAR TO 'test-user-%'
GROUP BY status
ORDER BY status;

-- Show all test data
SELECT 
  id,
  event_name,
  status,
  user_id,
  workflow_id,
  metadata->>'description' as description,
  event_timestamp
FROM process_events
WHERE user_id SIMILAR TO 'test-user-%'
ORDER BY event_timestamp DESC;
