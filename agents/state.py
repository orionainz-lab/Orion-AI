"""
State Schema for LangGraph Code Generation

This module defines the TypedDict state schema used by LangGraph
for the Plan -> Generate -> Verify -> Correct reasoning loop.

The state flows through each node, accumulating:
1. Plan: Task analysis and requirements
2. Generate: Generated code
3. Verify: AST verification results
4. Correct: Error feedback (if invalid)

Usage:
    from agents.state import CodeGenerationState
    
    initial_state: CodeGenerationState = {
        "task": "Create a sorting function",
        "language": "python",
        ...
    }
"""

from typing import TypedDict, Literal, Optional, List, Dict, Any


class CodeGenerationState(TypedDict, total=False):
    """
    State for code generation reasoning loop.
    
    All fields are optional (total=False) to allow partial state
    initialization at different stages of the reasoning loop.
    """
    
    # ========== INPUT ==========
    task: str
    """User's task description (e.g., 'Create a function that sorts a list')"""
    
    language: Literal["python", "typescript"]
    """Target programming language"""
    
    context: Optional[str]
    """Additional context or constraints for code generation"""
    
    # ========== PLANNING ==========
    plan: str
    """High-level execution plan from Plan node"""
    
    requirements: List[str]
    """Extracted functional requirements from the task"""
    
    # ========== GENERATION ==========
    code: str
    """Generated code from Generate node"""
    
    imports: List[str]
    """List of required imports identified"""
    
    # ========== VERIFICATION ==========
    is_valid: bool
    """True if code passes AST verification"""
    
    errors: List[Dict[str, Any]]
    """List of syntax errors: [{line, offset, message, text}]"""
    
    warnings: List[Dict[str, Any]]
    """List of non-fatal warnings"""
    
    # ========== CORRECTION ==========
    feedback: str
    """Error feedback string for LLM to fix issues"""
    
    correction_hints: List[str]
    """Specific hints for fixing errors"""
    
    # ========== LOOP CONTROL ==========
    iteration: int
    """Current iteration count (0-based)"""
    
    max_iterations: int
    """Maximum iterations before returning partial result (default: 3)"""
    
    # ========== METADATA ==========
    model_used: str
    """LLM model name used for generation"""
    
    tokens_used: int
    """Total token count for this reasoning loop"""
    
    reasoning_time_ms: int
    """Total time in milliseconds for reasoning loop"""


def create_initial_state(
    task: str,
    language: str = "python",
    context: Optional[str] = None,
    max_iterations: int = 3
) -> CodeGenerationState:
    """
    Create a properly initialized state for code generation.
    
    Args:
        task: The code generation task description
        language: Target language (default: python)
        context: Optional additional context
        max_iterations: Maximum correction iterations (default: 3)
    
    Returns:
        Initialized CodeGenerationState ready for LangGraph
    """
    return CodeGenerationState(
        # Input
        task=task,
        language=language,
        context=context,
        # Planning
        plan="",
        requirements=[],
        # Generation
        code="",
        imports=[],
        # Verification
        is_valid=False,
        errors=[],
        warnings=[],
        # Correction
        feedback="",
        correction_hints=[],
        # Loop control
        iteration=0,
        max_iterations=max_iterations,
        # Metadata
        model_used="",
        tokens_used=0,
        reasoning_time_ms=0
    )


def get_state_summary(state: CodeGenerationState) -> str:
    """
    Get a human-readable summary of the current state.
    
    Useful for logging and debugging.
    """
    lines = [
        f"Task: {state.get('task', 'N/A')[:50]}...",
        f"Language: {state.get('language', 'N/A')}",
        f"Iteration: {state.get('iteration', 0)}/{state.get('max_iterations', 3)}",
        f"Valid: {state.get('is_valid', False)}",
        f"Errors: {len(state.get('errors', []))}",
        f"Code Length: {len(state.get('code', ''))} chars",
    ]
    return " | ".join(lines)
