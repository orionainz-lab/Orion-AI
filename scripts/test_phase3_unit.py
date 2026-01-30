#!/usr/bin/env python3
"""
Phase 3: Unit Tests (No External Dependencies)

Tests that can run without Supabase or OpenAI credentials.
These validate the core algorithms and logic.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_document_chunking():
    """Test 1: Document chunking with various sizes."""
    print("\n" + "="*60)
    print("TEST 1: Document Chunking")
    print("="*60)
    
    from services.document_chunker import DocumentChunker
    
    # Test document with multiple paragraphs
    test_doc = """
Introduction to Async Programming

Python's asyncio module provides infrastructure for writing concurrent code.
This is particularly useful for I/O-bound tasks like network requests.

Key Concepts

Coroutines are functions defined with async def that can be paused and resumed.
The event loop manages and distributes execution of asynchronous tasks.
Tasks are wrappers around coroutines that allow concurrent execution.

Best Practices

Use async for I/O operations like database queries and API calls.
Avoid blocking calls inside async functions to prevent blocking the event loop.
Handle exceptions properly with try/except blocks in your coroutines.
Use asyncio.gather() to wait for multiple tasks to complete concurrently.
"""
    
    # Test with different chunk sizes
    test_cases = [
        (50, 10, "Small chunks"),
        (100, 20, "Medium chunks"),
        (200, 50, "Large chunks"),
    ]
    
    for chunk_size, overlap, desc in test_cases:
        print(f"\n{desc} (size={chunk_size}, overlap={overlap}):")
        
        chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=overlap)
        chunks = chunker.chunk_text(test_doc, "test-doc")
        
        print(f"  Chunks created: {len(chunks)}")
        print(f"  Token range: {min(c.token_count for c in chunks)} - {max(c.token_count for c in chunks)}")
        
        # Verify chunks
        assert len(chunks) > 0, "Should create chunks"
        assert all(c.chunk_index == i for i, c in enumerate(chunks)), "Indices sequential"
        assert all(c.metadata['document_id'] == "test-doc" for c in chunks), "Metadata correct"
    
    # Test edge cases
    print("\nEdge cases:")
    
    # Empty document
    empty_chunks = chunker.chunk_text("", "empty")
    print(f"  Empty document: {len(empty_chunks)} chunks")
    assert len(empty_chunks) == 0, "Empty doc produces no chunks"
    
    # Very short document
    short_chunks = chunker.chunk_text("Short text.", "short")
    print(f"  Short document: {len(short_chunks)} chunks")
    assert len(short_chunks) == 1, "Short doc produces 1 chunk"
    
    # Document with no separators
    nosep_chunks = chunker.chunk_text("a" * 1000, "nosep")
    print(f"  No separators: {len(nosep_chunks)} chunks (hard split)")
    assert len(nosep_chunks) > 1, "Long text without separators gets split"
    
    print("\nPASS: Document chunking works correctly")
    return True


async def test_vector_math():
    """Test 2: Vector mathematics."""
    print("\n" + "="*60)
    print("TEST 2: Vector Mathematics")
    print("="*60)
    
    from utils.vector_utils import (
        cosine_similarity,
        normalize_vector,
        validate_vector_dimensions,
        calculate_storage_size,
        vector_to_string
    )
    
    # Test cosine similarity
    print("\nCosine Similarity:")
    test_cases = [
        ([1, 0, 0], [1, 0, 0], 1.0, "Identical"),
        ([1, 0, 0], [0, 1, 0], 0.0, "Orthogonal"),
        ([1, 2, 3], [1, 2, 3], 1.0, "Same vector"),
        ([1, 2, 3], [-1, -2, -3], -1.0, "Opposite"),
        ([1, 2], [2, 4], 1.0, "Parallel"),
    ]
    
    for vec1, vec2, expected, desc in test_cases:
        sim = cosine_similarity(vec1, vec2)
        print(f"  {desc}: {sim:.4f} (expected {expected:.4f})")
        assert abs(sim - expected) < 0.01, f"{desc} failed"
    
    # Test normalization
    print("\nNormalization:")
    test_vectors = [
        [3, 4],
        [1, 1, 1],
        [5, 0, 0],
    ]
    
    for vec in test_vectors:
        normalized = normalize_vector(vec)
        magnitude = sum(x**2 for x in normalized) ** 0.5
        print(f"  {vec} -> magnitude = {magnitude:.4f}")
        assert abs(magnitude - 1.0) < 0.001, "Should be unit length"
    
    # Test dimension validation
    print("\nDimension Validation:")
    valid_1536 = validate_vector_dimensions([0.0] * 1536, 1536)
    valid_384 = validate_vector_dimensions([0.0] * 384, 384)
    invalid = validate_vector_dimensions([0.0] * 100, 1536)
    print(f"  1536d vector: {valid_1536}")
    print(f"  384d vector: {valid_384}")
    print(f"  Wrong dimension: {invalid}")
    assert valid_1536 and valid_384 and not invalid
    
    # Test storage calculation
    print("\nStorage Calculation:")
    for num_vectors in [1000, 10000, 100000]:
        storage = calculate_storage_size(num_vectors, dimensions=1536)
        print(f"  {num_vectors:,} vectors:")
        print(f"    Data: {storage['data_size_mb']:.2f} MB")
        print(f"    Total: {storage['total_size_mb']:.2f} MB")
    
    # Test vector string conversion
    print("\nVector String Conversion:")
    vec = [0.1, 0.2, 0.3]
    vec_str = vector_to_string(vec)
    print(f"  {vec} -> '{vec_str}'")
    assert vec_str == '[0.1,0.2,0.3]', "String format correct"
    
    print("\nPASS: Vector mathematics correct")
    return True


async def test_context_builder():
    """Test 3: Context builder formatting."""
    print("\n" + "="*60)
    print("TEST 3: Context Builder")
    print("="*60)
    
    from services.context_builder import ContextBuilder
    from services.rag_service import RAGResult
    
    # Create mock RAG results
    mock_results = [
        RAGResult(
            id="chunk-1",
            document_id="doc-1",
            document_title="Python Async Guide",
            chunk_text="Async functions are defined with async def...",
            chunk_index=0,
            similarity_score=0.95,
            metadata={}
        ),
        RAGResult(
            id="chunk-2",
            document_id="doc-2",
            document_title="Error Handling",
            chunk_text="Use try/except blocks to handle exceptions...",
            chunk_index=0,
            similarity_score=0.87,
            metadata={}
        ),
    ]
    
    builder = ContextBuilder(max_tokens=1000)
    
    # Test different formats
    formats = ["claude", "openai", "gemini"]
    
    for fmt in formats:
        print(f"\n{fmt.upper()} format:")
        context = builder.build_context("test query", mock_results, format=fmt)
        
        print(f"  Context length: {len(context.context_text)} chars")
        print(f"  Sources: {len(context.sources)}")
        print(f"  Tokens: {context.token_count}")
        print(f"  Truncated: {context.truncated}")
        print(f"  Preview: {context.context_text[:100]}...")
        
        assert len(context.sources) == 2, "Should have 2 sources"
        assert context.token_count > 0, "Should count tokens"
        assert not context.truncated, "Should not be truncated"
    
    # Test truncation
    print("\nTruncation test:")
    builder_small = ContextBuilder(max_tokens=10)
    context = builder_small.build_context("test", mock_results)
    print(f"  Truncated: {context.truncated}")
    print(f"  Sources included: {len(context.sources)}")
    assert context.truncated or len(context.sources) < len(mock_results), "Should truncate"
    
    # Test prompt building
    print("\nPrompt building:")
    context = builder.build_context("How to use async?", mock_results)
    prompt = builder.build_prompt_with_context(
        task="Create async function",
        context=context,
        system_message="You are a Python expert"
    )
    print(f"  Prompt length: {len(prompt)} chars")
    assert "Create async function" in prompt, "Task included"
    assert "Python expert" in prompt, "System message included"
    
    # Test sources summary
    summary = builder.get_sources_summary(context)
    print(f"\nSources summary:\n{summary}")
    assert "Python Async Guide" in summary, "Document title included"
    
    print("\nPASS: Context builder works correctly")
    return True


async def test_acl_logic():
    """Test 4: ACL helper logic (mock)."""
    print("\n" + "="*60)
    print("TEST 4: ACL Helper Logic")
    print("="*60)
    
    from utils.acl_helper import ACLHelper
    
    # Mock Supabase with predictable responses
    class MockSupabase:
        def __init__(self):
            self.documents = {
                'doc-1': {'owner': 'user-1'},
                'doc-2': {'owner': 'user-2'},
            }
            self.teams = {
                'user-1': ['team-a', 'team-b'],
                'user-2': ['team-b'],
            }
        
        def table(self, name):
            self.current_table = name
            return self
        
        def select(self, cols):
            return self
        
        def eq(self, col, val):
            self.filter_val = val
            return self
        
        def in_(self, col, vals):
            self.filter_vals = vals
            return self
        
        def insert(self, data):
            return self
        
        def delete(self):
            return self
        
        def execute(self):
            class Result:
                def __init__(self, data):
                    self.data = data
            
            if self.current_table == 'documents':
                if hasattr(self, 'filter_vals'):
                    # Filter documents by IDs
                    data = [{'id': doc_id} for doc_id in self.filter_vals 
                           if doc_id in self.documents]
                else:
                    # Single document check
                    data = [{'id': self.filter_val}] if self.filter_val in self.documents else []
            elif self.current_table == 'team_members':
                user_id = self.filter_val
                data = [{'team_id': team} for team in self.teams.get(user_id, [])]
            else:
                data = []
            
            return Result(data)
    
    mock = MockSupabase()
    acl = ACLHelper(mock)
    
    # Test access checks
    print("\nAccess checks:")
    can_access_1 = await acl.user_can_access_document('user-1', 'doc-1')
    can_access_2 = await acl.user_can_access_document('user-1', 'doc-999')
    print(f"  User-1 can access doc-1: {can_access_1}")
    print(f"  User-1 can access doc-999: {can_access_2}")
    assert can_access_1 == True, "Should access existing doc"
    assert can_access_2 == False, "Should not access missing doc"
    
    # Test team membership
    print("\nTeam membership:")
    teams_1 = await acl.get_user_teams('user-1')
    teams_2 = await acl.get_user_teams('user-2')
    print(f"  User-1 teams: {teams_1}")
    print(f"  User-2 teams: {teams_2}")
    assert len(teams_1) == 2, "User-1 has 2 teams"
    assert len(teams_2) == 1, "User-2 has 1 team"
    
    # Test permission filtering
    print("\nPermission filtering:")
    doc_ids = ['doc-1', 'doc-2', 'doc-3']
    filtered = await acl.filter_documents_by_permission('user-1', doc_ids)
    print(f"  Input IDs: {doc_ids}")
    print(f"  Filtered: {filtered}")
    assert len(filtered) == 2, "Should filter to existing docs"
    
    print("\nPASS: ACL logic correct")
    return True


async def test_langraph_state():
    """Test 5: LangGraph state schema."""
    print("\n" + "="*60)
    print("TEST 5: LangGraph State Schema")
    print("="*60)
    
    from agents.state import create_initial_state, get_state_summary
    
    # Test state creation
    print("\nState creation:")
    state = create_initial_state(
        task="Create a sorting function",
        user_id="user-123",
        language="python",
        context="Use quicksort algorithm",
        max_iterations=5,
        rag_enabled=True
    )
    
    # Check all required fields
    required_fields = [
        'task', 'user_id', 'language', 'context',
        'plan', 'requirements',
        'rag_context', 'rag_sources', 'rag_enabled',
        'code', 'imports',
        'is_valid', 'errors', 'warnings',
        'feedback', 'correction_hints',
        'iteration', 'max_iterations',
        'model_used', 'tokens_used', 'reasoning_time_ms'
    ]
    
    print(f"\nChecking {len(required_fields)} required fields:")
    for field in required_fields:
        has_field = field in state
        status = "OK" if has_field else "MISSING"
        print(f"  {field}: {status}")
        assert has_field, f"Missing field: {field}"
    
    # Check initial values
    print("\nInitial values:")
    print(f"  task: {state['task']}")
    print(f"  user_id: {state['user_id']}")
    print(f"  rag_enabled: {state['rag_enabled']}")
    print(f"  iteration: {state['iteration']}")
    print(f"  max_iterations: {state['max_iterations']}")
    
    assert state['task'] == "Create a sorting function"
    assert state['user_id'] == "user-123"
    assert state['rag_enabled'] == True
    assert state['iteration'] == 0
    assert state['max_iterations'] == 5
    
    # Test state summary
    summary = get_state_summary(state)
    print(f"\nState summary:\n  {summary}")
    assert "Create a sorting function" in summary
    assert "python" in summary
    
    print("\nPASS: LangGraph state schema correct")
    return True


def main():
    """Run all unit tests."""
    print("\n" + "="*60)
    print("PHASE 3 UNIT TESTS (No External Dependencies)")
    print("="*60)
    
    results = {}
    
    # Run async tests
    loop = asyncio.get_event_loop()
    
    tests = [
        ("Document Chunking", test_document_chunking),
        ("Vector Mathematics", test_vector_math),
        ("Context Builder", test_context_builder),
        ("ACL Logic", test_acl_logic),
        ("LangGraph State", test_langraph_state),
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
    failed = sum(1 for r in results.values() if r is False)
    
    print(f"\nTotal: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    print("\nDetailed Results:")
    for name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")
    
    if failed > 0:
        print("\n" + "="*60)
        print("FAIL: Some tests failed")
        print("="*60)
        return 1
    else:
        print("\n" + "="*60)
        print("SUCCESS: All unit tests passed")
        print("="*60)
        return 0


if __name__ == '__main__':
    sys.exit(main())
