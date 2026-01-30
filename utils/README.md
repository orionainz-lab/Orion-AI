# Utils Directory

**Purpose**: Helper functions and utilities (maximum 200 lines per file)

## Structure

Pure utility functions with no side effects:

```
utils/
├── file_operations.py   # File I/O helpers
├── validation.py        # Input validation utilities
├── formatting.py        # String and data formatting
└── logging.py          # Logging configuration
```

## Coding Standards

- **200-Line Rule**: MANDATORY - Any file exceeding 200 lines must be refactored
- **Pure Functions**: No side effects, deterministic outputs
- **Type Hints**: Required for all functions
- **Testing**: Minimum 90% coverage (utils should be highly testable)

## Guidelines

1. Utils are pure, reusable functions
2. No business logic in utils
3. Keep functions small and focused
4. Comprehensive documentation

---

**Phase**: 1+ - Implementation  
**Status**: Awaiting util development
