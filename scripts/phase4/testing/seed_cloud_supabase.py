#!/usr/bin/env python3
"""
Seed Test Data to Cloud Supabase
Purpose: Insert test proposals for Phase 4.2/4.3 testing
"""

import os
from datetime import datetime, timedelta
from supabase import create_client, Client

# Configuration from frontend/.env.local
SUPABASE_URL = "https://bdvebjnxpsdhinpgvkgo.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJkdmViam54cHNkaGlucGd2a2dvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzY2NTMyMzQsImV4cCI6MjA1MjIyOTIzNH0.z6LUJ5Uo7XlMEU81xFPIPE0z2O7XxXtIGtU3I"

print("=" * 70)
print("SEEDING TEST DATA TO SUPABASE")
print("=" * 70)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
print(f"\n[INFO] Connected to Supabase: {SUPABASE_URL}")

# Test proposals data
test_proposals = [
    {
        'id': 'test-pending-001',
        'event_name': 'code_generation_requested',
        'event_type': 'ai_event',
        'event_metadata': {'status': 'pending', 'description': 'Generate authentication service', 'language': 'python'},
        'user_id': 'test-user-001',
        'workflow_id': 'workflow-pending-001',
    },
    {
        'id': 'test-pending-002',
        'event_name': 'code_review_requested',
        'event_type': 'ai_event',
        'event_metadata': {'status': 'pending', 'description': 'Review API endpoints', 'language': 'typescript'},
        'user_id': 'test-user-002',
        'workflow_id': 'workflow-pending-002',
    },
    {
        'id': 'test-pending-003',
        'event_name': 'refactor_requested',
        'event_type': 'ai_event',
        'event_metadata': {'status': 'pending', 'description': 'Optimize database queries', 'language': 'sql'},
        'user_id': 'test-user-003',
        'workflow_id': 'workflow-pending-003',
    },
    {
        'id': 'test-approved-001',
        'event_name': 'deployment_completed',
        'event_type': 'ai_event',
        'event_metadata': {'status': 'approved', 'description': 'Deploy to production', 'environment': 'production'},
        'user_id': 'test-user-004',
        'workflow_id': 'workflow-approved-001',
    },
    {
        'id': 'test-approved-002',
        'event_name': 'test_suite_passed',
        'event_type': 'ai_event',
        'event_metadata': {'status': 'approved', 'description': 'All unit tests passed', 'coverage': '95%'},
        'user_id': 'test-user-005',
        'workflow_id': 'workflow-approved-002',
    },
    {
        'id': 'test-rejected-001',
        'event_name': 'code_quality_check_failed',
        'event_type': 'ai_event',
        'event_metadata': {'status': 'rejected', 'description': 'Linting errors detected', 'errors': 15},
        'user_id': 'test-user-006',
        'workflow_id': 'workflow-rejected-001',
    },
    {
        'id': 'test-rejected-002',
        'event_name': 'security_scan_failed',
        'event_type': 'ai_event',
        'event_metadata': {'status': 'rejected', 'description': 'Security vulnerabilities found', 'vulnerabilities': 3},
        'user_id': 'test-user-007',
        'workflow_id': 'workflow-rejected-002',
    },
    {
        'id': 'test-processing-001',
        'event_name': 'ai_model_inference',
        'event_type': 'ai_event',
        'event_metadata': {'status': 'processing', 'description': 'Running AI model', 'progress': '50%'},
        'user_id': 'test-user-008',
        'workflow_id': 'workflow-processing-001',
    },
]

print(f"\n[INFO] Inserting {len(test_proposals)} test proposals...")

inserted_count = 0
failed_count = 0

for proposal in test_proposals:
    try:
        result = supabase.table('process_events').upsert(proposal).execute()
        print(f"[SUCCESS] Inserted: {proposal['id']} ({proposal['event_metadata']['status']})")
        inserted_count += 1
    except Exception as e:
        print(f"[ERROR] Failed to insert {proposal['id']}: {str(e)}")
        failed_count += 1

print(f"\n[SUMMARY] Inserted: {inserted_count}, Failed: {failed_count}")

# Query to verify
print("\n[VERIFY] Querying test proposals...")
try:
    result = supabase.table('process_events') \
        .select('id, event_name, event_metadata') \
        .like('user_id', 'test-user-%') \
        .execute()
    
    print(f"[SUCCESS] Found {len(result.data)} test proposals")
    
    # Count by status
    status_counts = {}
    for item in result.data:
        status = item.get('event_metadata', {}).get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\n[STATUS BREAKDOWN]")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    
except Exception as e:
    print(f"[ERROR] Failed to verify: {str(e)}")

print("\n" + "=" * 70)
print("TEST DATA SEEDING COMPLETE")
print("=" * 70)
print("\n[NEXT STEP] Open Matrix Grid to see the data:")
print("  http://localhost:3000/matrix")
print("\n[NEXT STEP] Open Dashboard to see stats:")
print("  http://localhost:3000")
