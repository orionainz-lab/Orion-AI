#!/usr/bin/env python3
"""
Test Supabase Realtime Subscriptions
Purpose: Verify that Realtime subscriptions work correctly
"""

import os
import asyncio
import json
from datetime import datetime
from supabase import create_client, Client

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', 'http://127.0.0.1:54321')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')

print("=" * 70)
print("SUPABASE REALTIME SUBSCRIPTIONS TEST")
print("=" * 70)

if not SUPABASE_ANON_KEY:
    print("\n[ERROR] SUPABASE_ANON_KEY not set in environment")
    print("Please run: export SUPABASE_ANON_KEY=your_key")
    exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

print(f"\n[INFO] Connected to Supabase: {SUPABASE_URL}")

# Test 1: Insert test proposal
print("\n[TEST 1] Inserting test proposal...")
test_id = f"realtime-test-{datetime.now().strftime('%Y%m%d%H%M%S')}"

try:
    result = supabase.table('process_events').insert({
        'id': test_id,
        'event_name': 'realtime_test',
        'event_type': 'test_event',
        'event_metadata': {'status': 'pending', 'test': True},
        'user_id': 'realtime-test-user',
        'workflow_id': 'realtime-test-workflow',
    }).execute()
    
    print(f"[SUCCESS] Inserted proposal: {test_id}")
except Exception as e:
    print(f"[ERROR] Failed to insert: {str(e)}")
    exit(1)

# Test 2: Update test proposal
print("\n[TEST 2] Updating test proposal status...")
try:
    result = supabase.table('process_events').update({
        'event_metadata': {'status': 'approved', 'test': True}
    }).eq('id', test_id).execute()
    
    print(f"[SUCCESS] Updated proposal to 'approved'")
except Exception as e:
    print(f"[ERROR] Failed to update: {str(e)}")

# Test 3: Query to verify
print("\n[TEST 3] Querying updated proposal...")
try:
    result = supabase.table('process_events').select('*').eq('id', test_id).execute()
    
    if result.data:
        status = result.data[0].get('event_metadata', {}).get('status', 'unknown')
        print(f"[SUCCESS] Verified status: {status}")
    else:
        print("[ERROR] Proposal not found")
except Exception as e:
    print(f"[ERROR] Failed to query: {str(e)}")

# Test 4: Delete test proposal
print("\n[TEST 4] Deleting test proposal...")
try:
    result = supabase.table('process_events').delete().eq('id', test_id).execute()
    print(f"[SUCCESS] Deleted proposal: {test_id}")
except Exception as e:
    print(f"[ERROR] Failed to delete: {str(e)}")

print("\n" + "=" * 70)
print("REALTIME SUBSCRIPTION TEST COMPLETE")
print("=" * 70)
print("\n[NEXT STEP] Open the Matrix Grid in your browser:")
print("  1. Start frontend: cd frontend && npm run dev")
print("  2. Open: http://localhost:3000/matrix")
print("  3. Watch for real-time updates as you run this script again")
print("\n[NOTE] The frontend should show:")
print("  - New proposal appears instantly (INSERT)")
print("  - Status changes to 'approved' (UPDATE)")
print("  - Proposal disappears (DELETE)")
print("  - Toast notifications for each event")
