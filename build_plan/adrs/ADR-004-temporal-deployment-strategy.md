# ADR-004: Temporal.io Deployment Strategy

**Status**: Accepted  
**Date**: 2026-01-30  
**Context**: Phase 1 - The Durable Foundation  
**Deciders**: AI + Developer (Distributed Systems Engineer persona)

---

## Context

Phase 1 requires establishing a Temporal.io workflow execution environment. We need to decide how Temporal Server will be deployed for:
- Local development (fast iteration, debugging)
- Staging/testing environments
- Production deployment (reliability, scalability)

The decision impacts infrastructure complexity, operational burden, and development velocity.

---

## Decision

**Use Hybrid Approach: Docker Compose for Development, Temporal Cloud for Production**

### Local Development
- Docker Compose with official Temporal images
- PostgreSQL for Temporal's persistence
- Temporal UI for workflow visualization
- No external dependencies, zero cost

### Production
- Temporal Cloud (managed service)
- Temporal handles infrastructure, upgrades, monitoring
- Focus on workflow logic, not operations

---

## Rationale

### Why Not Other Options?

**❌ Local Docker Only (Dev & Prod)**
- Production operations burden (monitoring, upgrades, scaling)
- Requires dedicated DevOps expertise
- On-call rotation for Temporal Server issues

**❌ Temporal Cloud Only (Dev & Prod)**
- Development costs (charged per namespace/execution)
- Slower feedback loops (network latency)
- Requires internet connectivity for development

**❌ Self-Hosted Kubernetes**
- Massive operational complexity
- Overkill for current team size
- Distracts from core platform development

### Why Hybrid Works

✅ **Best of Both Worlds**
- Local: Fast iteration, free, isolated testing
- Production: Managed, reliable, scales automatically

✅ **Minimal Code Changes**
- Connection URL is environment variable
- Same workflow/activity code works everywhere
- Easy migration path

✅ **Separation of Concerns**
- Developers focus on workflow logic
- Temporal Cloud handles infrastructure
- Clear responsibility boundaries

---

## Consequences

### Positive
- ✅ Zero cost for local development
- ✅ Production-grade reliability via managed service
- ✅ No operational burden (upgrades, monitoring, scaling)
- ✅ Fast local feedback loops

### Negative
- ⚠️ Need to ensure parity between local and cloud
  - **Mitigation**: Use same Temporal version locally
- ⚠️ Temporal Cloud costs in production (variable by usage)
  - **Mitigation**: Acceptable trade-off for reliability
- ⚠️ Vendor lock-in to Temporal Cloud
  - **Mitigation**: Open-source Temporal Server is fallback

### Neutral
- Configuration must support both environments
- Environment variables manage connection details

---

## Implementation

### Phase 1 (Now)
```yaml
# docker/docker-compose.yml
services:
  temporal:
    image: temporalio/auto-setup:latest
    environment:
      - DB=postgresql
      - POSTGRES_HOST=postgresql
    ports:
      - "7233:7233"
  
  postgresql:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=temporal
      - POSTGRES_USER=temporal
      - POSTGRES_DB=temporal
  
  temporal-ui:
    image: temporalio/ui:latest
    ports:
      - "8080:8080"
```

### Phase 4+ (Production)
```python
# temporal/config.py
import os

def get_temporal_client():
    if os.getenv("ENV") == "production":
        # Temporal Cloud
        return Client(
            target_host=os.getenv("TEMPORAL_CLOUD_URL"),
            namespace=os.getenv("TEMPORAL_NAMESPACE"),
            data_converter=dataclasses.default()
        )
    else:
        # Local Docker
        return Client(
            target_host="localhost:7233",
            namespace="default"
        )
```

---

## Alternatives Considered

| Option | Pros | Cons | Cost | Complexity |
|--------|------|------|------|------------|
| **Hybrid (CHOSEN)** | Best DX, managed prod | Env parity needed | Free dev, pay prod | Low dev, zero ops |
| Local Docker Only | Full control, no costs | Ops burden | Free | High ops |
| Temporal Cloud Only | Fully managed | Dev costs, latency | Pay dev+prod | Low |
| Self-Hosted K8s | Maximum control | Extreme complexity | Infrastructure costs | Very high |

---

## Related Decisions

- **ADR-005**: Workflow State Persistence Strategy
  - Temporal's internal persistence is primary
- **ADR-006**: Worker Deployment Pattern
  - Workers connect to Temporal (local or cloud) via environment config

---

## References

- [Temporal Cloud Documentation](https://docs.temporal.io/cloud)
- [Temporal Docker Compose Setup](https://github.com/temporalio/docker-compose)
- Phase 1 Architecture: `build_plan/phase1-architecture.md`

---

**Status**: ✅ Accepted and Ready for Implementation
