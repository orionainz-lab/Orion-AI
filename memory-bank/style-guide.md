# Memory Bank: Style Guide

## Code Hygiene Rules

### The 200-Line Rule
**CRITICAL**: Any file exceeding 200 lines must be immediately refactored into `services/` or `utils/`.

### Zero Tech Debt Policy
- Modular code enforced from Day 1
- No shortcuts or temporary solutions
- Immediate refactoring when complexity increases

## Coding Standards

### Python (Backend)
- **Framework**: FastAPI
- **Style**: PEP 8 compliant
- **Type Hints**: Required for all functions
- **Docstrings**: Required for all public functions
- **Testing**: pytest with minimum 80% coverage

### TypeScript/JavaScript (Frontend)
- **Framework**: Next.js (React)
- **Style**: ESLint + Prettier
- **Type Safety**: Strict TypeScript mode
- **Component Structure**: Functional components with hooks
- **Testing**: Jest + React Testing Library

### Database (Supabase)
- **Migrations**: Always versioned and tested
- **RLS**: Required for all tables with user data
- **Indexing**: Performance-critical queries must have indexes
- **Documentation**: All schema changes must be documented

## Documentation Standards

### Code Comments
- Why, not what (code shows what, comments show why)
- Complex logic requires explanation
- Public APIs require JSDoc/docstring

### File Organization
- Feature-based directory structure
- Clear separation of concerns
- Single Responsibility Principle

### Naming Conventions
- **Python**: snake_case for functions/variables, PascalCase for classes
- **TypeScript**: camelCase for functions/variables, PascalCase for components/classes
- **Files**: kebab-case for file names
- **Constants**: UPPER_SNAKE_CASE

## Git Workflow
- **Commits**: Descriptive messages following Conventional Commits
- **Branches**: Feature branches from main
- **PRs**: Required for all changes, must pass CI/CD
- **Reviews**: Required before merge

## Project Hygiene
- **Master Roadmap**: `build_plan/roadmap.md` maintained with check-offs
- **Chain of Custody**: Every completed task documented
- **Atomic Tasks**: Small, isolated units of work
