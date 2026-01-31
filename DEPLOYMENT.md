# Phase 6A Deployment Guide

**Last Updated**: 2026-01-31  
**Version**: 1.0.0  
**Environment**: Production Ready

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Initial Deployment](#initial-deployment)
4. [Deployment Process](#deployment-process)
5. [Monitoring](#monitoring)
6. [Rollback Procedures](#rollback-procedures)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

| Tool | Version | Installation |
|------|---------|--------------|
| Git | 2.40+ | https://git-scm.com/ |
| Node.js | 22+ | https://nodejs.org/ |
| Python | 3.12+ | https://python.org/ |
| Vercel CLI | Latest | `npm install -g vercel` |
| Railway CLI | Latest | `npm install -g @railway/cli` |
| jq | Latest | https://jqlang.github.io/jq/ |

### Required Accounts

- [ ] GitHub account with repo access
- [ ] Vercel account (team plan recommended)
- [ ] Railway account
- [ ] Temporal Cloud account
- [ ] Supabase account (Pro plan for production)
- [ ] Better Stack account (optional, for monitoring)

---

## Environment Setup

### 1. GitHub Secrets

Navigate to repository Settings → Secrets and variables → Actions

**Required Secrets**:

```
VERCEL_TOKEN                    # Vercel deployment token
RAILWAY_TOKEN_STAGING           # Railway staging token
RAILWAY_TOKEN_PRODUCTION        # Railway production token
NEXT_PUBLIC_SUPABASE_URL        # Supabase project URL
NEXT_PUBLIC_SUPABASE_ANON_KEY   # Supabase anon key
```

### 2. Railway Environment Variables

#### Staging Environment

```bash
# Set via Railway Dashboard or CLI
railway variables set ENVIRONMENT=staging
railway variables set NEXT_PUBLIC_SUPABASE_URL=[staging-url]
railway variables set SUPABASE_SERVICE_ROLE_KEY=[staging-key]
railway variables set TEMPORAL_ADDRESS=staging.tmprl.cloud:7233
railway variables set ENCRYPTION_KEY=[generate-new-key]
railway variables set STRIPE_API_KEY=[test-key]
railway variables set HUBSPOT_API_KEY=[sandbox-key]
```

#### Production Environment

```bash
# Set via Railway Dashboard or CLI
railway variables set ENVIRONMENT=production
railway variables set NEXT_PUBLIC_SUPABASE_URL=[prod-url]
railway variables set SUPABASE_SERVICE_ROLE_KEY=[prod-key]
railway variables set TEMPORAL_ADDRESS=prod.tmprl.cloud:7233
railway variables set ENCRYPTION_KEY=[generate-new-key]
railway variables set STRIPE_API_KEY=[live-key]
railway variables set HUBSPOT_API_KEY=[prod-key]
```

### 3. Vercel Environment Variables

Set via Vercel Dashboard → Project Settings → Environment Variables

**For Production**:
- `NEXT_PUBLIC_SUPABASE_URL` → Production Supabase URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` → Production Anon Key

**For Preview (Staging)**:
- `NEXT_PUBLIC_SUPABASE_URL` → Staging Supabase URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` → Staging Anon Key

---

## Initial Deployment

### Step 1: Prepare Repository

```bash
# Clone repository
git clone https://github.com/your-org/orion-ai.git
cd orion-ai

# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Verify build
cd frontend && npm run build && cd ..
pytest connectors/tests/ -v
```

### Step 2: Deploy to Staging

```bash
# Run staging deployment
./scripts/deploy/deploy-staging.sh
```

This script will:
1. Check for uncommitted changes
2. Deploy backend to Railway staging
3. Deploy frontend to Vercel preview
4. Run smoke tests
5. Report deployment status

### Step 3: Test Staging

Visit https://orion-ai-staging.vercel.app and verify:

- [ ] Homepage loads
- [ ] Login with OAuth works
- [ ] Dashboard displays stats
- [ ] Matrix Grid loads data
- [ ] Approve/Reject actions work
- [ ] Realtime updates function

### Step 4: Deploy to Production

```bash
# Create release tag
git tag -a v1.0.0 -m "Production release 1.0.0"
git push origin v1.0.0

# Deploy to production
./scripts/deploy/deploy-production.sh
```

Or use GitHub Actions:
1. Go to Actions tab
2. Select "Deploy to Production"
3. Click "Run workflow"
4. Enter version tag (e.g., v1.0.0)
5. Confirm deployment

---

## Deployment Process

### Automated CI/CD (Recommended)

#### On Every Push to `main`:
1. Linting (Python + TypeScript)
2. Unit tests
3. Build verification
4. Security scan
5. **Auto-deploy to Staging**

#### For Production:
1. Manual trigger via GitHub Actions
2. Pre-deployment checks
3. Staging health verification
4. Backend deployment
5. Frontend deployment
6. Smoke tests
7. 2-minute monitoring
8. Success/rollback

### Manual Deployment

#### Staging:
```bash
./scripts/deploy/deploy-staging.sh
```

#### Production:
```bash
./scripts/deploy/deploy-production.sh
```

---

## Monitoring

### Health Checks

```bash
# Basic health
curl https://api-prod.railway.app/health

# Detailed health with dependencies
curl https://api-prod.railway.app/health/detailed | jq

# Readiness probe
curl https://api-prod.railway.app/health/readiness

# Liveness probe
curl https://api-prod.railway.app/health/liveness
```

### Dashboards

| Service | URL | Purpose |
|---------|-----|---------|
| Vercel Analytics | https://vercel.com/dashboard/analytics | Frontend performance |
| Railway Dashboard | https://railway.app/dashboard | Backend logs & metrics |
| Temporal Cloud | https://cloud.temporal.io | Workflow health |
| Supabase Dashboard | https://supabase.com/dashboard | Database metrics |
| Better Stack | https://betterstack.com | Uptime monitoring |

### Logs

```bash
# Railway backend logs
railway logs --service api-prod --tail 100

# Vercel frontend logs
vercel logs orion-ai --follow

# GitHub Actions logs
# Visit: https://github.com/[your-org]/orion-ai/actions
```

---

## Rollback Procedures

### Automatic Rollback

Deployment will automatically roll back if:
- Health checks fail
- Smoke tests fail
- Error rate exceeds threshold

### Manual Rollback

#### Roll back everything:
```bash
./scripts/deploy/rollback.sh all
```

#### Roll back frontend only:
```bash
./scripts/deploy/rollback.sh frontend
```

#### Roll back backend only:
```bash
./scripts/deploy/rollback.sh backend
```

### Restore from Backup Tag

```bash
# List backup tags
git tag -l "production-backup-*"

# Checkout specific backup
git checkout production-backup-20260131-143022

# Deploy from backup
./scripts/deploy/deploy-production.sh
```

---

## Troubleshooting

### Issue: Backend Health Check Fails

**Symptoms**:
- `/health` endpoint returns 500 or times out
- Railway logs show connection errors

**Solutions**:
1. Check environment variables in Railway
2. Verify Supabase credentials
3. Check Temporal connection
4. Review Railway logs for stack traces

```bash
railway logs --service api-prod --tail 200
```

### Issue: Frontend Build Fails

**Symptoms**:
- Vercel deployment fails
- TypeScript errors

**Solutions**:
1. Verify all environment variables in Vercel
2. Check for TypeScript errors locally:
   ```bash
   cd frontend
   npx tsc --noEmit
   ```
3. Verify dependencies:
   ```bash
   cd frontend
   npm ci
   npm run build
   ```

### Issue: Smoke Tests Fail

**Symptoms**:
- Deployment completes but smoke tests fail
- Rollback triggered

**Solutions**:
1. Run smoke tests manually:
   ```bash
   ./scripts/deploy/smoke-test.sh production
   ```
2. Check specific endpoint:
   ```bash
   curl -v https://orion-ai.vercel.app
   curl -v https://api-prod.railway.app/health
   ```
3. Verify CORS configuration
4. Check security headers

### Issue: Database Connection Errors

**Symptoms**:
- "Supabase: unhealthy" in detailed health check
- 500 errors on API endpoints

**Solutions**:
1. Verify Supabase project is active
2. Check service role key is correct
3. Verify RLS policies allow access
4. Check Supabase dashboard for issues

### Issue: Temporal Connection Fails

**Symptoms**:
- "Temporal: unhealthy" in health check
- Workflows fail to start

**Solutions**:
1. Verify Temporal Cloud namespace
2. Check TEMPORAL_ADDRESS is correct
3. Verify API key/credentials
4. Check Temporal Cloud dashboard

---

## Performance Tuning

### Railway Scaling

```bash
# Scale to 2 instances
railway service scale --instances 2

# Set memory limit
railway service scale --memory 2048
```

### Vercel Optimization

- Enable Edge Functions for API routes
- Use Image Optimization
- Enable Incremental Static Regeneration
- Configure CDN caching headers

---

## Security Checklist

Before deploying to production:

- [ ] All secrets rotated from development
- [ ] HTTPS enforced (automatic on Vercel/Railway)
- [ ] CORS properly configured
- [ ] Security headers enabled
- [ ] Rate limiting configured
- [ ] Database RLS policies active
- [ ] Service role key secured
- [ ] No sensitive data in logs
- [ ] Dependency vulnerabilities patched
- [ ] GitHub security scanning enabled

---

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing locally
- [ ] Staging deployment successful
- [ ] Manual testing complete
- [ ] No critical bugs in issue tracker
- [ ] Database migrations prepared
- [ ] Team notified of deployment window
- [ ] Backup tag created

### During Deployment
- [ ] Monitor deployment progress
- [ ] Watch logs for errors
- [ ] Check health endpoints
- [ ] Run smoke tests
- [ ] Verify critical user flows

### Post-Deployment
- [ ] All health checks green
- [ ] Monitoring dashboards checked
- [ ] Error rates normal
- [ ] Performance metrics acceptable
- [ ] Team notified of completion
- [ ] Documentation updated

---

## Support

For deployment issues:
1. Check this guide first
2. Review logs (Railway, Vercel, GitHub Actions)
3. Contact DevOps team
4. Create incident ticket

**Emergency Contact**: [Your on-call contact]

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-31
