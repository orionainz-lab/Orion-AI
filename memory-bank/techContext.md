# Memory Bank: Technical Context

## Technology Stack

### Backend Framework
- **Primary**: Python (FastAPI)
- **Rationale**: Required for AI libraries (Pandas/PyTorch) and AST parsing

### Infrastructure
- **Primary**: Supabase
- **Components**: Auth, PostgreSQL, Vector Search (pgvector), Realtime
- **Rationale**: Unified platform reduces infrastructure fragmentation

### Workflow Engine
- **Primary**: Temporal.io
- **Purpose**: Durable Execution and Replay History
- **Critical For**: Agent state persistence across crashes

### Agent Framework
- **Primary**: LangGraph
- **Purpose**: Cyclic reasoning loops and multi-agent state management

### Frontend
- **Primary**: Next.js + AG Grid
- **Purpose**: "Matrix UI" for high-density data visualization

### Verification
- **Primary**: Python `ast` module
- **Purpose**: Syntax validation for AI-generated code

### AI Models
- **Reasoning**: Claude 3.5 Sonnet (complex logic)
- **Function Calling**: Gorilla / xLAM (API payloads)
- **Context**: Gemini 1.5 Pro (long document analysis)

## Development Environment
- **IDE**: Cursor AI
- **MCPs**: Supabase MCP, Brave Search, Chrome Dev Tools
- **Code Hygiene**: 200-line file limit, zero tech debt policy
