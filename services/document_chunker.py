"""
Phase 3: Document Chunker Service

Splits documents into optimal chunks for embedding.
Strategy: Recursive character-based splitting with paragraph boundaries.
Target: 500 tokens (~2000 chars), 50 token overlap (~200 chars)
"""

from dataclasses import dataclass
from typing import List, Optional
import re


@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document."""
    text: str
    chunk_index: int
    token_count: int
    metadata: dict


class DocumentChunker:
    """Chunks documents for embedding and vector search."""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None
    ):
        """
        Initialize chunker with size and overlap settings.
        
        Args:
            chunk_size: Target tokens per chunk (default 500)
            chunk_overlap: Overlap tokens between chunks (default 50)
            separators: Text separators to split on (paragraphs, sentences)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " "]
    
    def chunk_text(self, text: str, document_id: str) -> List[DocumentChunk]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Full document text
            document_id: Document UUID for metadata
            
        Returns:
            List of DocumentChunk objects
        """
        if not text or not text.strip():
            return []
        
        # Split text recursively using separators
        chunks_text = self._recursive_split(text)
        
        # Create DocumentChunk objects with metadata
        chunks = []
        for i, chunk_text in enumerate(chunks_text):
            chunk = DocumentChunk(
                text=chunk_text,
                chunk_index=i,
                token_count=self.estimate_tokens(chunk_text),
                metadata={
                    'document_id': document_id,
                    'char_count': len(chunk_text),
                    'separator_used': self._detect_separator(chunk_text)
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _recursive_split(self, text: str) -> List[str]:
        """
        Recursively split text using separators.
        
        Tries separators in order (paragraphs → sentences → words)
        until chunks are small enough.
        """
        target_chars = self.chunk_size * 4  # Rough char estimate
        overlap_chars = self.chunk_overlap * 4
        
        # Base case: text is small enough
        if len(text) <= target_chars:
            return [text] if text.strip() else []
        
        # Try each separator
        for separator in self.separators:
            splits = text.split(separator)
            
            # Check if separator produces useful splits
            if len(splits) > 1:
                chunks = self._merge_splits(
                    splits, 
                    separator, 
                    target_chars, 
                    overlap_chars
                )
                return chunks
        
        # Fallback: hard split by characters
        return self._hard_split(text, target_chars, overlap_chars)
    
    def _merge_splits(
        self, 
        splits: List[str], 
        separator: str,
        target_size: int,
        overlap: int
    ) -> List[str]:
        """Merge splits into chunks of target size with overlap."""
        chunks = []
        current_chunk = []
        current_size = 0
        
        for split in splits:
            split_size = len(split)
            
            if current_size + split_size > target_size and current_chunk:
                # Save current chunk
                chunks.append(separator.join(current_chunk))
                
                # Start new chunk with overlap (keep last splits)
                current_chunk = self._get_overlap_splits(current_chunk, overlap)
                current_size = sum(len(s) for s in current_chunk)
            
            current_chunk.append(split)
            current_size += split_size
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(separator.join(current_chunk))
        
        return chunks
    
    def _get_overlap_splits(self, splits: List[str], overlap: int) -> List[str]:
        """Get splits for overlap window."""
        overlap_splits = []
        overlap_size = 0
        for s in reversed(splits):
            if overlap_size + len(s) <= overlap:
                overlap_splits.insert(0, s)
                overlap_size += len(s)
            else:
                break
        return overlap_splits
    
    def _hard_split(self, text: str, target_size: int, overlap: int) -> List[str]:
        """Hard split by characters (last resort)."""
        chunks = []
        start = 0
        
        while start < len(text):
            chunk = text[start:start + target_size]
            if chunk.strip():
                chunks.append(chunk)
            start += target_size - overlap
        
        return chunks
    
    def _detect_separator(self, text: str) -> str:
        """Detect which separator was likely used."""
        for sep, name in [("\n\n", "paragraph"), ("\n", "newline"), (". ", "sentence")]:
            if sep in text:
                return name
        return "word"
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count (chars / 4 heuristic).
        
        This is approximate. For exact counts, use tiktoken.
        """
        return max(1, len(text) // 4)
    
    def get_chunk_stats(self, chunks: List[DocumentChunk]) -> dict:
        """Get statistics about chunked document."""
        if not chunks:
            return {'total_chunks': 0, 'total_tokens': 0, 'avg_tokens_per_chunk': 0, 'min_tokens': 0, 'max_tokens': 0}
        
        token_counts = [c.token_count for c in chunks]
        return {
            'total_chunks': len(chunks),
            'total_tokens': sum(token_counts),
            'avg_tokens_per_chunk': sum(token_counts) / len(token_counts),
            'min_tokens': min(token_counts),
            'max_tokens': max(token_counts)
        }
