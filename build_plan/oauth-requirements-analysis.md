# OAuth vs API Key Requirements: Customer Software Integration

**Date**: 2026-01-31  
**Purpose**: Identify which integrations require OAuth setup

---

## Quick Answer

**OAuth Required (You need free developer app):**
- Salesforce
- QuickBooks
- Slack
- Google Workspace
- Microsoft 365

**API Key Only (Customer pastes their key):**
- HubSpot
- Stripe
- Most simple APIs

---

## 1. OAUTH-REQUIRED INTEGRATIONS

These require you to register a **free developer app** once to enable the "Connect" button.

### Salesforce (MUST USE OAUTH)

| What You Need | Cost | Where | Time |
|---------------|------|-------|------|
| Connected App | Free | developer.salesforce.com | 10 min |

**Why OAuth Only:**
- Salesforce deprecated password-based API access
- OAuth is the only supported method for new apps
- Customer must authorize via OAuth flow

**Setup Steps:**
1. Create Salesforce Developer account (free)
2. Create "Connected App" in Setup
3. Get Client ID + Client Secret
4. Configure OAuth callback URL: `https://orion-ai.vercel.app/api/oauth/salesforce/callback`

**Your Code Already Uses OAuth:**
```python
# connectors/adapters/salesforce/adapter.py
def _get_auth_headers(self) -> dict[str, str]:
    access_token = self.credentials.get("access_token", "")
    return {"Authorization": f"Bearer {access_token}"}
```

---

### QuickBooks (MUST USE OAUTH)

| What You Need | Cost | Where | Time |
|---------------|------|-------|------|
| Intuit App | Free | developer.intuit.com | 10 min |

**Why OAuth Only:**
- QuickBooks Online only supports OAuth 2.0
- No API key option available
- Tokens expire every 1 hour (auto-refresh implemented)

**Setup Steps:**
1. Create Intuit Developer account (free)
2. Create "App" for QuickBooks Online
3. Get Client ID + Client Secret
4. Configure redirect URI: `https://orion-ai.vercel.app/api/oauth/quickbooks/callback`

**Your Code Handles Token Refresh:**
```python
# connectors/adapters/quickbooks/adapter.py
async def _refresh_token_if_needed(self):
    # Auto-refreshes when token expires
    # QuickBooks tokens expire after 1 hour
```

---

### Slack (MUST USE OAUTH)

| What You Need | Cost | Where | Time |
|---------------|------|-------|------|
| Slack App | Free | api.slack.com/apps | 5 min |

**Why OAuth Only:**
- Slack requires OAuth for workspace access
- Bot tokens are issued via OAuth
- No alternative API key method

**Setup Steps:**
1. Go to api.slack.com/apps
2. Create "New App"
3. Add Bot Token Scopes (chat:write, channels:read, users:read)
4. Configure OAuth Redirect URL: `https://orion-ai.vercel.app/api/oauth/slack/callback`
5. Install app to workspace

**Your Code Uses Bot Token:**
```python
# connectors/adapters/slack/adapter.py
def _get_auth_headers(self) -> dict[str, str]:
    bot_token = self.credentials.get("bot_token", "")
    return {"Authorization": f"Bearer {bot_token}"}
```

---

### Google Workspace (OAUTH RECOMMENDED)

| What You Need | Cost | Where | Time |
|---------------|------|-------|------|
| Google Cloud Project | Free | console.cloud.google.com | 10 min |

**Why OAuth:**
- Access Gmail, Drive, Calendar, Contacts
- API keys only work for public data
- OAuth required for user-specific data

**Setup Steps:**
1. Create Google Cloud Project (free)
2. Enable APIs (Gmail, Drive, Calendar)
3. Create OAuth 2.0 Client
4. Add authorized redirect: `https://orion-ai.vercel.app/api/oauth/google/callback`

**Scopes Needed:**
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/drive.readonly`
- `https://www.googleapis.com/auth/calendar`

---

### Microsoft 365 (OAUTH RECOMMENDED)

| What You Need | Cost | Where | Time |
|---------------|------|-------|------|
| Azure AD App | Free | portal.azure.com | 10 min |

**Why OAuth:**
- Access Outlook, OneDrive, Teams
- OAuth required for user data
- API keys not sufficient for user content

**Setup Steps:**
1. Go to Azure Portal → App Registrations
2. Create new registration
3. Add redirect URI: `https://orion-ai.vercel.app/api/oauth/microsoft/callback`
4. Configure API Permissions (Mail.Read, Files.Read)

---

## 2. API KEY INTEGRATIONS

These DON'T require OAuth setup. Customer just pastes their API key.

### HubSpot (API KEY SUPPORTED)

| What Customer Needs | How They Get It |
|---------------------|-----------------|
| Private App Token | HubSpot Settings → Private Apps |

**Why API Key Works:**
- HubSpot supports both OAuth and API keys
- Private App tokens = permanent API keys
- Simpler for customers to set up

**Your Code:**
```python
# connectors/adapters/hubspot/adapter.py
def _get_auth_headers(self) -> dict[str, str]:
    api_key = self.credentials.get("api_key", "")
    return {"Authorization": f"Bearer {api_key}"}
```

**Customer Setup:**
1. Go to HubSpot Settings
2. Integrations → Private Apps
3. Create private app
4. Copy API token
5. Paste into Orion

---

### Stripe (API KEY ONLY)

| What Customer Needs | How They Get It |
|---------------------|-----------------|
| Secret Key | Stripe Dashboard → Developers → API Keys |

**Why API Key:**
- Stripe provides permanent secret keys
- No OAuth needed for backend integrations
- Simpler authentication model

**Your Code:**
```python
# connectors/adapters/stripe/adapter.py
def _get_auth_headers(self) -> dict[str, str]:
    api_key = self.credentials.get("api_key", "")
    return {"Authorization": f"Bearer {api_key}"}
```

---

## 3. COMPARISON TABLE

| Service | Auth Method | You Need | Customer Needs | Complexity |
|---------|-------------|----------|----------------|------------|
| **Salesforce** | OAuth only | Developer account + Connected App | Salesforce login | High |
| **QuickBooks** | OAuth only | Developer account + App | QuickBooks subscription | High |
| **Slack** | OAuth only | Slack App | Workspace admin access | Medium |
| **Google** | OAuth preferred | Cloud Project + OAuth Client | Google account | Medium |
| **Microsoft** | OAuth preferred | Azure AD App | Microsoft account | Medium |
| **HubSpot** | OAuth or API Key | Nothing (if API key) | Private App token | Low |
| **Stripe** | API Key | Nothing | Stripe account | Low |

---

## 4. OAUTH SETUP SUMMARY

### What You Need to Create (One-Time)

| Platform | Resource | Cost | URL |
|----------|----------|------|-----|
| Salesforce | Connected App | Free | developer.salesforce.com |
| QuickBooks | Intuit App | Free | developer.intuit.com |
| Slack | Slack App | Free | api.slack.com/apps |
| Google | Cloud Project + OAuth Client | Free | console.cloud.google.com |
| Microsoft | Azure AD App Registration | Free | portal.azure.com |

**Total Cost**: $0

---

## 5. OAUTH FLOW ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    CUSTOMER                                  │
│  1. Clicks "Connect Salesforce" in Orion                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    ORION (Your App)                          │
│  2. Redirects to:                                            │
│     https://login.salesforce.com/services/oauth2/authorize  │
│     ?client_id=YOUR_CLIENT_ID                                │
│     &redirect_uri=https://orion-ai.vercel.app/oauth/callback│
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    SALESFORCE                                │
│  3. Customer logs in (on Salesforce page, not yours)        │
│  4. Customer approves access                                 │
│  5. Salesforce redirects back to YOUR callback with code:   │
│     https://orion-ai.vercel.app/oauth/callback?code=ABC123  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    ORION (Your App)                          │
│  6. Exchanges code for access_token (backend call)          │
│  7. Stores access_token + refresh_token in Supabase         │
│  8. Uses access_token for all API calls                     │
└─────────────────────────────────────────────────────────────┘
```

**Key Points:**
- Customer NEVER gives you their password
- Salesforce (or other service) confirms the customer owns the account
- You get a token that expires (QuickBooks: 1 hour, Salesforce: varies)
- Your code auto-refreshes tokens when they expire

---

## 6. IMPLEMENTATION STATUS

### Already Implemented in Your Code

| Feature | Status | File |
|---------|--------|------|
| Salesforce OAuth handling | ✅ | `connectors/adapters/salesforce/adapter.py` |
| QuickBooks token refresh | ✅ | `connectors/adapters/quickbooks/adapter.py` |
| Slack bot token | ✅ | `connectors/adapters/slack/adapter.py` |
| HubSpot API key | ✅ | `connectors/adapters/hubspot/adapter.py` |
| Stripe API key | ✅ | `connectors/adapters/stripe/adapter.py` |

### What's Missing (OAuth Callback Endpoints)

You need to create OAuth callback routes in your API:

```python
# api/oauth/routes.py (TO CREATE)

@router.get("/oauth/salesforce/callback")
async def salesforce_callback(code: str, state: str):
    # 1. Exchange code for access_token
    # 2. Store in Supabase credentials table
    # 3. Redirect user to success page
    pass

@router.get("/oauth/quickbooks/callback")
async def quickbooks_callback(code: str, realmId: str):
    # Similar flow
    pass

@router.get("/oauth/slack/callback")
async def slack_callback(code: str):
    # Similar flow
    pass
```

---

## 7. DEVELOPER ACCOUNT CHECKLIST

### To Enable All OAuth Connectors

- [ ] **Salesforce Developer Account**
  - URL: developer.salesforce.com
  - Time: 10 minutes
  - Create Connected App
  - Get Client ID + Secret

- [ ] **Intuit Developer Account**
  - URL: developer.intuit.com
  - Time: 10 minutes
  - Create QuickBooks Online App
  - Get Client ID + Secret

- [ ] **Slack App**
  - URL: api.slack.com/apps
  - Time: 5 minutes
  - Create app, add bot scopes
  - Get Client ID + Secret

- [ ] **Google Cloud Project** (Optional)
  - URL: console.cloud.google.com
  - Time: 10 minutes
  - Enable APIs, create OAuth client

- [ ] **Azure AD App** (Optional)
  - URL: portal.azure.com
  - Time: 10 minutes
  - Register app, configure permissions

---

## 8. CUSTOMER EXPERIENCE COMPARISON

### OAuth Flow (Salesforce, QuickBooks, Slack)

```
1. Customer clicks "Connect Salesforce"
2. Popup opens to Salesforce login
3. Customer logs in (on Salesforce's page)
4. "Allow Orion to access your data?" → Approve
5. Popup closes, connection shows as "Connected"
```

**Pros:** Secure, no password sharing  
**Cons:** Requires OAuth callback setup

### API Key Flow (HubSpot, Stripe)

```
1. Customer clicks "Connect HubSpot"
2. Modal opens: "Paste your HubSpot API key"
3. Customer goes to HubSpot → gets API key → pastes
4. Click "Connect" → Done
```

**Pros:** Simple, no OAuth setup needed  
**Cons:** Customer must manually get API key

---

## Bottom Line

### OAuth Required (5 services):
1. **Salesforce** - No choice, OAuth only
2. **QuickBooks** - No choice, OAuth only
3. **Slack** - No choice, OAuth only
4. **Google** - OAuth for user data (Gmail, Drive)
5. **Microsoft** - OAuth for user data (Outlook, OneDrive)

### API Key Works (2 services):
1. **HubSpot** - Simpler for customers
2. **Stripe** - Standard API key model

**Total OAuth Setup Time**: ~45 minutes (all 5 services)  
**Total Cost**: $0 (all free developer accounts)

---

**Next Steps:**
1. Create free developer accounts for OAuth services
2. Implement OAuth callback endpoints in your API
3. Test OAuth flows for each service
4. Document setup guide for customers
