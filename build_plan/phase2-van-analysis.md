# Phase 2 VAN Analysis: The Reliable Brain
## Verification, Analysis, Navigation

**Phase**: Phase 2 - The Reliable Brain (AST Verification)  
**Mode**: VAN (Verification, Analysis, Navigation)  
**Date**: 2026-01-30  
**Status**: 🔄 IN PROGRESS

---

## Executive Summary

**Objective**: Build AI agents that generate syntactically valid code on the first try, solving the "Syntax Gap" through LangGraph cyclic reasoning loops combined with Python AST verification.

**Complexity Assessment**: **Level 4** (Complex System)
- Multiple new technologies (LangGraph, AST parsing)
- Integration with Phase 1 (Temporal workflows)
- Cyclic reasoning patterns (Plan→Generate→Verify→Correct)
- Production-ready verification system required

**Estimated Duration**: 8-12 hours implementation (based on Phase 1 learnings)

---

## Problem Statement

### The Syntax Gap

**Current State**: AI models (GPT-4, Claude) generate code with syntax errors 15-30% of the time on first attempt. Common issues:
- Missing imports
- Undefined variables
- Type mismatches
- Invalid function signatures
- Malformed JSON/dictionaries
- Indentation errors

**Impact**: 
- Human developers spend time debugging AI-generated code
- Reduces trust in AI agents
- Slows down automation pipeline
- Requires manual validation before execution

**Target**: 95%+ first-attempt success rate (verified via AST parsing)

---

## Proposed Solution

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Phase 2: The Reliable Brain                      │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  LangGraph Cyclic Reasoning Loop (Temporal Workflow)          │ │
│  │                                                                │ │
│  │  ┌──────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐│ │
│  │  │ Plan │────▶│ Generate │────▶│ Verify   │────▶│ Correct  ││ │
│  │  └──────┘     └──────────┘     └──────────┘     └──────────┘│ │
│  │     │                               │                 │       │ │
│  │     │                               │ (AST Parse)     │       │ │
│  │     │                               ▼                 │       │ │
│  │     │                           ┌────────┐            │       │ │
│  │     │                           │ Valid? │────────────┘       │ │
│  │     │                           └────┬───┘                    │ │
│  │     │                                │ Yes                    │ │
│  │     └────────────────────────────────▼────────────────────────┤ │
│  │                                   ┌─────┐                     │ │
│  │                                   │ END │                     │ │
│  │                                   └─────┘                     │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  AST Verification Activities (Temporal Activities)            │ │
│  │  ├─ parse_python_code()      - Parse with ast module         │ │
│  │  ├─ validate_imports()       - Check import validity         │ │
│  │  ├─ validate_syntax()        - Full syntax check             │ │
│  │  ├─ extract_errors()         - Parse error messages          │ │
│  │  └─ generate_feedback()      - Create correction prompts     │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  Phase 1 Foundation (Inherited)                               │ │
│  │  ├─ Temporal.io (durable execution)                          │ │
│  │  ├─ Worker Process (registers LangGraph workflows)           │ │
│  │  └─ Chaos Testing (verify reasoning loop recovery)           │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Core Components

1. **LangGraph Reasoning Loop** (Temporal Workflow)
   - Plan step: Analyze task requirements
   - Generate step: Create Python code via LLM
   - Verify step: AST parse + validation
   - Correct step: Fix errors based on feedback
   - Conditional edge: Loop if invalid, exit if valid

2. **AST Verification System** (Temporal Activities)
   - Python AST parsing (built-in `ast` module)
   - Syntax error detection
   - Import validation
   - Type checking (basic)
   - Error-to-feedback translation

3. **Integration with Phase 1**
   - LangGraph loop runs as Temporal workflow
   - AST verification as Temporal activities
   - Inherit durability guarantees from Phase 1
   - Use existing worker process (extend registration)

---

## Requirements Analysis

### Functional Requirements

**FR-P2-001**: LangGraph state graph with cyclic reasoning
- State schema: task, plan, code, errors, iteration_count
- Nodes: planner, generator, verifier, corrector
- Edges: conditional (valid → END, invalid → corrector → generator)
- Max iterations: 3 (prevent infinite loops)

**FR-P2-002**: Python AST verification activity
- Parse Python code with `ast.parse()`
- Catch SyntaxError, IndentationError, etc.
- Extract error line numbers and messages
- Return structured error report

**FR-P2-003**: Import validation
- Check if imports are from stdlib or installed packages
- Flag unresolved imports
- Suggest corrections (common typos)

**FR-P2-004**: Error-to-feedback translation
- Convert AST errors to actionable LLM prompts
- Include error line numbers and context
- Provide correction hints

**FR-P2-005**: Integration with Temporal
- LangGraph loop as `@workflow.defn`
- AST verification as `@activity.defn`
- Reuse Phase 1 worker process

**FR-P2-006**: Chaos testing for reasoning loops
- Kill worker mid-generation → Verify loop resumes
- Test at each step: plan, generate, verify, correct
- Target: 100% state recovery (same as Phase 1)

### Non-Functional Requirements

**NFR-P2-001**: Performance
- Full reasoning loop (3 iterations max) < 30 seconds
- AST parsing < 100ms
- LLM generation < 5 seconds per attempt

**NFR-P2-002**: Code Quality
- All files ≤ 200 lines (200-line rule)
- Type hints on all functions
- Comprehensive docstrings
- Zero hardcoded values (use config)

**NFR-P2-003**: Observability
- Log each reasoning step
- Track iteration count
- Record verification results
- Temporal UI shows full reasoning history

**NFR-P2-004**: Extensibility
- Pluggable verification strategies (Python, TypeScript, SQL)
- Configurable max iterations
- Customizable LLM prompts

---

## Technology Stack

### New Technologies (Phase 2)

| Technology | Purpose | Version | Status |
|-----------|---------|---------|--------|
| **LangGraph** | Cyclic reasoning loops | Latest | ⏳ Needs validation |
| **Python ast** | Syntax verification | Built-in | ✅ Available |
| **langchain-core** | LangGraph dependency | Latest | ⏳ Needs validation |
| **LLM SDKs** | Code generation | anthropic/google | ⏳ Needs validation |

### Inherited from Phase 1

| Technology | Purpose | Status |
|-----------|---------|--------|
| Temporal.io | Workflow orchestration | ✅ Operational |
| Docker Compose | Service orchestration | ✅ Running |
| pytest | Testing framework | ✅ Installed |
| psutil | Process management | ✅ Installed |

---

## Dependency Analysis

### Required Python Packages

```txt
# Phase 2 additions to requirements.txt

# LangGraph & LangChain
langgraph>=0.2.0           # Cyclic reasoning framework
langchain-core>=0.3.0      # LangGraph dependency
langchain-anthropic>=0.2.0 # Claude integration
langchain-google-genai>=2.0.0  # Gemini integration

# Code Analysis
ast-comments>=1.2.0        # AST with comment preservation (optional)
black>=24.0.0              # Code formatting (for validation)
isort>=5.13.0              # Import sorting (for validation)

# Existing (from Phase 1)
temporalio>=1.8.0
fastapi>=0.128.0
pydantic>=2.10.0
python-dotenv>=1.0.0
pytest>=8.3.0
pytest-asyncio>=0.24.0
psutil>=6.1.1
```

### Version Compatibility Matrix

| Package | Minimum Version | Tested Version | Conflicts |
|---------|----------------|----------------|-----------|
| langgraph | 0.2.0 | TBD (VAN QA) | None known |
| langchain-core | 0.3.0 | TBD (VAN QA) | None known |
| temporalio | 1.8.0 | 1.21.1 (Phase 1) | None |
| python | 3.11+ | 3.11+ | None |

---

## Complexity Assessment

### Complexity Level: 4 (Complex System)

**Justification**:
- Multiple new technologies (LangGraph, AST, LLM SDKs)
- Cyclic control flow (not linear)
- Integration complexity (LangGraph + Temporal)
- State management across loop iterations
- Multi-LLM support (Claude + Gemini)

**Indicators**:
- ✅ New technology integration (LangGraph)
- ✅ Requires architectural decisions (ADRs needed)
- ✅ Cyclic patterns (conditional edges, loops)
- ✅ External dependencies (LLM APIs)
- ✅ Performance requirements (30s per loop)

**Workflow Recommended**: VAN → PLAN → VAN QA → BUILD → REFLECT → ARCHIVE

---

## Risk Assessment

### Technical Risks

| Risk ID | Risk | Probability | Impact | Mitigation |
|---------|------|-------------|--------|------------|
| R-P2-001 | LangGraph learning curve | Medium | Medium | VAN QA mode with hello-world |
| R-P2-002 | AST parser edge cases | Medium | High | Comprehensive test suite |
| R-P2-003 | LLM API rate limits | Low | Medium | Token budgeting, backoff |
| R-P2-004 | Infinite reasoning loops | Medium | High | Max iteration limit (3) |
| R-P2-005 | LangGraph-Temporal integration | Medium | High | Validate in VAN QA |
| R-P2-006 | File size >200 lines | Low | Low | Modular design from start |

### Dependency Risks

| Risk ID | Risk | Probability | Impact | Mitigation |
|---------|------|-------------|--------|------------|
| R-P2-D01 | LangGraph version incompatibility | Low | High | Pin versions, test early |
| R-P2-D02 | LLM SDK breaking changes | Low | Medium | Version pinning |
| R-P2-D03 | AST module limitations | Low | High | Fallback to regex validation |

---

## Integration Points

### With Phase 1 (Temporal Infrastructure)

**Reuse**:
- ✅ Temporal worker process (extend with LangGraph workflows)
- ✅ Configuration pattern (Config dataclasses)
- ✅ Chaos testing framework (test reasoning loop recovery)
- ✅ Docker Compose (add Redis for LangGraph checkpointer)

**New**:
- LangGraph workflows registered alongside Phase 1 workflows
- AST verification activities added to worker
- New task queue: "verification" (optional, or reuse "default")

### With Future Phases

**Phase 3 (Knowledge Layer)**:
- RAG context → LangGraph planner step
- Vector search → Code example retrieval

**Phase 4 (Frontend)**:
- Matrix UI → Trigger reasoning loops
- Real-time updates → LangGraph step progress

---

## Component Specifications

### Component 1: LangGraph State Schema

**File**: `agents/state.py` (~80 lines)

```python
from typing import TypedDict, Literal

class CodeGenerationState(TypedDict):
    """State for code generation reasoning loop"""
    
    # Input
    task: str                    # User's task description
    language: Literal["python", "typescript"]  # Target language
    
    # Planning
    plan: str                    # High-level approach
    requirements: list[str]      # Extracted requirements
    
    # Generation
    code: str                    # Generated code
    imports: list[str]           # Required imports
    
    # Verification
    is_valid: bool               # AST verification result
    errors: list[dict]           # Syntax errors (line, message)
    warnings: list[dict]         # Non-fatal issues
    
    # Correction
    feedback: str                # Error feedback for next iteration
    iteration: int               # Current iteration (max 3)
    max_iterations: int          # Iteration limit
    
    # Metadata
    model_used: str              # LLM model name
    tokens_used: int             # Token count tracking
```

**Rationale**:
- Clear separation: input, planning, generation, verification, correction
- Type safety (TypedDict + Literal)
- Observability (track iterations, tokens)

---

### Component 2: LangGraph Reasoning Nodes

**File**: `agents/reasoning_nodes.py` (~180 lines)

**Nodes**:
1. `plan_node`: Analyze task, create execution plan (LLM call)
2. `generate_node`: Generate code from plan (LLM call)
3. `verify_node`: AST verification (Activity call)
4. `correct_node`: Generate correction feedback (LLM call or rule-based)

**Conditional Logic**:
```python
def should_continue(state: CodeGenerationState) -> str:
    """Route based on verification result"""
    if state["is_valid"]:
        return "END"
    elif state["iteration"] >= state["max_iterations"]:
        return "END"  # Give up after max attempts
    else:
        return "correct"  # Loop back for correction
```

---

### Component 3: AST Verification Activities

**File**: `verification/ast_verifier.py` (~150 lines)

**Activities**:
1. `verify_python_syntax`: Parse with `ast.parse()`, return errors
2. `validate_imports`: Check stdlib/installed packages
3. `extract_error_details`: Parse SyntaxError into structured format
4. `generate_correction_prompt`: Create LLM feedback from errors

**Example**:
```python
import ast
from temporalio import activity

@activity.defn
async def verify_python_syntax(code: str) -> dict:
    """
    Verify Python code syntax using AST parser.
    Returns validation result with errors/warnings.
    """
    try:
        ast.parse(code)
        return {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
    except SyntaxError as e:
        return {
            "is_valid": False,
            "errors": [{
                "line": e.lineno,
                "offset": e.offset,
                "message": e.msg,
                "text": e.text
            }],
            "warnings": []
        }
```

---

### Component 4: LangGraph Workflow Integration

**File**: `agents/code_generation_workflow.py` (~180 lines)

**Workflow Structure**:
```python
from temporalio import workflow
from langgraph.graph import StateGraph, END

@workflow.defn
class CodeGenerationWorkflow:
    """Temporal workflow that runs LangGraph reasoning loop"""
    
    @workflow.run
    async def run(self, task: str, language: str = "python") -> dict:
        # Initialize LangGraph state
        initial_state = {
            "task": task,
            "language": language,
            "iteration": 0,
            "max_iterations": 3
        }
        
        # Build LangGraph graph
        graph = self._build_graph()
        
        # Execute reasoning loop (durable!)
        final_state = await graph.ainvoke(initial_state)
        
        return {
            "code": final_state["code"],
            "is_valid": final_state["is_valid"],
            "iterations": final_state["iteration"],
            "errors": final_state.get("errors", [])
        }
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph cyclic reasoning graph"""
        graph = StateGraph(CodeGenerationState)
        
        # Add nodes
        graph.add_node("plan", plan_node)
        graph.add_node("generate", generate_node)
        graph.add_node("verify", verify_node)
        graph.add_node("correct", correct_node)
        
        # Define flow
        graph.set_entry_point("plan")
        graph.add_edge("plan", "generate")
        graph.add_edge("generate", "verify")
        graph.add_conditional_edges(
            "verify",
            should_continue,
            {
                "END": END,
                "correct": "correct"
            }
        )
        graph.add_edge("correct", "generate")  # Loop back
        
        return graph.compile()
```

**Key Innovation**: LangGraph loop runs INSIDE Temporal workflow
- Inherits Phase 1 durability
- Can survive crashes mid-loop
- Full execution history in Temporal UI

---

### Component 5: LLM Integration Layer

**File**: `agents/llm_clients.py` (~120 lines)

**Features**:
- Multi-LLM support (Claude, Gemini)
- Token counting and budgeting
- Rate limit handling
- Prompt templates for each step
- Async API calls

**Example**:
```python
from anthropic import AsyncAnthropic
from temporalio import activity

@activity.defn
async def generate_code_with_llm(
    task: str,
    plan: str,
    language: str,
    feedback: str = None
) -> dict:
    """
    Generate code using Claude/Gemini.
    Includes feedback from previous iteration if correction needed.
    """
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    prompt = f"""
Task: {task}

Plan: {plan}

Generate {language} code that:
1. Implements the task according to the plan
2. Is syntactically valid
3. Includes all necessary imports

{f"Previous attempt had errors: {feedback}" if feedback else ""}

Output ONLY the code, no explanations.
"""
    
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return {
        "code": response.content[0].text,
        "model": "claude-sonnet-4",
        "tokens": response.usage.total_tokens
    }
```

---

### Component 6: Configuration Extension

**File**: `agents/config.py` (~60 lines)

```python
from dataclasses import dataclass
import os
from dotenv import load_dotenv

@dataclass
class LangGraphConfig:
    max_iterations: int
    enable_checkpointing: bool
    checkpointer_type: str  # "memory" or "redis"
    
    @classmethod
    def from_env(cls) -> "LangGraphConfig":
        return cls(
            max_iterations=int(os.getenv("LANGGRAPH_MAX_ITERATIONS", "3")),
            enable_checkpointing=bool(os.getenv("LANGGRAPH_CHECKPOINTING", "true")),
            checkpointer_type=os.getenv("LANGGRAPH_CHECKPOINTER", "memory")
        )

@dataclass
class LLMConfig:
    anthropic_api_key: str
    google_api_key: str
    default_model: str
    max_tokens: int
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            google_api_key=os.getenv("GOOGLE_API_KEY", ""),
            default_model=os.getenv("DEFAULT_LLM_MODEL", "claude-sonnet-4"),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000"))
        )
```

**Reuses Phase 1 Pattern**: Config dataclasses with `from_env()` classmethod

---

## Acceptance Criteria

### Must Have (Phase 2.0)

- [ ] LangGraph graph with 4 nodes (plan, generate, verify, correct)
- [ ] Conditional edge routing (valid → END, invalid → loop)
- [ ] Python AST verification activity (parse, validate, extract errors)
- [ ] Integration with Temporal (workflow + activities)
- [ ] Simple test: Generate "Hello World" function (3 iterations max)
- [ ] Chaos test: Kill during verification step → Loop resumes
- [ ] All files ≤ 200 lines
- [ ] 95%+ first-attempt success rate on test suite (10 tasks)

### Should Have (Phase 2.1)

- [ ] Import validation (stdlib + installed packages)
- [ ] Error-to-feedback translation
- [ ] Multi-LLM support (Claude + Gemini)
- [ ] Token usage tracking
- [ ] Comprehensive test suite (20+ code generation tasks)

### Nice to Have (Phase 3+)

- [ ] TypeScript AST verification
- [ ] SQL query validation
- [ ] Advanced type checking (mypy integration)
- [ ] Code quality metrics (cyclomatic complexity)

---

## Component Dependencies

```
Phase 2 Dependency Graph:

agents/state.py
    └─ No dependencies (TypedDict only)

agents/config.py
    └─ Depends: python-dotenv (from Phase 1)

verification/ast_verifier.py
    └─ Depends: ast (built-in), temporalio (Phase 1)

agents/llm_clients.py
    └─ Depends: anthropic, google-generativeai, temporalio

agents/reasoning_nodes.py
    └─ Depends: agents/state.py, agents/llm_clients.py, verification/ast_verifier.py

agents/code_generation_workflow.py
    └─ Depends: agents/reasoning_nodes.py, langgraph, temporalio

temporal/workers/worker.py (extend)
    └─ Depends: Phase 1 worker + agents/code_generation_workflow.py
```

---

## Directory Structure (Planned)

```
F:/New folder (22)/OrionAi/Orion-AI/
├── agents/                     # NEW: LangGraph reasoning loops
│   ├── __init__.py
│   ├── state.py               # State schema
│   ├── config.py              # LangGraph + LLM config
│   ├── reasoning_nodes.py     # Plan, generate, verify, correct nodes
│   ├── code_generation_workflow.py  # Main LangGraph workflow
│   └── llm_clients.py         # Claude + Gemini integration
│
├── verification/              # NEW: AST verification system
│   ├── __init__.py
│   ├── ast_verifier.py        # Python AST parsing activities
│   └── validators.py          # Import/type validators
│
├── temporal/                  # EXISTING: Extended from Phase 1
│   ├── workflows/
│   │   ├── durable_demo.py    # Phase 1
│   │   ├── approval_workflow.py  # Phase 1
│   │   └── (imports from agents/)  # Phase 2 workflows registered here
│   ├── activities/
│   │   ├── test_activities.py   # Phase 1
│   │   └── (imports from verification/)  # Phase 2 activities
│   └── workers/
│       └── worker.py          # EXTENDED: Register Phase 2 workflows
│
├── scripts/                   # EXTENDED: Add Phase 2 test scripts
│   ├── test_code_generation.py  # NEW: Test reasoning loop
│   ├── chaos_test_phase2.py     # NEW: Chaos tests for Phase 2
│   └── (Phase 1 scripts remain)
│
├── utils/                     # EXTENDED: Add verification utils
│   ├── chaos_utils.py         # Phase 1 (reused)
│   └── ast_utils.py           # NEW: AST parsing helpers
│
└── .env                       # EXTENDED: Add LLM API keys
```

**Estimated Files**: 10 new files (~1000 lines) + 3 extended files

---

## Implementation Phases

### Phase 2.1: LangGraph Hello World (2-3 hours)

**Objective**: Validate LangGraph can run as Temporal workflow

**Tasks**:
1. Install LangGraph dependencies
2. Create simple graph (2 nodes, 1 edge)
3. Run as standalone script (not Temporal)
4. Verify state propagation works

**Deliverable**: `scripts/test_langgraph_hello.py` (proof-of-concept)

---

### Phase 2.2: AST Verification System (2-3 hours)

**Objective**: Build robust Python syntax checker

**Tasks**:
1. Implement `verify_python_syntax` activity
2. Test with valid/invalid code samples
3. Extract structured error details
4. Generate correction feedback

**Deliverable**: `verification/ast_verifier.py` + test suite

---

### Phase 2.3: LangGraph-Temporal Integration (2-3 hours)

**Objective**: Run LangGraph loop inside Temporal workflow

**Tasks**:
1. Create `CodeGenerationWorkflow` with LangGraph
2. Register workflow in Phase 1 worker
3. Test end-to-end (task → code)
4. Verify durability (workflow survives restarts)

**Deliverable**: `agents/code_generation_workflow.py`

---

### Phase 2.4: Cyclic Reasoning Loop (2-3 hours)

**Objective**: Implement Plan→Generate→Verify→Correct cycle

**Tasks**:
1. Implement all 4 nodes
2. Add conditional edge logic
3. Test with intentionally broken code
4. Verify loop correction behavior

**Deliverable**: Complete reasoning loop with correction

---

### Phase 2.5: LLM Integration (1-2 hours)

**Objective**: Connect Claude/Gemini for code generation

**Tasks**:
1. Implement LLM client activities
2. Add API key configuration
3. Test token usage tracking
4. Handle rate limits gracefully

**Deliverable**: `agents/llm_clients.py`

---

### Phase 2.6: Chaos Testing (1-2 hours)

**Objective**: Prove reasoning loop survives crashes

**Tasks**:
1. Adapt Phase 1 chaos framework
2. Kill worker during each step (plan, generate, verify, correct)
3. Verify loop resumes correctly
4. Target: 100% state recovery

**Deliverable**: `scripts/chaos_test_phase2.py` (2 chaos tests)

---

## Success Metrics

### Quantitative Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| First-attempt success rate | 95%+ | AST verification on 20-task test suite |
| Average iterations per task | <2 | Track in LangGraph state |
| Loop completion time | <30s | End-to-end timing |
| Chaos test pass rate | 100% | 2/2 chaos tests pass |
| 200-line compliance | 100% | All files ≤ 200 lines |
| Code quality | A+ | Type hints, docstrings, no duplication |

### Qualitative Metrics

- LangGraph integration is seamless
- AST errors are actionable
- Developers trust AI-generated code
- Reasoning loop is observable (logs + Temporal UI)

---

## Architectural Decisions Needed

### ADR-007: LangGraph Integration Pattern (PENDING)

**Question**: How should LangGraph integrate with Temporal?

**Options**:
1. **LangGraph AS Temporal Workflow** (Recommended)
   - Pros: Inherit Phase 1 durability, full Temporal UI visibility
   - Cons: Requires LangGraph to be workflow-safe (no non-determinism)

2. **LangGraph OUTSIDE Temporal, Results Saved**
   - Pros: Simpler LangGraph usage
   - Cons: Lose durability during reasoning loop

3. **Hybrid: Temporal Orchestrates LangGraph Steps**
   - Pros: Fine-grained durability per step
   - Cons: More complex, more Temporal overhead

**Recommendation**: Option 1 (LangGraph AS Temporal Workflow)
- Best alignment with Phase 1 patterns
- Full durability for multi-step reasoning
- Clear Temporal UI visualization

**Decision Status**: ⏳ Pending PLAN mode

---

### ADR-008: LLM Provider Strategy (PENDING)

**Question**: Which LLM(s) for code generation?

**Options**:
1. **Claude Sonnet 4.5 Only**
   - Pros: Best code quality, function calling
   - Cons: Single point of failure, cost

2. **Multi-LLM (Claude + Gemini)**
   - Pros: Redundancy, cost optimization
   - Cons: More complexity, different APIs

3. **xLAM/Gorilla (Open Source)**
   - Pros: Zero API costs
   - Cons: Lower quality, requires hosting

**Recommendation**: Start with Claude Sonnet 4.5, add Gemini as fallback
- Phase 2.0: Claude only (simplicity)
- Phase 2.1: Add Gemini (redundancy)
- Phase 3+: Evaluate xLAM

**Decision Status**: ⏳ Pending PLAN mode

---

### ADR-009: AST Verification Scope (PENDING)

**Question**: How deep should AST verification go?

**Options**:
1. **Syntax Only** (Recommended for Phase 2.0)
   - Pros: Fast, reliable, well-defined
   - Cons: Misses type errors, logic bugs

2. **Syntax + Type Checking (mypy)**
   - Pros: Catches more errors
   - Cons: Slower, more dependencies, false positives

3. **Full Static Analysis (pylint, ruff)**
   - Pros: Catches style issues, bugs
   - Cons: Very slow, opinion-based rules

**Recommendation**: Syntax only for Phase 2.0, add type checking in Phase 2.1
- Phase 2.0: `ast.parse()` only
- Phase 2.1: Add `mypy` validation
- Phase 3+: Consider ruff/pylint

**Decision Status**: ⏳ Pending PLAN mode

---

## VAN QA Validation Requirements

### Technology Validation Checklist

**LangGraph**:
- [ ] Install `langgraph` package
- [ ] Create hello-world graph (2 nodes, 1 edge)
- [ ] Test state propagation
- [ ] Verify conditional edges work
- [ ] Test checkpointer (MemorySaver)

**Python AST**:
- [ ] Test `ast.parse()` with valid code
- [ ] Test `ast.parse()` with syntax errors
- [ ] Extract error line numbers
- [ ] Test import validation

**LangGraph + Temporal**:
- [ ] Run LangGraph graph inside Temporal workflow
- [ ] Verify state persists across workflow steps
- [ ] Test workflow crash during LangGraph execution
- [ ] Confirm Temporal UI shows LangGraph steps

**LLM APIs**:
- [ ] Test Claude Sonnet 4.5 API
- [ ] Test Gemini 2.0 Flash API
- [ ] Verify token counting
- [ ] Test rate limit handling

---

## Dependencies on Phase 1

### Hard Dependencies

**Required from Phase 1**:
- ✅ Temporal Server (localhost:7233) - RUNNING
- ✅ Worker process pattern - ESTABLISHED
- ✅ Configuration dataclass pattern - PROVEN
- ✅ Chaos testing framework - REUSABLE

### Soft Dependencies

**Nice to have from Phase 1**:
- ✅ Docker Compose infrastructure - CAN EXTEND
- ✅ Temporal UI - HELPFUL FOR DEBUGGING
- ✅ PostgreSQL - ALREADY RUNNING

**Status**: All Phase 1 dependencies MET ✅

---

## Time Estimate

### Based on Phase 1 Learnings

| Sub-Phase | Estimated | Confidence | Basis |
|-----------|-----------|------------|-------|
| 2.1: LangGraph Hello World | 2-3h | High | Similar to Phase 1.1 |
| 2.2: AST Verification | 2-3h | High | Python stdlib, well-documented |
| 2.3: LangGraph-Temporal | 2-3h | Medium | New integration, unknown issues |
| 2.4: Cyclic Reasoning | 2-3h | Medium | Conditional edges, testing loops |
| 2.5: LLM Integration | 1-2h | High | Async API calls, straightforward |
| 2.6: Chaos Testing | 1-2h | High | Reuse Phase 1 framework |
| **Total** | **8-12h** | **Medium-High** | **Based on Phase 1 ROI** |

**Confidence Drivers**:
- ✅ Phase 1 patterns proven (config, workers, chaos)
- ✅ LangGraph has good documentation (checked during review)
- ✅ AST is Python built-in (zero external complexity)
- ⚠️ LangGraph-Temporal integration unknown (VAN QA required)

---

## Risks & Mitigation

### High-Priority Risks

**R-P2-001: LangGraph Learning Curve**
- Mitigation: VAN QA with hello-world before PLAN
- Validation: Build simple 2-node graph, verify state works
- Fallback: Use plain Python state machine if LangGraph too complex

**R-P2-004: Infinite Reasoning Loops**
- Mitigation: Hard limit of 3 iterations in state
- Validation: Test with intentionally broken code
- Fallback: Return partial result after max iterations

**R-P2-005: LangGraph-Temporal Integration**
- Mitigation: VAN QA with proof-of-concept
- Validation: Run LangGraph inside workflow, test crash recovery
- Fallback: Run LangGraph outside Temporal (lose durability)

### Medium-Priority Risks

**R-P2-002: AST Parser Edge Cases**
- Mitigation: Comprehensive test suite (100+ code samples)
- Validation: Test stdlib code, common errors, edge cases
- Fallback: Fallback to `compile()` if `ast.parse()` fails

**R-P2-003: LLM API Rate Limits**
- Mitigation: Exponential backoff, token budgeting
- Validation: Test with high-frequency requests
- Fallback: Queue requests, add delays

---

## Phase 1 Lessons Applied

### Lesson 1: Always Run VAN QA Before BUILD
**Application**: Create `scripts/test_langgraph_hello.py` and `scripts/test_ast_parsing.py` BEFORE planning architecture

### Lesson 2: Plan for utils/ Extraction at 150 Lines
**Application**: Create `utils/ast_utils.py` and `utils/langgraph_utils.py` from the start

### Lesson 3: Chaos Testing Framework is Reusable
**Application**: Use `utils/chaos_utils.py` for Phase 2 chaos tests (80% reusable)

### Lesson 4: Integration Tests Beat Unit Tests
**Application**: Focus on end-to-end LangGraph + Temporal + AST tests, skip low-value unit tests

### Lesson 5: Docker First, Code Second
**Application**: If Redis needed for LangGraph checkpointer, add to docker-compose.yml during VAN QA

---

## Open Questions (For PLAN Mode)

1. **LangGraph Checkpointer**: Use MemorySaver (in-memory) or Redis (persistent)?
   - MemorySaver: Simple, no dependencies
   - Redis: Survives worker restarts, more production-ready
   - **Defer to PLAN mode**

2. **Error Feedback Strategy**: Rule-based or LLM-generated?
   - Rule-based: Fast, deterministic, cheap
   - LLM-generated: More nuanced, flexible
   - **Defer to PLAN mode**

3. **Multi-LLM Routing**: When to use Claude vs Gemini?
   - Claude: Complex code generation
   - Gemini: Simple tasks, cost optimization
   - **Defer to PLAN mode**

4. **AST Validation Depth**: Syntax only or include type checking?
   - Syntax only: Fast, reliable
   - Type checking (mypy): Catches more errors, slower
   - **Defer to PLAN mode**

---

## VAN Analysis Complete

### Summary

**Phase 2 is ready for PLAN mode**:
- ✅ Requirements analyzed (6 functional, 4 non-functional)
- ✅ Technology stack identified (LangGraph, AST, LLM SDKs)
- ✅ Complexity assessed (Level 4 - Complex System)
- ✅ Dependencies mapped (4 hard, 3 soft)
- ✅ Risks identified (6 technical, 2 dependency)
- ✅ Time estimated (8-12 hours, based on Phase 1 ROI)
- ✅ Component specifications drafted (6 components)
- ✅ Integration points defined (Phase 1, Phase 3-4)
- ✅ Acceptance criteria established (8 must-have, 5 should-have)

### Recommendations

1. **Proceed to VAN QA Mode IMMEDIATELY**
   - Validate LangGraph hello-world
   - Test AST parsing edge cases
   - Verify LangGraph-Temporal integration feasibility
   - **Rationale**: Phase 1 lesson - validate before planning

2. **Create 3 ADRs in PLAN Mode**
   - ADR-007: LangGraph integration pattern
   - ADR-008: LLM provider strategy
   - ADR-009: AST verification scope

3. **Target 8-12h Implementation**
   - Reuse Phase 1 patterns (config, chaos, workers)
   - Modular design from start (utils/ extraction at 150 lines)
   - Chaos testing mandatory (100% pass rate)

---

## Next Steps

**Immediate**: `/van qa` - Technology validation
- Test LangGraph hello-world
- Validate AST parsing
- Verify LangGraph-Temporal integration

**After VAN QA**: `/plan` - Architectural planning
- Document 3 ADRs
- Design component architecture
- Plan 6 sub-phases

**After PLAN**: `/build` - Implementation
- 8-12 hours estimated (with Phase 1 ROI)
- Target: 95%+ first-attempt success rate
- Chaos tests: 100% pass rate

---

**VAN Mode Status**: ✅ COMPLETE  
**Next Command**: `/van qa`  
**Estimated VAN QA Time**: 1-2 hours  

---

**Document Created**: 2026-01-30  
**Analysis Duration**: ~30 minutes  
**Quality**: Comprehensive (based on Phase 1 template)

**Ready to proceed to VAN QA Mode.**
