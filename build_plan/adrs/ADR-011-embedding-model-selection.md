# ADR-011: Embedding Model Selection

**Status**: DECIDED  
**Date**: 2026-01-30  
**Deciders**: ML Engineer, Backend Architect, Finance Team  
**Phase**: Phase 3 - The Secure Context

---

## Context

Phase 3 requires converting text documents into vector embeddings for semantic search in the RAG system. The choice of embedding model impacts:
- **Cost**: API pricing per million tokens
- **Quality**: Retrieval accuracy (MTEB benchmark scores)
- **Latency**: Time to generate embeddings
- **Operations**: API dependency vs local inference
- **Dimensions**: Vector size (impacts ADR-010 pgvector config)

**Key Requirements**:
1. High-quality semantic search for RAG
2. Cost-effective at scale (10k-100k document chunks)
3. Low latency (<500ms per chunk)
4. Vendor independence (avoid lock-in)

---

## Decision

**Primary Model**: **OpenAI `text-embedding-3-small`**

| Attribute | Value |
|-----------|-------|
| **Model** | `text-embedding-3-small` |
| **Provider** | OpenAI |
| **Dimensions** | 1536 |
| **Cost** | $0.02 per 1M tokens |
| **Latency** | ~200ms per request (batch) |
| **MTEB Score** | 62.3% (competitive) |

**Fallback Model**: **Local `all-MiniLM-L6-v2`**

| Attribute | Value |
|-----------|-------|
| **Model** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Provider** | Local (Hugging Face) |
| **Dimensions** | 384 |
| **Cost** | Free (local inference) |
| **Latency** | ~50ms per text (CPU) |
| **MTEB Score** | 56.3% (good for local) |

**Usage Strategy**:
- **Primary**: Use OpenAI for production and high-quality retrieval
- **Fallback**: Use local model for development without API keys
- **Hybrid**: Cache OpenAI embeddings, fall back to local on API errors

---

## Options Considered

### Option 1: OpenAI `text-embedding-3-small` (SELECTED - Primary)

```python
import openai

response = openai.embeddings.create(
    model="text-embedding-3-small",
    input=["Document text to embed..."]
)
embedding = response.data[0].embedding  # List[float], 1536 dims
```

**Pros**:
- ✅ Best cost/quality ratio ($0.02 vs $0.13 for -large)
- ✅ 1536 dimensions (standard, well-optimized in pgvector)
- ✅ High retrieval quality (MTEB: 62.3%)
- ✅ Proven at scale (used by many production systems)
- ✅ Fast inference (~200ms for batched requests)
- ✅ No local infrastructure needed

**Cons**:
- ❌ API dependency (vendor lock-in risk)
- ❌ Requires OpenAI API key
- ❌ Costs scale with document volume
- ❌ Rate limits (3,000 RPM on tier 1)

**Cost Analysis**:
- 1,000 chunks (avg 400 tokens): $0.008
- 10,000 chunks: $0.08
- 100,000 chunks: $0.80
- **Acceptable** for Phase 3 scale

**Verdict**: **SELECTED** as primary model.

---

### Option 2: OpenAI `text-embedding-3-large`

```python
response = openai.embeddings.create(
    model="text-embedding-3-large",
    input=["Document text to embed..."]
)
embedding = response.data[0].embedding  # List[float], 3072 dims
```

**Pros**:
- ✅ Highest retrieval quality (MTEB: 64.6%)
- ✅ Better performance on complex queries
- ✅ Same API as -small (easy migration)

**Cons**:
- ❌ 6.5x more expensive ($0.13 vs $0.02 per 1M tokens)
- ❌ Larger vectors (3072d vs 1536d)
  - 2x storage cost in pgvector
  - Slower queries (more dimensions to compare)
- ❌ Diminishing returns (2.3% MTEB improvement)

**Cost Analysis**:
- 10,000 chunks: $0.52 (vs $0.08 for -small)
- 100,000 chunks: $5.20 (vs $0.80 for -small)
- **Too expensive** for marginal quality gain

**Verdict**: **REJECTED** - Cost not justified by quality improvement.

---

### Option 3: Local Models `all-MiniLM-L6-v2` (SELECTED - Fallback)

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("Document text to embed...")  # ndarray, 384 dims
```

**Pros**:
- ✅ Free (no API costs)
- ✅ Fast inference (~50ms per text on CPU)
- ✅ No rate limits
- ✅ Works offline
- ✅ No vendor lock-in

**Cons**:
- ❌ Lower quality (MTEB: 56.3% vs 62.3% for OpenAI)
- ❌ Different dimensions (384d vs 1536d)
  - Requires separate pgvector table or re-embedding
- ❌ Requires local infrastructure (model download, CPU/GPU)
- ❌ Maintenance burden (model updates)

**Use Cases**:
- Development/testing without API keys
- Fallback when OpenAI API is down
- Cost optimization for non-critical documents

**Verdict**: **SELECTED** as fallback/development model.

---

### Option 4: Anthropic Embeddings (2026)

```python
# Hypothetical - check availability in VAN QA Mode
import anthropic

response = anthropic.embeddings.create(
    model="anthropic-embedding-v1",
    input=["Document text to embed..."]
)
embedding = response.embedding
```

**Status**: **Unknown in 2026** - check in VAN QA Mode

**Pros** (if available):
- ✅ Vendor diversification (reduce OpenAI dependency)
- ✅ Potentially competitive pricing
- ✅ Same provider as reasoning models (Claude)

**Cons**:
- ❌ Availability unknown
- ❌ Quality unknown
- ❌ Dimensions unknown (may require pgvector reconfiguration)

**Verdict**: **TBD** - Validate in VAN QA Mode, consider for future.

---

### Option 5: Cohere Embeddings

```python
import cohere

response = cohere.embed(
    model="embed-english-v3.0",
    texts=["Document text to embed..."],
    input_type="search_document"
)
embedding = response.embeddings[0]  # 1024 dims
```

**Pros**:
- ✅ Competitive quality (MTEB: 64.5%)
- ✅ Built for search (separate query/document embeddings)
- ✅ Good pricing ($0.10 per 1M tokens)

**Cons**:
- ❌ 1024 dimensions (different from OpenAI)
- ❌ Less widely adopted (fewer examples)
- ❌ Additional vendor dependency

**Verdict**: **REJECTED** - OpenAI more standard, similar cost.

---

## Rationale

### Why OpenAI `text-embedding-3-small`?

1. **Cost-Effective**: $0.02/1M tokens is 6.5x cheaper than -large
   - 100k chunks: $0.80 (vs $5.20 for -large)
   - Acceptable for Phase 3 budget

2. **High Quality**: MTEB 62.3% is competitive
   - Only 2.3% behind -large
   - Sufficient for enterprise RAG use cases

3. **Standard Dimensions**: 1536d widely used
   - Well-optimized in pgvector
   - Matches industry best practices
   - Easy to find examples and benchmarks

4. **Proven at Scale**: Used by many production systems
   - OpenAI's own ChatGPT uses embeddings
   - Community support and documentation

5. **Low Latency**: ~200ms for batched requests
   - Meets Phase 3 SLA (<500ms per chunk)

### Why Local Model as Fallback?

1. **Development Flexibility**: Work without API keys
2. **Cost Reduction**: Free for testing and non-critical docs
3. **Resilience**: Continue if OpenAI API is down
4. **Vendor Independence**: Reduce lock-in risk

### Why Not `text-embedding-3-large`?

**Diminishing Returns Analysis**:
| Metric | -small | -large | Improvement | Cost Increase |
|--------|--------|--------|-------------|---------------|
| MTEB Score | 62.3% | 64.6% | +2.3% | 6.5x |
| Cost (100k chunks) | $0.80 | $5.20 | - | +$4.40 |
| Storage (100k chunks) | ~590MB | ~1.18GB | 2x | - |
| Query Time | Baseline | +20-30% | Slower | - |

**Conclusion**: 2.3% quality improvement not worth 6.5x cost increase.

---

## Consequences

### Positive Consequences

1. **Low Cost**: $0.80 for 100k chunks (acceptable budget)
2. **High Quality**: RAG retrieval should be accurate and relevant
3. **Standard Config**: 1536d matches pgvector defaults (ADR-010)
4. **Flexibility**: Fallback to local model reduces risk
5. **Fast Development**: API-based (no model management)

### Negative Consequences

1. **API Dependency**: Requires OpenAI API key and internet
   - Mitigation: Local fallback model available
2. **Vendor Lock-In**: Switching models requires re-embedding
   - Mitigation: Embedding cache + abstraction layer
3. **Rate Limits**: 3,000 RPM on OpenAI tier 1
   - Mitigation: Exponential backoff retry logic
4. **Dimension Lock-In**: 1536d locked after first embeddings
   - Mitigation: Document clearly, validate in ADR-010

### Neutral Consequences

1. **Embedding Cache**: Should implement to reduce API calls
2. **Cost Monitoring**: Need telemetry for usage tracking
3. **Batch Processing**: Optimize API calls (batch up to 100 texts)

---

## Implementation Strategy

### Embedding Service Architecture

```python
# services/embedding_service.py
from typing import List, Optional, Literal
import hashlib
from sentence_transformers import SentenceTransformer
import openai

class EmbeddingService:
    def __init__(
        self,
        primary_model: Literal["openai", "local"] = "openai",
        use_cache: bool = True,
        fallback_to_local: bool = True
    ):
        self.primary_model = primary_model
        self.use_cache = use_cache
        self.fallback_to_local = fallback_to_local
        
        # Lazy load local model
        self._local_model = None
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding with cache and fallback."""
        
        # Check cache first
        if self.use_cache:
            cached = await self._check_cache(text)
            if cached:
                return cached
        
        # Try primary model
        try:
            if self.primary_model == "openai":
                embedding = await self._generate_openai(text)
            else:
                embedding = self._generate_local(text)
        except Exception as e:
            if self.fallback_to_local and self.primary_model == "openai":
                print(f"OpenAI failed, falling back to local: {e}")
                embedding = self._generate_local(text)
            else:
                raise
        
        # Save to cache
        if self.use_cache:
            await self._save_to_cache(text, embedding)
        
        return embedding
    
    async def _generate_openai(self, text: str) -> List[float]:
        """Generate with OpenAI text-embedding-3-small."""
        response = await openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding  # 1536 dims
    
    def _generate_local(self, text: str) -> List[float]:
        """Generate with local sentence-transformers."""
        if self._local_model is None:
            self._local_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        embedding = self._local_model.encode(text)
        return embedding.tolist()  # 384 dims
    
    async def _check_cache(self, text: str) -> Optional[List[float]]:
        """Check embedding cache."""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        result = await supabase.table('embedding_cache')\
            .select('embedding')\
            .eq('text_hash', text_hash)\
            .execute()
        
        if result.data:
            return result.data[0]['embedding']
        return None
    
    async def _save_to_cache(self, text: str, embedding: List[float]):
        """Save to embedding cache."""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        await supabase.table('embedding_cache').insert({
            'text_hash': text_hash,
            'embedding': embedding,
            'model': self.primary_model,
            'dimensions': len(embedding)
        }).execute()
```

### Batch Processing Optimization

```python
async def generate_embeddings_batch(
    self,
    texts: List[str],
    batch_size: int = 100
) -> List[List[float]]:
    """Generate embeddings in batches for cost efficiency."""
    
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        
        # Check cache for batch
        cached_embeddings = []
        uncached_texts = []
        
        for text in batch:
            cached = await self._check_cache(text)
            if cached:
                cached_embeddings.append((text, cached))
            else:
                uncached_texts.append(text)
        
        # Generate uncached embeddings
        if uncached_texts:
            if self.primary_model == "openai":
                response = await openai.embeddings.create(
                    model="text-embedding-3-small",
                    input=uncached_texts
                )
                new_embeddings = [d.embedding for d in response.data]
            else:
                new_embeddings = [
                    self._generate_local(text) 
                    for text in uncached_texts
                ]
            
            # Cache new embeddings
            for text, emb in zip(uncached_texts, new_embeddings):
                await self._save_to_cache(text, emb)
            
            embeddings.extend(new_embeddings)
        
        embeddings.extend([emb for _, emb in cached_embeddings])
    
    return embeddings
```

---

## Validation Criteria

Phase 3 VAN QA Mode will validate this decision:

- [ ] **VAN-QA-4**: OpenAI embedding API integration
  - Test: Generate embedding for sample text
  - Success: Valid 1536d vector returned in <500ms
  - Script: `scripts/test_embeddings_api.py`

- [ ] **VAN-QA-4b**: Local model fallback
  - Test: Generate embedding with local model
  - Success: Valid 384d vector returned in <100ms

- [ ] **VAN-QA-4c**: Embedding quality
  - Test: Embed 10 similar documents, verify high similarity
  - Success: Cosine similarity >0.8 for similar docs

- [ ] **VAN-QA-4d**: Cost estimation
  - Test: Calculate cost for 1k, 10k, 100k chunks
  - Success: Costs within budget projections

- [ ] **VAN-QA-4e**: Anthropic availability (optional)
  - Test: Check if Anthropic embeddings API exists in 2026
  - Action: Update ADR if viable alternative

---

## Cost Management

### Monitoring and Budgeting

```python
# utils/embedding_telemetry.py
class EmbeddingTelemetry:
    async def log_embedding_generation(
        self,
        model: str,
        text_length: int,
        token_count: int,
        duration_ms: int,
        cost_usd: float
    ):
        """Log embedding generation for cost tracking."""
        await supabase.table('embedding_telemetry').insert({
            'model': model,
            'text_length': text_length,
            'token_count': token_count,
            'duration_ms': duration_ms,
            'cost_usd': cost_usd,
            'timestamp': datetime.utcnow()
        }).execute()
    
    async def get_monthly_cost(self) -> float:
        """Get total embedding cost for current month."""
        result = await supabase.rpc('sum_embedding_costs_monthly').execute()
        return result.data[0]['total_cost']
```

### Cost Optimization Strategies

1. **Embedding Cache**: Avoid re-embedding identical text
2. **Batch Processing**: Reduce API overhead (1 request for 100 texts)
3. **Incremental Ingestion**: Only embed new/changed documents
4. **Local Fallback**: Use free model for non-critical docs

---

## Migration Path

If switching models in the future:

```python
async def migrate_embeddings(
    from_model: str,
    to_model: str,
    batch_size: int = 100
):
    """
    Re-embed all documents with new model.
    
    Steps:
    1. Create new document_chunks table (temp)
    2. Re-embed all chunks with new model
    3. Swap tables atomically
    4. Rebuild HNSW index
    """
    # Fetch all chunks
    chunks = await supabase.table('document_chunks')\
        .select('id, chunk_text')\
        .execute()
    
    # Re-embed with new model
    new_service = EmbeddingService(primary_model=to_model)
    texts = [c['chunk_text'] for c in chunks.data]
    new_embeddings = await new_service.generate_embeddings_batch(texts)
    
    # Insert to new table
    # ... (implementation details)
```

---

## Related ADRs

- **ADR-010**: pgvector Configuration (defines 1536d expectation)
- **ADR-012**: ACL Data Model (embeddings inherit document permissions)

---

## References

- [OpenAI Embeddings Pricing](https://openai.com/api/pricing/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [Sentence-Transformers](https://www.sbert.net/)

---

**Decision Status**: ✅ DECIDED  
**Validation Status**: ⏳ Pending VAN QA Mode  
**Supersedes**: None  
**Last Updated**: 2026-01-30
