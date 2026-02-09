"""
ExecutionPlanner implementation for the Multi-Agent Orchestration System

This module implements the ExecutionPlanner class that generates detailed execution plans
with user approval workflows, verification gates, and plan modification capabilities.
Supports requirements 2.5 and 8.2 for execution plan generation and user approval.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from uuid import uuid4
from enum import Enum

from ..models import (
    WorkflowPlan, ValidationResult, OrchestrationPattern, AgentType,
    AgentAssignment, TaskDependency, ResourceRequirement, ClarifiedRequest
)
from ..models.verification import (
    VerificationGate, ApprovalWorkflow, ApprovalCriteria, ApprovalLevel,
    VerificationStatus, UserFeedback, PlanModification, ModificationType
)
from ..exceptions.workflow import (
    WorkflowEngineError, WorkflowValidationError, WorkflowMatchingError
)
from ..utils.logging import StructuredLogger
from ..utils.audit_trail import get_audit_trail


class PlanComplexity(Enum):
    """Complexity levels for execution plans"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"


class PlanValidationLevel(Enum):
    """Validation levels for execution plans"""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    ENTERPRISE = "enterprise"


@dataclass
class ExecutionPlanDetails:
    """Detailed breakdown of an execution plan"""
    id: str = field(default_factory=lambda: str(uuid4()))
    plan_id: str = ""
    complexity: PlanComplexity = PlanComplexity.MODERATE
    validation_level: PlanValidationLevel = PlanValidationLevel.STANDARD
    
    # Task breakdown
    total_tasks: int = 0
    critical_path_tasks: List[str] = field(default_factory=list)
    parallel_task_groups: List[List[str]] = field(default_factory=list)
    task_breakdown: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Resource analysis
    peak_resource_usage: Dict[str, float] = field(default_factory=dict)
    resource_timeline: List[Dict[str, Any]] = field(default_factory=list)
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    
    # Risk assessment
    identified_risks: List[Dict[str, Any]] = field(default_factory=list)
    mitigation_strategies: List[Dict[str, Any]] = field(default_factory=list)
    contingency_plans: List[Dict[str, Any]] = field(default_factory=list)
    
    # Quality gates
    quality_checkpoints: List[str] = field(default_factory=list)
    success_metrics: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timeline analysis
    earliest_start: Optional[datetime] = None
    latest_finish: Optional[datetime] = None
    buffer_time_minutes: int = 0
    
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the execution plan details"""
        return {
            "complexity": self.complexity.value,
            "validation_level": self.validation_level.value,
            "total_tasks": self.total_tasks,
            "critical_path_length": len(self.critical_path_tasks),
            "parallel_groups": len(self.parallel_task_groups),
            "total_cost": sum(self.cost_breakdown.values()),
            "identified_risks": len(self.identified_risks),
            "quality_checkpoints": len(self.quality_checkpoints),
            "buffer_time_hours": self.buffer_time_minutes / 60,
            "created_at": self.created_at.isoformat()
        }


class ExecutionPlanner:
    """
    ExecutionPlanner generates detailed execution plans with user approval workflows
    
    This planner creates comprehensive execution plans from workflow plans, including
    detailed task breakdowns, resource analysis, risk assessment, and verification
    gates for user approval. Supports plan modification and approval tracking.
    """
    
    def __init__(self, planner_id: Optional[str] = None):
        """Initialize the ExecutionPlanner"""
        self.planner_id = planner_id or str(uuid4())
        self.logger = StructuredLogger(
            name="orchestration.engine.ExecutionPlanner",
            component="ExecutionPlanner",
            agent_id=self.planner_id
        )
        
        # Initialize audit trail
        self.audit_trail = get_audit_trail()
        
        # Plan storage
        self.execution_plans: Dict[str, ExecutionPlanDetails] = {}
        self.approval_workflows: Dict[str, ApprovalWorkflow] = {}
        
        # Configuration
        self.default_buffer_percentage = 0.2  # 20% buffer time
        self.max_parallel_agents = 5
        self.default_approval_timeout_hours = 24
        
        self.logger.info("ExecutionPlanner initialized", planner_id=self.planner_id)
        self.audit_trail.log_agent_event(
            agent_id=self.planner_id,
            event="ExecutionPlanner initialized",
            category="planner_lifecycle",
            severity="info"
        )
    
    def generate_execution_plan(
        self,
        workflow_plan: WorkflowPlan,
        request: Optional[ClarifiedRequest] = None,
        validation_level: PlanValidationLevel = PlanValidationLevel.STANDARD
    ) -> ExecutionPlanDetails:
        """
        Generate detailed execution plan from workflow plan
        
        Args:
            workflow_plan: The workflow plan to detail
            request: Optional original request for context
            validation_level: Level of validation to apply
            
        Returns:
            ExecutionPlanDetails with comprehensive plan breakdown
            
        Raises:
            WorkflowEngineError: If plan generation fails
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(
                "Generating execution plan",
                plan_id=workflow_plan.id,
                agent_count=len(workflow_plan.agents),
                validation_level=validation_level.value
            )
            
            # Determine plan complexity
            complexity = self._assess_plan_complexity(workflow_plan)
            
            # Create execution plan details
            execution_plan = ExecutionPlanDetails(
                plan_id=workflow_plan.id,
                complexity=complexity,
                validation_level=validation_level
            )
            
            # Generate task breakdown
            self._generate_task_breakdown(execution_plan, workflow_plan)
            
            # Analyze resource requirements
            self._analyze_resource_requirements(execution_plan, workflow_plan)
            
            # Perform risk assessment
            self._perform_risk_assessment(execution_plan, workflow_plan)
            
            # Create quality checkpoints
            self._create_quality_checkpoints(execution_plan, workflow_plan)
            
            # Calculate timeline with buffers
            self._calculate_timeline(execution_plan, workflow_plan)
            
            # Store the execution plan
            self.execution_plans[execution_plan.id] = execution_plan
            
            generation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.info(
                "Execution plan generated",
                plan_id=workflow_plan.id,
                execution_plan_id=execution_plan.id,
                complexity=complexity.value,
                total_tasks=execution_plan.total_tasks,
                generation_time_ms=generation_time_ms
            )
            
            # Log with audit trail
            self.audit_trail.log_agent_event(
                agent_id=self.planner_id,
                event="Execution plan generated",
                category="plan_generation",
                severity="info",
                metadata={
                    "plan_id": workflow_plan.id,
                    "execution_plan_id": execution_plan.id,
                    "complexity": complexity.value,
                    "validation_level": validation_level.value,
                    "total_tasks": execution_plan.total_tasks,
                    "generation_time_ms": generation_time_ms
                }
            )
            
            return execution_plan
            
        except Exception as e:
            generation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.error(
                "Failed to generate execution plan",
                plan_id=workflow_plan.id,
                error=str(e),
                generation_time_ms=generation_time_ms
            )
            
            self.audit_trail.log_error(
                error=e,
                agent_id=self.planner_id,
                operation="execution_plan_generation",
                context={
                    "plan_id": workflow_plan.id,
                    "generation_time_ms": generation_time_ms
                }
            )
            
            raise WorkflowEngineError(
                f"Failed to generate execution plan: {str(e)}",
                plan_id=workflow_plan.id,
                planner_id=self.planner_id,
                cause=e
            )
    
    def create_approval_workflow(
        self,
        execution_plan: ExecutionPlanDetails,
        workflow_plan: WorkflowPlan,
        approval_level: ApprovalLevel = ApprovalLevel.USER
    ) -> ApprovalWorkflow:
        """
        Create user approval workflow for execution plan
        
        Args:
            execution_plan: The detailed execution plan
            workflow_plan: The original workflow plan
            approval_level: Required approval level
            
        Returns:
            ApprovalWorkflow with verification gates
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(
                "Creating approval workflow",
                execution_plan_id=execution_plan.id,
                plan_id=workflow_plan.id,
                approval_level=approval_level.value
            )
            
            # Create approval workflow
            approval_workflow = ApprovalWorkflow(
                plan_id=workflow_plan.id
            )
            
            # Create verification gates based on complexity and validation level
            gates = self._create_verification_gates(
                execution_plan, workflow_plan, approval_level
            )
            
            for gate in gates:
                approval_workflow.add_gate(gate)
            
            # Store the approval workflow
            self.approval_workflows[approval_workflow.id] = approval_workflow
            
            creation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.info(
                "Approval workflow created",
                workflow_id=approval_workflow.id,
                execution_plan_id=execution_plan.id,
                gates_count=len(gates),
                creation_time_ms=creation_time_ms
            )
            
            # Log with audit trail
            self.audit_trail.log_agent_event(
                agent_id=self.planner_id,
                event="Approval workflow created",
                category="approval_workflow",
                severity="info",
                metadata={
                    "workflow_id": approval_workflow.id,
                    "execution_plan_id": execution_plan.id,
                    "plan_id": workflow_plan.id,
                    "approval_level": approval_level.value,
                    "gates_count": len(gates),
                    "creation_time_ms": creation_time_ms
                }
            )
            
            return approval_workflow
            
        except Exception as e:
            creation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.error(
                "Failed to create approval workflow",
                execution_plan_id=execution_plan.id,
                error=str(e),
                creation_time_ms=creation_time_ms
            )
            
            self.audit_trail.log_error(
                error=e,
                agent_id=self.planner_id,
                operation="approval_workflow_creation",
                context={
                    "execution_plan_id": execution_plan.id,
                    "creation_time_ms": creation_time_ms
                }
            )
            
            raise WorkflowEngineError(
                f"Failed to create approval workflow: {str(e)}",
                plan_id=workflow_plan.id,
                planner_id=self.planner_id,
                cause=e
            )
    
    def validate_execution_plan(
        self,
        execution_plan: ExecutionPlanDetails,
        workflow_plan: WorkflowPlan
    ) -> ValidationResult:
        """
        Validate execution plan for completeness and feasibility
        
        Args:
            execution_plan: The execution plan to validate
            workflow_plan: The original workflow plan
            
        Returns:
            ValidationResult with validation status and issues
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(
                "Validating execution plan",
                execution_plan_id=execution_plan.id,
                plan_id=workflow_plan.id
            )
            
            result = ValidationResult(is_valid=True)
            
            # Validate task breakdown
            self._validate_task_breakdown(execution_plan, workflow_plan, result)
            
            # Validate resource allocation
            self._validate_resource_allocation(execution_plan, workflow_plan, result)
            
            # Validate dependencies
            self._validate_plan_dependencies(execution_plan, workflow_plan, result)
            
            # Validate timeline feasibility
            self._validate_timeline(execution_plan, workflow_plan, result)
            
            # Validate risk mitigation
            self._validate_risk_mitigation(execution_plan, result)
            
            validation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.info(
                "Execution plan validation completed",
                execution_plan_id=execution_plan.id,
                is_valid=result.is_valid,
                issues_count=len(result.missing_prerequisites) + len(result.warnings),
                validation_time_ms=validation_time_ms
            )
            
            # Log with audit trail
            self.audit_trail.log_agent_event(
                agent_id=self.planner_id,
                event="Execution plan validated",
                category="plan_validation",
                severity="info" if result.is_valid else "warning",
                metadata={
                    "execution_plan_id": execution_plan.id,
                    "plan_id": workflow_plan.id,
                    "is_valid": result.is_valid,
                    "missing_prerequisites": len(result.missing_prerequisites),
                    "warnings": len(result.warnings),
                    "validation_time_ms": validation_time_ms
                }
            )
            
            return result
            
        except Exception as e:
            validation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.error(
                "Failed to validate execution plan",
                execution_plan_id=execution_plan.id,
                error=str(e),
                validation_time_ms=validation_time_ms
            )
            
            self.audit_trail.log_error(
                error=e,
                agent_id=self.planner_id,
                operation="execution_plan_validation",
                context={
                    "execution_plan_id": execution_plan.id,
                    "validation_time_ms": validation_time_ms
                }
            )
            
            raise WorkflowValidationError(
                f"Failed to validate execution plan: {str(e)}",
                plan_id=workflow_plan.id,
                planner_id=self.planner_id,
                cause=e
            )
    
    def modify_execution_plan(
        self,
        execution_plan_id: str,
        modification: PlanModification,
        requester: str
    ) -> ExecutionPlanDetails:
        """
        Apply modification to execution plan
        
        Args:
            execution_plan_id: ID of the execution plan to modify
            modification: The modification to apply
            requester: User requesting the modification
            
        Returns:
            Updated ExecutionPlanDetails
            
        Raises:
            WorkflowEngineError: If modification fails
        """
        start_time = datetime.now()
        
        try:
            execution_plan = self.execution_plans.get(execution_plan_id)
            if not execution_plan:
                raise WorkflowEngineError(
                    f"Execution plan {execution_plan_id} not found",
                    planner_id=self.planner_id
                )
            
            self.logger.info(
                "Applying plan modification",
                execution_plan_id=execution_plan_id,
                modification_type=modification.modification_type.value,
                requester=requester
            )
            
            # Apply the modification based on type
            self._apply_modification(execution_plan, modification)
            
            # Update modification metadata
            modification.requested_by = requester
            
            # Calculate impact assessment
            modification.impact_assessment = self._assess_modification_impact(
                execution_plan, modification
            )
            
            # Update approval workflow if exists
            workflow_id = next(
                (wf_id for wf_id, wf in self.approval_workflows.items() 
                 if wf.plan_id == execution_plan.plan_id),
                None
            )
            
            if workflow_id:
                workflow = self.approval_workflows[workflow_id]
                workflow.apply_modification(modification)
            
            modification_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.info(
                "Plan modification applied",
                execution_plan_id=execution_plan_id,
                modification_id=modification.id,
                impact_summary=modification.get_impact_summary(),
                modification_time_ms=modification_time_ms
            )
            
            # Log with audit trail
            self.audit_trail.log_agent_event(
                agent_id=self.planner_id,
                event="Plan modification applied",
                category="plan_modification",
                severity="info",
                metadata={
                    "execution_plan_id": execution_plan_id,
                    "modification_id": modification.id,
                    "modification_type": modification.modification_type.value,
                    "requester": requester,
                    "impact_assessment": modification.impact_assessment,
                    "modification_time_ms": modification_time_ms
                }
            )
            
            return execution_plan
            
        except Exception as e:
            modification_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.error(
                "Failed to apply plan modification",
                execution_plan_id=execution_plan_id,
                error=str(e),
                modification_time_ms=modification_time_ms
            )
            
            self.audit_trail.log_error(
                error=e,
                agent_id=self.planner_id,
                operation="plan_modification",
                context={
                    "execution_plan_id": execution_plan_id,
                    "modification_time_ms": modification_time_ms
                }
            )
            
            raise WorkflowEngineError(
                f"Failed to apply plan modification: {str(e)}",
                plan_id=execution_plan.plan_id,
                planner_id=self.planner_id,
                cause=e
            )
    
    def get_execution_plan(self, execution_plan_id: str) -> Optional[ExecutionPlanDetails]:
        """Get execution plan by ID"""
        return self.execution_plans.get(execution_plan_id)
    
    def get_approval_workflow(self, workflow_id: str) -> Optional[ApprovalWorkflow]:
        """Get approval workflow by ID"""
        return self.approval_workflows.get(workflow_id)
    
    def list_execution_plans(self) -> List[ExecutionPlanDetails]:
        """List all execution plans"""
        return list(self.execution_plans.values())
    
    def list_approval_workflows(self) -> List[ApprovalWorkflow]:
        """List all approval workflows"""
        return list(self.approval_workflows.values())
    
    def get_planner_metrics(self) -> Dict[str, Any]:
        """Get planner performance metrics"""
        total_plans = len(self.execution_plans)
        total_workflows = len(self.approval_workflows)
        
        # Calculate complexity distribution
        complexity_counts = {}
        for plan in self.execution_plans.values():
            complexity = plan.complexity.value
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
        
        # Calculate approval status distribution
        status_counts = {}
        for workflow in self.approval_workflows.values():
            status = workflow.workflow_status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "planner_id": self.planner_id,
            "total_execution_plans": total_plans,
            "total_approval_workflows": total_workflows,
            "complexity_distribution": complexity_counts,
            "approval_status_distribution": status_counts,
            "average_tasks_per_plan": (
                sum(plan.total_tasks for plan in self.execution_plans.values()) / total_plans
                if total_plans > 0 else 0
            )
        }
    
    # Private helper methods
    
    def _assess_plan_complexity(self, workflow_plan: WorkflowPlan) -> PlanComplexity:
        """Assess the complexity of a workflow plan"""
        # Simple heuristic based on agents, dependencies, and resources
        agent_count = len(workflow_plan.agents)
        dependency_count = len(workflow_plan.dependencies)
        resource_count = len(workflow_plan.required_resources)
        
        complexity_score = agent_count + (dependency_count * 0.5) + (resource_count * 0.3)
        
        if complexity_score <= 3:
            return PlanComplexity.SIMPLE
        elif complexity_score <= 6:
            return PlanComplexity.MODERATE
        elif complexity_score <= 10:
            return PlanComplexity.COMPLEX
        else:
            return PlanComplexity.ENTERPRISE
    
    def _generate_task_breakdown(
        self,
        execution_plan: ExecutionPlanDetails,
        workflow_plan: WorkflowPlan
    ):
        """Generate detailed task breakdown"""
        task_id_counter = 1
        
        for agent_assignment in workflow_plan.agents:
            agent_type = agent_assignment.agent_type
            
            # Generate tasks for each agent type
            agent_tasks = self._get_agent_tasks(agent_type)
            
            for task_name in agent_tasks:
                task_id = f"task_{task_id_counter:03d}_{agent_type.value}_{task_name.lower().replace(' ', '_')}"
                
                task_details = {
                    "id": task_id,
                    "name": task_name,
                    "agent_type": agent_type.value,
                    "estimated_duration": agent_assignment.estimated_duration // len(agent_tasks),
                    "priority": agent_assignment.priority,
                    "dependencies": [],
                    "deliverables": self._get_task_deliverables(agent_type, task_name),
                    "success_criteria": self._get_task_success_criteria(agent_type, task_name)
                }
                
                execution_plan.task_breakdown[task_id] = task_details
                task_id_counter += 1
        
        execution_plan.total_tasks = len(execution_plan.task_breakdown)
        
        # Identify critical path (simplified)
        execution_plan.critical_path_tasks = self._identify_critical_path(
            execution_plan.task_breakdown, workflow_plan.dependencies
        )
        
        # Group parallel tasks
        execution_plan.parallel_task_groups = self._identify_parallel_groups(
            execution_plan.task_breakdown, workflow_plan.dependencies
        )
    
    def _analyze_resource_requirements(
        self,
        execution_plan: ExecutionPlanDetails,
        workflow_plan: WorkflowPlan
    ):
        """Analyze resource requirements and usage patterns"""
        # Calculate peak resource usage
        for resource in workflow_plan.required_resources:
            execution_plan.peak_resource_usage[resource.resource_type] = resource.amount
        
        # Create resource timeline (simplified)
        timeline_entry = {
            "timestamp": datetime.now().isoformat(),
            "resources": {r.resource_type: r.amount for r in workflow_plan.required_resources}
        }
        execution_plan.resource_timeline.append(timeline_entry)
        
        # Calculate cost breakdown
        for resource in workflow_plan.required_resources:
            execution_plan.cost_breakdown[resource.resource_type] = resource.estimated_cost
    
    def _perform_risk_assessment(
        self,
        execution_plan: ExecutionPlanDetails,
        workflow_plan: WorkflowPlan
    ):
        """Perform risk assessment for the execution plan"""
        # Identify common risks based on plan characteristics
        risks = []
        
        # Resource availability risk
        if len(workflow_plan.required_resources) > 3:
            risks.append({
                "id": "resource_availability",
                "description": "High resource requirements may lead to availability issues",
                "probability": 0.3,
                "impact": 0.7,
                "category": "resource"
            })
        
        # Agent coordination risk
        if len(workflow_plan.agents) > 3:
            risks.append({
                "id": "agent_coordination",
                "description": "Multiple agents may have coordination challenges",
                "probability": 0.4,
                "impact": 0.6,
                "category": "coordination"
            })
        
        # Timeline risk
        if workflow_plan.estimated_duration > 480:  # 8 hours
            risks.append({
                "id": "timeline_overrun",
                "description": "Long duration increases risk of timeline overrun",
                "probability": 0.5,
                "impact": 0.5,
                "category": "timeline"
            })
        
        execution_plan.identified_risks = risks
        
        # Create mitigation strategies
        for risk in risks:
            mitigation = {
                "risk_id": risk["id"],
                "strategy": self._get_mitigation_strategy(risk),
                "owner": "project_manager",
                "timeline": "before_execution"
            }
            execution_plan.mitigation_strategies.append(mitigation)
        
        # Create contingency plans
        if execution_plan.complexity in [PlanComplexity.COMPLEX, PlanComplexity.ENTERPRISE]:
            contingency = {
                "trigger": "critical_path_delay",
                "action": "activate_backup_agents",
                "resources_required": ["additional_compute", "backup_agents"],
                "estimated_cost": sum(execution_plan.cost_breakdown.values()) * 0.2
            }
            execution_plan.contingency_plans.append(contingency)
    
    def _create_quality_checkpoints(
        self,
        execution_plan: ExecutionPlanDetails,
        workflow_plan: WorkflowPlan
    ):
        """Create quality checkpoints throughout the execution"""
        checkpoints = []
        
        # Add checkpoints based on orchestration pattern
        if workflow_plan.pattern == OrchestrationPattern.SEQUENTIAL_HANDOFF:
            checkpoints.extend([
                "agent_handoff_validation",
                "intermediate_deliverable_review",
                "final_output_validation"
            ])
        elif workflow_plan.pattern == OrchestrationPattern.PARALLEL_EXECUTION:
            checkpoints.extend([
                "parallel_task_synchronization",
                "output_integration_validation",
                "final_quality_review"
            ])
        
        execution_plan.quality_checkpoints = checkpoints
        
        # Define success metrics
        metrics = [
            {
                "name": "task_completion_rate",
                "target": 100.0,
                "unit": "percentage",
                "measurement": "automated"
            },
            {
                "name": "quality_score",
                "target": 0.8,
                "unit": "score",
                "measurement": "agent_evaluation"
            },
            {
                "name": "timeline_adherence",
                "target": 95.0,
                "unit": "percentage",
                "measurement": "automated"
            }
        ]
        execution_plan.success_metrics = metrics
    
    def _calculate_timeline(
        self,
        execution_plan: ExecutionPlanDetails,
        workflow_plan: WorkflowPlan
    ):
        """Calculate timeline with buffer time"""
        base_duration = workflow_plan.estimated_duration
        buffer_time = int(base_duration * self.default_buffer_percentage)
        
        execution_plan.buffer_time_minutes = buffer_time
        execution_plan.earliest_start = datetime.now()
        execution_plan.latest_finish = execution_plan.earliest_start + timedelta(
            minutes=base_duration + buffer_time
        )
    
    def _create_verification_gates(
        self,
        execution_plan: ExecutionPlanDetails,
        workflow_plan: WorkflowPlan,
        approval_level: ApprovalLevel
    ) -> List[VerificationGate]:
        """Create verification gates based on plan complexity"""
        gates = []
        
        # Plan Review Gate
        plan_review_gate = VerificationGate(
            name="Execution Plan Review",
            description="Review and approve the detailed execution plan",
            plan_id=workflow_plan.id,
            approval_level=approval_level,
            expires_at=datetime.now() + timedelta(hours=self.default_approval_timeout_hours)
        )
        
        # Add criteria based on complexity
        if execution_plan.complexity in [PlanComplexity.COMPLEX, PlanComplexity.ENTERPRISE]:
            plan_review_gate.add_criteria(ApprovalCriteria(
                name="Resource Approval",
                description="Approve resource allocation and costs",
                is_required=True,
                approval_level=ApprovalLevel.PROJECT_MANAGER,
                auto_approve_conditions=["cost < 1000", "duration <= 480"]
            ))
        
        plan_review_gate.add_criteria(ApprovalCriteria(
            name="Timeline Approval",
            description="Approve estimated timeline and milestones",
            is_required=True,
            auto_approve_conditions=["duration <= 240"]  # Auto-approve if under 4 hours
        ))
        
        gates.append(plan_review_gate)
        
        # Risk Assessment Gate (for complex plans)
        if execution_plan.complexity in [PlanComplexity.COMPLEX, PlanComplexity.ENTERPRISE]:
            risk_gate = VerificationGate(
                name="Risk Assessment Review",
                description="Review identified risks and mitigation strategies",
                plan_id=workflow_plan.id,
                approval_level=approval_level
            )
            
            risk_gate.add_criteria(ApprovalCriteria(
                name="Risk Mitigation",
                description="Approve risk mitigation strategies",
                is_required=True,
                approval_level=ApprovalLevel.TECHNICAL_LEAD
            ))
            
            gates.append(risk_gate)
        
        # Final Approval Gate
        final_gate = VerificationGate(
            name="Final Execution Approval",
            description="Final approval to proceed with execution",
            plan_id=workflow_plan.id,
            approval_level=approval_level
        )
        
        final_gate.add_criteria(ApprovalCriteria(
            name="Execution Authorization",
            description="Authorize plan execution",
            is_required=True
        ))
        
        gates.append(final_gate)
        
        return gates
    
    def _validate_task_breakdown(
        self,
        execution_plan: ExecutionPlanDetails,
        workflow_plan: WorkflowPlan,
        result: ValidationResult
    ):
        """Validate task breakdown completeness"""
        if execution_plan.total_tasks == 0:
            result.add_missing_prerequisite("No tasks defined in execution plan")
        
        # Check if all agents have tasks
        agent_types = {agent.agent_type for agent in workflow_plan.agents}
        task_agent_types = {
            AgentType(task["agent_type"]) 
            for task in execution_plan.task_breakdown.values()
        }
        
        missing_agents = agent_types - task_agent_types
        for agent_type in missing_agents:
            result.add_warning(f"No tasks defined for agent type: {agent_type.value}")
    
    def _validate_resource_allocation(
        self,
        execution_plan: ExecutionPlanDetails,
        workflow_plan: WorkflowPlan,
        result: ValidationResult
    ):
        """Validate resource allocation"""
        if not execution_plan.peak_resource_usage:
            result.add_warning("No resource usage analysis available")
        
        # Check for resource conflicts
        total_cost = sum(execution_plan.cost_breakdown.values())
        if total_cost > 10000:  # Arbitrary threshold
            result.add_warning(f"High estimated cost: ${total_cost:.2f}")
    
    def _validate_plan_dependencies(
        self,
        execution_plan: ExecutionPlanDetails,
        workflow_plan: WorkflowPlan,
        result: ValidationResult
    ):
        """Validate plan dependencies"""
        if not execution_plan.critical_path_tasks:
            result.add_warning("Critical path not identified")
        
        # Check for circular dependencies in task breakdown
        # This is a simplified check
        task_deps = {}
        for task_id, task in execution_plan.task_breakdown.items():
            task_deps[task_id] = task.get("dependencies", [])
        
        # Simple cycle detection would go here
        # For now, just check for self-dependencies
        for task_id, deps in task_deps.items():
            if task_id in deps:
                result.add_missing_prerequisite(f"Self-dependency detected in task: {task_id}")
    
    def _validate_timeline(
        self,
        execution_plan: ExecutionPlanDetails,
        workflow_plan: WorkflowPlan,
        result: ValidationResult
    ):
        """Validate timeline feasibility"""
        if not execution_plan.earliest_start or not execution_plan.latest_finish:
            result.add_missing_prerequisite("Timeline not calculated")
        
        if execution_plan.buffer_time_minutes < 30:  # Less than 30 minutes buffer
            result.add_warning("Very low buffer time may lead to timeline issues")
    
    def _validate_risk_mitigation(
        self,
        execution_plan: ExecutionPlanDetails,
        result: ValidationResult
    ):
        """Validate risk mitigation strategies"""
        high_risk_count = sum(
            1 for risk in execution_plan.identified_risks
            if risk.get("probability", 0) * risk.get("impact", 0) > 0.5
        )
        
        if high_risk_count > len(execution_plan.mitigation_strategies):
            result.add_warning("Not all high-risk items have mitigation strategies")
    
    def _apply_modification(
        self,
        execution_plan: ExecutionPlanDetails,
        modification: PlanModification
    ):
        """Apply a modification to the execution plan"""
        if modification.modification_type == ModificationType.TIMELINE_CHANGE:
            if modification.new_value and isinstance(modification.new_value, int):
                # Update buffer time
                execution_plan.buffer_time_minutes = modification.new_value
                if execution_plan.earliest_start:
                    execution_plan.latest_finish = execution_plan.earliest_start + timedelta(
                        minutes=execution_plan.buffer_time_minutes
                    )
        
        elif modification.modification_type == ModificationType.RESOURCE_ADJUSTMENT:
            if modification.new_value and isinstance(modification.new_value, dict):
                # Update resource allocation
                execution_plan.peak_resource_usage.update(modification.new_value)
        
        elif modification.modification_type == ModificationType.SCOPE_MODIFICATION:
            if modification.new_value and isinstance(modification.new_value, dict):
                # Update task breakdown
                execution_plan.task_breakdown.update(modification.new_value)
                execution_plan.total_tasks = len(execution_plan.task_breakdown)
        
        # Add more modification types as needed
    
    def _assess_modification_impact(
        self,
        execution_plan: ExecutionPlanDetails,
        modification: PlanModification
    ) -> Dict[str, Any]:
        """Assess the impact of a modification"""
        impact = {}
        
        if modification.modification_type == ModificationType.TIMELINE_CHANGE:
            old_buffer = modification.old_value or 0
            new_buffer = modification.new_value or 0
            impact["duration_change"] = new_buffer - old_buffer
        
        elif modification.modification_type == ModificationType.RESOURCE_ADJUSTMENT:
            # Calculate cost impact
            old_cost = sum(execution_plan.cost_breakdown.values())
            # This is simplified - in practice, you'd calculate the actual cost change
            impact["cost_change"] = old_cost * 0.1  # Assume 10% change
        
        # Assess risk level
        if modification.modification_type in [
            ModificationType.SCOPE_MODIFICATION,
            ModificationType.AGENT_CHANGE
        ]:
            impact["risk_level"] = "medium"
        else:
            impact["risk_level"] = "low"
        
        return impact
    
    # Helper methods for task generation
    
    def _get_agent_tasks(self, agent_type: AgentType) -> List[str]:
        """Get typical tasks for an agent type"""
        task_mapping = {
            AgentType.PM: [
                "Requirements Analysis",
                "Stakeholder Communication",
                "Project Planning",
                "Risk Assessment"
            ],
            AgentType.BA: [
                "Business Process Analysis",
                "Requirements Documentation",
                "Stakeholder Impact Analysis",
                "Business Rules Definition"
            ],
            AgentType.SA: [
                "Architecture Design",
                "Component Specification",
                "Integration Planning",
                "Technical Documentation"
            ],
            AgentType.RESEARCH: [
                "Information Gathering",
                "Technology Research",
                "Best Practices Analysis",
                "Recommendation Generation"
            ],
            AgentType.QUALITY_JUDGE: [
                "Quality Assessment",
                "Code Review",
                "Test Planning",
                "Performance Evaluation"
            ],
            AgentType.IMPLEMENTATION: [
                "Code Development",
                "Unit Testing",
                "Integration Testing",
                "Documentation Updates"
            ]
        }
        
        return task_mapping.get(agent_type, ["Generic Task"])
    
    def _get_task_deliverables(self, agent_type: AgentType, task_name: str) -> List[str]:
        """Get expected deliverables for a task"""
        # Simplified deliverable mapping
        if "Analysis" in task_name:
            return ["Analysis Report", "Recommendations"]
        elif "Design" in task_name:
            return ["Design Document", "Architecture Diagrams"]
        elif "Development" in task_name or "Implementation" in task_name:
            return ["Source Code", "Unit Tests"]
        elif "Testing" in task_name:
            return ["Test Results", "Test Report"]
        else:
            return ["Task Output", "Documentation"]
    
    def _get_task_success_criteria(self, agent_type: AgentType, task_name: str) -> List[str]:
        """Get success criteria for a task"""
        # Simplified success criteria
        return [
            "Task completed within estimated time",
            "Deliverables meet quality standards",
            "All requirements addressed"
        ]
    
    def _identify_critical_path(
        self,
        task_breakdown: Dict[str, Dict[str, Any]],
        dependencies: List[TaskDependency]
    ) -> List[str]:
        """Identify critical path tasks (simplified)"""
        # This is a simplified implementation
        # In practice, you'd use proper critical path method (CPM)
        
        # For now, just return tasks with the longest estimated duration
        sorted_tasks = sorted(
            task_breakdown.items(),
            key=lambda x: x[1].get("estimated_duration", 0),
            reverse=True
        )
        
        # Return top 3 longest tasks as critical path
        return [task_id for task_id, _ in sorted_tasks[:3]]
    
    def _identify_parallel_groups(
        self,
        task_breakdown: Dict[str, Dict[str, Any]],
        dependencies: List[TaskDependency]
    ) -> List[List[str]]:
        """Identify groups of tasks that can run in parallel"""
        # Simplified parallel group identification
        # Group tasks by agent type that don't have dependencies
        
        agent_groups = {}
        for task_id, task in task_breakdown.items():
            agent_type = task["agent_type"]
            if agent_type not in agent_groups:
                agent_groups[agent_type] = []
            agent_groups[agent_type].append(task_id)
        
        # Return groups with more than one task
        return [tasks for tasks in agent_groups.values() if len(tasks) > 1]
    
    def _get_mitigation_strategy(self, risk: Dict[str, Any]) -> str:
        """Get mitigation strategy for a risk"""
        strategy_mapping = {
            "resource_availability": "Pre-allocate resources and maintain backup options",
            "agent_coordination": "Implement regular sync meetings and clear communication protocols",
            "timeline_overrun": "Add buffer time and implement milestone tracking"
        }
        
        return strategy_mapping.get(
            risk["id"],
            "Monitor risk and implement corrective actions as needed"
        )