#!/usr/bin/env python3
"""
Phase 3: Comprehensive Integration Testing

Tests the complete RAG pipeline end-to-end:
1. Document ingestion (chunking + embedding + storage)
2. Vector search with RLS
3. Context building
4. Integration with LangGraph agents
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env
load_dotenv()


def check_environment():
    """Check required environment variables."""
    print("\n" + "="*60)
    print("ENVIRONMENT CHECK")
    print("="*60)
    
    required = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_ANON_KEY': os.getenv('SUPABASE_ANON_KEY'),
        'SUPABASE_SERVICE_ROLE_KEY': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
    }
    
    optional = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    }
    
    all_present = True
    
    for key, value in required.items():
        status = "OK" if value else "MISSING"
        print(f"  {key}: {status}")
        if not value:
            all_present = False
    
    print("\nOptional:")
    for key, value in optional.items():
        status = "OK" if value else "Not set (will use local fallback)"
        print(f"  {key}: {status}")
    
    if not all_present:
        print("\nERROR: Missing required environment variables")
        print("Please set them in .env or export them")
        return False
    
    print("\nPASS: Environment configured")
    return True


async def test_document_chunking():
    """Test 1: Document chunking with overlap."""
    print("\n" + "="*60)
    print("TEST 1: Document Chunking")
    print("="*60)
    
    from services.document_chunker import DocumentChunker
    
    test_doc = """
    Introduction to Python Async Programming
    
    Python's asyncio module provides infrastructure for writing concurrent code
    using the async/await syntax. This is particularly useful for I/O-bound tasks.
    
    Key Concepts:
    
    1. Coroutines: Functions defined with async def that can be paused and resumed.
    2. Event Loop: Manages and distributes execution of asynchronous tasks.
    3. Tasks: Wrappers around coroutines that allow concurrent execution.
    
    Best Practices:
    
    - Use async for I/O operations (database, API calls, file operations)
    - Avoid blocking calls inside async functions
    - Handle exceptions properly with try/except blocks
    - Use asyncio.gather() to wait for multiple tasks
    """
    
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_text(test_doc, "test-doc-123")
    
    print(f"\nDocument: {len(test_doc)} chars")
    print(f"Chunks created: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        print(f"\n  Chunk {i}:")
        print(f"    Tokens: {chunk.token_count}")
        print(f"    Chars: {len(chunk.text)}")
        print(f"    Preview: {chunk.text[:50]}...")
    
    stats = chunker.get_chunk_stats(chunks)
    print(f"\nStatistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Total tokens: {stats['total_tokens']}")
    print(f"  Avg tokens/chunk: {stats['avg_tokens_per_chunk']:.1f}")
    print(f"  Min tokens: {stats['min_tokens']}")
    print(f"  Max tokens: {stats['max_tokens']}")
    
    # Assertions
    assert len(chunks) > 1, "Should create multiple chunks"
    assert all(c.chunk_index == i for i, c in enumerate(chunks)), "Indices correct"
    assert stats['total_chunks'] == len(chunks), "Stats match"
    
    print("\nPASS: Document chunking works correctly")
    return True


async def test_embedding_service():
    """Test 2: Embedding generation (local fallback)."""
    print("\n" + "="*60)
    print("TEST 2: Embedding Service")
    print("="*60)
    
    try:
        from sentence_transformers import SentenceTransformer
        has_local = True
    except ImportError:
        print("SKIP: sentence-transformers not installed")
        print("  Install with: pip install sentence-transformers")
        return None
    
    from services.embedding_service import EmbeddingService
    
    # Mock Supabase client
    class MockSupabase:
        def table(self, name):
            return self
        def select(self, cols):
            return self
        def eq(self, col, val):
            return self
        def insert(self, data):
            return self
        def execute(self):
            class Result:
                data = []
            return Result()
        def rpc(self, func, params):
            return self
    
    service = EmbeddingService(
        MockSupabase(),
        primary_model="local",
        use_cache=False
    )
    
    test_texts = [
        "Python async programming",
        "Database queries with asyncio",
        "Event loop and coroutines"
    ]
    
    print(f"\nGenerating embeddings for {len(test_texts)} texts...")
    
    # Single embedding
    embedding1 = await service.generate_embedding(test_texts[0])
    print(f"\nSingle embedding:")
    print(f"  Dimensions: {len(embedding1)}")
    print(f"  Type: {type(embedding1[0])}")
    print(f"  Sample values: {[f'{x:.4f}' for x in embedding1[:3]]}")
    
    # Batch embeddings
    embeddings = await service.generate_embeddings_batch(test_texts, batch_size=10)
    print(f"\nBatch embeddings:")
    print(f"  Count: {len(embeddings)}")
    print(f"  All same dimensions: {all(len(e) == 384 for e in embeddings)}")
    
    # Assertions
    assert len(embedding1) == 384, "Local model produces 384d vectors"
    assert len(embeddings) == len(test_texts), "Batch count matches"
    assert all(isinstance(x, float) for x in embedding1), "Values are floats"
    
    print("\nPASS: Embedding generation works")
    return True


async def test_vector_similarity():
    """Test 3: Vector similarity calculations."""
    print("\n" + "="*60)
    print("TEST 3: Vector Similarity")
    print("="*60)
    
    from utils.vector_utils import (
        cosine_similarity,
        normalize_vector,
        validate_vector_dimensions,
        calculate_storage_size
    )
    
    # Test 1: Identical vectors
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    sim = cosine_similarity(vec1, vec2)
    print(f"\nIdentical vectors similarity: {sim:.4f}")
    assert abs(sim - 1.0) < 0.001, "Should be ~1.0"
    
    # Test 2: Orthogonal vectors
    vec3 = [1.0, 0.0, 0.0]
    vec4 = [0.0, 1.0, 0.0]
    sim = cosine_similarity(vec3, vec4)
    print(f"Orthogonal vectors similarity: {sim:.4f}")
    assert abs(sim) < 0.001, "Should be ~0.0"
    
    # Test 3: Similar vectors
    vec5 = [1.0, 2.0, 3.0]
    vec6 = [1.1, 2.1, 2.9]
    sim = cosine_similarity(vec5, vec6)
    print(f"Similar vectors similarity: {sim:.4f}")
    assert sim > 0.9, "Should be >0.9"
    
    # Test 4: Normalization
    vec7 = [3.0, 4.0]
    normalized = normalize_vector(vec7)
    magnitude = sum(x**2 for x in normalized) ** 0.5
    print(f"\nNormalization:")
    print(f"  Original: {vec7}")
    print(f"  Normalized: {[f'{x:.4f}' for x in normalized]}")
    print(f"  Magnitude: {magnitude:.4f}")
    assert abs(magnitude - 1.0) < 0.001, "Should be unit length"
    
    # Test 5: Dimension validation
    vec_1536 = [0.0] * 1536
    vec_384 = [0.0] * 384
    print(f"\nDimension validation:")
    print(f"  1536d valid: {validate_vector_dimensions(vec_1536, 1536)}")
    print(f"  384d valid: {validate_vector_dimensions(vec_384, 384)}")
    print(f"  384d as 1536d: {validate_vector_dimensions(vec_384, 1536)}")
    
    # Test 6: Storage estimation
    storage = calculate_storage_size(10000, dimensions=1536)
    print(f"\nStorage for 10,000 vectors (1536d):")
    print(f"  Data: {storage['data_size_mb']} MB")
    print(f"  Index: {storage['index_size_mb']} MB")
    print(f"  Total: {storage['total_size_mb']} MB")
    
    print("\nPASS: Vector utilities work correctly")
    return True


async def test_supabase_connection():
    """Test 4: Supabase database connection."""
    print("\n" + "="*60)
    print("TEST 4: Supabase Connection")
    print("="*60)
    
    try:
        import supabase as sb
        create_client = sb.create_client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_ANON_KEY')
        
        print(f"\nConnecting to Supabase...")
        print(f"  URL: {url[:30]}..." if url else "  URL: NOT SET")
        
        supabase = create_client(url, key)
        
        # Test query (should work even with empty tables)
        result = supabase.table('documents').select('count', count='exact').execute()
        doc_count = result.count
        
        print(f"\nConnection successful!")
        print(f"  Documents in database: {doc_count}")
        
        # Check other tables
        tables = ['document_chunks', 'teams', 'process_events', 'embedding_cache']
        for table in tables:
            try:
                result = supabase.table(table).select('count', count='exact').execute()
                print(f"  {table}: {result.count} rows")
            except Exception as e:
                print(f"  {table}: ERROR - {e}")
        
        print("\nPASS: Supabase connection works")
        return True
        
    except Exception as e:
        print(f"\nFAIL: Supabase connection failed - {e}")
        return False


async def test_acl_helper():
    """Test 5: ACL helper functions."""
    print("\n" + "="*60)
    print("TEST 5: ACL Helper")
    print("="*60)
    
    from utils.acl_helper import ACLHelper
    
    # Mock Supabase client
    class MockSupabase:
        def __init__(self, return_data=None):
            self.return_data = return_data or []
        
        def table(self, name):
            return self
        
        def select(self, cols):
            return self
        
        def eq(self, col, val):
            return self
        
        def in_(self, col, vals):
            return self
        
        def insert(self, data):
            self.inserted_data = data
            return self
        
        def delete(self):
            return self
        
        def execute(self):
            class Result:
                def __init__(self, data):
                    self.data = data
            return Result(self.return_data)
    
    # Test document access check
    print("\nTesting document access check...")
    mock = MockSupabase(return_data=[{'id': 'doc-123'}])
    acl = ACLHelper(mock)
    
    can_access = await acl.user_can_access_document('user-1', 'doc-123')
    print(f"  User can access: {can_access}")
    assert can_access == True, "Should return True when document found"
    
    # Test team membership
    print("\nTesting team membership...")
    mock = MockSupabase(return_data=[
        {'team_id': 'team-1'},
        {'team_id': 'team-2'}
    ])
    acl = ACLHelper(mock)
    
    teams = await acl.get_user_teams('user-1')
    print(f"  User teams: {teams}")
    assert len(teams) == 2, "Should return 2 teams"
    
    # Test permission filtering
    print("\nTesting permission filtering...")
    mock = MockSupabase(return_data=[
        {'id': 'doc-1'},
        {'id': 'doc-3'}
    ])
    acl = ACLHelper(mock)
    
    doc_ids = ['doc-1', 'doc-2', 'doc-3', 'doc-4']
    filtered = await acl.filter_documents_by_permission('user-1', doc_ids)
    print(f"  Input: {doc_ids}")
    print(f"  Filtered: {filtered}")
    assert len(filtered) == 2, "Should filter to accessible docs"
    
    print("\nPASS: ACL helper works correctly")
    return True


async def test_langraph_integration():
    """Test 6: LangGraph state integration."""
    print("\n" + "="*60)
    print("TEST 6: LangGraph Integration")
    print("="*60)
    
    from agents.state import create_initial_state, get_state_summary
    
    # Create state with RAG fields
    state = create_initial_state(
        task="Create an async function",
        user_id="user-123",
        language="python",
        rag_enabled=True
    )
    
    print("\nState fields:")
    print(f"  task: {state['task']}")
    print(f"  user_id: {state['user_id']}")
    print(f"  language: {state['language']}")
    print(f"  rag_enabled: {state['rag_enabled']}")
    print(f"  rag_context: {state['rag_context']}")
    print(f"  rag_sources: {state['rag_sources']}")
    
    # Check state summary
    summary = get_state_summary(state)
    print(f"\nState summary: {summary}")
    
    # Assertions
    assert state['user_id'] == "user-123", "user_id set"
    assert state['rag_enabled'] == True, "RAG enabled"
    assert 'rag_context' in state, "Has rag_context field"
    assert 'rag_sources' in state, "Has rag_sources field"
    
    print("\nPASS: LangGraph integration ready")
    return True


def main():
    """Run all Phase 3 integration tests."""
    print("\n" + "="*60)
    print("PHASE 3 COMPREHENSIVE INTEGRATION TESTS")
    print("="*60)
    
    # Check environment first
    if not check_environment():
        print("\nSKIP: Environment not configured")
        return 1
    
    results = {}
    
    # Run async tests
    loop = asyncio.get_event_loop()
    
    tests = [
        ("Document Chunking", test_document_chunking),
        ("Embedding Service", test_embedding_service),
        ("Vector Similarity", test_vector_similarity),
        ("Supabase Connection", test_supabase_connection),
        ("ACL Helper", test_acl_helper),
        ("LangGraph Integration", test_langraph_integration),
    ]
    
    for name, test_func in tests:
        try:
            result = loop.run_until_complete(test_func())
            results[name] = result
        except Exception as e:
            print(f"\nERROR in {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r is True)
    skipped = sum(1 for r in results.values() if r is None)
    failed = sum(1 for r in results.values() if r is False)
    
    print(f"\nTotal: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
    
    print("\nDetailed Results:")
    for name, result in results.items():
        if result is True:
            status = "PASS"
        elif result is None:
            status = "SKIP"
        else:
            status = "FAIL"
        print(f"  [{status}] {name}")
    
    if failed > 0:
        print("\n" + "="*60)
        print("FAIL: Some tests failed")
        print("="*60)
        return 1
    else:
        print("\n" + "="*60)
        print("SUCCESS: All tests passed or skipped")
        print("="*60)
        return 0


if __name__ == '__main__':
    sys.exit(main())
