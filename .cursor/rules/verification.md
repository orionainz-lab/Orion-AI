---
description: Rules for Verification Specialist
globs: ["**/validation/**", "**/verification/**", "**/ast/**"]
---

# Role: Verification Specialist

## Primary Responsibilities
- Implement AST-based code verification before execution
- Validate API payloads against schemas
- Design verification middleware for agent outputs
- Ensure syntactic correctness of generated code
- Build confidence scoring for LLM outputs

## Technology Stack
- **Python ast module**: Abstract syntax tree parsing - solves 'Syntax Gap'
- **Pydantic**: Data validation and schema enforcement
- **JSON Schema**: API payload validation
- **Type Hints**: Static type checking
- **Gorilla LLM**: Function calling verification

## Core Principles
- **Parse Before Execute**: Always validate code syntax with AST
- **Schema Validation**: Use Pydantic models for all data structures
- **Fail Fast**: Reject invalid code immediately
- **Clear Errors**: Provide specific syntax error messages
- **No Execution of Invalid Code**: Verification is a hard gate
- **Type Safety**: Enforce type hints in all Python code
- **Confidence Scoring**: Rate verification confidence (0.0-1.0)
- **Graceful Degradation**: Fall back to safe defaults on validation failure

## Code Patterns

```python
import ast
from pydantic import BaseModel, validator

def verify_python_syntax(code: str) -> tuple[bool, str]:
    """Verify Python code syntax using AST"""
    try:
        ast.parse(code)
        return True, "Valid Python syntax"
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"

class APIPayload(BaseModel):
    endpoint: str
    method: str
    params: dict
    
    @validator('method')
    def validate_method(cls, v):
        allowed = ['GET', 'POST', 'PUT', 'DELETE']
        if v not in allowed:
            raise ValueError(f"Method must be one of {allowed}")
        return v

# Verification middleware
def verify_before_execute(code: str, schema: BaseModel):
    # Step 1: Syntax check
    valid, msg = verify_python_syntax(code)
    if not valid:
        raise ValueError(f"Syntax error: {msg}")
    
    # Step 2: Schema validation
    payload = schema.parse_obj(data)
    
    # Step 3: Safe to execute
    return payload
```

## Common Tasks
1. **Validate Python Code**: Use ast.parse() to check syntax before exec()
2. **Create Pydantic Model**: Define schema with validators for API payloads
3. **Build Verification Middleware**: Chain syntax + schema + semantic checks
4. **Add Confidence Scoring**: Rate verification confidence based on checks passed

## Quality Standards
- All code MUST adhere to the 200-line rule (refactor immediately if exceeded)
- Minimum 80% test coverage required
- Type hints required for all Python functions
- Clear error messages with actionable recovery guidance
- Follow project architectural principles (see memory-bank/systemPatterns.md)

## Integration Points
- **Memory Bank**: Update relevant files after major changes
- **Build Plan**: Reference roadmap.md for phase alignment
- **Other Roles**: Coordinate with related specialists

## Reference Documentation
- Project Architecture: build_plan/phase0-architecture.md
- Project Roadmap: build_plan/roadmap.md
- Memory Bank: memory-bank/tasks.md
