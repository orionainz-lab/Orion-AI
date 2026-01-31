"""
Phase 6C: Enterprise Monitoring - Alert Manager
Manages alerting rules and notifications.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import httpx
from supabase import Client


class AlertType(str, Enum):
    """Alert types"""
    THRESHOLD = "threshold"
    ANOMALY = "anomaly"
    ABSENCE = "absence"


class Severity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alert definition"""
    id: str
    org_id: str
    alert_name: str
    alert_type: AlertType
    metric_name: str
    condition: Dict[str, Any]
    severity: Severity
    notification_channels: List[str]
    enabled: bool
    last_triggered: Optional[datetime]


@dataclass
class AlertEvent:
    """Alert event/trigger"""
    alert_id: str
    org_id: str
    metric_name: str
    metric_value: float
    condition_met: str
    severity: Severity
    timestamp: datetime


class AlertManager:
    """
    Manages alerting rules and notifications.
    
    Features:
    - Threshold-based alerts
    - Anomaly detection alerts
    - Absence alerts (no data)
    - Multiple notification channels (email, Slack, webhook)
    - Alert history
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
    
    # ========================================
    # ALERT MANAGEMENT
    # ========================================
    
    async def create_alert(
        self,
        org_id: str,
        alert_name: str,
        alert_type: AlertType,
        metric_name: str,
        condition: Dict[str, Any],
        severity: Severity,
        notification_channels: List[str],
        enabled: bool = True
    ) -> Alert:
        """Create alert rule"""
        alert_data = {
            "org_id": org_id,
            "alert_name": alert_name,
            "alert_type": alert_type.value,
            "metric_name": metric_name,
            "condition": condition,
            "severity": severity.value,
            "notification_channels": notification_channels,
            "enabled": enabled
        }
        
        response = self.client.table("alerts").insert(alert_data).execute()
        
        if not response.data:
            raise Exception("Failed to create alert")
        
        return self._dict_to_alert(response.data[0])
    
    async def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID"""
        response = self.client.table("alerts").select("*").eq("id", alert_id).execute()
        
        if not response.data:
            return None
        
        return self._dict_to_alert(response.data[0])
    
    async def list_alerts(
        self,
        org_id: str,
        enabled_only: bool = False
    ) -> List[Alert]:
        """List alerts for organization"""
        query = self.client.table("alerts").select("*").eq("org_id", org_id)
        
        if enabled_only:
            query = query.eq("enabled", True)
        
        response = query.order("alert_name").execute()
        
        if not response.data:
            return []
        
        return [self._dict_to_alert(a) for a in response.data]
    
    async def update_alert(self, alert_id: str, **updates) -> Alert:
        """Update alert fields"""
        response = self.client.table("alerts").update(updates).eq("id", alert_id).execute()
        
        if not response.data:
            raise Exception(f"Failed to update alert: {alert_id}")
        
        return self._dict_to_alert(response.data[0])
    
    async def delete_alert(self, alert_id: str) -> bool:
        """Delete alert"""
        response = self.client.table("alerts").delete().eq("id", alert_id).execute()
        return bool(response.data)
    
    # ========================================
    # METRIC MONITORING
    # ========================================
    
    async def record_metric(
        self,
        org_id: str,
        metric_name: str,
        metric_value: float,
        metric_type: str = "gauge",
        tags: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a custom metric"""
        self.client.table("custom_metrics").insert({
            "org_id": org_id,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "metric_type": metric_type,
            "tags": tags or {}
        }).execute()
    
    async def get_metric_value(
        self,
        org_id: str,
        metric_name: str,
        minutes: int = 5
    ) -> Optional[float]:
        """Get latest metric value"""
        start_time = datetime.now() - timedelta(minutes=minutes)
        
        response = self.client.table("custom_metrics").select("metric_value").eq(
            "org_id", org_id
        ).eq("metric_name", metric_name).gte(
            "created_at", start_time.isoformat()
        ).order("created_at", desc=True).limit(1).execute()
        
        if not response.data:
            return None
        
        return float(response.data[0]["metric_value"])
    
    # ========================================
    # ALERT EVALUATION
    # ========================================
    
    async def evaluate_alerts(self, org_id: str) -> List[AlertEvent]:
        """Evaluate all alerts for organization"""
        alerts = await self.list_alerts(org_id, enabled_only=True)
        triggered_alerts = []
        
        for alert in alerts:
            triggered = await self._evaluate_alert(alert)
            
            if triggered:
                triggered_alerts.append(triggered)
                
                # Send notifications
                await self._send_notifications(alert, triggered)
                
                # Update last_triggered
                await self.update_alert(alert.id, last_triggered=datetime.now().isoformat())
        
        return triggered_alerts
    
    async def _evaluate_alert(self, alert: Alert) -> Optional[AlertEvent]:
        """Evaluate single alert"""
        if alert.alert_type == AlertType.THRESHOLD:
            return await self._evaluate_threshold_alert(alert)
        elif alert.alert_type == AlertType.ANOMALY:
            return await self._evaluate_anomaly_alert(alert)
        elif alert.alert_type == AlertType.ABSENCE:
            return await self._evaluate_absence_alert(alert)
        
        return None
    
    async def _evaluate_threshold_alert(self, alert: Alert) -> Optional[AlertEvent]:
        """Evaluate threshold alert"""
        # Get current metric value
        metric_value = await self.get_metric_value(alert.org_id, alert.metric_name)
        
        if metric_value is None:
            return None
        
        # Check condition
        operator = alert.condition.get("operator")
        threshold = alert.condition.get("value")
        
        triggered = False
        
        if operator == ">":
            triggered = metric_value > threshold
        elif operator == ">=":
            triggered = metric_value >= threshold
        elif operator == "<":
            triggered = metric_value < threshold
        elif operator == "<=":
            triggered = metric_value <= threshold
        elif operator == "==":
            triggered = metric_value == threshold
        
        if triggered:
            return AlertEvent(
                alert_id=alert.id,
                org_id=alert.org_id,
                metric_name=alert.metric_name,
                metric_value=metric_value,
                condition_met=f"{metric_value} {operator} {threshold}",
                severity=alert.severity,
                timestamp=datetime.now()
            )
        
        return None
    
    async def _evaluate_anomaly_alert(self, alert: Alert) -> Optional[AlertEvent]:
        """Evaluate anomaly detection alert"""
        # TODO: Implement anomaly detection (statistical analysis)
        # For now, placeholder
        return None
    
    async def _evaluate_absence_alert(self, alert: Alert) -> Optional[AlertEvent]:
        """Evaluate absence alert (no data)"""
        # Check if metric has been updated recently
        metric_value = await self.get_metric_value(
            alert.org_id,
            alert.metric_name,
            minutes=alert.condition.get("absence_minutes", 15)
        )
        
        if metric_value is None:
            # No data found - trigger alert
            return AlertEvent(
                alert_id=alert.id,
                org_id=alert.org_id,
                metric_name=alert.metric_name,
                metric_value=0,
                condition_met="No data received",
                severity=alert.severity,
                timestamp=datetime.now()
            )
        
        return None
    
    # ========================================
    # NOTIFICATIONS
    # ========================================
    
    async def _send_notifications(
        self,
        alert: Alert,
        event: AlertEvent
    ) -> None:
        """Send notifications for triggered alert"""
        for channel in alert.notification_channels:
            if channel == "email":
                await self._send_email_notification(alert, event)
            elif channel == "slack":
                await self._send_slack_notification(alert, event)
            elif channel == "webhook":
                await self._send_webhook_notification(alert, event)
    
    async def _send_email_notification(
        self,
        alert: Alert,
        event: AlertEvent
    ) -> None:
        """Send email notification"""
        # TODO: Implement email sending
        print(f"Email notification: {alert.alert_name} triggered")
    
    async def _send_slack_notification(
        self,
        alert: Alert,
        event: AlertEvent
    ) -> None:
        """Send Slack notification"""
        # TODO: Get Slack webhook URL from org settings
        slack_webhook_url = None
        
        if not slack_webhook_url:
            return
        
        # Format Slack message
        severity_emoji = {
            Severity.INFO: "ℹ️",
            Severity.WARNING: "⚠️",
            Severity.CRITICAL: "🚨"
        }
        
        message = {
            "text": f"{severity_emoji[alert.severity]} Alert: {alert.alert_name}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{alert.alert_name}*\n{event.condition_met}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Metric:*\n{event.metric_name}"},
                        {"type": "mrkdwn", "text": f"*Value:*\n{event.metric_value}"},
                        {"type": "mrkdwn", "text": f"*Severity:*\n{alert.severity.value}"},
                        {"type": "mrkdwn", "text": f"*Time:*\n{event.timestamp.isoformat()}"}
                    ]
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(slack_webhook_url, json=message)
    
    async def _send_webhook_notification(
        self,
        alert: Alert,
        event: AlertEvent
    ) -> None:
        """Send webhook notification"""
        # TODO: Get webhook URL from org settings
        webhook_url = None
        
        if not webhook_url:
            return
        
        payload = {
            "alert_id": alert.id,
            "alert_name": alert.alert_name,
            "org_id": alert.org_id,
            "metric_name": event.metric_name,
            "metric_value": event.metric_value,
            "condition": event.condition_met,
            "severity": alert.severity.value,
            "timestamp": event.timestamp.isoformat()
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json=payload)
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _dict_to_alert(self, data: Dict[str, Any]) -> Alert:
        """Convert dict to Alert"""
        last_triggered = None
        if data.get("last_triggered"):
            last_triggered = datetime.fromisoformat(
                data["last_triggered"].replace("Z", "+00:00")
            )
        
        return Alert(
            id=data["id"],
            org_id=data["org_id"],
            alert_name=data["alert_name"],
            alert_type=AlertType(data["alert_type"]),
            metric_name=data["metric_name"],
            condition=data["condition"],
            severity=Severity(data["severity"]),
            notification_channels=data["notification_channels"],
            enabled=data["enabled"],
            last_triggered=last_triggered
        )


# Example usage
"""
from services.monitoring.alert_manager import AlertManager, AlertType, Severity

alert_manager = AlertManager(supabase_client)

# Create threshold alert
alert = await alert_manager.create_alert(
    org_id="org-123",
    alert_name="High API Usage",
    alert_type=AlertType.THRESHOLD,
    metric_name="api_calls_per_hour",
    condition={"operator": ">", "value": 50000},
    severity=Severity.WARNING,
    notification_channels=["email", "slack"]
)

# Record metric
await alert_manager.record_metric(
    org_id="org-123",
    metric_name="api_calls_per_hour",
    metric_value=55000
)

# Evaluate alerts (run periodically)
triggered = await alert_manager.evaluate_alerts("org-123")
for event in triggered:
    print(f"Alert triggered: {event.alert_id}")
"""
