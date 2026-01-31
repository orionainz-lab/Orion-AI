"""
Tests for Slack Adapter

Comprehensive test suite for Slack integration.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from connectors.adapters.slack import SlackAdapter
from connectors.adapters.base import AdapterConfig, AdapterCapability
from connectors.adapters.exceptions import AuthenticationError, APIError


@pytest.fixture
def slack_config():
    """Create Slack adapter configuration"""
    return AdapterConfig(
        credentials={
            "bot_token": "xoxb-test-token-123456"
        }
    )


@pytest.fixture
def adapter(slack_config):
    """Create Slack adapter instance"""
    return SlackAdapter(config=slack_config)


@pytest.fixture
def sample_channel_data():
    """Sample Slack channel data"""
    return {
        "id": "C1234567890",
        "name": "general",
        "is_channel": True,
        "is_archived": False,
        "is_member": True
    }


@pytest.fixture
def sample_user_data():
    """Sample Slack user data"""
    return {
        "id": "U1234567890",
        "name": "john.doe",
        "real_name": "John Doe",
        "profile": {
            "email": "john@example.com",
            "display_name": "John"
        }
    }


# ============================================
# Registration & Configuration Tests
# ============================================

def test_adapter_registration(adapter):
    """Test adapter is registered with correct name"""
    assert adapter.name == "slack"
    assert SlackAdapter.name == "slack"


def test_adapter_version(adapter):
    """Test adapter version"""
    assert adapter.version == "1.0.0"
    assert SlackAdapter.version == "1.0.0"


def test_adapter_capabilities(adapter):
    """Test adapter capabilities"""
    expected_capabilities = [
        AdapterCapability.WEBHOOK,
        AdapterCapability.STREAMING
    ]
    assert SlackAdapter.capabilities == expected_capabilities


def test_base_url(adapter):
    """Test Slack API base URL"""
    assert adapter.BASE_URL == "https://slack.com/api"


# ============================================
# Authentication Tests
# ============================================

def test_auth_headers_success(adapter):
    """Test successful auth header generation"""
    headers = adapter._get_auth_headers()
    
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer xoxb-test-token-123456"
    assert headers["Content-Type"] == "application/json"


def test_auth_headers_missing_token():
    """Test auth headers fail without bot token"""
    config = AdapterConfig(credentials={})
    adapter = SlackAdapter(config=config)
    
    with pytest.raises(AuthenticationError, match="bot token not provided"):
        adapter._get_auth_headers()


# ============================================
# Send Message Tests
# ============================================

@pytest.mark.asyncio
async def test_send_message_basic(adapter):
    """Test sending basic message"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": True,
        "channel": "C1234567890",
        "ts": "1503435956.000247",
        "message": {"text": "Test message"}
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    result = await adapter.send_message(
        channel="#general",
        text="Test message"
    )
    
    assert result["ok"] is True
    assert result["channel"] == "C1234567890"
    mock_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_with_blocks(adapter):
    """Test sending message with Block Kit blocks"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": True,
        "channel": "C1234567890",
        "ts": "1503435956.000247"
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Bold text* and _italic text_"
            }
        }
    ]
    
    result = await adapter.send_message(
        channel="#general",
        text="Fallback text",
        blocks=blocks
    )
    
    assert result["ok"] is True
    call_args = mock_client.post.call_args
    payload = call_args[1]["json"]
    assert "blocks" in payload


@pytest.mark.asyncio
async def test_send_message_in_thread(adapter):
    """Test sending message in thread"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": True,
        "channel": "C1234567890",
        "ts": "1503435957.000248",
        "thread_ts": "1503435956.000247"
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    result = await adapter.send_message(
        channel="#general",
        text="Thread reply",
        thread_ts="1503435956.000247"
    )
    
    assert result["ok"] is True
    call_args = mock_client.post.call_args
    payload = call_args[1]["json"]
    assert payload["thread_ts"] == "1503435956.000247"


@pytest.mark.asyncio
async def test_send_message_api_error(adapter):
    """Test send message handles Slack API errors"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": False,
        "error": "channel_not_found"
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    with pytest.raises(APIError, match="Slack API error"):
        await adapter.send_message(channel="#nonexistent", text="Test")


# ============================================
# Notification Tests
# ============================================

@pytest.mark.asyncio
async def test_send_notification(adapter):
    """Test sending formatted notification"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {"ok": True, "ts": "1234567890.123456"}
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    result = await adapter.send_notification(
        channel="#alerts",
        title="System Alert",
        message="Database backup completed",
        color="good"
    )
    
    assert result["ok"] is True
    mock_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_send_notification_with_fields(adapter):
    """Test notification with fields"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {"ok": True, "ts": "1234567890.123456"}
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    fields = [
        {"title": "Duration", "value": "30 seconds", "short": True},
        {"title": "Records", "value": "1,234", "short": True}
    ]
    
    result = await adapter.send_notification(
        channel="#alerts",
        title="Sync Complete",
        message="Salesforce sync finished",
        fields=fields
    )
    
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_send_error_alert(adapter):
    """Test sending error alert"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {"ok": True, "ts": "1234567890.123456"}
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    details = {
        "connector": "Salesforce",
        "error_code": "AUTH_FAILED",
        "timestamp": "2026-01-31T12:00:00Z"
    }
    
    result = await adapter.send_error_alert(
        channel="#errors",
        error_title="Authentication Failed",
        error_message="Could not connect to Salesforce",
        details=details
    )
    
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_send_success_alert(adapter):
    """Test sending success alert"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {"ok": True, "ts": "1234567890.123456"}
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    details = {
        "records_synced": "1,234",
        "duration": "45 seconds"
    }
    
    result = await adapter.send_success_alert(
        channel="#alerts",
        title="Sync Complete",
        message="All records synced successfully",
        details=details
    )
    
    assert result["ok"] is True


# ============================================
# Approval Request Tests
# ============================================

@pytest.mark.asyncio
async def test_send_approval_request(adapter):
    """Test sending approval request with buttons"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {"ok": True, "ts": "1234567890.123456"}
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    result = await adapter.send_approval_request(
        channel="#approvals",
        title="Workflow Approval Required",
        description="Please approve the data sync workflow",
        approve_value="workflow_123_approve",
        reject_value="workflow_123_reject"
    )
    
    assert result["ok"] is True
    call_args = mock_client.post.call_args
    payload = call_args[1]["json"]
    assert "blocks" in payload
    # Check for actions block with buttons
    has_actions = any(block.get("type") == "actions" for block in payload["blocks"])
    assert has_actions


# ============================================
# File Upload Tests
# ============================================

@pytest.mark.asyncio
async def test_upload_file(adapter):
    """Test file upload"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": True,
        "file": {
            "id": "F1234567890",
            "name": "report.pdf"
        }
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    file_content = b"Test file content"
    
    result = await adapter.upload_file(
        channels=["C1234567890"],
        file_content=file_content,
        filename="test.txt",
        title="Test File",
        initial_comment="Here's the report"
    )
    
    assert result["ok"] is True
    assert result["file"]["id"] == "F1234567890"


@pytest.mark.asyncio
async def test_upload_file_error(adapter):
    """Test file upload error handling"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": False,
        "error": "file_too_large"
    }
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    adapter._client = mock_client
    
    with pytest.raises(APIError, match="Slack API error"):
        await adapter.upload_file(
            channels=["C1234567890"],
            file_content=b"content",
            filename="test.txt"
        )


# ============================================
# Channel Listing Tests
# ============================================

@pytest.mark.asyncio
async def test_list_channels(adapter, sample_channel_data):
    """Test listing channels"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": True,
        "channels": [
            sample_channel_data,
            {
                "id": "C0987654321",
                "name": "random",
                "is_channel": True,
                "is_archived": False
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    adapter._client = mock_client
    
    channels = await adapter.list_channels(limit=100)
    
    assert len(channels) == 2
    assert channels[0]["id"] == "C1234567890"
    assert channels[0]["name"] == "general"


@pytest.mark.asyncio
async def test_list_channels_limit(adapter):
    """Test list channels respects limit"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {"ok": True, "channels": []}
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    adapter._client = mock_client
    
    await adapter.list_channels(limit=2000)
    
    call_args = mock_client.get.call_args
    params = call_args[1]["params"]
    assert params["limit"] == 1000  # Should cap at 1000


@pytest.mark.asyncio
async def test_list_channels_error(adapter):
    """Test list channels error handling"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": False,
        "error": "invalid_auth"
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    adapter._client = mock_client
    
    with pytest.raises(APIError, match="Slack API error"):
        await adapter.list_channels()


# ============================================
# User Listing Tests
# ============================================

@pytest.mark.asyncio
async def test_list_users(adapter, sample_user_data):
    """Test listing users"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": True,
        "members": [
            sample_user_data,
            {
                "id": "U0987654321",
                "name": "jane.smith",
                "real_name": "Jane Smith"
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    adapter._client = mock_client
    
    users = await adapter.list_users(limit=100)
    
    assert len(users) == 2
    assert users[0]["id"] == "U1234567890"
    assert users[0]["name"] == "john.doe"


@pytest.mark.asyncio
async def test_list_users_error(adapter):
    """Test list users error handling"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": False,
        "error": "not_authed"
    }
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    adapter._client = mock_client
    
    with pytest.raises(APIError, match="Slack API error"):
        await adapter.list_users()


# ============================================
# Event Handling Tests
# ============================================

@pytest.mark.asyncio
async def test_handle_event_url_verification(adapter):
    """Test handling URL verification challenge"""
    event_data = {
        "type": "url_verification",
        "challenge": "test_challenge_string_123"
    }
    
    result = await adapter.handle_event(event_data)
    
    assert result["challenge"] == "test_challenge_string_123"


@pytest.mark.asyncio
async def test_handle_event_message(adapter):
    """Test handling message event"""
    event_data = {
        "type": "event_callback",
        "event": {
            "type": "message",
            "user": "U1234567890",
            "channel": "C1234567890",
            "text": "Hello world",
            "ts": "1503435956.000247"
        }
    }
    
    result = await adapter.handle_event(event_data)
    
    assert result["event_type"] == "message"
    assert result["user"] == "U1234567890"
    assert result["channel"] == "C1234567890"
    assert result["text"] == "Hello world"


@pytest.mark.asyncio
async def test_handle_event_reaction(adapter):
    """Test handling reaction event"""
    event_data = {
        "type": "event_callback",
        "event": {
            "type": "reaction_added",
            "user": "U1234567890",
            "item": {
                "type": "message",
                "channel": "C1234567890",
                "ts": "1503435956.000247"
            },
            "reaction": "thumbsup"
        }
    }
    
    result = await adapter.handle_event(event_data)
    
    assert result["event_type"] == "reaction_added"
    assert result["user"] == "U1234567890"


@pytest.mark.asyncio
async def test_handle_event_unknown_type(adapter):
    """Test handling unknown event type"""
    event_data = {
        "type": "unknown_event_type"
    }
    
    result = await adapter.handle_event(event_data)
    
    assert result["event_type"] == "unknown_event_type"


# ============================================
# Integration Tests
# ============================================

@pytest.mark.asyncio
async def test_send_and_reply_in_thread(adapter):
    """Test sending message and replying in thread"""
    mock_client = AsyncMock()
    
    # First message
    mock_response1 = Mock()
    mock_response1.json.return_value = {
        "ok": True,
        "ts": "1503435956.000247"
    }
    mock_response1.raise_for_status = Mock()
    
    # Thread reply
    mock_response2 = Mock()
    mock_response2.json.return_value = {
        "ok": True,
        "ts": "1503435957.000248",
        "thread_ts": "1503435956.000247"
    }
    mock_response2.raise_for_status = Mock()
    
    mock_client.post.side_effect = [mock_response1, mock_response2]
    adapter._client = mock_client
    
    # Send initial message
    result1 = await adapter.send_message(
        channel="#general",
        text="Main message"
    )
    parent_ts = result1["ts"]
    
    # Reply in thread
    result2 = await adapter.send_message(
        channel="#general",
        text="Thread reply",
        thread_ts=parent_ts
    )
    
    assert result2["thread_ts"] == parent_ts
