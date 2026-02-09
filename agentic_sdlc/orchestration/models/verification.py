"""
Verification gate models for the Multi-Agent Orchestration System

This module defines data structures for user approval workflows, verification gates,
and plan modification tracking. These models support requirements 2.5 and 8.2 for
execution plan generation with user approval checkpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from uuid import uuid4


class VerificationStatus(Enum):
    """Status of verification gate"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_MODIFICATION = "requires_modification"
    EXPIRED = "expired"


class ApprovalLevel(Enum):
    """Level of approval required"""
    USER = "user"
    STAKEHOLDER = "stakeholder"
    TECHNICAL_LEAD = "technical_lead"
    PROJECT_MANAGER = "project_manager"
    AUTOMATIC = "automatic"


class ModificationType(Enum):
    """Type of plan modification"""
    AGENT_CHANGE = "agent_change"
    RESOURCE_ADJUSTMENT = "resource_adjustment"
    TIMELINE_CHANGE = "timeline_change"
    SCOPE_MODIFICATION = "scope_modification"
    DEPENDENCY_UPDATE = "dependency_update"
    PRIORITY_CHANGE = "priority_change"


@dataclass
class ApprovalCriteria:
    """Criteria that must be met for approval"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    is_required: bool = True
    validation_rules: List[str] = field(default_factory=list)
    approval_level: ApprovalLevel = ApprovalLevel.USER
    auto_approve_conditions: List[str] = field(default_factory=list)
    
    def can_auto_approve(self, context: Dict[str, Any]) -> bool:
        """Check if criteria can be automatically approved based on context"""
        if not self.auto_approve_conditions:
            return False
        
        # Simple rule evaluation - in production, use a proper rule engine
        for condition in self.auto_approve_conditions:
            if not self._evaluate_condition(condition, context):
                return False
        return True
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a single approval condition"""
        # Simplified condition evaluation
        # Format: "field operator value" (e.g., "cost < 100", "duration <= 480")
        try:
            parts = condition.split()
            if len(parts) != 3:
                return False
            
            field, operator, value = parts
            context_value = context.get(field)
            
            if context_value is None:
                return False
            
            # Convert value to appropriate type
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                # Keep as string
                pass
            
            # Evaluate condition
            if operator == "==":
                return context_value == value
            elif operator == "!=":
                return context_value != value
            elif operator == "<":
                return context_value < value
            elif operator == "<=":
                return context_value <= value
            elif operator == ">":
                return context_value > value
            elif operator == ">=":
                return context_value >= value
            elif operator == "in":
                return str(context_value).lower() in str(value).lower()
            
            return False
        except Exception:
            return False


@dataclass
class UserFeedback:
    """User feedback on execution plan"""
    id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    feedback_type: str = "general"  # general, concern, suggestion, approval, rejection
    content: str = ""
    priority: int = 1  # 1 = high, 5 = low
    addressed: bool = False
    response: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    addressed_at: Optional[datetime] = None
    
    def mark_addressed(self, response: str = ""):
        """Mark feedback as addressed"""
        self.addressed = True
        self.response = response
        self.addressed_at = datetime.now()


@dataclass
class PlanModification:
    """Record of a modification made to an execution plan"""
    id: str = field(default_factory=lambda: str(uuid4()))
    plan_id: str = ""
    modification_type: ModificationType = ModificationType.SCOPE_MODIFICATION
    description: str = ""
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    reason: str = ""
    requested_by: str = ""
    approved_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    impact_assessment: Dict[str, Any] = field(default_factory=dict)
    
    def approve_modification(self, approver: str):
        """Approve the modification"""
        self.approved_by = approver
        self.approved_at = datetime.now()
    
    def get_impact_summary(self) -> str:
        """Get a summary of the modification's impact"""
        if not self.impact_assessment:
            return "Impact not assessed"
        
        summary_parts = []
        if "cost_change" in self.impact_assessment:
            cost_change = self.impact_assessment["cost_change"]
            if cost_change != 0:
                direction = "increase" if cost_change > 0 else "decrease"
                summary_parts.append(f"Cost {direction}: ${abs(cost_change):.2f}")
        
        if "duration_change" in self.impact_assessment:
            duration_change = self.impact_assessment["duration_change"]
            if duration_change != 0:
                direction = "increase" if duration_change > 0 else "decrease"
                summary_parts.append(f"Duration {direction}: {abs(duration_change)} minutes")
        
        if "risk_level" in self.impact_assessment:
            risk_level = self.impact_assessment["risk_level"]
            summary_parts.append(f"Risk level: {risk_level}")
        
        return "; ".join(summary_parts) if summary_parts else "No significant impact"


@dataclass
class VerificationGate:
    """A checkpoint requiring user approval before proceeding"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    plan_id: str = ""
    status: VerificationStatus = VerificationStatus.PENDING
    approval_level: ApprovalLevel = ApprovalLevel.USER
    criteria: List[ApprovalCriteria] = field(default_factory=list)
    user_feedback: List[UserFeedback] = field(default_factory=list)
    modifications: List[PlanModification] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_criteria(self, criteria: ApprovalCriteria):
        """Add approval criteria to the gate"""
        self.criteria.append(criteria)
    
    def add_feedback(self, feedback: UserFeedback):
        """Add user feedback to the gate"""
        self.user_feedback.append(feedback)
    
    def add_modification(self, modification: PlanModification):
        """Add a plan modification to the gate"""
        self.modifications.append(modification)
    
    def approve(self, approver: str, context: Optional[Dict[str, Any]] = None):
        """Approve the verification gate"""
        if self.status != VerificationStatus.PENDING:
            raise ValueError(f"Cannot approve gate with status {self.status.value}")
        
        # Check if all required criteria are met
        if not self._all_criteria_met(context or {}):
            raise ValueError("Not all required criteria are met for approval")
        
        self.status = VerificationStatus.APPROVED
        self.approved_by = approver
        self.approved_at = datetime.now()
    
    def reject(self, rejector: str, reason: str):
        """Reject the verification gate"""
        if self.status != VerificationStatus.PENDING:
            raise ValueError(f"Cannot reject gate with status {self.status.value}")
        
        self.status = VerificationStatus.REJECTED
        self.approved_by = rejector
        self.approved_at = datetime.now()
        self.rejection_reason = reason
    
    def request_modification(self, requester: str, reason: str):
        """Request modifications to the plan"""
        self.status = VerificationStatus.REQUIRES_MODIFICATION
        self.approved_by = requester
        self.approved_at = datetime.now()
        self.rejection_reason = reason
    
    def check_expiration(self):
        """Check if the gate has expired"""
        if self.expires_at and datetime.now() > self.expires_at:
            if self.status == VerificationStatus.PENDING:
                self.status = VerificationStatus.EXPIRED
    
    def can_auto_approve(self, context: Dict[str, Any]) -> bool:
        """Check if the gate can be automatically approved"""
        if self.approval_level != ApprovalLevel.AUTOMATIC:
            return False
        
        return all(criteria.can_auto_approve(context) for criteria in self.criteria)
    
    def get_pending_feedback(self) -> List[UserFeedback]:
        """Get feedback that hasn't been addressed"""
        return [f for f in self.user_feedback if not f.addressed]
    
    def get_high_priority_feedback(self) -> List[UserFeedback]:
        """Get high priority feedback (priority 1-2)"""
        return [f for f in self.user_feedback if f.priority <= 2 and not f.addressed]
    
    def get_approval_progress(self) -> Dict[str, Any]:
        """Get progress towards approval"""
        total_criteria = len(self.criteria)
        if total_criteria == 0:
            return {"progress": 1.0, "met_criteria": 0, "total_criteria": 0}
        
        # This is simplified - in practice, you'd evaluate against actual context
        met_criteria = sum(1 for c in self.criteria if not c.is_required)
        
        return {
            "progress": met_criteria / total_criteria,
            "met_criteria": met_criteria,
            "total_criteria": total_criteria,
            "pending_feedback": len(self.get_pending_feedback()),
            "high_priority_feedback": len(self.get_high_priority_feedback())
        }
    
    def _all_criteria_met(self, context: Dict[str, Any]) -> bool:
        """Check if all required criteria are met"""
        for criteria in self.criteria:
            if criteria.is_required:
                # If criteria has auto-approve conditions, check them
                if criteria.auto_approve_conditions:
                    if not criteria.can_auto_approve(context):
                        return False
                # If no auto-approve conditions, assume criteria can be met through manual approval
                # This allows for manual approval workflows where criteria don't have automatic conditions
        return True


@dataclass
class ApprovalWorkflow:
    """Manages the complete approval workflow for an execution plan"""
    id: str = field(default_factory=lambda: str(uuid4()))
    plan_id: str = ""
    gates: List[VerificationGate] = field(default_factory=list)
    current_gate_index: int = 0
    workflow_status: VerificationStatus = VerificationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_modifications: int = 0
    approval_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_gate(self, gate: VerificationGate):
        """Add a verification gate to the workflow"""
        gate.plan_id = self.plan_id
        self.gates.append(gate)
    
    def get_current_gate(self) -> Optional[VerificationGate]:
        """Get the current active gate"""
        if 0 <= self.current_gate_index < len(self.gates):
            return self.gates[self.current_gate_index]
        return None
    
    def advance_to_next_gate(self) -> bool:
        """Advance to the next gate in the workflow"""
        current_gate = self.get_current_gate()
        if not current_gate or current_gate.status != VerificationStatus.APPROVED:
            return False
        
        self.current_gate_index += 1
        
        # Check if workflow is complete
        if self.current_gate_index >= len(self.gates):
            self.workflow_status = VerificationStatus.APPROVED
            self.completed_at = datetime.now()
            return True
        
        return True
    
    def process_gate_decision(self, gate_id: str, decision: str, user: str, reason: str = "", context: Optional[Dict[str, Any]] = None):
        """Process a decision on a verification gate"""
        gate = next((g for g in self.gates if g.id == gate_id), None)
        if not gate:
            raise ValueError(f"Gate {gate_id} not found in workflow")
        
        # Record the decision in history
        decision_record = {
            "gate_id": gate_id,
            "gate_name": gate.name,
            "decision": decision,
            "user": user,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        self.approval_history.append(decision_record)
        
        if decision == "approve":
            gate.approve(user, context)
            if gate == self.get_current_gate():
                self.advance_to_next_gate()
        elif decision == "reject":
            gate.reject(user, reason)
            self.workflow_status = VerificationStatus.REJECTED
            self.completed_at = datetime.now()
        elif decision == "modify":
            gate.request_modification(user, reason)
            self.workflow_status = VerificationStatus.REQUIRES_MODIFICATION
    
    def apply_modification(self, modification: PlanModification):
        """Apply a modification to the plan and update workflow state"""
        self.total_modifications += 1
        
        # Add modification to the current gate
        current_gate = self.get_current_gate()
        if current_gate:
            current_gate.add_modification(modification)
        
        # Reset workflow status if it was requiring modification
        if self.workflow_status == VerificationStatus.REQUIRES_MODIFICATION:
            self.workflow_status = VerificationStatus.PENDING
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get a summary of the approval workflow"""
        total_gates = len(self.gates)
        completed_gates = sum(1 for g in self.gates if g.status == VerificationStatus.APPROVED)
        
        return {
            "workflow_id": self.id,
            "plan_id": self.plan_id,
            "status": self.workflow_status.value,
            "progress": {
                "completed_gates": completed_gates,
                "total_gates": total_gates,
                "current_gate": self.current_gate_index,
                "progress_percentage": (completed_gates / total_gates * 100) if total_gates > 0 else 0
            },
            "modifications": self.total_modifications,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "current_gate_name": self.get_current_gate().name if self.get_current_gate() else None
        }
    
    def is_complete(self) -> bool:
        """Check if the approval workflow is complete"""
        return self.workflow_status in [VerificationStatus.APPROVED, VerificationStatus.REJECTED]
    
    def can_proceed_to_execution(self) -> bool:
        """Check if the plan can proceed to execution"""
        return self.workflow_status == VerificationStatus.APPROVED
    
    def get_blocking_issues(self) -> List[str]:
        """Get issues that are blocking approval"""
        issues = []
        
        current_gate = self.get_current_gate()
        if current_gate:
            # Check for high priority feedback
            high_priority_feedback = current_gate.get_high_priority_feedback()
            if high_priority_feedback:
                issues.append(f"{len(high_priority_feedback)} high priority feedback items need attention")
            
            # Check for expired gates
            current_gate.check_expiration()
            if current_gate.status == VerificationStatus.EXPIRED:
                issues.append("Current verification gate has expired")
            
            # Check for required criteria
            progress = current_gate.get_approval_progress()
            if progress["progress"] < 1.0:
                unmet_criteria = progress["total_criteria"] - progress["met_criteria"]
                issues.append(f"{unmet_criteria} required criteria not yet met")
        
        return issues