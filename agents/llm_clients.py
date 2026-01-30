"""
LLM Client Integration

This module provides integration with LLM providers (Claude, Gemini)
for code generation tasks. Per ADR-008, Claude Sonnet 4.5 is primary.

Usage:
    from agents.llm_clients import call_llm_for_plan, call_llm_for_code
"""

import os
import logging
from typing import Optional, Dict, Any

from agents.config import llm_config
from agents.prompts import PLAN_PROMPT_TEMPLATE, CODE_PROMPT_TEMPLATE
from agents.llm_utils import (
    parse_plan_response,
    extract_code_from_response,
    extract_imports
)

logger = logging.getLogger(__name__)

_claude_client = None


async def get_claude_client():
    """Get or create async Claude client."""
    global _claude_client
    
    if _claude_client is None:
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Run: pip install anthropic"
            )
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key == "your-anthropic-api-key-here":
            raise ValueError(
                "ANTHROPIC_API_KEY not configured. Set it in .env file."
            )
        
        _claude_client = AsyncAnthropic(api_key=api_key)
        logger.info("Claude client initialized")
    
    return _claude_client


async def call_llm_for_plan(
    task: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Call LLM to generate execution plan.
    
    Returns:
        Dictionary with plan, requirements, model, tokens
    """
    logger.info(f"Calling LLM for plan: {task[:50]}...")
    
    context_section = f"Context: {context}\n" if context else ""
    prompt = PLAN_PROMPT_TEMPLATE.format(
        task=task,
        context_section=context_section
    )
    
    try:
        client = await get_claude_client()
        
        response = await client.messages.create(
            model=llm_config.primary_model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        tokens = response.usage.input_tokens + response.usage.output_tokens
        
        plan, requirements = parse_plan_response(content)
        
        logger.info(f"Plan generated: {len(plan)} chars")
        
        return {
            "plan": plan,
            "requirements": requirements,
            "model": llm_config.primary_model,
            "tokens": tokens
        }
        
    except Exception as e:
        logger.error(f"LLM plan error: {e}")
        return {
            "plan": f"Create code to: {task}",
            "requirements": [task],
            "model": "fallback",
            "tokens": 0
        }


async def call_llm_for_code(
    task: str,
    plan: str,
    language: str = "python",
    feedback: Optional[str] = None
) -> Dict[str, Any]:
    """
    Call LLM to generate code.
    
    Returns:
        Dictionary with code, imports, model, tokens
    """
    iteration_msg = "(retry with feedback)" if feedback else "(first attempt)"
    logger.info(f"Calling LLM for code {iteration_msg}")
    
    feedback_section = ""
    if feedback:
        feedback_section = f"""
IMPORTANT - Previous attempt had errors:
{feedback}

Please fix these errors in your new code.
"""
    
    prompt = CODE_PROMPT_TEMPLATE.format(
        task=task,
        plan=plan,
        language=language,
        feedback_section=feedback_section
    )
    
    try:
        client = await get_claude_client()
        
        response = await client.messages.create(
            model=llm_config.primary_model,
            max_tokens=llm_config.max_tokens,
            temperature=llm_config.temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        tokens = response.usage.input_tokens + response.usage.output_tokens
        
        code = extract_code_from_response(content)
        imports = extract_imports(code)
        
        logger.info(f"Code generated: {len(code)} chars")
        
        return {
            "code": code,
            "imports": imports,
            "model": llm_config.primary_model,
            "tokens": tokens
        }
        
    except Exception as e:
        logger.error(f"LLM code error: {e}")
        return {
            "code": "",
            "imports": [],
            "model": "error",
            "tokens": 0
        }
