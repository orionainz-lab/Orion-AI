#!/usr/bin/env python3
"""
Phase 3: Integration Tests

End-to-end testing of embedding pipeline and RAG system.
Validates all Phase 3 components working together.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_document_chunking():
    """Test document chunker service."""
    print("\n" + "="*60)
    print("TEST 1: Document Chunking")
    print("="*60)
    
    from services.document_chunker import DocumentChunker
    
    # Test document
    test_doc = """
    This is the first paragraph with some content.
    It has multiple sentences to test chunking.
    
    This is the second paragraph.
    It should be in a different chunk.
    
    This is the third paragraph with more content.
    We want to ensure overlap works correctly.
    """
    
    chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
    chunks = chunker.chunk_text(test_doc, "test-doc-id")
    
    print(f"\nChunks created: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i}: {chunk.token_count} tokens, {len(chunk.text)} chars")
    
    stats = chunker.get_chunk_stats(chunks)
    print(f"\nStats: {stats}")
    
    assert len(chunks) > 0, "Should create chunks"
    assert all(c.chunk_index == i for i, c in enumerate(chunks)), "Indices correct"
    
    print("PASS: Document chunking works")
    return True


async def test_embedding_service_local():
    """Test embedding service with local model."""
    print("\n" + "="*60)
    print("TEST 2: Embedding Service (Local Model)")
    print("="*60)
    
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("SKIP: sentence-transformers not installed")
        print("  Run: pip install sentence-transformers")
        return None
    
    from services.embedding_service import EmbeddingService
    
    # Mock supabase client (cache not tested here)
    class MockSupabase:
        def table(self, name):
            return self
        def select(self, cols):
            return self
        def eq(self, col, val):
            return self
        def execute(self):
            class Result:
                data = []
            return Result()
    
    service = EmbeddingService(
        MockSupabase(),
        primary_model="local",
        use_cache=False
    )
    
    test_text = "This is a test document for embedding."
    embedding = await service.generate_embedding(test_text)
    
    print(f"\nEmbedding generated:")
    print(f"  Dimensions: {len(embedding)}")
    print(f"  Sample: {embedding[:5]}")
    print(f"  Expected: 384 (all-MiniLM-L6-v2)")
    
    assert len(embedding) == 384, "Local model should produce 384d vectors"
    assert all(isinstance(x, float) for x in embedding), "Should be floats"
    
    print("PASS: Local embedding generation works")
    return True


async def test_vector_similarity():
    """Test vector similarity calculation."""
    print("\n" + "="*60)
    print("TEST 3: Vector Similarity")
    print("="*60)
    
    from utils.vector_utils import cosine_similarity, normalize_vector
    
    # Test identical vectors
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    sim = cosine_similarity(vec1, vec2)
    print(f"\nIdentical vectors: {sim:.4f} (expected ~1.0)")
    assert abs(sim - 1.0) < 0.001, "Identical vectors should have similarity ~1"
    
    # Test orthogonal vectors
    vec3 = [1.0, 0.0, 0.0]
    vec4 = [0.0, 1.0, 0.0]
    sim = cosine_similarity(vec3, vec4)
    print(f"Orthogonal vectors: {sim:.4f} (expected 0.0)")
    assert abs(sim) < 0.001, "Orthogonal vectors should have similarity ~0"
    
    # Test similar vectors
    vec5 = [1.0, 2.0, 3.0]
    vec6 = [1.1, 2.1, 2.9]
    sim = cosine_similarity(vec5, vec6)
    print(f"Similar vectors: {sim:.4f} (expected >0.9)")
    assert sim > 0.9, "Similar vectors should have high similarity"
    
    # Test normalization
    vec7 = [3.0, 4.0]
    normalized = normalize_vector(vec7)
    magnitude = sum(x**2 for x in normalized) ** 0.5
    print(f"\nNormalized magnitude: {magnitude:.4f} (expected 1.0)")
    assert abs(magnitude - 1.0) < 0.001, "Normalized vector should have magnitude 1"
    
    print("PASS: Vector similarity calculations correct")
    return True


def main():
    """Run all Phase 3 integration tests."""
    print("\n" + "="*60)
    print("PHASE 3 INTEGRATION TESTS")
    print("="*60)
    
    results = {}
    
    # Run async tests
    loop = asyncio.get_event_loop()
    
    tests = [
        ("Document Chunking", test_document_chunking),
        ("Embedding Service (Local)", test_embedding_service_local),
        ("Vector Similarity", test_vector_similarity),
    ]
    
    for name, test_func in tests:
        try:
            result = loop.run_until_complete(test_func())
            results[name] = result
        except Exception as e:
            print(f"\nERROR in {name}: {e}")
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
    
    for name, result in results.items():
        status = "PASS" if result is True else ("SKIP" if result is None else "FAIL")
        print(f"  {status}: {name}")
    
    if failed > 0:
        print("\nFAIL: Some tests failed")
        return 1
    else:
        print("\nPASS: All tests passed or skipped")
        return 0


if __name__ == '__main__':
    sys.exit(main())
