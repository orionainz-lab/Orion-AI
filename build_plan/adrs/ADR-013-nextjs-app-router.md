# ADR-013: Next.js App Router vs Pages Router

**Status**: ACCEPTED  
**Date**: 2026-01-30  
**Phase**: Phase 4 - Frontend  
**Deciders**: System Architect, Senior Frontend Engineer

---

## Context

Next.js 13+ introduced the App Router, a new routing paradigm built on React Server Components (RSC). We must decide between the App Router and the traditional Pages Router for the Command Center frontend.

### Background

**Pages Router** (Legacy, Next.js <13):
- File-based routing with `pages/` directory
- Client-side rendering by default
- `getServerSideProps` / `getStaticProps` for data fetching
- Mature, well-documented, stable

**App Router** (Modern, Next.js 13+):
- File-based routing with `app/` directory
- React Server Components (RSC) by default
- Server-first data fetching
- Streaming and Suspense built-in
- Better TypeScript support
- Nested layouts with shared state

---

## Decision

We will use **App Router** for the Command Center frontend.

---

## Rationale

### 1. Performance Benefits

**React Server Components (RSC)**:
- Reduces client-side JavaScript bundle size
- Server-side data fetching without API routes
- Automatic code splitting per route
- **Benefit**: Faster initial page loads, better LCP (Largest Contentful Paint)

**Streaming & Suspense**:
- Progressive rendering of UI
- Show skeleton loaders while data fetches
- **Benefit**: Better perceived performance, lower TTI (Time to Interactive)

**Example**:
```typescript
// App Router (RSC)
export default async function MatrixPage() {
  const proposals = await fetchProposals(); // Server-side
  return <MatrixGrid proposals={proposals} />;
}

// Pages Router (Client-side)
export default function MatrixPage() {
  const [proposals, setProposals] = useState([]);
  useEffect(() => {
    fetchProposals().then(setProposals); // Client-side
  }, []);
  return <MatrixGrid proposals={proposals} />;
}
```

**Result**: App Router reduces client-side JS by ~30-40%.

### 2. Future-Proof

**Industry Direction**:
- React team pushing RSC as the future
- Next.js team deprecated Pages Router features
- New features (Partial Prerendering, Server Actions) App Router only

**Migration Path**:
- Pages Router → App Router migration is painful
- Starting with App Router avoids future rewrite

**Evidence**: Next.js 14 focused on App Router improvements, Pages Router in maintenance mode.

### 3. Better Developer Experience

**TypeScript Support**:
- Better type inference with RSC
- Automatic types for `params`, `searchParams`
- No need for `GetServerSidePropsContext` types

**Layouts & Nested Routing**:
- Shared layouts with persistent state
- Parallel routes (loading multiple things simultaneously)
- Intercepting routes (modals as routes)

**Server Actions**:
- Form handling without API routes
- Direct server mutations from components
- Automatic revalidation

**Example**:
```typescript
// Server Action (App Router)
async function approveProposal(formData: FormData) {
  'use server';
  const id = formData.get('id');
  await supabase.from('process_events').update({ status: 'approved' }).eq('id', id);
  revalidatePath('/matrix');
}

// No API route needed!
```

### 4. Alignment with Phase 4 Requirements

**Matrix Grid**:
- Large dataset (10K+ rows) benefits from server-side rendering
- AG Grid is client-side, but layout/data fetching can be server-side

**Real-time Updates**:
- Supabase Realtime works with both routers
- App Router's streaming allows progressive updates

**Authentication**:
- Middleware-based auth works better with App Router
- Server-side session checks without extra API calls

---

## Consequences

### Positive

✅ **Better Performance**: Smaller bundle, faster loads  
✅ **Future-Proof**: Aligned with React/Next.js direction  
✅ **Better DX**: TypeScript, layouts, server actions  
✅ **SEO-Friendly**: Server-side rendering by default  
✅ **Cost-Effective**: Less compute on client (mobile-friendly)

### Negative

⚠️ **Learning Curve**: Team needs to learn RSC paradigm  
⚠️ **Library Compatibility**: Some libraries don't support RSC (need `'use client'`)  
⚠️ **Debugging**: Server-side errors harder to trace  
⚠️ **Documentation**: Fewer Stack Overflow answers vs Pages Router  

### Mitigation

**Learning Curve**:
- Invest 2-3 hours in Next.js 14 docs
- Follow official examples (Next.js repo)
- Use `'use client'` for interactive components

**Library Compatibility**:
- AG Grid: `'use client'` (expected for data grid)
- Zustand: Works with both
- Supabase: Client-side hooks use `'use client'`

**Debugging**:
- Use Next.js Dev Tools
- Enable verbose logging in dev
- Server errors shown in dev server console

---

## Alternatives Considered

### Alternative 1: Pages Router

**Pros**:
- Mature, stable, well-documented
- More Stack Overflow answers
- Easier migration from existing Next.js apps

**Cons**:
- Deprecated features (not actively developed)
- Worse performance (larger bundles)
- Migration to App Router painful later

**Rejected Because**: Short-term ease outweighed by long-term technical debt.

### Alternative 2: Remix

**Pros**:
- Similar RSC-like patterns
- Nested routing
- Form-first API

**Cons**:
- Less mature ecosystem vs Next.js
- Smaller community
- No Vercel deployment optimization

**Rejected Because**: Next.js has better Vercel integration, larger ecosystem.

### Alternative 3: Pure React SPA (Vite + React Router)

**Pros**:
- Maximum flexibility
- No server-side complexity
- Fast dev server (Vite)

**Cons**:
- No SSR (worse SEO, slower initial load)
- Need separate backend API
- More boilerplate

**Rejected Because**: SSR required for performance, Next.js reduces boilerplate.

---

## Implementation Notes

### File Structure

```
app/
├── layout.tsx                    # Root layout (global providers)
├── page.tsx                      # Home (redirect)
├── (auth)/                       # Auth route group
│   ├── login/page.tsx
│   └── callback/page.tsx
├── (dashboard)/                  # Protected route group
│   ├── layout.tsx               # Dashboard layout (sidebar)
│   ├── matrix/page.tsx
│   ├── analytics/page.tsx
│   └── settings/page.tsx
└── api/                          # API routes (if needed)
    └── temporal/signal/route.ts
```

### Using `'use client'`

Mark components as client-side when they need:
- Interactive hooks (`useState`, `useEffect`, `useRef`)
- Browser APIs (`window`, `document`, `localStorage`)
- Event handlers (`onClick`, `onChange`)
- Third-party libraries that use hooks (AG Grid, Zustand)

**Example**:
```typescript
// components/matrix/matrix-grid.tsx
'use client';

import { AgGridReact } from 'ag-grid-react';
import { useProposalsStore } from '@/store/proposals-store';

export function MatrixGrid() {
  const proposals = useProposalsStore((state) => state.proposals);
  return <AgGridReact rowData={proposals} />;
}
```

### Server Components (Default)

Keep server components for:
- Layouts (header, sidebar, footer)
- Data fetching pages
- Static content
- SEO-critical pages

**Example**:
```typescript
// app/(dashboard)/matrix/page.tsx
import { MatrixGrid } from '@/components/matrix/matrix-grid';

export default async function MatrixPage() {
  // Server-side data fetch (optional, can also fetch client-side)
  return (
    <div>
      <h1>Matrix Grid</h1>
      <MatrixGrid />
    </div>
  );
}
```

---

## Validation

### Success Criteria

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| **Bundle Size** | <300KB (gzipped) | `next build` output |
| **LCP** | <2s | Lighthouse audit |
| **FID** | <100ms | Lighthouse audit |
| **Build Time** | <2min | CI/CD logs |
| **Type Safety** | 0 errors | `tsc --noEmit` |

### Testing

- **Development**: `npm run dev` starts successfully
- **Production**: `npm run build && npm run start` works
- **TypeScript**: No type errors with strict mode
- **Performance**: Lighthouse score >90

---

## References

- [Next.js App Router Docs](https://nextjs.org/docs/app)
- [React Server Components RFC](https://github.com/reactjs/rfcs/blob/main/text/0188-server-components.md)
- [Next.js 14 Announcement](https://nextjs.org/blog/next-14)
- [App Router Performance Case Study](https://vercel.com/blog/nextjs-app-router-performance)

---

## Decision Log

| Date | Author | Decision |
|------|--------|----------|
| 2026-01-30 | System Architect | ADR Created - App Router selected |

---

**Status**: ACCEPTED  
**Last Reviewed**: 2026-01-30  
**Next Review**: Phase 4 BUILD completion (or if significant issues arise)
