# ADR-008: LLM Provider Strategy

**Status**: DECIDED  
**Date**: 2026-01-30  
**Deciders**: Development Team  
**Phase**: Phase 2 - The Reliable Brain

---

## Context

Phase 2 requires LLM integration for code generation (Plan and Generate nodes in the reasoning loop). We need to select providers, handle costs, and ensure reliability.

## Decision

**Decision**: Use **Claude Sonnet 4.5** as primary LLM with **Gemini 2.0 Flash** as fallback. Start with Claude-only in Phase 2.0, add Gemini fallback in Phase 2.1.

## Options Considered

### Option 1: Claude Only (Phase 2.0)

**Pros**: Best code quality, excellent instruction following  
**Cons**: Single point of failure, higher cost

### Option 2: Gemini Only

**Pros**: Lower cost, good speed  
**Cons**: Lower code quality than Claude

### Option 3: Multi-LLM with Fallback (Phase 2.1+) - SELECTED

**Pros**: Redundancy, cost optimization possible  
**Cons**: More complexity, API differences

### Option 4: Open Source (xLAM/Gorilla)

**Pros**: Zero API costs, privacy  
**Cons**: Lower quality, requires hosting

## Rationale

### Phase 2.0: Claude Sonnet 4.5 Only

- Simplicity for initial implementation
- Best code generation quality
- Faster to implement
- Sufficient for proving the architecture

### Phase 2.1: Add Gemini 2.0 Flash as Fallback

- Redundancy if Claude API fails
- Cost optimization for simple tasks
- Validate multi-LLM architecture

### Future: Evaluate xLAM for Specific Use Cases

- Function calling optimization
- Cost reduction for high-volume scenarios

## Implementation

### Configuration

```python
@dataclass
class LLMConfig:
    primary_provider: str = "claude"
    primary_model: str = "claude-sonnet-4-20250514"
    fallback_provider: str = "gemini"
    fallback_model: str = "gemini-2.0-flash"
    max_tokens: int = 2000
    temperature: float = 0.1  # Low for code generation
```

### Fallback Logic (Phase 2.1)

```python
async def generate_code(task: str) -> str:
    try:
        return await call_claude(task)
    except (RateLimitError, APIError) as e:
        logger.warning(f"Claude failed: {e}, falling back to Gemini")
        return await call_gemini(task)
```

## Consequences

### Positive

- Best code quality with Claude
- Fallback ensures reliability (Phase 2.1+)
- Clear migration path for cost optimization

### Negative

- Requires two API keys (Phase 2.1+)
- Different prompt formats per provider
- Testing complexity increases with fallback

## Cost Estimate

| Provider | Cost | Per Loop (3K tokens) |
|----------|------|---------------------|
| Claude Sonnet | $0.003/1K in, $0.015/1K out | ~$0.02-0.05 |
| Gemini Flash | ~$0.0001/1K | ~$0.001-0.005 |

**Monthly Budget at 1000 loops/day**: ~$600-1500 (Claude only)

## Environment Variables

```ini
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional (Phase 2.1+)
GOOGLE_API_KEY=...

# Settings
LLM_PRIMARY_PROVIDER=claude
LLM_PRIMARY_MODEL=claude-sonnet-4-20250514
LLM_MAX_TOKENS=2000
LLM_TEMPERATURE=0.1
```

---

**Related ADRs**: ADR-007 (LangGraph integration)  
**Supersedes**: None
