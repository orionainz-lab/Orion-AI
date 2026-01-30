#!/usr/bin/env python3
"""
VAN-QA-2: HNSW Index Performance Test

Validates:
- HNSW index creation succeeds
- Query time <100ms for top-10 results
- Recall rate >90% vs brute-force

Risk: MEDIUM - Affects RAG query responsiveness
"""

import os
import sys
import time
import random
from typing import List

def generate_random_vector(dimensions: int = 1536) -> List[float]:
    """Generate random normalized vector."""
    vector = [random.gauss(0, 1) for _ in range(dimensions)]
    # Normalize
    magnitude = sum(x**2 for x in vector) ** 0.5
    return [x / magnitude for x in vector]

def test_hnsw_performance():
    """Test HNSW index performance (requires pgvector)."""
    print("=" * 60)
    print("VAN-QA-2: HNSW Index Performance")
    print("=" * 60)
    
    print("\n📋 Performance Test Scenario:")
    print("   1. Create test table with 1000 vectors (1536d)")
    print("   2. Build HNSW index")
    print("   3. Query for top-10 similar vectors")
    print("   4. Measure query time (target <100ms)")
    
    print("\n🧪 SQL to run in Supabase SQL Editor:\n")
    
    test_sql = """
-- Step 1: Create test table
DROP TABLE IF EXISTS _test_hnsw_performance;
CREATE TABLE _test_hnsw_performance (
    id SERIAL PRIMARY KEY,
    embedding vector(1536)
);

-- Step 2: Insert 1000 random vectors
-- (Use generate_series for bulk insert)
INSERT INTO _test_hnsw_performance (embedding)
SELECT array_fill(random(), ARRAY[1536])::vector
FROM generate_series(1, 1000);

-- Step 3: Create HNSW index
CREATE INDEX idx_hnsw_test 
ON _test_hnsw_performance 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- Step 4: Query performance test (with EXPLAIN ANALYZE)
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, embedding <=> '[...]'::vector AS distance
FROM _test_hnsw_performance
ORDER BY embedding <=> '[...]'::vector
LIMIT 10;

-- Look for "Execution Time" in output
-- Target: <100ms

-- Step 5: Compare with sequential scan (no index)
DROP INDEX idx_hnsw_test;

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, embedding <=> '[...]'::vector AS distance
FROM _test_hnsw_performance
ORDER BY embedding <=> '[...]'::vector
LIMIT 10;

-- Sequential scan will be much slower (200-500ms for 1000 vectors)

-- Cleanup
DROP TABLE _test_hnsw_performance;
"""
    
    print(test_sql)
    
    print("\n" + "=" * 60)
    print("VAN-QA-2 STATUS: MANUAL VERIFICATION REQUIRED")
    print("=" * 60)
    print("\nExpected Results:")
    print("   HNSW Index Query: <100ms (target <50ms)")
    print("   Sequential Scan: 200-500ms (for comparison)")
    print("   Speedup: 2-10x faster with HNSW")
    
    print("\n✅ If HNSW query <100ms → Performance validated")
    print("⚠️  If HNSW query >100ms → May need tuning or larger dataset")

def test_recall_accuracy():
    """Test HNSW recall vs brute-force."""
    print("\n" + "=" * 60)
    print("HNSW Recall Accuracy Test")
    print("=" * 60)
    
    print("\n📋 Recall measures how many true neighbors HNSW finds")
    print("   Target: >90% recall (>95% ideal)")
    
    print("\n🧪 SQL to test recall:\n")
    
    recall_sql = """
-- Create test table with 1000 vectors
DROP TABLE IF EXISTS _test_hnsw_recall;
CREATE TABLE _test_hnsw_recall (
    id SERIAL PRIMARY KEY,
    embedding vector(1536)
);

INSERT INTO _test_hnsw_recall (embedding)
SELECT array_fill(random(), ARRAY[1536])::vector
FROM generate_series(1, 1000);

-- Query 1: Brute-force (no index) - TRUE neighbors
SELECT id, embedding <=> '[...]'::vector AS distance
FROM _test_hnsw_recall
ORDER BY distance
LIMIT 10;
-- Save these IDs as "ground truth"

-- Create HNSW index
CREATE INDEX idx_hnsw_recall 
ON _test_hnsw_recall 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- Query 2: HNSW (with index) - HNSW neighbors
SELECT id, embedding <=> '[...]'::vector AS distance
FROM _test_hnsw_recall
ORDER BY distance
LIMIT 10;
-- Compare IDs with ground truth

-- Recall = (# of matching IDs) / 10
-- Example: If 9 out of 10 IDs match → 90% recall

-- Cleanup
DROP TABLE _test_hnsw_recall;
"""
    
    print(recall_sql)
    
    print("\n📊 Interpretation:")
    print("   10/10 matches → 100% recall (perfect)")
    print("   9/10 matches → 90% recall (acceptable)")
    print("   <9/10 matches → <90% recall (may need tuning)")

def test_index_build_time():
    """Test HNSW index build time."""
    print("\n" + "=" * 60)
    print("HNSW Index Build Time")
    print("=" * 60)
    
    print("\n📊 Expected index build times (1536d vectors):\n")
    
    build_times = [
        ("1,000 vectors", "~10-30 seconds"),
        ("10,000 vectors", "~30-90 seconds"),
        ("100,000 vectors", "~5-10 minutes"),
    ]
    
    print(f"{'Dataset Size':<20} {'Build Time':<20}")
    print("-" * 40)
    for size, time in build_times:
        print(f"{size:<20} {time:<20}")
    
    print("\n💡 Tips for faster builds:")
    print("   - Use CREATE INDEX CONCURRENTLY (allows reads/writes)")
    print("   - Build during off-peak hours")
    print("   - Consider lower ef_construction for faster builds")

def main():
    """Run HNSW performance validation."""
    print("\n" + "=" * 60)
    print("PHASE 3 VAN QA - TEST 2: HNSW Performance")
    print("=" * 60)
    
    test_hnsw_performance()
    test_recall_accuracy()
    test_index_build_time()
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print("⚠️  MANUAL: HNSW performance requires manual testing in Supabase")
    print("   Follow SQL scripts above to validate")
    print("\n✅ Target metrics:")
    print("   - Query time: <100ms (ideal <50ms)")
    print("   - Recall: >90% (ideal >95%)")
    print("   - Build time: <2min for 10k vectors")
    
    return 2  # Manual verification

if __name__ == '__main__':
    sys.exit(main())
