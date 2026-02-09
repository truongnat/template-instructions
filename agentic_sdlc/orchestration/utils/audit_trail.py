"""
Audit Trail utilities for the Multi-Agent Orchestration System

This module provides comprehensive audit trail functionality for tracking
all user requests, processing decisions, and workflow executions with
proper timestamps, user context, and persistence capabilities.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from uuid import uuid4
from contextlib import contextmanager

from ..models import UserRequest, ConversationContext, WorkflowInitiation
from ..exceptions.state import StatePersistenceError
from .logging import StructuredLogger


@dataclass
class AuditEntry:
    """Represents a single audit trail entry"""
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    entry_type: str = ""  # request, processing, workflow, decision, error
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    request_id: Optional[str] = None
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    
    # Core data
    action: str = ""
    category: str = ""
    severity: str = "info"  # debug, info, warning, error, critical
    
    # Request-specific data
    request_content: Optional[str] = None
    request_intent: Optional[str] = None
    request_confidence: Optional[float] = None
    request_complexity: Optional[str] = None
    
    # Processing data
    processing_duration_ms: Optional[int] = None
    processing_result: Optional[str] = None
    entities_extracted: Optional[Dict[str, Any]] = None
    keywords_extracted: Optional[List[str]] = None
    
    # Workflow data
    workflow_type: Optional[str] = None
    workflow_phase: Optional[str] = None
    workflow_decision: Optional[str] = None
    clarifications_requested: Optional[List[str]] = None
    next_steps_suggested: Optional[List[str]] = None
    
    # Context and metadata
    user_context: Optional[Dict[str, Any]] = None
    system_context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Error information
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    error_stack_trace: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        # Convert datetime to ISO string
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEntry':
        """Create from dictionary"""
        # Convert datetime string to datetime object
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Remove database-specific fields that aren't part of the dataclass
        db_fields = {'created_at'}
        filtered_data = {k: v for k, v in data.items() if k not in db_fields}
        
        return cls(**filtered_data)


class OrchestrationAuditTrail:
    """
    Comprehensive audit trail system for the orchestration system
    
    Provides structured logging with timestamps, user context, and persistence
    for all requests, processing decisions, and workflow executions.
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        max_entries_per_file: int = 10000,
        retention_days: int = 365
    ):
        """Initialize the audit trail system"""
        self.storage_path = storage_path or Path("data/audit_trail")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.max_entries_per_file = max_entries_per_file
        self.retention_days = retention_days
        
        # Initialize database
        self.db_path = self.storage_path / "audit_trail.db"
        self._init_database()
        
        # Initialize logger
        self.logger = StructuredLogger(
            name="orchestration.audit_trail",
            component="AuditTrail"
        )
        
        self.logger.info("Audit trail system initialized", storage_path=str(self.storage_path))
    
    def _init_database(self):
        """Initialize SQLite database for audit trail storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS audit_entries (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        entry_type TEXT NOT NULL,
                        user_id TEXT,
                        conversation_id TEXT,
                        request_id TEXT,
                        workflow_id TEXT,
                        agent_id TEXT,
                        action TEXT NOT NULL,
                        category TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        request_content TEXT,
                        request_intent TEXT,
                        request_confidence REAL,
                        request_complexity TEXT,
                        processing_duration_ms INTEGER,
                        processing_result TEXT,
                        entities_extracted TEXT,
                        keywords_extracted TEXT,
                        workflow_type TEXT,
                        workflow_phase TEXT,
                        workflow_decision TEXT,
                        clarifications_requested TEXT,
                        next_steps_suggested TEXT,
                        user_context TEXT,
                        system_context TEXT,
                        metadata TEXT,
                        error_type TEXT,
                        error_message TEXT,
                        error_stack_trace TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for common queries
                conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_entries(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON audit_entries(user_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_request_id ON audit_entries(request_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_workflow_id ON audit_entries(workflow_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_entry_type ON audit_entries(entry_type)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON audit_entries(category)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_severity ON audit_entries(severity)")
                
                conn.commit()
                
        except Exception as e:
            raise StatePersistenceError(
                f"Failed to initialize audit trail database: {str(e)}",
                operation="database_init",
                cause=e
            )
    
    def log_request_received(
        self,
        request: UserRequest,
        context: Optional[ConversationContext] = None
    ) -> str:
        """Log when a user request is received"""
        entry = AuditEntry(
            entry_type="request",
            user_id=request.user_id,
            conversation_id=context.conversation_id if context else None,
            request_id=request.id,
            action="Request received",
            category="user_interaction",
            severity="info",
            request_content=request.content,
            request_intent=getattr(request, 'intent', None),
            request_confidence=getattr(request, 'confidence', None),
            user_context=self._extract_user_context(context) if context else None,
            system_context=self._extract_system_context(),
            metadata={
                "content_length": len(request.content),
                "has_context": context is not None,
                "interaction_count": context.interaction_count if context else 0
            }
        )
        
        return self._persist_entry(entry)
    
    def log_request_processing(
        self,
        request: UserRequest,
        parsing_result: Any,  # RequestParsingResult
        processing_duration_ms: int,
        context: Optional[ConversationContext] = None
    ) -> str:
        """Log request processing results"""
        entry = AuditEntry(
            entry_type="processing",
            user_id=request.user_id,
            conversation_id=context.conversation_id if context else None,
            request_id=request.id,
            action="Request processed",
            category="request_processing",
            severity="info",
            request_content=request.content,
            request_intent=parsing_result.intent,
            request_confidence=parsing_result.confidence,
            request_complexity=parsing_result.complexity,
            processing_duration_ms=processing_duration_ms,
            processing_result="success",
            entities_extracted=parsing_result.entities,
            keywords_extracted=parsing_result.keywords,
            clarifications_requested=parsing_result.clarification_questions,
            user_context=self._extract_user_context(context) if context else None,
            system_context=self._extract_system_context(),
            metadata={
                "requires_clarification": parsing_result.requires_clarification,
                "entities_count": len(parsing_result.entities),
                "keywords_count": len(parsing_result.keywords)
            }
        )
        
        return self._persist_entry(entry)
    
    def log_workflow_decision(
        self,
        request: UserRequest,
        workflow_initiation: WorkflowInitiation,
        context: Optional[ConversationContext] = None
    ) -> str:
        """Log workflow initiation decision"""
        entry = AuditEntry(
            entry_type="workflow",
            user_id=request.user_id,
            conversation_id=context.conversation_id if context else None,
            request_id=request.id,
            workflow_id=workflow_initiation.request_id,  # Using request_id as workflow_id
            action="Workflow decision made",
            category="workflow_orchestration",
            severity="info",
            workflow_type=workflow_initiation.workflow_type,
            workflow_decision="proceed" if workflow_initiation.should_proceed else "clarification_needed",
            clarifications_requested=workflow_initiation.required_clarifications,
            next_steps_suggested=workflow_initiation.suggested_next_steps,
            user_context=self._extract_user_context(context) if context else None,
            system_context=self._extract_system_context(),
            metadata={
                "should_proceed": workflow_initiation.should_proceed,
                "estimated_complexity": workflow_initiation.estimated_complexity,
                "clarifications_count": len(workflow_initiation.required_clarifications),
                "next_steps_count": len(workflow_initiation.suggested_next_steps)
            }
        )
        
        return self._persist_entry(entry)
    
    def log_error(
        self,
        error: Exception,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        operation: str = "unknown",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log an error with full context"""
        import traceback
        
        entry = AuditEntry(
            entry_type="error",
            user_id=user_id,
            request_id=request_id,
            workflow_id=workflow_id,
            agent_id=agent_id,
            action=f"Error in {operation}",
            category="error",
            severity="error",
            error_type=type(error).__name__,
            error_message=str(error),
            error_stack_trace=traceback.format_exc(),
            system_context=self._extract_system_context(),
            metadata={
                "operation": operation,
                "context": context or {}
            }
        )
        
        return self._persist_entry(entry)
    
    def log_agent_event(
        self,
        agent_id: str,
        event: str,
        category: str,
        request_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        user_id: Optional[str] = None,
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log an agent-specific event"""
        entry = AuditEntry(
            entry_type="agent_event",
            user_id=user_id,
            request_id=request_id,
            workflow_id=workflow_id,
            agent_id=agent_id,
            action=event,
            category=category,
            severity=severity,
            system_context=self._extract_system_context(),
            metadata=metadata or {}
        )
        
        return self._persist_entry(entry)
    
    def log_workflow_phase_transition(
        self,
        workflow_id: str,
        from_phase: str,
        to_phase: str,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log workflow phase transitions"""
        entry = AuditEntry(
            entry_type="workflow",
            user_id=user_id,
            workflow_id=workflow_id,
            agent_id=agent_id,
            action=f"Phase transition: {from_phase} -> {to_phase}",
            category="workflow_phase",
            severity="info",
            workflow_phase=to_phase,
            system_context=self._extract_system_context(),
            metadata={
                "from_phase": from_phase,
                "to_phase": to_phase,
                **(metadata or {})
            }
        )
        
        return self._persist_entry(entry)
    
    def _persist_entry(self, entry: AuditEntry) -> str:
        """Persist an audit entry to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Convert complex fields to JSON strings
                entities_json = json.dumps(entry.entities_extracted) if entry.entities_extracted else None
                keywords_json = json.dumps(entry.keywords_extracted) if entry.keywords_extracted else None
                clarifications_json = json.dumps(entry.clarifications_requested) if entry.clarifications_requested else None
                next_steps_json = json.dumps(entry.next_steps_suggested) if entry.next_steps_suggested else None
                user_context_json = json.dumps(entry.user_context) if entry.user_context else None
                system_context_json = json.dumps(entry.system_context) if entry.system_context else None
                metadata_json = json.dumps(entry.metadata) if entry.metadata else None
                
                conn.execute("""
                    INSERT INTO audit_entries (
                        id, timestamp, entry_type, user_id, conversation_id, request_id,
                        workflow_id, agent_id, action, category, severity,
                        request_content, request_intent, request_confidence, request_complexity,
                        processing_duration_ms, processing_result, entities_extracted, keywords_extracted,
                        workflow_type, workflow_phase, workflow_decision,
                        clarifications_requested, next_steps_suggested,
                        user_context, system_context, metadata,
                        error_type, error_message, error_stack_trace
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.id, entry.timestamp.isoformat(), entry.entry_type,
                    entry.user_id, entry.conversation_id, entry.request_id,
                    entry.workflow_id, entry.agent_id, entry.action, entry.category, entry.severity,
                    entry.request_content, entry.request_intent, entry.request_confidence, entry.request_complexity,
                    entry.processing_duration_ms, entry.processing_result, entities_json, keywords_json,
                    entry.workflow_type, entry.workflow_phase, entry.workflow_decision,
                    clarifications_json, next_steps_json,
                    user_context_json, system_context_json, metadata_json,
                    entry.error_type, entry.error_message, entry.error_stack_trace
                ))
                
                conn.commit()
                
            self.logger.debug("Audit entry persisted", entry_id=entry.id, entry_type=entry.entry_type)
            return entry.id
            
        except Exception as e:
            self.logger.error("Failed to persist audit entry", error=str(e), entry_id=entry.id)
            raise StatePersistenceError(
                f"Failed to persist audit entry: {str(e)}",
                operation="persist_audit_entry",
                cause=e
            )
    
    def get_entries(
        self,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        entry_type: Optional[str] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[AuditEntry]:
        """Retrieve audit entries with filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                query = "SELECT * FROM audit_entries WHERE 1=1"
                params = []
                
                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)
                
                if request_id:
                    query += " AND request_id = ?"
                    params.append(request_id)
                
                if workflow_id:
                    query += " AND workflow_id = ?"
                    params.append(workflow_id)
                
                if entry_type:
                    query += " AND entry_type = ?"
                    params.append(entry_type)
                
                if category:
                    query += " AND category = ?"
                    params.append(category)
                
                if severity:
                    query += " AND severity = ?"
                    params.append(severity)
                
                if start_time:
                    query += " AND timestamp >= ?"
                    params.append(start_time.isoformat())
                
                if end_time:
                    query += " AND timestamp <= ?"
                    params.append(end_time.isoformat())
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                entries = []
                for row in rows:
                    # Convert row to dict and handle JSON fields
                    data = dict(row)
                    
                    # Parse JSON fields
                    for field in ['entities_extracted', 'keywords_extracted', 'clarifications_requested',
                                  'next_steps_suggested', 'user_context', 'system_context', 'metadata']:
                        if data.get(field):
                            try:
                                data[field] = json.loads(data[field])
                            except json.JSONDecodeError:
                                data[field] = None
                    
                    # Convert timestamp
                    if data.get('timestamp'):
                        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                    
                    entries.append(AuditEntry.from_dict(data))
                
                return entries
                
        except Exception as e:
            self.logger.error("Failed to retrieve audit entries", error=str(e))
            raise StatePersistenceError(
                f"Failed to retrieve audit entries: {str(e)}",
                operation="get_audit_entries",
                cause=e
            )
    
    def get_request_trail(self, request_id: str) -> List[AuditEntry]:
        """Get complete audit trail for a specific request"""
        return self.get_entries(request_id=request_id)
    
    def get_user_activity(self, user_id: str, days: int = 30) -> List[AuditEntry]:
        """Get user activity for the specified number of days"""
        start_time = datetime.now() - timedelta(days=days)
        return self.get_entries(user_id=user_id, start_time=start_time)
    
    def get_workflow_trail(self, workflow_id: str) -> List[AuditEntry]:
        """Get complete audit trail for a specific workflow"""
        return self.get_entries(workflow_id=workflow_id)
    
    def get_error_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get error summary for the specified number of days"""
        start_time = datetime.now() - timedelta(days=days)
        errors = self.get_entries(severity="error", start_time=start_time)
        
        error_types = {}
        error_operations = {}
        
        for error in errors:
            error_type = error.error_type or "unknown"
            operation = error.metadata.get("operation", "unknown") if error.metadata else "unknown"
            
            error_types[error_type] = error_types.get(error_type, 0) + 1
            error_operations[operation] = error_operations.get(operation, 0) + 1
        
        return {
            "total_errors": len(errors),
            "error_types": error_types,
            "error_operations": error_operations,
            "recent_errors": [
                {
                    "timestamp": error.timestamp.isoformat(),
                    "error_type": error.error_type,
                    "error_message": error.error_message,
                    "operation": error.metadata.get("operation") if error.metadata else None
                }
                for error in errors[:10]  # Last 10 errors
            ]
        }
    
    def cleanup_old_entries(self, days: Optional[int] = None) -> int:
        """Clean up old audit entries beyond retention period"""
        retention_days = days or self.retention_days
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM audit_entries WHERE timestamp < ?",
                    (cutoff_date.isoformat(),)
                )
                deleted_count = cursor.rowcount
                conn.commit()
                
            self.logger.info(
                "Cleaned up old audit entries",
                deleted_count=deleted_count,
                cutoff_date=cutoff_date.isoformat()
            )
            
            return deleted_count
            
        except Exception as e:
            self.logger.error("Failed to cleanup old audit entries", error=str(e))
            raise StatePersistenceError(
                f"Failed to cleanup old audit entries: {str(e)}",
                operation="cleanup_audit_entries",
                cause=e
            )
    
    def _extract_user_context(self, context: ConversationContext) -> Dict[str, Any]:
        """Extract relevant user context for audit logging"""
        return {
            "conversation_id": context.conversation_id,
            "session_start": context.session_start.isoformat(),
            "interaction_count": context.interaction_count,
            "preferences": context.preferences,
            "context_keys": list(context.context_data.keys())
        }
    
    def _extract_system_context(self) -> Dict[str, Any]:
        """Extract relevant system context for audit logging"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": "multi_agent_orchestration",
            "version": "1.0.0"  # This could be dynamically determined
        }
    
    @contextmanager
    def audit_operation(
        self,
        operation: str,
        category: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ):
        """Context manager for auditing operations with automatic error logging"""
        start_time = datetime.now()
        
        try:
            # Log operation start
            self.log_agent_event(
                agent_id=agent_id or "system",
                event=f"Started {operation}",
                category=category,
                request_id=request_id,
                workflow_id=workflow_id,
                user_id=user_id,
                severity="debug",
                metadata={"operation_start": start_time.isoformat()}
            )
            
            yield
            
            # Log operation success
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            self.log_agent_event(
                agent_id=agent_id or "system",
                event=f"Completed {operation}",
                category=category,
                request_id=request_id,
                workflow_id=workflow_id,
                user_id=user_id,
                severity="info",
                metadata={
                    "operation_duration_ms": duration_ms,
                    "operation_result": "success"
                }
            )
            
        except Exception as e:
            # Log operation failure
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            self.log_error(
                error=e,
                request_id=request_id,
                user_id=user_id,
                workflow_id=workflow_id,
                agent_id=agent_id,
                operation=operation,
                context={
                    "operation_duration_ms": duration_ms,
                    "category": category
                }
            )
            raise


# Global audit trail instance
_audit_trail: Optional[OrchestrationAuditTrail] = None


def get_audit_trail(storage_path: Optional[Path] = None) -> OrchestrationAuditTrail:
    """Get the global audit trail instance"""
    global _audit_trail
    if _audit_trail is None:
        _audit_trail = OrchestrationAuditTrail(storage_path)
    return _audit_trail


def setup_audit_trail(storage_path: Optional[Path] = None, **kwargs) -> OrchestrationAuditTrail:
    """Setup and configure the global audit trail instance"""
    global _audit_trail
    _audit_trail = OrchestrationAuditTrail(storage_path, **kwargs)
    return _audit_trail