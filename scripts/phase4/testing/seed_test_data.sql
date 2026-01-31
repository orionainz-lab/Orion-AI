-- ================================================================
-- Test Data Seeding Script for Phase 4.2/4.3 Testing
-- ================================================================
-- Purpose: Create test proposals for manual testing
-- Usage: Run via Supabase MCP or SQL Editor
-- Status: ✅ EXECUTED on 2026-01-31 (9 records seeded)
-- ================================================================

-- NOTE: This file has been updated to match actual database constraints:
-- - status values: 'started', 'completed', 'failed', 'cancelled'
-- - event_type values: 'code_generate', 'code_verify', 'rag_query', 'system_event', etc.
-- - user_id is nullable UUID (test_user stored in metadata instead)

-- Clear existing test data (optional)
-- DELETE FROM process_events WHERE metadata->>'test_user' LIKE 'test-user-%';

-- Insert test proposals with correct status values and event types
INSERT INTO process_events (
  event_name,
  event_type,
  status,
  metadata,
  workflow_id,
  event_timestamp
) VALUES 
-- Pending/Started Proposals (for Approve/Reject testing)
(
  'code_generation_requested',
  'code_generate',
  'started',
  '{"description": "Generate authentication service", "language": "python", "priority": "high", "test_user": "test-user-001"}'::jsonb,
  'workflow-pending-001',
  NOW() - INTERVAL '2 hours'
),
(
  'code_review_requested',
  'code_verify',
  'started',
  '{"description": "Review API endpoints", "language": "typescript", "files": 15, "test_user": "test-user-002"}'::jsonb,
  'workflow-pending-002',
  NOW() - INTERVAL '1 hour'
),
(
  'refactor_requested',
  'code_generate',
  'started',
  '{"description": "Optimize database queries", "language": "sql", "tables": 5, "test_user": "test-user-003"}'::jsonb,
  'workflow-pending-003',
  NOW() - INTERVAL '30 minutes'
),
-- Completed Proposals
(
  'deployment_completed',
  'system_event',
  'completed',
  '{"description": "Deploy to production", "environment": "production", "version": "1.2.0", "test_user": "test-user-004"}'::jsonb,
  'workflow-approved-001',
  NOW() - INTERVAL '3 hours'
),
(
  'test_suite_passed',
  'code_verify',
  'completed',
  '{"description": "All unit tests passed", "coverage": "95%", "tests": 142, "test_user": "test-user-005"}'::jsonb,
  'workflow-approved-002',
  NOW() - INTERVAL '4 hours'
),
-- Failed Proposals
(
  'code_quality_check_failed',
  'code_verify',
  'failed',
  '{"description": "Linting errors detected", "errors": 15, "severity": "high", "test_user": "test-user-006"}'::jsonb,
  'workflow-rejected-001',
  NOW() - INTERVAL '5 hours'
),
(
  'security_scan_failed',
  'code_verify',
  'failed',
  '{"description": "Security vulnerabilities found", "vulnerabilities": 3, "critical": 1, "test_user": "test-user-007"}'::jsonb,
  'workflow-rejected-002',
  NOW() - INTERVAL '6 hours'
),
-- In-Progress/Started Proposals
(
  'ai_model_inference',
  'code_generate',
  'started',
  '{"description": "Running AI model", "progress": "50%", "model": "claude-4-sonnet", "test_user": "test-user-008"}'::jsonb,
  'workflow-processing-001',
  NOW() - INTERVAL '10 minutes'
),
(
  'data_analysis',
  'rag_query',
  'started',
  '{"description": "Analyzing codebase", "progress": "75%", "files_analyzed": 450, "test_user": "test-user-009"}'::jsonb,
  'workflow-processing-002',
  NOW() - INTERVAL '5 minutes'
);

-- Verify insertion
SELECT 
  status,
  COUNT(*) as count
FROM process_events
WHERE metadata->>'test_user' LIKE 'test-user-%'
GROUP BY status
ORDER BY status;

-- Show all test data
SELECT 
  id,
  event_name,
  event_type,
  status,
  workflow_id,
  metadata->>'description' as description,
  metadata->>'test_user' as test_user,
  event_timestamp
FROM process_events
WHERE metadata->>'test_user' LIKE 'test-user-%'
ORDER BY event_timestamp DESC;
