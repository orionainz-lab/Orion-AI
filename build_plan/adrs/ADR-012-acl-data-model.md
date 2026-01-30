# ADR-012: ACL Data Model & Permission Inheritance

**Status**: DECIDED  
**Date**: 2026-01-30  
**Deciders**: Security Engineer, Backend Architect, Compliance Team  
**Phase**: Phase 3 - The Secure Context

---

## Context

Phase 3 requires modeling document permissions to enforce security boundaries in the RAG (Retrieval-Augmented Generation) system. The ACL (Access Control List) data model determines:
- **What context AI agents can access** on behalf of users
- **How permissions are inherited** (user, team, organization)
- **How sharing works** (explicit grants, team membership)
- **How RLS policies enforce boundaries** at the database level

**Key Requirements**:
1. **100% Security Enforcement**: No user sees unauthorized documents
2. **Flexible Sharing**: Support individual ownership, team collaboration, explicit grants
3. **Performance**: RLS queries must be <10ms overhead
4. **Testability**: Clear rules that can be validated programmatically
5. **Auditability**: Track who can access what, and why

**Critical Constraint**: This is **security-critical**. Errors could leak sensitive business data to unauthorized users or AI agents.

---

## Decision

**Model Selected**: **Hybrid User-Team ACL with Explicit Grants**

### Schema Overview

```sql
-- Document ownership and visibility
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    
    -- Ownership
    created_by UUID NOT NULL REFERENCES auth.users(id),
    team_id UUID REFERENCES teams(id),
    
    -- Access control
    visibility TEXT NOT NULL DEFAULT 'private',  
    -- Options: 'private', 'team', 'org', 'public'
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Explicit permission grants (user or team)
CREATE TABLE document_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id),    -- NULL for team grant
    team_id UUID REFERENCES teams(id),         -- NULL for user grant
    permission TEXT NOT NULL DEFAULT 'read',   -- 'read', 'write', 'admin'
    granted_by UUID NOT NULL REFERENCES auth.users(id),
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraint: Either user_id OR team_id (not both)
    CONSTRAINT single_grant CHECK (
        (user_id IS NOT NULL AND team_id IS NULL) OR
        (user_id IS NULL AND team_id IS NOT NULL)
    )
);

-- Team membership
CREATE TABLE team_members (
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'member',  -- 'member', 'admin', 'owner'
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (team_id, user_id)
);
```

### RLS Policy

```sql
-- Users see documents based on ownership, team, grants, or public
CREATE POLICY "Users see authorized documents" ON documents
FOR SELECT USING (
    -- 1. Owner
    created_by = auth.uid() 
    OR
    -- 2. Team member (if visibility = 'team')
    (visibility = 'team' AND team_id IN (
        SELECT team_id FROM team_members WHERE user_id = auth.uid()
    ))
    OR
    -- 3. Explicit user grant
    id IN (
        SELECT document_id FROM document_permissions 
        WHERE user_id = auth.uid()
    )
    OR
    -- 4. Team grant (user is member of granted team)
    id IN (
        SELECT dp.document_id FROM document_permissions dp
        JOIN team_members tm ON dp.team_id = tm.team_id
        WHERE tm.user_id = auth.uid()
    )
    OR
    -- 5. Public document
    visibility = 'public'
);
```

---

## Options Considered

### Option 1: Simple User-Level ACLs

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    content TEXT
);

-- RLS: Users see only their own documents
CREATE POLICY "Users see own docs" ON documents
FOR SELECT USING (user_id = auth.uid());
```

**Pros**:
- ✅ Simplest model (minimal complexity)
- ✅ Fastest queries (single equality check)
- ✅ Easiest to test (clear boundaries)
- ✅ No permission inheritance issues

**Cons**:
- ❌ No sharing between users (major limitation)
- ❌ No team collaboration
- ❌ No explicit grants
- ❌ Inflexible for enterprise use cases

**Example Scenario**: User A creates a document. User B cannot access it, even if they're on the same team. No way to share.

**Verdict**: **REJECTED** - Too limiting for enterprise collaboration needs.

---

### Option 2: Hierarchical ACLs (User → Team → Org)

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),      -- Owner
    team_id UUID REFERENCES teams(id),           -- Team-level access
    org_id UUID REFERENCES organizations(id),    -- Org-level access
    content TEXT
);

-- RLS: Users see docs if they match user, team, or org
CREATE POLICY "Hierarchical access" ON documents
FOR SELECT USING (
    user_id = auth.uid() OR
    team_id IN (SELECT team_id FROM team_members WHERE user_id = auth.uid()) OR
    org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid())
);
```

**Pros**:
- ✅ Supports organizational hierarchy
- ✅ Clear ownership levels (user < team < org)
- ✅ Common in enterprise software

**Cons**:
- ❌ Rigid structure (fixed 3 levels)
- ❌ No explicit grants (can't share to specific user outside team)
- ❌ Complex RLS (3 subqueries)
- ❌ Unclear precedence (what if user, team, org all set?)

**Example Scenario**: User A creates a document with team_id='team-123'. All members of team-123 can see it, but User A can't share with User B from team-456.

**Verdict**: **REJECTED** - Too rigid, lacks flexibility for explicit sharing.

---

### Option 3: Hybrid User-Team with Explicit Grants (SELECTED)

```sql
-- See full schema in Decision section above
```

**Pros**:
- ✅ Flexible: Supports ownership, team sharing, explicit grants
- ✅ Extensible: Can add org_id later without breaking changes
- ✅ Clear semantics: visibility + grants
- ✅ Testable: Well-defined rules
- ✅ Standard pattern: Used by Google Docs, Notion, etc.

**Cons**:
- ❌ More complex than Option 1 (but manageable)
- ❌ RLS queries require joins (slight performance cost)
- ❌ More test cases needed

**Example Scenarios**:
1. **Private Doc**: User A creates doc with visibility='private'. Only User A sees it.
2. **Team Doc**: User A creates doc with visibility='team', team_id='team-123'. All team-123 members see it.
3. **Explicit Grant**: User A grants 'read' to User B. User B sees it (even if not on team).
4. **Team Grant**: User A grants 'read' to team-456. All members of team-456 see it.
5. **Public Doc**: visibility='public'. Everyone sees it.

**Verdict**: **SELECTED** - Best balance of flexibility, security, and performance.

---

### Option 4: Role-Based Access Control (RBAC)

```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    permissions JSONB  -- {'documents': ['read', 'write'], ...}
);

CREATE TABLE user_roles (
    user_id UUID REFERENCES auth.users(id),
    role_id UUID REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

CREATE POLICY "Users see docs based on roles" ON documents
FOR SELECT USING (
    -- Complex policy based on role permissions
    ...
);
```

**Pros**:
- ✅ Highly flexible (policy-based)
- ✅ Centralized permission management
- ✅ Scalable for complex enterprise needs

**Cons**:
- ❌ Very complex to implement
- ❌ Harder to test (many edge cases)
- ❌ Overkill for Phase 3
- ❌ RLS policies become very complex

**Verdict**: **REJECTED** - Over-engineered for current needs. Can evolve from Option 3 later if needed.

---

## Rationale

### Why Hybrid User-Team with Explicit Grants?

1. **Flexibility Without Complexity**
   - Simple case: Private docs (just ownership)
   - Team case: Team docs (team membership)
   - Advanced case: Explicit grants (fine-grained sharing)

2. **Real-World Alignment**
   - Mirrors Google Docs, Notion, Slack permissions
   - Familiar to users and developers
   - Proven pattern in production systems

3. **Security by Default**
   - Default visibility='private' (least privilege)
   - Explicit grants required for sharing
   - RLS enforced at PostgreSQL level (can't bypass)

4. **Performance Acceptable**
   - RLS queries optimized with indexes
   - Typical overhead: <10ms (measured in similar systems)
   - Team membership cached in application layer

5. **Testability**
   - Clear rules: owner, team, grant, public
   - Easy to enumerate test cases
   - RLS policies can be unit tested

6. **Extensibility**
   - Can add org_id column later without breaking
   - Can add RBAC on top of this foundation
   - Can add permission levels (read/write/admin)

### Why Not RBAC?

**RBAC is overkill for Phase 3**:
- Phase 3 needs basic document sharing
- RBAC adds complexity without clear benefit
- Can evolve to RBAC later if requirements grow

**Phase 3 Focus**: Get RAG working securely, not build enterprise IAM system.

---

## Implementation Details

### Permission Resolution Algorithm

When User X queries for documents, PostgreSQL evaluates:

```
User X sees document D if:
    D.created_by = X.user_id                              (Owner)
OR  (D.visibility = 'team' AND D.team_id IN X.teams)     (Team)
OR  EXISTS(grant WHERE grant.document_id = D.id AND grant.user_id = X.user_id)  (User Grant)
OR  EXISTS(grant WHERE grant.document_id = D.id AND grant.team_id IN X.teams)   (Team Grant)
OR  D.visibility = 'public'                               (Public)
```

**Order of Evaluation** (PostgreSQL optimizer determines, but conceptually):
1. Check ownership (fastest: equality)
2. Check public (fast: equality)
3. Check team membership (indexed: IN clause)
4. Check grants (indexed: subquery)

### Indexes for Performance

```sql
-- Documents table
CREATE INDEX idx_documents_created_by ON documents(created_by);
CREATE INDEX idx_documents_team_id ON documents(team_id);
CREATE INDEX idx_documents_visibility ON documents(visibility);

-- Team members table
CREATE INDEX idx_team_members_user_id ON team_members(user_id);
CREATE INDEX idx_team_members_team_id ON team_members(team_id);

-- Document permissions table
CREATE INDEX idx_permissions_document_id ON document_permissions(document_id);
CREATE INDEX idx_permissions_user_id ON document_permissions(user_id);
CREATE INDEX idx_permissions_team_id ON document_permissions(team_id);
```

**Expected RLS Overhead**: <10ms (vs no RLS)

### Visibility Levels

| Level | Semantics | Example Use Case |
|-------|-----------|------------------|
| `private` | Only owner sees | Personal notes, drafts |
| `team` | Team members see | Team docs, shared knowledge |
| `org` | Organization members see | Company policies (future) |
| `public` | Everyone sees | Public FAQs, help docs |

### Permission Levels

| Level | Semantics | Capabilities |
|-------|-----------|--------------|
| `read` | View only | Query in RAG, read content |
| `write` | Edit | Modify content, add chunks |
| `admin` | Full control | Change visibility, grant permissions, delete |

**Phase 3 Focus**: Implement `read` only. Add `write`/`admin` in Phase 4.

---

## Security Considerations

### Threat Model

**Threat 1: User A accesses User B's private documents**
- **Mitigation**: RLS policy checks `created_by = auth.uid()`
- **Test**: Create docs as User A, query as User B, verify 0 results

**Threat 2: User A joins Team X to see Team Y's documents**
- **Mitigation**: RLS checks `team_id IN (user's teams)`
- **Test**: Create team doc, verify only team members see it

**Threat 3: Explicit grant bypasses team boundary**
- **Mitigation**: This is intended behavior (explicit grants are explicit)
- **Audit**: Log all grants to `document_permissions` with `granted_by`

**Threat 4: SQL injection in RLS policy**
- **Mitigation**: Parameterized queries in Supabase client
- **Test**: Attempt injection in document queries

**Threat 5: service_role bypasses RLS**
- **Mitigation**: Never use service_role for user-facing queries
- **Review**: Code review all Supabase client instantiations

### Defense in Depth

**Layer 1: Database (RLS)**
```sql
-- PostgreSQL enforces RLS on every SELECT
-- Cannot be bypassed (except by service_role)
```

**Layer 2: Application (ACL Helper)**
```python
# utils/acl_helper.py
async def user_can_access_document(user_id: str, document_id: str) -> bool:
    """Explicit permission check (in addition to RLS)."""
    result = await supabase.table('documents')\
        .select('id')\
        .eq('id', document_id)\
        .execute()  # RLS applies automatically
    
    return len(result.data) > 0
```

**Layer 3: API (JWT Validation)**
```python
# Supabase client uses user's JWT
supabase_client = create_client(
    supabase_url,
    supabase_key,
    options=ClientOptions(
        headers={"Authorization": f"Bearer {user_jwt}"}
    )
)
```

**Layer 4: Audit (Logging)**
```python
# Log all RAG queries to process_events
await logger.log_event(
    event_type='rag_query',
    user_id=user_id,
    input_data={'query': query_text},
    output_data={'document_ids': [r.document_id for r in results]}
)
```

---

## Testing Strategy

### RLS Test Cases

```python
# scripts/test_rls.py

async def test_user_isolation():
    """User A cannot see User B's private docs."""
    # Setup
    user_a_id = create_test_user("user_a")
    user_b_id = create_test_user("user_b")
    
    doc_id = await create_document(
        title="User A Private Doc",
        created_by=user_a_id,
        visibility="private"
    )
    
    # Test: User B queries
    results = await query_as_user(user_b_id, "Private Doc")
    
    # Verify: User B sees 0 documents
    assert len(results) == 0, "User B should not see User A's private doc"

async def test_team_sharing():
    """Team members see team docs, non-members don't."""
    # Setup
    team_id = create_test_team("Engineering")
    user_a_id = create_test_user("user_a")
    user_b_id = create_test_user("user_b")
    user_c_id = create_test_user("user_c")
    
    add_to_team(team_id, user_a_id)
    add_to_team(team_id, user_b_id)
    # user_c is NOT on team
    
    doc_id = await create_document(
        title="Team Engineering Doc",
        created_by=user_a_id,
        team_id=team_id,
        visibility="team"
    )
    
    # Test: All users query
    results_a = await query_as_user(user_a_id, "Engineering")
    results_b = await query_as_user(user_b_id, "Engineering")
    results_c = await query_as_user(user_c_id, "Engineering")
    
    # Verify
    assert doc_id in [r.id for r in results_a], "User A sees team doc"
    assert doc_id in [r.id for r in results_b], "User B sees team doc"
    assert doc_id not in [r.id for r in results_c], "User C does NOT see team doc"

async def test_explicit_grant():
    """Explicit grant allows access outside team."""
    # Setup
    user_a_id = create_test_user("user_a")
    user_b_id = create_test_user("user_b")
    
    doc_id = await create_document(
        title="User A Private Doc",
        created_by=user_a_id,
        visibility="private"
    )
    
    # Grant access to User B
    await grant_permission(
        document_id=doc_id,
        user_id=user_b_id,
        permission="read",
        granted_by=user_a_id
    )
    
    # Test: User B queries
    results = await query_as_user(user_b_id, "Private Doc")
    
    # Verify: User B now sees doc (via explicit grant)
    assert doc_id in [r.id for r in results], "User B sees doc via grant"

async def test_public_visibility():
    """Public docs visible to all users."""
    # Setup
    user_a_id = create_test_user("user_a")
    user_b_id = create_test_user("user_b")
    
    doc_id = await create_document(
        title="Public FAQ",
        created_by=user_a_id,
        visibility="public"
    )
    
    # Test: Any user queries
    results = await query_as_user(user_b_id, "FAQ")
    
    # Verify: User B sees public doc
    assert doc_id in [r.id for r in results], "Public docs visible to all"

# Run all tests
async def test_rls_suite():
    tests = [
        test_user_isolation,
        test_team_sharing,
        test_explicit_grant,
        test_public_visibility
    ]
    
    for test in tests:
        try:
            await test()
            print(f"✅ {test.__name__} PASSED")
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            raise
```

### Performance Test

```python
async def test_rls_performance():
    """Measure RLS overhead on queries."""
    # Setup: 1000 documents, 10 teams, 100 users
    setup_large_dataset()
    
    # Test 1: Query without RLS (service_role)
    start = time.time()
    results_no_rls = await query_service_role("engineering")
    time_no_rls = (time.time() - start) * 1000  # ms
    
    # Test 2: Query with RLS (user JWT)
    start = time.time()
    results_with_rls = await query_as_user(user_id, "engineering")
    time_with_rls = (time.time() - start) * 1000  # ms
    
    overhead = time_with_rls - time_no_rls
    
    # Verify: Overhead <10ms
    assert overhead < 10, f"RLS overhead {overhead}ms exceeds 10ms target"
    
    print(f"RLS overhead: {overhead:.2f}ms (target <10ms)")
```

---

## Consequences

### Positive Consequences

1. **Flexible Sharing**: Supports all common sharing patterns
2. **Security by Default**: Private by default, explicit grants required
3. **PostgreSQL Enforcement**: RLS at database level (can't bypass)
4. **Testable**: Clear rules, easy to verify isolation
5. **Standard Pattern**: Familiar to developers and users

### Negative Consequences

1. **Complexity**: More complex than user-only model
   - Mitigation: Comprehensive test suite, clear documentation
2. **RLS Query Performance**: Requires joins for grants
   - Mitigation: Proper indexes, <10ms overhead target
3. **Team Management**: Requires team membership system
   - Mitigation: Simple team_members table, part of Phase 3
4. **More Test Cases**: Each permission path needs testing
   - Mitigation: Automated test suite (scripts/test_rls.py)

### Neutral Consequences

1. **Explicit Grants Table**: Additional table to maintain
2. **Audit Trail**: All grants logged (good for compliance)
3. **Permission Levels**: Future work (Phase 4: write/admin)

---

## Validation Criteria

Phase 3 VAN QA Mode and Testing:

- [ ] **VAN-QA-3**: RLS policy enforcement validated
  - Test: Create test table with RLS, verify isolation
  - Success: User A cannot query User B's rows

- [ ] **Test-RLS-1**: User isolation test passes
  - Test: User A's private doc not visible to User B
  - Success: 0 results for User B

- [ ] **Test-RLS-2**: Team sharing test passes
  - Test: Team members see team docs
  - Success: Team members see, non-members don't

- [ ] **Test-RLS-3**: Explicit grant test passes
  - Test: Grant allows access
  - Success: Granted user sees doc

- [ ] **Test-RLS-4**: Public visibility test passes
  - Test: Public docs visible to all
  - Success: All users see public docs

- [ ] **Test-RLS-5**: Performance test passes
  - Test: Measure RLS overhead
  - Success: <10ms additional latency

---

## Future Evolution

### Phase 4: Write/Admin Permissions

```sql
-- Add permission checks to INSERT/UPDATE/DELETE policies
CREATE POLICY "Users write with permission" ON documents
FOR UPDATE USING (
    created_by = auth.uid() OR
    id IN (
        SELECT document_id FROM document_permissions
        WHERE user_id = auth.uid() AND permission IN ('write', 'admin')
    )
);
```

### Phase 5: Organization Hierarchy (Optional)

```sql
-- Add org_id column
ALTER TABLE documents ADD COLUMN org_id UUID REFERENCES organizations(id);

-- Update RLS policy
CREATE POLICY "Users see org docs" ON documents
FOR SELECT USING (
    ... existing rules ...
    OR
    (visibility = 'org' AND org_id IN (
        SELECT org_id FROM org_members WHERE user_id = auth.uid()
    ))
);
```

### Phase 6: RBAC (Optional)

Build RBAC on top of this foundation if requirements justify complexity.

---

## Related ADRs

- **ADR-010**: pgvector Configuration (vectors inherit document permissions)
- **ADR-011**: Embedding Model Selection (chunks inherit document ACLs)

---

## References

- [Supabase RLS Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL RLS Documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Google Docs Sharing Model](https://support.google.com/docs/answer/2494822)
- [Notion Permissions](https://www.notion.so/help/shared-pages)

---

**Decision Status**: ✅ DECIDED  
**Validation Status**: ⏳ Pending VAN QA Mode & Testing  
**Supersedes**: None  
**Last Updated**: 2026-01-30
