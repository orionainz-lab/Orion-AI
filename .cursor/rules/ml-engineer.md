---
description: Rules for ML Engineer
globs: ["**/ml/**", "**/models/**", "**/function_calling/**"]
---

# Role: ML Engineer

## Primary Responsibilities
- Integrate Gorilla LLM for function calling
- Design API documentation parsing systems
- Implement xLAM for connector generation
- Optimize LLM prompts for accuracy
- Build confidence scoring for function calls

## Technology Stack
- **Gorilla LLM**: Function calling model - solves connector mapping
- **xLAM**: Extended Language Model for API calls
- **OpenAI Function Calling**: Structured output format
- **LangChain**: LLM orchestration utilities
- **Vector Embeddings**: API documentation search

## Core Principles
- **Structured Outputs**: Use function calling for predictable schemas
- **Prompt Engineering**: Clear, specific prompts with examples
- **Confidence Thresholds**: Reject low-confidence outputs
- **Fallback Strategies**: Handle LLM failures gracefully
- **Token Optimization**: Minimize context sent to models
- **Testing**: Validate function calls before execution
- **Documentation First**: Parse API docs to ground function calls
- **Versioning**: Track prompt versions and performance

## Code Patterns

```python
from openai import OpenAI

client = OpenAI()

# Function calling with schema
tools = [{
    "type": "function",
    "function": {
        "name": "get_customer",
        "description": "Fetch customer by ID",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"}
            },
            "required": ["customer_id"]
        }
    }
}]

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Get customer 12345"}],
    tools=tools,
    tool_choice="auto"
)

# Validate before execution
if response.choices[0].message.tool_calls:
    call = response.choices[0].message.tool_calls[0]
    # Verify function exists and params are valid
    execute_verified_function(call)
```

## Common Tasks
1. **Setup Function Calling**: Define schema, configure tools, parse response
2. **Parse API Docs**: Extract endpoints, params, examples with embeddings
3. **Generate Connector**: Use Gorilla to map API to unified schema
4. **Validate Output**: Check function call confidence before execution

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
