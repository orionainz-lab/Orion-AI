# Services Directory

**Purpose**: Business logic modules (maximum 200 lines per file)

## Structure

This directory contains modular business logic organized by domain:

```
services/
├── authentication/     # Auth and identity services
├── workflows/          # Temporal workflow definitions
├── agents/             # LangGraph agent implementations
├── connectors/         # API integration services
└── validation/         # AST and verification services
```

## Coding Standards

- **200-Line Rule**: MANDATORY - Any file exceeding 200 lines must be refactored
- **Single Responsibility**: Each service handles one domain concern
- **Type Hints**: Required for all Python functions
- **Testing**: Minimum 80% coverage required

## Guidelines

1. Keep services focused and modular
2. Use dependency injection for testability
3. Document all public interfaces
4. Follow project coding standards (see memory-bank/style-guide.md)

---

**Phase**: 1+ - Implementation  
**Status**: Awaiting Phase 1 service development
