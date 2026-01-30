Here is the consolidated **Master Execution Plan**. It synthesizes the architectural theory from the whitepaper, the engineering blueprint, and the specific "Cursor Context" requirements into a single execution guide.

***

# Master Execution Plan: Adaptive AI Integration Platform

## 1. Executive Vision & Core Strategy

**Objective:** Build a "Self-Driving Enterprise" platform that transitions from static, deterministic automation (RPA) to dynamic, probabilistic **Agentic AI**. The system acts as a central nervous system, capable of Universal Integration, Adaptive Business Automation, and Strategic Interaction.

### The "Three Gaps" Strategy
To succeed where generic agent builders fail, this platform addresses three specific engineering deficits identified in the *Architectures of Autonomy* research:

1.  **The State Gap (Durability):** Agents typically die when servers restart. We solve this with **Temporal.io**, enabling "Agent Continuations" where workflows survive crashes and can sleep for days awaiting human approval.
2.  **The Syntax Gap (Reliability):** LLMs generate broken code. We solve this with a **Verification Layer** using Python’s `ast` module and **Gorilla LLM** to mathematically parse and validate API calls before execution.
3.  **The Context Gap (Memory):** Agents lack business awareness. We solve this with **Process Intelligence** (Celonis-style logs) and **Permissions-Aware RAG** stored in **Supabase**, ensuring agents act on "ground truth."

---

## 2. Technical Architecture (The 4-Layer Stack)

The architecture is consolidated around **Supabase** to reduce infrastructure fragmentation, while retaining the rigorous logic of the original design.

### Layer 1: The Connectivity Fabric (Integration)
*   **Goal:** Solve the "N-to-N Integration" problem without writing 30,000 unique connectors.
*   **Core Logic:** **Unified Schema Engine.** Map niche APIs to canonical models (e.g., `Unified.create_contact`).
*   **Key Tech:**
    *   **Supabase PostgreSQL:** Stores the Unified Schema and entity mappings.
    *   **Gorilla LLM:** Reads raw API documentation and auto-generates the connector mapping logic.

### Layer 2: The Cognitive Orchestration (The Brain)
*   **Goal:** Solve timeout issues and manage complex reasoning loops.
*   **Core Logic:** **Cyclic Reasoning.** Instead of linear scripts, agents loop: *Plan $\rightarrow$ Act $\rightarrow$ Observe $\rightarrow$ Correct*.
*   **Key Tech:**
    *   **Temporal.io:** Provides the "Durable Execution Engine" to persist state to Supabase.
    *   **LangGraph:** Manages the cyclic graph logic and multi-agent shared state.

### Layer 3: The Intelligence Layer (Memory & Verification)
*   **Goal:** Eliminate hallucinations and invalid code execution.
*   **Core Logic:** **AST Verification & Contextual Anchoring.**
*   **Key Tech:**
    *   **Python `ast` module:** Middleware that parses AI output into an Abstract Syntax Tree to verify syntax validity.
    *   **Supabase pgvector:** Stores embedded business context and process logs (RAG).
    *   **Supabase RLS:** Enforces Access Control Lists (ACLs) at the query level for security.

### Layer 4: The Strategic Interface (The Control Room)
*   **Goal:** Governance and high-bandwidth collaboration.
*   **Core Logic:** **"The Matrix" UI.** A spreadsheet-like grid for "Propose & Approve" workflows (Human-in-the-Loop).
*   **Key Tech:**
    *   **Next.js + AG Grid:** Renders thousands of "Logic Function" cards and data rows.
    *   **Supabase Realtime:** Pushes WebSocket updates to the UI when agents enter a "Waiting for Approval" state.

---

## 3. Detailed Bill of Materials (The Cursor Stack)

| Component | Technology | Role in Architecture |
| :--- | :--- | :--- |
| **Backend Framework** | **Python (FastAPI)** | Required for AI libraries (Pandas/PyTorch) and AST parsing. |
| **Infrastructure** | **Supabase** | Unifies Auth, Database, Vector Search, and Realtime Sync. |
| **Workflow Engine** | **Temporal.io** | Critical. Handles "Durable Execution" and Replay History. |
| **Agent Framework** | **LangGraph** | Manages "Cyclic Reasoning" loops and multi-agent state. |
| **Frontend** | **Next.js + AG Grid** | Renders the "Matrix UI" and citation layers. |
| **Verification** | **Python `ast`** | Implements the "Verification Layer" to validate AI syntax. |
| **Reasoning Model** | **Claude 3.5 Sonnet** | Best-in-class for coding and complex logic. |
| **Function Model** | **Gorilla / xLAM** | Specialized endpoint for generating valid API JSON payloads. |
| **Context Model** | **Gemini 1.5 Pro** | Huge context window for analyzing long logs/docs. |

---

## 4. Personnel & Roles (Agent Assignments)

When using Cursor AI, distinct "Personas" should be adopted based on the active file or task type.

| Role | Primary Tech | Critical Responsibility |
| :--- | :--- | :--- |
| **1. Distributed Systems Eng** | Temporal, Docker | **The "State" Keeper.** Builds the engine to ensure agents survive crashes. |
| **2. AI Orchestration Eng** | LangGraph, Python | **The "Brain" Builder.** Designs Plan/Act/Observe loops. |
| **3. Verification Specialist** | Python `ast` | **The "Syntax" Validator.** Writes the `syntax_checker.py` middleware. |
| **4. Senior Frontend Eng** | Next.js, AG Grid | **The "Matrix" Architect.** Builds the "Propose & Approve" grid UI. |
| **5. Real-Time Systems Eng** | WebSockets | **The "Live" Wire.** Connects Supabase Realtime to the Frontend. |
| **6. ML Engineer** | Gorilla, xLAM | **The "Tool" Tuner.** Integrates function-calling specific models. |
| **7. Security Engineer** | RLS, OAuth2 | **The "Gatekeeper."** Implements ACLs to prevent data leaks in RAG. |
| **8. Backend API Architect** | Pydantic, FastAPI | **The "Schema" Mapper.** Defines the "Unified Models" (N-to-N solution). |
| **9. SDET** | Chaos Monkey | **The "Resilience" Tester.** Crashes servers to prove workflow recovery. |

---

## 5. Development Methodology & Hygiene

### The "Self-Driving" Build Method
1.  **Environment:** Project executed entirely inside **Cursor AI**.
2.  **Tools (MCPs):**
    *   *Supabase MCP:* For direct schema/vector management.
    *   *Brave Search:* For fetching live Temporal/LangGraph docs.
    *   *Chrome Dev Tools:* For validating the Matrix UI.
3.  **Atomic Tasks:** Work is broken down into small, isolated units checked against the roadmap.

### Code Hygiene Rules
*   **The 200-Line Rule:** Any file exceeding 200 lines must be immediately refactored into `services/` or `utils/`.
*   **Zero Tech Debt:** Modular code is enforced from Day 1.
*   **Documentation:** A master `build_plan/roadmap.md` must be maintained. Every completed task requires a "check-off" to maintain Chain of Custody.

---

## 6. Phased Implementation Roadmap

### Phase 0: Initialization
*   [ ] **Directory Setup:** Create `services/`, `utils/`, `build_plan/`.
*   [ ] **Rule Generation:** Generate `.cursor/rules` files for each of the 9 Personnel Roles.
*   [ ] **Supabase Init:** Spin up PostgreSQL with `pgvector` extension.

### Phase 1: The Durable Foundation (Infrastructure)
*   **Objective:** Establish runtime that survives server crashes.
*   [ ] **Docker Compose:** Spin up Temporal Server alongside Supabase.
*   [ ] **Workflow-as-Code:** Write a Python workflow that executes a task, sleeps for 24 hours, and resumes.
*   [ ] **Signals:** Implement a "Human Signal" listener (pause until API call).
*   [ ] **Chaos Test:** Kill the worker process mid-workflow and verify state recovery.

### Phase 2: The Reliable Brain (AI & Verification)
*   **Objective:** Build agents that plan and generate valid code.
*   [ ] **AST Verifier:** Develop `verification/syntax_checker.py`. Must reject JSON that doesn't match the Schema.
*   [ ] **Reasoning Loop:** Use LangGraph to define a "Re-Plan" node. If AST fails, loop back with error message.
*   [ ] **Unified Schema:** Define Pydantic models for `UnifiedCustomer` and `UnifiedInvoice`.

### Phase 3: The Secure Context (Data & RAG)
*   **Objective:** Give agents memory and security boundaries.
*   [ ] **Vector Pipeline:** Ingest docs into Supabase.
*   [ ] **ACL Filtering:** Implement RLS logic to filter search results based on user permissions *before* LLM context generation.
*   [ ] **Process Logs:** Create a table to store event logs ("Process Graph").

### Phase 4: The Command Center (Frontend)
*   **Objective:** Create the "Matrix" interface.
*   [ ] **Matrix Grid:** Implement AG Grid to render high-density agent proposals.
*   [ ] **Realtime Wiring:** Connect Frontend to Supabase Realtime for status updates.
*   [ ] **Logic Cards:** Build UI components for "Approve/Reject" actions.
