"""
Python AST Syntax Verification

This module provides syntax verification for Python code using
the built-in ast module. Per ADR-009, syntax-only verification
is used in Phase 2.0.

Usage:
    from verification.ast_verifier import verify_python_syntax
    result = verify_python_syntax(code)
"""

import ast
from typing import Dict, List, Any


def verify_python_syntax(code: str) -> Dict[str, Any]:
    """
    Verify Python code syntax using AST parser.
    
    Returns:
        Dictionary with is_valid, errors, warnings, ast_dump
    """
    if not code or not code.strip():
        return {
            "is_valid": False,
            "errors": [{"line": 0, "offset": 0, "message": "Empty code", "text": None}],
            "warnings": [],
            "ast_dump": None
        }
    
    try:
        tree = ast.parse(code)
        ast_dump = ast.dump(tree, indent=2)[:200]
        return {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "ast_dump": ast_dump
        }
    except SyntaxError as e:
        return {
            "is_valid": False,
            "errors": [_extract_syntax_error(e)],
            "warnings": [],
            "ast_dump": None
        }
    except Exception as e:
        return {
            "is_valid": False,
            "errors": [{"line": 0, "offset": 0, "message": f"Error: {e}", "text": None}],
            "warnings": [],
            "ast_dump": None
        }


def _extract_syntax_error(e: SyntaxError) -> Dict[str, Any]:
    """Extract structured info from SyntaxError."""
    return {
        "line": e.lineno or 0,
        "offset": e.offset or 0,
        "message": str(e.msg) if hasattr(e, 'msg') else str(e),
        "text": e.text.strip() if e.text else None
    }


def generate_error_feedback(errors: List[Dict[str, Any]]) -> str:
    """Convert errors to actionable LLM feedback."""
    if not errors:
        return ""
    
    lines = ["The code has the following syntax errors:"]
    for error in errors:
        line_num = error.get("line", 0)
        message = error.get("message", "Unknown error")
        text = error.get("text")
        
        if line_num:
            lines.append(f"- Line {line_num}: {message}")
        else:
            lines.append(f"- {message}")
        if text:
            lines.append(f"  Code: {text}")
    
    lines.append("")
    lines.append("Please fix these errors and regenerate the code.")
    return "\n".join(lines)


def extract_correction_hints(errors: List[Dict[str, Any]]) -> List[str]:
    """Extract correction hints from errors."""
    hints = []
    
    for error in errors:
        msg = error.get("message", "").lower()
        
        if "expected ':'" in msg or "missing ':'" in msg:
            hints.append("Add colon after function/class definition")
        elif "expected ')'" in msg or "missing ')'" in msg:
            hints.append("Check for unmatched parentheses")
        elif "indentation" in msg:
            hints.append("Fix indentation (use 4 spaces)")
        elif "unterminated string" in msg:
            hints.append("Close string with matching quote")
        elif "unexpected indent" in msg:
            hints.append("Remove extra indentation")
        elif "eof" in msg:
            hints.append("Code incomplete, check for missing brackets")
        else:
            hints.append(f"Fix: {error.get('message', 'syntax error')}")
    
    return hints


def verify_and_feedback(code: str) -> Dict[str, Any]:
    """Verify code and generate feedback in one call."""
    result = verify_python_syntax(code)
    
    if not result["is_valid"]:
        result["feedback"] = generate_error_feedback(result["errors"])
        result["correction_hints"] = extract_correction_hints(result["errors"])
    else:
        result["feedback"] = ""
        result["correction_hints"] = []
    
    return result
