# Memory Bank: System Patterns

## Architecture: 4-Layer Stack

### Layer 1: Connectivity Fabric (Integration)
- **Technology**: Supabase PostgreSQL + Gorilla LLM
- **Pattern**: Unified Schema Engine for N-to-N integration
- **Purpose**: Universal API mapping without writing thousands of connectors

### Layer 2: Cognitive Orchestration (The Brain)
- **Technology**: Temporal.io + LangGraph
- **Pattern**: Cyclic Reasoning (Plan → Act → Observe → Correct)
- **Purpose**: Durable execution with complex reasoning loops

### Layer 3: Intelligence Layer (Memory & Verification)
- **Technology**: Python `ast` + Supabase pgvector + RLS
- **Pattern**: AST Verification & Contextual Anchoring
- **Purpose**: Eliminate hallucinations and enforce security

### Layer 4: Strategic Interface (Control Room)
- **Technology**: Next.js + AG Grid + Supabase Realtime
- **Pattern**: "Matrix UI" for Propose & Approve workflows
- **Purpose**: High-bandwidth human-in-the-loop governance

## Key Design Patterns
- **Durable Execution**: Workflows persist across crashes
- **Verification Layer**: All AI-generated code validated before execution
- **Permissions-Aware RAG**: Context filtered by user access rights
- **Cyclic Reasoning**: Agents loop until success or human intervention

## Phase 0 Architectural Patterns

### Directory Organization Pattern
- **services/**: Business logic modules (max 200 lines per file)
- **utils/**: Pure helper functions (max 200 lines per file)
- **build_plan/**: Architecture and planning documentation
- **scripts/**: Automation and setup scripts (max 200 lines per file)

### Modular Script Pattern
- Small, focused scripts (<200 lines)
- Single responsibility principle
- Independent execution capability
- Clear error messages
- Orchestration via simple runner script

### Role-Based Development Pattern
- 10 specialized AI personas via .cursor/rules
- Context-aware assistance per domain
- Clear responsibility boundaries
- Actionable, specific guidance
- Includes documentation specialist (added in Phase 0)

### Security-First Pattern
- RLS enabled by default on all tables
- ACL filtering before LLM context generation
- Credentials in environment variables (never committed)
- Audit logging for sensitive operations

### Zero Technical Debt Pattern
- 200-line rule enforced from Day 1
- No temporary solutions or shortcuts
- Immediate refactoring when complexity increases
- Comprehensive documentation mandatory
