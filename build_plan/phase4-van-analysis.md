# Phase 4 VAN Analysis: The Command Center (Frontend)

**Date**: 2026-01-30  
**Mode**: VAN (Validate, Analyze, Navigate)  
**Phase**: Phase 4 - Command Center (Frontend)  
**Status**: ANALYSIS IN PROGRESS

---

## 1. VALIDATE: Requirements & Objectives

### Phase 4 Objective

**Primary Goal**: Create the "Matrix" interface for human-in-the-loop governance.

**Core Purpose**: Build a high-density, real-time frontend that enables humans to monitor, approve, and control AI agent proposals through an intuitive command center interface.

---

### Success Criteria

| Criterion | Target | Validation Method |
|-----------|--------|-------------------|
| **Functionality** | Matrix UI operational | Manual testing |
| **Real-time Updates** | <1s latency | Performance monitoring |
| **Approval Workflow** | Full lifecycle | E2E testing |
| **Data Grid Performance** | 10K+ rows smooth | Load testing |
| **Code Quality** | 100% <200 lines | Linter validation |
| **Type Safety** | Zero type errors | TypeScript strict mode |
| **Responsive Design** | Mobile + Desktop | Browser testing |
| **UX Quality** | Modern, intuitive | User feedback |

---

### Context from Previous Phases

**Phase 1 (Temporal)**: ✅ COMPLETE
- Durable workflows with human signal handling
- Approval workflow (`approval_workflow.py`) implemented
- Signal pattern: `workflow.wait_condition(lambda: state.approved is not None)`
- **Integration Point**: Frontend sends approve/reject signals

**Phase 2 (LangGraph)**: ✅ COMPLETE
- Code generation agents operational
- Plan → Act → Observe loops working
- Agent state management complete
- **Integration Point**: Display agent reasoning steps

**Phase 3 (RAG)**: ✅ COMPLETE
- Document ingestion pipeline working
- Vector search with Supabase ready
- Process events logging (`process_events` table)
- **Integration Point**: Display process intelligence, RAG sources

**Supabase Database**: ✅ READY
- TypeScript types generated (`database.types.ts`)
- RLS policies defined (currently disabled for testing)
- Realtime subscriptions available
- **Integration Point**: Real-time data sync

---

### Functional Requirements

#### FR-1: Matrix UI (AG Grid)
**Description**: High-density data grid displaying AI agent proposals  
**Priority**: CRITICAL  
**Acceptance Criteria**:
- Display agent proposals in sortable/filterable grid
- Support 10,000+ rows with virtual scrolling
- Column customization (hide/show/reorder)
- Row selection for bulk operations
- Cell rendering for status badges, timestamps
- Export to CSV/Excel

#### FR-2: Real-time Updates (Supabase Realtime)
**Description**: Live status updates without page refresh  
**Priority**: CRITICAL  
**Acceptance Criteria**:
- Subscribe to `process_events` table changes
- Update grid rows in real-time (<1s latency)
- Visual indicators for new/updated rows
- Connection status indicator
- Automatic reconnection on disconnect

#### FR-3: Approval Workflow UI
**Description**: Approve/Reject interface for agent proposals  
**Priority**: CRITICAL  
**Acceptance Criteria**:
- "Approve" button sends signal to Temporal
- "Reject" button sends signal with reason
- Bulk approve/reject for multiple rows
- Confirmation dialogs for destructive actions
- Optimistic UI updates

#### FR-4: Logic Cards (Proposal Details)
**Description**: Detailed view of agent proposals  
**Priority**: HIGH  
**Acceptance Criteria**:
- Modal or side panel with full proposal details
- Syntax-highlighted code display
- Step-by-step reasoning breakdown (Plan → Act → Observe)
- RAG source citations
- Edit capability before approval (stretch goal)

#### FR-5: Process Intelligence Dashboard
**Description**: Analytics and monitoring for agent activity  
**Priority**: MEDIUM  
**Acceptance Criteria**:
- Total proposals by status (pending/approved/rejected)
- Average approval time
- Agent performance metrics
- Error rate tracking
- Timeline visualization

#### FR-6: Authentication & Authorization
**Description**: Secure login with role-based access  
**Priority**: HIGH  
**Acceptance Criteria**:
- Supabase Auth integration
- OAuth providers (Google, GitHub)
- Role-based UI (admin vs user)
- RLS enforcement on all queries
- Session management

---

### Non-Functional Requirements

#### NFR-1: Performance
- **Grid Rendering**: <100ms for initial load
- **Real-time Latency**: <1s for updates
- **Page Load Time**: <2s (LCP)
- **Interaction Delay**: <100ms (FID)

#### NFR-2: Scalability
- **Data Volume**: Support 10,000+ rows in grid
- **Concurrent Users**: 100+ simultaneous users
- **WebSocket Connections**: Stable with reconnection

#### NFR-3: Usability
- **Responsive**: Mobile-first design (320px to 4K)
- **Accessibility**: WCAG 2.1 AA compliance
- **Browser Support**: Chrome, Firefox, Safari, Edge (latest 2 versions)

#### NFR-4: Code Quality
- **200-Line Rule**: MANDATORY (all components <200 lines)
- **Type Safety**: TypeScript strict mode, zero errors
- **Testing**: >80% coverage (unit + integration)
- **Documentation**: JSDoc for all public APIs

---

## 2. ANALYZE: Technical Architecture

### Technology Stack

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Framework** | Next.js | 14+ | App Router, RSC, SSR/SSG |
| **Language** | TypeScript | 5.3+ | Type safety, IDE support |
| **Data Grid** | AG Grid Enterprise | 31+ | High performance, rich features |
| **UI Library** | Shadcn UI + Radix | Latest | Accessible, customizable |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first, responsive |
| **State** | Zustand | 4.5+ | Lightweight, TypeScript-first |
| **Real-time** | Supabase Realtime | 2.38+ | PostgreSQL change streams |
| **Database Client** | Supabase JS | 2.38+ | TypeScript SDK |
| **Auth** | Supabase Auth | Built-in | OAuth, RLS integration |
| **Forms** | React Hook Form | 7.50+ | Performance, validation |
| **Validation** | Zod | 3.22+ | Type-safe schemas |
| **Testing** | Jest + RTL | Latest | Unit + integration |
| **E2E Testing** | Playwright | 1.40+ | Browser automation |

### Why AG Grid Enterprise?

**Alternatives Considered**:
1. **TanStack Table** (React Table v8)
   - Pros: Free, headless, flexible
   - Cons: Requires custom virtualization, limited enterprise features
2. **Material-UI Data Grid**
   - Pros: Free tier, good UX
   - Cons: Performance degrades >1000 rows
3. **AG Grid Community**
   - Pros: Free, excellent performance
   - Cons: Missing key features (row grouping, Excel export)

**Decision**: **AG Grid Enterprise**
- Best-in-class performance (100K+ rows)
- Rich feature set (grouping, pivoting, Excel export)
- Enterprise support and documentation
- **Cost**: $999/developer/year (justified for critical UI)

---

### Application Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (Client)                          │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Next.js App (App Router)               │   │
│  │                                                      │   │
│  │  ┌───────────────┐  ┌───────────────────────────┐  │   │
│  │  │ Matrix Grid   │  │  Logic Cards (Modals)    │  │   │
│  │  │ (AG Grid)     │  │  - Code Display          │  │   │
│  │  │               │  │  - Reasoning Steps       │  │   │
│  │  │ - Proposals   │  │  - RAG Citations         │  │   │
│  │  │ - Realtime    │  │                          │  │   │
│  │  │ - Filters     │  │  ┌────────────────────┐  │  │   │
│  │  └───────────────┘  │  │ Approve/Reject UI │  │  │   │
│  │                      │  │ - Buttons         │  │  │   │
│  │  ┌───────────────┐  │  │ - Bulk Actions    │  │  │   │
│  │  │  Dashboard    │  │  └────────────────────┘  │  │   │
│  │  │  - Metrics    │  │                          │  │   │
│  │  │  - Charts     │  └───────────────────────────┘  │   │
│  │  └───────────────┘                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          │ (Supabase JS Client)             │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Supabase Platform                         │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  PostgreSQL    │  │  Realtime      │  │  Auth        │  │
│  │                │  │                │  │              │  │
│  │  - process_    │←─┤  - Change      │  │  - OAuth     │  │
│  │    events      │  │    streams     │  │  - Sessions  │  │
│  │  - documents   │  │  - WebSockets  │  │  - RLS ctx   │  │
│  │  - RLS         │  │                │  │              │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Backend Services                          │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  Temporal      │  │  LangGraph     │  │  RAG Service │  │
│  │  Workflows     │  │  Agents        │  │              │  │
│  │                │  │                │  │              │  │
│  │  - Approval    │  │  - Code Gen    │  │  - Vectors   │  │
│  │  - Signals     │  │  - Planning    │  │  - Search    │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

### Directory Structure (Proposed)

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout (<200 lines)
│   ├── page.tsx                  # Home redirect (<100 lines)
│   ├── (auth)/                   # Auth group
│   │   ├── login/
│   │   │   └── page.tsx          # Login page (<150 lines)
│   │   └── callback/
│   │       └── page.tsx          # OAuth callback (<100 lines)
│   ├── (dashboard)/              # Protected group
│   │   ├── layout.tsx            # Dashboard layout (<150 lines)
│   │   ├── matrix/
│   │   │   └── page.tsx          # Matrix grid page (<150 lines)
│   │   ├── analytics/
│   │   │   └── page.tsx          # Analytics dashboard (<150 lines)
│   │   └── settings/
│   │       └── page.tsx          # User settings (<150 lines)
│   └── api/                      # API routes (if needed)
│       └── temporal/
│           └── signal/
│               └── route.ts      # Send signal to Temporal (<150 lines)
├── components/                   # React components
│   ├── matrix/
│   │   ├── matrix-grid.tsx       # AG Grid wrapper (<200 lines)
│   │   ├── column-defs.ts        # Column definitions (<200 lines)
│   │   ├── status-badge.tsx      # Status cell renderer (<100 lines)
│   │   └── action-buttons.tsx    # Approve/Reject buttons (<150 lines)
│   ├── logic-cards/
│   │   ├── proposal-modal.tsx    # Main modal (<200 lines)
│   │   ├── code-display.tsx      # Syntax-highlighted code (<150 lines)
│   │   ├── reasoning-steps.tsx   # Plan/Act/Observe (<150 lines)
│   │   └── rag-citations.tsx     # Source citations (<100 lines)
│   ├── dashboard/
│   │   ├── metrics-card.tsx      # KPI card (<100 lines)
│   │   ├── timeline-chart.tsx    # Activity timeline (<150 lines)
│   │   └── status-pie.tsx        # Status distribution (<100 lines)
│   ├── auth/
│   │   ├── login-form.tsx        # Login UI (<150 lines)
│   │   └── auth-provider.tsx     # Auth context (<150 lines)
│   └── ui/                       # Shadcn components
│       ├── button.tsx
│       ├── dialog.tsx
│       ├── badge.tsx
│       └── ... (Shadcn components)
├── lib/                          # Utilities
│   ├── supabase/
│   │   ├── client.ts             # Browser client (<100 lines)
│   │   ├── server.ts             # Server client (<100 lines)
│   │   └── realtime.ts           # Realtime subscription (<150 lines)
│   ├── temporal/
│   │   └── signal-client.ts      # Temporal signal sender (<150 lines)
│   ├── utils.ts                  # Helper functions (<200 lines)
│   └── types.ts                  # Shared types (<200 lines)
├── hooks/                        # Custom hooks
│   ├── use-proposals.ts          # Fetch proposals (<150 lines)
│   ├── use-realtime.ts           # Realtime subscription (<150 lines)
│   ├── use-approval.ts           # Approval actions (<100 lines)
│   └── use-auth.ts               # Auth state (<100 lines)
├── store/                        # Zustand state
│   ├── proposals-store.ts        # Proposals state (<150 lines)
│   └── ui-store.ts               # UI state (modals, etc.) (<100 lines)
├── styles/
│   └── globals.css               # Global styles
├── public/
│   └── assets/                   # Images, icons
├── __tests__/                    # Tests
│   ├── unit/
│   └── e2e/
├── .env.local                    # Environment variables
├── .env.example                  # Example env
├── next.config.js                # Next.js config (<100 lines)
├── tailwind.config.js            # Tailwind config (<150 lines)
├── tsconfig.json                 # TypeScript config
├── package.json                  # Dependencies
└── README.md                     # Frontend docs
```

**File Count Estimate**: ~40-50 files
**Compliance**: 100% files <200 lines (by design)

---

### Data Flow: Approval Workflow

```
1. User Loads Matrix Grid
   ↓
   [Matrix Page] → useProposals() → Supabase.from('process_events')
   ↓
   [AG Grid] displays rows

2. Real-time Update Arrives
   ↓
   [useRealtime()] subscribes to 'process_events' changes
   ↓
   [Zustand Store] updates state
   ↓
   [AG Grid] re-renders affected rows

3. User Clicks "Approve"
   ↓
   [Action Buttons] → handleApprove(workflowId)
   ↓
   [Temporal Signal Client] → POST /api/temporal/signal
   ↓
   [Backend API] → workflow.signal('approve', {approved: true})
   ↓
   [Temporal Workflow] resumes execution
   ↓
   [Process Logger] → INSERT INTO process_events (status: 'approved')
   ↓
   [Realtime] → pushes update to all subscribed clients
   ↓
   [AG Grid] updates row status (optimistic + confirmed)

4. User Opens Logic Card
   ↓
   [Row Double-Click] → setSelectedProposal(proposalId)
   ↓
   [Proposal Modal] → fetch detailed data
   ↓
   Display: code, reasoning steps, RAG sources
```

---

### State Management Strategy

**Zustand Stores**:

1. **`proposals-store.ts`** (Global proposals state)
```typescript
interface ProposalsStore {
  proposals: Proposal[];
  loading: boolean;
  error: string | null;
  
  fetchProposals: () => Promise<void>;
  updateProposal: (id: string, updates: Partial<Proposal>) => void;
  approveProposal: (id: string, workflowId: string) => Promise<void>;
  rejectProposal: (id: string, workflowId: string, reason: string) => Promise<void>;
}
```

2. **`ui-store.ts`** (UI ephemeral state)
```typescript
interface UIStore {
  selectedProposalId: string | null;
  isModalOpen: boolean;
  gridFilters: GridFilters;
  
  setSelectedProposal: (id: string | null) => void;
  toggleModal: () => void;
  updateFilters: (filters: GridFilters) => void;
}
```

**Why Zustand over Redux/Context**:
- Lightweight (1KB vs 8KB Redux)
- No boilerplate (no actions/reducers)
- TypeScript-first
- Built-in dev tools
- Easy testing

---

### API Integration Points

#### 1. Supabase Database Queries

**Fetch Proposals**:
```typescript
const { data, error } = await supabase
  .from('process_events')
  .select('*')
  .eq('event_type', 'proposal_created')
  .order('created_at', { ascending: false });
```

**Fetch Proposal Details**:
```typescript
const { data, error } = await supabase
  .from('process_events')
  .select('*, rag_sources:event_metadata->rag_sources')
  .eq('id', proposalId)
  .single();
```

#### 2. Supabase Realtime Subscription

```typescript
const channel = supabase
  .channel('process_events_changes')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'process_events'
  }, (payload) => {
    updateProposal(payload.new);
  })
  .subscribe();
```

#### 3. Temporal Signal API

**Send Approval Signal**:
```typescript
// Frontend → Backend API → Temporal
await fetch('/api/temporal/signal', {
  method: 'POST',
  body: JSON.stringify({
    workflowId: 'code-gen-workflow-123',
    signalName: 'approve_signal',
    signalArgs: { approved: true }
  })
});
```

**Backend Implementation (Next.js API Route)**:
```typescript
// app/api/temporal/signal/route.ts
import { Connection, WorkflowClient } from '@temporalio/client';

export async function POST(request: Request) {
  const { workflowId, signalName, signalArgs } = await request.json();
  
  const connection = await Connection.connect({ address: 'localhost:7233' });
  const client = new WorkflowClient({ connection });
  
  const handle = client.getHandle(workflowId);
  await handle.signal(signalName, signalArgs);
  
  return Response.json({ success: true });
}
```

---

### Security Considerations

#### 1. Row Level Security (RLS)
- All Supabase queries filtered by `user_id`
- RLS policies enforce `auth.uid() = user_id`
- No direct SERVICE_ROLE_KEY access from frontend

#### 2. Authentication
- Supabase Auth with JWT tokens
- OAuth providers (Google, GitHub)
- Session management with automatic refresh

#### 3. Authorization
- Role-based UI (admin vs user)
- Admin: Can approve/reject any proposal
- User: Can only view own proposals (unless granted)

#### 4. Input Validation
- Zod schemas for all form inputs
- Sanitize rejection reasons (no XSS)
- Rate limiting on signal API

#### 5. HTTPS Only
- Next.js enforces HTTPS in production
- Secure cookies (httpOnly, sameSite: 'lax')

---

## 3. NAVIGATE: Implementation Plan

### Workstreams & Estimates

| Workstream | Description | Estimated Time | Priority |
|------------|-------------|----------------|----------|
| **WS-1: Project Setup** | Next.js init, dependencies | 2 hours | P0 |
| **WS-2: Authentication** | Supabase Auth integration | 3 hours | P0 |
| **WS-3: Matrix Grid** | AG Grid + data fetching | 6 hours | P0 |
| **WS-4: Real-time** | Supabase Realtime subscriptions | 4 hours | P0 |
| **WS-5: Approval UI** | Approve/Reject buttons + signals | 4 hours | P0 |
| **WS-6: Logic Cards** | Proposal detail modals | 5 hours | P1 |
| **WS-7: Dashboard** | Analytics and metrics | 4 hours | P1 |
| **WS-8: Testing** | Unit + E2E tests | 4 hours | P1 |
| **WS-9: Polish** | UX refinements, responsive | 3 hours | P2 |
| **Total** | | **35-40 hours** | |

**Priority Levels**:
- **P0**: Critical (blocks launch)
- **P1**: High (needed for MVP)
- **P2**: Medium (polish, can defer)

---

### Phase Breakdown

#### Phase 4.1: Foundation (8 hours) - WS1 + WS2 + WS3

**Deliverables**:
1. Next.js project initialized
2. Supabase Auth working (login/logout)
3. Basic Matrix grid displaying proposals
4. Protected routes (redirect if not authenticated)

**Acceptance Criteria**:
- `npm run dev` starts server
- Login redirects to Matrix grid
- Grid displays mock or real data
- TypeScript strict mode, zero errors

---

#### Phase 4.2: Real-time & Actions (12 hours) - WS4 + WS5 + WS6

**Deliverables**:
1. Real-time subscription to `process_events`
2. Approve/Reject buttons functional
3. Temporal signal integration
4. Proposal detail modal (Logic Cards)

**Acceptance Criteria**:
- Grid updates in real-time (<1s)
- Approve button sends signal to Temporal
- Modal shows code, reasoning, RAG sources
- Optimistic UI updates

---

#### Phase 4.3: Dashboard & Testing (12 hours) - WS7 + WS8 + WS9

**Deliverables**:
1. Analytics dashboard with metrics
2. Unit tests for critical components
3. E2E tests for approval workflow
4. Responsive design (mobile + desktop)

**Acceptance Criteria**:
- Dashboard displays KPIs (proposals, approvals, rejections)
- Test coverage >80%
- E2E test: login → approve → verify status
- Mobile-friendly (320px+)

---

### Technical Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **AG Grid licensing cost** | High | Medium | Evaluate Community Edition first, upgrade if needed |
| **Temporal signal latency** | Medium | Low | Add timeout + retry logic, optimistic UI |
| **Real-time connection drops** | Medium | Medium | Auto-reconnect, offline mode UI |
| **RLS circular dependencies** | High | Medium | Use fixed RLS policies from Phase 3 testing |
| **Type generation issues** | Low | Low | Re-run `supabase gen types` if schema changes |
| **AG Grid performance** | Medium | Low | Use virtual scrolling, pagination fallback |
| **200-line violations** | High | Medium | Enforce via linter pre-commit hook |

---

### Dependencies

**Prerequisites**:
- ✅ Phase 1 (Temporal workflows with signals)
- ✅ Phase 2 (LangGraph agents generating proposals)
- ✅ Phase 3 (Supabase database with `process_events` table)
- ✅ Supabase TypeScript types (`database.types.ts`)
- ⏳ Temporal signal API endpoint (need to build)
- ⏳ AG Grid Enterprise license (need to purchase or use Community)

**External Dependencies**:
- Node.js 18+ (for Next.js 14)
- npm or pnpm
- Supabase credentials (SUPABASE_URL, SUPABASE_ANON_KEY)
- Temporal server running (from Phase 1)

---

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Grid Load Time** | <2s | Lighthouse LCP |
| **Real-time Latency** | <1s | WebSocket ping |
| **Approval Action Time** | <500ms | Signal send duration |
| **Code Coverage** | >80% | Jest coverage report |
| **Type Errors** | 0 | `tsc --noEmit` |
| **200-Line Compliance** | 100% | ESLint max-lines rule |
| **Lighthouse Score** | >90 | Performance audit |
| **Accessibility** | WCAG AA | Axe DevTools |

---

## 4. COMPLEXITY ASSESSMENT

### Overall Complexity: **Level 3 (High)**

**Reasoning**:
- Multiple integrations (Supabase, Temporal, AG Grid)
- Real-time WebSocket management
- Complex state synchronization
- Enterprise-grade data grid configuration
- Authentication and authorization
- Responsive design requirements

**Compared to Previous Phases**:
- Phase 1: Level 4 (Very High) - Temporal orchestration
- Phase 2: Level 4 (Very High) - LangGraph + AST
- Phase 3: Level 4 (Very High) - RAG + pgvector + RLS
- Phase 4: Level 3 (High) - Frontend integration

**Why Lower Complexity?**:
- Backend already built (just integrate)
- Next.js is well-documented
- AG Grid has extensive examples
- Supabase client is straightforward
- No new architectural patterns (use proven stack)

---

### Complexity Breakdown

| Component | Complexity | Effort | Notes |
|-----------|-----------|--------|-------|
| Next.js Setup | Low | 2h | Standard create-next-app |
| Supabase Auth | Low | 3h | Follow official docs |
| AG Grid | Medium | 6h | Configuration + styling |
| Real-time | Medium | 4h | WebSocket subscription |
| Temporal Signal | Medium | 4h | Need API endpoint |
| Logic Cards | Medium | 5h | Modal + code display |
| Dashboard | Low | 4h | Charts + KPIs |
| Testing | Medium | 4h | Jest + Playwright |
| Polish | Low | 3h | CSS tweaks |

**Total Effort**: 35-40 hours (1 work week)

---

## 5. ARCHITECTURAL DECISION RECORDS (ADRs)

### ADR-013: Next.js App Router vs Pages Router

**Context**: Next.js 13+ introduced App Router with React Server Components (RSC).

**Decision**: Use **App Router** (not Pages Router)

**Rationale**:
- RSC reduces client-side JavaScript
- Better performance (streaming, suspense)
- Future-proof (Pages Router legacy)
- Better TypeScript support
- Server actions for forms

**Consequences**:
- Steeper learning curve (new paradigm)
- Some libraries don't support RSC yet (mark with 'use client')
- Migration from Pages Router harder (but we're starting fresh)

**Status**: RECOMMENDED

---

### ADR-014: AG Grid Community vs Enterprise

**Context**: AG Grid offers Community (free) and Enterprise (paid) editions.

**Decision**: Start with **Community Edition**, upgrade to **Enterprise** if needed

**Rationale**:
- Community Edition free and open-source
- Supports virtual scrolling (10K+ rows)
- Basic features sufficient for MVP
- Enterprise adds: row grouping, pivoting, Excel export, master-detail
- Can upgrade later without code changes

**Trial Strategy**:
- Build with Community Edition first
- Evaluate if missing features block launch
- Purchase Enterprise if needed ($999/dev/year)

**Consequences**:
- Save ~$1000 upfront
- May need to upgrade later
- Enterprise features impressive but not critical for MVP

**Status**: RECOMMENDED (Community first)

---

### ADR-015: Zustand vs Redux vs Context

**Context**: Need global state management for proposals and UI state.

**Decision**: Use **Zustand**

**Rationale**:
- Lightweight (1KB vs 8KB Redux)
- No boilerplate (no actions/reducers/providers)
- TypeScript-first API
- Built-in dev tools
- Easier testing than Context
- Better performance than Context (selective subscriptions)

**Alternatives Considered**:
1. **Redux Toolkit**: Too much boilerplate, overkill for this app
2. **React Context**: Performance issues with many consumers, re-renders
3. **Jotai/Recoil**: Atomic state model not needed

**Consequences**:
- Less familiar to Redux developers
- No time-travel debugging (can add Redux DevTools if needed)
- Excellent TypeScript DX

**Status**: RECOMMENDED

---

### ADR-016: Temporal Signal API Approach

**Context**: Frontend needs to send signals to Temporal workflows.

**Decision**: Create **Next.js API Route** as proxy to Temporal

**Architecture**:
```
Frontend → POST /api/temporal/signal → Temporal gRPC
```

**Rationale**:
- Frontend cannot connect to Temporal gRPC directly (browser limitation)
- API route runs on server, can use `@temporalio/client`
- Secure: no Temporal credentials exposed to browser
- Flexible: add validation, logging, rate limiting

**Alternatives Considered**:
1. **Direct gRPC-Web**: Complex, requires Envoy proxy
2. **Separate FastAPI service**: Extra infrastructure, latency
3. **Supabase Edge Function**: Adds dependency, harder debugging

**Consequences**:
- Extra hop (frontend → Next.js → Temporal)
- ~50ms additional latency (acceptable)
- Centralized control point for signals

**Status**: RECOMMENDED

---

### ADR-017: Real-time Update Strategy

**Context**: Grid needs to reflect database changes in real-time.

**Decision**: Use **Supabase Realtime** (PostgreSQL change streams)

**Rationale**:
- Built-in Supabase feature (no extra infra)
- WebSocket-based (efficient)
- Automatic reconnection
- Filters by table/schema/row
- RLS-aware (only sends changes user can see)

**Alternatives Considered**:
1. **Polling**: Inefficient, increases database load
2. **Server-Sent Events (SSE)**: One-way only, no filtering
3. **Custom WebSocket server**: Overkill, maintenance burden

**Update Strategy**:
- Subscribe to `process_events` table changes
- On INSERT/UPDATE: merge into Zustand store
- AG Grid re-renders affected rows automatically
- Optimistic updates for user actions (approve/reject)

**Consequences**:
- Dependent on Supabase Realtime reliability
- WebSocket connection needs error handling
- RLS policies must be correct (or receive nothing)

**Status**: RECOMMENDED

---

## 6. VAN SUMMARY

### Validation ✅

**Requirements**: Clear and validated
- Matrix UI for agent proposals (FR-1)
- Real-time updates (FR-2)
- Approval workflow (FR-3)
- Detailed proposal view (FR-4)
- Analytics dashboard (FR-5)
- Authentication (FR-6)

**Success Criteria**: Well-defined and measurable
- Performance targets (<2s load, <1s realtime)
- Code quality (100% <200 lines, TypeScript strict)
- Test coverage (>80%)

**Dependencies**: All prerequisites met
- Phase 1, 2, 3 complete
- Supabase database ready
- TypeScript types generated

---

### Analysis ✅

**Technology Stack**: Modern and proven
- Next.js 14+ (App Router, RSC)
- AG Grid (high performance)
- Supabase (database + realtime + auth)
- Zustand (lightweight state)
- TypeScript (type safety)

**Architecture**: Clean and scalable
- Component-based (React)
- 200-line rule enforced
- Clear separation of concerns
- API routes for backend integration

**Risks**: Identified with mitigation plans
- AG Grid licensing (start with Community)
- Real-time drops (auto-reconnect)
- RLS issues (use fixed policies from Phase 3)

---

### Navigation ✅

**Implementation Plan**: Phased and realistic
- Phase 4.1: Foundation (8 hours)
- Phase 4.2: Real-time & Actions (12 hours)
- Phase 4.3: Dashboard & Testing (12 hours)
- **Total**: 35-40 hours (~1 work week)

**ADRs**: 5 key decisions documented
- ADR-013: Next.js App Router
- ADR-014: AG Grid Community → Enterprise
- ADR-015: Zustand for state
- ADR-016: Next.js API for Temporal signals
- ADR-017: Supabase Realtime

**Workstreams**: Clear and prioritized
- 9 workstreams identified
- Effort estimates provided
- Dependencies mapped

---

## 7. RECOMMENDATION

### Proceed to PLAN Mode? **YES**

**Confidence**: **HIGH** (9/10)

**Reasoning**:
1. **Clear Requirements**: Matrix UI, realtime, approval workflow well-defined
2. **Proven Stack**: Next.js, AG Grid, Supabase all production-ready
3. **Strong Foundation**: Phases 1-3 complete, backend working
4. **Manageable Complexity**: Level 3 (lower than previous phases)
5. **Realistic Estimate**: 35-40 hours aligns with 1 work week

**Risks**:
- AG Grid configuration learning curve (mitigated: extensive docs)
- Real-time connection stability (mitigated: auto-reconnect)
- 200-line rule on components (mitigated: modular design from start)

**Expected Outcome**: Production-ready Matrix UI in ~40 hours

---

## 8. NEXT STEPS

### Immediate: PLAN Mode (3-4 hours)

**Deliverables**:
1. **Detailed Architecture Document** (20-30KB)
   - Component hierarchy
   - State management diagram
   - API integration flows
   - Real-time subscription patterns

2. **File-by-File Implementation Plan**
   - Each component designed to <200 lines
   - Type definitions
   - Props interfaces

3. **ADR Refinement**
   - Finalize 5 ADRs
   - Add implementation notes

4. **Testing Strategy**
   - Unit test plan (Jest + RTL)
   - E2E test scenarios (Playwright)
   - Coverage targets

---

### Then: VAN QA Mode (2-3 hours)

**Validation Scripts** (6-8 scripts):
1. `test_nextjs_setup.sh` - Verify Next.js runs
2. `test_supabase_auth.ts` - Validate auth flow
3. `test_aggrid_rendering.ts` - Test grid performance
4. `test_realtime_connection.ts` - WebSocket connection
5. `test_temporal_signal.ts` - Signal API endpoint
6. `test_typescript_types.sh` - Type checking
7. `test_200line_rule.sh` - Linter validation

---

### Finally: BUILD Mode (35-40 hours)

**Phased Implementation**:
- Week 1, Days 1-2: Foundation (8h)
- Week 1, Days 3-4: Real-time & Actions (12h)
- Week 1, Day 5: Dashboard & Testing (8h)
- Week 2, Day 1: Testing & Polish (4h)
- **Total**: ~32-40 hours

---

## 9. ESTIMATED TIMELINE

| Mode | Duration | Deliverable |
|------|----------|-------------|
| **VAN** | 1 hour | This document (~15KB) |
| **PLAN** | 3-4 hours | Architecture + ADRs (~40KB) |
| **VAN QA** | 2-3 hours | 6-8 validation scripts |
| **BUILD** | 35-40 hours | Full frontend application |
| **TESTING** | 4 hours | E2E tests, coverage reports |
| **REFLECT** | 1 hour | Lessons learned |
| **ARCHIVE** | 30 min | Phase 4 archive |
| **Total** | **46-52 hours** | **Complete Matrix UI** |

**Expected Efficiency**: 70-80% (based on Phase 1-3 learning)

---

**VAN Mode Complete**: 2026-01-30  
**Status**: ✅ READY FOR PLAN MODE  
**Complexity**: Level 3 (High)  
**Estimated Duration**: 46-52 hours  
**Recommendation**: **PROCEED**
