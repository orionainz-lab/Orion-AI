# Phase 3 VAN Analysis: The Secure Context (Data & RAG)

**Date**: 2026-01-30  
**Mode**: VAN (Validate, Analyze, Navigate)  
**Phase**: Phase 3 - The Contextual Memory (Context Gap Solution)

---

## 1. Requirements Analysis

### 1.1 Functional Requirements (from Plan.md)

#### Core Deliverables
1. **Vector Pipeline**
   - Document ingestion system
   - Text chunking and embedding generation
   - Storage in Supabase pgvector
   - Batch and streaming ingestion modes

2. **ACL Filtering System**
   - Row Level Security (RLS) policies on vector tables
   - Pre-LLM context filtering based on user permissions
   - Permission inheritance from source documents
   - ACL metadata storage and querying

3. **Process Intelligence Logs**
   - Event log storage ("Process Graph" table)
   - Workflow execution tracking
   - Agent reasoning trace storage
   - Temporal workflow state persistence
   - Query interface for process mining

4. **Permissions-Aware RAG**
   - Semantic search with cosine similarity
   - Permission-filtered vector search
   - Context ranking and relevance scoring
   - LLM context assembly with citations

### 1.2 Non-Functional Requirements

1. **Security**
   - RLS enforced on ALL vector and process tables
   - ACL filtering prevents unauthorized context access
   - User impersonation for testing RLS policies
   - Audit logging for RAG queries

2. **Performance**
   - Vector search: <100ms for queries (target: <50ms)
   - Embedding generation: <500ms per chunk
   - RLS overhead: <10ms additional latency
   - Batch ingestion: >100 docs/minute

3. **Scalability**
   - Support 10,000+ document chunks initially
   - Efficient similarity search with HNSW indexing
   - Horizontal scaling via Supabase's infrastructure

4. **Maintainability**
   - All files <200 lines (strict adherence)
   - Modular embedding service
   - Clear separation: ingestion / search / ACL

---

## 2. Complexity Assessment

### Complexity Level: **4 (Complex System)**

**Justification**:
- **Multi-service integration**: Supabase (pgvector), embedding APIs, Temporal
- **Security critical**: RLS policies are foundational, errors expose data
- **Novel architecture**: Permissions-aware RAG is non-standard
- **Multiple personas required**: Backend API, Security, ML Engineer
- **Cross-layer dependencies**: Integrates with Phase 1 (Temporal) and Phase 2 (LangGraph)

### Complexity Factors

| Factor | Level | Rationale |
|--------|-------|-----------|
| **Technical Depth** | High | pgvector configuration, embedding models, RLS policies |
| **Integration Points** | Medium | Supabase, OpenAI/Anthropic embeddings, Temporal activities |
| **Security Risk** | High | RLS errors could leak sensitive context to agents |
| **Novelty** | High | Permissions-aware RAG is custom implementation |
| **Testing Needs** | High | Must verify RLS enforcement, vector search accuracy |

---

## 3. Prerequisites Verification

### 3.1 Completed Phases
- ✅ **Phase 0**: Directory structure, rules, architecture planning
- ✅ **Phase 1**: Temporal.io integration, durable workflows, chaos testing
- ✅ **Phase 2**: LangGraph reasoning loops, AST verification

### 3.2 Technology Stack Requirements

| Technology | Required For | Status | Verification Needed |
|------------|--------------|--------|---------------------|
| **Supabase** | PostgreSQL + pgvector + RLS | Planned | ✅ Verify pgvector availability |
| **pgvector** | Vector similarity search | Planned | ✅ Test HNSW index creation |
| **Python SDK** | Supabase client | Ready | ✅ Check supabase-py version |
| **Embedding API** | Text → Vectors | TBD | ✅ Choose OpenAI vs Anthropic |
| **Temporal** | Process log persistence | ✅ Complete | Already integrated |

### 3.3 External Dependencies
- Supabase project (local or cloud)
- Embedding API credentials (OpenAI `text-embedding-3-small` or Anthropic)
- Vector dimension size decision (384, 768, 1536, or 3072)

---

## 4. Technology Stack Validation

### 4.1 Core Technologies

#### 4.1.1 Supabase pgvector
**Purpose**: High-performance vector similarity search  
**Status**: Requires validation  
**Questions**:
- Is pgvector available on Supabase free tier?
- What HNSW index parameters should we use?
- What are the performance characteristics at scale?

**Decision Point**: ADR-010 required

#### 4.1.2 Embedding Model Selection
**Options**:
1. **OpenAI `text-embedding-3-small`** (1536 dimensions, $0.02/1M tokens)
2. **OpenAI `text-embedding-3-large`** (3072 dimensions, $0.13/1M tokens)
3. **Anthropic embeddings** (if available)
4. **Local models** (sentence-transformers, all-MiniLM)

**Decision Point**: ADR-011 required

#### 4.1.3 RLS Architecture
**Purpose**: Security boundary enforcement  
**Status**: Documented in Phase 0, needs implementation  
**Questions**:
- How to model document permissions (user_id, team_id, org_id)?
- How to handle hierarchical permissions?
- How to test RLS policies effectively?

**Decision Point**: ADR-012 required

### 4.2 Supporting Technologies

| Component | Technology | Purpose | Status |
|-----------|-----------|---------|--------|
| **Text Chunking** | LangChain or custom | Split documents for embedding | TBD |
| **Embedding Cache** | Supabase table | Avoid re-embedding same text | Design needed |
| **Process Logging** | Supabase table + triggers | Audit trail for workflows | Design needed |
| **RLS Testing** | pgTAP or Python tests | Verify security enforcement | Design needed |

---

## 5. Scope Breakdown

### Workstream 1: Supabase Setup (~2-3 hours)
**Owner**: Backend API Architect + Security Engineer  
**Tasks**:
- [ ] Set up Supabase project (local or cloud)
- [ ] Enable pgvector extension
- [ ] Create database schema:
  - `documents` table (source documents with ACL metadata)
  - `document_chunks` table (chunked text with embeddings)
  - `process_events` table (Temporal workflow logs)
- [ ] Configure RLS policies on all tables
- [ ] Create helper functions for vector search
- [ ] Test HNSW index creation and performance

**Deliverables**:
- SQL migration files
- Schema documentation
- RLS policy definitions

---

### Workstream 2: Vector Embedding Pipeline (~3-4 hours)
**Owner**: ML Engineer + Backend API Architect  
**Tasks**:
- [ ] Choose embedding model (ADR-011)
- [ ] Implement text chunking service (`services/embedding_service.py`)
- [ ] Create embedding generation service
- [ ] Implement batch ingestion workflow
- [ ] Add streaming ingestion support
- [ ] Create embedding cache mechanism
- [ ] Add error handling and retry logic
- [ ] Implement progress tracking

**Deliverables**:
- `services/embedding_service.py` (<200 lines)
- `services/document_chunker.py` (<200 lines)
- Embedding API integration
- Batch ingestion script

---

### Workstream 3: RLS & ACL Security (~2-3 hours)
**Owner**: Security Engineer  
**Tasks**:
- [ ] Design ACL data model (ADR-012)
- [ ] Implement RLS policies for `document_chunks`
- [ ] Implement RLS policies for `process_events`
- [ ] Create permission inheritance system
- [ ] Build ACL filtering functions
- [ ] Write RLS test suite (pgTAP or Python)
- [ ] Test user impersonation flows
- [ ] Document security patterns

**Deliverables**:
- RLS policies SQL
- ACL data model documentation
- Security test suite
- `utils/acl_helper.py` (<200 lines)

---

### Workstream 4: Permissions-Aware RAG (~3-4 hours)
**Owner**: AI Orchestration Engineer + Backend API Architect  
**Tasks**:
- [ ] Design RAG query interface
- [ ] Implement vector similarity search with RLS
- [ ] Create context ranking algorithm
- [ ] Build LLM context assembly service
- [ ] Add citation tracking (source document references)
- [ ] Integrate with Phase 2 LangGraph agents
- [ ] Implement caching for frequent queries
- [ ] Add telemetry and monitoring

**Deliverables**:
- `services/rag_service.py` (<200 lines)
- `services/context_builder.py` (<200 lines)
- Integration with LangGraph state
- RAG query API

---

### Workstream 5: Process Intelligence System (~2-3 hours)
**Owner**: Distributed Systems Engineer  
**Tasks**:
- [ ] Design `process_events` schema
- [ ] Create event ingestion service
- [ ] Integrate with Temporal workflows (activities)
- [ ] Implement event querying and filtering
- [ ] Build process graph visualization data
- [ ] Add event log RLS policies
- [ ] Create process mining queries
- [ ] Document event structure

**Deliverables**:
- `process_events` table schema
- `services/process_logger.py` (<200 lines)
- Temporal activity integration
- Query examples for process mining

---

### Workstream 6: Testing & Validation (~2-3 hours)
**Owner**: SDET + Security Engineer  
**Tasks**:
- [ ] Create integration tests for vector pipeline
- [ ] Write RLS enforcement tests (verify isolation)
- [ ] Test RAG query accuracy and relevance
- [ ] Verify permission filtering correctness
- [ ] Load test vector search performance
- [ ] Chaos test: crash during embedding ingestion
- [ ] End-to-end RAG workflow test
- [ ] Generate QA validation report

**Deliverables**:
- Test scripts (`scripts/test_phase3.py`)
- RLS test suite
- Performance benchmarks
- QA validation report

---

## 6. Risk Identification

### High-Priority Risks

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| **R-P3-001** | pgvector not available on Supabase tier | Medium | High | Verify before implementation; fallback to external vector DB |
| **R-P3-002** | RLS policies incorrectly configured | Medium | Critical | Comprehensive test suite; security review |
| **R-P3-003** | Embedding API rate limits | Medium | Medium | Implement retry logic; batch operations |
| **R-P3-004** | Vector search performance degradation | Medium | High | HNSW indexing; benchmark at scale |
| **R-P3-005** | Permission inheritance complexity | High | High | Start with simple model; document clearly |
| **R-P3-006** | RAG context quality issues | Medium | High | Implement ranking; allow manual tuning |

### Medium-Priority Risks

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| **R-P3-007** | Chunking strategy suboptimal | Medium | Medium | Test multiple strategies; make configurable |
| **R-P3-008** | Embedding dimension mismatch | Low | Medium | Document clearly in ADR; validate early |
| **R-P3-009** | Process log volume overwhelming | Medium | Medium | Implement log levels; add retention policies |

---

## 7. ADR Requirements

### Required ADRs for Phase 3

#### ADR-010: Vector Database Configuration
**Question**: How should pgvector be configured for optimal performance and cost?

**Key Decisions**:
- HNSW index parameters (m, ef_construction)
- Vector dimensions (tied to embedding model)
- Distance metric (cosine vs L2 vs inner product)
- Index rebuild strategy

---

#### ADR-011: Embedding Model Selection
**Question**: Which embedding model should we use for text vectorization?

**Options**:
1. OpenAI `text-embedding-3-small` (1536d, $0.02/1M tokens)
2. OpenAI `text-embedding-3-large` (3072d, $0.13/1M tokens)
3. Local models (sentence-transformers)
4. Anthropic embeddings (if available in 2026)

**Evaluation Criteria**:
- Cost per million tokens
- Retrieval accuracy (MTEB benchmark)
- Latency and throughput
- Vendor lock-in risk

---

#### ADR-012: ACL Data Model & Permission Inheritance
**Question**: How should document permissions be modeled and enforced?

**Options**:
1. Simple user-level ACLs (user_id column)
2. Hierarchical ACLs (user_id, team_id, org_id)
3. Role-based ACLs (permission groups)
4. Attribute-based ACLs (ABAC with policies)

**Evaluation Criteria**:
- Complexity vs flexibility trade-off
- RLS query performance impact
- Ease of testing and debugging
- Alignment with business requirements

---

## 8. Technology Validation Checklist (VAN QA Mode)

### Critical Validations Required

- [ ] **VAN-QA-1**: Supabase pgvector extension availability
  - Action: Connect to Supabase, run `CREATE EXTENSION vector`
  - Success: Extension creates without errors
  
- [ ] **VAN-QA-2**: Vector similarity search performance
  - Action: Create test table, insert 1000 vectors, query with HNSW
  - Success: <100ms query time for top 10 results

- [ ] **VAN-QA-3**: RLS policy enforcement
  - Action: Create test table with RLS, verify user isolation
  - Success: User A cannot see User B's rows

- [ ] **VAN-QA-4**: Embedding API integration
  - Action: Generate embeddings for test text
  - Success: Valid vectors returned in <500ms

- [ ] **VAN-QA-5**: Supabase Python client compatibility
  - Action: Test CRUD operations with RLS enabled
  - Success: Operations respect RLS policies

- [ ] **VAN-QA-6**: Process event logging
  - Action: Insert event from Temporal activity
  - Success: Event persisted with correct timestamp and metadata

---

## 9. Estimated Effort & Timeline

### Total Estimated Effort: 14-20 hours

**Breakdown by Workstream**:
- Workstream 1 (Supabase Setup): 2-3 hours
- Workstream 2 (Vector Pipeline): 3-4 hours
- Workstream 3 (RLS & ACL): 2-3 hours
- Workstream 4 (RAG System): 3-4 hours
- Workstream 5 (Process Intelligence): 2-3 hours
- Workstream 6 (Testing): 2-3 hours

**Complexity Factors**:
- Security implementation requires careful design (no room for errors)
- RLS testing can be time-consuming
- Embedding model integration may have API quirks
- Performance optimization may require iteration

**Expected ROI** (based on Phase 1 & 2 results):
- Manual implementation: 25-35 hours
- AI-assisted (VAN methodology): 14-20 hours
- **Projected time savings**: 40-57%

---

## 10. Dependencies & Blockers

### Internal Dependencies (Complete)
- ✅ Phase 1 Temporal integration (for process logging)
- ✅ Phase 2 LangGraph agents (RAG context consumers)
- ✅ Architectural patterns established

### External Dependencies (Pending)
- ⏳ Supabase project setup (local or cloud)
- ⏳ Embedding API credentials (OpenAI or Anthropic)
- ⏳ pgvector extension enabled

### Potential Blockers
1. **Supabase pgvector unavailable**: Fallback to Pinecone/Weaviate
2. **Embedding API rate limits**: Implement queue system
3. **RLS complexity**: Start with simple user-level model

---

## 11. Architecture Considerations

### 11.1 Key Architectural Patterns

#### Pattern 1: Document Ingestion Flow
```
Source Document → Chunker → Embedding API → pgvector Storage
                ↓
         ACL Metadata Extraction
```

#### Pattern 2: RAG Query Flow
```
User Query → Embedding API → Vector Search (with RLS) → Context Ranking → LLM
                                      ↓
                            ACL Filter (user permissions)
```

#### Pattern 3: Process Event Logging
```
Temporal Workflow → Activity (process_logger) → Supabase (process_events)
                                                         ↓
                                                   RLS Enforcement
```

### 11.2 Security Architecture

**Defense in Depth**:
1. **Database Level**: RLS policies (enforced by PostgreSQL)
2. **Application Level**: ACL validation in Python services
3. **API Level**: JWT validation and user context
4. **Audit Level**: All RAG queries logged

---

## 12. File Structure Planning

### New Directories (if needed)
```
services/
  ├── embedding_service.py      # Text → vectors (<200 lines)
  ├── document_chunker.py        # Document → chunks (<200 lines)
  ├── rag_service.py             # Vector search + context assembly (<200 lines)
  ├── context_builder.py         # LLM context construction (<200 lines)
  └── process_logger.py          # Event logging service (<200 lines)

utils/
  ├── acl_helper.py              # ACL filtering utilities (<200 lines)
  └── vector_utils.py            # pgvector helpers (<200 lines)

scripts/
  ├── test_phase3.py             # Integration tests (<200 lines)
  ├── ingest_documents.py        # Batch ingestion CLI (<200 lines)
  └── test_rls.py                # RLS enforcement tests (<200 lines)

supabase/
  └── migrations/
      ├── 001_create_vector_tables.sql
      ├── 002_create_rls_policies.sql
      └── 003_create_process_events.sql
```

**200-Line Rule Compliance**: Strict adherence, modular design

---

## 13. Integration Points

### 13.1 Phase 1 Integration (Temporal)
- Process event logging via Temporal activities
- Workflow state persistence
- Durable RAG context retrieval

### 13.2 Phase 2 Integration (LangGraph)
- RAG context injection into agent state
- Document retrieval during "Plan" node
- Context citations in generated code

### 13.3 Future Phase 4 Integration (Frontend)
- UI for document management
- RAG query visualization
- Process event timeline

---

## 14. Success Criteria

### Phase 3 Completion Checklist
- [ ] **Supabase Setup Complete**
  - [ ] pgvector extension enabled
  - [ ] All tables created with schemas
  - [ ] RLS policies implemented and tested
  - [ ] HNSW indexes created

- [ ] **Vector Pipeline Operational**
  - [ ] Document chunking service functional
  - [ ] Embedding generation working
  - [ ] Batch ingestion tested with 100+ documents
  - [ ] Embedding cache functional

- [ ] **Security Validated**
  - [ ] RLS policies enforce user isolation (100%)
  - [ ] ACL filtering prevents unauthorized access
  - [ ] Security test suite passes (all tests)
  - [ ] Audit logging captures all RAG queries

- [ ] **RAG System Functional**
  - [ ] Vector search returns relevant results
  - [ ] Context ranking working
  - [ ] LLM context assembly tested
  - [ ] Integration with LangGraph verified

- [ ] **Process Intelligence Ready**
  - [ ] Event logging from Temporal activities
  - [ ] Process event schema validated
  - [ ] Query interface functional
  - [ ] RLS on process events enforced

- [ ] **Testing Complete**
  - [ ] Integration tests pass (95%+ success rate)
  - [ ] RLS tests pass (100% isolation)
  - [ ] Performance benchmarks documented
  - [ ] Chaos test passes (crash during embedding)

- [ ] **Documentation Complete**
  - [ ] Architecture document created
  - [ ] 3 ADRs documented (ADR-010, ADR-011, ADR-012)
  - [ ] API documentation for RAG service
  - [ ] Security patterns documented

- [ ] **Code Quality**
  - [ ] All files <200 lines (100% compliance)
  - [ ] Zero technical debt
  - [ ] Modular, testable design

---

## 15. VAN Mode Deliverables

### Documents Created
1. ✅ `build_plan/phase3-van-marker.txt` - VAN initialization marker
2. ✅ `build_plan/phase3-van-analysis.md` - This comprehensive analysis (15KB+)

### Key Insights
1. **Complexity Level 4** confirmed - Security + novel architecture
2. **3 ADRs required** - pgvector config, embedding model, ACL design
3. **6 workstreams identified** - 14-20 hour estimate
4. **9 high/medium risks** - Security is critical focus
5. **6 technology validations** needed before BUILD mode

### Next Steps
1. **Transition to PLAN Mode** - Create phase3-architecture.md
2. **Make ADR decisions** - ADR-010, ADR-011, ADR-012
3. **Design detailed architecture** - Schema, services, integration
4. **Create implementation plan** - Sequencing, dependencies

---

## 16. VAN Mode Summary

**Phase**: Phase 3 - The Secure Context (Data & RAG)  
**Gap Addressed**: Context Gap (Memory + Security)  
**Complexity**: Level 4 (Complex System)  
**Estimated Effort**: 14-20 hours implementation  
**ADRs Required**: 3 (ADR-010, ADR-011, ADR-012)  
**Risk Profile**: High (security-critical)  
**Prerequisites**: ✅ All complete (Phase 0, 1, 2)

**VAN Analysis Status**: ✅ COMPLETE

**Next Command**: Ready to transition to PLAN Mode

---

**Document Status**: 🟢 VAN Analysis Complete  
**Next Review**: After PLAN Mode completion  
**Last Updated**: 2026-01-30
