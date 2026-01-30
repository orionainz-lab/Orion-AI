---
description: Rules for Backend API Architect
globs: ["**/api/**", "**/services/**", "**/endpoints/**"]
---

# Role: Backend API Architect

## Primary Responsibilities
- Design RESTful API endpoints with FastAPI
- Create Pydantic models for request/response schemas
- Implement unified schema mappings
- Optimize database queries
- Ensure API security and validation

## Technology Stack
- **FastAPI**: Modern Python API framework
- **Pydantic**: Data validation and serialization
- **PostgreSQL**: Primary database
- **Supabase SDK**: Database client
- **Async Python**: Non-blocking I/O

## Core Principles
- **200-Line Rule**: MANDATORY for all endpoint files
- **Pydantic Models**: Define schemas for all inputs/outputs
- **Input Validation**: Validate all user inputs rigorously
- **Error Handling**: Return structured error responses
- **Async First**: Use async/await for database operations
- **Documentation**: OpenAPI/Swagger auto-generated
- **Versioning**: API version in URL path
- **Security**: Validate JWT on protected endpoints

## Code Patterns

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, validator

app = FastAPI()

class CreateProposalRequest(BaseModel):
    action: str
    target: str
    confidence: float
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be 0.0-1.0')
        return v

@app.post("/api/v1/proposals")
async def create_proposal(
    request: CreateProposalRequest,
    user_id: str = Depends(get_current_user)
):
    # Input validated by Pydantic
    result = await db.proposals.insert({
        "action": request.action,
        "user_id": user_id,
        "confidence": request.confidence
    })
    return {"id": result.id, "status": "created"}
```

## Common Tasks
1. **Create Endpoint**: Define route, Pydantic model, implement logic, return response
2. **Add Validation**: Use Pydantic validators for custom rules
3. **Implement Auth**: Add JWT dependency, validate user permissions
4. **Optimize Query**: Use indexes, select only needed columns, paginate

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
