"""
Phase 2: Code Verification Module

This module provides code verification capabilities for AI-generated code,
starting with Python AST syntax verification (Phase 2.0).

Components:
    - ast_verifier: Python syntax verification using built-in ast module

Verification Levels (per ADR-009):
    - Level 1 (syntax): ast.parse() - <5ms, 70% coverage (Phase 2.0)
    - Level 2 (types): mypy integration - 100-500ms (Phase 2.1)
    - Level 3 (full): ruff/pylint - 500-2000ms (Future)

Usage:
    from verification.ast_verifier import verify_python_syntax
    
    result = verify_python_syntax("def hello(): print('world')")
    if result["is_valid"]:
        print("Code is syntactically valid!")
    else:
        for error in result["errors"]:
            print(f"Line {error['line']}: {error['message']}")
"""

__version__ = "0.2.0"
__phase__ = "Phase 2: The Reliable Brain"
