"""
Tests for Salesforce Adapter

Comprehensive test suite for Salesforce CRM integration.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from connectors.adapters.salesforce import SalesforceAdapter
from connectors.adapters.base import AdapterConfig, AdapterCapability
from connectors.adapters.exceptions import AuthenticationError, APIError
from connectors.unified_schema.customer import UnifiedCustomer


@pytest.fixture
def salesforce_config():
    """Create Salesforce adapter configuration"""
    return AdapterConfig(
        credentials={
            "access_token": "test_access_token_123",
            "instance_url": "https://test.salesforce.com"
        }
    )


@pytest.fixture
def adapter(salesforce_config):
    """Create Salesforce adapter instance"""
    return SalesforceAdapter(config=salesforce_config)


@pytest.fixture
def sample_contact_data():
    """Sample Salesforce Contact data"""
    return {
        "Id": "003xx000004TmiQAAS",
        "Email": "test@example.com",
        "FirstName": "John",
        "LastName": "Doe",
        "Phone": "+1234567890",
        "MailingStreet": "123 Main St",
        "MailingCity": "San Francisco",
        "MailingState": "CA",
        "MailingPostalCode": "94105",
        "MailingCountry": "US",
        "AccountId": "001xx000003DGb2AAG"
    }


@pytest.fixture
def sample_account_data():
    """Sample Salesforce Account data"""
    return {
        "Id": "001xx000003DGb2AAG",
        "Name": "Acme Corp",
        "Phone": "+1987654321",
        "BillingStreet": "456 Market St",
        "BillingCity": "San Francisco",
        "BillingState": "CA",
        "BillingPostalCode": "94105",
        "BillingCountry": "US"
    }


@pytest.fixture
def sample_lead_data():
    """Sample Salesforce Lead data"""
    return {
        "Id": "00Qxx000001gHyUEAU",
        "Email": "lead@example.com",
        "FirstName": "Jane",
        "LastName": "Smith",
        "Phone": "+1555123456",
        "Company": "TechStart Inc",
        "Street": "789 Startup Ave",
        "City": "Austin",
        "State": "TX",
        "PostalCode": "78701",
        "Country": "US",
        "Status": "Open - Not Contacted"
    }


# ============================================
# Registration & Configuration Tests
# ============================================

def test_adapter_registration(adapter):
    """Test adapter is registered with correct name"""
    assert adapter.name == "salesforce"
    assert SalesforceAdapter.name == "salesforce"


def test_adapter_version(adapter):
    """Test adapter version"""
    assert adapter.version == "1.0.0"
    assert SalesforceAdapter.version == "1.0.0"


def test_adapter_capabilities(adapter):
    """Test adapter capabilities"""
    expected_capabilities = [
        AdapterCapability.READ,
        AdapterCapability.WRITE,
        AdapterCapability.WEBHOOK,
        AdapterCapability.BATCH,
        AdapterCapability.STREAMING
    ]
    assert SalesforceAdapter.capabilities == expected_capabilities


def test_supported_object_types(adapter):
    """Test supported Salesforce object types"""
    assert "Account" in SalesforceAdapter.OBJECT_TYPES
    assert "Contact" in SalesforceAdapter.OBJECT_TYPES
    assert "Lead" in SalesforceAdapter.OBJECT_TYPES
    assert "Opportunity" in SalesforceAdapter.OBJECT_TYPES


# ============================================
# Authentication Tests
# ============================================

def test_auth_headers_success(adapter):
    """Test successful auth header generation"""
    headers = adapter._get_auth_headers()
    
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test_access_token_123"
    assert headers["Content-Type"] == "application/json"


def test_auth_headers_missing_token():
    """Test auth headers fail without access token"""
    config = AdapterConfig(credentials={"instance_url": "https://test.salesforce.com"})
    adapter = SalesforceAdapter(config=config)
    
    with pytest.raises(AuthenticationError, match="access token not provided"):
        adapter._get_auth_headers()


def test_instance_url_success(adapter):
    """Test instance URL retrieval"""
    url = adapter._get_instance_url()
    assert url == "https://test.salesforce.com"


def test_instance_url_strips_trailing_slash():
    """Test instance URL strips trailing slash"""
    config = AdapterConfig(
        credentials={
            "access_token": "token123",
            "instance_url": "https://test.salesforce.com/"
        }
    )
    adapter = SalesforceAdapter(config=config)
    url = adapter._get_instance_url()
    assert url == "https://test.salesforce.com"


def test_instance_url_missing():
    """Test instance URL fails when missing"""
    config = AdapterConfig(credentials={"access_token": "token123"})
    adapter = SalesforceAdapter(config=config)
    
    with pytest.raises(AuthenticationError, match="instance URL not provided"):
        adapter._get_instance_url()


# ============================================
# Transformation Tests - Contact
# ============================================

@pytest.mark.asyncio
async def test_to_unified_contact(adapter, sample_contact_data):
    """Test Contact to UnifiedCustomer transformation"""
    unified = await adapter.to_unified(sample_contact_data, "Contact")
    
    assert unified.source_system == "salesforce"
    assert unified.source_id == "003xx000004TmiQAAS"
    assert unified.email == "test@example.com"
    assert unified.name == "John Doe"
    assert unified.phone == "+1234567890"
    
    # Check billing address
    assert unified.billing_address is not None
    assert unified.billing_address["street"] == "123 Main St"
    assert unified.billing_address["city"] == "San Francisco"
    assert unified.billing_address["state"] == "CA"
    assert unified.billing_address["postal_code"] == "94105"
    assert unified.billing_address["country"] == "US"
    
    # Check custom fields
    assert unified.custom_fields["salesforce_type"] == "Contact"
    assert unified.custom_fields["account_id"] == "001xx000003DGb2AAG"


@pytest.mark.asyncio
async def test_to_unified_contact_no_address(adapter):
    """Test Contact transformation without address"""
    data = {
        "Id": "003xx000004TmiQAAS",
        "Email": "test@example.com",
        "FirstName": "John",
        "LastName": "Doe"
    }
    
    unified = await adapter.to_unified(data, "Contact")
    
    assert unified.billing_address is None


# ============================================
# Transformation Tests - Account
# ============================================

@pytest.mark.asyncio
async def test_to_unified_account(adapter, sample_account_data):
    """Test Account to UnifiedCustomer transformation"""
    unified = await adapter.to_unified(sample_account_data, "Account")
    
    assert unified.source_system == "salesforce"
    assert unified.source_id == "001xx000003DGb2AAG"
    assert unified.name == "Acme Corp"
    assert unified.phone == "+1987654321"
    
    # Check billing address
    assert unified.billing_address is not None
    assert unified.billing_address["street"] == "456 Market St"
    assert unified.billing_address["city"] == "San Francisco"
    
    # Check custom fields
    assert unified.custom_fields["salesforce_type"] == "Account"


# ============================================
# Transformation Tests - Lead
# ============================================

@pytest.mark.asyncio
async def test_to_unified_lead(adapter, sample_lead_data):
    """Test Lead to UnifiedCustomer transformation"""
    unified = await adapter.to_unified(sample_lead_data, "Lead")
    
    assert unified.source_system == "salesforce"
    assert unified.source_id == "00Qxx000001gHyUEAU"
    assert unified.email == "lead@example.com"
    assert unified.name == "Jane Smith"
    assert unified.phone == "+1555123456"
    assert unified.company == "TechStart Inc"
    
    # Check billing address
    assert unified.billing_address is not None
    assert unified.billing_address["street"] == "789 Startup Ave"
    assert unified.billing_address["city"] == "Austin"
    assert unified.billing_address["state"] == "TX"
    
    # Check custom fields
    assert unified.custom_fields["salesforce_type"] == "Lead"
    assert unified.custom_fields["status"] == "Open - Not Contacted"


@pytest.mark.asyncio
async def test_to_unified_unsupported_type(adapter, sample_contact_data):
    """Test transformation fails for unsupported object type"""
    with pytest.raises(APIError, match="Unsupported Salesforce object type"):
        await adapter.to_unified(sample_contact_data, "Opportunity")


# ============================================
# Reverse Transformation Tests
# ============================================

@pytest.mark.asyncio
async def test_from_unified_contact(adapter):
    """Test UnifiedCustomer to Contact transformation"""
    customer = UnifiedCustomer(
        source_system="salesforce",
        email="test@example.com",
        name="John Doe",
        phone="+1234567890",
        billing_address={
            "source_system": "salesforce",
            "source_id": "123",
            "street": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "postal_code": "94105",
            "country": "US"
        }
    )
    
    data = await adapter.from_unified(customer, "Contact")
    
    assert data["Email"] == "test@example.com"
    assert data["FirstName"] == "John"
    assert data["LastName"] == "Doe"
    assert data["Phone"] == "+1234567890"
    assert data["MailingStreet"] == "123 Main St"
    assert data["MailingCity"] == "San Francisco"
    assert data["MailingState"] == "CA"


@pytest.mark.asyncio
async def test_from_unified_lead(adapter):
    """Test UnifiedCustomer to Lead transformation"""
    customer = UnifiedCustomer(
        source_system="salesforce",
        email="lead@example.com",
        name="Jane Smith",
        phone="+1555123456",
        company="TechStart Inc",
        billing_address={
            "source_system": "salesforce",
            "source_id": "123",
            "street": "789 Startup Ave",
            "city": "Austin",
            "state": "TX",
            "postal_code": "78701",
            "country": "US"
        }
    )
    
    data = await adapter.from_unified(customer, "Lead")
    
    assert data["Email"] == "lead@example.com"
    assert data["FirstName"] == "Jane"
    assert data["LastName"] == "Smith"
    assert data["Phone"] == "+1555123456"
    assert data["Company"] == "TechStart Inc"
    assert data["Street"] == "789 Startup Ave"


@pytest.mark.asyncio
async def test_from_unified_single_name(adapter):
    """Test name handling when single word"""
    customer = UnifiedCustomer(
        source_system="salesforce",
        email="test@example.com",
        name="Madonna"
    )
    
    data = await adapter.from_unified(customer, "Contact")
    
    assert data["FirstName"] == "Madonna"
    assert data["LastName"] == "Madonna"


@pytest.mark.asyncio
async def test_from_unified_unsupported_type(adapter):
    """Test reverse transformation fails for unsupported type"""
    customer = UnifiedCustomer(
        source_system="salesforce",
        email="test@example.com",
        name="John Doe"
    )
    
    with pytest.raises(APIError, match="Unsupported Salesforce object type"):
        await adapter.from_unified(customer, "Account")


# ============================================
# SOQL Query Tests
# ============================================

@pytest.mark.asyncio
async def test_query_soql_success(adapter):
    """Test SOQL query execution"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "records": [
            {"Id": "001", "Name": "Test Account"}
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    adapter._client = mock_client
    
    results = await adapter.query_soql("SELECT Id, Name FROM Account LIMIT 10")
    
    assert len(results) == 1
    assert results[0]["Id"] == "001"
    assert results[0]["Name"] == "Test Account"
    mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_query_soql_error(adapter):
    """Test SOQL query error handling"""
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("SOQL syntax error")
    adapter._client = mock_client
    
    with pytest.raises(APIError, match="SOQL query failed"):
        await adapter.query_soql("INVALID SOQL")


# ============================================
# Bulk Operations Tests
# ============================================

@pytest.mark.asyncio
async def test_bulk_upsert_exceeds_limit(adapter):
    """Test bulk upsert rejects >10,000 records"""
    customers = [
        UnifiedCustomer(
            source_system="salesforce",
            email=f"test{i}@example.com",
            name=f"Test User {i}"
        )
        for i in range(10001)
    ]
    
    with pytest.raises(APIError, match="limited to 10,000 records"):
        await adapter.bulk_upsert_customers(customers)


def test_convert_to_csv(adapter):
    """Test CSV conversion for bulk API"""
    records = [
        {"Email": "test1@example.com", "FirstName": "John", "LastName": "Doe"},
        {"Email": "test2@example.com", "FirstName": "Jane", "LastName": "Smith"}
    ]
    
    csv_data = adapter._convert_to_csv(records)
    
    assert "Email,FirstName,LastName" in csv_data
    assert "test1@example.com,John,Doe" in csv_data
    assert "test2@example.com,Jane,Smith" in csv_data


def test_convert_to_csv_empty(adapter):
    """Test CSV conversion with empty list"""
    csv_data = adapter._convert_to_csv([])
    assert csv_data == ""


# ============================================
# Error Handling Tests
# ============================================

@pytest.mark.asyncio
async def test_list_customers_connection_error(adapter):
    """Test list customers handles connection errors"""
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("Connection timeout")
    adapter._client = mock_client
    
    with pytest.raises(APIError, match="Failed to list"):
        await adapter.list_customers()


@pytest.mark.asyncio
async def test_create_customer_api_error(adapter):
    """Test create customer handles API errors"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("API Error")
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    customer = UnifiedCustomer(
        source_system="salesforce",
        email="test@example.com",
        name="Test User"
    )
    
    with pytest.raises(APIError, match="Failed to create"):
        await adapter.create_customer(customer)
