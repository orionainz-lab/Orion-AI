# Frontend Directory

**Purpose**: Next.js application with "Matrix UI"

## Structure

React-based frontend application:

```
frontend/
├── app/               # Next.js 14 app directory
├── components/        # React components
│   ├── matrix/       # Matrix grid components (AG Grid)
│   ├── logic-cards/  # Approval workflow cards
│   └── ui/           # Shared UI components
├── lib/              # Client utilities
├── hooks/            # Custom React hooks
└── public/           # Static assets
```

## Architecture

- **Matrix UI**: High-density agent proposal grid (AG Grid Enterprise)
- **Real-time**: Supabase Realtime for status updates
- **Propose & Approve**: Human-in-the-loop governance workflows

## Coding Standards

- **200-Line Rule**: MANDATORY for all components
- **TypeScript**: Strict mode required
- **Component Pattern**: Functional components with hooks
- **Testing**: Jest + React Testing Library

## Guidelines

1. Use Next.js 14+ App Router
2. Implement AG Grid for Matrix UI
3. Connect to Supabase Realtime
4. Follow modern UX best practices

---

**Phase**: 4 - Command Center  
**Status**: Awaiting frontend development
