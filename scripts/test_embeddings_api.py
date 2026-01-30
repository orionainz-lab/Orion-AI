#!/usr/bin/env python3
"""
VAN-QA-4: Embedding API Integration Test

Validates:
- OpenAI embedding API is accessible
- text-embedding-3-small model works
- Latency meets <500ms target
- 1536-dimensional vectors returned

Risk: MEDIUM - Can fall back to local model if fails
"""

import os
import sys
import time
from typing import List, Optional

def test_openai_embeddings():
    """Test OpenAI text-embedding-3-small API."""
    print("=" * 60)
    print("VAN-QA-4: OpenAI Embedding API")
    print("=" * 60)
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("\n⚠️  WARNING: OPENAI_API_KEY not found in environment")
        print("   Skipping OpenAI validation")
        print("   Will test local fallback model instead")
        return None
    
    try:
        import openai
        print("\n✅ openai package installed")
    except ImportError:
        print("\n❌ FAILED: openai package not installed")
        print("   Run: pip install openai")
        return False
    
    try:
        # Configure OpenAI client
        openai.api_key = api_key
        print(f"\n🔑 API Key configured: {api_key[:10]}...")
        
        # Test embedding generation
        print("\n🧪 Testing text-embedding-3-small...")
        test_text = "This is a test document for Phase 3 RAG system validation."
        
        start_time = time.time()
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=test_text
        )
        latency_ms = (time.time() - start_time) * 1000
        
        # Validate response
        embedding = response.data[0].embedding
        dimensions = len(embedding)
        
        print(f"✅ Embedding generated successfully")
        print(f"   Dimensions: {dimensions}")
        print(f"   Latency: {latency_ms:.0f}ms")
        print(f"   Sample values: {embedding[:5]}")
        
        # Validate dimensions (should be 1536 for text-embedding-3-small)
        if dimensions != 1536:
            print(f"❌ FAILED: Expected 1536 dimensions, got {dimensions}")
            return False
        
        # Validate latency (<500ms target)
        if latency_ms > 500:
            print(f"⚠️  WARNING: Latency {latency_ms:.0f}ms exceeds 500ms target")
            print("   This may impact RAG performance")
        else:
            print(f"✅ Latency within target (<500ms)")
        
        # Test batch processing
        print("\n🧪 Testing batch embedding generation...")
        test_texts = [
            "First document chunk",
            "Second document chunk",
            "Third document chunk"
        ]
        
        start_time = time.time()
        batch_response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=test_texts
        )
        batch_latency_ms = (time.time() - start_time) * 1000
        
        print(f"✅ Batch generation successful")
        print(f"   Texts: {len(test_texts)}")
        print(f"   Total latency: {batch_latency_ms:.0f}ms")
        print(f"   Per-text: {batch_latency_ms / len(test_texts):.0f}ms")
        
        # Cost calculation
        total_tokens = sum(len(text.split()) for text in test_texts) * 1.3  # Rough estimate
        cost = (total_tokens / 1_000_000) * 0.02  # $0.02 per 1M tokens
        print(f"\n💰 Cost estimate:")
        print(f"   Tokens: ~{total_tokens:.0f}")
        print(f"   Cost: ${cost:.6f}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        return False

def test_local_embeddings():
    """Test local embedding model fallback."""
    print("\n" + "=" * 60)
    print("Testing Local Embedding Model (Fallback)")
    print("=" * 60)
    
    try:
        from sentence_transformers import SentenceTransformer
        print("\n✅ sentence-transformers installed")
    except ImportError:
        print("\n⚠️  sentence-transformers not installed")
        print("   Run: pip install sentence-transformers")
        print("   Local fallback will not be available")
        return False
    
    try:
        print("\n📥 Loading all-MiniLM-L6-v2 model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model loaded")
        
        # Test embedding
        test_text = "This is a test document."
        
        start_time = time.time()
        embedding = model.encode(test_text)
        latency_ms = (time.time() - start_time) * 1000
        
        dimensions = len(embedding)
        
        print(f"\n✅ Local embedding generated")
        print(f"   Dimensions: {dimensions}")
        print(f"   Latency: {latency_ms:.0f}ms")
        print(f"   Sample values: {embedding[:5]}")
        
        # Note: Local model is 384d, not 1536d
        if dimensions != 384:
            print(f"⚠️  WARNING: Expected 384 dimensions, got {dimensions}")
        
        print(f"\n💡 Note: Local model is 384d (vs 1536d for OpenAI)")
        print("   Would require separate pgvector table or re-embedding")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        return False

def calculate_costs():
    """Calculate embedding costs for Phase 3 scale."""
    print("\n" + "=" * 60)
    print("Cost Analysis for Phase 3")
    print("=" * 60)
    
    scenarios = [
        ("Small", 1_000, 400),      # 1k chunks, 400 tokens avg
        ("Medium", 10_000, 400),    # 10k chunks
        ("Large", 100_000, 400),    # 100k chunks
    ]
    
    print("\n📊 OpenAI text-embedding-3-small ($0.02 per 1M tokens):\n")
    print(f"{'Scenario':<10} {'Chunks':<10} {'Tokens':<12} {'Cost':<10}")
    print("-" * 45)
    
    for name, chunks, avg_tokens in scenarios:
        total_tokens = chunks * avg_tokens
        cost = (total_tokens / 1_000_000) * 0.02
        print(f"{name:<10} {chunks:<10,} {total_tokens:<12,} ${cost:<9.2f}")
    
    print("\n💡 Local model: $0 (but lower quality)")

def main():
    """Run embedding API validation tests."""
    print("\n" + "=" * 60)
    print("PHASE 3 VAN QA - TEST 4: Embedding API")
    print("=" * 60)
    
    openai_result = test_openai_embeddings()
    local_result = test_local_embeddings()
    calculate_costs()
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if openai_result is True:
        print("✅ PASS: OpenAI embeddings working (primary model)")
        if local_result:
            print("✅ BONUS: Local fallback also available")
        return 0
    elif openai_result is None:
        if local_result:
            print("⚠️  CONDITIONAL: No OpenAI key, but local model works")
            print("   Can proceed with local model for development")
            print("   Production should use OpenAI for best quality")
            return 2
        else:
            print("❌ FAIL: Neither OpenAI nor local model working")
            return 1
    else:
        print("❌ FAIL: OpenAI API validation failed")
        if local_result:
            print("⚠️  Local fallback available (proceed with caution)")
            return 2
        return 1

if __name__ == '__main__':
    sys.exit(main())
