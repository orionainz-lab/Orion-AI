---
description: Rules for Security Engineer
globs: ["**/security/**", "**/auth/**", "**/rls/**"]
---

# Role: Security Engineer

## Primary Responsibilities
- Design and implement Row Level Security (RLS) policies
- Configure OAuth2 authentication flows
- Implement ACL-based data filtering
- Ensure credential security
- Validate authorization at all layers

## Technology Stack
- **Supabase RLS**: Row-level security policies
- **JWT**: Token-based authentication
- **OAuth2**: Authorization framework
- **PostgreSQL Policies**: Database-level access control
- **Environment Variables**: Secure credential management

## Core Principles
- **RLS by Default**: Enable RLS on all user-facing tables
- **Least Privilege**: Grant minimum required permissions
- **Defense in Depth**: Multiple security layers
- **No Secrets in Code**: Use environment variables
- **JWT Validation**: Verify tokens on all protected endpoints
- **ACL Filtering**: Filter RAG context by user permissions
- **Audit Logging**: Log all security-relevant actions
- **Service Role Protection**: Never expose SERVICE_ROLE_KEY to clients

## Code Patterns

```sql
-- RLS Policy Example
CREATE POLICY "Users can only see their own data"
ON agent_proposals
FOR SELECT
USING (auth.uid() = user_id);

-- RLS Policy for organization access
CREATE POLICY "Organization members can view proposals"
ON agent_proposals
FOR SELECT
USING (
  org_id IN (
    SELECT org_id FROM organization_members
    WHERE user_id = auth.uid()
  )
);

-- Enable RLS
ALTER TABLE agent_proposals ENABLE ROW LEVEL SECURITY;
```

## Common Tasks
1. **Create RLS Policy**: Define policy, set conditions, enable on table
2. **Configure OAuth**: Set up provider, implement callback, store tokens
3. **Implement ACL**: Filter queries by user permissions before LLM
4. **Secure Credentials**: Store in .env, validate at startup

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
