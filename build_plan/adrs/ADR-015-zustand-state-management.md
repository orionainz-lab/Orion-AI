# ADR-015: Zustand for State Management

**Status**: ACCEPTED  
**Date**: 2026-01-30  
**Phase**: Phase 4 - Frontend  
**Deciders**: System Architect, Senior Frontend Engineer

---

## Context

The Command Center frontend requires global state management for:
- Proposals data (list, CRUD operations)
- UI state (modals, filters, selections)
- User session (auth, preferences)

We need a state management solution that is lightweight, TypeScript-friendly, and easy to test.

---

## Decision

Use **Zustand** for global state management.

---

## Rationale

### 1. Lightweight (1KB vs 8KB Redux)

**Bundle Size Comparison**:
- Zustand: 1.2KB (gzipped)
- Redux Toolkit: 8.4KB (gzipped)
- React Context: Built-in (0KB), but performance issues

**Benefit**: Faster page loads, especially on mobile.

### 2. No Boilerplate

**Zustand** (Simple):
```typescript
const useStore = create((set) => ({
  proposals: [],
  fetchProposals: async () => {
    const data = await api.getProposals();
    set({ proposals: data });
  },
}));
```

**Redux Toolkit** (Verbose):
```typescript
const slice = createSlice({
  name: 'proposals',
  initialState: { proposals: [] },
  reducers: {
    setProposals: (state, action) => {
      state.proposals = action.payload;
    },
  },
});

const fetchProposals = createAsyncThunk('proposals/fetch', async () => {
  return await api.getProposals();
});
```

**Benefit**: 50% less code, faster development.

### 3. TypeScript-First

**Zustand** (Native TypeScript):
```typescript
interface ProposalsState {
  proposals: Proposal[];
  fetchProposals: () => Promise<void>;
}

const useProposalsStore = create<ProposalsState>((set) => ({
  proposals: [],
  fetchProposals: async () => {
    const data = await api.getProposals();
    set({ proposals: data });
  },
}));
```

**Auto-completion, type inference, compile-time safety.**

### 4. Selective Subscriptions (Performance)

**Zustand** (Granular):
```typescript
// Only re-renders when proposals change, not entire store
const proposals = useProposalsStore((state) => state.proposals);
```

**React Context** (All or nothing):
```typescript
// Re-renders on any context value change
const { proposals, ui, user } = useContext(AppContext);
```

**Benefit**: Fewer re-renders, better performance.

### 5. Built-in DevTools

Zustand integrates with Redux DevTools:
```typescript
const useStore = create(
  devtools((set) => ({
    proposals: [],
    // ...
  }), { name: 'proposals-store' })
);
```

**Features**: Time-travel debugging, state inspection, action logging.

---

## Store Architecture

### Two Stores (Separation of Concerns)

**1. Proposals Store** (`store/proposals-store.ts`)
- Manages proposal data
- Handles CRUD operations
- Coordinates with Supabase
- ~150 lines

**2. UI Store** (`store/ui-store.ts`)
- Manages ephemeral UI state
- Modal open/close, filters, selections
- Persisted preferences (theme, sidebar collapsed)
- ~80 lines

**Why Two Stores?**
- Clearer responsibilities
- Easier testing (mock proposals without UI state)
- Better performance (UI changes don't affect proposal subscriptions)

---

## Consequences

### Positive

✅ **Lightweight**: 1KB bundle size  
✅ **Simple API**: No boilerplate, easy to learn  
✅ **TypeScript-First**: Native support, great DX  
✅ **Performance**: Selective subscriptions, fewer re-renders  
✅ **DevTools**: Redux DevTools integration  
✅ **Middleware**: Persist, immer, devtools built-in  

### Negative

⚠️ **Less Familiar**: Team may know Redux better  
⚠️ **Smaller Ecosystem**: Fewer third-party libraries vs Redux  
⚠️ **No Time-Travel by Default**: Need to enable devtools middleware

### Mitigation

- **Learning Curve**: Zustand is simpler than Redux (2-hour learning curve)
- **Ecosystem**: Zustand has all needed features (persist, devtools, immer)
- **Time-Travel**: Enable devtools middleware (one line)

---

## Alternatives Considered

### Alternative 1: Redux Toolkit

**Pros**:
- Industry standard, well-known
- Large ecosystem, many tutorials
- Time-travel debugging
- DevTools

**Cons**:
- 8KB bundle size (8x larger)
- More boilerplate (slices, actions, reducers)
- Steeper learning curve
- Overkill for this app's complexity

**Rejected Because**: Unnecessary complexity and bundle size for our use case.

### Alternative 2: React Context + useReducer

**Pros**:
- Built-in (0 dependencies)
- Simple for small apps
- Works with Server Components

**Cons**:
- Performance issues with many consumers
- All consumers re-render on any context change
- No DevTools
- No persistence middleware
- Verbose reducer patterns

**Rejected Because**: Performance issues at scale (many components subscribing).

### Alternative 3: Jotai (Atomic State)

**Pros**:
- Atomic state model (like Recoil)
- Lightweight (~3KB)
- TypeScript-first

**Cons**:
- Less intuitive than Zustand
- Atomic model overkill for our use case
- Smaller community

**Rejected Because**: Zustand simpler and sufficient.

### Alternative 4: Recoil

**Pros**:
- Facebook-backed
- Atomic state model
- Concurrent Mode support

**Cons**:
- Still experimental
- Larger bundle (~14KB)
- More complex API

**Rejected Because**: Experimental status, larger bundle.

---

## Implementation Example

### Proposals Store

```typescript
// store/proposals-store.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface Proposal {
  id: string;
  workflow_id: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

interface ProposalsState {
  proposals: Proposal[];
  loading: boolean;
  fetchProposals: () => Promise<void>;
  approveProposal: (id: string) => Promise<void>;
}

export const useProposalsStore = create<ProposalsState>()(
  devtools(
    (set) => ({
      proposals: [],
      loading: false,
      
      fetchProposals: async () => {
        set({ loading: true });
        const data = await api.getProposals();
        set({ proposals: data, loading: false });
      },
      
      approveProposal: async (id) => {
        await api.approve(id);
        set((state) => ({
          proposals: state.proposals.map((p) =>
            p.id === id ? { ...p, status: 'approved' } : p
          ),
        }));
      },
    }),
    { name: 'proposals-store' }
  )
);
```

### UI Store with Persistence

```typescript
// store/ui-store.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  selectedProposalId: string | null;
  isModalOpen: boolean;
  theme: 'light' | 'dark' | 'system';
  
  setSelectedProposal: (id: string | null) => void;
  toggleModal: () => void;
  setTheme: (theme: UIState['theme']) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      selectedProposalId: null,
      isModalOpen: false,
      theme: 'system',
      
      setSelectedProposal: (id) => set({ selectedProposalId: id }),
      toggleModal: () => set((state) => ({ isModalOpen: !state.isModalOpen })),
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'ui-store', // localStorage key
      partialize: (state) => ({ theme: state.theme }), // Only persist theme
    }
  )
);
```

### Usage in Components

```typescript
// components/matrix/matrix-grid.tsx
'use client';

import { useProposalsStore } from '@/store/proposals-store';

export function MatrixGrid() {
  // Selective subscription (only re-renders on proposals change)
  const proposals = useProposalsStore((state) => state.proposals);
  const approveProposal = useProposalsStore((state) => state.approveProposal);
  
  return <AgGridReact rowData={proposals} />;
}
```

---

## Success Criteria

| Metric | Target | Validation |
|--------|--------|------------|
| **Bundle Size** | <2KB | Webpack analyzer |
| **Re-render Count** | Minimal | React DevTools Profiler |
| **Type Safety** | 100% | `tsc --noEmit` |
| **DevTools** | Working | Redux DevTools extension |

---

## References

- [Zustand Documentation](https://zustand-demo.pmnd.rs/)
- [Zustand vs Redux Comparison](https://github.com/pmndrs/zustand#comparison-with-other-state-management-libraries)
- [Why Zustand over Redux](https://tkdodo.eu/blog/working-with-zustand)

---

**Status**: ACCEPTED  
**Last Reviewed**: 2026-01-30  
**Next Review**: Phase 4 BUILD (evaluate if sufficient)
