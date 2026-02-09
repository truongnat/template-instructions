"""
Document Generation and Verification System

This module implements the DocumentSystem class responsible for compiling reports,
managing verification gates, and handling feedback routing.

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
"""

import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from uuid import uuid4

from ..models.workflow import WorkflowExecution
from ..models.agent import AgentResult, TaskStatus
from ..utils.logging import get_logger


class ApprovalStatus(Enum):
    """Status of user approval"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


@dataclass
class VerificationGate:
    """User verification gate requiring explicit approval"""
    id: str = field(default_factory=lambda: str(uuid4()))
    workflow_id: str = ""
    phase: str = ""
    document_id: str = ""
    status: ApprovalStatus = ApprovalStatus.PENDING
    feedback: str = ""
    approver: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    """Generated document"""
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    content: str = ""
    type: str = "report"
    format: str = "markdown"
    version: int = 1
    source_results: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DocumentSystem:
    """
    System for document generation, verification, and feedback management.
    
    Features:
    - Comprehensive Report Compilation
    - User Verification Gates
    - Feedback Routing
    - Document Archiving
    """
    
    def __init__(self, archive_path: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.archive_path = archive_path
        self.documents: Dict[str, Document] = {}
        self.gates: Dict[str, VerificationGate] = {}
        
    def compile_report(self, workflow: WorkflowExecution, title: str = "Workflow Report") -> Document:
        """
        Compile a comprehensive report from workflow execution results
        
        Args:
            workflow: Workflow execution object
            title: Title of the report
            
        Returns:
            Generated Document object
        """
        content = [f"# {title}", f"**Execution ID:** {workflow.id}", f"**Generated:** {datetime.now()}"]
        
        source_ids = []
        
        # In a real implementation, we would traverse task results
        # Assuming workflow.completed_tasks is a list of AgentResult or similar
        # But WorkflowExecution definition in models might differ, using generic attribute access
        
        # If workflow has completed_tasks attribute which is list of AgentResult
        results = getattr(workflow, 'completed_tasks', [])
        
        for result in results:
            if isinstance(result, AgentResult):
                source_ids.append(result.task_id)
                content.append(f"\n## Task: {result.task_id}")
                content.append(f"**Agent:** {result.instance_id}")
                content.append(f"**Status:** {result.status.value}")
                
                # Format output data
                if result.output and result.output.data:
                    data_str = json.dumps(result.output.data, indent=2) if isinstance(result.output.data, (dict, list)) else str(result.output.data)
                    content.append(f"\n```json\n{data_str}\n```")
        
        document = Document(
            title=title,
            content="\n".join(content),
            source_results=source_ids
        )
        
        self.documents[document.id] = document
        self.logger.info(f"Generated document {document.id}: {title}")
        return document
        
    def create_verification_gate(self, workflow_id: str, document_id: str, phase: str) -> VerificationGate:
        """Create a new verification gate"""
        gate = VerificationGate(
            workflow_id=workflow_id,
            document_id=document_id,
            phase=phase
        )
        self.gates[gate.id] = gate
        self.logger.info(f"Created verification gate {gate.id} for document {document_id}")
        return gate
        
    def process_approval(self, gate_id: str, approved: bool, feedback: str = "", approver: str = "user") -> VerificationGate:
        """Process a user approval decision"""
        if gate_id not in self.gates:
            raise ValueError(f"Gate {gate_id} not found")
            
        gate = self.gates[gate_id]
        gate.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        if not approved and feedback:
            gate.status = ApprovalStatus.REVISION_REQUESTED
            
        gate.feedback = feedback
        gate.approver = approver
        gate.updated_at = datetime.now()
        
        self.logger.info(f"Processed approval for gate {gate_id}: {gate.status.value}")
        return gate
        
    def get_document(self, document_id: str) -> Optional[Document]:
        """Retrieve a document by ID"""
        return self.documents.get(document_id)
    
    def get_gate(self, gate_id: str) -> Optional[VerificationGate]:
        """Retrieve a gate by ID"""
        return self.gates.get(gate_id)

