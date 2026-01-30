"""
Phase 3: Context Builder Service

Assembles LLM-ready context from RAG results with citations.
Supports multiple LLM providers (Claude, OpenAI, Gemini).
"""

from dataclasses import dataclass
from typing import List, Dict, Literal, Optional
from services.rag_service import RAGResult


@dataclass
class LLMContext:
    """Represents assembled context for LLM."""
    context_text: str
    sources: List[Dict]
    token_count: int
    truncated: bool


class ContextBuilder:
    """Build LLM-ready context from RAG results."""
    
    def __init__(self, max_tokens: int = 4000):
        """
        Initialize context builder.
        
        Args:
            max_tokens: Maximum tokens for context (default 4000)
        """
        self.max_tokens = max_tokens
    
    def build_context(
        self,
        query: str,
        rag_results: List[RAGResult],
        format: Literal["claude", "openai", "gemini"] = "claude"
    ) -> LLMContext:
        """
        Build LLM context from RAG results.
        
        Args:
            query: Original query
            rag_results: RAG search results
            format: LLM provider format
            
        Returns:
            LLMContext with formatted text and metadata
        """
        if not rag_results:
            return LLMContext(
                context_text="No relevant context found.",
                sources=[],
                token_count=0,
                truncated=False
            )
        
        # Build context parts
        context_parts = ["Relevant Context:\n"]
        sources = []
        total_tokens = 0
        truncated = False
        
        for i, result in enumerate(rag_results, 1):
            chunk_tokens = self._estimate_tokens(result.chunk_text)
            
            # Check token budget
            if total_tokens + chunk_tokens > self.max_tokens:
                truncated = True
                break
            
            # Format based on provider
            if format == "claude":
                context_parts.append(
                    f"[Source {i}: {result.document_title}]\n"
                    f"{result.chunk_text}\n"
                )
            elif format == "openai":
                context_parts.append(
                    f"### Source {i}: {result.document_title}\n"
                    f"{result.chunk_text}\n"
                )
            else:  # gemini
                context_parts.append(
                    f"**Source {i}**: {result.document_title}\n"
                    f"{result.chunk_text}\n"
                )
            
            # Track sources for citations
            sources.append({
                'id': result.document_id,
                'title': result.document_title,
                'similarity': result.similarity_score,
                'chunk_index': result.chunk_index
            })
            
            total_tokens += chunk_tokens
        
        context_text = "\n".join(context_parts)
        
        if truncated:
            context_text += f"\n(Note: Context truncated at {self.max_tokens} tokens)\n"
        
        return LLMContext(
            context_text=context_text,
            sources=sources,
            token_count=total_tokens,
            truncated=truncated
        )
    
    def build_prompt_with_context(
        self,
        task: str,
        context: LLMContext,
        system_message: Optional[str] = None
    ) -> str:
        """
        Build complete prompt with task and context.
        
        Args:
            task: User's task/query
            context: LLMContext from RAG
            system_message: Optional system message
            
        Returns:
            Complete prompt string
        """
        parts = []
        
        if system_message:
            parts.append(system_message)
            parts.append("")
        
        parts.append(f"Task: {task}")
        parts.append("")
        parts.append(context.context_text)
        parts.append("")
        parts.append("Based on the above context, please complete the task.")
        
        return "\n".join(parts)
    
    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Estimate token count (chars / 4 heuristic)."""
        return max(1, len(text) // 4)
    
    def get_sources_summary(self, context: LLMContext) -> str:
        """Generate human-readable sources summary."""
        if not context.sources:
            return "No sources"
        
        lines = ["Sources:"]
        for i, source in enumerate(context.sources, 1):
            lines.append(
                f"  {i}. {source['title']} "
                f"(similarity: {source['similarity']:.2f})"
            )
        
        return "\n".join(lines)
