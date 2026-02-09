"""
Utility modules for the Multi-Agent Orchestration System

This module provides common utilities including logging, validation,
audit trail, and helper functions used throughout the orchestration system.
"""

from .logging import (
    get_logger,
    setup_logging,
    LoggerMixin,
    StructuredLogger
)

from .validation import (
    validate_workflow_plan,
    validate_agent_config,
    validate_task_input,
    ValidationResult as UtilValidationResult
)

from .helpers import (
    generate_id,
    format_duration,
    safe_json_serialize,
    retry_with_backoff,
    timeout_after
)

from .audit_trail import (
    get_audit_trail,
    setup_audit_trail,
    OrchestrationAuditTrail,
    AuditEntry
)

__all__ = [
    # Logging
    "get_logger",
    "setup_logging", 
    "LoggerMixin",
    "StructuredLogger",
    
    # Validation
    "validate_workflow_plan",
    "validate_agent_config",
    "validate_task_input",
    "UtilValidationResult",
    
    # Helpers
    "generate_id",
    "format_duration",
    "safe_json_serialize",
    "retry_with_backoff",
    "timeout_after",
    
    # Audit Trail
    "get_audit_trail",
    "setup_audit_trail",
    "OrchestrationAuditTrail",
    "AuditEntry"
]