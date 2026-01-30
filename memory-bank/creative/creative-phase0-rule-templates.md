# 🎨 CREATIVE PHASE 1: Rule Template Design
**Component**: Rule Generation System  
**Phase**: Phase 0 - Initialization  
**Date**: 2026-01-30  
**Status**: ✅ Complete

---

## 📌 CREATIVE PHASE START: Rule Template Design
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 1️⃣ PROBLEM

**Description**: Design a template structure for generating 9 role-based .cursor/rules files that provide context-aware AI assistance for specialized development domains.

**Requirements**:
- Each role must have clear, actionable guidance
- Rules must be specific enough to trigger appropriate context
- Must support 9 distinct personas (Distributed Systems, AI Orchestration, Verification, Frontend, Real-Time, ML, Security, Backend API, SDET)
- Templates must be maintainable and consistent
- Should include code examples and patterns
- Must reference relevant technologies per role

**Constraints**:
- Must work with Cursor AI's rules system
- Should not exceed 300 lines per rule file (reasonable for documentation)
- Must align with architectural principles (security-first, 200-line code rule)
- Should be easily modifiable as project evolves

---

### 2️⃣ OPTIONS

**Option A**: Minimal Template - Concise role-based rules
- Brief description of role responsibilities
- 3-5 key technologies per role
- Short list of best practices
- No code examples
- ~50-100 lines per file

**Option B**: Comprehensive Template - Detailed guidance with examples
- Full role description with responsibilities
- Technology stack with rationale
- Detailed best practices (10-15 items)
- Code examples for common patterns
- Architecture patterns specific to role
- Troubleshooting guidance
- ~200-300 lines per file

**Option C**: Hybrid Template - Structured sections with progressive detail
- Clear role definition
- Technology stack with brief rationale
- Organized best practices (8-12 items)
- Selected code examples (3-5)
- Quick reference patterns
- ~150-200 lines per file

---

### 3️⃣ ANALYSIS

| Criterion | Option A (Minimal) | Option B (Comprehensive) | Option C (Hybrid) |
|-----------|-------------------|-------------------------|-------------------|
| **Actionability** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Maintainability** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Context Quality** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **AI Triggering** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Complexity** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Implementation Time** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

**Key Insights**:
- **Option A** is too sparse - won't provide sufficient context for AI to be effective
- **Option B** provides excellent guidance but may be overwhelming and harder to maintain
- **Option C** offers best balance - enough detail for effective AI assistance while remaining maintainable
- Cursor AI works best with clear, structured patterns that can trigger role-specific behavior
- Code examples are critical for AI to understand expected patterns

---

### 4️⃣ DECISION

**Selected**: **Option C - Hybrid Template with Structured Sections**

**Rationale**:
- Provides strong context for AI triggering without overwhelming detail
- Balances comprehensiveness with maintainability
- Code examples critical for pattern recognition
- Structured format enables easy updates as project evolves
- ~150-200 lines is reasonable for documentation files
- Aligns with progressive enhancement principle

---

### 5️⃣ IMPLEMENTATION NOTES

#### Template Structure (All 9 Roles)

```markdown
# Role: [Role Name]

## Primary Responsibilities
[3-5 key responsibilities]

## Technology Stack
[5-8 key technologies with brief rationale]

## Core Principles
[8-12 actionable best practices organized by category]

## Code Patterns
[3-5 code examples showing expected patterns]

## Common Tasks
[4-6 typical tasks with implementation notes]

## Quality Standards
[Specific quality criteria for this role]

## Integration Points
[How this role interfaces with others]

## Reference Documentation
[Links to key external docs]
```

#### Specific Role Definitions

**1. Distributed Systems Engineer**
- **Focus**: Temporal.io, Docker, state persistence
- **Key Tech**: Temporal, Docker Compose, Python workflows
- **Patterns**: Durable execution, workflow-as-code, signal handling
- **Example**: Temporal workflow with sleep/resume

**2. AI Orchestration Engineer**
- **Focus**: LangGraph, reasoning loops, agent coordination
- **Key Tech**: LangGraph, Python, async patterns
- **Patterns**: Plan→Act→Observe→Correct cycles
- **Example**: Cyclic reasoning loop implementation

**3. Verification Specialist**
- **Focus**: AST parsing, syntax validation, code verification
- **Key Tech**: Python `ast` module, Pydantic, JSON Schema
- **Patterns**: Syntax checking before execution
- **Example**: AST-based validation middleware

**4. Senior Frontend Engineer**
- **Focus**: Next.js, AG Grid, Matrix UI
- **Key Tech**: Next.js 14+, React 18+, AG Grid, TailwindCSS
- **Patterns**: Component composition, state management
- **Example**: AG Grid Matrix implementation

**5. Real-Time Systems Engineer**
- **Focus**: WebSockets, Supabase Realtime, event streaming
- **Key Tech**: Supabase Realtime, WebSocket API
- **Patterns**: Real-time data sync, event broadcasting
- **Example**: Realtime subscription setup

**6. ML Engineer**
- **Focus**: Function calling models, Gorilla/xLAM integration
- **Key Tech**: Gorilla LLM, xLAM, OpenAI function calling
- **Patterns**: API documentation parsing, payload generation
- **Example**: Function calling implementation

**7. Security Engineer**
- **Focus**: RLS policies, OAuth2, ACL enforcement
- **Key Tech**: Supabase RLS, JWT, OAuth2
- **Patterns**: Defense in depth, least privilege
- **Example**: RLS policy creation

**8. Backend API Architect**
- **Focus**: FastAPI, Pydantic models, Unified Schema
- **Key Tech**: FastAPI, Pydantic, PostgreSQL
- **Patterns**: API design, schema mapping
- **Example**: Pydantic model with validation

**9. SDET (Software Development Engineer in Test)**
- **Focus**: Chaos testing, resilience validation
- **Key Tech**: pytest, Chaos Monkey patterns, Docker
- **Patterns**: Failure injection, recovery testing
- **Example**: Chaos test for Temporal workflow

#### Generation Script Requirements

The `scripts/generate-rules.py` should:
1. Read template structure from config
2. Inject role-specific content
3. Validate output format
4. Create files in `.cursor/rules/`
5. Generate index file listing all roles

---

## 📊 TEMPLATE EXAMPLE: Distributed Systems Engineer

```markdown
---
description: Rules for Distributed Systems Engineering with Temporal.io
globs: ["**/temporal/**", "**/workflows/**", "**/docker/**"]
---

# Role: Distributed Systems Engineer

## Primary Responsibilities
- Design and implement durable workflow systems using Temporal.io
- Ensure state persistence across crashes and restarts
- Manage Docker containerization and orchestration
- Implement signal handling for human-in-the-loop workflows
- Validate workflow recovery and resilience

## Technology Stack
- **Temporal.io**: Durable workflow execution engine - solves "State Gap"
- **Docker & Docker Compose**: Container orchestration
- **Python**: Temporal SDK implementation language
- **PostgreSQL**: Temporal's persistence layer
- **Signals & Queries**: Temporal's workflow interaction patterns

## Core Principles

### State Management
- Always design workflows to survive crashes
- Use Temporal's built-in persistence - no manual state saving
- Implement workflow history for debugging
- Design for idempotency in all workflow activities

### Resilience
- Test workflows with chaos engineering (kill processes mid-execution)
- Implement proper timeout and retry policies
- Use Temporal signals for human approval workflows
- Design for long-running workflows (hours to days)

### Docker Best Practices
- Use multi-stage builds for smaller images
- Never store secrets in images - use environment variables
- Implement health checks for all services
- Use Docker Compose for local development orchestration

## Code Patterns

### Temporal Workflow Example
\`\`\`python
from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta

@workflow.defn
class ApprovalWorkflow:
    def __init__(self):
        self._approved = False
    
    @workflow.run
    async def run(self, data: dict) -> str:
        # Execute business logic
        result = await workflow.execute_activity(
            process_data,
            data,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        # Wait for human approval (can wait days!)
        await workflow.wait_condition(lambda: self._approved)
        
        return result
    
    @workflow.signal
    async def approve(self):
        self._approved = True
\`\`\`

### Docker Compose Structure
\`\`\`yaml
version: '3.8'
services:
  temporal:
    image: temporalio/auto-setup:latest
    ports:
      - "7233:7233"
    environment:
      - DB=postgresql
      - DB_PORT=5432
    depends_on:
      - postgresql
  
  worker:
    build: ./worker
    environment:
      - TEMPORAL_HOST=temporal:7233
    depends_on:
      - temporal
\`\`\`

## Common Tasks

### Task 1: Create New Workflow
1. Define workflow class with `@workflow.defn`
2. Implement `@workflow.run` method
3. Add activities with proper timeouts
4. Register workflow with worker
5. Write chaos test (kill worker mid-workflow)

### Task 2: Implement Human-in-the-Loop
1. Add signal handler to workflow
2. Implement wait condition
3. Create signal API endpoint
4. Test timeout scenarios

### Task 3: Deploy with Docker
1. Create Dockerfile with multi-stage build
2. Add to docker-compose.yml
3. Configure environment variables
4. Test container restart scenarios

## Quality Standards
- All workflows MUST survive worker crashes
- Minimum 80% test coverage including chaos tests
- All activities MUST have explicit timeouts
- Workflow history MUST be reviewable
- Docker images MUST be <500MB

## Integration Points
- **Backend API**: Workflows triggered via FastAPI endpoints
- **Database**: Temporal uses PostgreSQL for persistence
- **Frontend**: Status updates via Supabase Realtime
- **Security**: Workflow authorization via JWT validation

## Reference Documentation
- [Temporal Python SDK](https://docs.temporal.io/dev-guide/python)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Workflow Patterns](https://docs.temporal.io/workflows)
```

---

## ✅ VERIFICATION

- [x] Problem clearly defined (9 role templates needed)
- [x] Multiple options considered (3 approaches)
- [x] Decision made with rationale (Hybrid template selected)
- [x] Implementation guidance provided (detailed structure + example)
- [x] Template example created (Distributed Systems Engineer)

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## 📌 CREATIVE PHASE 1 COMPLETE

**Outcome**: Hybrid template structure with 150-200 lines per role, balancing comprehensiveness with maintainability.

**Next**: Creative Phase 2 - Validation Framework Architecture
