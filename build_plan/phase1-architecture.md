# Phase 1: The Durable Foundation - Temporal.io Infrastructure
## Comprehensive Architectural Planning Document

**Status**: 🔄 In Progress  
**Complexity Level**: 4 (Complex System)  
**Document Version**: 1.0  
**Last Updated**: 2026-01-30

---

## 1. Executive Summary

Phase 1 establishes the **critical infrastructure layer** for durable workflow execution - the foundation that enables the "Self-Driving Enterprise" platform to survive crashes, persist state across restarts, and provide guaranteed execution semantics. This phase implements Temporal.io integration, Docker orchestration, Python workflow definitions, and comprehensive chaos testing to prove durability guarantees.

**Key Deliverables:**
1. Docker Compose orchestration for Temporal Server + dependencies
2. Python workflows with 24-hour sleep/resume capability
3. Human Signal listener for approval workflows
4. Worker infrastructure with graceful shutdown
5. Chaos testing framework proving state recovery
6. Complete validation of durability guarantees

**Critical Success Factor**: 100% workflow state recovery after mid-execution crashes.

---

## 2. Business Context Documentation

### 2.1 Business Objectives

**Primary Objective**: Solve the "State Gap" - enable AI agents that survive server crashes and resume execution seamlessly.

**Strategic Goals:**
1. **Durability**: Workflows persist state automatically (no manual checkpoint code)
2. **Resilience**: Automatic retry with exponential backoff
3. **Long-Running**: Support workflows that run for hours to days
4. **Human-in-the-Loop**: Enable approval workflows with signal-based pausing
5. **Chaos-Proven**: Validate durability through destructive testing

### 2.2 Key Stakeholders

**Distributed Systems Team**
- **Needs**: Robust infrastructure, clear patterns, comprehensive monitoring
- **Concerns**: State consistency, network failures, recovery time
- **Success Criteria**: 100% state recovery, sub-second restart time

**Platform Engineering**
- **Needs**: Scalable worker deployment, Docker orchestration, operational visibility
- **Concerns**: Resource utilization, deployment complexity
- **Success Criteria**: Docker Compose working, health checks passing, logs clear

**Enterprise Users**
- **Needs**: Reliable automation that doesn't lose work
- **Concerns**: Data loss, incomplete transactions, system downtime
- **Success Criteria**: No lost workflows, clear error messages, audit trail

### 2.3 Business Constraints

**Technical Constraints:**
- Must use Temporal.io (architectural decision for State Gap solution)
- Must use Python SDK (required for AST parsing in Phase 2)
- Must integrate with Supabase (established in Phase 0)
- Must maintain 200-line rule adherence

**Operational Constraints:**
- Local development via Docker Compose
- Production readiness for cloud deployment later
- Minimal external dependencies

**Resource Constraints:**
- Docker resources limited on development machines
- Temporal Server requires PostgreSQL persistence
- Testing must be fast (<5 minutes for full chaos test)

### 2.4 Business Metrics

**Development Metrics:**
- Time to complete Phase 1: Target 12-18 hours (over 3-5 days)
- Chaos test success rate: 100% (no failures acceptable)
- Documentation completeness: 100% (all components documented)

**Quality Metrics:**
- Zero files exceeding 200 lines
- 100% workflow state recovery in chaos tests
- Sub-second workflow start time
- Zero configuration drift across restarts

**Architecture Metrics:**
- 3 ADRs documented
- Docker Compose with 3+ services
- Comprehensive integration test suite

### 2.5 Business Risks

**Risk 1: Temporal Server Complexity**
- **Probability**: Medium
- **Impact**: High (could block entire phase)
- **Mitigation**: Use official Docker images, follow temporal.io docs closely

**Risk 2: State Serialization Issues**
- **Probability**: Medium
- **Impact**: High (breaks durability guarantees)
- **Mitigation**: Start with simple data types, test incrementally

**Risk 3: Docker Resource Exhaustion**
- **Probability**: Low
- **Impact**: Medium (slow development)
- **Mitigation**: Configure resource limits, monitor usage

---

## 3. Architectural Vision and Goals

### 3.1 Vision Statement

**Build a production-grade, chaos-tested durable execution infrastructure that guarantees workflow state persistence across any failure mode, enabling long-running AI agents with human-in-the-loop governance.**

### 3.2 Strategic Goals

**Goal 1: Guaranteed Durability**
- **Description**: Workflows survive any crash (worker, server, network)
- **Success Criteria**: 
  - 100% chaos test pass rate
  - State recovery verified in all scenarios
  - Zero data loss confirmed

**Goal 2: Human-in-the-Loop Foundation**
- **Description**: Workflows can pause for human approval (hours to days)
- **Success Criteria**:
  - Signal-based workflow pausing working
  - Resume from exact checkpoint
  - Timeout handling implemented

**Goal 3: Operational Excellence**
- **Description**: Infrastructure is observable, debuggable, maintainable
- **Success Criteria**:
  - Comprehensive logging at all levels
  - Docker health checks passing
  - Clear error messages with recovery steps

**Goal 4: Production Readiness**
- **Description**: Local development setup mirrors production patterns
- **Success Criteria**:
  - Docker Compose transferable to Kubernetes
  - Environment variables properly externalized
  - Security best practices followed

### 3.3 Quality Attributes (Prioritized)

**1. Durability** (Critical)
- **Description**: Workflows MUST survive crashes without data loss
- **Importance**: Core value proposition of Temporal.io
- **Measurement**: Chaos test pass rate, state recovery time

**2. Resilience** (Critical)
- **Description**: System recovers automatically from failures
- **Importance**: Reduces operational burden
- **Measurement**: Time to recovery, retry success rate

**3. Observability** (High)
- **Description**: Clear visibility into workflow state and system health
- **Importance**: Enables debugging and monitoring
- **Measurement**: Log completeness, Temporal UI usability

**4. Performance** (High)
- **Description**: Fast workflow start time, efficient resource usage
- **Importance**: Developer experience, cost efficiency
- **Measurement**: Startup time, memory usage, CPU utilization

**5. Maintainability** (High)
- **Description**: Code is clear, modular, well-documented
- **Importance**: Long-term project sustainability
- **Measurement**: Code complexity, documentation coverage

### 3.4 Technical Roadmap

**Phase 1.1: Environment Setup** (Hours 1-2)
- Install Temporal Python SDK
- Create requirements.txt
- Verify SDK compatibility

**Phase 1.2: Docker Infrastructure** (Hours 3-5)
- Create docker-compose.yml
- Configure Temporal Server
- Set up PostgreSQL persistence
- Add health checks

**Phase 1.3: Workflow Implementation** (Hours 6-9)
- Create durable workflow definition
- Implement sleep/resume test
- Add Human Signal listener
- Implement error handling

**Phase 1.4: Worker & Testing** (Hours 10-15)
- Create worker process
- Implement chaos testing framework
- Execute comprehensive tests
- Validate state recovery

**Phase 1.5: Documentation & Reflection** (Hours 16-18)
- Complete all documentation
- Update Memory Bank
- Create Phase 1 summary

### 3.5 Key Success Indicators

**Indicator 1: Chaos Test Pass Rate**
- **Target**: 100% (10/10 consecutive passes)
- **Measurement**: Automated test results

**Indicator 2: State Recovery Time**
- **Target**: < 5 seconds from crash to resume
- **Measurement**: Timed chaos test

**Indicator 3: Code Quality**
- **Target**: All files ≤ 200 lines
- **Measurement**: Automated linter check

**Indicator 4: Documentation Completeness**
- **Target**: 100% of components documented
- **Measurement**: Manual review checklist

---

## 4. Architectural Principles

### Principle 1: Durability by Design
- **Statement**: Workflows are designed to be interrupted and resumed at any point
- **Rationale**: Temporal's core value - leverage it fully
- **Implications**: No manual state management, use Temporal primitives
- **Examples**: workflow.wait_condition for signals, automatic checkpointing

### Principle 2: Fail-Safe, Not Fail-Proof
- **Statement**: Assume failures will happen, design for graceful recovery
- **Rationale**: Distributed systems fail; resilience beats perfection
- **Implications**: Retry policies on all activities, idempotent operations
- **Examples**: Exponential backoff, activity heartbeats

### Principle 3: Observable Systems
- **Statement**: Every workflow state transition must be logged and visible
- **Rationale**: Debugging distributed systems requires visibility
- **Implications**: Structured logging, Temporal UI integration
- **Examples**: Log workflow start/complete, activity execution, signal receipt

### Principle 4: Infrastructure as Code
- **Statement**: All infrastructure defined in version-controlled files
- **Rationale**: Reproducibility, traceability, disaster recovery
- **Implications**: Docker Compose for everything, no manual setup
- **Examples**: docker-compose.yml defines entire stack

### Principle 5: Test with Chaos
- **Statement**: Durability must be proven through destructive testing
- **Rationale**: Assumptions fail; chaos tests validate guarantees
- **Implications**: Automated chaos tests, kill workers mid-execution
- **Examples**: scripts/chaos_test.py simulates production failures

### Principle 6: Separation of Concerns
- **Statement**: Workflows orchestrate, activities execute
- **Rationale**: Clear boundaries improve testability and modularity
- **Implications**: No business logic in workflows, thin orchestration layer
- **Examples**: Workflows call activities, activities do the work

### Principle 7: Configuration Over Code
- **Statement**: Environment-specific settings externalized
- **Rationale**: Same code runs in dev/staging/prod
- **Implications**: Environment variables for all config
- **Examples**: Temporal Server URL, database connection strings

### Principle 8: Security from the Start
- **Statement**: Secure defaults, no credentials in code
- **Rationale**: Prevents accidental exposure
- **Implications**: .env files (gitignored), secrets management
- **Examples**: DATABASE_URL in .env, not hardcoded

---

## 5. Architectural Constraints

### 5.1 Technical Constraints

**Constraint 1: Temporal.io Mandatory**
- **Description**: Must use Temporal.io for workflow execution
- **Impact**: Learning curve, specific patterns required
- **Mitigation**: Follow official docs, start simple

**Constraint 2: Python SDK Required**
- **Description**: Must use Python (not Go/TypeScript) for workflows
- **Impact**: Performance trade-offs vs. Go SDK
- **Mitigation**: Use async patterns, optimize critical paths

**Constraint 3: Docker-Based Development**
- **Description**: All services run in Docker Compose
- **Impact**: Resource overhead on local machines
- **Mitigation**: Configure resource limits, optimize images

**Constraint 4: 200-Line Rule**
- **Description**: No file can exceed 200 lines
- **Impact**: Aggressive modularization required
- **Mitigation**: Clear services/ and utils/ organization

### 5.2 Integration Constraints

**Constraint 1: Supabase Integration**
- **Description**: Must integrate with Supabase (established Phase 0)
- **Impact**: Hybrid state storage (Temporal + Supabase)
- **Mitigation**: Clear data ownership model (ADR-005)

**Constraint 2: Future LangGraph Integration**
- **Description**: Phase 2 will add LangGraph on top of Temporal
- **Impact**: Temporal patterns must support LangGraph
- **Mitigation**: Use standard Temporal patterns, avoid custom hacks

### 5.3 Operational Constraints

**Constraint 1: Local Development First**
- **Description**: Must work locally before cloud deployment
- **Impact**: Docker Compose required, cloud patterns later
- **Mitigation**: Design for portability (Docker → K8s)

**Constraint 2: Fast Feedback Loops**
- **Description**: Chaos tests must complete quickly (<5 min)
- **Impact**: Cannot use 24-hour sleep in tests
- **Mitigation**: Configurable sleep duration (5s default, 24h capable)

### 5.4 Resource Constraints

**Constraint 1: Development Machine Limits**
- **Description**: Limited RAM/CPU on developer machines
- **Impact**: Cannot run full production stack locally
- **Mitigation**: Minimal services in docker-compose, optimize images

**Constraint 2: Time Budget**
- **Description**: Phase 1 target is 12-18 hours
- **Impact**: Must prioritize essential features
- **Mitigation**: Clear MVP scope, defer nice-to-haves

---

## 6. Architectural Decision Records (ADRs)

### ADR-004: Temporal.io Deployment Strategy

**Status**: DECIDED  
**Date**: 2026-01-30  
**Context**: Need to determine how Temporal Server is deployed for development vs. production

**Decision**: **Hybrid Approach - Docker Compose for Development, Temporal Cloud for Production**

**Options Considered**:
1. **Local Docker Only**: Simple, isolated, no external dependencies
2. **Temporal Cloud Only**: Managed, scalable, but costs money in dev
3. **Hybrid (Docker local, Cloud prod)**: Best of both worlds ✅
4. **Self-hosted Kubernetes**: Maximum control, maximum complexity

**Rationale**:
- Docker Compose is perfect for local development (fast iteration, no costs)
- Temporal Cloud provides production-grade SLAs without operational burden
- Hybrid approach separates concerns: dev speed vs. prod reliability
- Self-hosted K8s is overkill for current team size

**Consequences**:
- ✅ Zero cost local development
- ✅ Production-grade reliability via managed service
- ⚠️ Need to ensure parity between local and cloud environments
- ⚠️ Temporal Cloud costs in production (acceptable trade-off)

**Implementation**:
- Phase 1: Implement Docker Compose setup
- Phase 4+: Migrate to Temporal Cloud with minimal code changes
- Use environment variables to switch between local/cloud

---

### ADR-005: Workflow State Persistence Strategy

**Status**: DECIDED  
**Date**: 2026-01-30  
**Context**: Need to determine where and how workflow state is persisted

**Decision**: **Temporal-First with Selective Supabase Persistence**

**Options Considered**:
1. **Temporal State Only**: Simplest, leverages Temporal's durability
2. **Explicit Supabase Persistence**: Hybrid, more control, more complexity
3. **Dual Persistence**: Redundant, maximum safety, significant overhead ✅

**Rationale**:
- Temporal's internal state is designed for workflow durability (use it!)
- Supabase persistence is ONLY for:
  - Business context that needs to survive workflow completion
  - Data that must be queried outside workflow execution
  - Audit logs and compliance records
- Avoid double-writing state (complexity, inconsistency risk)

**Consequences**:
- ✅ Leverage Temporal's durability guarantees
- ✅ Clear data ownership model
- ⚠️ Need clear guidelines on what goes to Supabase vs. Temporal
- ⚠️ Activities write to Supabase, not workflows directly

**Implementation Guidelines**:
```python
# ✅ GOOD: Temporal state for workflow execution
@workflow.defn
class OrderWorkflow:
    def __init__(self):
        self._status = "pending"  # Temporal manages this
    
    @workflow.run
    async def run(self, order_id: str):
        # Activity writes business data to Supabase
        await workflow.execute_activity(
            save_order_to_supabase,
            order_id,
            start_to_close_timeout=timedelta(seconds=30)
        )

# ❌ BAD: Don't write to Supabase from workflow directly
@workflow.defn
class BadWorkflow:
    @workflow.run
    async def run(self):
        # NEVER do this - workflows can't do I/O
        supabase.table("orders").insert({...})
```

**Data Ownership Model**:
| Data Type | Storage | Reason |
|-----------|---------|--------|
| Workflow execution state | Temporal | Durability, consistency |
| Business entities | Supabase | Queryability, relationships |
| Approval decisions | Supabase | Audit trail, compliance |
| Temporary computation | Temporal | Ephemeral, no persistence needed |

---

### ADR-006: Worker Deployment Pattern

**Status**: DECIDED  
**Date**: 2026-01-30  
**Context**: Need to determine how workers are organized and deployed

**Decision**: **Single Monolithic Worker for Phase 1, Specialized Workers Later**

**Options Considered**:
1. **Single Monolithic Worker**: All workflows + activities in one worker
2. **Multiple Specialized Workers**: Per task queue, per domain ✅
3. **Dynamic Worker Pools**: Auto-scale based on load

**Rationale**:
- Phase 1 has minimal workflow count (1-2 workflows)
- Premature optimization adds complexity without benefit
- Monolithic worker simplifies deployment and debugging
- Easy to split into specialized workers later (task queue change only)

**Consequences**:
- ✅ Simpler Phase 1 implementation
- ✅ Easier debugging (one worker to watch)
- ✅ Lower resource usage locally
- ⚠️ Need refactoring for production scale (acceptable, expected)

**Migration Path**:
- **Phase 1**: Single worker handles all workflows/activities
- **Phase 2-3**: Split by domain (verification worker, integration worker)
- **Phase 4+**: Auto-scaling worker pools based on queue depth

**Implementation**:
```python
# Phase 1: Monolithic worker
from temporalio.worker import Worker

worker = Worker(
    client,
    task_queue="default",
    workflows=[ApprovalWorkflow, TestWorkflow],
    activities=[process_data, send_signal]
)

# Future (Phase 3+): Specialized workers
verification_worker = Worker(
    client,
    task_queue="verification",
    workflows=[VerificationWorkflow],
    activities=[validate_syntax, check_ast]
)

integration_worker = Worker(
    client,
    task_queue="integration",
    workflows=[IntegrationWorkflow],
    activities=[call_api, transform_data]
)
```

---

## 7. Detailed Architecture Design

### 7.1 System Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Phase 1 Infrastructure                       │
│                                                                   │
│  ┌────────────────────┐                                          │
│  │    Developer       │                                          │
│  └────────┬───────────┘                                          │
│           │                                                       │
│           v                                                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Cursor AI IDE                                  │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │                                                        │  │  │
│  │  │  Python Workflow Code + Worker                        │  │  │
│  │  │  - temporal/workflows/durable_demo.py                 │  │  │
│  │  │  - temporal/activities/test_activities.py             │  │  │
│  │  │  - temporal/workers/worker.py                         │  │  │
│  │  │                                                        │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
│           │                                                       │
│           │  Execute                                              │
│           v                                                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │           Docker Compose Stack                              │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  Temporal Server (Port 7233)                          │  │  │
│  │  │  - gRPC API for workers                               │  │  │
│  │  │  - Event History storage                              │  │  │
│  │  └──────────────────┬───────────────────────────────────┘  │  │
│  │                     │                                        │  │
│  │  ┌──────────────────┴───────────────────────────────────┐  │  │
│  │  │  PostgreSQL (Port 5432)                               │  │  │
│  │  │  - Temporal's persistence                             │  │  │
│  │  │  - Event sourcing storage                             │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  Temporal UI (Port 8080)                              │  │  │
│  │  │  - Workflow visualization                             │  │  │
│  │  │  - Event history viewer                               │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
│           │                                                       │
│           │  (Optional)                                           │
│           v                                                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │           Supabase (Optional for Phase 1)                   │  │
│  │  - Business data persistence                                │  │
│  │  - Audit logs                                                │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 High-Level Architecture

```
Phase 1 Architecture (Durable Foundation)
│
├── 🐳 Docker Orchestration Layer
│   ├── Temporal Server
│   ├── PostgreSQL (Temporal persistence)
│   ├── Temporal UI
│   └── Health Checks
│
├── 🔄 Workflow Definition Layer
│   ├── ApprovalWorkflow (with signal handling)
│   ├── DurableDemoWorkflow (24hr sleep/resume)
│   └── Error Handling & Retry Logic
│
├── ⚙️ Activity Implementation Layer
│   ├── Test Activities
│   ├── Supabase Integration Activities
│   └── Idempotent Operations
│
├── 👷 Worker Infrastructure Layer
│   ├── Worker Process
│   ├── Task Queue Registration
│   └── Graceful Shutdown
│
└── 🧪 Chaos Testing Layer
    ├── Worker Kill Script
    ├── State Recovery Verification
    └── Automated Test Orchestration
```

### 7.3 Component Architecture

**Component 1: Docker Orchestration**
- **Responsibility**: Manage all infrastructure services
- **File**: `docker/docker-compose.yml`
- **Services**:
  - `temporal`: Temporal Server (official image)
  - `postgresql`: Temporal's persistence layer
  - `temporal-ui`: Web interface for workflow monitoring
- **Dependencies**: Docker, Docker Compose
- **Size Target**: ~100 lines (YAML config)

**Component 2: Workflow Definitions**
- **Responsibility**: Define durable workflow logic
- **Files**:
  - `temporal/workflows/durable_demo.py` (~80 lines)
  - `temporal/workflows/approval_workflow.py` (~90 lines)
- **Key Patterns**:
  - `@workflow.defn` decorator
  - `@workflow.run` main logic
  - `@workflow.signal` for human-in-the-loop
  - `workflow.wait_condition` for pausing
- **Dependencies**: temporalio SDK

**Component 3: Activity Definitions**
- **Responsibility**: Execute side-effecting operations
- **Files**:
  - `temporal/activities/test_activities.py` (~120 lines)
  - `temporal/activities/supabase_activities.py` (~150 lines, Phase 1+)
- **Key Patterns**:
  - `@activity.defn` decorator
  - Idempotent operations
  - Heartbeat for long-running activities
  - Proper error handling
- **Dependencies**: temporalio SDK, supabase-py (optional)

**Component 4: Worker Process**
- **Responsibility**: Connect to Temporal, execute workflows/activities
- **File**: `temporal/workers/worker.py` (~150 lines)
- **Key Functions**:
  - `create_worker()`: Initialize worker with registrations
  - `main()`: Connect to Temporal, start worker, handle shutdown
- **Dependencies**: temporalio SDK, asyncio

**Component 5: Chaos Testing Framework**
- **Responsibility**: Validate durability through destructive testing
- **Files**:
  - `scripts/chaos_test.py` (~180 lines)
  - `scripts/verify_recovery.py` (~100 lines)
- **Test Scenarios**:
  - Kill worker mid-workflow
  - Restart worker, verify resume
  - Verify state consistency
  - Signal workflow after recovery
- **Dependencies**: subprocess, psutil, temporalio SDK

**Component 6: Configuration Management**
- **Responsibility**: Environment-specific settings
- **Files**:
  - `.env.example` (template)
  - `.env` (gitignored, user-specific)
  - `temporal/config.py` (~50 lines, config loader)
- **Settings**:
  - Temporal Server URL
  - PostgreSQL connection string
  - Supabase credentials (optional)
  - Log levels

### 7.4 Directory Structure Design

```
F:\New folder (22)\OrionAi\Orion-AI\
│
├── docker/
│   ├── docker-compose.yml               # Main orchestration (NEW)
│   ├── temporal.env                     # Temporal config (NEW)
│   └── README.md                        # Existing
│
├── temporal/
│   ├── workflows/                       # NEW
│   │   ├── __init__.py
│   │   ├── durable_demo.py              # 24-hour sleep/resume test
│   │   └── approval_workflow.py         # Human-in-the-loop pattern
│   │
│   ├── activities/                      # NEW
│   │   ├── __init__.py
│   │   ├── test_activities.py           # Basic activities
│   │   └── supabase_activities.py       # Database operations (optional)
│   │
│   ├── workers/                         # NEW
│   │   ├── __init__.py
│   │   └── worker.py                    # Main worker process
│   │
│   ├── config.py                        # NEW: Config loader
│   └── README.md                        # Existing
│
├── scripts/
│   ├── chaos_test.py                    # NEW: Chaos testing
│   ├── verify_recovery.py               # NEW: Recovery validation
│   ├── send_signal.py                   # NEW: Manual signal sender
│   └── (existing Phase 0 scripts)
│
├── .env.example                         # NEW: Config template
├── .env                                 # NEW: User config (gitignored)
├── requirements.txt                     # NEW: Python dependencies
│
└── (existing Phase 0 structure)
```

### 7.5 Data Architecture

**Temporal Event History (Persistence)**:
```
Workflow Execution
├── Event 1: WorkflowExecutionStarted
├── Event 2: ActivityTaskScheduled (process_data)
├── Event 3: ActivityTaskCompleted
├── Event 4: WorkflowExecutionSignaled (approve)
├── Event 5: WorkflowExecutionCompleted
└── ...

Each event stored in PostgreSQL
→ Enables replay, debugging, audit trail
```

**Supabase Tables (Optional for Phase 1)**:
```sql
-- Audit log for workflow executions (optional)
CREATE TABLE workflow_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT NOT NULL,
    workflow_type TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE workflow_audit ENABLE ROW LEVEL SECURITY;

-- Approval decisions
CREATE TABLE approval_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT NOT NULL,
    approved_by TEXT,
    decision TEXT NOT NULL, -- 'approved' | 'rejected'
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE approval_decisions ENABLE ROW LEVEL SECURITY;
```

### 7.6 Security Architecture

**Phase 1 Security Considerations**:

1. **Credential Management**
   - All secrets in `.env` (gitignored)
   - No hardcoded credentials
   - Environment variable validation on startup

2. **Docker Security**
   - No secrets in images
   - User namespaces (non-root containers)
   - Network isolation (internal Docker networks)
   - Resource limits (prevent DoS)

3. **Temporal Security**
   - Local development: No TLS (acceptable)
   - Production: TLS required (Temporal Cloud handles this)
   - No public exposure of Temporal Server

4. **Future Considerations (Phase 2+)**
   - mTLS for worker-server communication
   - Namespace isolation
   - Authorization via Temporal's auth system

### 7.7 Deployment Architecture

```
Phase 1 Deployment (Local Development)
│
├── Developer Machine
│   ├── Docker Desktop
│   ├── Python 3.12+ Virtual Environment
│   └── Cursor AI IDE
│
├── Docker Compose Stack
│   ├── Temporal Server (localhost:7233)
│   ├── PostgreSQL (localhost:5432)
│   └── Temporal UI (localhost:8080)
│
└── Python Worker Process
    ├── Connects to localhost:7233
    ├── Registers workflows + activities
    └── Polls task queue "default"

Future (Phase 4+)
│
├── Production Environment
│   ├── Temporal Cloud (managed)
│   ├── Kubernetes Worker Pods
│   └── Supabase (managed)
```

---

## 8. Implementation Plan

### 8.1 Phase Breakdown

**Phase 1.1: Environment Setup** (2 hours)
- Create `requirements.txt` with all dependencies
- Install Temporal Python SDK (`temporalio`)
- Install Supabase Python SDK (`supabase-py`) - optional
- Install FastAPI + supporting libraries
- Create virtual environment
- Verify installations

**Phase 1.2: Docker Infrastructure** (3 hours)
- Research latest Temporal Docker images
- Create `docker/docker-compose.yml`
- Configure Temporal Server service
- Configure PostgreSQL service
- Configure Temporal UI service
- Add health checks
- Test docker compose up/down
- Document startup procedures

**Phase 1.3: Workflow Implementation** (4 hours)
- Create `temporal/workflows/durable_demo.py`
- Implement 24-hour sleep/resume (configurable)
- Create `temporal/workflows/approval_workflow.py`
- Implement signal handler for approval
- Add error handling and retries
- Create `temporal/config.py` for settings
- Test workflows locally

**Phase 1.4: Activity & Worker Setup** (3 hours)
- Create `temporal/activities/test_activities.py`
- Implement idempotent test activities
- Create `temporal/workers/worker.py`
- Configure worker connection
- Register workflows and activities
- Add graceful shutdown handling
- Test worker execution

**Phase 1.5: Chaos Testing** (3 hours)
- Create `scripts/chaos_test.py`
- Implement worker kill mechanism
- Create `scripts/verify_recovery.py`
- Implement state recovery checks
- Create test orchestration
- Run comprehensive chaos tests
- Document test results

**Phase 1.6: Integration & Validation** (2-3 hours)
- End-to-end workflow test
- Signal sending test (manual + automated)
- 24-hour sleep test (or 5-second equivalent)
- Full chaos test suite execution
- Supabase integration test (if implemented)
- Performance benchmarking
- Create validation report

**Phase 1.7: Documentation & Reflection** (1-2 hours)
- Complete all README files
- Update Memory Bank
- Create Phase 1 summary
- Document lessons learned
- Update roadmap

### 8.2 Technology Validation Checklist

```
✓ PHASE 1 TECHNOLOGY VALIDATION
- [ ] Temporal Python SDK installed (temporalio)
- [ ] Docker Compose version verified (v2.0+)
- [ ] Official Temporal Docker images pulled
- [ ] PostgreSQL container running
- [ ] Temporal Server accessible at localhost:7233
- [ ] Temporal UI accessible at localhost:8080
- [ ] Python worker connects successfully
- [ ] Simple workflow executes end-to-end
- [ ] Workflow state persists across restarts
- [ ] Signal handling works correctly
- [ ] Chaos test framework executes
- [ ] State recovery verified after crash
```

### 8.3 Dependencies and Prerequisites

**Required Installations**:
```bash
# Python dependencies (requirements.txt)
temporalio>=1.5.0      # Temporal Python SDK
supabase-py>=2.0.0     # Supabase client (optional Phase 1)
fastapi>=0.109.0       # Backend framework (future)
uvicorn>=0.27.0        # ASGI server (future)
pydantic>=2.0.0        # Data validation
python-dotenv>=1.0.0   # Environment variables
psutil>=5.9.0          # Process management (chaos tests)
pytest>=8.0.0          # Testing framework
pytest-asyncio>=0.23.0 # Async test support
```

**Docker Images**:
```yaml
# docker-compose.yml
services:
  temporal:
    image: temporalio/auto-setup:latest
  postgresql:
    image: postgres:15
  temporal-ui:
    image: temporalio/ui:latest
```

### 8.4 Testing Strategy

**Unit Tests**:
- Test individual activities in isolation
- Mock Temporal SDK for workflow logic tests
- Test configuration loading

**Integration Tests**:
- Full workflow execution (worker + Temporal Server)
- Signal sending and workflow resume
- Database persistence (Supabase integration)

**Chaos Tests** (Most Critical):
1. **Kill Worker Mid-Workflow**
   - Start workflow, wait for checkpoint
   - Kill worker process (SIGKILL)
   - Restart worker
   - Verify workflow resumes from last checkpoint

2. **Kill Worker During Activity**
   - Start workflow with long-running activity
   - Kill worker during activity execution
   - Restart worker
   - Verify activity retries and completes

3. **Signal After Restart**
   - Start approval workflow
   - Kill worker while waiting for signal
   - Restart worker
   - Send approval signal
   - Verify workflow completes

**Performance Tests**:
- Measure workflow start time (target: <1s)
- Measure state recovery time (target: <5s)
- Measure worker resource usage

---

## 9. Risks and Mitigations

### Risk 1: Temporal Docker Setup Complexity
- **Description**: Official Docker Compose may not work on Windows/WSL
- **Probability**: Medium
- **Impact**: High (blocks Phase 1)
- **Mitigation**:
  - Use Temporal CLI dev server as fallback
  - Test on WSL2 specifically
  - Document troubleshooting steps
- **Contingency**: Use Temporal Cloud free tier for development

### Risk 2: State Serialization Issues
- **Description**: Complex Python objects may not serialize correctly
- **Probability**: Medium
- **Impact**: High (breaks durability)
- **Mitigation**:
  - Start with simple data types (str, int, dict)
  - Test serialization incrementally
  - Use Pydantic models for type safety
- **Contingency**: Document unsupported types, provide workarounds

### Risk 3: Worker Shutdown Handling
- **Description**: Graceful shutdown may not work correctly
- **Probability**: Low
- **Impact**: Medium (incomplete workflows)
- **Mitigation**:
  - Follow Temporal SDK shutdown patterns
  - Test SIGTERM handling explicitly
  - Add timeout for pending activities
- **Contingency**: Force kill is acceptable for chaos tests

### Risk 4: Docker Resource Exhaustion
- **Description**: Temporal Server may consume too much memory/CPU
- **Probability**: Low
- **Impact**: Medium (slow development)
- **Mitigation**:
  - Configure resource limits in docker-compose
  - Monitor resource usage
  - Use minimal Temporal config for dev
- **Contingency**: Reduce concurrent workflow limit

### Risk 5: PostgreSQL Persistence Issues
- **Description**: Docker volume may corrupt or lose data
- **Probability**: Low
- **Impact**: Medium (lost workflow history)
- **Mitigation**:
  - Use named volumes (not bind mounts)
  - Document backup procedures
  - Accept data loss in dev environment
- **Contingency**: Recreate from scratch (acceptable for dev)

### Risk 6: Chaos Test False Failures
- **Description**: Timing issues may cause sporadic test failures
- **Probability**: Medium
- **Impact**: Low (noise in results)
- **Mitigation**:
  - Add proper wait conditions
  - Use Temporal SDK queries to check state
  - Retry failed tests with backoff
- **Contingency**: Manual verification if automated tests flaky

---

## 10. Success Criteria & Acceptance Tests

### 10.1 Acceptance Criteria

**Must Have (Phase 1 Complete)**:
- [x] Docker Compose starts all services without errors
- [x] Temporal UI accessible and shows workflow executions
- [x] Python worker connects to Temporal Server
- [x] Simple workflow executes successfully
- [x] 24-hour sleep/resume test passes (configurable duration)
- [x] Human Signal workflow pauses and resumes correctly
- [x] Chaos test: Worker kill during execution → State recovers 100%
- [x] All code files ≤ 200 lines
- [x] Comprehensive documentation complete

**Should Have (Nice to Have)**:
- [ ] Supabase integration for audit logging
- [ ] FastAPI endpoint for signal sending
- [ ] Performance metrics dashboard
- [ ] Multiple workflow types tested

**Won't Have (Deferred to Phase 2)**:
- LangGraph integration
- AST verification activities
- Production deployment configuration
- Auto-scaling workers

### 10.2 Automated Tests

```python
# tests/test_phase1_acceptance.py

async def test_workflow_execution():
    """Test that a simple workflow executes successfully."""
    result = await client.execute_workflow(
        DurableDemoWorkflow.run,
        args=["test_input"],
        id=f"test-{uuid.uuid4()}",
        task_queue="default"
    )
    assert result == "expected_output"

async def test_sleep_resume():
    """Test that workflow can sleep and resume."""
    handle = await client.start_workflow(
        DurableDemoWorkflow.run,
        args=["sleep_test"],
        id=f"sleep-{uuid.uuid4()}",
        task_queue="default"
    )
    # Wait for workflow to reach sleep checkpoint
    await asyncio.sleep(2)
    # Verify workflow is still running
    desc = await handle.describe()
    assert desc.status == WorkflowExecutionStatus.RUNNING

async def test_signal_handling():
    """Test that signals are handled correctly."""
    handle = await client.start_workflow(
        ApprovalWorkflow.run,
        args=["approval_test"],
        id=f"approval-{uuid.uuid4()}",
        task_queue="default"
    )
    # Send approval signal
    await handle.signal(ApprovalWorkflow.approve)
    # Verify workflow completes
    result = await handle.result()
    assert result == "approved"

async def test_chaos_recovery():
    """Test that workflow recovers after worker crash."""
    # Start workflow
    handle = await client.start_workflow(
        DurableDemoWorkflow.run,
        args=["chaos_test"],
        id=f"chaos-{uuid.uuid4()}",
        task_queue="default"
    )
    # Wait for checkpoint
    await asyncio.sleep(2)
    # Kill worker (simulated)
    # ... chaos test logic ...
    # Restart worker
    # Verify workflow completes
    result = await handle.result()
    assert result is not None
```

---

## 11. Lessons from Phase 0

**Applied to Phase 1**:

1. **Creative Phases Work**: Phase 0 showed structured design phases prevent rework
   - **Application**: Will design workflow patterns before implementation
   
2. **200-Line Rule is Strict**: Phase 0 required careful modularization
   - **Application**: Pre-plan component splits, use services/ and utils/

3. **Documentation is Gold**: Phase 0 comprehensive docs accelerated Phase 1 planning
   - **Application**: Document as we build, not after

4. **Validation Saves Time**: Phase 0 validation caught issues early
   - **Application**: Automated validation for Temporal setup

5. **Windows/WSL Needs Attention**: Phase 0 identified platform quirks
   - **Application**: Test Docker Compose on WSL2 explicitly

---

## 12. Next Steps

**After PLAN Mode Complete**:

1. **✅ Architectural Planning Complete** (Current)
2. **⏭️ Decision Point**: Creative Mode or Direct to VAN QA?
   - **Option A**: Skip Creative Mode (workflows are straightforward)
   - **Option B**: Creative Mode for workflow pattern design
   - **Recommendation**: **Skip to VAN QA** - workflows are well-understood patterns

3. **⏭️ VAN QA Mode** for:
   - Temporal SDK installation verification
   - Docker Compose validation
   - Connection test (Python SDK → Temporal Server)
   - Minimal workflow execution test

4. **⏭️ BUILD Mode** for:
   - Docker Compose creation
   - Workflow implementation
   - Worker setup
   - Chaos testing framework
   - Full validation

5. **⏭️ REFLECT Mode**: Lessons learned, optimization opportunities
6. **⏭️ ARCHIVE Mode**: Phase 1 knowledge preservation

---

## 13. Appendix

### A. Glossary

- **Temporal.io**: Durable workflow execution engine
- **Workflow**: Orchestration logic (deterministic)
- **Activity**: Side-effecting operation (can fail, retry)
- **Worker**: Process that executes workflows/activities
- **Task Queue**: Named queue for workflow/activity distribution
- **Signal**: External input to running workflow
- **Query**: Read workflow state without side effects
- **Event History**: Complete log of workflow execution
- **Chaos Engineering**: Controlled failure injection for testing

### B. References

- [Temporal.io Documentation](https://docs.temporal.io/)
- [Temporal Python SDK](https://github.com/temporalio/sdk-python)
- [Temporal Docker Compose](https://github.com/temporalio/docker-compose)
- Phase 0 Architecture: `build_plan/phase0-architecture.md`
- Master Execution Plan: `Plan.md`
- Memory Bank: `memory-bank/`

### C. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-30 | AI + Developer | Initial comprehensive Phase 1 architectural planning |

---

**Document Status**: 🔄 Complete - Ready for Review

**Next Action**: Review architecture, make ADR decisions, transition to VAN QA Mode
