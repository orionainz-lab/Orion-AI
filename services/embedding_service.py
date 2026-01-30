"""
Phase 3: Embedding Service

Generates vector embeddings for text chunks.
Primary: OpenAI text-embedding-3-small (ADR-011)
Fallback: Local sentence-transformers (all-MiniLM-L6-v2)
"""

import os
import hashlib
import asyncio
from typing import List, Optional, Literal
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate vector embeddings with caching and fallback."""
    
    def __init__(
        self,
        supabase_client,
        primary_model: Literal["openai", "local"] = "openai",
        use_cache: bool = True,
        fallback_to_local: bool = True
    ):
        """
        Initialize embedding service.
        
        Args:
            supabase_client: Supabase client for cache access
            primary_model: 'openai' or 'local'
            use_cache: Whether to cache embeddings
            fallback_to_local: Fall back to local if API fails
        """
        self.supabase = supabase_client
        self.primary_model = primary_model
        self.use_cache = use_cache
        self.fallback_to_local = fallback_to_local
        
        # Lazy load models
        self._openai_client = None
        self._local_model = None
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate single embedding with cache and fallback.
        
        Args:
            text: Text to embed
            
        Returns:
            1536d vector (OpenAI) or 384d (local)
        """
        # Check cache first
        if self.use_cache:
            cached = await self._check_cache(text)
            if cached:
                logger.debug(f"Cache hit for text hash")
                return cached
        
        # Generate embedding
        try:
            if self.primary_model == "openai":
                embedding = await self._generate_openai(text)
            else:
                embedding = self._generate_local(text)
        except Exception as e:
            logger.warning(f"Primary model failed: {e}")
            
            if self.fallback_to_local and self.primary_model == "openai":
                logger.info("Falling back to local model")
                embedding = self._generate_local(text)
            else:
                raise
        
        # Save to cache
        if self.use_cache:
            await self._save_to_cache(text, embedding)
        
        return embedding
    
    async def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings in batches for cost efficiency.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for API calls (default 100)
            
        Returns:
            List of embeddings (same order as input)
        """
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} texts)")
            
            # Check cache for batch
            batch_embeddings = []
            
            for text in batch:
                if self.use_cache:
                    cached = await self._check_cache(text)
                    if cached:
                        batch_embeddings.append(cached)
                        continue
                
                # Generate uncached embeddings
                embedding = await self.generate_embedding(text)
                batch_embeddings.append(embedding)
            
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    async def _generate_openai(self, text: str) -> List[float]:
        """Generate embedding with OpenAI API."""
        if self._openai_client is None:
            import openai
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            self._openai_client = openai.OpenAI(api_key=api_key)
        
        response = self._openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        
        return response.data[0].embedding
    
    def _generate_local(self, text: str) -> List[float]:
        """Generate embedding with local model."""
        if self._local_model is None:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading local model: all-MiniLM-L6-v2")
            self._local_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        embedding = self._local_model.encode(text)
        return embedding.tolist()
    
    async def _check_cache(self, text: str) -> Optional[List[float]]:
        """Check if embedding exists in cache."""
        text_hash = self._text_hash(text)
        
        try:
            result = self.supabase.table('embedding_cache')\
                .select('embedding, dimensions')\
                .eq('text_hash', text_hash)\
                .execute()
            
            if result.data:
                # Update last_used and use_count
                await self._update_cache_stats(text_hash)
                return result.data[0]['embedding']
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
        
        return None
    
    async def _save_to_cache(self, text: str, embedding: List[float]):
        """Save embedding to cache."""
        text_hash = self._text_hash(text)
        
        try:
            self.supabase.table('embedding_cache').insert({
                'text_hash': text_hash,
                'embedding': embedding,
                'model': self.primary_model,
                'dimensions': len(embedding),
                'use_count': 1
            }).execute()
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")
    
    async def _update_cache_stats(self, text_hash: str):
        """Update cache usage statistics."""
        try:
            self.supabase.rpc('increment_cache_use', {
                'hash': text_hash
            }).execute()
        except Exception:
            pass  # Non-critical operation
    
    @staticmethod
    def _text_hash(text: str) -> str:
        """Generate SHA-256 hash for cache key."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
