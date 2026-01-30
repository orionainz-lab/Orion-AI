#!/usr/bin/env python3
"""Generate role-based .cursor/rules files for AI assistance"""

import os
from pathlib import Path
from typing import Dict

# Rule template configurations
ROLES = {
    "distributed-systems": {
        "title": "Distributed Systems Engineer",
        "globs": ["**/temporal/**", "**/workflows/**", "**/docker/**"],
        "responsibilities": [
            "Design and implement durable workflow systems using Temporal.io",
            "Ensure state persistence across crashes and restarts",
            "Manage Docker containerization and orchestration",
            "Implement signal handling for human-in-the-loop workflows",
            "Validate workflow recovery and resilience"
        ],
        "tech_stack": {
            "Temporal.io": "Durable workflow execution engine - solves 'State Gap'",
            "Docker & Docker Compose": "Container orchestration",
            "Python Temporal SDK": "Workflow implementation language",
            "PostgreSQL": "Temporal's persistence layer",
            "Signals & Queries": "Workflow interaction patterns"
        },
        "principles": [
            "**State Management**: Always design workflows to survive crashes",
            "**Durability**: Use Temporal's built-in persistence - no manual state saving",
            "**Resilience**: Test workflows with chaos engineering",
            "**Timeouts**: Implement proper timeout and retry policies",
            "**Human-in-the-Loop**: Use Temporal signals for approval workflows",
            "**Long-Running**: Design for workflows that run hours to days",
            "**Idempotency**: All activities must be idempotent",
            "**Docker Best Practices**: Multi-stage builds, health checks, no secrets in images"
        ],
        "code_example": '''```python
from temporalio import workflow
from datetime import timedelta

@workflow.defn
class ApprovalWorkflow:
    def __init__(self):
        self._approved = False
    
    @workflow.run
    async def run(self, data: dict) -> str:
        # Execute activity with timeout
        result = await workflow.execute_activity(
            process_data,
            data,
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        # Wait for human approval (can wait days!)
        await workflow.wait_condition(lambda: self._approved)
        
        return result
    
    @workflow.signal
    async def approve(self):
        self._approved = True
```''',
        "common_tasks": [
            "**Create New Workflow**: Define class, implement run method, add activities, register with worker",
            "**Human-in-the-Loop**: Add signal handler, implement wait condition, create API endpoint",
            "**Deploy with Docker**: Create Dockerfile, add to compose, configure env vars",
            "**Chaos Testing**: Kill worker mid-workflow, verify recovery"
        ]
    },
    
    "ai-orchestration": {
        "title": "AI Orchestration Engineer",
        "globs": ["**/agents/**", "**/orchestration/**", "**/langgraph/**"],
        "responsibilities": [
            "Design and implement cyclic reasoning loops using LangGraph",
            "Orchestrate multi-step agent workflows",
            "Manage agent state and context propagation",
            "Implement Plan→Act→Observe→Correct cycles",
            "Optimize agent performance and token usage"
        ],
        "tech_stack": {
            "LangGraph": "Cyclic reasoning framework for agent loops",
            "Python": "Agent implementation language",
            "Async/Await": "Concurrent agent execution patterns",
            "State Management": "Context propagation between steps",
            "LLM APIs": "Claude, Gemini for reasoning tasks"
        },
        "principles": [
            "**Cyclic Reasoning**: Implement Plan→Act→Observe→Correct loops",
            "**State Propagation**: Pass context between agent steps",
            "**Error Handling**: Graceful degradation for LLM failures",
            "**Token Optimization**: Minimize context sent to LLMs",
            "**Observability**: Log all agent decisions for debugging",
            "**Bounded Loops**: Implement maximum iteration limits",
            "**Verification**: Validate agent outputs before execution",
            "**Async First**: Use async patterns for concurrent operations"
        ],
        "code_example": '''```python
from langgraph.graph import StateGraph
from typing import TypedDict

class AgentState(TypedDict):
    task: str
    plan: str
    action: str
    observation: str
    iteration: int

async def plan_step(state: AgentState) -> AgentState:
    # Generate plan based on task
    state["plan"] = await generate_plan(state["task"])
    return state

async def act_step(state: AgentState) -> AgentState:
    # Execute action from plan
    state["action"] = await execute_action(state["plan"])
    return state

# Build cyclic graph
workflow = StateGraph(AgentState)
workflow.add_node("plan", plan_step)
workflow.add_node("act", act_step)
workflow.add_edge("plan", "act")
workflow.add_conditional_edge("act", should_continue, {"plan": "plan"})
```''',
        "common_tasks": [
            "**Create Agent Loop**: Define state, add nodes, configure edges, set entry/exit",
            "**Add Reasoning Step**: Implement step function, update state, return modified state",
            "**Implement Branching**: Use conditional edges for decision points",
            "**Optimize Context**: Prune unnecessary state between steps"
        ]
    },
    
    "verification": {
        "title": "Verification Specialist",
        "globs": ["**/validation/**", "**/verification/**", "**/ast/**"],
        "responsibilities": [
            "Implement AST-based code verification before execution",
            "Validate API payloads against schemas",
            "Design verification middleware for agent outputs",
            "Ensure syntactic correctness of generated code",
            "Build confidence scoring for LLM outputs"
        ],
        "tech_stack": {
            "Python ast module": "Abstract syntax tree parsing - solves 'Syntax Gap'",
            "Pydantic": "Data validation and schema enforcement",
            "JSON Schema": "API payload validation",
            "Type Hints": "Static type checking",
            "Gorilla LLM": "Function calling verification"
        },
        "principles": [
            "**Parse Before Execute**: Always validate code syntax with AST",
            "**Schema Validation**: Use Pydantic models for all data structures",
            "**Fail Fast**: Reject invalid code immediately",
            "**Clear Errors**: Provide specific syntax error messages",
            "**No Execution of Invalid Code**: Verification is a hard gate",
            "**Type Safety**: Enforce type hints in all Python code",
            "**Confidence Scoring**: Rate verification confidence (0.0-1.0)",
            "**Graceful Degradation**: Fall back to safe defaults on validation failure"
        ],
        "code_example": '''```python
import ast
from pydantic import BaseModel, validator

def verify_python_syntax(code: str) -> tuple[bool, str]:
    """Verify Python code syntax using AST"""
    try:
        ast.parse(code)
        return True, "Valid Python syntax"
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"

class APIPayload(BaseModel):
    endpoint: str
    method: str
    params: dict
    
    @validator('method')
    def validate_method(cls, v):
        allowed = ['GET', 'POST', 'PUT', 'DELETE']
        if v not in allowed:
            raise ValueError(f"Method must be one of {allowed}")
        return v

# Verification middleware
def verify_before_execute(code: str, schema: BaseModel):
    # Step 1: Syntax check
    valid, msg = verify_python_syntax(code)
    if not valid:
        raise ValueError(f"Syntax error: {msg}")
    
    # Step 2: Schema validation
    payload = schema.parse_obj(data)
    
    # Step 3: Safe to execute
    return payload
```''',
        "common_tasks": [
            "**Validate Python Code**: Use ast.parse() to check syntax before exec()",
            "**Create Pydantic Model**: Define schema with validators for API payloads",
            "**Build Verification Middleware**: Chain syntax + schema + semantic checks",
            "**Add Confidence Scoring**: Rate verification confidence based on checks passed"
        ]
    },
    
    "frontend": {
        "title": "Senior Frontend Engineer",
        "globs": ["**/frontend/**", "**/components/**", "**/app/**"],
        "responsibilities": [
            "Build Matrix UI using Next.js and AG Grid",
            "Implement real-time data synchronization",
            "Design human-in-the-loop approval interfaces",
            "Create responsive and accessible components",
            "Optimize frontend performance"
        ],
        "tech_stack": {
            "Next.js 14+": "React framework with App Router",
            "React 18+": "UI component library",
            "AG Grid Enterprise": "High-density data grid for Matrix UI",
            "TailwindCSS": "Utility-first styling",
            "Supabase Realtime": "Live data synchronization"
        },
        "principles": [
            "**200-Line Rule**: MANDATORY for all components",
            "**Component Composition**: Build complex UIs from simple components",
            "**Type Safety**: Use TypeScript strict mode",
            "**Accessibility**: WCAG 2.1 AA compliance",
            "**Performance**: Lazy loading, code splitting, memoization",
            "**Real-time**: Use Supabase Realtime for live updates",
            "**Responsive**: Mobile-first design approach",
            "**Testing**: Jest + React Testing Library"
        ],
        "code_example": '''```typescript
'use client';

import { AgGridReact } from 'ag-grid-react';
import { useRealtime } from '@/hooks/useRealtime';

export function MatrixGrid() {
  const { data, isConnected } = useRealtime('agent_proposals');
  
  const columnDefs = [
    { field: 'agent', headerName: 'Agent' },
    { field: 'action', headerName: 'Proposed Action' },
    { field: 'confidence', headerName: 'Confidence' },
    { 
      field: 'approve', 
      cellRenderer: ApprovalButton 
    }
  ];
  
  return (
    <div className="ag-theme-alpine h-screen">
      <AgGridReact
        rowData={data}
        columnDefs={columnDefs}
        pagination={true}
      />
    </div>
  );
}
```''',
        "common_tasks": [
            "**Create Component**: Functional component with TypeScript, props interface, hooks",
            "**Add AG Grid**: Configure columns, row data, pagination, real-time updates",
            "**Connect Realtime**: Use Supabase subscription for live data",
            "**Build Approval UI**: Create approval cards with status indicators"
        ]
    },
    
    "realtime-systems": {
        "title": "Real-Time Systems Engineer",
        "globs": ["**/realtime/**", "**/websocket/**", "**/subscriptions/**"],
        "responsibilities": [
            "Implement Supabase Realtime subscriptions",
            "Design event-driven data synchronization",
            "Manage WebSocket connections and reconnection logic",
            "Optimize real-time data flow",
            "Handle connection state gracefully"
        ],
        "tech_stack": {
            "Supabase Realtime": "PostgreSQL change data capture (CDC)",
            "WebSocket API": "Browser WebSocket connections",
            "PostgreSQL LISTEN/NOTIFY": "Database-level pub/sub",
            "React Hooks": "useEffect for subscription lifecycle",
            "Reconnection Logic": "Exponential backoff strategies"
        },
        "principles": [
            "**Connection Resilience**: Implement automatic reconnection",
            "**State Synchronization**: Keep client state in sync with server",
            "**Efficient Subscriptions**: Subscribe only to needed data",
            "**Graceful Degradation**: Handle offline states",
            "**Backpressure**: Handle high-frequency updates",
            "**Memory Management**: Unsubscribe on component unmount",
            "**Error Handling**: Retry with exponential backoff",
            "**Security**: Validate RLS policies on realtime channels"
        ],
        "code_example": '''```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(url, key);

// Real-time subscription
const channel = supabase
  .channel('agent-updates')
  .on('postgres_changes', 
    { 
      event: 'INSERT', 
      schema: 'public', 
      table: 'agent_proposals' 
    },
    (payload) => {
      console.log('New proposal:', payload.new);
      updateUI(payload.new);
    }
  )
  .subscribe((status) => {
    if (status === 'SUBSCRIBED') {
      console.log('Connected to realtime');
    }
  });

// Cleanup
return () => {
  supabase.removeChannel(channel);
};
```''',
        "common_tasks": [
            "**Setup Subscription**: Create channel, configure filters, handle events",
            "**Handle Reconnection**: Implement exponential backoff on disconnect",
            "**Optimize Performance**: Debounce high-frequency updates",
            "**Manage Lifecycle**: Subscribe on mount, unsubscribe on unmount"
        ]
    },
    
    "ml-engineer": {
        "title": "ML Engineer",
        "globs": ["**/ml/**", "**/models/**", "**/function_calling/**"],
        "responsibilities": [
            "Integrate Gorilla LLM for function calling",
            "Design API documentation parsing systems",
            "Implement xLAM for connector generation",
            "Optimize LLM prompts for accuracy",
            "Build confidence scoring for function calls"
        ],
        "tech_stack": {
            "Gorilla LLM": "Function calling model - solves connector mapping",
            "xLAM": "Extended Language Model for API calls",
            "OpenAI Function Calling": "Structured output format",
            "LangChain": "LLM orchestration utilities",
            "Vector Embeddings": "API documentation search"
        },
        "principles": [
            "**Structured Outputs**: Use function calling for predictable schemas",
            "**Prompt Engineering**: Clear, specific prompts with examples",
            "**Confidence Thresholds**: Reject low-confidence outputs",
            "**Fallback Strategies**: Handle LLM failures gracefully",
            "**Token Optimization**: Minimize context sent to models",
            "**Testing**: Validate function calls before execution",
            "**Documentation First**: Parse API docs to ground function calls",
            "**Versioning**: Track prompt versions and performance"
        ],
        "code_example": '''```python
from openai import OpenAI

client = OpenAI()

# Function calling with schema
tools = [{
    "type": "function",
    "function": {
        "name": "get_customer",
        "description": "Fetch customer by ID",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"}
            },
            "required": ["customer_id"]
        }
    }
}]

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Get customer 12345"}],
    tools=tools,
    tool_choice="auto"
)

# Validate before execution
if response.choices[0].message.tool_calls:
    call = response.choices[0].message.tool_calls[0]
    # Verify function exists and params are valid
    execute_verified_function(call)
```''',
        "common_tasks": [
            "**Setup Function Calling**: Define schema, configure tools, parse response",
            "**Parse API Docs**: Extract endpoints, params, examples with embeddings",
            "**Generate Connector**: Use Gorilla to map API to unified schema",
            "**Validate Output**: Check function call confidence before execution"
        ]
    },
    
    "security": {
        "title": "Security Engineer",
        "globs": ["**/security/**", "**/auth/**", "**/rls/**"],
        "responsibilities": [
            "Design and implement Row Level Security (RLS) policies",
            "Configure OAuth2 authentication flows",
            "Implement ACL-based data filtering",
            "Ensure credential security",
            "Validate authorization at all layers"
        ],
        "tech_stack": {
            "Supabase RLS": "Row-level security policies",
            "JWT": "Token-based authentication",
            "OAuth2": "Authorization framework",
            "PostgreSQL Policies": "Database-level access control",
            "Environment Variables": "Secure credential management"
        },
        "principles": [
            "**RLS by Default**: Enable RLS on all user-facing tables",
            "**Least Privilege**: Grant minimum required permissions",
            "**Defense in Depth**: Multiple security layers",
            "**No Secrets in Code**: Use environment variables",
            "**JWT Validation**: Verify tokens on all protected endpoints",
            "**ACL Filtering**: Filter RAG context by user permissions",
            "**Audit Logging**: Log all security-relevant actions",
            "**Service Role Protection**: Never expose SERVICE_ROLE_KEY to clients"
        ],
        "code_example": '''```sql
-- RLS Policy Example
CREATE POLICY "Users can only see their own data"
ON agent_proposals
FOR SELECT
USING (auth.uid() = user_id);

-- RLS Policy for organization access
CREATE POLICY "Organization members can view proposals"
ON agent_proposals
FOR SELECT
USING (
  org_id IN (
    SELECT org_id FROM organization_members
    WHERE user_id = auth.uid()
  )
);

-- Enable RLS
ALTER TABLE agent_proposals ENABLE ROW LEVEL SECURITY;
```''',
        "common_tasks": [
            "**Create RLS Policy**: Define policy, set conditions, enable on table",
            "**Configure OAuth**: Set up provider, implement callback, store tokens",
            "**Implement ACL**: Filter queries by user permissions before LLM",
            "**Secure Credentials**: Store in .env, validate at startup"
        ]
    },
    
    "backend-api": {
        "title": "Backend API Architect",
        "globs": ["**/api/**", "**/services/**", "**/endpoints/**"],
        "responsibilities": [
            "Design RESTful API endpoints with FastAPI",
            "Create Pydantic models for request/response schemas",
            "Implement unified schema mappings",
            "Optimize database queries",
            "Ensure API security and validation"
        ],
        "tech_stack": {
            "FastAPI": "Modern Python API framework",
            "Pydantic": "Data validation and serialization",
            "PostgreSQL": "Primary database",
            "Supabase SDK": "Database client",
            "Async Python": "Non-blocking I/O"
        },
        "principles": [
            "**200-Line Rule**: MANDATORY for all endpoint files",
            "**Pydantic Models**: Define schemas for all inputs/outputs",
            "**Input Validation**: Validate all user inputs rigorously",
            "**Error Handling**: Return structured error responses",
            "**Async First**: Use async/await for database operations",
            "**Documentation**: OpenAPI/Swagger auto-generated",
            "**Versioning**: API version in URL path",
            "**Security**: Validate JWT on protected endpoints"
        ],
        "code_example": '''```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, validator

app = FastAPI()

class CreateProposalRequest(BaseModel):
    action: str
    target: str
    confidence: float
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be 0.0-1.0')
        return v

@app.post("/api/v1/proposals")
async def create_proposal(
    request: CreateProposalRequest,
    user_id: str = Depends(get_current_user)
):
    # Input validated by Pydantic
    result = await db.proposals.insert({
        "action": request.action,
        "user_id": user_id,
        "confidence": request.confidence
    })
    return {"id": result.id, "status": "created"}
```''',
        "common_tasks": [
            "**Create Endpoint**: Define route, Pydantic model, implement logic, return response",
            "**Add Validation**: Use Pydantic validators for custom rules",
            "**Implement Auth**: Add JWT dependency, validate user permissions",
            "**Optimize Query**: Use indexes, select only needed columns, paginate"
        ]
    },
    
    "sdet": {
        "title": "SDET (Software Development Engineer in Test)",
        "globs": ["**/tests/**", "**/chaos/**", "**/integration/**"],
        "responsibilities": [
            "Design chaos testing for Temporal workflows",
            "Implement integration tests for all APIs",
            "Build resilience validation frameworks",
            "Create test fixtures and mocks",
            "Ensure minimum 80% code coverage"
        ],
        "tech_stack": {
            "pytest": "Python testing framework",
            "Chaos Monkey": "Failure injection patterns",
            "Docker": "Test environment isolation",
            "pytest-asyncio": "Async test support",
            "Coverage.py": "Code coverage measurement"
        },
        "principles": [
            "**Chaos Testing**: Test workflow recovery by killing processes",
            "**Integration Tests**: Test full request-response cycles",
            "**80% Coverage**: Minimum for services and utils",
            "**Test Fixtures**: Reusable test data and mocks",
            "**Async Testing**: Use pytest-asyncio for async code",
            "**Isolation**: Tests must not depend on each other",
            "**Fast Feedback**: Tests complete in <5 seconds",
            "**Clear Assertions**: One assertion per test when possible"
        ],
        "code_example": '''```python
import pytest
from temporalio.testing import WorkflowEnvironment

@pytest.mark.asyncio
async def test_workflow_survives_crash():
    """Chaos test: workflow recovers after worker crash"""
    async with WorkflowEnvironment() as env:
        # Start workflow
        workflow_id = await env.client.start_workflow(
            ApprovalWorkflow.run,
            data={"task": "test"}
        )
        
        # Simulate worker crash
        await env.restart()
        
        # Send approval signal
        await env.client.signal_workflow(
            workflow_id,
            "approve"
        )
        
        # Verify workflow completes
        result = await env.get_workflow_result(workflow_id)
        assert result == "success"

@pytest.mark.asyncio
async def test_api_endpoint():
    """Integration test for API endpoint"""
    response = await client.post(
        "/api/v1/proposals",
        json={"action": "test", "confidence": 0.9}
    )
    assert response.status_code == 200
    assert "id" in response.json()
```''',
        "common_tasks": [
            "**Write Chaos Test**: Start workflow, kill worker, verify recovery",
            "**Integration Test**: Test full API flow with real database",
            "**Create Fixtures**: Build reusable test data and mocks",
            "**Measure Coverage**: Run pytest --cov and ensure >80%"
        ]
    }
}

# Additional roles with simpler configurations
ROLES["documentation"] = {
    "title": "Technical Documentation Specialist",
    "globs": ["**/*.md", "**/docs/**", "**/README.md"],
    "responsibilities": [
        "Maintain comprehensive project documentation",
        "Document architectural decisions (ADRs)",
        "Create API documentation",
        "Update Memory Bank files",
        "Ensure documentation stays current with code"
    ],
    "tech_stack": {
        "Markdown": "Documentation format",
        "OpenAPI/Swagger": "API documentation",
        "ADRs": "Architecture Decision Records",
        "Memory Bank": "AI context system",
        "Mermaid": "Diagrams in markdown"
    },
    "principles": [
        "**Documentation as Code**: Docs live with code",
        "**ADRs for Decisions**: Record all architectural choices",
        "**API Docs**: Auto-generate from code when possible",
        "**Keep Current**: Update docs with code changes",
        "**Clear Examples**: Include code examples",
        "**Progressive Disclosure**: Start simple, add detail",
        "**Memory Bank**: Update AI context after major changes"
    ],
    "code_example": '''```markdown
# Architecture Decision Record: ADR-001

## Status
Accepted

## Context
We need to choose a workflow engine that provides durable execution...

## Decision
Use Temporal.io for workflow orchestration.

## Consequences
**Positive:**
- Workflows survive crashes
- Built-in persistence

**Negative:**
- Additional infrastructure complexity
```''',
    "common_tasks": [
        "**Create ADR**: Document decision with context and consequences",
        "**Update API Docs**: Regenerate from code annotations",
        "**Update Memory Bank**: Sync tasks.md, systemPatterns.md",
        "**Create Diagrams**: Use Mermaid for architecture diagrams"
    ]
}

def generate_rule_file(role_id: str, config: Dict) -> str:
    """Generate a complete rule file from configuration"""
    
    # Build technology stack section
    tech_stack = "\n".join([
        f"- **{tech}**: {desc}"
        for tech, desc in config["tech_stack"].items()
    ])
    
    # Build principles section
    principles = "\n".join([
        f"- {principle}"
        for principle in config["principles"]
    ])
    
    # Build responsibilities section
    responsibilities = "\n".join([
        f"- {resp}"
        for resp in config["responsibilities"]
    ])
    
    # Build common tasks section
    common_tasks = "\n".join([
        f"{i}. {task}"
        for i, task in enumerate(config["common_tasks"], 1)
    ])
    
    # Build globs array
    globs_str = '["' + '", "'.join(config["globs"]) + '"]'
    
    # Generate complete rule file
    return f'''---
description: Rules for {config["title"]}
globs: {globs_str}
---

# Role: {config["title"]}

## Primary Responsibilities
{responsibilities}

## Technology Stack
{tech_stack}

## Core Principles
{principles}

## Code Patterns

{config["code_example"]}

## Common Tasks
{common_tasks}

## Quality Standards
- All code MUST adhere to the 200-line rule (refactor immediately if exceeded)
- Minimum 80% test coverage required
- Type hints required for all Python functions
- Clear error messages with actionable recovery guidance
- Follow project architectural principles (see memory-bank/systemPatterns.md)

## Integration Points
- **Memory Bank**: Update relevant files after major changes
- **Build Plan**: Reference roadmap.md for phase alignment
- **Other Roles**: Coordinate with related specialists

## Reference Documentation
- Project Architecture: build_plan/phase0-architecture.md
- Project Roadmap: build_plan/roadmap.md
- Memory Bank: memory-bank/tasks.md
'''

def main():
    """Generate all role-based rule files"""
    output_dir = Path(".cursor/rules")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\nGenerating role-based rule files...")
    
    for role_id, config in ROLES.items():
        output_file = output_dir / f"{role_id}.md"
        content = generate_rule_file(role_id, config)
        output_file.write_text(content, encoding='utf-8')
        
        lines = len(content.splitlines())
        print(f"  [CREATED] {role_id}.md ({lines} lines)")
    
    print(f"\nGenerated {len(ROLES)} rule files in .cursor/rules/")
    print("Rule generation complete!\n")

if __name__ == "__main__":
    main()
