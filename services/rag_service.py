"""
Phase 3: RAG Service

Permissions-aware Retrieval-Augmented Generation.
Performs vector similarity search with RLS enforcement.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class RAGResult:
    """Represents a single RAG search result."""
    id: str
    document_id: str
    document_title: str
    chunk_text: str
    chunk_index: int
    similarity_score: float
    metadata: dict


class RAGService:
    """Retrieve relevant context for LLM with permission enforcement."""
    
    def __init__(
        self,
        supabase_client,
        embedding_service,
        similarity_threshold: float = 0.7,
        max_results: int = 10
    ):
        """
        Initialize RAG service.
        
        Args:
            supabase_client: Supabase client (with user JWT for RLS)
            embedding_service: EmbeddingService instance
            similarity_threshold: Minimum similarity score (0-1)
            max_results: Maximum results to return
        """
        self.supabase = supabase_client
        self.embedding_service = embedding_service
        self.similarity_threshold = similarity_threshold
        self.max_results = max_results
    
    async def query(
        self,
        query_text: str,
        user_id: str,
        filters: Optional[Dict] = None
    ) -> List[RAGResult]:
        """
        Execute permissions-aware RAG query.
        
        Args:
            query_text: User's query
            user_id: User ID for audit logging
            filters: Optional filters (document_type, team_id, etc.)
            
        Returns:
            List of RAGResult objects (RLS-filtered)
        """
        start_time = time.time()
        
        # 1. Generate query embedding
        query_vector = await self.embedding_service.generate_embedding(query_text)
        
        # 2. Vector search with RLS enforcement
        results = await self._vector_search(query_vector, filters)
        
        # 3. Convert to RAGResult objects
        rag_results = []
        for row in results:
            if row['similarity'] >= self.similarity_threshold:
                rag_results.append(RAGResult(
                    id=row['id'],
                    document_id=row['document_id'],
                    document_title=row['document_title'],
                    chunk_text=row['chunk_text'],
                    chunk_index=row['chunk_index'],
                    similarity_score=row['similarity'],
                    metadata={}
                ))
        
        # 4. Limit results
        top_results = rag_results[:self.max_results]
        
        # 5. Log query for audit
        duration_ms = int((time.time() - start_time) * 1000)
        await self._log_rag_query(query_text, user_id, top_results, duration_ms)
        
        logger.info(
            f"RAG query: '{query_text[:50]}...' → {len(top_results)} results "
            f"({duration_ms}ms)"
        )
        
        return top_results
    
    async def _vector_search(
        self,
        query_vector: List[float],
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Execute vector similarity search.
        
        Uses match_documents() function (RLS automatically enforced).
        """
        try:
            result = self.supabase.rpc('match_documents', {
                'query_embedding': query_vector,
                'match_threshold': self.similarity_threshold,
                'match_count': self.max_results * 2  # Get more, filter later
            }).execute()
            
            return result.data
        
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def _log_rag_query(
        self,
        query_text: str,
        user_id: str,
        results: List[RAGResult],
        duration_ms: int
    ):
        """Log RAG query to process_events for audit."""
        try:
            self.supabase.table('process_events').insert({
                'event_type': 'rag_query',
                'event_name': 'semantic_search',
                'user_id': user_id,
                'input_data': {'query': query_text},
                'output_data': {
                    'result_count': len(results),
                    'document_ids': [r.document_id for r in results],
                    'avg_similarity': (
                        sum(r.similarity_score for r in results) / len(results)
                        if results else 0
                    )
                },
                'status': 'completed',
                'duration_ms': duration_ms
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to log RAG query: {e}")
