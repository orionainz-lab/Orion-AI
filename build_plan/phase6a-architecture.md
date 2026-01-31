# Phase 6A Architecture: Production Deployment

**Created**: 2026-01-31  
**Complexity**: Level 3 (Medium) - DevOps & Infrastructure  
**Estimated Duration**: 8-13 hours  
**Prerequisites**: All Phases 0-5 Complete ✅

---

## Executive Summary

Phase 6A transforms the development platform into a **production-ready system** with:
- Automated CI/CD pipeline (GitHub Actions)
- Environment-specific configurations (dev, staging, prod)
- Monitoring & observability (Uptime, logs, metrics)
- Security hardening (secrets management, HTTPS, rate limiting)
- Deployment automation (Vercel, Railway, Docker)

### Success Criteria
- ✅ Zero-downtime deployments
- ✅ Automated testing on every commit
- ✅ Environment parity (dev/staging/prod)
- ✅ <1 min deployment time
- ✅ 99.9% uptime monitoring
- ✅ Automated rollback on failure

---

## Architecture Decisions (ADRs)

### ADR-021: Deployment Platform Strategy
**Decision**: Hybrid Cloud Deployment

| Component | Platform | Rationale |
|-----------|----------|-----------|
| Frontend | **Vercel** | Zero-config Next.js, edge functions, instant rollback |
| Backend API | **Railway** | Easy Python deployment, env management, auto-scaling |
| Temporal | **Temporal Cloud** | Managed workflows, high availability, zero ops |
| Supabase | **Supabase Cloud** | Already in use, managed database, built-in monitoring |
| Database | **Supabase PostgreSQL** | Integrated with auth, realtime, pgvector |

**Alternatives Considered**:
1. **Full AWS**: More control but higher complexity (ECS, RDS, ALB)
2. **Full Kubernetes**: Overkill for current scale, high ops overhead
3. **Single Platform (Heroku)**: Limited for polyglot stack (Python + Next.js)

---

### ADR-022: CI/CD Pipeline
**Decision**: GitHub Actions with Multi-Environment Strategy

**Pipeline Stages**:
```yaml
1. Lint & Type Check (30s)
2. Unit Tests (1-2min)
3. Integration Tests (2-3min)
4. Build (1-2min)
5. Deploy to Staging (automatic on main)
6. Smoke Tests (30s)
7. Deploy to Production (manual approval)
```

**Alternatives Considered**:
1. **GitLab CI**: Not using GitLab
2. **Jenkins**: Overkill, requires self-hosting
3. **CircleCI**: Good but GitHub Actions is free and integrated

---

### ADR-023: Secrets Management
**Decision**: Platform-Native Secrets + 1Password for Team

| Secret Type | Storage | Access |
|-------------|---------|--------|
| API Keys (prod) | Vercel/Railway Env Vars | Platform UI |
| Database URLs | Supabase Dashboard | Auto-injected |
| Service Account Keys | GitHub Secrets | CI/CD only |
| Team Credentials | 1Password | Human access |
| Encryption Keys | Railway Config Vars | Runtime only |

**Alternatives Considered**:
1. **HashiCorp Vault**: Too complex for current scale
2. **AWS Secrets Manager**: Vendor lock-in
3. **Environment Files**: Insecure for production

---

### ADR-024: Monitoring Strategy
**Decision**: Multi-Layer Observability

| Layer | Tool | Metrics |
|-------|------|---------|
| Uptime | **Better Stack** | HTTP endpoints, API health |
| APM | **Vercel Analytics** | Frontend performance, Core Web Vitals |
| Logs | **Railway Logs** | Backend errors, workflow traces |
| Database | **Supabase Dashboard** | Query performance, RLS violations |
| Workflows | **Temporal Cloud** | Workflow health, activity failures |
| Errors | **Sentry** (optional) | Stack traces, user context |

**Alternatives Considered**:
1. **Datadog**: Too expensive for early stage
2. **Self-hosted Grafana**: High ops overhead
3. **CloudWatch**: AWS lock-in

---

## Infrastructure Design

### Environment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PRODUCTION                           │
├─────────────────────────────────────────────────────────┤
│  Vercel (Frontend)                                      │
│  ├─ orion-ai.vercel.app                                │
│  ├─ Edge Functions (API Routes)                        │
│  └─ CDN + Global Edge Network                          │
├─────────────────────────────────────────────────────────┤
│  Railway (Backend)                                      │
│  ├─ api-prod.railway.app                               │
│  ├─ FastAPI (Connectors, Webhooks)                     │
│  └─ Auto-scaling (2-10 instances)                      │
├─────────────────────────────────────────────────────────┤
│  Temporal Cloud                                         │
│  ├─ namespace: orion-prod                              │
│  ├─ Durable Workflows                                  │
│  └─ 99.99% SLA                                         │
├─────────────────────────────────────────────────────────┤
│  Supabase (Database)                                    │
│  ├─ PostgreSQL 15 + pgvector                           │
│  ├─ Realtime WebSockets                                │
│  └─ Auth (OAuth)                                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    STAGING                              │
├─────────────────────────────────────────────────────────┤
│  Vercel (Preview Deployments)                           │
│  Railway (Staging Service)                              │
│  Temporal Cloud (orion-staging namespace)               │
│  Supabase (Staging Project)                             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   DEVELOPMENT                           │
├─────────────────────────────────────────────────────────┤
│  localhost:3000 (Next.js dev)                           │
│  localhost:8000 (FastAPI dev)                           │
│  Docker Compose (Temporal local)                        │
│  Supabase (Cloud - dev project)                         │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Workstream 1: CI/CD Pipeline (2-3 hours)

**Files to Create**:
```
.github/
├── workflows/
│   ├── ci.yml                    # Main CI pipeline
│   ├── deploy-staging.yml        # Auto-deploy to staging
│   ├── deploy-production.yml     # Manual prod deploy
│   └── security-scan.yml         # Weekly security audit
└── CODEOWNERS                    # Require reviews
```

**CI Pipeline (`ci.yml`)**:
```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Python Lint
        run: |
          pip install ruff
          ruff check .
      - name: TypeScript Lint
        run: |
          cd frontend
          npm ci
          npm run lint

  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Python deps
        run: pip install -r requirements.txt
      - name: Run pytest
        run: pytest connectors/tests/ -v --tb=short

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Node deps
        run: |
          cd frontend
          npm ci
      - name: Type Check
        run: |
          cd frontend
          npx tsc --noEmit

  build:
    needs: [lint, test-backend, test-frontend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Frontend
        run: |
          cd frontend
          npm ci
          npm run build
```

---

### Workstream 2: Environment Configuration (1-2 hours)

**Files to Create**:
```
config/
├── environments/
│   ├── development.env          # Local dev
│   ├── staging.env.example      # Staging template
│   └── production.env.example   # Production template
├── deploy/
│   ├── railway.toml             # Railway config
│   └── vercel.json              # Vercel config
└── docker/
    └── Dockerfile.production    # Production container
```

**Environment Variables Strategy**:

| Variable | Dev | Staging | Prod |
|----------|-----|---------|------|
| `NEXT_PUBLIC_SUPABASE_URL` | Local/Cloud | Staging Project | Production Project |
| `SUPABASE_SERVICE_ROLE_KEY` | GitHub Secret | Railway Secret | Railway Secret |
| `TEMPORAL_ADDRESS` | localhost:7233 | staging.tmprl.cloud | prod.tmprl.cloud |
| `STRIPE_API_KEY` | Test Key | Test Key | Live Key |
| `HUBSPOT_API_KEY` | Sandbox | Sandbox | Production |
| `ENCRYPTION_KEY` | Local Gen | Railway Gen | Railway Gen |

**Vercel Configuration (`vercel.json`)**:
```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/.next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_SUPABASE_URL": "@supabase-url",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@supabase-anon-key",
    "NEXT_PUBLIC_TEMPORAL_API_URL": "@temporal-api-url"
  },
  "rewrites": [
    {
      "source": "/api/backend/:path*",
      "destination": "https://api-prod.railway.app/:path*"
    }
  ]
}
```

**Railway Configuration (`railway.toml`)**:
```toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

---

### Workstream 3: Monitoring & Alerting (2-3 hours)

**Health Check Endpoints**:

Create `api/health.py`:
```python
from fastapi import APIRouter
from typing import Dict, Any
import asyncio

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "orion-api",
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health() -> Dict[str, Any]:
    """Detailed health with dependency checks"""
    checks = {
        "supabase": await check_supabase(),
        "temporal": await check_temporal(),
        "redis": await check_redis(),
    }
    
    all_healthy = all(c["healthy"] for c in checks.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

**Better Stack Configuration**:
```yaml
# monitors.yml
monitors:
  - name: "Orion Frontend"
    url: "https://orion-ai.vercel.app"
    method: "GET"
    interval: 60
    timeout: 10
    
  - name: "Orion API"
    url: "https://api-prod.railway.app/health"
    method: "GET"
    interval: 60
    expected_status: 200
    
  - name: "Temporal Workflows"
    url: "https://api-prod.railway.app/health/temporal"
    method: "GET"
    interval: 300
```

**Vercel Analytics Setup**:
```tsx
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
```

---

### Workstream 4: Security Hardening (2-3 hours)

**Security Checklist**:

| Area | Task | Implementation |
|------|------|----------------|
| **Secrets** | Rotate all keys | Generate new prod keys |
| **HTTPS** | Force SSL | Vercel auto, Railway config |
| **CORS** | Whitelist origins | FastAPI middleware |
| **Rate Limiting** | Add throttling | Vercel Edge, Supabase RLS |
| **Headers** | Security headers | Next.js config |
| **Dependencies** | Audit vulns | `npm audit`, `pip-audit` |
| **Logs** | Sanitize PII | Remove sensitive data |
| **Backups** | Automated snapshots | Supabase daily |

**Security Headers (`next.config.ts`)**:
```typescript
const nextConfig = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin'
          }
        ]
      }
    ];
  }
};
```

**CORS Configuration (`api/main.py`)**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Production CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://orion-ai.vercel.app",
        "https://orion-ai-staging.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

### Workstream 5: Deployment Automation (1-2 hours)

**Deployment Scripts**:

Create `scripts/deploy/`:
```bash
scripts/deploy/
├── deploy-staging.sh       # Deploy to staging
├── deploy-production.sh    # Deploy to production
├── rollback.sh            # Rollback last deployment
└── smoke-test.sh          # Post-deployment tests
```

**Deployment Script (`deploy-production.sh`)**:
```bash
#!/bin/bash
set -e

echo "🚀 Starting Production Deployment..."

# Pre-deployment checks
echo "1️⃣ Running pre-deployment checks..."
./scripts/deploy/smoke-test.sh staging

# Deploy backend
echo "2️⃣ Deploying Backend API..."
railway up --service api-prod --environment production

# Wait for backend health
echo "3️⃣ Waiting for backend health..."
sleep 10
curl -f https://api-prod.railway.app/health || exit 1

# Deploy frontend
echo "4️⃣ Deploying Frontend..."
cd frontend
vercel --prod

# Post-deployment smoke tests
echo "5️⃣ Running smoke tests..."
./scripts/deploy/smoke-test.sh production

echo "✅ Deployment Complete!"
echo "🔗 https://orion-ai.vercel.app"
```

**Smoke Test Script (`smoke-test.sh`)**:
```bash
#!/bin/bash
ENV=$1  # staging or production

if [ "$ENV" = "production" ]; then
  FRONTEND_URL="https://orion-ai.vercel.app"
  API_URL="https://api-prod.railway.app"
else
  FRONTEND_URL="https://orion-ai-staging.vercel.app"
  API_URL="https://api-staging.railway.app"
fi

echo "🧪 Running smoke tests for $ENV..."

# Test 1: Frontend loads
echo "Test 1: Frontend homepage..."
curl -f $FRONTEND_URL || exit 1

# Test 2: API health check
echo "Test 2: API health..."
curl -f $API_URL/health || exit 1

# Test 3: Database connection
echo "Test 3: Database..."
curl -f $API_URL/health/detailed || exit 1

echo "✅ All smoke tests passed!"
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] All Phase 0-5 tests passing
- [ ] Environment variables configured
- [ ] Secrets rotated for production
- [ ] Database migrations applied
- [ ] Backup verification
- [ ] Monitoring dashboards ready

### Deployment Steps
1. [ ] Deploy to Staging
2. [ ] Run smoke tests on Staging
3. [ ] Manual QA on Staging
4. [ ] Create production release tag
5. [ ] Deploy to Production (manual approval)
6. [ ] Run smoke tests on Production
7. [ ] Monitor for 15 minutes
8. [ ] Update status page

### Post-Deployment
- [ ] Verify all services healthy
- [ ] Check monitoring alerts
- [ ] Test critical user flows
- [ ] Notify team of deployment
- [ ] Update documentation
- [ ] Archive deployment logs

---

## Rollback Plan

### Automatic Rollback Triggers
- Health check fails for >2 minutes
- Error rate >5% for >1 minute
- P95 latency >3 seconds for >1 minute

### Manual Rollback Process
```bash
# 1. Identify last good deployment
vercel rollback --yes

# 2. Rollback backend
railway rollback --service api-prod

# 3. Verify health
./scripts/deploy/smoke-test.sh production

# 4. Investigate issue
railway logs --service api-prod --tail 100
```

---

## Cost Estimate

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| Vercel Pro | 1 team | $20 |
| Railway Hobby | API service | $5-20 |
| Temporal Cloud | Starter | $200 |
| Supabase Pro | Database | $25 |
| Better Stack | Free tier | $0 |
| GitHub Actions | 2000 mins/mo | $0 |
| **Total** | | **~$250-270/mo** |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Deployment Time** | <60 seconds | GitHub Actions duration |
| **Uptime** | >99.9% | Better Stack |
| **Error Rate** | <0.1% | Vercel Analytics |
| **Build Success Rate** | >95% | GitHub Actions |
| **Time to Rollback** | <2 minutes | Manual drill |
| **Mean Time to Recovery** | <5 minutes | Incident logs |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Deployment fails | Medium | High | Automated rollback, staging env |
| Service degradation | Medium | High | Health checks, auto-scaling |
| Secret exposure | Low | Critical | GitHub Secrets, rotation policy |
| Database migration failure | Low | Critical | Backup before migration, dry-run |
| Cost overrun | Medium | Medium | Budget alerts, usage monitoring |

---

## Timeline

| Week | Milestones |
|------|------------|
| **Week 1** | • CI/CD pipeline setup<br>• Environment configuration<br>• Deploy to staging |
| **Week 2** | • Monitoring setup<br>• Security hardening<br>• Production deployment |

**Total Duration**: 8-13 hours over 1-2 weeks

---

## Next Steps After Phase 6A

1. **Phase 6B**: Advanced Features (more connectors, LLM mapping)
2. **Phase 6C**: Enterprise Features (multi-tenancy, SSO)
3. **Scaling**: Horizontal scaling, caching, performance optimization
4. **Compliance**: SOC2, GDPR, security audits

---

**Status**: READY FOR BUILD MODE
