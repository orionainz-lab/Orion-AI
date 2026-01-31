"""
Tests for LLM Schema Mapper

Comprehensive test suite for AI-powered schema mapping.
"""

import pytest
from unittest.mock import Mock, AsyncMock
import json
from services.llm.schema_mapper import (
    SchemaMapper,
    MappingSuggestion,
    split_name,
    format_phone,
    extract_email_domain,
    parse_address
)


@pytest.fixture
def mock_llm_client():
    """Create mock LLM client"""
    return AsyncMock()


@pytest.fixture
def schema_mapper(mock_llm_client):
    """Create SchemaMapper instance"""
    return SchemaMapper(llm_client=mock_llm_client)


@pytest.fixture
def sample_api_response():
    """Sample API response for testing"""
    return {
        "user_id": "12345",
        "email_address": "john.doe@example.com",
        "full_name": "John Doe",
        "contact_phone": "+1-555-1234",
        "organization": "Acme Corp",
        "address": {
            "line1": "123 Main St",
            "line2": "Apt 4B",
            "city_name": "San Francisco",
            "state_code": "CA",
            "zip": "94105",
            "country_code": "US"
        },
        "tags": "vip,enterprise",
        "created_at": "2026-01-15T10:30:00Z"
    }


@pytest.fixture
def sample_llm_mapping_response():
    """Sample LLM response with mappings"""
    return {
        "customer_email": {
            "source_path": "email_address",
            "confidence": 0.99,
            "transformation": None,
            "reasoning": "Direct email field match"
        },
        "customer_name": {
            "source_path": "full_name",
            "confidence": 0.95,
            "transformation": None,
            "reasoning": "Clear full name field"
        },
        "customer_phone": {
            "source_path": "contact_phone",
            "confidence": 0.90,
            "transformation": "format_phone",
            "reasoning": "Phone field needs E.164 formatting"
        },
        "customer_company": {
            "source_path": "organization",
            "confidence": 0.85,
            "transformation": None,
            "reasoning": "Organization likely represents company"
        },
        "billing_address_street": {
            "source_path": "address.line1",
            "confidence": 0.95,
            "transformation": None,
            "reasoning": "Primary address line"
        },
        "billing_address_city": {
            "source_path": "address.city_name",
            "confidence": 0.90,
            "transformation": None,
            "reasoning": "City field mapped"
        }
    }


# ============================================
# Model Tests
# ============================================

def test_mapping_suggestion_model():
    """Test MappingSuggestion model validation"""
    suggestion = MappingSuggestion(
        source_path="email",
        confidence=0.95,
        transformation=None,
        reasoning="Direct match"
    )
    
    assert suggestion.source_path == "email"
    assert suggestion.confidence == 0.95
    assert suggestion.transformation is None
    assert suggestion.reasoning == "Direct match"


def test_mapping_suggestion_with_transformation():
    """Test MappingSuggestion with transformation"""
    suggestion = MappingSuggestion(
        source_path="phone",
        confidence=0.85,
        transformation="format_phone",
        reasoning="Needs formatting"
    )
    
    assert suggestion.transformation == "format_phone"


# ============================================
# Schema Discovery Tests
# ============================================

@pytest.mark.asyncio
async def test_discover_schema_success(schema_mapper, sample_api_response, sample_llm_mapping_response):
    """Test successful schema discovery"""
    # Mock LLM response
    mock_message = Mock()
    mock_message.content = [Mock(text=json.dumps(sample_llm_mapping_response))]
    schema_mapper.llm.messages.create.return_value = mock_message
    
    result = await schema_mapper.discover_schema(sample_api_response)
    
    assert isinstance(result, dict)
    assert "customer_email" in result
    assert isinstance(result["customer_email"], MappingSuggestion)
    assert result["customer_email"].source_path == "email_address"
    assert result["customer_email"].confidence == 0.99


@pytest.mark.asyncio
async def test_discover_schema_with_api_docs(schema_mapper, sample_api_response):
    """Test schema discovery with API documentation"""
    mock_message = Mock()
    mock_message.content = [Mock(text='{"field": {"source_path": "test", "confidence": 0.9, "transformation": null, "reasoning": "test"}}')]
    schema_mapper.llm.messages.create.return_value = mock_message
    
    api_docs = "API Documentation: email_address field contains user email"
    
    result = await schema_mapper.discover_schema(
        sample_api_response,
        api_docs=api_docs
    )
    
    # Verify API docs were included in prompt
    call_args = schema_mapper.llm.messages.create.call_args
    prompt = call_args[1]["messages"][0]["content"]
    assert "Additional API Documentation" in prompt


@pytest.mark.asyncio
async def test_discover_schema_with_markdown_json(schema_mapper, sample_api_response):
    """Test handling LLM response with markdown-wrapped JSON"""
    mock_message = Mock()
    # LLM sometimes wraps JSON in markdown code blocks
    mock_message.content = [Mock(text='```json\n{"field": {"source_path": "test", "confidence": 0.9, "transformation": null, "reasoning": "test"}}\n```')]
    schema_mapper.llm.messages.create.return_value = mock_message
    
    result = await schema_mapper.discover_schema(sample_api_response)
    
    assert isinstance(result, dict)
    assert "field" in result


@pytest.mark.asyncio
async def test_discover_schema_llm_error(schema_mapper, sample_api_response):
    """Test schema discovery handles LLM errors"""
    schema_mapper.llm.messages.create.side_effect = Exception("LLM API error")
    
    with pytest.raises(ValueError, match="LLM schema mapping failed"):
        await schema_mapper.discover_schema(sample_api_response)


@pytest.mark.asyncio
async def test_discover_schema_invalid_json(schema_mapper, sample_api_response):
    """Test schema discovery handles invalid JSON"""
    mock_message = Mock()
    mock_message.content = [Mock(text="Not valid JSON at all")]
    schema_mapper.llm.messages.create.return_value = mock_message
    
    with pytest.raises(ValueError, match="LLM schema mapping failed"):
        await schema_mapper.discover_schema(sample_api_response)


# ============================================
# Transformation Code Generation Tests
# ============================================

@pytest.mark.asyncio
async def test_generate_transformation_code(schema_mapper):
    """Test transformation code generation"""
    mock_message = Mock()
    mock_message.content = [Mock(text='''```python
def transform_phone(value):
    import re
    digits = re.sub(r'\\D', '', value)
    return f"+1{digits}"
```''')]
    schema_mapper.llm.messages.create.return_value = mock_message
    
    code = await schema_mapper.generate_transformation_code(
        field_name="phone",
        source_field="contact_phone",
        sample_values=["+1-555-1234", "555-5678"],
        target_format="E.164 format (+1XXXXXXXXXX)"
    )
    
    assert "def transform_phone" in code
    assert "import re" in code


@pytest.mark.asyncio
async def test_generate_transformation_code_clean_output(schema_mapper):
    """Test code generation strips markdown"""
    mock_message = Mock()
    mock_message.content = [Mock(text='Here is the code:\n```python\ndef transform_field(value):\n    return value.upper()\n```\nHope this helps!')]
    schema_mapper.llm.messages.create.return_value = mock_message
    
    code = await schema_mapper.generate_transformation_code(
        field_name="field",
        source_field="src",
        sample_values=["test"],
        target_format="uppercase"
    )
    
    assert "def transform_field" in code
    assert "Here is the code" not in code
    assert "Hope this helps" not in code


# ============================================
# Mapping Validation Tests
# ============================================

@pytest.mark.asyncio
async def test_validate_mapping_all_valid(schema_mapper, sample_api_response):
    """Test validating all valid mappings"""
    mapping = {
        "email": MappingSuggestion(
            source_path="email_address",
            confidence=0.95,
            reasoning="test"
        ),
        "name": MappingSuggestion(
            source_path="full_name",
            confidence=0.90,
            reasoning="test"
        ),
        "phone": MappingSuggestion(
            source_path="contact_phone",
            confidence=0.85,
            reasoning="test"
        )
    }
    
    results = await schema_mapper.validate_mapping(mapping, sample_api_response)
    
    assert results["email"] is True
    assert results["name"] is True
    assert results["phone"] is True


@pytest.mark.asyncio
async def test_validate_mapping_some_invalid(schema_mapper, sample_api_response):
    """Test validating with some invalid mappings"""
    mapping = {
        "email": MappingSuggestion(
            source_path="email_address",
            confidence=0.95,
            reasoning="test"
        ),
        "invalid_field": MappingSuggestion(
            source_path="nonexistent_field",
            confidence=0.50,
            reasoning="test"
        )
    }
    
    results = await schema_mapper.validate_mapping(mapping, sample_api_response)
    
    assert results["email"] is True
    assert results["invalid_field"] is False


@pytest.mark.asyncio
async def test_validate_mapping_nested_path(schema_mapper, sample_api_response):
    """Test validating nested field paths"""
    mapping = {
        "city": MappingSuggestion(
            source_path="address.city_name",
            confidence=0.90,
            reasoning="test"
        ),
        "invalid_nested": MappingSuggestion(
            source_path="address.invalid_field",
            confidence=0.50,
            reasoning="test"
        )
    }
    
    results = await schema_mapper.validate_mapping(mapping, sample_api_response)
    
    assert results["city"] is True
    assert results["invalid_nested"] is False


# ============================================
# Apply Mapping Tests
# ============================================

def test_apply_mapping_simple(schema_mapper, sample_api_response):
    """Test applying simple field mappings"""
    mapping = {
        "email": MappingSuggestion(
            source_path="email_address",
            confidence=0.95,
            reasoning="test"
        ),
        "name": MappingSuggestion(
            source_path="full_name",
            confidence=0.90,
            reasoning="test"
        )
    }
    
    result = schema_mapper.apply_mapping(sample_api_response, mapping)
    
    assert result["email"] == "john.doe@example.com"
    assert result["name"] == "John Doe"


def test_apply_mapping_nested(schema_mapper, sample_api_response):
    """Test applying nested field mappings"""
    mapping = {
        "city": MappingSuggestion(
            source_path="address.city_name",
            confidence=0.90,
            reasoning="test"
        ),
        "state": MappingSuggestion(
            source_path="address.state_code",
            confidence=0.90,
            reasoning="test"
        )
    }
    
    result = schema_mapper.apply_mapping(sample_api_response, mapping)
    
    assert result["city"] == "San Francisco"
    assert result["state"] == "CA"


def test_apply_mapping_missing_field(schema_mapper, sample_api_response):
    """Test applying mapping with missing source field"""
    mapping = {
        "email": MappingSuggestion(
            source_path="email_address",
            confidence=0.95,
            reasoning="test"
        ),
        "missing": MappingSuggestion(
            source_path="nonexistent_field",
            confidence=0.50,
            reasoning="test"
        )
    }
    
    result = schema_mapper.apply_mapping(sample_api_response, mapping)
    
    assert result["email"] == "john.doe@example.com"
    assert "missing" not in result  # Missing field should be skipped


# ============================================
# Transformation Function Tests
# ============================================

def test_split_name_full():
    """Test splitting full name"""
    first, last = split_name("John Doe")
    assert first == "John"
    assert last == "Doe"


def test_split_name_single():
    """Test splitting single name"""
    first, last = split_name("Madonna")
    assert first == "Madonna"
    assert last == ""


def test_split_name_multiple_parts():
    """Test splitting name with multiple parts"""
    first, last = split_name("John Michael Doe")
    assert first == "John"
    assert last == "Michael Doe"


def test_format_phone_10_digit():
    """Test formatting 10-digit US phone"""
    result = format_phone("5551234567")
    assert result == "+15551234567"


def test_format_phone_11_digit():
    """Test formatting 11-digit phone with country code"""
    result = format_phone("15551234567")
    assert result == "+15551234567"


def test_format_phone_with_formatting():
    """Test formatting phone with existing formatting"""
    result = format_phone("(555) 123-4567")
    assert result == "+15551234567"


def test_format_phone_already_e164():
    """Test phone already in E.164 format"""
    result = format_phone("+15551234567")
    assert result == "+15551234567"


def test_extract_email_domain():
    """Test extracting domain from email"""
    domain = extract_email_domain("john.doe@example.com")
    assert domain == "example.com"


def test_extract_email_domain_subdomain():
    """Test extracting domain with subdomain"""
    domain = extract_email_domain("john@mail.example.com")
    assert domain == "mail.example.com"


def test_extract_email_domain_invalid():
    """Test extracting domain from invalid email"""
    domain = extract_email_domain("not-an-email")
    assert domain == ""


def test_parse_address():
    """Test parsing address string"""
    result = parse_address("123 Main St, San Francisco, CA 94105")
    
    assert isinstance(result, dict)
    assert result["street"] == "123 Main St, San Francisco, CA 94105"
    assert result["city"] == ""  # Simple parser doesn't split
    assert result["country"] == "US"


# ============================================
# Confidence Scoring Tests
# ============================================

@pytest.mark.asyncio
async def test_high_confidence_exact_match(schema_mapper):
    """Test high confidence for exact field name matches"""
    mock_message = Mock()
    mock_message.content = [Mock(text='{"email": {"source_path": "email", "confidence": 1.0, "transformation": null, "reasoning": "Exact match"}}')]
    schema_mapper.llm.messages.create.return_value = mock_message
    
    result = await schema_mapper.discover_schema({"email": "test@example.com"})
    
    assert result["email"].confidence == 1.0


@pytest.mark.asyncio
async def test_lower_confidence_guess(schema_mapper):
    """Test lower confidence for field guesses"""
    mock_message = Mock()
    mock_message.content = [Mock(text='{"company": {"source_path": "org_name", "confidence": 0.6, "transformation": null, "reasoning": "Guessing organization is company"}}')]
    schema_mapper.llm.messages.create.return_value = mock_message
    
    result = await schema_mapper.discover_schema({"org_name": "Acme Corp"})
    
    assert result["company"].confidence == 0.6
