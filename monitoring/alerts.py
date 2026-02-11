"""Alert system for SDLC Kit.

This module provides functionality for defining alert conditions
and triggering notifications when conditions are met.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Callable, Dict, Any
from monitoring.loggers import SDLCLogger


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class Alert:
    """Represents an alert instance.
    
    Attributes:
        id: Unique alert identifier
        name: Alert name
        severity: Alert severity level
        message: Alert message
        timestamp: When the alert was triggered
        status: Current alert status
        metadata: Additional alert metadata
    """
    id: str
    name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    status: AlertStatus = AlertStatus.ACTIVE
    metadata: Optional[Dict[str, Any]] = None
    
    def acknowledge(self) -> None:
        """Mark alert as acknowledged."""
        self.status = AlertStatus.ACKNOWLEDGED
    
    def resolve(self) -> None:
        """Mark alert as resolved."""
        self.status = AlertStatus.RESOLVED


@dataclass
class AlertCondition:
    """Defines a condition that triggers an alert.
    
    Attributes:
        name: Condition name
        check_function: Function that returns True if alert should trigger
        severity: Alert severity when triggered
        message_template: Template for alert message
        cooldown_seconds: Minimum seconds between alerts (prevents spam)
    """
    name: str
    check_function: Callable[[], bool]
    severity: AlertSeverity
    message_template: str
    cooldown_seconds: int = 300  # 5 minutes default
    
    last_triggered: Optional[datetime] = None
    
    def should_trigger(self) -> bool:
        """Check if condition should trigger an alert.
        
        Returns:
            True if alert should trigger, False otherwise
        """
        # Check cooldown period
        if self.last_triggered:
            elapsed = (datetime.now() - self.last_triggered).total_seconds()
            if elapsed < self.cooldown_seconds:
                return False
        
        # Check condition
        try:
            return self.check_function()
        except Exception as e:
            logger = SDLCLogger.get_logger(__name__)
            logger.error(f"Error checking alert condition '{self.name}': {e}")
            return False


class AlertManager:
    """Manages alert conditions and notifications.
    
    The AlertManager monitors defined conditions and triggers alerts
    when conditions are met. It supports multiple notification handlers
    for different alert delivery methods.
    """
    
    def __init__(self):
        """Initialize alert manager."""
        self.conditions: List[AlertCondition] = []
        self.active_alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        self.notification_handlers: List[Callable[[Alert], None]] = []
        self.logger = SDLCLogger.get_logger(__name__)
        self._alert_counter = 0
    
    def add_condition(self, condition: AlertCondition) -> None:
        """Add an alert condition to monitor.
        
        Args:
            condition: Alert condition to add
        """
        self.conditions.append(condition)
        self.logger.info(f"Added alert condition: {condition.name}")
    
    def remove_condition(self, name: str) -> bool:
        """Remove an alert condition by name.
        
        Args:
            name: Name of condition to remove
        
        Returns:
            True if condition was removed, False if not found
        """
        for i, condition in enumerate(self.conditions):
            if condition.name == name:
                self.conditions.pop(i)
                self.logger.info(f"Removed alert condition: {name}")
                return True
        return False
    
    def add_notification_handler(self, handler: Callable[[Alert], None]) -> None:
        """Add a notification handler for alerts.
        
        Args:
            handler: Function that receives Alert and sends notification
        
        Example:
            >>> def email_handler(alert: Alert):
            ...     send_email(f"Alert: {alert.message}")
            >>> manager.add_notification_handler(email_handler)
        """
        self.notification_handlers.append(handler)
    
    def check_conditions(self) -> List[Alert]:
        """Check all conditions and trigger alerts if needed.
        
        Returns:
            List of newly triggered alerts
        """
        new_alerts = []
        
        for condition in self.conditions:
            if condition.should_trigger():
                alert = self._create_alert(condition)
                new_alerts.append(alert)
                condition.last_triggered = datetime.now()
        
        return new_alerts
    
    def _create_alert(self, condition: AlertCondition) -> Alert:
        """Create an alert from a triggered condition.
        
        Args:
            condition: The triggered condition
        
        Returns:
            Created alert
        """
        self._alert_counter += 1
        alert = Alert(
            id=f"alert-{self._alert_counter}",
            name=condition.name,
            severity=condition.severity,
            message=condition.message_template,
            timestamp=datetime.now()
        )
        
        self.active_alerts.append(alert)
        self.alert_history.append(alert)
        
        # Log alert
        self.logger.log(
            self._severity_to_log_level(condition.severity),
            f"Alert triggered: {alert.name} - {alert.message}"
        )
        
        # Send notifications
        self._notify(alert)
        
        return alert
    
    def _notify(self, alert: Alert) -> None:
        """Send notifications for an alert.
        
        Args:
            alert: Alert to notify about
        """
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Error in notification handler: {e}")
    
    def _severity_to_log_level(self, severity: AlertSeverity) -> int:
        """Convert alert severity to logging level.
        
        Args:
            severity: Alert severity
        
        Returns:
            Logging level constant
        """
        import logging
        mapping = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL,
        }
        return mapping.get(severity, logging.INFO)
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert by ID.
        
        Args:
            alert_id: Alert ID to acknowledge
        
        Returns:
            True if alert was acknowledged, False if not found
        """
        for alert in self.active_alerts:
            if alert.id == alert_id:
                alert.acknowledge()
                self.logger.info(f"Alert acknowledged: {alert_id}")
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert by ID.
        
        Args:
            alert_id: Alert ID to resolve
        
        Returns:
            True if alert was resolved, False if not found
        """
        for i, alert in enumerate(self.active_alerts):
            if alert.id == alert_id:
                alert.resolve()
                self.active_alerts.pop(i)
                self.logger.info(f"Alert resolved: {alert_id}")
                return True
        return False
    
    def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """Get all active alerts, optionally filtered by severity.
        
        Args:
            severity: Optional severity filter
        
        Returns:
            List of active alerts
        """
        if severity:
            return [a for a in self.active_alerts if a.severity == severity]
        return self.active_alerts.copy()
    
    def get_alert_history(
        self,
        limit: Optional[int] = None
    ) -> List[Alert]:
        """Get alert history.
        
        Args:
            limit: Optional limit on number of alerts to return
        
        Returns:
            List of historical alerts (most recent first)
        """
        history = sorted(self.alert_history, key=lambda a: a.timestamp, reverse=True)
        if limit:
            return history[:limit]
        return history
