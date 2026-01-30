# Phase 4 Architecture: The Command Center (Frontend)

**Date**: 2026-01-30  
**Mode**: PLAN  
**Phase**: Phase 4 - Command Center (Frontend)  
**Status**: ARCHITECTURE IN PROGRESS

---

## Executive Summary

This document provides the comprehensive architectural blueprint for Phase 4: The Command Center, a Next.js-based frontend application featuring the "Matrix" interface for human-in-the-loop AI governance.

**Core Objective**: Build a high-density, real-time dashboard that enables humans to monitor AI agent proposals, review generated code, approve/reject actions, and track system performance through an intuitive, production-grade interface.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Technology Stack](#2-technology-stack)
3. [Application Architecture](#3-application-architecture)
4. [Component Design](#4-component-design)
5. [State Management](#5-state-management)
6. [Data Flow](#6-data-flow)
7. [API Integration](#7-api-integration)
8. [Real-time Architecture](#8-real-time-architecture)
9. [Authentication & Authorization](#9-authentication--authorization)
10. [File Structure](#10-file-structure)
11. [Implementation Plan](#11-implementation-plan)
12. [Testing Strategy](#12-testing-strategy)
13. [Performance Optimization](#13-performance-optimization)
14. [Security Considerations](#14-security-considerations)

---

## 1. System Overview

### 1.1 Vision

The Command Center is the primary interface for human operators to govern AI agents. It provides:

- **Real-time Visibility**: Live view of all agent proposals and actions
- **Interactive Approval**: One-click approve/reject with detailed review
- **Process Intelligence**: Analytics on agent performance and patterns
- **Contextual Memory**: Display of RAG sources and reasoning chains

### 1.2 User Personas

**1. AI Operator (Primary)**
- Monitors agent proposals in real-time
- Reviews and approves/rejects code generation
- Investigates agent reasoning and RAG sources
- Tracks approval metrics and patterns

**2. System Administrator (Secondary)**
- Manages user access and permissions
- Configures system settings
- Monitors system health and performance
- Reviews audit logs

**3. Developer (Tertiary)**
- Uses API for programmatic access
- Integrates with CI/CD pipelines
- Debugs agent behavior

### 1.3 Key Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **Matrix Grid** | High-density AG Grid displaying proposals | P0 (Critical) |
| **Real-time Updates** | WebSocket-based live data sync | P0 (Critical) |
| **Approval Workflow** | Approve/Reject UI with Temporal signals | P0 (Critical) |
| **Logic Cards** | Detailed proposal modals with code display | P0 (Critical) |
| **Authentication** | Supabase Auth with OAuth providers | P0 (Critical) |
| **Dashboard** | Analytics and KPI visualizations | P1 (High) |
| **Search & Filter** | Advanced grid filtering | P1 (High) |
| **Bulk Operations** | Multi-select approve/reject | P1 (High) |
| **Mobile Support** | Responsive design for tablets/phones | P2 (Medium) |
| **Notifications** | Toast alerts for status changes | P2 (Medium) |

---

## 2. Technology Stack

### 2.1 Core Framework

**Next.js 14.1.0+** (App Router)
- **Rationale**: Industry-standard React framework with SSR, SSG, and RSC
- **Features Used**:
  - App Router (file-based routing)
  - React Server Components (RSC)
  - Server Actions (form handling)
  - API Routes (Temporal signal proxy)
  - Streaming & Suspense
  - Image Optimization

### 2.2 Language

**TypeScript 5.3.3+** (Strict Mode)
- **Rationale**: Type safety, IDE support, refactoring confidence
- **Configuration**:
  ```json
  {
    "compilerOptions": {
      "strict": true,
      "noUncheckedIndexedAccess": true,
      "noImplicitAny": true,
      "strictNullChecks": true,
      "strictFunctionTypes": true
    }
  }
  ```

### 2.3 UI Framework

**React 18.2.0+**
- **Rationale**: Component-based architecture, hooks, concurrent features
- **Patterns**:
  - Functional components only
  - Custom hooks for logic reuse
  - Suspense boundaries for loading states
  - Error boundaries for fault isolation

### 2.4 Data Grid

**AG Grid Community 31.0.0+**
- **Rationale**: Best-in-class performance (100K+ rows), rich features
- **Features**:
  - Virtual scrolling (DOM recycling)
  - Column sorting, filtering, resizing
  - Cell rendering customization
  - Row selection (single/multi)
  - CSV/Excel export (Community has CSV)
  - Theme customization

**Enterprise Upgrade Path** (if needed):
- Row grouping
- Pivoting
- Master-detail views
- Excel export with formatting
- Aggregation
- **Cost**: $999/developer/year

### 2.5 UI Component Library

**Shadcn UI + Radix UI**
- **Rationale**: Accessible, customizable, copy-paste components
- **Components**:
  - Button, Dialog, Dropdown, Tooltip
  - Badge, Card, Alert
  - Form inputs, Select, Checkbox
  - Sheet (side panel), Tabs
  - No runtime dependency (copy into codebase)

**Tailwind CSS 3.4.0+**
- **Rationale**: Utility-first, responsive, production-optimized
- **Configuration**: Custom color palette matching brand

### 2.6 State Management

**Zustand 4.5.0+**
- **Rationale**: Lightweight (1KB), TypeScript-first, no boilerplate
- **Usage**:
  - Global state for proposals, user session
  - Persistent state (localStorage integration)
  - DevTools integration

### 2.7 Data Fetching & Real-time

**Supabase JS 2.38.0+**
- **Components**:
  - Supabase Client (database queries)
  - Supabase Auth (authentication)
  - Supabase Realtime (WebSocket subscriptions)
- **Features**:
  - Automatic RLS enforcement
  - TypeScript types from schema
  - Optimistic updates

### 2.8 Forms & Validation

**React Hook Form 7.50.0+**
- **Rationale**: Performance (uncontrolled inputs), easy validation
- **Features**:
  - Field-level validation
  - Schema validation with Zod
  - Async validation
  - Form state management

**Zod 3.22.0+**
- **Rationale**: Type-safe schema validation
- **Usage**:
  - Form validation
  - API response validation
  - Environment variable validation

### 2.9 Testing

**Jest 29.7.0+**
- Unit tests for utilities, hooks, pure functions
- Snapshot testing for components

**React Testing Library 14.1.0+**
- Component integration tests
- User interaction testing
- Accessibility testing

**Playwright 1.40.0+**
- End-to-end tests
- Cross-browser testing
- Visual regression testing

### 2.10 Development Tools

**ESLint 8.56.0+**
- Code quality linting
- Custom rules for 200-line limit
- TypeScript-specific rules

**Prettier 3.2.0+**
- Code formatting
- Pre-commit hook integration

**Husky + lint-staged**
- Git hooks for pre-commit checks
- Run linter and tests before commit

---

## 3. Application Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser Client                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Next.js Application (Port 3000)                │ │
│  │                                                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │ │
│  │  │  App Router  │  │  Components  │  │  Client Hooks    │ │ │
│  │  │              │  │              │  │                  │ │ │
│  │  │  /matrix     │  │  - Matrix    │  │  - useProposals │ │ │
│  │  │  /analytics  │  │  - LogicCard │  │  - useRealtime  │ │ │
│  │  │  /login      │  │  - Dashboard │  │  - useApproval  │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘ │ │
│  │                                                              │ │
│  │  ┌──────────────┐  ┌──────────────┐                        │ │
│  │  │ Zustand Store│  │  API Routes  │                        │ │
│  │  │              │  │              │                        │ │
│  │  │ - Proposals  │  │ /api/temporal│                        │ │
│  │  │ - UI State   │  │   /signal    │                        │ │
│  │  └──────────────┘  └──────────────┘                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                          │         │                             │
│                          │         │                             │
└──────────────────────────┼─────────┼─────────────────────────────┘
                           │         │
                   ┌───────┘         └────────┐
                   ↓                           ↓
    ┌──────────────────────────┐   ┌─────────────────────┐
    │   Supabase Platform      │   │  Temporal Server    │
    │                          │   │                     │
    │  ┌────────────────────┐  │   │  ┌───────────────┐ │
    │  │  PostgreSQL        │  │   │  │  Workflows    │ │
    │  │  - process_events  │  │   │  │  - approval   │ │
    │  │  - documents       │  │   │  │  - signals    │ │
    │  └────────────────────┘  │   │  └───────────────┘ │
    │                          │   │                     │
    │  ┌────────────────────┐  │   └─────────────────────┘
    │  │  Realtime Engine   │  │
    │  │  - WebSockets      │  │
    │  │  - Change streams  │  │
    │  └────────────────────┘  │
    │                          │
    │  ┌────────────────────┐  │
    │  │  Auth              │  │
    │  │  - JWT tokens      │  │
    │  │  - OAuth providers │  │
    │  └────────────────────┘  │
    └──────────────────────────┘
```

### 3.2 Component Hierarchy

```
App (layout.tsx)
├── Header (global navigation)
├── Sidebar (navigation menu)
└── Main Content
    │
    ├── /login (public)
    │   └── LoginForm
    │       ├── OAuthButtons (Google, GitHub)
    │       └── EmailPasswordForm
    │
    ├── /matrix (protected)
    │   ├── MatrixGrid (AG Grid)
    │   │   ├── StatusBadgeRenderer
    │   │   ├── TimestampRenderer
    │   │   └── ActionButtonsRenderer
    │   │       ├── ApproveButton
    │   │       └── RejectButton
    │   ├── ProposalModal (Logic Card)
    │   │   ├── CodeDisplay (syntax highlighting)
    │   │   ├── ReasoningSteps (Plan → Act → Observe)
    │   │   ├── RAGCitations (source documents)
    │   │   └── ApprovalActions
    │   └── FilterBar
    │       ├── StatusFilter
    │       ├── DateRangePicker
    │       └── SearchInput
    │
    ├── /analytics (protected)
    │   ├── MetricsGrid
    │   │   ├── MetricCard (KPI display)
    │   │   ├── StatusPieChart
    │   │   └── TimelineChart
    │   └── RecentActivityFeed
    │
    └── /settings (protected)
        ├── ProfileSettings
        ├── NotificationPreferences
        └── APIKeyManagement
```

### 3.3 Routing Strategy

**Next.js App Router (File-based)**

```
app/
├── layout.tsx                    # Root layout (global providers)
├── page.tsx                      # Home (redirect to /matrix)
├── (auth)/                       # Auth route group (no layout)
│   ├── login/page.tsx           # Login page
│   └── callback/page.tsx        # OAuth callback
├── (dashboard)/                  # Protected route group (with sidebar)
│   ├── layout.tsx               # Dashboard layout
│   ├── matrix/page.tsx          # Matrix grid
│   ├── analytics/page.tsx       # Analytics dashboard
│   └── settings/page.tsx        # User settings
└── api/                          # API routes
    └── temporal/
        └── signal/
            └── route.ts          # POST /api/temporal/signal
```

**Route Protection**: Middleware-based authentication check

```typescript
// middleware.ts
export async function middleware(request: NextRequest) {
  const { supabase, response } = createMiddlewareClient({ request });
  const { data: { session } } = await supabase.auth.getSession();
  
  if (!session && !request.nextUrl.pathname.startsWith('/login')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  return response;
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)']
};
```

---

## 4. Component Design

### 4.1 Matrix Grid Component

**Location**: `components/matrix/matrix-grid.tsx`

**Purpose**: High-density data grid displaying agent proposals

**Props**:
```typescript
interface MatrixGridProps {
  proposals: Proposal[];
  loading: boolean;
  onRowClick: (proposal: Proposal) => void;
  onApprove: (proposalId: string) => Promise<void>;
  onReject: (proposalId: string, reason: string) => Promise<void>;
}
```

**Features**:
- Virtual scrolling (AG Grid handles DOM recycling)
- Column definitions:
  - ID (UUID, hidden by default)
  - Workflow ID (link to Temporal UI)
  - Status (badge renderer)
  - Event Name (text)
  - Created At (timestamp renderer)
  - User ID (text)
  - Actions (approve/reject buttons)
- Row selection (single/multi)
- Context menu (right-click)
- Export to CSV

**Column Definitions**:
```typescript
// components/matrix/column-defs.ts
const columnDefs: ColDef[] = [
  {
    field: 'id',
    headerName: 'ID',
    hide: true,
  },
  {
    field: 'workflow_id',
    headerName: 'Workflow',
    width: 200,
    cellRenderer: WorkflowLinkRenderer,
  },
  {
    field: 'event_metadata.status',
    headerName: 'Status',
    width: 120,
    cellRenderer: StatusBadgeRenderer,
    filter: 'agSetColumnFilter',
  },
  {
    field: 'event_name',
    headerName: 'Event',
    width: 250,
  },
  {
    field: 'created_at',
    headerName: 'Created',
    width: 180,
    cellRenderer: TimestampRenderer,
    sort: 'desc',
  },
  {
    field: 'user_id',
    headerName: 'User',
    width: 150,
  },
  {
    headerName: 'Actions',
    width: 200,
    cellRenderer: ActionButtonsRenderer,
    pinned: 'right',
  },
];
```

**Custom Cell Renderers**:

1. **StatusBadgeRenderer** (`components/matrix/status-badge.tsx`)
```typescript
interface StatusBadgeProps {
  value: 'pending' | 'approved' | 'rejected' | 'processing';
}

export function StatusBadgeRenderer({ value }: StatusBadgeProps) {
  const variants = {
    pending: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    processing: 'bg-blue-100 text-blue-800',
  };
  
  return (
    <Badge className={variants[value]}>
      {value}
    </Badge>
  );
}
```

2. **ActionButtonsRenderer** (`components/matrix/action-buttons.tsx`)
```typescript
interface ActionButtonsProps {
  data: Proposal;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}

export function ActionButtonsRenderer({ 
  data, 
  onApprove, 
  onReject 
}: ActionButtonsProps) {
  if (data.event_metadata.status !== 'pending') {
    return <span className="text-muted-foreground">-</span>;
  }
  
  return (
    <div className="flex gap-2">
      <Button
        size="sm"
        variant="default"
        onClick={() => onApprove(data.id)}
      >
        Approve
      </Button>
      <Button
        size="sm"
        variant="destructive"
        onClick={() => onReject(data.id)}
      >
        Reject
      </Button>
    </div>
  );
}
```

**File Size**: ~180 lines (compliant with 200-line rule)

---

### 4.2 Proposal Modal (Logic Card)

**Location**: `components/logic-cards/proposal-modal.tsx`

**Purpose**: Detailed view of agent proposal with code, reasoning, and actions

**Props**:
```typescript
interface ProposalModalProps {
  proposal: Proposal | null;
  open: boolean;
  onClose: () => void;
  onApprove: () => Promise<void>;
  onReject: (reason: string) => Promise<void>;
}
```

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  [X] Proposal Details                                   │
├─────────────────────────────────────────────────────────┤
│  Tabs: [ Code ] [ Reasoning ] [ RAG Sources ] [ Meta ] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [Code Tab]:                                            │
│  ┌────────────────────────────────────────────────────┐ │
│  │  // Syntax-highlighted code display                │ │
│  │  def example_function():                            │ │
│  │      return "Generated code here"                   │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  [Reasoning Tab]:                                       │
│  - Plan: "Generate utility function..."                │
│  - Act: "Created function with error handling..."      │
│  - Observe: "Syntax validated, tests pass..."          │
│                                                          │
│  [RAG Sources Tab]:                                     │
│  - Document: "Python Best Practices" (similarity: 0.85)│
│  - Chunk: "Error handling patterns..."                 │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  [ Approve ]  [ Reject ]  [ Cancel ]                    │
└─────────────────────────────────────────────────────────┘
```

**Sub-components**:

1. **CodeDisplay** (`components/logic-cards/code-display.tsx`)
```typescript
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface CodeDisplayProps {
  code: string;
  language: string;
}

export function CodeDisplay({ code, language }: CodeDisplayProps) {
  return (
    <SyntaxHighlighter
      language={language}
      style={vscDarkPlus}
      showLineNumbers
      wrapLines
      customStyle={{
        maxHeight: '500px',
        borderRadius: '0.5rem',
      }}
    >
      {code}
    </SyntaxHighlighter>
  );
}
```

2. **ReasoningSteps** (`components/logic-cards/reasoning-steps.tsx`)
```typescript
interface ReasoningStepsProps {
  steps: {
    plan: string;
    act: string;
    observe: string;
  };
}

export function ReasoningSteps({ steps }: ReasoningStepsProps) {
  return (
    <div className="space-y-4">
      <StepCard title="Plan" icon={Target} content={steps.plan} />
      <StepCard title="Act" icon={Code} content={steps.act} />
      <StepCard title="Observe" icon={Eye} content={steps.observe} />
    </div>
  );
}
```

3. **RAGCitations** (`components/logic-cards/rag-citations.tsx`)
```typescript
interface RAGCitationsProps {
  sources: RAGSource[];
}

interface RAGSource {
  documentTitle: string;
  chunkContent: string;
  similarity: number;
}

export function RAGCitations({ sources }: RAGCitationsProps) {
  return (
    <div className="space-y-3">
      {sources.map((source, idx) => (
        <Card key={idx}>
          <CardHeader>
            <CardTitle className="text-sm">
              {source.documentTitle}
            </CardTitle>
            <Badge variant="secondary">
              {(source.similarity * 100).toFixed(1)}% match
            </Badge>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {source.chunkContent}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
```

**File Size**: ~190 lines (compliant)

---

### 4.3 Dashboard Components

**Location**: `components/dashboard/`

**1. MetricsCard** (`metrics-card.tsx`)
```typescript
interface MetricsCardProps {
  title: string;
  value: number | string;
  description?: string;
  icon?: React.ComponentType;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
}

export function MetricsCard({ 
  title, 
  value, 
  description, 
  icon: Icon,
  trend 
}: MetricsCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm font-medium">
          {title}
        </CardTitle>
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground">
            {description}
          </p>
        )}
        {trend && (
          <div className="flex items-center text-xs">
            {trend.direction === 'up' ? (
              <TrendingUp className="h-3 w-3 text-green-500" />
            ) : (
              <TrendingDown className="h-3 w-3 text-red-500" />
            )}
            <span className="ml-1">{trend.value}%</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

**2. StatusPieChart** (`status-pie.tsx`)
```typescript
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';

interface StatusPieChartProps {
  data: {
    pending: number;
    approved: number;
    rejected: number;
  };
}

export function StatusPieChart({ data }: StatusPieChartProps) {
  const chartData = [
    { name: 'Pending', value: data.pending, color: '#fbbf24' },
    { name: 'Approved', value: data.approved, color: '#10b981' },
    { name: 'Rejected', value: data.rejected, color: '#ef4444' },
  ];
  
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={80}
          label
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
```

**3. TimelineChart** (`timeline-chart.tsx`)
```typescript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface TimelineChartProps {
  data: Array<{
    date: string;
    proposals: number;
    approvals: number;
  }>;
}

export function TimelineChart({ data }: TimelineChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Line 
          type="monotone" 
          dataKey="proposals" 
          stroke="#3b82f6" 
          strokeWidth={2}
        />
        <Line 
          type="monotone" 
          dataKey="approvals" 
          stroke="#10b981" 
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

---

## 5. State Management

### 5.1 Zustand Store Architecture

**Two stores for separation of concerns:**

1. **Proposals Store** (`store/proposals-store.ts`)
   - Manages proposal data and operations
   - Handles CRUD operations
   - Coordinates with Supabase

2. **UI Store** (`store/ui-store.ts`)
   - Manages ephemeral UI state
   - Modal open/close
   - Selected items
   - Filters

### 5.2 Proposals Store

```typescript
// store/proposals-store.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface Proposal {
  id: string;
  workflow_id: string;
  event_type: string;
  event_name: string;
  event_metadata: {
    status: 'pending' | 'approved' | 'rejected' | 'processing';
    code?: string;
    reasoning?: {
      plan: string;
      act: string;
      observe: string;
    };
    rag_sources?: RAGSource[];
  };
  user_id: string;
  created_at: string;
}

interface ProposalsState {
  // State
  proposals: Proposal[];
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchProposals: () => Promise<void>;
  updateProposal: (id: string, updates: Partial<Proposal>) => void;
  approveProposal: (id: string, workflowId: string) => Promise<void>;
  rejectProposal: (id: string, workflowId: string, reason: string) => Promise<void>;
  bulkApprove: (ids: string[]) => Promise<void>;
  bulkReject: (ids: string[], reason: string) => Promise<void>;
}

export const useProposalsStore = create<ProposalsState>()(
  devtools(
    (set, get) => ({
      proposals: [],
      loading: false,
      error: null,
      
      fetchProposals: async () => {
        set({ loading: true, error: null });
        try {
          const supabase = createClientComponentClient();
          const { data, error } = await supabase
            .from('process_events')
            .select('*')
            .eq('event_type', 'proposal_created')
            .order('created_at', { ascending: false });
          
          if (error) throw error;
          set({ proposals: data, loading: false });
        } catch (error) {
          set({ error: error.message, loading: false });
        }
      },
      
      updateProposal: (id, updates) => {
        set((state) => ({
          proposals: state.proposals.map((p) =>
            p.id === id ? { ...p, ...updates } : p
          ),
        }));
      },
      
      approveProposal: async (id, workflowId) => {
        // Optimistic update
        get().updateProposal(id, {
          event_metadata: { ...get().proposals.find(p => p.id === id)?.event_metadata, status: 'approved' }
        });
        
        try {
          // Send signal to Temporal
          await fetch('/api/temporal/signal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              workflowId,
              signalName: 'approve_signal',
              signalArgs: { approved: true },
            }),
          });
        } catch (error) {
          // Revert on error
          get().updateProposal(id, {
            event_metadata: { ...get().proposals.find(p => p.id === id)?.event_metadata, status: 'pending' }
          });
          throw error;
        }
      },
      
      rejectProposal: async (id, workflowId, reason) => {
        // Optimistic update
        get().updateProposal(id, {
          event_metadata: { ...get().proposals.find(p => p.id === id)?.event_metadata, status: 'rejected' }
        });
        
        try {
          await fetch('/api/temporal/signal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              workflowId,
              signalName: 'approve_signal',
              signalArgs: { approved: false, reason },
            }),
          });
        } catch (error) {
          get().updateProposal(id, {
            event_metadata: { ...get().proposals.find(p => p.id === id)?.event_metadata, status: 'pending' }
          });
          throw error;
        }
      },
      
      bulkApprove: async (ids) => {
        const proposals = get().proposals.filter((p) => ids.includes(p.id));
        await Promise.all(
          proposals.map((p) => get().approveProposal(p.id, p.workflow_id))
        );
      },
      
      bulkReject: async (ids, reason) => {
        const proposals = get().proposals.filter((p) => ids.includes(p.id));
        await Promise.all(
          proposals.map((p) => get().rejectProposal(p.id, p.workflow_id, reason))
        );
      },
    }),
    { name: 'proposals-store' }
  )
);
```

**File Size**: ~150 lines (compliant)

### 5.3 UI Store

```typescript
// store/ui-store.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  // Modal state
  selectedProposalId: string | null;
  isModalOpen: boolean;
  
  // Grid state
  gridFilters: {
    status: string[];
    dateRange: { start: Date | null; end: Date | null };
    searchTerm: string;
  };
  
  // UI preferences (persisted)
  theme: 'light' | 'dark' | 'system';
  sidebarCollapsed: boolean;
  
  // Actions
  setSelectedProposal: (id: string | null) => void;
  toggleModal: () => void;
  updateFilters: (filters: Partial<UIState['gridFilters']>) => void;
  setTheme: (theme: UIState['theme']) => void;
  toggleSidebar: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      selectedProposalId: null,
      isModalOpen: false,
      gridFilters: {
        status: [],
        dateRange: { start: null, end: null },
        searchTerm: '',
      },
      theme: 'system',
      sidebarCollapsed: false,
      
      setSelectedProposal: (id) => set({ selectedProposalId: id }),
      toggleModal: () => set((state) => ({ isModalOpen: !state.isModalOpen })),
      updateFilters: (filters) =>
        set((state) => ({
          gridFilters: { ...state.gridFilters, ...filters },
        })),
      setTheme: (theme) => set({ theme }),
      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
    }),
    {
      name: 'ui-store',
      partialize: (state) => ({
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);
```

**File Size**: ~80 lines (compliant)

---

## 6. Data Flow

### 6.1 Proposal Lifecycle Flow

```
1. Agent generates proposal
   ↓
2. Temporal workflow creates proposal
   ↓
3. ProcessLogger inserts into process_events table
   ↓
4. Supabase Realtime pushes change to subscribed clients
   ↓
5. Frontend useRealtime hook receives update
   ↓
6. Zustand proposals store updates state
   ↓
7. AG Grid re-renders affected row
   ↓
8. User clicks "Approve" button
   ↓
9. approveProposal() action dispatched
   ↓
10. Optimistic update (status → 'approved')
    ↓
11. POST /api/temporal/signal
    ↓
12. Next.js API route sends signal to Temporal
    ↓
13. Temporal workflow resumes
    ↓
14. ProcessLogger updates process_events
    ↓
15. Realtime pushes confirmed update
    ↓
16. Frontend confirms optimistic update
```

### 6.2 Real-time Subscription Flow

```typescript
// hooks/use-realtime.ts
import { useEffect } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { useProposalsStore } from '@/store/proposals-store';

export function useRealtime() {
  const updateProposal = useProposalsStore((state) => state.updateProposal);
  
  useEffect(() => {
    const supabase = createClientComponentClient();
    
    const channel = supabase
      .channel('process_events_changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'process_events',
          filter: 'event_type=eq.proposal_created',
        },
        (payload) => {
          if (payload.eventType === 'INSERT') {
            // New proposal created
            useProposalsStore.setState((state) => ({
              proposals: [payload.new, ...state.proposals],
            }));
          } else if (payload.eventType === 'UPDATE') {
            // Proposal updated (status change)
            updateProposal(payload.new.id, payload.new);
          }
        }
      )
      .subscribe();
    
    return () => {
      supabase.removeChannel(channel);
    };
  }, [updateProposal]);
}
```

**File Size**: ~50 lines (compliant)

### 6.3 Approval Action Flow

```typescript
// hooks/use-approval.ts
import { useState } from 'react';
import { useProposalsStore } from '@/store/proposals-store';
import { useToast } from '@/components/ui/use-toast';

export function useApproval() {
  const { approveProposal, rejectProposal } = useProposalsStore();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  
  const handleApprove = async (id: string, workflowId: string) => {
    setLoading(true);
    try {
      await approveProposal(id, workflowId);
      toast({
        title: 'Proposal Approved',
        description: 'The workflow will continue execution.',
      });
    } catch (error) {
      toast({
        title: 'Approval Failed',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleReject = async (
    id: string,
    workflowId: string,
    reason: string
  ) => {
    setLoading(true);
    try {
      await rejectProposal(id, workflowId, reason);
      toast({
        title: 'Proposal Rejected',
        description: 'The workflow has been terminated.',
      });
    } catch (error) {
      toast({
        title: 'Rejection Failed',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };
  
  return { handleApprove, handleReject, loading };
}
```

**File Size**: ~60 lines (compliant)

---

## 7. API Integration

### 7.1 Temporal Signal API

**Location**: `app/api/temporal/signal/route.ts`

**Purpose**: Proxy for sending signals to Temporal workflows

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { Connection, WorkflowClient } from '@temporalio/client';
import { z } from 'zod';

// Request validation schema
const SignalRequestSchema = z.object({
  workflowId: z.string().uuid(),
  signalName: z.string().min(1),
  signalArgs: z.record(z.any()),
});

export async function POST(request: NextRequest) {
  try {
    // Parse and validate request body
    const body = await request.json();
    const { workflowId, signalName, signalArgs } = SignalRequestSchema.parse(body);
    
    // Connect to Temporal
    const connection = await Connection.connect({
      address: process.env.TEMPORAL_ADDRESS || 'localhost:7233',
    });
    
    const client = new WorkflowClient({ connection });
    
    // Get workflow handle
    const handle = client.getHandle(workflowId);
    
    // Send signal
    await handle.signal(signalName, signalArgs);
    
    // Close connection
    await connection.close();
    
    return NextResponse.json({
      success: true,
      message: 'Signal sent successfully',
    });
  } catch (error) {
    console.error('Temporal signal error:', error);
    
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 }
      );
    }
    
    return NextResponse.json(
      { error: 'Failed to send signal', message: error.message },
      { status: 500 }
    );
  }
}
```

**File Size**: ~60 lines (compliant)

**Security**:
- Server-side only (no Temporal credentials exposed to browser)
- Request validation with Zod
- Error handling with proper status codes
- Rate limiting (via middleware, separate file)

### 7.2 Supabase Client Setup

**Browser Client** (`lib/supabase/client.ts`)
```typescript
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import type { Database } from '@/supabase/database.types';

export function createClient() {
  return createClientComponentClient<Database>();
}
```

**Server Client** (`lib/supabase/server.ts`)
```typescript
import { createServerComponentClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import type { Database } from '@/supabase/database.types';

export function createServerClient() {
  return createServerComponentClient<Database>({ cookies });
}
```

**Middleware Client** (`lib/supabase/middleware.ts`)
```typescript
import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs';
import { NextRequest, NextResponse } from 'next/server';
import type { Database } from '@/supabase/database.types';

export function createMiddlewareSupabase(request: NextRequest) {
  const response = NextResponse.next();
  const supabase = createMiddlewareClient<Database>({ req: request, res: response });
  return { supabase, response };
}
```

---

## 8. Real-time Architecture

### 8.1 Supabase Realtime Integration

**Subscription Hook** (`lib/supabase/realtime.ts`)

```typescript
import { useEffect } from 'react';
import { RealtimeChannel, RealtimePostgresChangesPayload } from '@supabase/supabase-js';
import { createClient } from './client';

interface UseRealtimeSubscriptionOptions<T> {
  table: string;
  filter?: string;
  onInsert?: (payload: T) => void;
  onUpdate?: (payload: T) => void;
  onDelete?: (payload: { id: string }) => void;
}

export function useRealtimeSubscription<T>({
  table,
  filter,
  onInsert,
  onUpdate,
  onDelete,
}: UseRealtimeSubscriptionOptions<T>) {
  useEffect(() => {
    const supabase = createClient();
    
    const channel: RealtimeChannel = supabase.channel(`${table}_changes`);
    
    // Configure subscription
    if (onInsert) {
      channel.on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table,
          filter,
        },
        (payload: RealtimePostgresChangesPayload<T>) => {
          onInsert(payload.new as T);
        }
      );
    }
    
    if (onUpdate) {
      channel.on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table,
          filter,
        },
        (payload: RealtimePostgresChangesPayload<T>) => {
          onUpdate(payload.new as T);
        }
      );
    }
    
    if (onDelete) {
      channel.on(
        'postgres_changes',
        {
          event: 'DELETE',
          schema: 'public',
          table,
          filter,
        },
        (payload: RealtimePostgresChangesPayload<T>) => {
          onDelete({ id: payload.old.id });
        }
      );
    }
    
    // Subscribe
    channel.subscribe((status) => {
      if (status === 'SUBSCRIBED') {
        console.log(`Subscribed to ${table} changes`);
      } else if (status === 'CLOSED') {
        console.log(`Subscription to ${table} closed`);
      } else if (status === 'CHANNEL_ERROR') {
        console.error(`Error subscribing to ${table}`);
      }
    });
    
    // Cleanup
    return () => {
      supabase.removeChannel(channel);
    };
  }, [table, filter, onInsert, onUpdate, onDelete]);
}
```

**File Size**: ~90 lines (compliant)

### 8.2 Connection Management

**Features**:
- Automatic reconnection (handled by Supabase client)
- Connection status indicator in UI
- Offline mode fallback (disable real-time updates)
- Error boundary for subscription failures

**Connection Status Hook** (`hooks/use-connection-status.ts`)
```typescript
import { useState, useEffect } from 'react';
import { createClient } from '@/lib/supabase/client';

export function useConnectionStatus() {
  const [status, setStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connecting');
  
  useEffect(() => {
    const supabase = createClient();
    
    // Listen to connection state
    const channel = supabase.channel('connection_status');
    
    channel.subscribe((status) => {
      if (status === 'SUBSCRIBED') {
        setStatus('connected');
      } else if (status === 'CLOSED') {
        setStatus('disconnected');
      } else if (status === 'CHANNEL_ERROR') {
        setStatus('disconnected');
      }
    });
    
    return () => {
      supabase.removeChannel(channel);
    };
  }, []);
  
  return status;
}
```

---

## 9. Authentication & Authorization

### 9.1 Supabase Auth Setup

**Auth Provider** (`components/auth/auth-provider.tsx`)

```typescript
'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { User, Session } from '@supabase/supabase-js';
import { createClient } from '@/lib/supabase/client';

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signInWithOAuth: (provider: 'google' | 'github') => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  
  const supabase = createClient();
  
  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });
    
    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
    });
    
    return () => subscription.unsubscribe();
  }, []);
  
  const signIn = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw error;
  };
  
  const signInWithOAuth = async (provider: 'google' | 'github') => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: `${window.location.origin}/callback`,
      },
    });
    if (error) throw error;
  };
  
  const signOut = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
  };
  
  return (
    <AuthContext.Provider value={{ user, session, loading, signIn, signInWithOAuth, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

**File Size**: ~100 lines (compliant)

### 9.2 Login Form

**Location**: `components/auth/login-form.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from './auth-provider';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { signIn, signInWithOAuth } = useAuth();
  const router = useRouter();
  const { toast } = useToast();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await signIn(email, password);
      router.push('/matrix');
    } catch (error) {
      toast({
        title: 'Login Failed',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleOAuth = async (provider: 'google' | 'github') => {
    try {
      await signInWithOAuth(provider);
    } catch (error) {
      toast({
        title: 'OAuth Failed',
        description: error.message,
        variant: 'destructive',
      });
    }
  };
  
  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        
        <div>
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        
        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? 'Signing in...' : 'Sign In'}
        </Button>
      </form>
      
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            Or continue with
          </span>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <Button variant="outline" onClick={() => handleOAuth('google')}>
          Google
        </Button>
        <Button variant="outline" onClick={() => handleOAuth('github')}>
          GitHub
        </Button>
      </div>
    </div>
  );
}
```

**File Size**: ~110 lines (compliant)

### 9.3 Route Protection

**Middleware** (`middleware.ts`)

```typescript
import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function middleware(req: NextRequest) {
  const res = NextResponse.next();
  const supabase = createMiddlewareClient({ req, res });
  
  const {
    data: { session },
  } = await supabase.auth.getSession();
  
  // Redirect to login if not authenticated
  if (!session && !req.nextUrl.pathname.startsWith('/login')) {
    return NextResponse.redirect(new URL('/login', req.url));
  }
  
  // Redirect to matrix if already authenticated and trying to access login
  if (session && req.nextUrl.pathname.startsWith('/login')) {
    return NextResponse.redirect(new URL('/matrix', req.url));
  }
  
  return res;
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
```

**File Size**: ~35 lines (compliant)

---

## 10. File Structure

### 10.1 Complete Directory Tree

```
frontend/
├── app/                                 # Next.js App Router
│   ├── layout.tsx                       # Root layout (180 lines)
│   ├── page.tsx                         # Home redirect (20 lines)
│   ├── globals.css                      # Global styles
│   ├── (auth)/                          # Public auth routes
│   │   ├── login/
│   │   │   └── page.tsx                 # Login page (100 lines)
│   │   └── callback/
│   │       └── page.tsx                 # OAuth callback (50 lines)
│   ├── (dashboard)/                     # Protected routes
│   │   ├── layout.tsx                   # Dashboard layout (150 lines)
│   │   ├── matrix/
│   │   │   └── page.tsx                 # Matrix grid page (120 lines)
│   │   ├── analytics/
│   │   │   └── page.tsx                 # Analytics page (140 lines)
│   │   └── settings/
│   │       └── page.tsx                 # Settings page (120 lines)
│   └── api/                             # API routes
│       └── temporal/
│           └── signal/
│               └── route.ts             # Signal endpoint (60 lines)
├── components/                          # React components
│   ├── matrix/
│   │   ├── matrix-grid.tsx              # AG Grid wrapper (180 lines)
│   │   ├── column-defs.ts               # Column definitions (120 lines)
│   │   ├── status-badge.tsx             # Status renderer (40 lines)
│   │   ├── action-buttons.tsx           # Action buttons (80 lines)
│   │   └── filter-bar.tsx               # Grid filters (100 lines)
│   ├── logic-cards/
│   │   ├── proposal-modal.tsx           # Modal container (190 lines)
│   │   ├── code-display.tsx             # Code viewer (80 lines)
│   │   ├── reasoning-steps.tsx          # Reasoning display (90 lines)
│   │   └── rag-citations.tsx            # RAG sources (70 lines)
│   ├── dashboard/
│   │   ├── metrics-card.tsx             # KPI card (60 lines)
│   │   ├── status-pie.tsx               # Pie chart (80 lines)
│   │   └── timeline-chart.tsx           # Line chart (90 lines)
│   ├── auth/
│   │   ├── login-form.tsx               # Login UI (110 lines)
│   │   └── auth-provider.tsx            # Auth context (100 lines)
│   ├── layout/
│   │   ├── header.tsx                   # Top navigation (80 lines)
│   │   ├── sidebar.tsx                  # Side navigation (120 lines)
│   │   └── footer.tsx                   # Footer (40 lines)
│   └── ui/                              # Shadcn components
│       ├── button.tsx                   # (Shadcn)
│       ├── dialog.tsx                   # (Shadcn)
│       ├── badge.tsx                    # (Shadcn)
│       ├── card.tsx                     # (Shadcn)
│       ├── input.tsx                    # (Shadcn)
│       ├── label.tsx                    # (Shadcn)
│       ├── toast.tsx                    # (Shadcn)
│       └── use-toast.ts                 # (Shadcn hook)
├── lib/                                 # Utilities
│   ├── supabase/
│   │   ├── client.ts                    # Browser client (15 lines)
│   │   ├── server.ts                    # Server client (15 lines)
│   │   ├── middleware.ts                # Middleware client (20 lines)
│   │   └── realtime.ts                  # Realtime hook (90 lines)
│   ├── temporal/
│   │   └── signal-client.ts             # Signal helper (40 lines)
│   ├── utils.ts                         # Helper functions (100 lines)
│   └── types.ts                         # Shared types (150 lines)
├── hooks/                               # Custom hooks
│   ├── use-proposals.ts                 # Proposals data (80 lines)
│   ├── use-realtime.ts                  # Realtime wrapper (50 lines)
│   ├── use-approval.ts                  # Approval actions (60 lines)
│   ├── use-auth.ts                      # Auth helper (30 lines)
│   └── use-connection-status.ts         # Connection state (40 lines)
├── store/                               # Zustand stores
│   ├── proposals-store.ts               # Proposals state (150 lines)
│   └── ui-store.ts                      # UI state (80 lines)
├── __tests__/                           # Tests
│   ├── unit/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── utils/
│   └── e2e/
│       ├── login.spec.ts
│       ├── matrix.spec.ts
│       └── approval.spec.ts
├── public/                              # Static assets
│   ├── logo.svg
│   └── favicon.ico
├── .env.local                           # Environment variables
├── .env.example                         # Example env
├── .eslintrc.json                       # ESLint config
├── .prettierrc                          # Prettier config
├── jest.config.js                       # Jest config
├── playwright.config.ts                 # Playwright config
├── middleware.ts                        # Route protection (35 lines)
├── next.config.js                       # Next.js config (80 lines)
├── package.json                         # Dependencies
├── tailwind.config.js                   # Tailwind config (60 lines)
├── tsconfig.json                        # TypeScript config
└── README.md                            # Frontend docs
```

**Total Files**: ~60 files  
**Custom Code Files**: ~45 files (excluding Shadcn, configs)  
**Compliance**: 100% files <200 lines

### 10.2 File Size Summary

| Directory | Files | Avg Lines | Max Lines |
|-----------|-------|-----------|-----------|
| app/ | 10 | 90 | 180 |
| components/matrix/ | 5 | 120 | 190 |
| components/logic-cards/ | 4 | 85 | 110 |
| components/dashboard/ | 3 | 75 | 90 |
| components/auth/ | 2 | 105 | 110 |
| components/layout/ | 3 | 80 | 120 |
| lib/ | 7 | 60 | 150 |
| hooks/ | 5 | 50 | 80 |
| store/ | 2 | 115 | 150 |
| **Total Custom** | **41** | **85** | **190** |

**Largest Files**:
1. `components/logic-cards/proposal-modal.tsx` - 190 lines
2. `components/matrix/matrix-grid.tsx` - 180 lines
3. `app/layout.tsx` - 180 lines

All **under 200 lines** ✅

---

## 11. Implementation Plan

### 11.1 Phase 4.1: Foundation (8 hours)

**Goal**: Get Next.js running with authentication and basic grid

**Tasks**:

1. **Project Initialization** (1 hour)
   - `npx create-next-app@latest frontend --typescript --tailwind --app`
   - Install dependencies:
     ```bash
     npm install @supabase/auth-helpers-nextjs @supabase/supabase-js
     npm install ag-grid-community ag-grid-react
     npm install zustand
     npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
     npm install lucide-react
     npm install zod react-hook-form @hookform/resolvers
     ```
   - Configure `tsconfig.json` (strict mode)
   - Configure `tailwind.config.js` (custom colors)

2. **Shadcn UI Setup** (30 min)
   - Initialize Shadcn: `npx shadcn-ui@latest init`
   - Add components:
     ```bash
     npx shadcn-ui@latest add button dialog card badge input label toast
     ```

3. **Supabase Client Setup** (30 min)
   - Create `lib/supabase/client.ts`
   - Create `lib/supabase/server.ts`
   - Create `lib/supabase/middleware.ts`
   - Add environment variables to `.env.local`

4. **Authentication** (2 hours)
   - Build `components/auth/auth-provider.tsx`
   - Build `components/auth/login-form.tsx`
   - Build `app/(auth)/login/page.tsx`
   - Build `app/(auth)/callback/page.tsx`
   - Configure `middleware.ts` for route protection
   - Test OAuth flow (Google, GitHub)

5. **Layout & Navigation** (2 hours)
   - Build `app/layout.tsx` (root layout with providers)
   - Build `app/(dashboard)/layout.tsx` (dashboard shell)
   - Build `components/layout/header.tsx`
   - Build `components/layout/sidebar.tsx`
   - Build `components/layout/footer.tsx`
   - Responsive design (mobile hamburger menu)

6. **Basic Matrix Grid** (2 hours)
   - Build `components/matrix/matrix-grid.tsx`
   - Build `components/matrix/column-defs.ts`
   - Build `app/(dashboard)/matrix/page.tsx`
   - Fetch proposals from Supabase
   - Display in AG Grid
   - Test with mock data

**Deliverables**:
- ✅ Next.js app running on `localhost:3000`
- ✅ Login/logout working
- ✅ Protected routes enforced
- ✅ Basic grid displaying data

**Acceptance Criteria**:
- `npm run dev` starts server
- Can login with OAuth
- Matrix page loads with grid
- TypeScript compiles with no errors

---

### 11.2 Phase 4.2: Real-time & Actions (12 hours)

**Goal**: Add real-time updates, approval buttons, and proposal modals

**Tasks**:

1. **Zustand Store** (1 hour)
   - Build `store/proposals-store.ts`
   - Build `store/ui-store.ts`
   - Integrate with components

2. **Real-time Subscriptions** (2 hours)
   - Build `lib/supabase/realtime.ts`
   - Build `hooks/use-realtime.ts`
   - Build `hooks/use-connection-status.ts`
   - Subscribe to `process_events` table
   - Update grid on INSERT/UPDATE
   - Connection status indicator in header

3. **Temporal Signal API** (2 hours)
   - Build `app/api/temporal/signal/route.ts`
   - Install `@temporalio/client` for Next.js API route
   - Test signal sending with Temporal running
   - Error handling and retries

4. **Approval UI** (2 hours)
   - Build `components/matrix/action-buttons.tsx`
   - Build `components/matrix/status-badge.tsx`
   - Build `hooks/use-approval.ts`
   - Integrate approve/reject buttons in grid
   - Optimistic UI updates
   - Toast notifications

5. **Proposal Modal (Logic Card)** (4 hours)
   - Build `components/logic-cards/proposal-modal.tsx`
   - Build `components/logic-cards/code-display.tsx`
   - Build `components/logic-cards/reasoning-steps.tsx`
   - Build `components/logic-cards/rag-citations.tsx`
   - Install `react-syntax-highlighter` for code display
   - Tabbed interface (Code / Reasoning / RAG / Meta)
   - Modal opens on row double-click

6. **Testing** (1 hour)
   - Test real-time updates (manual: create proposal in database)
   - Test approve flow (workflow resumes)
   - Test reject flow (workflow terminates)
   - Test modal display

**Deliverables**:
- ✅ Real-time updates working (<1s latency)
- ✅ Approve/Reject buttons functional
- ✅ Proposal modal with code display
- ✅ Temporal signal API working

**Acceptance Criteria**:
- Grid updates in real-time when proposal created
- Approve button sends signal to Temporal
- Modal shows code with syntax highlighting
- Status updates optimistically then confirms

---

### 11.3 Phase 4.3: Dashboard & Testing (12 hours)

**Goal**: Add analytics dashboard, comprehensive tests, and polish

**Tasks**:

1. **Analytics Dashboard** (4 hours)
   - Build `app/(dashboard)/analytics/page.tsx`
   - Build `components/dashboard/metrics-card.tsx`
   - Build `components/dashboard/status-pie.tsx`
   - Build `components/dashboard/timeline-chart.tsx`
   - Install `recharts` for visualizations
   - Fetch aggregate data from Supabase
   - Display KPIs:
     - Total proposals
     - Approval rate
     - Average approval time
     - Recent activity feed

2. **Grid Enhancements** (2 hours)
   - Build `components/matrix/filter-bar.tsx`
   - Advanced filtering (status, date range, search)
   - Column resizing/reordering
   - Bulk selection for multi-approve/reject
   - CSV export

3. **Settings Page** (1 hour)
   - Build `app/(dashboard)/settings/page.tsx`
   - User profile display
   - Theme switcher (light/dark/system)
   - Notification preferences

4. **Unit Tests** (2 hours)
   - Test utilities (`lib/utils.ts`)
   - Test hooks (`use-approval`, `use-realtime`)
   - Test stores (Zustand actions)
   - Test cell renderers
   - Jest + React Testing Library
   - **Target**: >80% coverage

5. **E2E Tests** (2 hours)
   - Test login flow
   - Test matrix grid loading
   - Test approve workflow
   - Test reject workflow
   - Test modal interaction
   - Playwright across Chrome, Firefox
   - **Target**: Critical paths covered

6. **Polish & Responsive** (1 hour)
   - Mobile responsive design (320px+)
   - Loading skeletons
   - Error boundaries
   - Accessibility (WCAG AA)
   - Performance optimization (lazy loading)

**Deliverables**:
- ✅ Analytics dashboard with charts
- ✅ Advanced grid filtering
- ✅ Unit tests (>80% coverage)
- ✅ E2E tests (critical paths)
- ✅ Mobile-responsive design

**Acceptance Criteria**:
- Dashboard displays accurate metrics
- Filters work correctly
- Tests pass (`npm run test`)
- E2E tests pass (`npx playwright test`)
- Lighthouse score >90

---

## 12. Testing Strategy

### 12.1 Unit Tests (Jest + RTL)

**Test Files**:
- `__tests__/unit/hooks/use-approval.test.ts`
- `__tests__/unit/hooks/use-realtime.test.ts`
- `__tests__/unit/store/proposals-store.test.ts`
- `__tests__/unit/components/status-badge.test.tsx`
- `__tests__/unit/utils/utils.test.ts`

**Example** (`use-approval.test.ts`):
```typescript
import { renderHook, act } from '@testing-library/react';
import { useApproval } from '@/hooks/use-approval';
import { useProposalsStore } from '@/store/proposals-store';

jest.mock('@/store/proposals-store');

describe('useApproval', () => {
  it('should approve proposal successfully', async () => {
    const mockApprove = jest.fn().mockResolvedValue(undefined);
    (useProposalsStore as jest.Mock).mockReturnValue({
      approveProposal: mockApprove,
    });
    
    const { result } = renderHook(() => useApproval());
    
    await act(async () => {
      await result.current.handleApprove('proposal-id', 'workflow-id');
    });
    
    expect(mockApprove).toHaveBeenCalledWith('proposal-id', 'workflow-id');
  });
});
```

**Coverage Target**: >80%

### 12.2 Integration Tests (RTL)

**Test Files**:
- `__tests__/integration/matrix-grid.test.tsx`
- `__tests__/integration/proposal-modal.test.tsx`
- `__tests__/integration/login-form.test.tsx`

**Example** (`matrix-grid.test.tsx`):
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MatrixGrid } from '@/components/matrix/matrix-grid';

describe('MatrixGrid', () => {
  const mockProposals = [
    {
      id: '1',
      workflow_id: 'wf-1',
      event_name: 'code_generated',
      event_metadata: { status: 'pending' },
      created_at: '2026-01-30T10:00:00Z',
    },
  ];
  
  it('should render proposals in grid', () => {
    render(<MatrixGrid proposals={mockProposals} loading={false} />);
    
    expect(screen.getByText('code_generated')).toBeInTheDocument();
    expect(screen.getByText('pending')).toBeInTheDocument();
  });
  
  it('should call onApprove when approve button clicked', async () => {
    const mockOnApprove = jest.fn();
    render(
      <MatrixGrid
        proposals={mockProposals}
        loading={false}
        onApprove={mockOnApprove}
      />
    );
    
    const approveButton = screen.getByRole('button', { name: /approve/i });
    await userEvent.click(approveButton);
    
    expect(mockOnApprove).toHaveBeenCalledWith('1');
  });
});
```

### 12.3 E2E Tests (Playwright)

**Test Files**:
- `__tests__/e2e/login.spec.ts`
- `__tests__/e2e/matrix.spec.ts`
- `__tests__/e2e/approval.spec.ts`

**Example** (`approval.spec.ts`):
```typescript
import { test, expect } from '@playwright/test';

test.describe('Approval Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://localhost:3000/login');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/matrix');
  });
  
  test('should approve proposal', async ({ page }) => {
    // Wait for grid to load
    await page.waitForSelector('[role="grid"]');
    
    // Find first pending proposal
    const firstRow = page.locator('[role="row"]').nth(1);
    const approveButton = firstRow.locator('button', { hasText: /approve/i });
    
    // Click approve
    await approveButton.click();
    
    // Verify toast notification
    await expect(page.locator('.toast')).toContainText('Proposal Approved');
    
    // Verify status changed (optimistic update)
    await expect(firstRow).toContainText('approved');
  });
  
  test('should open proposal modal on double-click', async ({ page }) => {
    await page.waitForSelector('[role="grid"]');
    
    // Double-click first row
    const firstRow = page.locator('[role="row"]').nth(1);
    await firstRow.dblclick();
    
    // Verify modal opened
    await expect(page.locator('[role="dialog"]')).toBeVisible();
    await expect(page.locator('[role="dialog"]')).toContainText('Proposal Details');
  });
});
```

**Coverage Target**: Critical user paths (login → approve → verify)

---

## 13. Performance Optimization

### 13.1 Next.js Optimizations

**1. React Server Components (RSC)**
- Use RSC for static layouts, headers, footers
- Reduce client-side JavaScript bundle

**2. Streaming & Suspense**
```typescript
// app/(dashboard)/matrix/page.tsx
import { Suspense } from 'react';
import { MatrixGrid } from '@/components/matrix/matrix-grid';
import { GridSkeleton } from '@/components/skeletons/grid-skeleton';

export default function MatrixPage() {
  return (
    <Suspense fallback={<GridSkeleton />}>
      <MatrixGrid />
    </Suspense>
  );
}
```

**3. Image Optimization**
```typescript
import Image from 'next/image';

<Image
  src="/logo.svg"
  alt="Logo"
  width={100}
  height={100}
  priority // for above-the-fold images
/>
```

**4. Code Splitting**
```typescript
import dynamic from 'next/dynamic';

const ProposalModal = dynamic(() => import('@/components/logic-cards/proposal-modal'), {
  loading: () => <p>Loading...</p>,
  ssr: false, // disable SSR for heavy components
});
```

### 13.2 AG Grid Optimizations

**1. Virtual Scrolling** (default, automatic)

**2. Row Buffer**
```typescript
<AgGridReact
  rowBuffer={10} // number of rows to render outside viewport
  rowModelType="clientSide"
  // ...
/>
```

**3. Suppress Animations**
```typescript
<AgGridReact
  suppressAnimationFrame={true} // for large datasets
  // ...
/>
```

**4. Pagination Fallback**
- If dataset > 10,000 rows, enable server-side pagination

### 13.3 Real-time Optimizations

**1. Debounce Updates**
```typescript
import { debounce } from 'lodash';

const handleUpdate = debounce((payload) => {
  updateProposal(payload.new.id, payload.new);
}, 300);
```

**2. Selective Subscriptions**
- Only subscribe to `event_type=proposal_created`
- Filter by `user_id` if needed (RLS handles this)

**3. Connection Pooling**
- Reuse Supabase client instance
- Single WebSocket connection for all subscriptions

### 13.4 Bundle Size Optimization

**1. Tree Shaking**
- Import only needed AG Grid features
- Use named imports from libraries

**2. Lazy Loading**
- Use `next/dynamic` for heavy components
- Code split by route (automatic with App Router)

**3. Font Optimization**
```typescript
// app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'], display: 'swap' });
```

**Target Metrics**:
- Initial Load: <2s (LCP)
- Interaction Delay: <100ms (FID)
- Layout Shift: <0.1 (CLS)
- Bundle Size: <300KB (gzipped)

---

## 14. Security Considerations

### 14.1 Authentication Security

**1. Secure Session Management**
- HttpOnly cookies (Supabase handles this)
- SameSite: 'lax'
- Automatic token refresh

**2. OAuth Security**
- Use PKCE flow (Supabase Auth default)
- Validate redirect URLs

**3. Password Requirements** (if implementing email/password)
- Minimum 8 characters
- Complexity rules (uppercase, lowercase, number)

### 14.2 Authorization Security

**1. Row Level Security (RLS)**
- All Supabase queries filtered by `user_id`
- RLS policies enforce `auth.uid() = user_id`

**2. Role-Based Access Control (RBAC)**
```typescript
// Check user role before showing admin features
const { data: user } = await supabase
  .from('users')
  .select('role')
  .eq('id', session.user.id)
  .single();

if (user.role === 'admin') {
  // Show admin UI
}
```

**3. API Route Protection**
```typescript
// app/api/temporal/signal/route.ts
export async function POST(request: NextRequest) {
  // Verify session
  const supabase = createServerClient();
  const { data: { session } } = await supabase.auth.getSession();
  
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  // ... rest of logic
}
```

### 14.3 Input Validation

**1. Zod Schemas**
```typescript
const RejectRequestSchema = z.object({
  proposalId: z.string().uuid(),
  reason: z.string().min(10).max(500),
});
```

**2. Sanitize User Input**
- Escape HTML in rejection reasons
- Validate workflow IDs (UUID format)

**3. Rate Limiting**
```typescript
// middleware.ts (use rate-limit library)
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
});
```

### 14.4 XSS Prevention

**1. React's Built-in Escaping**
- React escapes all values by default
- Avoid `dangerouslySetInnerHTML`

**2. Content Security Policy (CSP)**
```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-eval' 'unsafe-inline';
      style-src 'self' 'unsafe-inline';
      img-src 'self' blob: data:;
      font-src 'self';
      connect-src 'self' https://*.supabase.co;
    `.replace(/\s{2,}/g, ' ').trim()
  }
];
```

### 14.5 HTTPS Only

**Production Configuration**:
```typescript
// next.config.js
module.exports = {
  async redirects() {
    return [
      {
        source: '/:path*',
        has: [
          {
            type: 'header',
            key: 'x-forwarded-proto',
            value: 'http',
          },
        ],
        destination: 'https://your-domain.com/:path*',
        permanent: true,
      },
    ];
  },
};
```

---

## 15. Deployment Considerations

### 15.1 Vercel Deployment (Recommended)

**Why Vercel**:
- Created by Next.js team (perfect integration)
- Automatic deployments from Git
- Edge functions (fast globally)
- Free tier sufficient for MVP

**Setup**:
1. Push code to GitHub
2. Connect Vercel to repository
3. Configure environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `TEMPORAL_ADDRESS`
4. Deploy automatically on push to `main`

**Environment Variables**:
```bash
# .env.local (development)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
TEMPORAL_ADDRESS=localhost:7233

# Vercel (production)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
TEMPORAL_ADDRESS=production-temporal.example.com:7233
```

### 15.2 Alternative: Self-Hosted (Docker)

**Dockerfile**:
```dockerfile
FROM node:18-alpine AS base

# Install dependencies
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Build
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production
FROM base AS runner
WORKDIR /app
ENV NODE_ENV production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000
CMD ["node", "server.js"]
```

**Docker Compose** (add to existing):
```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - TEMPORAL_ADDRESS=temporal:7233
    depends_on:
      - temporal
```

---

## 16. Success Criteria & Acceptance

### 16.1 Functional Requirements

| Requirement | Acceptance Criteria | Status |
|-------------|-------------------|--------|
| **FR-1: Matrix Grid** | Display 10K+ proposals smoothly | ⏳ |
| **FR-2: Real-time** | Updates appear <1s after database change | ⏳ |
| **FR-3: Approval** | Approve button sends signal to Temporal | ⏳ |
| **FR-4: Logic Cards** | Modal shows code, reasoning, RAG sources | ⏳ |
| **FR-5: Dashboard** | Analytics display accurate metrics | ⏳ |
| **FR-6: Authentication** | Login with OAuth (Google, GitHub) works | ⏳ |

### 16.2 Non-Functional Requirements

| Requirement | Target | Validation |
|-------------|--------|------------|
| **Performance** | LCP <2s | Lighthouse |
| **Real-time Latency** | <1s | Manual test |
| **Code Quality** | 100% <200 lines | ESLint |
| **Type Safety** | 0 errors | `tsc --noEmit` |
| **Test Coverage** | >80% | Jest coverage |
| **Accessibility** | WCAG AA | Axe DevTools |

### 16.3 Phase 4 Complete When

✅ All functional requirements met  
✅ All non-functional requirements met  
✅ Unit tests passing (>80% coverage)  
✅ E2E tests passing (critical paths)  
✅ Lighthouse score >90  
✅ TypeScript strict mode (0 errors)  
✅ Production deployment successful  

---

## 17. Risk Mitigation

### 17.1 Technical Risks

| Risk | Mitigation |
|------|------------|
| **AG Grid performance degradation** | Use virtual scrolling, pagination fallback, row buffer tuning |
| **Real-time connection instability** | Auto-reconnect, offline mode UI, connection status indicator |
| **Temporal signal timeout** | Retry logic (3 attempts), timeout alerts, fallback to manual sync |
| **Type generation drift** | CI/CD step to regenerate types on schema change |
| **Bundle size bloat** | Code splitting, tree shaking, lazy loading, bundle analyzer |

### 17.2 Process Risks

| Risk | Mitigation |
|------|------------|
| **200-line violations** | Pre-commit ESLint hook, CI/CD check, manual review |
| **Scope creep** | Stick to defined phases, defer P2 features to future |
| **Testing gaps** | Define critical paths early, prioritize high-impact tests |
| **Integration issues** | Test with real Temporal/Supabase early, not just mocks |

---

## 18. Future Enhancements (Post-MVP)

### 18.1 Phase 4+ Features

1. **Advanced Filtering**
   - Saved filter presets
   - Complex boolean filters
   - Full-text search across proposals

2. **Bulk Operations**
   - Multi-select approve/reject
   - Batch export to Excel (AG Grid Enterprise)
   - Scheduled approvals

3. **Notifications**
   - Browser push notifications
   - Email alerts for pending approvals
   - Slack integration

4. **Admin Dashboard**
   - User management
   - System health monitoring
   - Configuration UI

5. **Mobile App**
   - React Native mobile app
   - Push notifications
   - Simplified approval interface

6. **AI Insights**
   - Approval pattern analysis
   - Anomaly detection
   - Recommendation engine ("auto-approve if...")

---

## 19. Appendices

### 19.1 Dependencies List

**Core**:
```json
{
  "dependencies": {
    "next": "^14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@supabase/auth-helpers-nextjs": "^0.9.0",
    "@supabase/supabase-js": "^2.38.0",
    "ag-grid-community": "^31.0.0",
    "ag-grid-react": "^31.0.0",
    "zustand": "^4.5.0",
    "@temporalio/client": "^1.9.0",
    "zod": "^3.22.0",
    "react-hook-form": "^7.50.0",
    "@hookform/resolvers": "^3.3.0",
    "react-syntax-highlighter": "^15.5.0",
    "recharts": "^2.10.0",
    "lucide-react": "^0.307.0"
  },
  "devDependencies": {
    "typescript": "^5.3.3",
    "@types/node": "^20.11.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "tailwindcss": "^3.4.0",
    "eslint": "^8.56.0",
    "eslint-config-next": "^14.1.0",
    "prettier": "^3.2.0",
    "jest": "^29.7.0",
    "@testing-library/react": "^14.1.0",
    "@testing-library/jest-dom": "^6.1.0",
    "playwright": "^1.40.0",
    "husky": "^8.0.3",
    "lint-staged": "^15.2.0"
  }
}
```

### 19.2 Environment Variables

```bash
# .env.example
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Temporal
TEMPORAL_ADDRESS=localhost:7233

# Next.js
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 19.3 Useful Commands

```bash
# Development
npm run dev              # Start dev server
npm run build            # Build for production
npm run start            # Start production server
npm run lint             # Run ESLint
npm run format           # Format with Prettier

# Testing
npm run test             # Run Jest tests
npm run test:watch       # Jest watch mode
npm run test:coverage    # Generate coverage report
npx playwright test      # Run E2E tests

# Database
npx supabase gen types typescript --project-id <id> > supabase/database.types.ts
```

---

## 20. Conclusion

This architecture document provides a comprehensive blueprint for Phase 4: The Command Center. With a proven technology stack (Next.js, AG Grid, Supabase, Zustand), clear component boundaries (100% <200 lines), and a phased implementation plan (Foundation → Real-time → Dashboard), we're positioned for a successful 35-40 hour implementation.

**Key Strengths**:
- ✅ Proven tech stack (production-ready)
- ✅ Clear component hierarchy (modular, testable)
- ✅ Real-time architecture (Supabase Realtime)
- ✅ Strong type safety (TypeScript strict mode)
- ✅ Comprehensive testing (unit + E2E)
- ✅ Security-first (RLS, auth, validation)

**Next Steps**:
1. **VAN QA Mode** (2-3 hours) - Validate technology setup
2. **BUILD Mode** (35-40 hours) - Implement per phase plan
3. **TESTING Mode** (4 hours) - Run comprehensive tests
4. **REFLECT & ARCHIVE** (1.5 hours) - Document lessons

**Expected Outcome**: Production-ready Matrix UI enabling human-in-the-loop AI governance within **~52 hours total effort**.

---

**Architecture Complete**: 2026-01-30  
**Next Mode**: VAN QA  
**Total Document Size**: ~40KB  
**Status**: ✅ READY FOR VALIDATION
