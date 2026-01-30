# Phase 2: The Reliable Brain - LangGraph & AST Verification
## Comprehensive Architectural Planning Document

**Status**: PLAN Mode Complete  
**Complexity Level**: 4 (Complex System)  
**Document Version**: 1.0  
**Last Updated**: 2026-01-30

---

## 1. Executive Summary

Phase 2 establishes the **AI reasoning and verification layer** - the "brain" that enables AI agents to generate syntactically valid code on the first attempt. This phase implements LangGraph cyclic reasoning loops with Python AST verification, running inside Temporal workflows for durability, solving the "Syntax Gap" identified in the platform vision.

**Key Deliverables:**
1. LangGraph cyclic reasoning framework (Plan→Generate→Verify→Correct)
2. Python AST verification system for syntax validation
3. LLM integration layer (Claude Sonnet 4.5 + Gemini fallback)
4. Temporal workflow integration for durable reasoning
5. Chaos testing for reasoning loop recovery
6. 95%+ first-attempt code validity target

**Critical Success Factor**: AI-generated code passes AST verification 95%+ on first attempt, with automatic correction loop for failures.

---

## 2. Business Context

### 2.1 Business Objectives

**Primary Objective**: Solve the "Syntax Gap" - enable AI agents that generate valid, executable code without human debugging.

**Strategic Goals:**
1. **Reliability**: 95%+ first-attempt success rate for code generation
2. **Self-Correction**: Automatic retry with intelligent error feedback
3. **Transparency**: Full reasoning chain visible in Temporal UI
4. **Durability**: Reasoning loops survive crashes (Phase 1 foundation)
5. **Extensibility**: Pluggable verification (Python first, then TypeScript, SQL)

### 2.2 Key Stakeholders

**AI Orchestration Team**
- **Needs**: Robust reasoning loops, clear state management, observable decisions
- **Concerns**: Infinite loops, LLM costs, error handling
- **Success Criteria**: <3 iterations average, <30s per loop

**Verification Team**
- **Needs**: Accurate syntax detection, actionable error messages
- **Concerns**: False positives, edge cases, performance
- **Success Criteria**: 100% syntax error detection, <100ms parse time

**Enterprise Users**
- **Needs**: Reliable AI code that "just works"
- **Concerns**: Buggy code, unclear errors, waiting time
- **Success Criteria**: 95%+ valid code, clear feedback when invalid

### 2.3 Business Constraints

**Technical Constraints:**
- Must integrate with Phase 1 Temporal infrastructure
- Must use Python AST (built-in, reliable)
- Must support multiple LLM providers (vendor independence)
- Must maintain 200-line rule adherence

**Operational Constraints:**
- LLM API keys required for full functionality
- Token budgeting for cost control
- Rate limit handling for APIs

**Resource Constraints:**
- LLM costs per reasoning loop (~$0.01-0.05)
- Temporal activity timeout (60s default)
- Memory for LangGraph state

### 2.4 Business Metrics

**Accuracy Metrics:**
- First-attempt success rate: Target 95%+
- Average iterations per task: Target <2
- False positive rate (valid code marked invalid): Target <1%

**Performance Metrics:**
- Reasoning loop time: Target <30s (3 iterations max)
- AST parse time: Target <100ms
- LLM response time: Target <5s per call

**Quality Metrics:**
- Zero files exceeding 200 lines
- 100% chaos test pass rate
- Comprehensive test coverage (20+ code generation tasks)

### 2.5 Problem Statement: The Syntax Gap

**Current State**: AI models (GPT-4, Claude) generate code with syntax errors 15-30% of the time on first attempt.

**Common Errors**:
| Error Type | Frequency | Detection Method |
|------------|-----------|------------------|
| Missing imports | 25% | Import validation |
| Indentation errors | 20% | AST parse |
| Missing colons/brackets | 15% | AST parse |
| Type mismatches | 15% | Basic type check |
| Undefined variables | 15% | Scope analysis |
| Other syntax | 10% | AST parse |

**Impact**:
- Developer time wasted debugging AI code
- Reduced trust in AI automation
- Slower adoption of AI tools

**Solution**: Cyclic reasoning with AST verification catches and corrects errors before human review.

---

## 3. Architecture Vision

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Phase 2: The Reliable Brain                           │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                    Temporal Workflow Layer                              ││
│  │  ┌───────────────────────────────────────────────────────────────────┐ ││
│  │  │  CodeGenerationWorkflow                                            │ ││
│  │  │  ├─ @workflow.defn                                                 │ ││
│  │  │  ├─ Orchestrates reasoning loop                                    │ ││
│  │  │  └─ Calls activities for LangGraph + AST                          │ ││
│  │  └───────────────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                    Temporal Activity Layer                              ││
│  │  ┌──────────────────────┐  ┌──────────────────────┐                    ││
│  │  │  LangGraph Activity  │  │  AST Verify Activity │                    ││
│  │  │  ├─ execute_loop()   │  │  ├─ verify_syntax()  │                    ││
│  │  │  ├─ Imports inside   │  │  ├─ extract_errors() │                    ││
│  │  │  └─ Returns result   │  │  └─ gen_feedback()   │                    ││
│  │  └──────────────────────┘  └──────────────────────┘                    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                    LangGraph Reasoning Layer                            ││
│  │  ┌──────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐             ││
│  │  │ Plan │───▶│ Generate │───▶│ Verify   │───▶│ Correct  │             ││
│  │  └──────┘    └──────────┘    └──────────┘    └──────────┘             ││
│  │      │            ▲               │ AST          │                      ││
│  │      │            │               ├─ Valid? ───▶ END                   ││
│  │      │            │               └─ Invalid? ──┘                      ││
│  │      └────────────┴───────────────────────────────                     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                    External Services                                    ││
│  │  ┌──────────────────────┐  ┌──────────────────────┐                    ││
│  │  │  Claude Sonnet 4.5   │  │  Gemini 2.0 Flash    │                    ││
│  │  │  (Primary LLM)       │  │  (Fallback LLM)      │                    ││
│  │  └──────────────────────┘  └──────────────────────┘                    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                    Phase 1 Foundation (Inherited)                       ││
│  │  ├─ Temporal Server (localhost:7233)                                    ││
│  │  ├─ PostgreSQL (Temporal persistence)                                   ││
│  │  ├─ Temporal UI (localhost:8080)                                        ││
│  │  └─ Worker Process (registers Phase 2 workflows)                        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Core Architectural Principles

1. **Activity-Level LangGraph** (ADR-007)
   - LangGraph executes inside Temporal activities (not workflows)
   - Avoids sandbox restrictions, provides retry durability
   - Imports happen inside activity functions

2. **Fail-Fast Verification**
   - AST parsing immediately on code generation
   - Structured error extraction for actionable feedback
   - Max 3 iterations to prevent runaway loops

3. **Observable Reasoning**
   - Every step logged in Temporal UI
   - State snapshots at each node
   - Full audit trail for debugging

4. **Graceful Degradation**
   - Primary LLM (Claude) with fallback (Gemini)
   - Return partial results after max iterations
   - Clear error messages when verification fails

5. **200-Line Rule Enforcement**
   - All components <200 lines
   - Extract to utils/ at 150 lines
   - Modular, testable design

---

## 4. Architectural Decision Records (ADRs)

### ADR-007: LangGraph Integration Pattern

**Status**: DECIDED  
**Date**: 2026-01-30  
**Deciders**: Development Team

#### Context

Phase 2 requires running LangGraph cyclic reasoning loops with Temporal durability guarantees. During VAN QA validation, we discovered that Temporal's workflow sandbox restricts importing LangGraph at module level because LangGraph depends on non-deterministic libraries (requests, urllib3).

#### Decision

**Decision**: Execute LangGraph inside Temporal **activities** (not workflows), with imports happening inside the activity function.

#### Options Considered

**Option 1: LangGraph Inside Workflows (Direct)** ❌
```python
from langgraph.graph import StateGraph  # TOP LEVEL

@workflow.defn
class ReasoningWorkflow:
    @workflow.run
    async def run(self, task):
        graph = StateGraph(...)  # FAILS: Sandbox restriction
```
- Pros: Per-step durability
- Cons: **Blocked by Temporal sandbox** (imports restricted)

**Option 2: LangGraph Inside Activities (Selected)** ✅
```python
@activity.defn
async def execute_reasoning(task: str) -> dict:
    # Import INSIDE activity
    from langgraph.graph import StateGraph, END
    
    graph = StateGraph(...)  # WORKS: Activities allow I/O
    return graph.invoke(initial_state)
```
- Pros: Works with Temporal, activity-level retries
- Cons: Re-executes full LangGraph on activity retry

**Option 3: LangGraph Outside Temporal**
```python
# Run LangGraph standalone, save results to Temporal
result = standalone_langgraph(task)
await workflow.execute_activity(save_result, result)
```
- Pros: Simple
- Cons: No durability during reasoning

#### Consequences

**Positive**:
- LangGraph-Temporal integration validated (VAN QA passed)
- Activity retries provide durability for full reasoning loop
- Clean separation: Workflow orchestrates, Activity reasons

**Negative**:
- On activity failure, entire LangGraph re-executes (not per-step)
- Must handle long-running activities (heartbeats needed)

**Mitigations**:
- Use heartbeats for activities >10s
- Set appropriate activity timeouts (60s)
- Log progress inside activity for debugging

**Code Pattern**:
```python
@activity.defn
async def execute_code_generation(task: str, max_iterations: int) -> dict:
    """LangGraph imports INSIDE activity function."""
    from langgraph.graph import StateGraph, END
    from agents.reasoning_nodes import plan_node, generate_node, verify_node, correct_node
    
    graph = StateGraph(CodeGenerationState)
    # ... build graph ...
    result = graph.invoke({"task": task, "iteration": 0, "max_iterations": max_iterations})
    return result
```

---

### ADR-008: LLM Provider Strategy

**Status**: DECIDED  
**Date**: 2026-01-30  
**Deciders**: Development Team

#### Context

Phase 2 requires LLM integration for code generation (Plan and Generate nodes). We need to select providers, handle costs, and ensure reliability.

#### Decision

**Decision**: Use **Claude Sonnet 4.5** as primary LLM with **Gemini 2.0 Flash** as fallback. Start with Claude-only in Phase 2.0, add Gemini fallback in Phase 2.1.

#### Options Considered

**Option 1: Claude Only** (Phase 2.0)
- Pros: Best code quality, excellent instruction following
- Cons: Single point of failure, higher cost

**Option 2: Gemini Only**
- Pros: Lower cost, good speed
- Cons: Lower code quality than Claude

**Option 3: Multi-LLM with Fallback** (Phase 2.1+) ✅
- Pros: Redundancy, cost optimization possible
- Cons: More complexity, API differences

**Option 4: Open Source (xLAM/Gorilla)**
- Pros: Zero API costs, privacy
- Cons: Lower quality, requires hosting

#### Decision Rationale

1. **Phase 2.0**: Claude Sonnet 4.5 only
   - Simplicity for initial implementation
   - Best code generation quality
   - Faster to implement

2. **Phase 2.1**: Add Gemini 2.0 Flash as fallback
   - Redundancy if Claude API fails
   - Cost optimization for simple tasks
   - Validate multi-LLM architecture

3. **Future**: Evaluate xLAM for specific use cases
   - Function calling optimization
   - Cost reduction for high-volume

#### Implementation

**Config Structure**:
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

**Fallback Logic** (Phase 2.1):
```python
async def generate_code(task: str) -> str:
    try:
        return await call_claude(task)
    except (RateLimitError, APIError) as e:
        logger.warning(f"Claude failed: {e}, falling back to Gemini")
        return await call_gemini(task)
```

#### Consequences

**Positive**:
- Best code quality with Claude
- Fallback ensures reliability
- Clear migration path for cost optimization

**Negative**:
- Requires two API keys (Phase 2.1+)
- Different prompt formats per provider
- Testing complexity increases

**Cost Estimate** (per reasoning loop):
- Claude Sonnet: ~$0.003/1K input, ~$0.015/1K output
- Estimated per loop (3K tokens): ~$0.02-0.05
- Monthly budget at 1000 loops/day: ~$600-1500

---

### ADR-009: AST Verification Scope

**Status**: DECIDED  
**Date**: 2026-01-30  
**Deciders**: Development Team

#### Context

Phase 2 needs code verification to detect errors. We must decide how deep verification should go: syntax only, type checking, or full static analysis.

#### Decision

**Decision**: Start with **syntax-only verification** using Python's built-in `ast.parse()` in Phase 2.0. Add optional type checking (mypy) in Phase 2.1 as a configurable enhancement.

#### Options Considered

**Option 1: Syntax Only (ast.parse)** ✅ Phase 2.0
```python
import ast

def verify_syntax(code: str) -> dict:
    try:
        ast.parse(code)
        return {"is_valid": True, "errors": []}
    except SyntaxError as e:
        return {"is_valid": False, "errors": [extract_error(e)]}
```
- Pros: Fast (<5ms), no dependencies, 100% reliable
- Cons: Misses type errors, logic bugs

**Option 2: Syntax + Type Checking (mypy)**
```python
from mypy import api

def verify_with_types(code: str) -> dict:
    result = api.run(["--ignore-missing-imports", code_file])
    # Parse mypy output...
```
- Pros: Catches type errors
- Cons: Slow (100-500ms), more dependencies, false positives

**Option 3: Full Static Analysis (pylint/ruff)**
```python
import subprocess
result = subprocess.run(["ruff", "check", code_file], ...)
```
- Pros: Catches style issues, potential bugs
- Cons: Very slow (1-5s), opinionated rules, noise

#### Decision Rationale

1. **Phase 2.0**: Syntax only (`ast.parse`)
   - Covers 70%+ of AI-generated errors (syntax issues)
   - Validated in VAN QA: 5ms for 400 lines
   - Zero external dependencies
   - Clear, actionable errors

2. **Phase 2.1**: Optional type checking
   - Add `--enable-type-checking` config flag
   - Use mypy for Python files with type hints
   - Catch additional 15-20% of errors

3. **Future**: Consider ruff for style enforcement
   - Only for production code review
   - Too noisy for AI generation feedback

#### Verification Levels

| Level | Method | Speed | Coverage | Phase |
|-------|--------|-------|----------|-------|
| **1. Syntax** | `ast.parse()` | <5ms | 70% | 2.0 |
| **2. Types** | mypy | 100-500ms | 85% | 2.1 |
| **3. Style** | ruff | 500-2000ms | 95% | Future |

#### Implementation

**Phase 2.0 Verifier**:
```python
import ast

@activity.defn
async def verify_python_syntax(code: str) -> dict:
    """Verify Python code syntax using AST parser."""
    try:
        tree = ast.parse(code)
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
                "message": str(e.msg),
                "text": e.text
            }],
            "warnings": []
        }
```

#### Consequences

**Positive**:
- Fast verification (<5ms) enables tight feedback loop
- No external dependencies for core functionality
- Clear path to enhanced verification

**Negative**:
- Won't catch type errors in Phase 2.0
- Won't catch logic bugs (expected)

**Mitigation**:
- Most AI syntax errors are caught by ast.parse
- Type checking available as opt-in for Phase 2.1
- Logic bugs are out of scope (requires testing)

---

## 5. Component Architecture

### 5.1 Component Overview

| Component | File | Lines | Purpose |
|-----------|------|-------|---------|
| **State Schema** | `agents/state.py` | ~80 | TypedDict for LangGraph state |
| **Reasoning Nodes** | `agents/nodes.py` | ~180 | Plan, Generate, Verify, Correct nodes |
| **LangGraph Builder** | `agents/graph_builder.py` | ~120 | Build and compile StateGraph |
| **AST Verifier** | `verification/ast_verifier.py` | ~150 | Python syntax verification |
| **LLM Clients** | `agents/llm_clients.py` | ~150 | Claude + Gemini integration |
| **Agent Config** | `agents/config.py` | ~80 | LangGraph + LLM configuration |
| **Workflow** | `agents/workflows.py` | ~120 | Temporal workflow definitions |
| **Activities** | `agents/activities.py` | ~180 | Temporal activity definitions |

**Total**: 8 new files, ~1060 lines (all <200 lines)

### 5.2 Component Details

#### 5.2.1 State Schema (`agents/state.py`)

```python
from typing import TypedDict, Literal, Optional

class CodeGenerationState(TypedDict):
    """State for code generation reasoning loop."""
    
    # Input
    task: str                              # User's task description
    language: Literal["python", "typescript"]  # Target language
    context: Optional[str]                 # Additional context
    
    # Planning
    plan: str                              # High-level approach
    requirements: list[str]                # Extracted requirements
    
    # Generation
    code: str                              # Generated code
    imports: list[str]                     # Required imports
    
    # Verification
    is_valid: bool                         # AST verification result
    errors: list[dict]                     # Syntax errors
    warnings: list[dict]                   # Non-fatal issues
    
    # Correction
    feedback: str                          # Error feedback for LLM
    correction_hints: list[str]            # Specific fix suggestions
    
    # Loop Control
    iteration: int                         # Current iteration (0-based)
    max_iterations: int                    # Limit (default 3)
    
    # Metadata
    model_used: str                        # LLM model name
    tokens_used: int                       # Token count
    reasoning_time_ms: int                 # Time tracking
```

#### 5.2.2 Reasoning Nodes (`agents/nodes.py`)

```python
from agents.state import CodeGenerationState

async def plan_node(state: CodeGenerationState) -> CodeGenerationState:
    """Analyze task and create execution plan."""
    # Call LLM to analyze task
    plan = await call_llm_for_plan(state["task"], state.get("context"))
    state["plan"] = plan
    state["requirements"] = extract_requirements(plan)
    return state

async def generate_node(state: CodeGenerationState) -> CodeGenerationState:
    """Generate code based on plan."""
    feedback = state.get("feedback", "")
    code = await call_llm_for_code(
        state["task"], 
        state["plan"], 
        state["language"],
        feedback
    )
    state["code"] = code
    state["iteration"] += 1
    return state

async def verify_node(state: CodeGenerationState) -> CodeGenerationState:
    """Verify code syntax using AST."""
    result = verify_python_syntax(state["code"])
    state["is_valid"] = result["is_valid"]
    state["errors"] = result["errors"]
    state["warnings"] = result.get("warnings", [])
    return state

async def correct_node(state: CodeGenerationState) -> CodeGenerationState:
    """Generate correction feedback from errors."""
    feedback = generate_error_feedback(state["errors"])
    state["feedback"] = feedback
    state["correction_hints"] = extract_hints(state["errors"])
    return state

def should_continue(state: CodeGenerationState) -> str:
    """Route: END if valid or max iterations, else correct."""
    if state["is_valid"]:
        return "end"
    elif state["iteration"] >= state["max_iterations"]:
        return "end"  # Return partial result
    else:
        return "correct"
```

#### 5.2.3 LangGraph Builder (`agents/graph_builder.py`)

```python
from langgraph.graph import StateGraph, END
from agents.state import CodeGenerationState
from agents.nodes import plan_node, generate_node, verify_node, correct_node, should_continue

def build_code_generation_graph() -> StateGraph:
    """Build the code generation reasoning graph."""
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
            "end": END,
            "correct": "correct"
        }
    )
    graph.add_edge("correct", "generate")  # Loop back
    
    return graph.compile()
```

#### 5.2.4 AST Verifier (`verification/ast_verifier.py`)

```python
import ast
from typing import Optional

def verify_python_syntax(code: str) -> dict:
    """Verify Python code syntax using AST parser."""
    if not code or not code.strip():
        return {
            "is_valid": False,
            "errors": [{"line": 0, "message": "Empty code provided"}],
            "warnings": []
        }
    
    try:
        tree = ast.parse(code)
        warnings = analyze_code_quality(tree)
        return {
            "is_valid": True,
            "errors": [],
            "warnings": warnings
        }
    except SyntaxError as e:
        return {
            "is_valid": False,
            "errors": [{
                "line": e.lineno or 0,
                "offset": e.offset or 0,
                "message": str(e.msg) if hasattr(e, 'msg') else str(e),
                "text": e.text.strip() if e.text else None
            }],
            "warnings": []
        }

def generate_error_feedback(errors: list[dict]) -> str:
    """Convert errors to actionable LLM feedback."""
    if not errors:
        return ""
    
    feedback_lines = ["The code has the following syntax errors:"]
    for error in errors:
        line_info = f"Line {error['line']}" if error.get('line') else "Unknown line"
        feedback_lines.append(f"- {line_info}: {error['message']}")
        if error.get('text'):
            feedback_lines.append(f"  Code: {error['text']}")
    
    feedback_lines.append("\nPlease fix these errors and regenerate the code.")
    return "\n".join(feedback_lines)
```

#### 5.2.5 LLM Clients (`agents/llm_clients.py`)

```python
import os
from anthropic import AsyncAnthropic
from agents.config import llm_config

_client: Optional[AsyncAnthropic] = None

async def get_claude_client() -> AsyncAnthropic:
    """Get or create Claude client."""
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client

async def call_llm_for_plan(task: str, context: str = None) -> str:
    """Call LLM to generate execution plan."""
    client = await get_claude_client()
    
    prompt = f"""Analyze this coding task and create a brief execution plan.

Task: {task}
{f"Context: {context}" if context else ""}

Provide a 2-3 sentence plan describing:
1. What the code should do
2. Key functions/classes needed
3. Important considerations

Plan:"""
    
    response = await client.messages.create(
        model=llm_config.primary_model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

async def call_llm_for_code(
    task: str, 
    plan: str, 
    language: str,
    feedback: str = None
) -> str:
    """Call LLM to generate code."""
    client = await get_claude_client()
    
    prompt = f"""Generate {language} code for this task.

Task: {task}
Plan: {plan}
{f"Previous attempt had errors: {feedback}" if feedback else ""}

Requirements:
- Code must be syntactically valid
- Include all necessary imports
- Follow best practices

Output ONLY the code, no explanations:"""
    
    response = await client.messages.create(
        model=llm_config.primary_model,
        max_tokens=llm_config.max_tokens,
        temperature=llm_config.temperature,
        messages=[{"role": "user", "content": prompt}]
    )
    return extract_code_from_response(response.content[0].text)
```

#### 5.2.6 Temporal Workflow (`agents/workflows.py`)

```python
from datetime import timedelta
from temporalio import workflow

# Import activities for type hints only
with workflow.unsafe.imports_passed_through():
    from agents.activities import execute_code_generation_activity

@workflow.defn
class CodeGenerationWorkflow:
    """Temporal workflow that orchestrates code generation."""
    
    @workflow.run
    async def run(
        self, 
        task: str, 
        language: str = "python",
        max_iterations: int = 3,
        context: str = None
    ) -> dict:
        """Execute code generation with LangGraph reasoning."""
        workflow.logger.info(f"Starting code generation for: {task[:50]}...")
        
        # Execute LangGraph reasoning as activity
        result = await workflow.execute_activity(
            execute_code_generation_activity,
            args=[task, language, max_iterations, context],
            start_to_close_timeout=timedelta(seconds=120),
            heartbeat_timeout=timedelta(seconds=30)
        )
        
        workflow.logger.info(
            f"Code generation complete: valid={result['is_valid']}, "
            f"iterations={result['iterations']}"
        )
        
        return {
            "workflow_id": workflow.info().workflow_id,
            "task": task,
            "code": result["code"],
            "is_valid": result["is_valid"],
            "iterations": result["iterations"],
            "errors": result.get("errors", []),
            "model_used": result.get("model_used", "unknown")
        }
```

#### 5.2.7 Temporal Activities (`agents/activities.py`)

```python
from temporalio import activity
import time

@activity.defn
async def execute_code_generation_activity(
    task: str,
    language: str,
    max_iterations: int,
    context: str = None
) -> dict:
    """
    Execute LangGraph code generation reasoning loop.
    
    KEY: LangGraph imports happen INSIDE this activity to avoid
    Temporal workflow sandbox restrictions.
    """
    # Import LangGraph inside activity (per ADR-007)
    from langgraph.graph import StateGraph, END
    from agents.graph_builder import build_code_generation_graph
    from agents.state import CodeGenerationState
    
    activity.logger.info(f"Starting LangGraph reasoning for: {task[:50]}...")
    start_time = time.time()
    
    # Build graph
    graph = build_code_generation_graph()
    
    # Initialize state
    initial_state: CodeGenerationState = {
        "task": task,
        "language": language,
        "context": context,
        "plan": "",
        "requirements": [],
        "code": "",
        "imports": [],
        "is_valid": False,
        "errors": [],
        "warnings": [],
        "feedback": "",
        "correction_hints": [],
        "iteration": 0,
        "max_iterations": max_iterations,
        "model_used": "",
        "tokens_used": 0,
        "reasoning_time_ms": 0
    }
    
    # Send heartbeat during execution
    activity.heartbeat("Starting reasoning loop")
    
    # Execute graph
    final_state = graph.invoke(initial_state)
    
    # Calculate timing
    elapsed_ms = int((time.time() - start_time) * 1000)
    final_state["reasoning_time_ms"] = elapsed_ms
    
    activity.logger.info(
        f"LangGraph complete: valid={final_state['is_valid']}, "
        f"iterations={final_state['iteration']}, time={elapsed_ms}ms"
    )
    
    return {
        "code": final_state["code"],
        "is_valid": final_state["is_valid"],
        "iterations": final_state["iteration"],
        "errors": final_state["errors"],
        "warnings": final_state["warnings"],
        "model_used": final_state.get("model_used", "claude-sonnet-4"),
        "reasoning_time_ms": elapsed_ms
    }
```

---

## 6. Directory Structure

### 6.1 New Files (Phase 2)

```
F:/New folder (22)/OrionAi/Orion-AI/
├── agents/                          # NEW: LangGraph reasoning
│   ├── __init__.py                  # Package init (~10 lines)
│   ├── state.py                     # State schema (~80 lines)
│   ├── nodes.py                     # Reasoning nodes (~180 lines)
│   ├── graph_builder.py             # LangGraph builder (~120 lines)
│   ├── llm_clients.py               # LLM integration (~150 lines)
│   ├── config.py                    # Agent configuration (~80 lines)
│   ├── workflows.py                 # Temporal workflows (~120 lines)
│   └── activities.py                # Temporal activities (~180 lines)
│
├── verification/                    # NEW: Code verification
│   ├── __init__.py                  # Package init (~10 lines)
│   └── ast_verifier.py              # AST verification (~150 lines)
│
├── scripts/                         # EXTENDED: Add Phase 2 tests
│   ├── test_code_generation.py      # NEW: Integration tests (~180 lines)
│   └── chaos_test_phase2.py         # NEW: Chaos tests (~180 lines)
│
└── temporal/workers/
    └── worker.py                    # EXTENDED: Register Phase 2 (~10 lines added)
```

### 6.2 File Count Summary

| Category | New Files | Extended Files | Total Lines |
|----------|-----------|----------------|-------------|
| agents/ | 8 | 0 | ~920 |
| verification/ | 2 | 0 | ~160 |
| scripts/ | 2 | 0 | ~360 |
| temporal/ | 0 | 1 | ~10 |
| **Total** | **12** | **1** | **~1450** |

**All files comply with 200-line rule** ✅

---

## 7. Data Flow

### 7.1 Code Generation Flow

```
User Request
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Temporal Workflow: CodeGenerationWorkflow                   │
│                                                               │
│  Input: task="Create a function to sort a list"             │
│         language="python"                                    │
│         max_iterations=3                                     │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Activity: execute_code_generation_activity          │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────────┐│   │
│  │  │ LangGraph Execution                             ││   │
│  │  │                                                   ││   │
│  │  │  1. PLAN NODE                                    ││   │
│  │  │     └─► LLM: "Analyze task..."                  ││   │
│  │  │         └─► plan: "Create a sort function..."   ││   │
│  │  │                                                   ││   │
│  │  │  2. GENERATE NODE                                ││   │
│  │  │     └─► LLM: "Generate code for plan..."        ││   │
│  │  │         └─► code: "def sort_list(arr):..."      ││   │
│  │  │                                                   ││   │
│  │  │  3. VERIFY NODE                                  ││   │
│  │  │     └─► ast.parse(code)                         ││   │
│  │  │         └─► is_valid: True                      ││   │
│  │  │                                                   ││   │
│  │  │  4. CONDITIONAL: is_valid=True → END            ││   │
│  │  └─────────────────────────────────────────────────┘│   │
│  │                                                       │   │
│  │  Return: {code, is_valid=True, iterations=1}        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Return: {workflow_id, code, is_valid, iterations}          │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
Valid Python Code
```

### 7.2 Correction Loop Flow (Invalid Code)

```
Initial Code Generation (Invalid)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ ITERATION 1                                                  │
│                                                               │
│  GENERATE → code: "def hello(\n  print('Hi'"               │
│  VERIFY → is_valid: False                                   │
│           errors: [{line: 2, message: "missing ')'"}]       │
│  CORRECT → feedback: "Line 2: missing ')'"                  │
│                                                               │
│  Loop back to GENERATE                                       │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ ITERATION 2                                                  │
│                                                               │
│  GENERATE → code: "def hello():\n    print('Hi')"          │
│             (LLM received error feedback)                    │
│  VERIFY → is_valid: True                                    │
│                                                               │
│  Exit to END                                                 │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
Valid Python Code (2 iterations)
```

---

## 8. Configuration

### 8.1 Environment Variables

**Add to `.env`**:
```ini
# Phase 2: LangGraph & LLM Configuration

# LLM API Keys (required for code generation)
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# LLM Settings
LLM_PRIMARY_PROVIDER=claude
LLM_PRIMARY_MODEL=claude-sonnet-4-20250514
LLM_FALLBACK_PROVIDER=gemini
LLM_FALLBACK_MODEL=gemini-2.0-flash
LLM_MAX_TOKENS=2000
LLM_TEMPERATURE=0.1

# LangGraph Settings
LANGGRAPH_MAX_ITERATIONS=3
LANGGRAPH_ENABLE_CHECKPOINTING=false

# Verification Settings
VERIFICATION_LEVEL=syntax
VERIFICATION_TIMEOUT_MS=5000

# Activity Settings
ACTIVITY_TIMEOUT_SECONDS=120
ACTIVITY_HEARTBEAT_SECONDS=30
```

### 8.2 Configuration Dataclasses

```python
# agents/config.py

from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class LLMConfig:
    primary_provider: str
    primary_model: str
    fallback_provider: str
    fallback_model: str
    max_tokens: int
    temperature: float
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls(
            primary_provider=os.getenv("LLM_PRIMARY_PROVIDER", "claude"),
            primary_model=os.getenv("LLM_PRIMARY_MODEL", "claude-sonnet-4-20250514"),
            fallback_provider=os.getenv("LLM_FALLBACK_PROVIDER", "gemini"),
            fallback_model=os.getenv("LLM_FALLBACK_MODEL", "gemini-2.0-flash"),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1"))
        )

@dataclass
class LangGraphConfig:
    max_iterations: int
    enable_checkpointing: bool
    
    @classmethod
    def from_env(cls) -> "LangGraphConfig":
        return cls(
            max_iterations=int(os.getenv("LANGGRAPH_MAX_ITERATIONS", "3")),
            enable_checkpointing=os.getenv("LANGGRAPH_ENABLE_CHECKPOINTING", "false").lower() == "true"
        )

# Singleton instances
llm_config = LLMConfig.from_env()
langgraph_config = LangGraphConfig.from_env()
```

---

## 9. Testing Strategy

### 9.1 Test Categories

| Category | Tests | Purpose |
|----------|-------|---------|
| Unit Tests | 10+ | Individual component testing |
| Integration Tests | 5+ | End-to-end code generation |
| Chaos Tests | 2 | Worker crash recovery |
| Performance Tests | 3 | Timing and resource usage |

### 9.2 Code Generation Test Suite

**Test Tasks** (20 total for acceptance criteria):

1. Simple function: "Create a function that adds two numbers"
2. String manipulation: "Create a function that reverses a string"
3. List operations: "Create a function that finds the max in a list"
4. Dictionary usage: "Create a function that counts word frequencies"
5. Class definition: "Create a Calculator class with add/subtract methods"
6. Async function: "Create an async function that fetches data"
7. File I/O: "Create a function that reads a JSON file"
8. Error handling: "Create a function with try/except for division"
9. List comprehension: "Create a function using list comprehension"
10. Decorator: "Create a timing decorator"
11. Generator: "Create a generator that yields Fibonacci numbers"
12. Context manager: "Create a context manager for file operations"
13. Dataclass: "Create a User dataclass with validation"
14. Type hints: "Create a typed function for data processing"
15. Recursion: "Create a recursive factorial function"
16. Lambda: "Create a function that sorts by custom key"
17. Regex: "Create a function that validates email format"
18. Date handling: "Create a function that calculates age from birthdate"
19. API client: "Create a simple HTTP client function"
20. Data validation: "Create a function that validates user input"

### 9.3 Chaos Tests

**Test 1: Kill During Plan**
```python
async def test_kill_during_plan():
    # Start workflow
    # Wait for plan node
    # Kill worker
    # Restart worker
    # Verify workflow resumes and completes
```

**Test 2: Kill During Generate**
```python
async def test_kill_during_generate():
    # Start workflow
    # Wait for generate node  
    # Kill worker
    # Restart worker
    # Verify workflow resumes and completes
```

### 9.4 Acceptance Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| First-attempt success rate | 95%+ | 19/20 test tasks pass on iteration 1 |
| Average iterations | <2 | Mean iterations across all tasks |
| Max iterations | ≤3 | No task exceeds 3 iterations |
| Chaos test pass rate | 100% | 2/2 chaos tests pass |
| 200-line compliance | 100% | All files ≤200 lines |
| Performance | <30s | Full loop completes in 30s |

---

## 10. Implementation Plan

### Phase 2.1: Core Infrastructure (2-3 hours)

**Tasks**:
1. Create `agents/` directory structure
2. Implement `agents/state.py` (state schema)
3. Implement `agents/config.py` (configuration)
4. Create `verification/__init__.py` and `verification/ast_verifier.py`

**Deliverables**:
- State schema TypedDict
- Configuration dataclasses
- AST verifier activity

**Verification**: Run `test_ast_parsing.py` (already created in VAN QA)

---

### Phase 2.2: LangGraph Nodes (2-3 hours)

**Tasks**:
1. Implement `agents/nodes.py` (4 reasoning nodes)
2. Implement `agents/graph_builder.py` (StateGraph construction)
3. Create basic LLM prompts

**Deliverables**:
- Plan, Generate, Verify, Correct nodes
- Graph builder with conditional edges
- Routing logic

**Verification**: Run `test_langgraph_hello.py` with Phase 2 patterns

---

### Phase 2.3: LLM Integration (2-3 hours)

**Tasks**:
1. Implement `agents/llm_clients.py` (Claude client)
2. Create prompt templates for Plan and Generate
3. Add error extraction and feedback generation
4. Update `.env` with API key placeholder

**Deliverables**:
- Claude API integration
- Prompt templates
- Error-to-feedback translation

**Verification**: Manual test with simple code generation task

---

### Phase 2.4: Temporal Integration (2-3 hours)

**Tasks**:
1. Implement `agents/workflows.py` (Temporal workflow)
2. Implement `agents/activities.py` (LangGraph activity)
3. Extend `temporal/workers/worker.py` (register Phase 2)
4. Add heartbeat support for long activities

**Deliverables**:
- CodeGenerationWorkflow
- execute_code_generation_activity
- Worker registration

**Verification**: Run `test_langgraph_temporal.py` (VAN QA test)

---

### Phase 2.5: Integration Testing (1-2 hours)

**Tasks**:
1. Create `scripts/test_code_generation.py`
2. Implement 20-task test suite
3. Track success rates and iterations
4. Document results

**Deliverables**:
- Integration test script
- Test results (95%+ target)
- Performance metrics

**Verification**: 19/20 tasks pass, <2 average iterations

---

### Phase 2.6: Chaos Testing (1-2 hours)

**Tasks**:
1. Create `scripts/chaos_test_phase2.py`
2. Implement kill-during-plan test
3. Implement kill-during-generate test
4. Reuse Phase 1 chaos utils

**Deliverables**:
- Chaos test script
- 2/2 tests passing
- Recovery time metrics

**Verification**: 100% chaos test pass rate

---

## 11. Risk Mitigation

### Risks Addressed in Architecture

| Risk | Mitigation | ADR |
|------|------------|-----|
| R-P2-001: LangGraph learning curve | VAN QA validated, patterns proven | - |
| R-P2-004: Infinite loops | Max iterations (3), conditional edge routing | ADR-007 |
| R-P2-005: LangGraph-Temporal integration | Activity-level imports, validated | ADR-007 |
| R-P2-007: Sandbox restrictions | Import inside activities | ADR-007 |
| R-P2-003: LLM rate limits | Exponential backoff, fallback provider | ADR-008 |

### Remaining Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LLM API costs exceed budget | Low | Medium | Token budgeting, monitoring |
| Claude API outage | Low | High | Gemini fallback (Phase 2.1) |
| AST edge cases | Low | Low | Comprehensive test suite |
| Activity timeout | Medium | Medium | 120s timeout, heartbeats |

---

## 12. Success Metrics

### Primary Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **First-attempt success** | 95%+ | AST verification on 20 tasks |
| **Average iterations** | <2 | Mean across all generations |
| **Chaos tests** | 100% | 2/2 tests pass |
| **200-line compliance** | 100% | All files ≤200 lines |

### Secondary Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Loop time | <30s | End-to-end timing |
| AST parse time | <100ms | Per-verification timing |
| LLM response time | <5s | Per-call timing |
| Files created | ~12 | Count new files |
| Total lines | ~1450 | Sum of new code |

---

## 13. Dependencies

### Phase 1 Dependencies (All Met)

| Dependency | Status | Notes |
|------------|--------|-------|
| Temporal Server | ✅ Running | localhost:7233 |
| PostgreSQL | ✅ Running | Temporal persistence |
| Temporal UI | ✅ Running | localhost:8080 |
| Worker process | ✅ Operational | Extend for Phase 2 |
| Chaos utils | ✅ Available | Reuse 80% |

### New Dependencies

| Dependency | Status | Version |
|------------|--------|---------|
| langgraph | ✅ Installed | 1.0.7 |
| langchain-core | ✅ Installed | 1.2.7 |
| langchain-anthropic | ✅ Installed | 1.3.1 |
| anthropic API key | ⏳ Required | User config |

---

## 14. Conclusion

### Architecture Summary

Phase 2 introduces:
1. **LangGraph cyclic reasoning** (Plan→Generate→Verify→Correct)
2. **Python AST verification** (syntax-only for Phase 2.0)
3. **Claude LLM integration** (with Gemini fallback path)
4. **Temporal durability** (activity-level imports pattern)

### Key Decisions

1. **ADR-007**: LangGraph inside activities (sandbox workaround)
2. **ADR-008**: Claude primary, Gemini fallback
3. **ADR-009**: Syntax-only verification (Phase 2.0)

### Estimated Effort

| Sub-Phase | Estimated | Confidence |
|-----------|-----------|------------|
| 2.1: Core Infrastructure | 2-3h | High |
| 2.2: LangGraph Nodes | 2-3h | High |
| 2.3: LLM Integration | 2-3h | Medium |
| 2.4: Temporal Integration | 2-3h | High |
| 2.5: Integration Testing | 1-2h | High |
| 2.6: Chaos Testing | 1-2h | High |
| **Total** | **10-16h** | **Medium-High** |

### Ready for BUILD

- ✅ VAN Mode: Requirements analyzed
- ✅ VAN QA Mode: Technologies validated (13/13 tests)
- ✅ PLAN Mode: Architecture designed (3 ADRs)
- ⏳ BUILD Mode: Ready to proceed

---

**Document Created**: 2026-01-30  
**Status**: COMPLETE  
**Next Command**: `/build`

---

**"The architecture is designed. The brain is ready to be built."**
