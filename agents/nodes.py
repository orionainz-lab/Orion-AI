"""
LangGraph Reasoning Nodes

This module defines the four reasoning nodes for code generation:
1. Plan Node: Analyze task and create execution plan
2. Generate Node: Generate code based on plan
3. Verify Node: Verify code syntax using AST
4. Correct Node: Generate correction feedback from errors

Usage:
    from agents.nodes import plan_node, generate_node, verify_node, correct_node
"""

import logging
from typing import Callable

from agents.state import CodeGenerationState
from verification.ast_verifier import (
    verify_python_syntax,
    generate_error_feedback,
    extract_correction_hints
)

logger = logging.getLogger(__name__)


async def plan_node(state: CodeGenerationState) -> CodeGenerationState:
    """Analyze task and create execution plan with RAG context."""
    logger.info(f"PLAN NODE: {state.get('task', 'N/A')[:50]}...")
    
    from agents.llm_clients import call_llm_for_plan
    
    task = state.get("task", "")
    context = state.get("context", "")
    user_id = state.get("user_id")
    rag_enabled = state.get("rag_enabled", True)
    
    # Phase 3: Retrieve relevant context via RAG
    if rag_enabled and user_id:
        try:
            logger.info("Retrieving RAG context...")
            rag_context = await _retrieve_rag_context(task, user_id)
            
            if rag_context:
                state["rag_context"] = rag_context.context_text
                state["rag_sources"] = rag_context.sources
                # Append RAG context to existing context
                if context:
                    context = f"{context}\n\n{rag_context.context_text}"
                else:
                    context = rag_context.context_text
                logger.info(f"RAG context retrieved: {len(rag_context.sources)} sources")
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")
    
    try:
        plan_result = await call_llm_for_plan(task, context)
        state["plan"] = plan_result.get("plan", "")
        state["requirements"] = plan_result.get("requirements", [])
        state["model_used"] = plan_result.get("model", "unknown")
        state["tokens_used"] = state.get("tokens_used", 0) + plan_result.get("tokens", 0)
        logger.info(f"PLAN NODE complete: {len(state['plan'])} chars")
    except Exception as e:
        logger.error(f"PLAN NODE error: {e}")
        state["plan"] = f"Create code for: {task}"
        state["requirements"] = [task]
    
    return state


async def _retrieve_rag_context(task: str, user_id: str):
    """
    Retrieve relevant context via RAG (Phase 3 integration).
    
    This is a helper function that initializes RAG services
    and performs semantic search.
    """
    import os
    from supabase import create_client
    from services.rag_service import RAGService
    from services.embedding_service import EmbeddingService
    from services.context_builder import ContextBuilder
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        logger.warning("Supabase credentials not configured, skipping RAG")
        return None
    
    # Initialize services
    supabase = create_client(supabase_url, supabase_key)
    embedding_service = EmbeddingService(supabase, primary_model="openai", fallback_to_local=True)
    rag_service = RAGService(supabase, embedding_service, similarity_threshold=0.7)
    context_builder = ContextBuilder(max_tokens=4000)
    
    # Query for relevant context
    rag_query = f"How to {task}?"
    rag_results = await rag_service.query(rag_query, user_id)
    
    if not rag_results:
        return None
    
    # Build context
    return context_builder.build_context(rag_query, rag_results, format="claude")


async def generate_node(state: CodeGenerationState) -> CodeGenerationState:
    """Generate code based on plan."""
    iteration = state.get("iteration", 0)
    logger.info(f"GENERATE NODE: iteration {iteration + 1}")
    
    from agents.llm_clients import call_llm_for_code
    
    task = state.get("task", "")
    plan = state.get("plan", "")
    language = state.get("language", "python")
    feedback = state.get("feedback", "")
    
    try:
        code_result = await call_llm_for_code(
            task=task, plan=plan, language=language, feedback=feedback
        )
        state["code"] = code_result.get("code", "")
        state["imports"] = code_result.get("imports", [])
        state["tokens_used"] = state.get("tokens_used", 0) + code_result.get("tokens", 0)
        logger.info(f"GENERATE NODE complete: {len(state['code'])} chars")
    except Exception as e:
        logger.error(f"GENERATE NODE error: {e}")
        state["code"] = ""
        state["errors"] = [{"line": 0, "message": f"Generation failed: {e}"}]
    
    state["iteration"] = iteration + 1
    return state


async def verify_node(state: CodeGenerationState) -> CodeGenerationState:
    """Verify code syntax using AST."""
    logger.info("VERIFY NODE: checking syntax...")
    
    code = state.get("code", "")
    result = verify_python_syntax(code)
    
    state["is_valid"] = result["is_valid"]
    state["errors"] = result["errors"]
    state["warnings"] = result.get("warnings", [])
    
    if result["is_valid"]:
        logger.info("VERIFY NODE: code is VALID")
    else:
        logger.warning(f"VERIFY NODE: INVALID ({len(result['errors'])} errors)")
    
    return state


async def correct_node(state: CodeGenerationState) -> CodeGenerationState:
    """Generate correction feedback from errors."""
    logger.info("CORRECT NODE: generating feedback...")
    
    errors = state.get("errors", [])
    state["feedback"] = generate_error_feedback(errors)
    state["correction_hints"] = extract_correction_hints(errors)
    
    logger.info(f"CORRECT NODE complete: {len(state['correction_hints'])} hints")
    return state


def should_continue(state: CodeGenerationState) -> str:
    """Routing function: END if valid or max iterations, else correct."""
    is_valid = state.get("is_valid", False)
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 3)
    
    if is_valid:
        logger.info(f"ROUTING: END (valid, {iteration} iterations)")
        return "end"
    elif iteration >= max_iterations:
        logger.warning(f"ROUTING: END (max iterations {max_iterations})")
        return "end"
    else:
        logger.info(f"ROUTING: CORRECT ({iteration}/{max_iterations})")
        return "correct"


# Node registry
NODE_REGISTRY: dict[str, Callable] = {
    "plan": plan_node,
    "generate": generate_node,
    "verify": verify_node,
    "correct": correct_node
}


def get_node(name: str) -> Callable:
    """Get a node function by name."""
    if name not in NODE_REGISTRY:
        raise ValueError(f"Unknown node: {name}")
    return NODE_REGISTRY[name]
