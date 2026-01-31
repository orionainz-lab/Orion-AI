# Phase 6B Architecture: Advanced Features

**Created**: 2026-01-31  
**Complexity**: Level 4 (Complex) - Enterprise Features  
**Estimated Duration**: 14-20 hours  
**Prerequisites**: Phase 6A Complete ✅

---

## Executive Summary

Phase 6B extends the platform with **advanced enterprise features**:
- Additional connectors (Salesforce, QuickBooks, Slack)
- LLM-assisted schema mapping UI
- Custom connector builder framework
- Advanced analytics dashboard
- Bulk sync operations
- Connector marketplace UI

### Success Criteria
- ✅ 3+ additional connectors implemented
- ✅ LLM schema mapping reduces config time by 70%
- ✅ Custom connector builder enables non-developers
- ✅ Analytics provide actionable insights
- ✅ Bulk operations handle 1000+ records
- ✅ Marketplace UI enables self-service

---

## Architecture Decisions (ADRs)

### ADR-025: LLM Schema Mapping Strategy
**Decision**: Claude 3.5 Sonnet with Function Calling for Schema Discovery

**Problem**: Manual schema mapping is tedious and error-prone. Users must:
1. Read API documentation
2. Identify field names and types
3. Map to unified schema manually
4. Test transformations

**Solution**: AI-assisted schema mapping that:
- Analyzes API documentation automatically
- Suggests field mappings with confidence scores
- Generates transformation functions
- Validates mappings with test data

**Implementation**:
```python
class SchemaMapper:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def discover_schema(self, api_docs: str, sample_response: dict):
        """
        Use LLM to analyze API docs and suggest mappings.
        
        Returns:
            {
                "customer_email": {
                    "source_field": "email",
                    "confidence": 0.95,
                    "transformation": null
                },
                "customer_name": {
                    "source_field": "name",
                    "confidence": 0.90,
                    "transformation": null
                },
                "customer_phone": {
                    "source_field": "contact.phone",
                    "confidence": 0.85,
                    "transformation": "extract_phone_number"
                }
            }
        """
```

**Benefits**:
- 70% reduction in connector setup time
- Fewer mapping errors
- Self-documenting transformations
- Easy to review and override

**Alternatives Considered**:
1. **Rule-based mapping**: Too rigid, can't handle variations
2. **Gorilla LLM**: Specialized but less flexible than Claude
3. **Manual only**: Time-consuming, error-prone

---

### ADR-026: Salesforce Integration Strategy
**Decision**: Hybrid MCP + Direct API Approach

**Rationale**:
- Salesforce API is complex with many object types
- MCP provides auth abstraction
- Direct API allows fine-grained control
- Bulk API needed for large data volumes

**Architecture**:
```
┌─────────────────────────────────────────┐
│        Salesforce Adapter               │
├─────────────────────────────────────────┤
│  ┌─────────────┐    ┌──────────────┐   │
│  │ MCP Client  │    │ Direct HTTP  │   │
│  │ (Auth/CRUD) │    │ (Bulk API)   │   │
│  └─────────────┘    └──────────────┘   │
├─────────────────────────────────────────┤
│         Unified Mapping Layer           │
│  • Account → UnifiedCustomer            │
│  • Opportunity → UnifiedInvoice         │
│  • Lead → UnifiedCustomer               │
└─────────────────────────────────────────┘
```

**Supported Operations**:
- Standard CRUD via REST API
- Bulk insert/update via Bulk API 2.0
- Real-time changes via Streaming API
- SOQL queries for advanced filtering

---

### ADR-027: Custom Connector Builder Architecture
**Decision**: No-Code UI with Generated Python Adapters

**User Flow**:
```
1. User provides API documentation URL
2. LLM analyzes docs, extracts endpoints
3. User maps sample response to unified schema
4. System generates Python adapter code
5. User tests with sandbox credentials
6. Connector deployed to personal namespace
```

**Generated Artifacts**:
```python
# connectors/adapters/custom_{connector_name}/
├── __init__.py
├── adapter.py              # Generated adapter class
├── schema_mapping.json     # Field mappings
├── tests/
│   └── test_adapter.py     # Generated tests
└── README.md              # Auto-generated docs
```

**Technology Stack**:
- **Frontend**: React form builder with drag-drop
- **Backend**: FastAPI endpoints for generation
- **LLM**: Claude 3.5 Sonnet for code generation
- **Storage**: Supabase for user connectors
- **Execution**: Sandboxed Python environment

**Security Considerations**:
- User credentials isolated per namespace
- Generated code reviewed before deployment
- Sandboxed execution environment
- Rate limiting on custom connectors

---

### ADR-028: Analytics Dashboard Strategy
**Decision**: Real-Time Metrics with Supabase + Chart.js

**Dashboard Sections**:

1. **Connector Health**
   - Active connections
   - Sync success rate
   - Error trends
   - API latency

2. **Data Flow Metrics**
   - Records synced (last 24h, 7d, 30d)
   - Top connectors by volume
   - Data growth trends
   - Sync frequency

3. **User Activity**
   - Active users
   - Most used connectors
   - Configuration changes
   - Support tickets

4. **System Performance**
   - API response times
   - Workflow success rate
   - Database query performance
   - Queue depths

**Implementation**:
```typescript
// Frontend: Real-time dashboard with Chart.js
interface DashboardMetrics {
  connectorHealth: {
    active: number;
    degraded: number;
    failed: number;
  };
  syncMetrics: {
    last24h: number;
    last7d: number;
    successRate: number;
  };
  performance: {
    avgResponseTime: number;
    p95ResponseTime: number;
    errorRate: number;
  };
}
```

**Data Pipeline**:
```
Connectors → Events → Supabase → Realtime → Dashboard
     ↓
Temporal Workflows → Metrics Table → Aggregation
     ↓
Process Events → Analytics Views → Chart Data
```

---

## Implementation Plan

### Workstream 1: Salesforce Connector (4-5 hours)

**Files to Create**:
```
connectors/adapters/salesforce/
├── __init__.py
├── adapter.py                  # Main adapter
├── bulk_api.py                 # Bulk operations
├── streaming.py                # Real-time events
├── soql.py                     # SOQL query builder
└── mappings.py                 # Object mappings

connectors/tests/
└── test_salesforce_adapter.py  # 15+ tests
```

**Salesforce Objects to Support**:
1. **Account** → UnifiedCustomer
2. **Contact** → UnifiedCustomer
3. **Lead** → UnifiedCustomer
4. **Opportunity** → UnifiedInvoice
5. **Product** → Custom object

**Key Features**:
- OAuth 2.0 authentication
- CRUD operations
- Bulk insert/update (up to 10,000 records)
- SOQL queries
- Streaming API for real-time changes

**Sample Code**:
```python
@register_adapter("salesforce")
class SalesforceAdapter(BaseAdapter[UnifiedCustomer]):
    """Salesforce CRM adapter with bulk operations"""
    
    name = "salesforce"
    version = "1.0.0"
    capabilities = [
        AdapterCapability.READ,
        AdapterCapability.WRITE,
        AdapterCapability.WEBHOOK,
        AdapterCapability.BATCH,
        AdapterCapability.STREAMING
    ]
    
    async def bulk_upsert_customers(
        self,
        customers: List[UnifiedCustomer],
        batch_size: int = 200
    ) -> Dict[str, Any]:
        """
        Bulk upsert using Salesforce Bulk API 2.0.
        
        Handles up to 10,000 records per job.
        """
        # Use Bulk API 2.0 for efficient large-scale operations
        ...
```

---

### Workstream 2: QuickBooks Connector (3-4 hours)

**Files to Create**:
```
connectors/adapters/quickbooks/
├── __init__.py
├── adapter.py                  # Main adapter
├── oauth_handler.py            # OAuth flow
└── invoice_mapping.py          # Invoice transformations

connectors/tests/
└── test_quickbooks_adapter.py
```

**QuickBooks Objects to Support**:
1. **Customer** → UnifiedCustomer
2. **Invoice** → UnifiedInvoice
3. **Payment** → UnifiedEvent
4. **Item** → UnifiedLineItem

**Key Features**:
- OAuth 2.0 with token refresh
- Query filters (date ranges, status)
- Invoice CRUD
- Payment tracking
- Webhook support for changes

**Sample Code**:
```python
@register_adapter("quickbooks")
class QuickBooksAdapter(BaseAdapter[UnifiedInvoice]):
    """QuickBooks Online adapter"""
    
    name = "quickbooks"
    version = "1.0.0"
    capabilities = [
        AdapterCapability.READ,
        AdapterCapability.WRITE,
        AdapterCapability.WEBHOOK
    ]
    
    async def sync_invoices(
        self,
        since: datetime = None
    ) -> List[UnifiedInvoice]:
        """
        Sync invoices modified since given date.
        
        Uses QuickBooks Query API with pagination.
        """
        ...
```

---

### Workstream 3: Slack Connector (2-3 hours)

**Files to Create**:
```
connectors/adapters/slack/
├── __init__.py
├── adapter.py                  # Main adapter
└── event_handler.py            # Webhook events

connectors/tests/
└── test_slack_adapter.py
```

**Slack Features to Support**:
1. **Notifications** → Send messages to channels
2. **Events** → Receive messages/reactions
3. **Users** → Sync user directory
4. **Workflows** → Approval requests

**Key Features**:
- OAuth 2.0 with bot token
- Send messages (markdown, blocks)
- Interactive components (buttons, modals)
- Event subscriptions
- File uploads

**Use Cases**:
- Notify team of sync failures
- Approval requests via Slack
- Status updates on workflows
- Error alerts

---

### Workstream 4: LLM Schema Mapping UI (4-5 hours)

**Files to Create**:
```
frontend/app/connectors/mapping/
├── page.tsx                    # Main mapping UI
├── ApiAnalyzer.tsx             # API doc analyzer
├── FieldMapper.tsx             # Drag-drop field mapper
├── TransformationEditor.tsx    # Code editor for transforms
└── MappingPreview.tsx          # Live preview

api/connectors/
├── schema_mapper.py            # LLM-powered mapping
└── code_generator.py           # Generate adapter code

services/
└── llm_mapper.py              # LLM integration
```

**UI Flow**:
```
Step 1: Upload API Documentation
  → User provides OpenAPI spec or URL
  → LLM analyzes and extracts endpoints

Step 2: Sample Response
  → User provides sample JSON response
  → LLM identifies fields and types

Step 3: Mapping Suggestions
  → LLM suggests field mappings
  → User reviews and overrides

Step 4: Transformation Functions
  → LLM generates transformation code
  → User tests with sample data

Step 5: Generate Connector
  → System generates Python adapter
  → User tests in sandbox
  → Deploy to personal namespace
```

**LLM Prompt Example**:
```python
SCHEMA_MAPPING_PROMPT = """
Analyze this API response and map fields to our UnifiedCustomer schema.

API Response:
{sample_response}

UnifiedCustomer Schema:
- email (required): EmailStr
- name (required): str
- phone (optional): str
- company (optional): str
- billing_address (optional): UnifiedAddress
- tags (optional): List[str]

Provide a JSON mapping with:
{
  "field_name": {
    "source_path": "path.to.field",
    "confidence": 0.0-1.0,
    "transformation": "function_name or null",
    "reasoning": "why this mapping"
  }
}
"""
```

---

### Workstream 5: Custom Connector Builder (3-4 hours)

**Files to Create**:
```
frontend/app/connectors/builder/
├── page.tsx                    # Builder home
├── ApiDocAnalyzer.tsx          # Doc upload/analysis
├── EndpointConfig.tsx          # Configure endpoints
├── AuthConfig.tsx              # Auth setup
└── TestSandbox.tsx             # Test environment

api/connectors/builder/
├── generator.py                # Code generator
├── validator.py                # Validate generated code
└── deployer.py                 # Deploy to namespace

templates/
└── adapter_template.py.jinja2  # Adapter template
```

**Generated Adapter Template**:
```python
# Generated by Orion AI Connector Builder
# Created: {timestamp}
# User: {user_id}

from connectors.adapters.base import BaseAdapter, AdapterConfig
from connectors.adapters.registry import register_adapter

@register_adapter("{connector_name}")
class {ConnectorName}Adapter(BaseAdapter[UnifiedCustomer]):
    """
    {connector_description}
    
    Auto-generated connector.
    API Documentation: {api_docs_url}
    """
    
    name = "{connector_name}"
    version = "1.0.0"
    capabilities = {capabilities}
    
    # Auto-generated mapping
    FIELD_MAPPINGS = {field_mappings}
    
    def _get_auth_headers(self) -> dict[str, str]:
        {auth_implementation}
    
    async def to_unified(self, data: dict) -> UnifiedCustomer:
        {transformation_implementation}
    
    async def from_unified(self, model: UnifiedCustomer) -> dict:
        {reverse_transformation_implementation}
```

**Security Measures**:
- Code review before deployment
- Sandboxed execution
- Rate limiting per user
- Credential isolation
- Audit logging

---

### Workstream 6: Analytics Dashboard (3-4 hours)

**Files to Create**:
```
frontend/app/analytics/
├── page.tsx                    # Main dashboard
├── ConnectorHealth.tsx         # Health widgets
├── SyncMetrics.tsx             # Sync statistics
├── PerformanceCharts.tsx       # Performance graphs
└── DataFlow.tsx                # Flow diagrams

frontend/components/charts/
├── LineChart.tsx               # Time series
├── BarChart.tsx                # Comparisons
├── PieChart.tsx                # Distributions
└── HeatMap.tsx                 # Activity heatmap

api/analytics/
├── metrics.py                  # Metrics aggregation
└── reports.py                  # Report generation

supabase/views/
├── connector_metrics.sql       # Metrics view
└── sync_analytics.sql          # Analytics view
```

**Dashboard Widgets**:

1. **Connector Status**
   ```typescript
   <ConnectorHealthWidget
     active={25}
     degraded={2}
     failed={1}
     onViewDetails={(status) => navigate(`/connectors?status=${status}`)}
   />
   ```

2. **Sync Volume**
   ```typescript
   <SyncVolumeChart
     data={[
       { date: '2026-01-24', records: 1234 },
       { date: '2026-01-25', records: 1456 },
       ...
     ]}
     timeRange="7d"
   />
   ```

3. **Performance Metrics**
   ```typescript
   <PerformanceMetrics
     avgResponseTime={234}  // ms
     p95ResponseTime={567}  // ms
     errorRate={0.02}       // 2%
     successRate={99.8}     // %
   />
   ```

4. **Top Connectors**
   ```typescript
   <TopConnectorsList
     connectors={[
       { name: "Salesforce", records: 45678, status: "healthy" },
       { name: "HubSpot", records: 23456, status: "healthy" },
       { name: "Stripe", records: 12345, status: "degraded" },
     ]}
   />
   ```

**Real-time Updates**:
```typescript
// Use Supabase Realtime for live updates
const { data: metrics } = useRealtimeMetrics({
  table: 'connector_metrics',
  filter: { user_id: userId },
  refreshInterval: 10000  // 10 seconds
});
```

---

## Database Schema Extensions

### New Tables

```sql
-- Connector marketplace
CREATE TABLE connector_marketplace (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  connector_id UUID NOT NULL REFERENCES connectors(id),
  publisher_id UUID NOT NULL REFERENCES auth.users(id),
  name TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL,
  pricing_model TEXT, -- free, paid, freemium
  install_count INTEGER DEFAULT 0,
  rating DECIMAL(2,1),
  is_verified BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User installed connectors
CREATE TABLE user_installed_connectors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  marketplace_connector_id UUID NOT NULL REFERENCES connector_marketplace(id),
  installed_at TIMESTAMPTZ DEFAULT NOW(),
  last_used_at TIMESTAMPTZ,
  config JSONB,
  UNIQUE(user_id, marketplace_connector_id)
);

-- Custom connectors (user-generated)
CREATE TABLE custom_connectors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  name TEXT NOT NULL,
  generated_code TEXT NOT NULL,
  field_mappings JSONB NOT NULL,
  api_docs_url TEXT,
  sandbox_tested BOOLEAN DEFAULT false,
  deployed BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Schema mappings (LLM-assisted)
CREATE TABLE schema_mappings_llm (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  connector_id UUID NOT NULL REFERENCES connectors(id),
  source_field TEXT NOT NULL,
  target_field TEXT NOT NULL,
  transformation TEXT,
  confidence DECIMAL(3,2), -- 0.00 to 1.00
  llm_reasoning TEXT,
  user_approved BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sync metrics (for analytics)
CREATE TABLE sync_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  config_id UUID NOT NULL REFERENCES connector_configs(id),
  sync_started_at TIMESTAMPTZ NOT NULL,
  sync_completed_at TIMESTAMPTZ,
  records_processed INTEGER,
  records_failed INTEGER,
  duration_ms INTEGER,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics aggregations (materialized view)
CREATE MATERIALIZED VIEW connector_analytics AS
SELECT 
  config_id,
  DATE(sync_started_at) as date,
  COUNT(*) as sync_count,
  SUM(records_processed) as total_records,
  AVG(duration_ms) as avg_duration_ms,
  SUM(CASE WHEN error_message IS NOT NULL THEN 1 ELSE 0 END) as error_count
FROM sync_metrics
GROUP BY config_id, DATE(sync_started_at);

-- Refresh materialized view hourly
CREATE INDEX idx_connector_analytics_date ON connector_analytics(date DESC);
```

---

## Integration Points

### With Existing Phases

**Phase 1 (Temporal)**:
- Bulk sync workflows
- Scheduled analytics aggregation
- Connector health monitoring

**Phase 2 (LangGraph)**:
- LLM schema mapping
- Intelligent error recovery
- Code generation workflows

**Phase 3 (Supabase)**:
- Custom connector storage
- Analytics data aggregation
- Marketplace RLS policies

**Phase 4 (Frontend)**:
- Analytics dashboard integration
- Connector builder UI
- Marketplace browsing

**Phase 5 (Connectors)**:
- New connector implementations
- Enhanced mapping capabilities
- Bulk operation support

---

## Testing Strategy

### New Tests Required

1. **Salesforce Adapter** (15 tests)
   - OAuth flow
   - CRUD operations
   - Bulk insert (1000 records)
   - SOQL queries
   - Streaming events

2. **QuickBooks Adapter** (12 tests)
   - OAuth token refresh
   - Invoice CRUD
   - Payment tracking
   - Webhook handling

3. **Slack Adapter** (10 tests)
   - Message sending
   - Interactive components
   - Event subscriptions
   - File uploads

4. **LLM Schema Mapper** (8 tests)
   - API doc analysis
   - Field mapping suggestions
   - Transformation generation
   - Confidence scoring

5. **Custom Connector Builder** (12 tests)
   - Code generation
   - Sandbox execution
   - Validation
   - Deployment

6. **Analytics Dashboard** (8 tests)
   - Metrics calculation
   - Real-time updates
   - Chart rendering
   - Export functionality

**Total New Tests**: 65+ tests

---

## Performance Considerations

### Bulk Operations

| Operation | Records | Target Time |
|-----------|---------|-------------|
| Bulk Insert | 1,000 | <30 seconds |
| Bulk Update | 1,000 | <30 seconds |
| Bulk Sync | 10,000 | <5 minutes |

### Analytics Queries

| Query | Target Time |
|-------|-------------|
| Dashboard metrics | <500ms |
| 7-day trend | <1 second |
| 30-day report | <3 seconds |
| Export CSV | <10 seconds |

### LLM Operations

| Operation | Target Time |
|-----------|-------------|
| Schema analysis | <10 seconds |
| Field mapping | <5 seconds |
| Code generation | <15 seconds |

---

## Cost Analysis

### Additional Costs

| Service | Component | Monthly Cost |
|---------|-----------|--------------|
| Claude API | Schema mapping | ~$50-100 |
| Salesforce Dev | Sandbox environment | $0 (dev) |
| QuickBooks Dev | Sandbox environment | $0 (dev) |
| Slack App | Bot hosting | $0 (free tier) |
| **Phase 6B Total** | | **~$50-100** |

**Combined Cost (6A + 6B)**: ~$300-370/month

---

## Timeline

| Week | Deliverables |
|------|--------------|
| **Week 1** | • Salesforce connector<br>• QuickBooks connector<br>• Slack connector |
| **Week 2** | • LLM schema mapping<br>• Custom connector builder |
| **Week 3** | • Analytics dashboard<br>• Testing & polish |

**Total Duration**: 14-20 hours over 2-3 weeks

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LLM hallucinations in mapping | Medium | Medium | Confidence scores, user review |
| Generated code security issues | Medium | High | Sandboxing, code review |
| Salesforce API rate limits | Medium | Medium | Exponential backoff, caching |
| Analytics query performance | Low | Medium | Materialized views, indexing |
| Marketplace abuse | Low | Medium | Verification process, reporting |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| New connectors | 3+ |
| LLM mapping accuracy | >80% |
| Custom connectors created | 10+ in first month |
| Analytics page load time | <1 second |
| Bulk sync throughput | >100 records/second |
| User satisfaction | >4.5/5 stars |

---

## Next Steps After Phase 6B

1. **Phase 6C**: Enterprise Features (multi-tenancy, SSO)
2. **Connector Marketplace**: Public marketplace launch
3. **Advanced Analytics**: Predictive insights, anomaly detection
4. **Mobile App**: iOS/Android connector management
5. **White-label**: Customer-branded connector platform

---

**Status**: READY FOR BUILD MODE  
**Prerequisites**: Phase 6A Complete ✅
