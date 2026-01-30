# ADR-009: AST Verification Scope

**Status**: DECIDED  
**Date**: 2026-01-30  
**Deciders**: Development Team  
**Phase**: Phase 2 - The Reliable Brain

---

## Context

Phase 2 needs code verification to detect errors in AI-generated code. We must decide how deep verification should go: syntax only, type checking, or full static analysis.

## Decision

**Decision**: Start with **syntax-only verification** using Python's built-in `ast.parse()` in Phase 2.0. Add optional type checking (mypy) in Phase 2.1 as a configurable enhancement.

## Options Considered

### Option 1: Syntax Only (ast.parse) - SELECTED for Phase 2.0

```python
import ast

def verify_syntax(code: str) -> dict:
    try:
        ast.parse(code)
        return {"is_valid": True, "errors": []}
    except SyntaxError as e:
        return {"is_valid": False, "errors": [extract_error(e)]}
```

**Pros**: Fast (<5ms), no dependencies, 100% reliable  
**Cons**: Misses type errors, logic bugs

### Option 2: Syntax + Type Checking (mypy)

```python
from mypy import api

def verify_with_types(code: str) -> dict:
    result = api.run(["--ignore-missing-imports", code_file])
    # Parse mypy output...
```

**Pros**: Catches type errors  
**Cons**: Slow (100-500ms), more dependencies, false positives

### Option 3: Full Static Analysis (pylint/ruff)

```python
import subprocess
result = subprocess.run(["ruff", "check", code_file], ...)
```

**Pros**: Catches style issues, potential bugs  
**Cons**: Very slow (1-5s), opinionated rules, noise

## Rationale

### Phase 2.0: Syntax Only

- Covers 70%+ of AI-generated errors (syntax issues)
- Validated in VAN QA: 5ms for 400 lines
- Zero external dependencies
- Clear, actionable errors

### Phase 2.1: Optional Type Checking

- Add `--enable-type-checking` config flag
- Use mypy for Python files with type hints
- Catch additional 15-20% of errors

### Future: Consider Ruff for Style

- Only for production code review
- Too noisy for AI generation feedback

## Verification Levels

| Level | Method | Speed | Coverage | Phase |
|-------|--------|-------|----------|-------|
| **1. Syntax** | `ast.parse()` | <5ms | 70% | 2.0 |
| **2. Types** | mypy | 100-500ms | 85% | 2.1 |
| **3. Style** | ruff | 500-2000ms | 95% | Future |

## Implementation

### Phase 2.0 Verifier

```python
import ast

@activity.defn
async def verify_python_syntax(code: str) -> dict:
    """Verify Python code syntax using AST parser."""
    try:
        tree = ast.parse(code)
        return {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
    except SyntaxError as e:
        return {
            "is_valid": False,
            "errors": [{
                "line": e.lineno,
                "offset": e.offset,
                "message": str(e.msg),
                "text": e.text
            }],
            "warnings": []
        }
```

### Error Feedback Generation

```python
def generate_error_feedback(errors: list[dict]) -> str:
    """Convert errors to actionable LLM feedback."""
    feedback_lines = ["The code has the following syntax errors:"]
    for error in errors:
        feedback_lines.append(f"- Line {error['line']}: {error['message']}")
    feedback_lines.append("\nPlease fix these errors and regenerate.")
    return "\n".join(feedback_lines)
```

## Consequences

### Positive

- Fast verification (<5ms) enables tight feedback loop
- No external dependencies for core functionality
- Clear path to enhanced verification

### Negative

- Won't catch type errors in Phase 2.0
- Won't catch logic bugs (expected - out of scope)

### Mitigations

- Most AI syntax errors are caught by ast.parse
- Type checking available as opt-in for Phase 2.1
- Logic bugs require testing, not static analysis

## Validation

VAN QA Tests (`scripts/test_ast_parsing.py`):
- 7/7 valid code samples parsed correctly
- 7/7 invalid code samples detected correctly
- 7/7 edge cases handled correctly
- 400 lines parsed in 4.9ms

**Result**: AST verification is sufficient for Phase 2.0 ✅

## Environment Variables

```ini
# Verification Settings
VERIFICATION_LEVEL=syntax  # Options: syntax, types, full
VERIFICATION_TIMEOUT_MS=5000
```

---

**Related ADRs**: ADR-007 (LangGraph integration)  
**Supersedes**: None
