# Adaptive AI Integration Platform

**Version**: 0.1.0-alpha (Phase 0 Complete)  
**Status**: 🏗️ In Active Development  
**Last Updated**: 2026-01-30

---

## 🎯 Vision

Build a "Self-Driving Enterprise" platform that transitions from static, deterministic automation (RPA) to dynamic, probabilistic **Agentic AI**. The system acts as a central nervous system, capable of Universal Integration, Adaptive Business Automation, and Strategic Interaction.

## 🔑 Core Innovation: Solving the Three Gaps

### 1. The State Gap (Durability) ✅
**Problem**: Agents die when servers restart  
**Solution**: Temporal.io enables "Agent Continuations" - workflows survive crashes and can sleep for days awaiting human approval

### 2. The Syntax Gap (Reliability) ✅
**Problem**: LLMs generate broken code  
**Solution**: Verification Layer using Python's `ast` module and Gorilla LLM to mathematically parse and validate API calls before execution

### 3. The Context Gap (Memory) ✅
**Problem**: Agents lack business awareness  
**Solution**: Process Intelligence (Celonis-style logs) and Permissions-Aware RAG stored in Supabase, ensuring agents act on "ground truth"

---

## 🏗️ Architecture: 4-Layer Stack

### Layer 1: The Connectivity Fabric (Integration)
- **Goal**: Universal N-to-N API integration without writing thousands of connectors
- **Core Logic**: Unified Schema Engine mapping niche APIs to canonical models
- **Tech**: Supabase PostgreSQL + Gorilla LLM

### Layer 2: The Cognitive Orchestration (The Brain)
- **Goal**: Manage complex reasoning loops and survive timeouts
- **Core Logic**: Cyclic Reasoning (Plan → Act → Observe → Correct)
- **Tech**: Temporal.io + LangGraph

### Layer 3: The Intelligence Layer (Memory & Verification)
- **Goal**: Eliminate hallucinations and invalid code execution
- **Core Logic**: AST Verification & Contextual Anchoring
- **Tech**: Python `ast` + Supabase pgvector + RLS

### Layer 4: The Strategic Interface (Control Room)
- **Goal**: High-bandwidth human-in-the-loop governance
- **Core Logic**: "Matrix UI" - spreadsheet-like grid for Propose & Approve workflows
- **Tech**: Next.js + AG Grid + Supabase Realtime

---

## 📚 Project Structure

```
orion-ai/
├── memory-bank/              # AI context and project memory
│   ├── creative/            # Design phase documents
│   ├── reflection/          # Post-implementation reviews
│   └── archive/             # Completed task archives
├── cursor-memory-bank/      # Cursor AI rules system
├── build_plan/              # Architecture and planning docs
│   ├── phase0-architecture.md
│   ├── roadmap.md
│   └── qa-validation-report.md
├── scripts/                 # Setup automation (Phase 0)
├── services/                # Business logic modules
├── utils/                   # Helper functions
├── temporal/                # Workflow definitions
├── connectors/              # API adapters
├── frontend/                # Next.js Matrix UI
└── docker/                  # Container configs
```

---

## 🚀 Quick Start

### Phase 0: Initialization (Current)

**Prerequisites:**
- Python 3.11+
- Bash 5.0+
- Git 2.0+
- Node.js 18+ (for frontend, Phase 4)

**Setup:**
```bash
# Complete automated setup
bash scripts/run-all.sh

# Or run individual scripts
bash scripts/setup-directories.sh
python scripts/generate-rules.py
python scripts/validate-setup.py
```

### Future Phases

**Phase 1**: Temporal.io integration (durable workflows)  
**Phase 2**: LangGraph + AST verification (reliable brain)  
**Phase 3**: Supabase pgvector + RLS (secure context)  
**Phase 4**: Next.js Matrix UI (command center)

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|----------|
| **Backend** | Python 3.11+ FastAPI | AI libraries + AST parsing |
| **Database** | Supabase PostgreSQL | Unified platform (Auth + DB + Realtime) |
| **Vector Search** | pgvector | Semantic search for RAG |
| **Workflows** | Temporal.io | Durable execution engine |
| **Agents** | LangGraph | Cyclic reasoning loops |
| **Frontend** | Next.js 14+ | Modern React framework |
| **UI Grid** | AG Grid Enterprise | Matrix UI visualization |
| **Verification** | Python `ast` | Syntax validation |
| **AI Models** | Claude 3.5 Sonnet | Reasoning & coding |
| **Function Calling** | Gorilla / xLAM | API payload generation |

---

## 📋 Development Principles

### The 200-Line Rule
**MANDATORY**: Any file exceeding 200 lines must be immediately refactored into `services/` or `utils/`

### Zero Tech Debt Policy
- Modular code enforced from Day 1
- No shortcuts or temporary solutions
- Immediate refactoring when complexity increases

### Security First
- RLS enabled by default on all user-facing tables
- ACL filtering before LLM context generation
- Credentials in environment variables (never committed)

### Test-Driven Development
- Minimum 80% coverage for production code
- Chaos tests for Temporal workflows
- Integration tests for all API endpoints

---

## 📖 Documentation

- **Architecture**: `build_plan/phase0-architecture.md`
- **Roadmap**: `build_plan/roadmap.md`
- **QA Report**: `build_plan/qa-validation-report.md`
- **Memory Bank**: `memory-bank/` (AI context system)
- **Creative Designs**: `memory-bank/creative/`

---

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest services/ utils/

# Integration tests
pytest tests/integration/

# Chaos tests (Temporal workflows)
pytest tests/chaos/
```

### Coverage
```bash
pytest --cov=services --cov=utils --cov-report=html
```

---

## 🤝 Contributing

This project follows a structured development methodology:

1. **VAN Mode**: Initialization and complexity assessment
2. **PLAN Mode**: Architectural planning and documentation
3. **CREATIVE Mode**: Design decisions for complex components
4. **VAN QA Mode**: Technology validation before implementation
5. **BUILD Mode**: Phased implementation with verification
6. **REFLECT Mode**: Post-implementation review
7. **ARCHIVE Mode**: Knowledge preservation

See `cursor-memory-bank/` for detailed workflow documentation.

---

## 📊 Current Status

**Phase 0 Progress**: 80% Complete

- ✅ Initialization (VAN Mode)
- ✅ Architectural Planning (PLAN Mode)
- ✅ Design Phases (CREATIVE Mode)
- ✅ Technology Validation (VAN QA Mode)
- 🔄 Implementation (BUILD Mode - In Progress)
- ⏳ Reflection (REFLECT Mode)
- ⏳ Archiving (ARCHIVE Mode)

**Next Milestone**: Complete Phase 0 setup scripts and rule generation

---

## 🔗 Resources

- [Temporal.io Documentation](https://docs.temporal.io/)
- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [Supabase Docs](https://supabase.com/docs)
- [AG Grid](https://www.ag-grid.com/)

---

## 📄 License

[License to be determined]

---

## 👥 Team

Built with Cursor AI and Claude 4.0 Sonnet

---

**"From Static Automation to Agentic Intelligence"**
