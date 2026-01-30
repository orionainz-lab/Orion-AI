#!/usr/bin/env python3
"""
VAN-QA-1: Supabase pgvector Extension Availability Test

Validates:
- pgvector extension can be enabled on Supabase
- Vector type can be created
- Basic vector operations work

Risk: HIGH - Blocks entire Phase 3 if fails
"""

import os
import sys
from typing import Optional

def test_pgvector_availability():
    """Test if pgvector extension is available."""
    print("=" * 60)
    print("VAN-QA-1: pgvector Extension Availability")
    print("=" * 60)
    
    # Check if Supabase credentials are available
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("\n⚠️  WARNING: Supabase credentials not found in environment")
        print("   Please set SUPABASE_URL and SUPABASE_KEY")
        print("   Skipping pgvector validation (will need manual verification)")
        return False
    
    try:
        from supabase import create_client, Client
        print("\n✅ Supabase Python client installed")
    except ImportError:
        print("\n❌ FAILED: supabase-py not installed")
        print("   Run: pip install supabase")
        return False
    
    try:
        # Connect to Supabase
        print(f"\n📡 Connecting to Supabase: {supabase_url[:30]}...")
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Try to create extension (may require admin privileges)
        print("\n🔧 Attempting to enable pgvector extension...")
        try:
            result = supabase.rpc('exec_sql', {
                'sql': 'CREATE EXTENSION IF NOT EXISTS vector'
            }).execute()
            print("✅ pgvector extension enabled (or already exists)")
        except Exception as e:
            # Extension might already exist or require SQL editor
            print(f"⚠️  Could not enable via RPC: {e}")
            print("   Please enable manually in Supabase SQL Editor:")
            print("   CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Test vector type creation
        print("\n🧪 Testing vector type operations...")
        test_sql = """
        -- Create test table with vector column
        DROP TABLE IF EXISTS _test_pgvector;
        CREATE TABLE _test_pgvector (
            id SERIAL PRIMARY KEY,
            embedding vector(3)
        );
        
        -- Insert test vector
        INSERT INTO _test_pgvector (embedding) 
        VALUES ('[1,2,3]');
        
        -- Query with cosine similarity
        SELECT embedding <=> '[1,2,3]' as distance 
        FROM _test_pgvector;
        
        -- Cleanup
        DROP TABLE _test_pgvector;
        """
        
        # Note: Direct SQL execution requires admin or SQL editor
        print("⚠️  Full vector operations test requires SQL editor access")
        print("   Please run the following in Supabase SQL Editor:\n")
        print(test_sql)
        
        print("\n" + "=" * 60)
        print("VAN-QA-1 STATUS: MANUAL VERIFICATION REQUIRED")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Go to Supabase SQL Editor")
        print("2. Run: CREATE EXTENSION IF NOT EXISTS vector;")
        print("3. Run the test SQL above")
        print("4. If all commands succeed → pgvector is available ✅")
        print("5. If 'extension does not exist' → contact Supabase support ❌")
        
        return None  # Manual verification needed
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        return False

def test_vector_dimensions():
    """Test that 1536-dimensional vectors work (ADR-011)."""
    print("\n" + "=" * 60)
    print("Testing 1536-Dimensional Vectors (OpenAI standard)")
    print("=" * 60)
    
    print("\nNote: This requires pgvector to be enabled first")
    print("SQL to test in Supabase SQL Editor:\n")
    
    test_sql = """
    -- Create table with 1536d vectors (OpenAI text-embedding-3-small)
    CREATE TABLE _test_embeddings (
        id SERIAL PRIMARY KEY,
        embedding vector(1536)
    );
    
    -- Insert sample embedding (zeros for test)
    INSERT INTO _test_embeddings (embedding)
    VALUES (array_fill(0, ARRAY[1536])::vector);
    
    -- Verify dimension
    SELECT vector_dims(embedding) as dimensions 
    FROM _test_embeddings;
    
    -- Expected output: 1536
    
    -- Cleanup
    DROP TABLE _test_embeddings;
    """
    
    print(test_sql)
    print("\n✅ If this runs without errors, 1536d vectors are supported")

def main():
    """Run pgvector validation tests."""
    print("\n" + "=" * 60)
    print("PHASE 3 VAN QA - TEST 1: pgvector Availability")
    print("=" * 60)
    
    result = test_pgvector_availability()
    test_vector_dimensions()
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if result is True:
        print("✅ PASS: pgvector is available and working")
        return 0
    elif result is False:
        print("❌ FAIL: pgvector validation failed")
        print("   Phase 3 is BLOCKED until this is resolved")
        print("   Fallback: Consider external vector DB (Pinecone, Weaviate)")
        return 1
    else:
        print("⚠️  MANUAL: pgvector validation requires manual verification")
        print("   Follow steps above to verify in Supabase SQL Editor")
        return 2

if __name__ == '__main__':
    sys.exit(main())
