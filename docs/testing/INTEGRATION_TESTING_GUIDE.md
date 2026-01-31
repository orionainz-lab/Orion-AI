# Integration Testing Guide - Live Environment

**Phase 7 Option B - Option 1: Complete Live Testing**

---

## Prerequisites

### 1. Environment Configuration

Ensure `.env` file has all required variables:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...

# Redis
REDIS_URL=rediss://default:password@host:6379

# API
API_BASE_URL=http://localhost:8000

# Test credentials
TEST_API_KEY=test-api-key-for-integration

# SSO Providers (for live SSO testing)
AZURE_AD_TENANT_ID=your-tenant-id
AZURE_AD_CLIENT_ID=your-client-id
AZURE_AD_CLIENT_SECRET=your-client-secret
```

### 2. Install Dependencies

```bash
pip install pytest pytest-asyncio httpx locust supabase redis
```

### 3. Database Setup

Ensure all Phase 6C migrations are applied:

```bash
# Check tables exist
psql $DATABASE_URL -c "\dt"

# Should see: organizations, org_members, sso_configurations, etc.
```

---

## Step-by-Step Testing

### Step 1: Environment Health Check

```bash
python scripts/check_test_environment.py
```

**Expected Output:**
```
[PASS] API server is healthy at http://localhost:8000
[PASS] Supabase connected
[PASS] Redis connected

Checks Passed: 3/3
[PASS] Environment ready for integration tests
```

**If Failed:**
- API not running → Start with `uvicorn api.main:app --reload`
- Supabase failed → Check credentials in `.env`
- Redis failed → Check REDIS_URL or start local Redis

---

### Step 2: Run Unit Tests (No API Required)

These test the test infrastructure itself:

```bash
# SSO mock tests
pytest tests/integration/sso/test_azure_ad.py::TestAzureADSSO::test_authorization_url_generation -v

# RBAC logic tests  
pytest tests/integration/rbac/test_viewer_permissions.py::TestPermissionDenied::test_permission_denied_returns_403 -v
```

**Expected:** All pass (tests use mocks, no live API needed)

---

### Step 3: Run Database Integration Tests

These test against live Supabase:

```bash
# Run all RBAC tests (requires Supabase)
pytest tests/integration/rbac/test_viewer_permissions.py -v

# Run SSO provisioning tests
pytest tests/integration/sso/test_azure_ad.py::TestAzureADSSO::test_fresh_user_jit_provisioning -v
```

**Expected:**
- Tests create test organizations
- Tests create test users
- Auto-cleanup after each test

---

### Step 4: Run API Integration Tests

Requires API server running at `http://localhost:8000`.

#### Start API Server

```bash
# Terminal 1: Start API
cd api
uvicorn main:app --reload --port 8000
```

#### Run API Tests

```bash
# Terminal 2: Run tests
pytest tests/integration/ -v --tb=short
```

---

### Step 5: Run Rate Limiting Load Tests

Requires API server running.

```bash
# Run load test (50 users, 10/sec spawn, 60 seconds)
bash scripts/load_tests/run_load_test.sh http://localhost:8000 50 10 60s
```

**Expected Output:**
```
[INFO] Starting load test...
[INFO] Users: 50, Spawn rate: 10/sec
...
Total Requests: 3000
Failed Requests: 500 (rate limited)
Success Rate: 83.3%
```

**Results saved to:**
- `test-results/load-tests/rate-limiting-report.html`
- `test-results/load-tests/rate-limiting_stats.csv`

---

## Test Scenarios

### SSO Testing (Manual + Automated)

#### Automated Tests (Mocked)
```bash
pytest tests/integration/sso/ -v
```

Tests:
- ✅ Authorization URL generation
- ✅ Token parsing
- ✅ JIT provisioning logic
- ✅ Domain restriction
- ✅ Token validation

#### Manual Live Testing

**Prerequisites:**
1. Set up Azure AD test tenant
2. Add OAuth redirect: `http://localhost:3000/api/oauth/azure/callback`
3. Get client credentials

**Steps:**
1. Start frontend: `cd frontend && npm run dev`
2. Navigate to `http://localhost:3000/login`
3. Click "Sign in with Microsoft"
4. Complete Azure AD login
5. Verify redirect back to app
6. Check `org_members` table for new user

---

### RBAC Testing

```bash
# Run all RBAC tests
pytest tests/integration/rbac/ -v -s
```

**Tests:**
- Viewer permissions (read-only)
- Member permissions (own resources)
- Admin permissions (org-wide)
- Owner permissions (billing)
- Role changes
- RLS enforcement

**Verify in Database:**
```sql
-- Check test organizations created
SELECT id, name, slug FROM organizations WHERE slug LIKE 'test-org-%';

-- Check test users
SELECT * FROM org_members WHERE org_id IN (
  SELECT id FROM organizations WHERE slug LIKE 'test-org-%'
);
```

---

### Rate Limiting Testing

#### Quick Test (Manual)

```bash
# Send 100 requests to API
for i in {1..100}; do
  curl -H "Authorization: Bearer test-api-key" \
       http://localhost:8000/api/connectors
done
```

**Expected:** After ~60 requests, get `429 Too Many Requests`

#### Load Test (Automated)

```bash
bash scripts/load_tests/run_load_test.sh http://localhost:8000 100 20 120s
```

**Monitors:**
- Requests per second
- Response times
- Rate limit hits (429 responses)
- Redis counter updates

---

## Troubleshooting

### Tests Fail: "Fixture not found"

**Solution:** Ensure `tests/conftest.py` exists and contains fixtures:
```bash
ls tests/conftest.py
# Should exist
```

### Tests Fail: "ModuleNotFoundError"

**Solution:** Install missing dependencies:
```bash
pip install pytest pytest-asyncio supabase httpx
```

### API Tests Fail: "Connection refused"

**Solution:** Start API server:
```bash
uvicorn api.main:app --reload
```

### Supabase Tests Fail: "Invalid JWT"

**Solution:** Check `SUPABASE_SERVICE_ROLE_KEY` in `.env`:
```bash
echo $SUPABASE_SERVICE_ROLE_KEY
# Should be long JWT string starting with eyJ...
```

### Redis Tests Fail: "Connection timeout"

**Solution:** Start local Redis or verify Upstash URL:
```bash
# Start local Redis
docker run -d -p 6379:6379 redis:7-alpine

# Or verify Upstash connection
redis-cli -u $REDIS_URL ping
# Should return: PONG
```

### Rate Limiting Not Working

**Check Redis counters:**
```bash
redis-cli -u $REDIS_URL
> KEYS ratelimit:*
> GET ratelimit:user:test-api-key:minute
```

---

## Test Reports

### Integration Test Report

Generated at: `test-results/integration-test-report.html`

Open in browser to see:
- Total tests run
- Pass/fail counts
- Individual test results
- Failure details

### Load Test Report

Generated at: `test-results/load-tests/rate-limiting-report.html`

Includes:
- Request distribution
- Response time charts
- Failure percentage
- Requests per second

---

## Continuous Integration

### GitHub Actions (Optional)

Create `.github/workflows/integration-tests.yml`:

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Run integration tests
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          REDIS_URL: redis://localhost:6379
        run: |
          python scripts/run_integration_tests.py
```

---

## Next Steps

### After All Tests Pass

1. **Deploy to Staging**
   ```bash
   vercel deploy --env-file .env.staging
   ```

2. **Run Tests Against Staging**
   ```bash
   API_BASE_URL=https://staging.orion-ai.vercel.app \
     python scripts/run_integration_tests.py
   ```

3. **Set Up Real SSO**
   - Configure production OAuth apps
   - Test with real user accounts
   - Verify JIT provisioning

4. **Load Test Production**
   ```bash
   bash scripts/load_tests/run_load_test.sh \
     https://api.orion-ai.com 500 50 300s
   ```

---

**Ready for Live Testing!**

Run: `python scripts/check_test_environment.py` to begin.
