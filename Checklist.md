# Phase 6C: Enterprise Master Data Checklist

**Status**: 🟢 **READY TO BUILD**
**Goal**: Hand this file to the AI/Developer to generate the integration code.

---

# PART 1: AUTHENTICATION PROVIDERS

## 1. Azure AD (Microsoft Entra ID) - OIDC (✅ COMPLETE)
**Implementation Priority**: Primary

### Credentials
- **Tenant ID**: `22116407-6817-4c85-96ce-1b6d4e631844`
- **Client ID**: `de01844a-115d-4789-8b5f-eab412c6089e`
- **Client Secret**: `ISD8Q~dypu1jXm33lD71uTerp5fWAWHqGhvmCahN`
- **Issuer URL**: `https://login.microsoftonline.com/22116407-6817-4c85-96ce-1b6d4e631844/v2.0`

### Configuration
- **Redirect URI**: `https://orion-ai.vercel.app/api/auth/callback/azure-ad`
- **Front-channel logout URL**: `https://orion-ai.vercel.app/api/auth/signout`
- **API Permissions**: `User.Read`, `openid`, `profile`, `email`

---

## 2. Google Workspace - OIDC (✅ COMPLETE)
**Implementation Priority**: Secondary

### Credentials
- **Client ID**: `27144313651-o4jt3m20kg43f96g35phgk7v224tkqqm.apps.googleusercontent.com`
- **Client Secret**: `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`

### Configuration
- **Authorized Redirect URI**: `https://orion-ai.vercel.app/api/auth/callback/google`
- **Authorized JavaScript Origin**: `https://orion-ai.vercel.app`

---

## 3. Auth0 - OIDC (✅ COMPLETE)
**Implementation Priority**: Tertiary

### Credentials
- **Domain**: `dev-46h61t2r8joe5aoc.au.auth0.com`
- **Client ID**: `mC1CAFbMsAcat0Uqnyr5NV5ljHOvQjQQ`
- **Client Secret**: `GmdY_3ZDiogh8vHC2zBsn9tf_7CDxGpI0W0tgiAV8Wv0tVdTnz606qxKuDptOACf`

### Configuration
- **Allowed Callback URLs**: `https://orion-ai.vercel.app/api/auth/callback/auth0`
- **Allowed Logout URLs**: `https://orion-ai.vercel.app`

---

## 4. OneLogin - SAML 2.0 (✅ COMPLETE)
**Implementation Priority**: Quaternary

### Credentials
- **Issuer URL**: `https://app.onelogin.com/saml/metadata/a156d5fe-9b16-4613-a498-ae8dcacc33a3`
- **SAML 2.0 Endpoint**: `https://orion-ai.onelogin.com/trust/saml2/http-post/sso/a156d5fe-9b16-4613-a498-ae8dcacc33a3`
- **SLO Endpoint**: `https://orion-ai.onelogin.com/trust/saml2/http-redirect/slo/4357754`
- **X.509 Certificate**: -----BEGIN CERTIFICATE----- MIID3zCCAsegAwIBAgIUcMgJSu/6RI7im9Pv5ESNuH8R+xQwDQYJKoZIhvcNAQEF BQAwRjERMA8GA1UECgwIT3Jpb24gQUkxFTATBgNVBAsMDE9uZUxvZ2luIElkUDEa MBgGA1UEAwwRT25lTG9naW4gQWNjb3VudCAwHhcNMjYwMTMxMDg0MzUyWhcNMzEw MTMxMDg0MzUyWjBGMREwDwYDVQQKDAhPcmlvbiBBSTEVMBMGA1UECwwMT25lTG9n aW4gSWRQMRowGAYDVQQDDBFPbmVMb2dpbiBBY2NvdW50IDCCASIwDQYJKoZIhvcN AQEBBQADggEPADCCAQoCggEBAL2oBJyLy9udfpI8aYWBQIndbdlPZQ4uZrNjHK0w wus6rbVImZtkStmSapL9jIfFxS5/d1aMlAvw25FzdSKPtIcmrqRRE4TTosmmEtOB jXncfT2gHgN3Cl7aXgnRRId7AfRjz67Pw5FOhlcoRUfE8NxKQlqnrESBa4Qx1XFC h7g8x0T86Pqfp9D69nX5SIyCX1aOeVU+BLf5EeuIiHvyr9LZPPO70Bj+QgzB9/4d B/qet+7D4PEBXOjxvQl6z0voVCjTQgC4mmu0foeU+F8aybezhu6xzuxfX3AzDv30 KFXZru2WNv4acJU+/EboAGLGmJjGrfUPx/G5QFfPzr7TudUCAwEAAaOBxDCBwTAM BgNVHRMBAf8EAjAAMB0GA1UdDgQWBBSQWdiyvxjQRndtCuqpIGyAuFtH1TCBgQYD VR0jBHoweIAUkFnYsr8Y0EZ3bQrqqSBsgLhbR9WhSqRIMEYxETAPBgNVBAoMCE9y aW9uIEFJMRUwEwYDVQQLDAxPbmVMb2dpbiBJZFAxGjAYBgNVBAMMEU9uZUxvZ2lu IEFjY291bnQgghRwyAlK7/pEjuKb0+/kRI24fxH7FDAOBgNVHQ8BAf8EBAMCB4Aw DQYJKoZIhvcNAQEFBQADggEBAGcBx+Z052mwglu6JT78YtL6XKb/XzVK3chmQVai l9uR/4WY45h0VxGPCLnzEpwCzbPgRMXaS6vXEiI8ACjExrRvoOIsIttjWZZUH6RY jvIh3likLNpwnwULbclvlm63VTFeaiwqHplmddcaJdCr1DmmGG72z++PAN6eM58j gXexsyV+9lzr9Sz2Ybqb06c5XnFQvqYPt611WGER7Qc3W2tKvEL/fF5mRuByhBqF fHQ29uukRHyp2VmiOPGL2gGD4bSC8fcJAAGZMn0DGZGh7G4FGF3GBE4/KVYrk8Q5 NDEGw918F7DnOyoGkf/jgPZyZhSNwCFxaLQnjpVvCogxz4s= -----END CERTIFICATE-----

### Configuration
- **ACS URL**: `https://orion-ai.vercel.app/api/auth/callback/onelogin`
- **Audience**: `https://orion-ai.vercel.app`
- **Validator**: `^https:\/\/orion-ai\.vercel\.app\/api\/auth\/callback\/onelogin$`

---

## 5. Okta - SAML 2.0 (⏳ LATER)
**Implementation Priority**: Post-Launch

*Notes: Postponed. Will implement after primary providers are stable.*

---

# PART 2: RBAC CONFIGURATION (✅ LOCKED)

## 1. Role Definitions
**Decision**: Use Default Standard Roles
* **Super Admin**: Full System Access
* **Org Admin**: Manage Billing, Invites, Settings
* **Team Lead**: Manage Team Projects
* **Member**: Manage Own Resources
* **Viewer**: Read Only

## 2. Granularity
**Decision**: Extended
* **Actions**: `create`, `read`, `update`, `delete`, `export`, `admin`

## 3. Structure
**Decision**: Teams Enabled
* **Hierarchy**: Organization -> Teams -> Members
* **Scopes**: `openid`, `profile`, `email`, `org`, `team`

## 4. Permission Matrix (Default)
| Resource | Org Admin | Team Lead | Member | Viewer |
| :--- | :--- | :--- | :--- | :--- |
| **Billing** | Full Access | No Access | No Access | No Access |
| **Connectors** | Full Access | Edit Team's | Edit Own | Read Only |
| **API Keys** | Create/Revoke | Create/Revoke | No Access | No Access |
| **Settings** | Full Access | Read Only | Read Only | No Access |
| **Audit Logs**| Read/Export | Read Only | No Access | No Access |

---

# PART 3: INFRASTRUCTURE (✅ COMPLETE)

## Redis (Rate Limiting)
- **Provider**: Upstash
- **Connection URL**: `rediss://default:ASYFAAImcDI2ZTI5Y2RkZTEzZGY0ZmFiOTNiNjg1ZDVkYzY0MmRlOXAyOTczMw@many-eagle-9733.upstash.io:6379`

## Storage (White Labeling)
- **Provider**: Supabase Storage
- **Bucket**: `brand-assets`