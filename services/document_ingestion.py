"""
Phase 3: Document Ingestion Service

End-to-end pipeline: Document → Chunks → Embeddings → Supabase
Orchestrates chunker and embedding services.
"""

from typing import Optional, Dict
import logging
from services.document_chunker import DocumentChunker
from services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class DocumentIngestionService:
    """Orchestrate document ingestion pipeline."""
    
    def __init__(
        self,
        supabase_client,
        chunker: Optional[DocumentChunker] = None,
        embedding_service: Optional[EmbeddingService] = None
    ):
        """
        Initialize ingestion service.
        
        Args:
            supabase_client: Supabase client
            chunker: DocumentChunker (default if None)
            embedding_service: EmbeddingService (default if None)
        """
        self.supabase = supabase_client
        self.chunker = chunker or DocumentChunker()
        self.embedding_service = embedding_service or EmbeddingService(
            supabase_client,
            primary_model="openai",
            use_cache=True,
            fallback_to_local=True
        )
    
    async def ingest_document(
        self,
        title: str,
        content: str,
        created_by: str,
        document_type: str = 'guide',
        team_id: Optional[str] = None,
        visibility: str = 'private',
        metadata: Optional[Dict] = None
    ) -> dict:
        """
        Ingest document into vector database.
        
        Steps:
        1. Insert document record
        2. Chunk document text
        3. Generate embeddings for chunks
        4. Insert chunks with embeddings
        5. Return statistics
        
        Args:
            title: Document title
            content: Full document text
            created_by: User ID who created document
            document_type: Type (guide, policy, code, chat_history)
            team_id: Optional team ID for team visibility
            visibility: Access level (private, team, org, public)
            metadata: Optional metadata dictionary
            
        Returns:
            Statistics dict with document_id, chunk count, etc.
        """
        logger.info(f"Ingesting document: {title}")
        
        # 1. Insert document
        doc_result = self.supabase.table('documents').insert({
            'title': title,
            'content': content,
            'document_type': document_type,
            'created_by': created_by,
            'team_id': team_id,
            'visibility': visibility,
            'metadata': metadata or {}
        }).execute()
        
        document_id = doc_result.data[0]['id']
        logger.info(f"Document created: {document_id}")
        
        # 2. Chunk document
        chunks = self.chunker.chunk_text(content, document_id)
        logger.info(f"Created {len(chunks)} chunks")
        
        if not chunks:
            logger.warning("No chunks created (empty document?)")
            return {
                'document_id': document_id,
                'chunks_created': 0,
                'embeddings_generated': 0,
                'total_tokens': 0
            }
        
        # 3. Generate embeddings (batch)
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = await self.embedding_service.generate_embeddings_batch(
            chunk_texts
        )
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # 4. Insert chunks with embeddings
        chunk_records = []
        for chunk, embedding in zip(chunks, embeddings):
            chunk_records.append({
                'document_id': document_id,
                'chunk_text': chunk.text,
                'chunk_index': chunk.chunk_index,
                'embedding': embedding,
                'token_count': chunk.token_count,
                'metadata': chunk.metadata
            })
        
        self.supabase.table('document_chunks').insert(chunk_records).execute()
        logger.info(f"Inserted {len(chunk_records)} chunks")
        
        # 5. Return statistics
        stats = self.chunker.get_chunk_stats(chunks)
        
        return {
            'document_id': document_id,
            'chunks_created': len(chunks),
            'embeddings_generated': len(embeddings),
            'total_tokens': stats['total_tokens'],
            'avg_tokens_per_chunk': stats['avg_tokens_per_chunk']
        }
    
    async def ingest_documents_batch(
        self,
        documents: list[dict],
        progress_callback: Optional[callable] = None
    ) -> dict:
        """
        Ingest multiple documents.
        
        Args:
            documents: List of document dicts (title, content, created_by, ...)
            progress_callback: Optional function called after each document
            
        Returns:
            Summary statistics
        """
        total_docs = len(documents)
        total_chunks = 0
        total_embeddings = 0
        errors = []
        
        for i, doc in enumerate(documents):
            try:
                stats = await self.ingest_document(**doc)
                total_chunks += stats['chunks_created']
                total_embeddings += stats['embeddings_generated']
                
                if progress_callback:
                    progress_callback(i + 1, total_docs, doc['title'])
                
            except Exception as e:
                logger.error(f"Failed to ingest '{doc.get('title')}': {e}")
                errors.append({'title': doc.get('title'), 'error': str(e)})
        
        return {
            'total_documents': total_docs,
            'successful': total_docs - len(errors),
            'failed': len(errors),
            'total_chunks': total_chunks,
            'total_embeddings': total_embeddings,
            'errors': errors
        }
