"""
Tests for Custom Connector Builder

Comprehensive test suite for code generation framework.
"""

import pytest
from services.llm.connector_builder import (
    ConnectorBuilder,
    ConnectorSpec
)


@pytest.fixture
def connector_builder():
    """Create ConnectorBuilder instance"""
    return ConnectorBuilder(llm_client=None)


@pytest.fixture
def sample_connector_spec():
    """Sample connector specification"""
    return ConnectorSpec(
        name="test_api",
        description="Test API Connector",
        api_base_url="https://api.test.com",
        auth_type="api_key",
        endpoints=[
            {
                "path": "/customers",
                "method": "GET",
                "operation": "list",
                "response_key": "data"
            },
            {
                "path": "/customers",
                "method": "POST",
                "operation": "create"
            }
        ],
        field_mappings={
            "email": {
                "source_path": "email",
                "confidence": 1.0
            },
            "name": {
                "source_path": "full_name",
                "confidence": 0.95
            },
            "phone": {
                "source_path": "phone_number",
                "confidence": 0.90,
                "transformation": "format_phone"
            }
        }
    )


# ============================================
# Model Tests
# ============================================

def test_connector_spec_model():
    """Test ConnectorSpec model validation"""
    spec = ConnectorSpec(
        name="my_api",
        description="My API",
        api_base_url="https://api.example.com",
        auth_type="oauth2",
        endpoints=[],
        field_mappings={}
    )
    
    assert spec.name == "my_api"
    assert spec.auth_type == "oauth2"


def test_connector_spec_with_mappings():
    """Test ConnectorSpec with field mappings"""
    spec = ConnectorSpec(
        name="test",
        description="Test",
        api_base_url="https://test.com",
        auth_type="api_key",
        endpoints=[],
        field_mappings={
            "email": {"source_path": "email", "confidence": 0.95}
        }
    )
    
    assert "email" in spec.field_mappings


# ============================================
# Code Generation Tests
# ============================================

def test_generate_adapter_code_api_key(connector_builder, sample_connector_spec):
    """Test adapter code generation with API key auth"""
    code = connector_builder.generate_adapter_code(sample_connector_spec)
    
    # Check basic structure
    assert "class TestApiAdapter" in code
    assert "@register_adapter(\"test_api\")" in code
    assert "version = \"1.0.0\"" in code
    
    # Check API key auth
    assert "api_key" in code.lower()
    assert "Bearer" in code
    
    # Check base URL
    assert "https://api.test.com" in code
    
    # Check endpoints
    assert "/customers" in code


def test_generate_adapter_code_oauth2(connector_builder):
    """Test adapter code generation with OAuth 2.0"""
    spec = ConnectorSpec(
        name="oauth_api",
        description="OAuth API",
        api_base_url="https://api.oauth.com",
        auth_type="oauth2",
        endpoints=[],
        field_mappings={}
    )
    
    code = connector_builder.generate_adapter_code(spec)
    
    assert "access_token" in code
    assert "Bearer" in code


def test_generate_adapter_code_basic_auth(connector_builder):
    """Test adapter code generation with Basic auth"""
    spec = ConnectorSpec(
        name="basic_api",
        description="Basic Auth API",
        api_base_url="https://api.basic.com",
        auth_type="basic",
        endpoints=[],
        field_mappings={}
    )
    
    code = connector_builder.generate_adapter_code(spec)
    
    assert "username" in code
    assert "password" in code
    assert "base64" in code
    assert "Basic" in code


def test_generate_adapter_code_no_auth(connector_builder):
    """Test adapter code generation with no authentication"""
    spec = ConnectorSpec(
        name="public_api",
        description="Public API",
        api_base_url="https://api.public.com",
        auth_type="none",
        endpoints=[],
        field_mappings={}
    )
    
    code = connector_builder.generate_adapter_code(spec)
    
    assert "Content-Type" in code
    # Should not have auth-specific code
    assert "api_key" not in code.lower() or "not provided" not in code


def test_generate_adapter_code_class_name(connector_builder):
    """Test adapter class name generation"""
    spec = ConnectorSpec(
        name="my_custom_api",
        description="Test",
        api_base_url="https://test.com",
        auth_type="api_key",
        endpoints=[],
        field_mappings={}
    )
    
    code = connector_builder.generate_adapter_code(spec)
    
    # Should convert snake_case to PascalCase
    assert "class MyCustomApiAdapter" in code


def test_generate_adapter_code_capabilities(connector_builder, sample_connector_spec):
    """Test capabilities generation"""
    code = connector_builder.generate_adapter_code(sample_connector_spec)
    
    assert "AdapterCapability.READ" in code
    assert "AdapterCapability.WRITE" in code


def test_generate_adapter_code_field_mappings(connector_builder, sample_connector_spec):
    """Test field mapping generation"""
    code = connector_builder.generate_adapter_code(sample_connector_spec)
    
    # Check to_unified includes mapped fields
    assert "email" in code
    assert "full_name" in code
    assert "phone_number" in code


# ============================================
# Auth Code Generation Tests
# ============================================

def test_generate_auth_code_api_key(connector_builder):
    """Test API key auth code generation"""
    code, doc = connector_builder._generate_auth_code("api_key")
    
    assert "api_key" in code
    assert "Bearer" in code
    assert "api_key not provided" in code
    assert "API key" in doc


def test_generate_auth_code_oauth2(connector_builder):
    """Test OAuth 2.0 auth code generation"""
    code, doc = connector_builder._generate_auth_code("oauth2")
    
    assert "access_token" in code
    assert "Bearer" in code
    assert "OAuth" in doc


def test_generate_auth_code_basic(connector_builder):
    """Test Basic auth code generation"""
    code, doc = connector_builder._generate_auth_code("basic")
    
    assert "username" in code
    assert "password" in code
    assert "base64" in code
    assert "Basic" in code
    assert "Basic" in doc


def test_generate_auth_code_none(connector_builder):
    """Test no auth code generation"""
    code, doc = connector_builder._generate_auth_code("none")
    
    assert "Content-Type" in code
    assert "no authentication" in doc.lower()


# ============================================
# Transformation Generation Tests
# ============================================

def test_generate_to_unified(connector_builder):
    """Test to_unified transformation generation"""
    field_mappings = {
        "email": {"source_path": "user_email", "confidence": 0.95},
        "name": {"source_path": "full_name", "confidence": 0.90},
        "phone": {"source_path": "contact_phone", "confidence": 0.85}
    }
    
    code = connector_builder._generate_to_unified(field_mappings)
    
    assert "UnifiedCustomer" in code
    assert "user_email" in code
    assert "full_name" in code
    assert "contact_phone" in code


def test_generate_to_unified_with_address(connector_builder):
    """Test to_unified with address mapping"""
    field_mappings = {
        "billing_address": {"source_path": "address", "confidence": 0.90}
    }
    
    code = connector_builder._generate_to_unified(field_mappings)
    
    assert "billing_address" in code
    assert "street" in code
    assert "city" in code
    assert "state" in code


def test_generate_from_unified(connector_builder):
    """Test from_unified transformation generation"""
    field_mappings = {
        "email": {"source_path": "user_email", "confidence": 0.95},
        "name": {"source_path": "full_name", "confidence": 0.90}
    }
    
    code = connector_builder._generate_from_unified(field_mappings)
    
    assert "data = {}" in code
    assert "user_email" in code
    assert "model.email" in code
    assert "return data" in code


# ============================================
# Test Generation Tests
# ============================================

def test_generate_tests_api_key(connector_builder, sample_connector_spec):
    """Test generation for API key auth"""
    sample_data = {"id": "123", "email": "test@example.com"}
    
    tests = connector_builder.generate_tests(sample_connector_spec, sample_data)
    
    assert "test_adapter_registration" in tests
    assert "test_capabilities" in tests
    assert "test_to_unified" in tests
    assert "test_from_unified" in tests
    assert "api_key" in tests


def test_generate_tests_oauth2(connector_builder):
    """Test generation for OAuth 2.0"""
    spec = ConnectorSpec(
        name="oauth_api",
        description="OAuth API",
        api_base_url="https://api.oauth.com",
        auth_type="oauth2",
        endpoints=[],
        field_mappings={}
    )
    sample_data = {"id": "123"}
    
    tests = connector_builder.generate_tests(spec, sample_data)
    
    assert "access_token" in tests


def test_generate_tests_basic_auth(connector_builder):
    """Test generation for Basic auth"""
    spec = ConnectorSpec(
        name="basic_api",
        description="Basic API",
        api_base_url="https://api.basic.com",
        auth_type="basic",
        endpoints=[],
        field_mappings={}
    )
    sample_data = {"id": "123"}
    
    tests = connector_builder.generate_tests(spec, sample_data)
    
    assert "username" in tests
    assert "password" in tests


def test_generate_tests_sample_data(connector_builder, sample_connector_spec):
    """Test sample data inclusion in tests"""
    sample_data = {
        "id": "123",
        "email": "test@example.com",
        "full_name": "Test User"
    }
    
    tests = connector_builder.generate_tests(sample_connector_spec, sample_data)
    
    assert '"id": "123"' in tests
    assert '"email": "test@example.com"' in tests


# ============================================
# README Generation Tests
# ============================================

def test_generate_readme(connector_builder, sample_connector_spec):
    """Test README generation"""
    readme = connector_builder.generate_readme(sample_connector_spec)
    
    assert "# Test Api Connector" in readme
    assert "Test API Connector" in readme
    assert "api_key" in readme
    assert "https://api.test.com" in readme
    
    # Check field mappings table
    assert "| Unified Field | API Field | Transformation |" in readme
    assert "| `email` |" in readme


def test_generate_readme_endpoints(connector_builder, sample_connector_spec):
    """Test README includes endpoints"""
    readme = connector_builder.generate_readme(sample_connector_spec)
    
    assert "/customers" in readme
    assert "GET" in readme
    assert "POST" in readme


def test_generate_readme_auth_instructions(connector_builder):
    """Test README includes auth instructions"""
    spec = ConnectorSpec(
        name="test_api",
        description="Test",
        api_base_url="https://test.com",
        auth_type="oauth2",
        endpoints=[],
        field_mappings={}
    )
    
    readme = connector_builder.generate_readme(spec)
    
    assert "oauth2" in readme
    assert "access_token" in readme
    assert "refresh_token" in readme


def test_generate_readme_usage_example(connector_builder, sample_connector_spec):
    """Test README includes usage example"""
    readme = connector_builder.generate_readme(sample_connector_spec)
    
    assert "## Usage" in readme
    assert "from connectors.adapters" in readme
    assert "await adapter.list_customers" in readme


# ============================================
# Field Mapping Tests
# ============================================

def test_format_mappings_empty(connector_builder):
    """Test formatting empty mappings"""
    result = connector_builder._format_mappings({})
    assert result == "No mappings configured"


def test_format_mappings_with_transformations(connector_builder):
    """Test formatting mappings with transformations"""
    mappings = {
        "email": {
            "source_path": "user_email",
            "transformation": None
        },
        "phone": {
            "source_path": "contact_phone",
            "transformation": "format_phone"
        }
    }
    
    result = connector_builder._format_mappings(mappings)
    
    assert "`email`" in result
    assert "`user_email`" in result
    assert "`None`" in result
    assert "`phone`" in result
    assert "`format_phone`" in result


# ============================================
# Integration Tests
# ============================================

def test_full_connector_generation(connector_builder, sample_connector_spec):
    """Test complete connector generation workflow"""
    sample_data = {
        "id": "123",
        "email": "test@example.com",
        "full_name": "Test User",
        "phone_number": "+1-555-1234"
    }
    
    # Generate adapter
    adapter_code = connector_builder.generate_adapter_code(sample_connector_spec)
    assert "class TestApiAdapter" in adapter_code
    
    # Generate tests
    test_code = connector_builder.generate_tests(sample_connector_spec, sample_data)
    assert "test_adapter_registration" in test_code
    
    # Generate README
    readme = connector_builder.generate_readme(sample_connector_spec)
    assert "# Test Api Connector" in readme
    
    # All components should be valid Python/Markdown
    assert len(adapter_code) > 100
    assert len(test_code) > 100
    assert len(readme) > 50
