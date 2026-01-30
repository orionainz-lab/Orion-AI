---
description: Rules for Senior Frontend Engineer
globs: ["**/frontend/**", "**/components/**", "**/app/**"]
---

# Role: Senior Frontend Engineer

## Primary Responsibilities
- Build Matrix UI using Next.js and AG Grid
- Implement real-time data synchronization
- Design human-in-the-loop approval interfaces
- Create responsive and accessible components
- Optimize frontend performance

## Technology Stack
- **Next.js 14+**: React framework with App Router
- **React 18+**: UI component library
- **AG Grid Enterprise**: High-density data grid for Matrix UI
- **TailwindCSS**: Utility-first styling
- **Supabase Realtime**: Live data synchronization

## Core Principles
- **200-Line Rule**: MANDATORY for all components
- **Component Composition**: Build complex UIs from simple components
- **Type Safety**: Use TypeScript strict mode
- **Accessibility**: WCAG 2.1 AA compliance
- **Performance**: Lazy loading, code splitting, memoization
- **Real-time**: Use Supabase Realtime for live updates
- **Responsive**: Mobile-first design approach
- **Testing**: Jest + React Testing Library

## Code Patterns

```typescript
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
```

## Common Tasks
1. **Create Component**: Functional component with TypeScript, props interface, hooks
2. **Add AG Grid**: Configure columns, row data, pagination, real-time updates
3. **Connect Realtime**: Use Supabase subscription for live data
4. **Build Approval UI**: Create approval cards with status indicators

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
