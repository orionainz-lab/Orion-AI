"""
Slack Adapter

Communication connector for notifications, events, and workflows.
"""

from typing import List, Dict, Any, Optional
from connectors.adapters.base import (
    BaseAdapter,
    AdapterConfig,
    AdapterCapability
)
from connectors.adapters.registry import register_adapter
from connectors.adapters.exceptions import (
    AuthenticationError,
    APIError
)


@register_adapter("slack")
class SlackAdapter(BaseAdapter):
    """
    Slack workspace adapter.
    
    Supports:
    - Send messages to channels
    - Interactive components (buttons, modals)
    - Event subscriptions
    - File uploads
    - User directory sync
    
    Docs: https://api.slack.com/
    """
    
    name = "slack"
    version = "1.0.0"
    capabilities = [
        AdapterCapability.WEBHOOK,
        AdapterCapability.STREAMING
    ]
    
    BASE_URL = "https://slack.com/api"
    
    def _get_auth_headers(self) -> dict[str, str]:
        """Get Slack bot token headers"""
        bot_token = self.credentials.get("bot_token", "")
        if not bot_token:
            raise AuthenticationError("Slack bot token not provided")
        
        return {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json"
        }
    
    async def send_message(
        self,
        channel: str,
        text: str,
        blocks: Optional[List[Dict[str, Any]]] = None,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send message to Slack channel.
        
        Args:
            channel: Channel ID or name (e.g., "#general", "C1234567890")
            text: Message text (markdown supported)
            blocks: Optional Block Kit blocks for rich formatting
            thread_ts: Optional thread timestamp to reply in thread
        
        Returns:
            {
                "ok": true,
                "channel": "C1234567890",
                "ts": "1503435956.000247",
                "message": {...}
            }
        """
        if not self._client:
            await self.connect()
        
        payload = {
            "channel": channel,
            "text": text
        }
        
        if blocks:
            payload["blocks"] = blocks
        
        if thread_ts:
            payload["thread_ts"] = thread_ts
        
        try:
            response = await self._client.post(
                f"{self.BASE_URL}/chat.postMessage",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok"):
                raise APIError(f"Slack API error: {data.get('error', 'Unknown error')}")
            
            return data
        
        except Exception as e:
            raise APIError(
                f"Failed to send message: {str(e)}",
                status_code=getattr(e, "status_code", None)
            )
    
    async def send_notification(
        self,
        channel: str,
        title: str,
        message: str,
        color: str = "#36a64f",  # Green
        fields: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Send formatted notification with attachment.
        
        Args:
            channel: Channel ID or name
            title: Notification title
            message: Main message text
            color: Sidebar color (hex or "good"/"warning"/"danger")
            fields: Optional list of {"title": "...", "value": "...", "short": true}
        
        Returns:
            Slack API response
        """
        attachment = {
            "color": color,
            "title": title,
            "text": message,
            "footer": "Orion AI Platform",
            "ts": int(__import__('time').time())
        }
        
        if fields:
            attachment["fields"] = fields
        
        return await self.send_message(
            channel=channel,
            text=title,  # Fallback text
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{title}*\n{message}"
                    }
                }
            ]
        )
    
    async def send_error_alert(
        self,
        channel: str,
        error_title: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send error alert to channel.
        
        Args:
            channel: Channel ID or name
            error_title: Error title
            error_message: Error description
            details: Optional error details (connector, user, etc.)
        
        Returns:
            Slack API response
        """
        fields = []
        if details:
            for key, value in details.items():
                fields.append({
                    "title": key.replace("_", " ").title(),
                    "value": str(value),
                    "short": True
                })
        
        return await self.send_notification(
            channel=channel,
            title=f"🚨 {error_title}",
            message=error_message,
            color="danger",
            fields=fields if fields else None
        )
    
    async def send_success_alert(
        self,
        channel: str,
        title: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send success notification.
        
        Args:
            channel: Channel ID or name
            title: Success title
            message: Success message
            details: Optional details
        
        Returns:
            Slack API response
        """
        fields = []
        if details:
            for key, value in details.items():
                fields.append({
                    "title": key.replace("_", " ").title(),
                    "value": str(value),
                    "short": True
                })
        
        return await self.send_notification(
            channel=channel,
            title=f"✅ {title}",
            message=message,
            color="good",
            fields=fields if fields else None
        )
    
    async def send_approval_request(
        self,
        channel: str,
        title: str,
        description: str,
        approve_value: str = "approve",
        reject_value: str = "reject"
    ) -> Dict[str, Any]:
        """
        Send interactive approval request with buttons.
        
        Args:
            channel: Channel ID or name
            title: Request title
            description: Request description
            approve_value: Value to send when approved
            reject_value: Value to send when rejected
        
        Returns:
            Slack API response
        """
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{title}*\n{description}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Approve"
                        },
                        "style": "primary",
                        "value": approve_value,
                        "action_id": "approve_action"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Reject"
                        },
                        "style": "danger",
                        "value": reject_value,
                        "action_id": "reject_action"
                    }
                ]
            }
        ]
        
        return await self.send_message(
            channel=channel,
            text=title,
            blocks=blocks
        )
    
    async def upload_file(
        self,
        channels: List[str],
        file_content: bytes,
        filename: str,
        title: Optional[str] = None,
        initial_comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload file to Slack channels.
        
        Args:
            channels: List of channel IDs
            file_content: File bytes
            filename: File name
            title: Optional file title
            initial_comment: Optional comment with file
        
        Returns:
            Slack API response
        """
        if not self._client:
            await self.connect()
        
        payload = {
            "channels": ",".join(channels),
            "filename": filename
        }
        
        if title:
            payload["title"] = title
        
        if initial_comment:
            payload["initial_comment"] = initial_comment
        
        try:
            # Use files.upload (legacy) or files.uploadV2 for newer apps
            response = await self._client.post(
                f"{self.BASE_URL}/files.upload",
                data=payload,
                files={"file": (filename, file_content)}
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok"):
                raise APIError(f"Slack API error: {data.get('error', 'Unknown error')}")
            
            return data
        
        except Exception as e:
            raise APIError(
                f"Failed to upload file: {str(e)}",
                status_code=getattr(e, "status_code", None)
            )
    
    async def list_channels(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List public channels in workspace.
        
        Args:
            limit: Max channels to fetch
        
        Returns:
            List of channel objects
        """
        if not self._client:
            await self.connect()
        
        try:
            response = await self._client.get(
                f"{self.BASE_URL}/conversations.list",
                params={
                    "limit": min(limit, 1000),
                    "exclude_archived": True
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok"):
                raise APIError(f"Slack API error: {data.get('error', 'Unknown error')}")
            
            return data.get("channels", [])
        
        except Exception as e:
            raise APIError(
                f"Failed to list channels: {str(e)}",
                status_code=getattr(e, "status_code", None)
            )
    
    async def list_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List users in workspace.
        
        Args:
            limit: Max users to fetch
        
        Returns:
            List of user objects
        """
        if not self._client:
            await self.connect()
        
        try:
            response = await self._client.get(
                f"{self.BASE_URL}/users.list",
                params={"limit": min(limit, 1000)}
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok"):
                raise APIError(f"Slack API error: {data.get('error', 'Unknown error')}")
            
            return data.get("members", [])
        
        except Exception as e:
            raise APIError(
                f"Failed to list users: {str(e)}",
                status_code=getattr(e, "status_code", None)
            )
    
    async def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming Slack event.
        
        Args:
            event_data: Event payload from Slack
        
        Returns:
            Processed event info
        """
        event_type = event_data.get("type")
        
        if event_type == "url_verification":
            # Respond to Slack's challenge
            return {"challenge": event_data.get("challenge")}
        
        elif event_type == "event_callback":
            event = event_data.get("event", {})
            return {
                "event_type": event.get("type"),
                "user": event.get("user"),
                "channel": event.get("channel"),
                "text": event.get("text"),
                "ts": event.get("ts")
            }
        
        else:
            return {"event_type": event_type}
