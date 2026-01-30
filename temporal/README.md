# Temporal Directory

**Purpose**: Durable workflow definitions and activities

## Structure

Temporal.io workflow implementations:

```
temporal/
├── workflows/          # Workflow definitions
├── activities/         # Activity implementations
├── workers/           # Worker configurations
└── tests/             # Workflow tests (including chaos tests)
```

## Key Concepts

- **Durable Execution**: Workflows survive crashes and resume seamlessly
- **State Gap Solution**: Workflows maintain state automatically
- **Human-in-the-Loop**: Signal handlers for approval workflows

## Coding Standards

- **200-Line Rule**: MANDATORY for all workflow files
- **Idempotency**: All activities must be idempotent
- **Timeouts**: Explicit timeouts required for all activities
- **Chaos Testing**: Required for all critical workflows

## Guidelines

1. Design workflows to survive worker crashes
2. Use Temporal's built-in persistence (no manual state saving)
3. Implement proper timeout and retry policies
4. Test with chaos engineering (kill processes mid-execution)

---

**Phase**: 1 - Durable Foundation  
**Status**: Awaiting Temporal.io integration
