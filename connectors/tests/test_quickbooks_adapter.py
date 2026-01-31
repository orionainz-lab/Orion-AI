"""
Tests for QuickBooks Adapter

Comprehensive test suite for QuickBooks Online integration.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from connectors.adapters.quickbooks import QuickBooksAdapter
from connectors.adapters.base import AdapterConfig, AdapterCapability
from connectors.adapters.exceptions import AuthenticationError, APIError
from connectors.unified_schema.customer import UnifiedCustomer


@pytest.fixture
def quickbooks_config():
    """Create QuickBooks adapter configuration"""
    return AdapterConfig(
        credentials={
            "access_token": "test_access_token_123",
            "refresh_token": "test_refresh_token_456",
            "realm_id": "9130353654853704",
            "token_expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "client_id": "test_client_id",
            "client_secret": "test_client_secret"
        }
    )


@pytest.fixture
def adapter(quickbooks_config):
    """Create QuickBooks adapter instance"""
    return QuickBooksAdapter(config=quickbooks_config)


@pytest.fixture
def sample_customer_data():
    """Sample QuickBooks Customer data"""
    return {
        "Id": "1",
        "DisplayName": "Acme Corporation",
        "CompanyName": "Acme Corporation",
        "PrimaryEmailAddr": {
            "Address": "contact@acme.com"
        },
        "PrimaryPhone": {
            "FreeFormNumber": "+1-555-1234"
        },
        "BillAddr": {
            "Line1": "123 Business St",
            "Line2": "Suite 100",
            "City": "San Francisco",
            "CountrySubDivisionCode": "CA",
            "PostalCode": "94105",
            "Country": "US"
        },
        "SyncToken": "0",
        "Balance": 1500.00
    }


@pytest.fixture
def sample_invoice_data():
    """Sample QuickBooks Invoice data"""
    return {
        "Id": "101",
        "DocNumber": "INV-1001",
        "TxnDate": "2026-01-15",
        "DueDate": "2026-02-15",
        "TotalAmt": 1500.00,
        "Balance": 1500.00,
        "CustomerRef": {
            "value": "1",
            "name": "Acme Corporation"
        }
    }


# ============================================
# Registration & Configuration Tests
# ============================================

def test_adapter_registration(adapter):
    """Test adapter is registered with correct name"""
    assert adapter.name == "quickbooks"
    assert QuickBooksAdapter.name == "quickbooks"


def test_adapter_version(adapter):
    """Test adapter version"""
    assert adapter.version == "1.0.0"
    assert QuickBooksAdapter.version == "1.0.0"


def test_adapter_capabilities(adapter):
    """Test adapter capabilities"""
    expected_capabilities = [
        AdapterCapability.READ,
        AdapterCapability.WRITE,
        AdapterCapability.WEBHOOK
    ]
    assert QuickBooksAdapter.capabilities == expected_capabilities


def test_base_url(adapter):
    """Test QuickBooks API base URL"""
    assert adapter.BASE_URL == "https://quickbooks.api.intuit.com/v3/company"


# ============================================
# Authentication Tests
# ============================================

def test_auth_headers_success(adapter):
    """Test successful auth header generation"""
    headers = adapter._get_auth_headers()
    
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test_access_token_123"
    assert headers["Accept"] == "application/json"
    assert headers["Content-Type"] == "application/json"


def test_auth_headers_missing_token():
    """Test auth headers fail without access token"""
    config = AdapterConfig(credentials={"realm_id": "123456"})
    adapter = QuickBooksAdapter(config=config)
    
    with pytest.raises(AuthenticationError, match="access token not provided"):
        adapter._get_auth_headers()


def test_realm_id_success(adapter):
    """Test realm ID retrieval"""
    realm_id = adapter._get_realm_id()
    assert realm_id == "9130353654853704"


def test_realm_id_missing():
    """Test realm ID fails when missing"""
    config = AdapterConfig(credentials={"access_token": "token123"})
    adapter = QuickBooksAdapter(config=config)
    
    with pytest.raises(AuthenticationError, match="realm_id not provided"):
        adapter._get_realm_id()


# ============================================
# Token Refresh Tests
# ============================================

@pytest.mark.asyncio
async def test_token_refresh_not_needed(adapter):
    """Test token refresh skipped when token is valid"""
    # Token expires in 1 hour, shouldn't refresh
    await adapter._refresh_token_if_needed()
    # Should complete without error


@pytest.mark.asyncio
async def test_token_refresh_needed():
    """Test token refresh when expired"""
    config = AdapterConfig(
        credentials={
            "access_token": "old_token",
            "refresh_token": "refresh_token",
            "realm_id": "123456",
            "token_expires_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "client_id": "client_id",
            "client_secret": "client_secret"
        }
    )
    adapter = QuickBooksAdapter(config=config)
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = AsyncMock()
        mock_client_class.return_value = mock_client
        
        await adapter._refresh_token_if_needed()
        
        assert adapter.credentials["access_token"] == "new_access_token"
        assert adapter.credentials["refresh_token"] == "new_refresh_token"


@pytest.mark.asyncio
async def test_token_refresh_missing_credentials():
    """Test token refresh fails with missing credentials"""
    config = AdapterConfig(
        credentials={
            "access_token": "token",
            "realm_id": "123456",
            "token_expires_at": (datetime.utcnow() - timedelta(hours=1)).isoformat()
        }
    )
    adapter = QuickBooksAdapter(config=config)
    
    with pytest.raises(AuthenticationError, match="Missing OAuth refresh credentials"):
        await adapter._refresh_token_if_needed()


# ============================================
# Transformation Tests
# ============================================

@pytest.mark.asyncio
async def test_to_unified_customer(adapter, sample_customer_data):
    """Test Customer to UnifiedCustomer transformation"""
    unified = await adapter.to_unified(sample_customer_data)
    
    assert unified.source_system == "quickbooks"
    assert unified.source_id == "1"
    assert unified.email == "contact@acme.com"
    assert unified.name == "Acme Corporation"
    assert unified.phone == "+1-555-1234"
    assert unified.company == "Acme Corporation"
    
    # Check billing address
    assert unified.billing_address is not None
    assert unified.billing_address["street"] == "123 Business St"
    assert unified.billing_address["street2"] == "Suite 100"
    assert unified.billing_address["city"] == "San Francisco"
    assert unified.billing_address["state"] == "CA"
    assert unified.billing_address["postal_code"] == "94105"
    assert unified.billing_address["country"] == "US"
    
    # Check custom fields
    assert unified.custom_fields["quickbooks_sync_token"] == "0"
    assert unified.custom_fields["balance"] == 1500.00


@pytest.mark.asyncio
async def test_to_unified_customer_no_address(adapter):
    """Test Customer transformation without address"""
    data = {
        "Id": "1",
        "DisplayName": "Simple Customer",
        "PrimaryEmailAddr": {
            "Address": "simple@example.com"
        }
    }
    
    unified = await adapter.to_unified(data)
    
    assert unified.billing_address is None


@pytest.mark.asyncio
async def test_to_unified_customer_minimal(adapter):
    """Test Customer transformation with minimal data"""
    data = {
        "Id": "1",
        "DisplayName": "Minimal Customer"
    }
    
    unified = await adapter.to_unified(data)
    
    assert unified.source_id == "1"
    assert unified.name == "Minimal Customer"
    assert unified.email == "unknown@example.com"  # Default


@pytest.mark.asyncio
async def test_from_unified_customer(adapter):
    """Test UnifiedCustomer to QuickBooks format transformation"""
    customer = UnifiedCustomer(
        source_system="quickbooks",
        email="test@example.com",
        name="Test Customer",
        phone="+1-555-9999",
        company="Test Corp",
        billing_address={
            "source_system": "quickbooks",
            "source_id": "1",
            "street": "456 Test St",
            "street2": "Floor 2",
            "city": "Austin",
            "state": "TX",
            "postal_code": "78701",
            "country": "US"
        }
    )
    
    data = await adapter.from_unified(customer)
    
    assert data["DisplayName"] == "Test Customer"
    assert data["PrimaryEmailAddr"]["Address"] == "test@example.com"
    assert data["PrimaryPhone"]["FreeFormNumber"] == "+1-555-9999"
    assert data["CompanyName"] == "Test Corp"
    assert data["BillAddr"]["Line1"] == "456 Test St"
    assert data["BillAddr"]["Line2"] == "Floor 2"
    assert data["BillAddr"]["City"] == "Austin"


@pytest.mark.asyncio
async def test_from_unified_with_sync_token(adapter):
    """Test from_unified includes sync token"""
    customer = UnifiedCustomer(
        source_system="quickbooks",
        email="test@example.com",
        name="Test Customer",
        custom_fields={"quickbooks_sync_token": "3"}
    )
    
    data = await adapter.from_unified(customer)
    
    assert data["SyncToken"] == "3"


# ============================================
# List Customers Tests
# ============================================

@pytest.mark.asyncio
async def test_list_customers_success(adapter):
    """Test listing customers"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "QueryResponse": {
            "Customer": [
                {
                    "Id": "1",
                    "DisplayName": "Customer 1",
                    "PrimaryEmailAddr": {"Address": "customer1@example.com"}
                },
                {
                    "Id": "2",
                    "DisplayName": "Customer 2",
                    "PrimaryEmailAddr": {"Address": "customer2@example.com"}
                }
            ]
        }
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    adapter._client = mock_client
    
    customers = await adapter.list_customers(limit=50)
    
    assert len(customers) == 2
    assert customers[0].source_id == "1"
    assert customers[0].name == "Customer 1"
    assert customers[1].source_id == "2"


@pytest.mark.asyncio
async def test_list_customers_with_date_filter(adapter):
    """Test listing customers with modified_since filter"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "QueryResponse": {"Customer": []}
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    adapter._client = mock_client
    
    modified_since = datetime(2026, 1, 1)
    await adapter.list_customers(limit=50, modified_since=modified_since)
    
    # Check that WHERE clause was added to query
    call_args = mock_client.get.call_args
    query = call_args[1]["params"]["query"]
    assert "WHERE MetaData.LastUpdatedTime >= '2026-01-01'" in query


@pytest.mark.asyncio
async def test_list_customers_limit(adapter):
    """Test list customers respects limit"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "QueryResponse": {"Customer": []}
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    adapter._client = mock_client
    
    await adapter.list_customers(limit=2000)
    
    # Should cap at 1000
    call_args = mock_client.get.call_args
    query = call_args[1]["params"]["query"]
    assert "MAXRESULTS 1000" in query


@pytest.mark.asyncio
async def test_list_customers_error(adapter):
    """Test list customers error handling"""
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("API Error")
    adapter._client = mock_client
    
    with pytest.raises(APIError, match="Failed to list customers"):
        await adapter.list_customers()


# ============================================
# Create Customer Tests
# ============================================

@pytest.mark.asyncio
async def test_create_customer_success(adapter, sample_customer_data):
    """Test creating customer"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "Customer": sample_customer_data
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    customer = UnifiedCustomer(
        source_system="quickbooks",
        email="contact@acme.com",
        name="Acme Corporation"
    )
    
    result = await adapter.create_customer(customer)
    
    assert result.source_id == "1"
    assert result.name == "Acme Corporation"
    assert result.email == "contact@acme.com"


@pytest.mark.asyncio
async def test_create_customer_error(adapter):
    """Test create customer error handling"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("Validation error")
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    customer = UnifiedCustomer(
        source_system="quickbooks",
        email="test@example.com",
        name="Test"
    )
    
    with pytest.raises(APIError, match="Failed to create customer"):
        await adapter.create_customer(customer)


# ============================================
# Update Customer Tests
# ============================================

@pytest.mark.asyncio
async def test_update_customer_success(adapter, sample_customer_data):
    """Test updating customer"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "Customer": sample_customer_data
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    customer = UnifiedCustomer(
        source_system="quickbooks",
        source_id="1",
        email="updated@acme.com",
        name="Updated Name",
        custom_fields={"quickbooks_sync_token": "0"}
    )
    
    result = await adapter.update_customer(customer)
    
    assert result.source_id == "1"


@pytest.mark.asyncio
async def test_update_customer_no_source_id(adapter):
    """Test update customer fails without source_id"""
    customer = UnifiedCustomer(
        source_system="quickbooks",
        email="test@example.com",
        name="Test"
    )
    
    with pytest.raises(APIError, match="source_id required"):
        await adapter.update_customer(customer)


# ============================================
# Invoice Sync Tests
# ============================================

@pytest.mark.asyncio
async def test_sync_invoices_success(adapter, sample_invoice_data):
    """Test syncing invoices"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "QueryResponse": {
            "Invoice": [sample_invoice_data]
        }
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    adapter._client = mock_client
    
    invoices = await adapter.sync_invoices(limit=50)
    
    assert len(invoices) == 1
    assert invoices[0]["Id"] == "101"
    assert invoices[0]["DocNumber"] == "INV-1001"


@pytest.mark.asyncio
async def test_sync_invoices_with_date_filter(adapter):
    """Test syncing invoices with date filter"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "QueryResponse": {"Invoice": []}
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    adapter._client = mock_client
    
    since = datetime(2026, 1, 1)
    await adapter.sync_invoices(since=since, limit=50)
    
    call_args = mock_client.get.call_args
    query = call_args[1]["params"]["query"]
    assert "WHERE MetaData.LastUpdatedTime >= '2026-01-01'" in query


# ============================================
# Get Customer By ID Tests
# ============================================

@pytest.mark.asyncio
async def test_get_customer_by_id_success(adapter, sample_customer_data):
    """Test getting customer by ID"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "Customer": sample_customer_data
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    adapter._client = mock_client
    
    customer = await adapter.get_customer_by_id("1")
    
    assert customer.source_id == "1"
    assert customer.name == "Acme Corporation"


@pytest.mark.asyncio
async def test_get_customer_by_id_not_found(adapter):
    """Test get customer by ID when not found"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("Not found")
    mock_client.get.return_value = mock_response
    adapter._client = mock_client
    
    with pytest.raises(APIError, match="Failed to get customer"):
        await adapter.get_customer_by_id("999")
