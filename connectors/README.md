# Connectors Directory

**Purpose**: API integration adapters for unified schema mapping

## Structure

N-to-N API connector framework:

```
connectors/
├── unified_schema/     # Canonical data models
├── adapters/          # API-specific adapters
├── mapping/           # Schema mapping logic
└── tests/             # Integration tests
```

## Architecture

- **Unified Schema Engine**: Map niche APIs to canonical models
- **Gorilla LLM**: Auto-generate connector mapping logic from API docs
- **N-to-N Solution**: Avoid writing thousands of unique connectors

## Coding Standards

- **200-Line Rule**: MANDATORY per file
- **Pydantic Models**: All schemas defined with Pydantic
- **Validation**: Comprehensive input/output validation
- **Testing**: Integration tests for each connector

## Guidelines

1. Define unified models (e.g., UnifiedCustomer, UnifiedInvoice)
2. Create thin adapters for specific APIs
3. Use Gorilla LLM for documentation parsing
4. Maintain connector registry

---

**Phase**: 2+ - Integration Layer  
**Status**: Awaiting connector development
