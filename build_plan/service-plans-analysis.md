# VAN Analysis: Service Plans & Pricing Guide

**Date**: 2026-01-31  
**Purpose**: Identify all integrated services and their required plans

---

## Executive Summary

| Category | Service | Current Plan | Required Action | Monthly Cost |
|----------|---------|--------------|-----------------|--------------|
| **AI (Required)** | Anthropic | No credits | Add credits | $5-50+ |
| **AI (Optional)** | OpenAI | Quota exceeded | Add credits | $5-20 |
| **Database** | Supabase | Free | Upgrade when ready | $0-25 |
| **Cache** | Upstash Redis | Free tier | None | $0 |
| **Hosting** | Vercel | Free | Upgrade for production | $0-20 |
| **Monitoring** | Better Stack | Free | None | $0 |
| **Workflow** | Temporal | Self-hosted | None | $0 |
| **SSO** | Auth0/Azure/Google | Free tiers | None | $0 |

**Total Minimum to Start**: ~$10/month (Anthropic + Supabase Free)  
**Total for Production**: ~$75-150/month

---

## 1. AI SERVICES (Core Features)

### Anthropic (Claude) - REQUIRED

**Purpose**: LangGraph code generation, schema mapping, connector builder

| Plan | Price | Tokens/Month | Recommendation |
|------|-------|--------------|----------------|
| Pay-as-you-go | $0.003/1K input, $0.015/1K output | Unlimited | **Start here** |
| Build Plan | $5/month minimum | Prepaid credits | Good for testing |

**Current Status**: ⚠️ Zero credits  
**Action Required**: Add $5-20 credits to start

**Billing URL**: https://console.anthropic.com/settings/billing

**Estimated Usage**:
- Per code generation: ~$0.02-0.05
- Per schema mapping: ~$0.01-0.03
- 100 operations/day: ~$60-150/month

---

### OpenAI - OPTIONAL

**Purpose**: Embeddings for RAG (text-embedding-3-small)

| Plan | Price | Tokens/Month | Recommendation |
|------|-------|--------------|----------------|
| Pay-as-you-go | $0.02/1M tokens | Unlimited | If you want faster embeddings |
| Free tier | $0 | None | N/A |

**Current Status**: ⚠️ Quota exceeded  
**Fallback**: Local sentence-transformers (already working, just slower)

**Action Required**: Optional - add $5-10 credits OR use local fallback

**Billing URL**: https://platform.openai.com/settings/organization/billing

**Estimated Usage**:
- Per embedding: ~$0.0001
- 10,000 embeddings/month: ~$1

---

## 2. DATABASE & STORAGE

### Supabase - REQUIRED

**Purpose**: PostgreSQL database, authentication, storage, real-time

| Plan | Price | Features | Recommendation |
|------|-------|----------|----------------|
| **Free** | $0/month | 500MB DB, 1GB storage, 50k MAU | **Current - Good for dev** |
| Pro | $25/month | 8GB DB, 100GB storage, no pause | Production |
| Team | $599/month | 100GB DB, SOC2, SSO | Enterprise |

**Current Status**: ✅ Free tier active  
**Action Required**: None for development. Upgrade to Pro ($25/mo) for production.

**Your Project**: https://supabase.com/dashboard/project/bdvebjnxpsdhinpgvkgo

**Free Tier Limits**:
- Database: 500MB (currently using ~10MB)
- Storage: 1GB (brand-assets bucket)
- Monthly Active Users: 50,000
- Pauses after 1 week of inactivity

---

### Upstash Redis - REQUIRED

**Purpose**: Rate limiting, caching, session storage

| Plan | Price | Features | Recommendation |
|------|-------|----------|----------------|
| **Free** | $0/month | 10,000 commands/day | **Current - OK for dev** |
| Pay-as-you-go | $0.2/100k commands | Unlimited | Production |
| Pro | $120/month | Dedicated, low latency | Enterprise |

**Current Status**: ✅ Free tier active  
**Action Required**: None. Free tier covers development and light production.

**Your Instance**: many-eagle-9733.upstash.io

---

## 3. HOSTING & DEPLOYMENT

### Vercel - REQUIRED

**Purpose**: Frontend hosting, serverless functions

| Plan | Price | Features | Recommendation |
|------|-------|----------|----------------|
| **Hobby** | $0/month | Personal projects, limited | **Current** |
| Pro | $20/month | Team, analytics, more builds | Production |
| Enterprise | Custom | SSO, SLAs | Enterprise |

**Current Status**: ✅ Hobby tier assumed  
**Action Required**: Upgrade to Pro ($20/mo) for production

**Your Domain**: orion-ai.vercel.app

---

### Temporal.io - SELF-HOSTED

**Purpose**: Durable workflow engine (crash recovery)

| Plan | Price | Features | Recommendation |
|------|-------|----------|----------------|
| **Self-hosted** | $0 | Full features, you manage | **Current** |
| Cloud Starter | $200/month | Managed, 1M actions | Production |
| Cloud Pro | Custom | SLAs, support | Enterprise |

**Current Status**: ✅ Self-hosted (localhost:7233)  
**Action Required**: None for development. Consider Cloud for production reliability.

---

## 4. MONITORING & OBSERVABILITY

### Better Stack - CONFIGURED

**Purpose**: Uptime monitoring, incident management

| Plan | Price | Features | Recommendation |
|------|-------|----------|----------------|
| **Free** | $0/month | 5 monitors, 3 min intervals | **Current** |
| Starter | $20/month | 20 monitors, 1 min intervals | Production |
| Team | $85/month | Unlimited monitors | Enterprise |

**Current Status**: ✅ Configured with API token  
**Action Required**: None. Free tier is sufficient for starting.

---

## 5. SSO PROVIDERS (Enterprise Features)

### Azure AD - CONFIGURED

**Purpose**: Enterprise SSO (OIDC)

| Plan | Price | Features |
|------|-------|----------|
| **Free (with M365)** | $0 | Basic SSO, 50k objects |
| P1 | $6/user/month | Conditional access |
| P2 | $9/user/month | Identity protection |

**Current Status**: ✅ Configured  
**Action Required**: None if you have Microsoft 365

---

### Google Workspace - CONFIGURED

**Purpose**: Google SSO (OIDC)

| Plan | Price | Features |
|------|-------|----------|
| **OAuth only** | $0 | SSO for any Google account |
| Workspace | $6/user/month | Managed domains |

**Current Status**: ✅ Configured  
**Action Required**: None - Google OAuth is free

---

### Auth0 - CONFIGURED

**Purpose**: Developer-friendly SSO

| Plan | Price | Features |
|------|-------|----------|
| **Free** | $0/month | 7,500 MAU, 2 social connections |
| Essential | $23/month | 10k MAU, unlimited connections |
| Professional | $240/month | 50k MAU, MFA, roles |

**Current Status**: ✅ Free tier  
**Action Required**: None for development

---

### OneLogin - CONFIGURED

**Purpose**: SAML SSO for enterprises

| Plan | Price | Features |
|------|-------|----------|
| **Starter** | $2/user/month | Basic SSO |
| Advanced | $4/user/month | MFA, directory sync |

**Current Status**: ✅ Configured  
**Action Required**: None - configured for SAML testing

---

## 6. FUTURE SERVICES (In Development)

### Stripe - NOT YET REQUIRED

**Purpose**: Payment processing for SaaS subscriptions

| Plan | Price | Features |
|------|-------|----------|
| Standard | 2.9% + $0.30/txn | Full API access |

**Current Status**: Placeholder in config  
**Action Required**: Set up when ready to accept payments

---

### HubSpot - NOT YET REQUIRED

**Purpose**: CRM connector for customer data sync

| Plan | Price | Features |
|------|-------|----------|
| Free CRM | $0 | Basic CRM, limited API |
| Starter | $20/month | 1,000 contacts, full API |

**Current Status**: Placeholder in config  
**Action Required**: Set up when implementing HubSpot connector

---

## Quick Start: Minimum Viable Costs

### Development (Now)

| Service | Plan | Cost |
|---------|------|------|
| Anthropic | Pay-as-you-go | $5-10 credits |
| Supabase | Free | $0 |
| Upstash | Free | $0 |
| Vercel | Hobby | $0 |
| Temporal | Self-hosted | $0 |
| Better Stack | Free | $0 |
| SSO Providers | Free tiers | $0 |
| **Total** | | **$5-10** |

### Production (MVP Launch)

| Service | Plan | Cost |
|---------|------|------|
| Anthropic | Pay-as-you-go | $50-150/month |
| OpenAI (optional) | Pay-as-you-go | $5-20/month |
| Supabase | Pro | $25/month |
| Upstash | Pay-as-you-go | $5-10/month |
| Vercel | Pro | $20/month |
| Temporal | Self-hosted or Cloud | $0-200/month |
| Better Stack | Starter | $20/month |
| **Total** | | **$125-445/month** |

### Enterprise (Scale)

| Service | Plan | Cost |
|---------|------|------|
| Anthropic | Enterprise | Custom |
| Supabase | Team | $599/month |
| Upstash | Pro | $120/month |
| Vercel | Enterprise | Custom |
| Temporal | Cloud Pro | Custom |
| Better Stack | Team | $85/month |
| **Total** | | **$1,000+/month** |

---

## Immediate Action Items

### Priority 1: Enable AI Features (Today)

1. **Add Anthropic Credits** (REQUIRED)
   - Go to: https://console.anthropic.com/settings/billing
   - Add payment method
   - Add $5-20 credits
   - This enables LangGraph code generation

2. **Add OpenAI Credits** (OPTIONAL)
   - Go to: https://platform.openai.com/settings/organization/billing
   - Add $5 credits
   - OR skip this - local embeddings work fine

### Priority 2: Production Prep (When Ready)

3. **Upgrade Supabase to Pro** ($25/mo)
   - Prevents database pausing
   - More storage and bandwidth

4. **Upgrade Vercel to Pro** ($20/mo)
   - Team features
   - Better analytics

---

## Cost Summary Table

| Scenario | Monthly Cost | Suitable For |
|----------|--------------|--------------|
| **Development** | $5-10 | Building & testing |
| **Soft Launch** | $50-75 | Early users, beta |
| **Production** | $125-200 | General availability |
| **Scale** | $500+ | High volume, enterprise |

---

## Billing URLs Quick Reference

| Service | Billing URL |
|---------|-------------|
| Anthropic | https://console.anthropic.com/settings/billing |
| OpenAI | https://platform.openai.com/settings/organization/billing |
| Supabase | https://supabase.com/dashboard/project/bdvebjnxpsdhinpgvkgo/settings/billing |
| Upstash | https://console.upstash.com/billing |
| Vercel | https://vercel.com/dashboard/usage |
| Better Stack | https://betterstack.com/team/billing |
| Auth0 | https://manage.auth0.com/dashboard/billing |

---

**Report Generated**: 2026-01-31
