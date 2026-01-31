# Phase 5 Architecture: The Connectivity Fabric

**Date**: 2026-01-31  
**Mode**: PLAN  
**Phase**: Phase 5 - N-to-N Connector Framework  
**Status**: Architecture Design

---

## 1. Executive Summary

Phase 5 implements **Layer 1: The Connectivity Fabric** - solving the N-to-N integration problem through a Unified Schema Engine. This document provides the complete architectural design, ADR decisions, database schema, and implementation plan.

### The N-to-N Problem

| Approach | Complexity | 100 Systems |
|----------|------------|-------------|
| Point-to-Point | O(N²) | 9,900 connectors |
| Hub & Spoke (This Phase) | O(2N) | 200 adapters |

**Savings**: 98% reduction in integration complexity

---

## 2. Architecture Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SYSTEMS                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ Stripe  │  │ HubSpot │  │ Slack   │  │ Jira    │  ...       │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘            │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ADAPTER LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │StripeAdapter │  │HubSpotAdapter│  │ SlackAdapter │  ...     │
│  │  (Inbound)   │  │  (Outbound)  │  │   (Both)     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼─────────────────┼─────────────────┼───────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                 UNIFIED SCHEMA ENGINE                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              CANONICAL MODELS                            │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐           │    │
│  │  │  Unified   │ │  Unified   │ │  Unified   │  ...      │    │
│  │  │  Customer  │ │  Invoice   │ │   Event    │           │    │
│  │  └────────────┘ └────────────┘ └────────────┘           │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────┐  ┌─────────────────┐                       │
│  │ Schema Mapper   │  │ Transformer     │                       │
│  │ (LLM-powered)   │  │ (Data Pipeline) │                       │
│  └─────────────────┘  └─────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PLATFORM CORE                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  │
│  │ Temporal   │  │ LangGraph  │  │ Supabase   │  │ Frontend │  │
│  │ (Phase 1)  │  │ (Phase 2)  │  │ (Phase 3)  │  │ (Phase 4)│  │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **Adapter Layer** | API-specific transformations, auth, retries |
| **Unified Schema** | Canonical models, validation, versioning |
| **Schema Mapper** | LLM-powered mapping generation |
| **Transformer** | Data conversion pipeline |
| **Registry** | Connector metadata, configs, credentials |

---

## 3. Architecture Decision Records

### ADR-017: Connector Architecture Pattern

**Status**: DECIDED  
**Date**: 2026-01-31

**Context**:  
We need a flexible architecture that allows adding new connectors without modifying core code.

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| 1. Monolithic | Simple | No extensibility |
| 2. Layered | Clear separation | Rigid structure |
| 3. Plugin | Extensible, dynamic | More complex |
| 4. Microservices | Scalable | Over-engineered |

**Decision**: **Option 3 - Plugin Architecture**

**Rationale**:
- Connectors can be added/removed at runtime
- Each connector is isolated
- Easy to test in isolation
- Supports third-party connectors
- Aligns with 200-line rule (small, focused files)

**Implementation**:
```python
# Decorator-based registration
@register_adapter("stripe")
class StripeAdapter(BaseAdapter):
    async def to_unified(self, data: dict) -> UnifiedCustomer:
        ...
    
    async def from_unified(self, model: UnifiedCustomer) -> dict:
        ...
```

---

### ADR-018: Credential Storage Strategy

**Status**: DECIDED  
**Date**: 2026-01-31

**Context**:  
Connectors require API keys, OAuth tokens, and other sensitive credentials.

**Options Considered**:

| Option | Security | Complexity | Native |
|--------|----------|------------|--------|
| 1. Environment vars | Medium | Low | No |
| 2. Supabase Vault | High | Medium | Yes |
| 3. HashiCorp Vault | Very High | High | No |
| 4. Encrypted DB column | High | Medium | Yes |

**Decision**: **Option 4 - Encrypted Database Column** with Option 2 (Supabase Vault) for OAuth tokens

**Rationale**:
- Supabase Vault may not be available on all tiers
- Encrypted columns work universally
- OAuth refresh tokens go to Vault when available
- Audit trail via process_events

**Implementation**:
```python
from cryptography.fernet import Fernet

class CredentialManager:
    def encrypt(self, plaintext: str) -> str:
        return self.fernet.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        return self.fernet.decrypt(ciphertext.encode()).decode()
```

**Security Controls**:
- Encryption key from environment variable
- RLS on credentials table (user can only see own)
- Audit logging for all access
- Automatic key rotation support

---

### ADR-019: Schema Versioning Strategy

**Status**: DECIDED  
**Date**: 2026-01-31

**Context**:  
Unified schemas will evolve over time. We need backward compatibility.

**Options Considered**:

| Option | Example | Compatibility |
|--------|---------|---------------|
| 1. Semantic | v1.0.0, v2.0.0 | Clear breaking changes |
| 2. Date-based | 2026-01-31 | Time-ordered |
| 3. Hash-based | abc123 | Content-addressed |
| 4. No versioning | latest | Simple but risky |

**Decision**: **Option 1 - Semantic Versioning**

**Rationale**:
- Industry standard (SemVer)
- Clear communication of breaking changes
- Easy to understand for developers
- Supports multiple versions in parallel

**Implementation**:
```python
class UnifiedCustomer(BaseModel):
    __schema_version__ = "1.0.0"
    
    id: str
    email: str
    name: str
    # v1.1.0 added:
    phone: Optional[str] = None
    # v2.0.0 breaking: renamed 'name' to 'full_name'
```

**Version Rules**:
- MAJOR: Breaking changes (field removal, type change)
- MINOR: Backward-compatible additions
- PATCH: Bug fixes, documentation

---

### ADR-020: LLM Model Selection for Schema Mapping

**Status**: DECIDED  
**Date**: 2026-01-31

**Context**:  
Need an LLM to parse API documentation and generate schema mappings.

**Options Considered**:

| Option | Specialty | Cost | Availability |
|--------|-----------|------|--------------|
| 1. Gorilla LLM | API calls | Free | Self-hosted |
| 2. xLAM | Function calling | Free | Self-hosted |
| 3. Claude 3.5 Sonnet | General + code | $$$ | API |
| 4. GPT-4o | Function calling | $$$ | API |

**Decision**: **Option 3 (Claude 3.5 Sonnet) as primary** with structured prompting

**Rationale**:
- Already integrated in platform (Plan.md)
- Excellent at code generation
- Strong JSON output
- Gorilla/xLAM availability uncertain
- Can switch to Gorilla later if beneficial

**Implementation**:
```python
async def generate_mapping(api_spec: dict) -> SchemaMapping:
    prompt = f"""
    Given this API specification:
    {json.dumps(api_spec)}
    
    Generate a mapping to UnifiedCustomer schema:
    - id: unique identifier
    - email: email address
    - name: full name
    
    Output JSON mapping:
    """
    response = await claude.complete(prompt)
    return SchemaMapping.parse_raw(response)
```

---

## 4. Database Schema

### 4.1 Entity Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────────┐
│     connectors      │       │  connector_configs  │
├─────────────────────┤       ├─────────────────────┤
│ id (PK, UUID)       │───┐   │ id (PK, UUID)       │
│ name                │   │   │ connector_id (FK)   │──┐
│ type                │   │   │ user_id (FK)        │  │
│ description         │   │   │ config (JSONB)      │  │
│ version             │   │   │ is_active           │  │
│ schema_version      │   │   │ created_at          │  │
│ capabilities        │   │   │ updated_at          │  │
│ status              │   │   └─────────────────────┘  │
│ created_at          │   │                            │
│ updated_at          │   │   ┌─────────────────────┐  │
└─────────────────────┘   │   │connector_credentials│  │
                          │   ├─────────────────────┤  │
                          └──▶│ id (PK, UUID)       │  │
                              │ config_id (FK)      │◀─┘
                              │ credential_type     │
                              │ encrypted_value     │
                              │ expires_at          │
                              │ created_at          │
                              │ updated_at          │
                              └─────────────────────┘

┌─────────────────────┐       ┌─────────────────────┐
│   schema_mappings   │       │   webhook_configs   │
├─────────────────────┤       ├─────────────────────┤
│ id (PK, UUID)       │       │ id (PK, UUID)       │
│ connector_id (FK)   │       │ connector_id (FK)   │
│ source_schema       │       │ user_id (FK)        │
│ target_schema       │       │ endpoint_path       │
│ mapping_rules       │       │ secret_key          │
│ version             │       │ is_active           │
│ is_active           │       │ created_at          │
│ created_at          │       └─────────────────────┘
│ updated_at          │
└─────────────────────┘
```

### 4.2 SQL Schema

```sql
-- Connector definitions (system-level)
CREATE TABLE connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK (type IN ('inbound', 'outbound', 'bidirectional')),
    description TEXT,
    version TEXT NOT NULL DEFAULT '1.0.0',
    schema_version TEXT NOT NULL DEFAULT '1.0.0',
    capabilities JSONB DEFAULT '[]'::jsonb,
    status TEXT NOT NULL DEFAULT 'active' 
        CHECK (status IN ('active', 'deprecated', 'disabled')),
    icon_url TEXT,
    documentation_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- User-specific connector configurations
CREATE TABLE connector_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_id UUID NOT NULL REFERENCES connectors(id),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    name TEXT NOT NULL,
    config JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMPTZ,
    sync_status TEXT DEFAULT 'idle' 
        CHECK (sync_status IN ('idle', 'syncing', 'error', 'success')),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(connector_id, user_id, name)
);

-- Encrypted credentials
CREATE TABLE connector_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID NOT NULL REFERENCES connector_configs(id) ON DELETE CASCADE,
    credential_type TEXT NOT NULL 
        CHECK (credential_type IN ('api_key', 'oauth_token', 'basic_auth', 'bearer_token')),
    encrypted_value TEXT NOT NULL,
    expires_at TIMESTAMPTZ,
    refresh_token_encrypted TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Schema mappings (LLM-generated)
CREATE TABLE schema_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_id UUID NOT NULL REFERENCES connectors(id),
    source_schema TEXT NOT NULL,
    target_schema TEXT NOT NULL,
    mapping_rules JSONB NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT true,
    confidence_score FLOAT,
    human_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Webhook configurations
CREATE TABLE webhook_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_id UUID NOT NULL REFERENCES connectors(id),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    endpoint_path TEXT NOT NULL,
    secret_key TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    event_types JSONB DEFAULT '["*"]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, endpoint_path)
);

-- Indexes for performance
CREATE INDEX idx_connector_configs_user ON connector_configs(user_id);
CREATE INDEX idx_connector_configs_connector ON connector_configs(connector_id);
CREATE INDEX idx_schema_mappings_connector ON schema_mappings(connector_id);
CREATE INDEX idx_webhook_configs_user ON webhook_configs(user_id);
CREATE INDEX idx_webhook_configs_path ON webhook_configs(endpoint_path);
```

### 4.3 Row Level Security Policies

```sql
-- Enable RLS on all tables
ALTER TABLE connector_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE connector_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_configs ENABLE ROW LEVEL SECURITY;

-- connector_configs: Users see only their own
CREATE POLICY "Users can view own configs"
    ON connector_configs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own configs"
    ON connector_configs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own configs"
    ON connector_configs FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own configs"
    ON connector_configs FOR DELETE
    USING (auth.uid() = user_id);

-- connector_credentials: Access via config ownership
CREATE POLICY "Users can view own credentials"
    ON connector_credentials FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM connector_configs
            WHERE connector_configs.id = connector_credentials.config_id
            AND connector_configs.user_id = auth.uid()
        )
    );

-- Similar policies for webhook_configs...
CREATE POLICY "Users can manage own webhooks"
    ON webhook_configs FOR ALL
    USING (auth.uid() = user_id);

-- connectors and schema_mappings are public read
-- (system-level, no RLS needed for read)
```

---

## 5. Unified Schema Design

### 5.1 Base Model

```python
# connectors/unified_schema/base.py
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum

class SchemaVersion(str, Enum):
    V1_0_0 = "1.0.0"
    V1_1_0 = "1.1.0"

class UnifiedBase(BaseModel):
    """Base class for all unified models"""
    
    __schema_version__: str = "1.0.0"
    
    # Common metadata
    source_system: str = Field(..., description="Origin system (e.g., 'stripe')")
    source_id: str = Field(..., description="ID in source system")
    unified_id: Optional[str] = Field(None, description="Platform unified ID")
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    synced_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Raw data preservation
    raw_data: Optional[dict] = Field(None, exclude=True)
    
    class Config:
        extra = "allow"  # Allow additional fields
```

### 5.2 Canonical Models

```python
# connectors/unified_schema/customer.py
from .base import UnifiedBase
from pydantic import EmailStr, Field
from typing import Optional, List

class UnifiedAddress(UnifiedBase):
    """Unified address model"""
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class UnifiedCustomer(UnifiedBase):
    """
    Canonical customer model.
    Maps to: Stripe Customer, HubSpot Contact, Salesforce Account
    """
    __schema_version__ = "1.0.0"
    
    # Core fields
    email: EmailStr
    name: str = Field(..., min_length=1)
    
    # Optional fields (v1.1.0+)
    phone: Optional[str] = None
    company: Optional[str] = None
    
    # Nested
    billing_address: Optional[UnifiedAddress] = None
    shipping_address: Optional[UnifiedAddress] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    custom_fields: dict = Field(default_factory=dict)
```

```python
# connectors/unified_schema/invoice.py
from .base import UnifiedBase
from pydantic import Field
from typing import Optional, List
from decimal import Decimal
from datetime import date

class UnifiedLineItem(UnifiedBase):
    """Invoice line item"""
    description: str
    quantity: int = 1
    unit_price: Decimal
    total: Decimal
    
class UnifiedInvoice(UnifiedBase):
    """
    Canonical invoice model.
    Maps to: Stripe Invoice, QuickBooks Invoice, Xero Invoice
    """
    __schema_version__ = "1.0.0"
    
    # Core fields
    customer_id: str
    invoice_number: str
    status: str = Field(..., pattern="^(draft|pending|paid|void|overdue)$")
    
    # Amounts
    subtotal: Decimal
    tax: Decimal = Decimal("0")
    total: Decimal
    currency: str = "USD"
    
    # Dates
    issue_date: date
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    
    # Line items
    line_items: List[UnifiedLineItem] = Field(default_factory=list)
```

```python
# connectors/unified_schema/event.py
from .base import UnifiedBase
from pydantic import Field
from typing import Optional, Any
from datetime import datetime

class UnifiedEvent(UnifiedBase):
    """
    Canonical event model for webhooks and notifications.
    Maps to: Stripe Event, HubSpot Webhook, Generic Webhook
    """
    __schema_version__ = "1.0.0"
    
    # Core fields
    event_type: str = Field(..., description="e.g., 'customer.created'")
    event_category: str = Field(default="system")
    
    # Payload
    payload: dict = Field(default_factory=dict)
    
    # Context
    user_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    
    # Timestamps
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## 6. Adapter Framework Design

### 6.1 Base Adapter

```python
# connectors/adapters/base.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Any
from pydantic import BaseModel
import httpx

T = TypeVar('T', bound=BaseModel)

class AdapterConfig(BaseModel):
    """Base configuration for adapters"""
    base_url: str
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0

class AdapterCapability:
    """Capability flags"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    WEBHOOK = "webhook"
    BATCH = "batch"

class BaseAdapter(ABC, Generic[T]):
    """
    Abstract base class for all connectors.
    Implements the Adapter pattern for API integration.
    """
    
    name: str = "base"
    version: str = "1.0.0"
    capabilities: List[str] = []
    
    def __init__(self, config: AdapterConfig, credentials: dict):
        self.config = config
        self.credentials = credentials
        self._client: Optional[httpx.AsyncClient] = None
    
    async def connect(self) -> None:
        """Initialize HTTP client with auth"""
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers=self._get_auth_headers()
        )
    
    async def disconnect(self) -> None:
        """Cleanup resources"""
        if self._client:
            await self._client.aclose()
    
    @abstractmethod
    def _get_auth_headers(self) -> dict:
        """Return authentication headers"""
        pass
    
    @abstractmethod
    async def to_unified(self, data: dict) -> T:
        """Transform external data to unified model"""
        pass
    
    @abstractmethod
    async def from_unified(self, model: T) -> dict:
        """Transform unified model to external format"""
        pass
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, *args):
        await self.disconnect()
```

### 6.2 Adapter Registry

```python
# connectors/adapters/registry.py
from typing import Dict, Type, Optional
from .base import BaseAdapter
import importlib
import pkgutil

_adapter_registry: Dict[str, Type[BaseAdapter]] = {}

def register_adapter(name: str):
    """Decorator to register an adapter"""
    def decorator(cls: Type[BaseAdapter]):
        cls.name = name
        _adapter_registry[name] = cls
        return cls
    return decorator

def get_adapter(name: str) -> Optional[Type[BaseAdapter]]:
    """Get adapter class by name"""
    return _adapter_registry.get(name)

def list_adapters() -> Dict[str, Type[BaseAdapter]]:
    """List all registered adapters"""
    return _adapter_registry.copy()

def discover_adapters(package_path: str = "connectors.adapters"):
    """Auto-discover and register adapters from package"""
    package = importlib.import_module(package_path)
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        if module_name not in ("base", "registry", "factory", "exceptions"):
            importlib.import_module(f"{package_path}.{module_name}")
```

### 6.3 Adapter Factory

```python
# connectors/adapters/factory.py
from typing import Optional
from .base import BaseAdapter, AdapterConfig
from .registry import get_adapter
from services.connector_registry import ConnectorRegistry

class AdapterFactory:
    """Factory for creating adapter instances"""
    
    def __init__(self, registry: ConnectorRegistry):
        self.registry = registry
    
    async def create(
        self, 
        connector_name: str, 
        config_id: str
    ) -> Optional[BaseAdapter]:
        """Create adapter instance with config and credentials"""
        
        # Get adapter class
        adapter_class = get_adapter(connector_name)
        if not adapter_class:
            raise ValueError(f"Unknown connector: {connector_name}")
        
        # Get config from database
        config_data = await self.registry.get_config(config_id)
        credentials = await self.registry.get_credentials(config_id)
        
        # Create instance
        adapter_config = AdapterConfig(**config_data)
        return adapter_class(adapter_config, credentials)
```

---

## 7. Demo Connector: Stripe

```python
# connectors/adapters/stripe/adapter.py
from connectors.adapters.base import BaseAdapter, AdapterConfig, AdapterCapability
from connectors.adapters.registry import register_adapter
from connectors.unified_schema.customer import UnifiedCustomer
from connectors.unified_schema.invoice import UnifiedInvoice
from typing import List
import httpx

@register_adapter("stripe")
class StripeAdapter(BaseAdapter[UnifiedCustomer]):
    """
    Stripe API adapter.
    Docs: https://stripe.com/docs/api
    """
    
    name = "stripe"
    version = "1.0.0"
    capabilities = [
        AdapterCapability.READ,
        AdapterCapability.WRITE,
        AdapterCapability.WEBHOOK
    ]
    
    def _get_auth_headers(self) -> dict:
        api_key = self.credentials.get("api_key", "")
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
    async def to_unified(self, data: dict) -> UnifiedCustomer:
        """Transform Stripe customer to unified model"""
        address = data.get("address", {}) or {}
        return UnifiedCustomer(
            source_system="stripe",
            source_id=data["id"],
            email=data["email"],
            name=data.get("name", data["email"]),
            phone=data.get("phone"),
            billing_address={
                "source_system": "stripe",
                "source_id": data["id"],
                "street": address.get("line1"),
                "city": address.get("city"),
                "state": address.get("state"),
                "postal_code": address.get("postal_code"),
                "country": address.get("country")
            } if address else None,
            raw_data=data
        )
    
    async def from_unified(self, model: UnifiedCustomer) -> dict:
        """Transform unified model to Stripe format"""
        data = {
            "email": model.email,
            "name": model.name,
        }
        if model.phone:
            data["phone"] = model.phone
        if model.billing_address:
            data["address"] = {
                "line1": model.billing_address.street,
                "city": model.billing_address.city,
                "state": model.billing_address.state,
                "postal_code": model.billing_address.postal_code,
                "country": model.billing_address.country
            }
        return data
    
    async def list_customers(self, limit: int = 100) -> List[UnifiedCustomer]:
        """Fetch customers from Stripe"""
        response = await self._client.get(
            "/v1/customers",
            params={"limit": limit}
        )
        response.raise_for_status()
        data = response.json()
        return [await self.to_unified(c) for c in data.get("data", [])]
    
    async def create_customer(self, customer: UnifiedCustomer) -> UnifiedCustomer:
        """Create customer in Stripe"""
        payload = await self.from_unified(customer)
        response = await self._client.post("/v1/customers", data=payload)
        response.raise_for_status()
        return await self.to_unified(response.json())
```

---

## 8. Webhook Handler Design

```python
# api/webhooks/handler.py
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import hmac
import hashlib
from services.connector_registry import ConnectorRegistry
from connectors.unified_schema.event import UnifiedEvent

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

async def verify_signature(
    payload: bytes,
    signature: str,
    secret: str,
    algorithm: str = "sha256"
) -> bool:
    """Verify webhook signature"""
    expected = hmac.new(
        secret.encode(),
        payload,
        getattr(hashlib, algorithm)
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

@router.post("/{connector}/{endpoint_path:path}")
async def handle_webhook(
    connector: str,
    endpoint_path: str,
    request: Request,
    x_signature: Optional[str] = Header(None, alias="X-Signature"),
    x_hub_signature: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    """
    Generic webhook handler.
    Routes: POST /webhooks/stripe/events
            POST /webhooks/hubspot/contact-update
    """
    payload = await request.body()
    
    # Get webhook config
    registry = ConnectorRegistry()
    config = await registry.get_webhook_config(connector, endpoint_path)
    
    if not config:
        raise HTTPException(404, "Webhook endpoint not found")
    
    # Verify signature
    signature = x_signature or x_hub_signature
    if signature and config.get("secret_key"):
        if not await verify_signature(payload, signature, config["secret_key"]):
            raise HTTPException(401, "Invalid signature")
    
    # Parse and transform to unified event
    data = await request.json()
    event = UnifiedEvent(
        source_system=connector,
        source_id=data.get("id", "unknown"),
        event_type=data.get("type", "unknown"),
        payload=data,
        user_id=config.get("user_id")
    )
    
    # Store event and trigger workflow
    await registry.store_event(event)
    
    # TODO: Trigger Temporal workflow for processing
    
    return {"received": True, "event_id": str(event.unified_id)}
```

---

## 9. Integration with Existing Phases

### 9.1 Temporal Integration (Phase 1)

```python
# temporal/activities/connector_activities.py
from temporalio import activity
from connectors.adapters.factory import AdapterFactory
from connectors.unified_schema.customer import UnifiedCustomer

@activity.defn
async def sync_customers(connector_name: str, config_id: str) -> int:
    """Sync customers from external system"""
    factory = AdapterFactory(ConnectorRegistry())
    
    async with await factory.create(connector_name, config_id) as adapter:
        customers = await adapter.list_customers()
        
        # Store in Supabase
        for customer in customers:
            await store_unified_customer(customer)
        
        return len(customers)

@activity.defn
async def push_customer(
    connector_name: str, 
    config_id: str, 
    customer_data: dict
) -> dict:
    """Push customer to external system"""
    factory = AdapterFactory(ConnectorRegistry())
    customer = UnifiedCustomer(**customer_data)
    
    async with await factory.create(connector_name, config_id) as adapter:
        result = await adapter.create_customer(customer)
        return result.model_dump()
```

### 9.2 LangGraph Integration (Phase 2)

```python
# agents/tools/connector_tools.py
from langchain.tools import tool
from connectors.adapters.factory import AdapterFactory

@tool
async def list_available_connectors() -> list:
    """List all available connector types"""
    from connectors.adapters.registry import list_adapters
    return [
        {"name": name, "version": cls.version, "capabilities": cls.capabilities}
        for name, cls in list_adapters().items()
    ]

@tool
async def fetch_customers(connector_name: str, config_id: str, limit: int = 10) -> list:
    """Fetch customers from a connected system"""
    factory = AdapterFactory(ConnectorRegistry())
    async with await factory.create(connector_name, config_id) as adapter:
        customers = await adapter.list_customers(limit=limit)
        return [c.model_dump() for c in customers]
```

### 9.3 Frontend Integration (Phase 4)

New pages to add:
- `/connectors` - List available connectors
- `/connectors/[id]` - Connector detail/config
- `/connectors/new` - Add new connector
- `/webhooks` - Webhook management

---

## 10. Implementation Plan

### Phase 5.1: Foundation (Day 1)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Create directory structure | 0.5h | Folder structure |
| Install dependencies | 0.5h | requirements.txt |
| Implement UnifiedBase | 1h | base.py |
| Implement UnifiedCustomer | 1h | customer.py |
| Implement UnifiedInvoice | 1h | invoice.py |
| Implement UnifiedEvent | 0.5h | event.py |
| Write schema tests | 0.5h | test_unified_schema.py |

**Subtotal**: 5 hours

### Phase 5.2: Adapter Framework (Day 1-2)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Implement BaseAdapter | 1h | base.py |
| Implement registry | 0.5h | registry.py |
| Implement factory | 0.5h | factory.py |
| Implement exceptions | 0.5h | exceptions.py |
| Database migration | 1h | SQL schema |
| RLS policies | 0.5h | Policies |
| Write framework tests | 1h | test_adapters.py |

**Subtotal**: 5 hours

### Phase 5.3: Demo Connectors (Day 2)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Stripe adapter | 1.5h | stripe/adapter.py |
| HubSpot adapter | 1.5h | hubspot/adapter.py |
| Mock test adapter | 0.5h | webhook_test/adapter.py |
| Integration tests | 1h | Mock API tests |

**Subtotal**: 4.5 hours

### Phase 5.4: Registry & Credentials (Day 2)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Connector registry service | 1h | connector_registry.py |
| Credential encryption | 1h | Crypto utils |
| CRUD operations | 1h | Service methods |

**Subtotal**: 3 hours

### Phase 5.5: Webhook Handler (Day 3)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Webhook router | 1h | handler.py |
| Signature verification | 0.5h | verify.py |
| Event storage | 0.5h | Integration |
| Webhook tests | 1h | Tests |

**Subtotal**: 3 hours

### Phase 5.6: LLM Mapping (Day 3)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Schema mapper service | 1.5h | schema_mapper.py |
| API spec parser | 1h | api_spec_parser.py |
| Mapping validation | 0.5h | Validation |

**Subtotal**: 3 hours

### Phase 5.7: Integration & Testing (Day 3-4)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Temporal activities | 1h | connector_activities.py |
| LangGraph tools | 1h | connector_tools.py |
| Frontend pages | 2h | Connector UI |
| E2E testing | 1.5h | Integration tests |
| Documentation | 0.5h | README updates |

**Subtotal**: 6 hours

### Total Estimated: 29.5 hours
### Expected Actual (89% efficiency): ~4-6 hours

---

## 11. Success Criteria

| Criterion | Target | Validation |
|-----------|--------|------------|
| Unified Schema | 3 models | UnifiedCustomer, Invoice, Event |
| Working Adapters | 2 minimum | Stripe + HubSpot |
| Connector Registry | CRUD working | Database integration |
| Webhook Handler | Operational | Signature verification |
| LLM Mapping | Functional | Generate valid mappings |
| Temporal Integration | Activities work | Sync workflows |
| LangGraph Integration | Tools work | Agent can use connectors |
| Code Quality | 200-line rule | All files compliant |
| Test Coverage | 80%+ | Unit + integration |

---

## 12. Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Gorilla unavailable | Use Claude with structured prompts |
| API rate limits | Implement backoff, caching |
| OAuth complexity | Use established libraries |
| Schema drift | Version schemas, migrations |
| Credential exposure | Encryption, audit logging |

---

## 13. File Checklist

### To Create

```
connectors/
├── __init__.py
├── unified_schema/
│   ├── __init__.py
│   ├── base.py
│   ├── customer.py
│   ├── invoice.py
│   └── event.py
├── adapters/
│   ├── __init__.py
│   ├── base.py
│   ├── registry.py
│   ├── factory.py
│   ├── exceptions.py
│   ├── stripe/
│   │   ├── __init__.py
│   │   └── adapter.py
│   └── hubspot/
│       ├── __init__.py
│       └── adapter.py
├── mapping/
│   ├── __init__.py
│   └── generator.py
└── tests/
    ├── __init__.py
    ├── test_unified_schema.py
    ├── test_adapters.py
    └── test_registry.py

services/
├── connector_registry.py
├── schema_mapper.py
└── credential_manager.py

api/
└── webhooks/
    ├── __init__.py
    ├── handler.py
    └── verify.py

temporal/activities/
└── connector_activities.py

agents/tools/
└── connector_tools.py
```

---

**PLAN Mode Complete**: 2026-01-31  
**Next Mode**: VAN QA (Dependency Verification) → BUILD  
**Status**: Ready for implementation
