"""
Security Audit Logger for SDLC Kit.

Logs security events including authentication, authorization, and secret access.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum


class SecurityEventType(Enum):
    """Types of security events."""
    AUTHENTICATION_SUCCESS = "authentication_success"
    AUTHENTICATION_FAILURE = "authentication_failure"
    LOGOUT = "logout"
    AUTHORIZATION_GRANTED = "authorization_granted"
    AUTHORIZATION_DENIED = "authorization_denied"
    SECRET_ACCESSED = "secret_accessed"
    SECRET_CREATED = "secret_created"
    SECRET_DELETED = "secret_deleted"
    PERMISSION_CHECK = "permission_check"


class AuditLogger:
    """Security audit logger for tracking security events."""
    
    def __init__(self, log_path: Optional[str] = None):
        """
        Initialize audit logger.
        
        Args:
            log_path: Optional path to audit log file.
                     Defaults to logs/security_audit.log
        """
        self.log_path = Path(log_path or "logs/security_audit.log")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure structured logging
        self.logger = logging.getLogger("security_audit")
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # File handler for audit log
        file_handler = logging.FileHandler(self.log_path)
        file_handler.setLevel(logging.INFO)
        
        # Use JSON formatter for structured logging
        formatter = logging.Formatter(
            '%(message)s'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.propagate = False
    
    def log_authentication(
        self,
        user: str,
        success: bool,
        method: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log authentication event.
        
        Args:
            user: Username or user identifier
            success: Whether authentication succeeded
            method: Authentication method (e.g., "password", "token")
            ip_address: IP address of the authentication attempt
            details: Additional event details
        """
        event_type = (
            SecurityEventType.AUTHENTICATION_SUCCESS if success
            else SecurityEventType.AUTHENTICATION_FAILURE
        )
        
        self._log_event(
            event_type=event_type,
            user=user,
            details={
                "method": method,
                "ip_address": ip_address,
                **(details or {})
            }
        )
    
    def log_logout(
        self,
        user: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log logout event.
        
        Args:
            user: Username or user identifier
            details: Additional event details
        """
        self._log_event(
            event_type=SecurityEventType.LOGOUT,
            user=user,
            details=details
        )
    
    def log_authorization(
        self,
        user: str,
        resource: str,
        action: str,
        granted: bool,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log authorization event.
        
        Args:
            user: Username or user identifier
            resource: Resource being accessed
            action: Action being performed
            granted: Whether access was granted
            details: Additional event details
        """
        event_type = (
            SecurityEventType.AUTHORIZATION_GRANTED if granted
            else SecurityEventType.AUTHORIZATION_DENIED
        )
        
        self._log_event(
            event_type=event_type,
            user=user,
            details={
                "resource": resource,
                "action": action,
                **(details or {})
            }
        )
    
    def log_secret_access(
        self,
        user: str,
        secret_key: str,
        action: str = "accessed",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log secret access event.
        
        IMPORTANT: Never log the actual secret value.
        
        Args:
            user: Username or user identifier
            secret_key: The key of the secret (NOT the value)
            action: Action performed ("accessed", "created", "deleted")
            details: Additional event details
        """
        event_type_map = {
            "accessed": SecurityEventType.SECRET_ACCESSED,
            "created": SecurityEventType.SECRET_CREATED,
            "deleted": SecurityEventType.SECRET_DELETED,
        }
        
        event_type = event_type_map.get(action, SecurityEventType.SECRET_ACCESSED)
        
        self._log_event(
            event_type=event_type,
            user=user,
            details={
                "secret_key": secret_key,
                **(details or {})
            }
        )
    
    def log_permission_check(
        self,
        user: str,
        permission: str,
        result: bool,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log permission check event.
        
        Args:
            user: Username or user identifier
            permission: Permission being checked
            result: Result of the permission check
            details: Additional event details
        """
        self._log_event(
            event_type=SecurityEventType.PERMISSION_CHECK,
            user=user,
            details={
                "permission": permission,
                "result": result,
                **(details or {})
            }
        )
    
    def _log_event(
        self,
        event_type: SecurityEventType,
        user: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a security event in structured format.
        
        Args:
            event_type: Type of security event
            user: Username or user identifier
            details: Additional event details
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "user": user,
            "details": details or {}
        }
        
        # Log as JSON for easy parsing
        self.logger.info(json.dumps(event))
    
    def query_events(
        self,
        event_type: Optional[SecurityEventType] = None,
        user: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> list:
        """
        Query audit log for events matching criteria.
        
        Args:
            event_type: Filter by event type
            user: Filter by user
            start_time: Filter events after this time
            end_time: Filter events before this time
            
        Returns:
            List of matching events
        """
        if not self.log_path.exists():
            return []
        
        matching_events = []
        
        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        
                        # Apply filters
                        if event_type and event.get("event_type") != event_type.value:
                            continue
                        
                        if user and event.get("user") != user:
                            continue
                        
                        event_time = datetime.fromisoformat(event.get("timestamp", ""))
                        
                        if start_time and event_time < start_time:
                            continue
                        
                        if end_time and event_time > end_time:
                            continue
                        
                        matching_events.append(event)
                    except (json.JSONDecodeError, ValueError):
                        # Skip malformed lines
                        continue
        except Exception:
            # Return what we have so far
            pass
        
        return matching_events
