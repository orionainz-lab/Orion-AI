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
  id,
  event_name,
  event_type,
  event_metadata,
  user_id,
  workflow_id,
  created_at
) VALUES 
(
  'test-pending-001',
  'code_generation_requested',
  'ai_event',
  '{"status": "pending", "description": "Generate authentication service", "language": "python"}'::jsonb,
  'test-user-001',
  'workflow-pending-001',
  NOW() - INTERVAL '2 hours'
),
(
  'test-pending-002',
  'code_review_requested',
  'ai_event',
  '{"status": "pending", "description": "Review API endpoints", "language": "typescript"}'::jsonb,
  'test-user-002',
  'workflow-pending-002',
  NOW() - INTERVAL '1 hour'
),
(
  'test-pending-003',
  'refactor_requested',
  'ai_event',
  '{"status": "pending", "description": "Optimize database queries", "language": "sql"}'::jsonb,
  'test-user-003',
  'workflow-pending-003',
  NOW() - INTERVAL '30 minutes'
);

-- Insert Approved Proposals
INSERT INTO process_events (
  id,
  event_name,
  event_type,
  event_metadata,
  user_id,
  workflow_id,
  created_at
) VALUES 
(
  'test-approved-001',
  'deployment_completed',
  'ai_event',
  '{"status": "approved", "description": "Deploy to production", "environment": "production"}'::jsonb,
  'test-user-004',
  'workflow-approved-001',
  NOW() - INTERVAL '3 hours'
),
(
  'test-approved-002',
  'test_suite_passed',
  'ai_event',
  '{"status": "approved", "description": "All unit tests passed", "coverage": "95%"}'::jsonb,
  'test-user-005',
  'workflow-approved-002',
  NOW() - INTERVAL '4 hours'
);

-- Insert Rejected Proposals
INSERT INTO process_events (
  id,
  event_name,
  event_type,
  event_metadata,
  user_id,
  workflow_id,
  created_at
) VALUES 
(
  'test-rejected-001',
  'code_quality_check_failed',
  'ai_event',
  '{"status": "rejected", "description": "Linting errors detected", "errors": 15}'::jsonb,
  'test-user-006',
  'workflow-rejected-001',
  NOW() - INTERVAL '5 hours'
),
(
  'test-rejected-002',
  'security_scan_failed',
  'ai_event',
  '{"status": "rejected", "description": "Security vulnerabilities found", "vulnerabilities": 3}'::jsonb,
  'test-user-007',
  'workflow-rejected-002',
  NOW() - INTERVAL '6 hours'
);

-- Insert Processing Proposals
INSERT INTO process_events (
  id,
  event_name,
  event_type,
  event_metadata,
  user_id,
  workflow_id,
  created_at
) VALUES 
(
  'test-processing-001',
  'ai_model_inference',
  'ai_event',
  '{"status": "processing", "description": "Running AI model", "progress": "50%"}'::jsonb,
  'test-user-008',
  'workflow-processing-001',
  NOW() - INTERVAL '10 minutes'
),
(
  'test-processing-002',
  'data_analysis',
  'ai_event',
  '{"status": "processing", "description": "Analyzing codebase", "progress": "75%"}'::jsonb,
  'test-user-009',
  'workflow-processing-002',
  NOW() - INTERVAL '5 minutes'
);

-- Verify insertion
SELECT 
  event_metadata->>'status' as status,
  COUNT(*) as count
FROM process_events
WHERE user_id LIKE 'test-user-%'
GROUP BY event_metadata->>'status'
ORDER BY status;

-- Show all test data
SELECT 
  id,
  event_name,
  event_metadata->>'status' as status,
  user_id,
  workflow_id,
  created_at
FROM process_events
WHERE user_id LIKE 'test-user-%'
ORDER BY created_at DESC;
