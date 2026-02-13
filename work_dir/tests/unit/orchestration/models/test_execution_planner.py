"""
Unit tests for ExecutionPlanner

Tests the execution plan generation, user approval workflows, and plan modification
capabilities of the ExecutionPlanner class.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from agentic_sdlc.orchestration.engine.execution_planner import (
    ExecutionPlanner, ExecutionPlanDetails, PlanComplexity, PlanValidationLevel
)
from agentic_sdlc.orchestration.models import (
    WorkflowPlan, OrchestrationPattern, AgentType, AgentAssignment,
    TaskDependency, ResourceRequirement, ValidationResult
)
from agentic_sdlc.orchestration.models.verification import (
    VerificationGate, ApprovalWorkflow, ApprovalCriteria, ApprovalLevel, VerificationStatus,
    PlanModification, ModificationType, UserFeedback
)
from agentic_sdlc.orchestration.utils.audit_trail import setup_audit_trail


class TestExecutionPlanner:
    """Test cases for ExecutionPlanner"""
    
    @pytest.fixture(scope="function")
    def temp_audit_dir(self):
        """Create temporary directory for audit trail during tests"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def planner(self, temp_audit_dir):
        """Create ExecutionPlanner instance for testing with isolated audit trail"""
        # Setup isolated audit trail for this test
        audit_trail = setup_audit_trail(storage_path=temp_audit_dir)
        
        # Create planner with isolated audit trail
        planner = ExecutionPlanner()
        planner.audit_trail = audit_trail
        
        return planner
    
    @pytest.fixture
    def sample_workflow_plan(self):
        """Create sample WorkflowPlan for testing"""
        agents = [
            AgentAssignment(
                agent_type=AgentType.PM,
                priority=1,
                estimated_duration=120
            ),
            AgentAssignment(
                agent_type=AgentType.BA,
                priority=1,
                estimated_duration=180
            ),
            AgentAssignment(
                agent_type=AgentType.IMPLEMENTATION,
                priority=2,
                estimated_duration=240
            )
        ]
        
        dependencies = [
            TaskDependency(
                dependent_task_id="task_ba",
                prerequisite_task_id="task_pm",
                dependency_type="completion",
                is_blocking=True
            )
        ]
        
        resources = [
            ResourceRequirement(
                resource_type="cpu_cores",
                amount=4.0,
                unit="cores",
                estimated_cost=40.0,
                is_critical=True
            ),
            ResourceRequirement(
                resource_type="memory",
                amount=8.0,
                unit="GB",
                estimated_cost=20.0,
                is_critical=True
            )
        ]
        
        return WorkflowPlan(
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            agents=agents,
            dependencies=dependencies,
            estimated_duration=540,  # 9 hours
            required_resources=resources,
            priority=1
        )
    
    def test_planner_initialization(self, planner):
        """Test ExecutionPlanner initialization"""
        assert planner.planner_id is not None
        assert planner.execution_plans == {}
        assert planner.approval_workflows == {}
        assert planner.default_buffer_percentage == 0.2
        assert planner.max_parallel_agents == 5
        assert planner.default_approval_timeout_hours == 24
    
    def test_generate_execution_plan_simple(self, planner, sample_workflow_plan):
        """Test execution plan generation for simple workflow"""
        # Modify plan to be simple
        sample_workflow_plan.agents = sample_workflow_plan.agents[:1]  # Only PM
        sample_workflow_plan.dependencies = []
        sample_workflow_plan.required_resources = sample_workflow_plan.required_resources[:1]
        
        execution_plan = planner.generate_execution_plan(
            sample_workflow_plan,
            validation_level=PlanValidationLevel.BASIC
        )
        
        assert execution_plan is not None
        assert execution_plan.plan_id == sample_workflow_plan.id
        assert execution_plan.complexity == PlanComplexity.SIMPLE
        assert execution_plan.validation_level == PlanValidationLevel.BASIC
        assert execution_plan.total_tasks > 0
        assert execution_plan.buffer_time_minutes > 0
        assert execution_plan.earliest_start is not None
        assert execution_plan.latest_finish is not None
        
        # Check that plan is stored
        assert execution_plan.id in planner.execution_plans
    
    def test_generate_execution_plan_complex(self, planner, sample_workflow_plan):
        """Test execution plan generation for complex workflow"""
        execution_plan = planner.generate_execution_plan(
            sample_workflow_plan,
            validation_level=PlanValidationLevel.COMPREHENSIVE
        )
        
        assert execution_plan.complexity in [PlanComplexity.MODERATE, PlanComplexity.COMPLEX]
        assert execution_plan.validation_level == PlanValidationLevel.COMPREHENSIVE
        assert len(execution_plan.task_breakdown) > 0
        assert len(execution_plan.identified_risks) > 0
        assert len(execution_plan.quality_checkpoints) > 0
        assert execution_plan.peak_resource_usage
        assert execution_plan.cost_breakdown
    
    def test_task_breakdown_generation(self, planner, sample_workflow_plan):
        """Test task breakdown generation"""
        execution_plan = planner.generate_execution_plan(sample_workflow_plan)
        
        # Check task breakdown structure
        assert execution_plan.total_tasks > 0
        assert len(execution_plan.task_breakdown) == execution_plan.total_tasks
        
        # Check that all agents have tasks
        agent_types_in_plan = {agent.agent_type for agent in sample_workflow_plan.agents}
        agent_types_in_tasks = {
            AgentType(task["agent_type"]) 
            for task in execution_plan.task_breakdown.values()
        }
        assert agent_types_in_plan.issubset(agent_types_in_tasks)
        
        # Check task structure
        for task_id, task in execution_plan.task_breakdown.items():
            assert "id" in task
            assert "name" in task
            assert "agent_type" in task
            assert "estimated_duration" in task
            assert "deliverables" in task
            assert "success_criteria" in task
    
    def test_resource_analysis(self, planner, sample_workflow_plan):
        """Test resource analysis"""
        execution_plan = planner.generate_execution_plan(sample_workflow_plan)
        
        # Check resource analysis
        assert execution_plan.peak_resource_usage
        assert execution_plan.resource_timeline
        assert execution_plan.cost_breakdown
        
        # Verify resource types match
        resource_types_in_plan = {r.resource_type for r in sample_workflow_plan.required_resources}
        resource_types_in_analysis = set(execution_plan.peak_resource_usage.keys())
        assert resource_types_in_plan == resource_types_in_analysis
    
    def test_risk_assessment(self, planner, sample_workflow_plan):
        """Test risk assessment"""
        execution_plan = planner.generate_execution_plan(sample_workflow_plan)
        
        # Check risk assessment
        assert isinstance(execution_plan.identified_risks, list)
        assert isinstance(execution_plan.mitigation_strategies, list)
        
        # For complex plans, should have risks
        if execution_plan.complexity in [PlanComplexity.COMPLEX, PlanComplexity.ENTERPRISE]:
            assert len(execution_plan.identified_risks) > 0
            assert len(execution_plan.mitigation_strategies) > 0
        
        # Check risk structure
        for risk in execution_plan.identified_risks:
            assert "id" in risk
            assert "description" in risk
            assert "probability" in risk
            assert "impact" in risk
            assert "category" in risk
        
        # Check mitigation structure
        for mitigation in execution_plan.mitigation_strategies:
            assert "risk_id" in mitigation
            assert "strategy" in mitigation
    
    def test_create_approval_workflow(self, planner, sample_workflow_plan):
        """Test approval workflow creation"""
        execution_plan = planner.generate_execution_plan(sample_workflow_plan)
        
        approval_workflow = planner.create_approval_workflow(
            execution_plan,
            sample_workflow_plan,
            ApprovalLevel.USER
        )
        
        assert approval_workflow is not None
        assert approval_workflow.plan_id == sample_workflow_plan.id
        assert len(approval_workflow.gates) > 0
        assert approval_workflow.workflow_status == VerificationStatus.PENDING
        
        # Check that workflow is stored
        assert approval_workflow.id in planner.approval_workflows
        
        # Check gate structure
        for gate in approval_workflow.gates:
            assert gate.plan_id == sample_workflow_plan.id
            assert gate.status == VerificationStatus.PENDING
            assert len(gate.criteria) > 0
    
    def test_verification_gates_by_complexity(self, planner):
        """Test that verification gates are created based on complexity"""
        # Simple plan
        simple_plan = WorkflowPlan(
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            agents=[AgentAssignment(agent_type=AgentType.PM, priority=1, estimated_duration=60)],
            estimated_duration=60
        )
        
        simple_execution_plan = planner.generate_execution_plan(simple_plan)
        simple_workflow = planner.create_approval_workflow(
            simple_execution_plan, simple_plan, ApprovalLevel.USER
        )
        
        # Complex plan
        complex_agents = [
            AgentAssignment(agent_type=AgentType.PM, priority=1, estimated_duration=120),
            AgentAssignment(agent_type=AgentType.BA, priority=1, estimated_duration=180),
            AgentAssignment(agent_type=AgentType.SA, priority=1, estimated_duration=240),
            AgentAssignment(agent_type=AgentType.IMPLEMENTATION, priority=2, estimated_duration=360),
            AgentAssignment(agent_type=AgentType.QUALITY_JUDGE, priority=2, estimated_duration=120)
        ]
        
        complex_plan = WorkflowPlan(
            pattern=OrchestrationPattern.PARALLEL_EXECUTION,
            agents=complex_agents,
            estimated_duration=1020,  # 17 hours
            required_resources=[
                ResourceRequirement("cpu_cores", 8.0, "cores", 80.0, True),
                ResourceRequirement("memory", 16.0, "GB", 40.0, True),
                ResourceRequirement("storage", 100.0, "GB", 10.0, False)
            ]
        )
        
        complex_execution_plan = planner.generate_execution_plan(complex_plan)
        complex_workflow = planner.create_approval_workflow(
            complex_execution_plan, complex_plan, ApprovalLevel.PROJECT_MANAGER
        )
        
        # Complex plans should have more gates
        assert len(complex_workflow.gates) >= len(simple_workflow.gates)
        
        # Complex plans should have risk assessment gates
        gate_names = [gate.name for gate in complex_workflow.gates]
        if complex_execution_plan.complexity in [PlanComplexity.COMPLEX, PlanComplexity.ENTERPRISE]:
            assert any("Risk" in name for name in gate_names)
    
    def test_validate_execution_plan(self, planner, sample_workflow_plan):
        """Test execution plan validation"""
        execution_plan = planner.generate_execution_plan(sample_workflow_plan)
        
        validation_result = planner.validate_execution_plan(execution_plan, sample_workflow_plan)
        
        assert isinstance(validation_result, ValidationResult)
        # For a well-formed plan, should be valid or have only warnings
        assert validation_result.is_valid or len(validation_result.warnings) > 0
    
    def test_plan_modification(self, planner, sample_workflow_plan):
        """Test plan modification"""
        execution_plan = planner.generate_execution_plan(sample_workflow_plan)
        
        # Create a timeline modification
        modification = PlanModification(
            plan_id=sample_workflow_plan.id,
            modification_type=ModificationType.TIMELINE_CHANGE,
            description="Increase buffer time",
            old_value=execution_plan.buffer_time_minutes,
            new_value=execution_plan.buffer_time_minutes + 60,
            reason="Additional time needed for quality assurance"
        )
        
        modified_plan = planner.modify_execution_plan(
            execution_plan.id,
            modification,
            "test_user"
        )
        
        assert modified_plan.buffer_time_minutes == modification.new_value
        assert modification.requested_by == "test_user"
        assert modification.impact_assessment is not None
    
    def test_plan_modification_with_workflow(self, planner, sample_workflow_plan):
        """Test plan modification with approval workflow"""
        execution_plan = planner.generate_execution_plan(sample_workflow_plan)
        approval_workflow = planner.create_approval_workflow(
            execution_plan, sample_workflow_plan, ApprovalLevel.USER
        )
        
        # Create modification
        modification = PlanModification(
            plan_id=sample_workflow_plan.id,
            modification_type=ModificationType.RESOURCE_ADJUSTMENT,
            description="Increase CPU allocation",
            old_value={"cpu_cores": 4.0},
            new_value={"cpu_cores": 6.0},
            reason="Performance requirements increased"
        )
        
        # Apply modification
        planner.modify_execution_plan(execution_plan.id, modification, "test_user")
        
        # Check that workflow was updated
        updated_workflow = planner.get_approval_workflow(approval_workflow.id)
        assert updated_workflow.total_modifications == 1
        assert updated_workflow.workflow_status == VerificationStatus.PENDING
    
    def test_get_planner_metrics(self, planner, sample_workflow_plan):
        """Test planner metrics"""
        # Generate some plans
        execution_plan1 = planner.generate_execution_plan(sample_workflow_plan)
        workflow1 = planner.create_approval_workflow(
            execution_plan1, sample_workflow_plan, ApprovalLevel.USER
        )
        
        # Create another plan
        simple_plan = WorkflowPlan(
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            agents=[AgentAssignment(agent_type=AgentType.PM, priority=1, estimated_duration=60)],
            estimated_duration=60
        )
        execution_plan2 = planner.generate_execution_plan(simple_plan)
        
        metrics = planner.get_planner_metrics()
        
        assert metrics["planner_id"] == planner.planner_id
        assert metrics["total_execution_plans"] == 2
        assert metrics["total_approval_workflows"] == 1
        assert "complexity_distribution" in metrics
        assert "approval_status_distribution" in metrics
        assert metrics["average_tasks_per_plan"] > 0
    
    def test_complexity_assessment(self, planner):
        """Test plan complexity assessment"""
        # Simple plan
        simple_plan = WorkflowPlan(
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            agents=[AgentAssignment(agent_type=AgentType.PM, priority=1, estimated_duration=60)],
            estimated_duration=60
        )
        
        simple_execution = planner.generate_execution_plan(simple_plan)
        assert simple_execution.complexity == PlanComplexity.SIMPLE
        
        # Complex plan
        complex_agents = [
            AgentAssignment(agent_type=AgentType.PM, priority=1, estimated_duration=120),
            AgentAssignment(agent_type=AgentType.BA, priority=1, estimated_duration=180),
            AgentAssignment(agent_type=AgentType.SA, priority=1, estimated_duration=240),
            AgentAssignment(agent_type=AgentType.IMPLEMENTATION, priority=2, estimated_duration=360),
            AgentAssignment(agent_type=AgentType.QUALITY_JUDGE, priority=2, estimated_duration=120),
            AgentAssignment(agent_type=AgentType.RESEARCH, priority=2, estimated_duration=180)
        ]
        
        complex_dependencies = [
            TaskDependency("task_2", "task_1", "completion", True),
            TaskDependency("task_3", "task_2", "completion", True),
            TaskDependency("task_4", "task_3", "data", False),
            TaskDependency("task_5", "task_4", "completion", True),
            TaskDependency("task_6", "task_1", "data", False)
        ]
        
        complex_resources = [
            ResourceRequirement("cpu_cores", 16.0, "cores", 160.0, True),
            ResourceRequirement("memory", 32.0, "GB", 80.0, True),
            ResourceRequirement("storage", 500.0, "GB", 50.0, False),
            ResourceRequirement("network", 10.0, "Gbps", 100.0, True)
        ]
        
        complex_plan = WorkflowPlan(
            pattern=OrchestrationPattern.HIERARCHICAL_DELEGATION,
            agents=complex_agents,
            dependencies=complex_dependencies,
            estimated_duration=1800,  # 30 hours
            required_resources=complex_resources
        )
        
        complex_execution = planner.generate_execution_plan(complex_plan)
        assert complex_execution.complexity in [PlanComplexity.COMPLEX, PlanComplexity.ENTERPRISE]
    
    def test_error_handling(self, planner):
        """Test error handling in ExecutionPlanner"""
        # Test with invalid plan
        with pytest.raises(Exception):
            planner.generate_execution_plan(None)
        
        # Test modification of non-existent plan
        modification = PlanModification(
            modification_type=ModificationType.TIMELINE_CHANGE,
            description="Test modification"
        )
        
        with pytest.raises(Exception):
            planner.modify_execution_plan("non_existent_id", modification, "test_user")
    
    def test_plan_summary(self, planner, sample_workflow_plan):
        """Test execution plan summary generation"""
        execution_plan = planner.generate_execution_plan(sample_workflow_plan)
        
        summary = execution_plan.get_summary()
        
        assert "complexity" in summary
        assert "validation_level" in summary
        assert "total_tasks" in summary
        assert "total_cost" in summary
        assert "identified_risks" in summary
        assert "created_at" in summary
        
        assert summary["total_tasks"] == execution_plan.total_tasks
        assert summary["complexity"] == execution_plan.complexity.value
    
    @patch('agentic_sdlc.orchestration.engine.execution_planner.get_audit_trail')
    def test_audit_trail_integration(self, mock_audit_trail, temp_audit_dir):
        """Test audit trail integration"""
        mock_audit = Mock()
        mock_audit_trail.return_value = mock_audit
        
        # Create new planner to trigger audit trail setup
        test_planner = ExecutionPlanner()
        
        # Create sample workflow plan for testing
        sample_workflow_plan = WorkflowPlan(
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            agents=[
                AgentAssignment(
                    agent_type=AgentType.PM,
                    priority=1,
                    estimated_duration=120
                )
            ],
            estimated_duration=120
        )
        
        # Generate execution plan
        execution_plan = test_planner.generate_execution_plan(sample_workflow_plan)
        
        # Verify audit trail calls
        assert mock_audit.log_agent_event.called
        
        # Check that initialization and generation events were logged
        call_args_list = mock_audit.log_agent_event.call_args_list
        events = [call[1]["event"] for call in call_args_list if len(call) > 1 and "event" in call[1]]
        
        assert "ExecutionPlanner initialized" in events
        assert "Execution plan generated" in events


class TestVerificationGate:
    """Test cases for VerificationGate"""
    
    @pytest.fixture
    def sample_gate(self):
        """Create sample VerificationGate for testing"""
        gate = VerificationGate(
            name="Test Gate",
            description="Test verification gate",
            plan_id="test_plan_123"
        )
        
        # Add some criteria
        gate.add_criteria(ApprovalCriteria(
            name="Cost Approval",
            description="Approve estimated costs",
            is_required=True,
            auto_approve_conditions=["cost < 1000"]
        ))
        
        return gate
    
    def test_gate_initialization(self, sample_gate):
        """Test VerificationGate initialization"""
        assert sample_gate.name == "Test Gate"
        assert sample_gate.status == VerificationStatus.PENDING
        assert len(sample_gate.criteria) == 1
        assert sample_gate.approved_by is None
    
    def test_gate_approval(self, sample_gate):
        """Test gate approval"""
        context = {"cost": 500}  # Under threshold
        
        sample_gate.approve("test_approver", context)
        
        assert sample_gate.status == VerificationStatus.APPROVED
        assert sample_gate.approved_by == "test_approver"
        assert sample_gate.approved_at is not None
    
    def test_gate_rejection(self, sample_gate):
        """Test gate rejection"""
        sample_gate.reject("test_rejector", "Cost too high")
        
        assert sample_gate.status == VerificationStatus.REJECTED
        assert sample_gate.approved_by == "test_rejector"
        assert sample_gate.rejection_reason == "Cost too high"
    
    def test_auto_approval_check(self, sample_gate):
        """Test auto-approval functionality"""
        # Set the gate to AUTOMATIC approval level for auto-approval to work
        sample_gate.approval_level = ApprovalLevel.AUTOMATIC
        
        # Should auto-approve with low cost
        context = {"cost": 500}
        assert sample_gate.can_auto_approve(context)
        
        # Should not auto-approve with high cost
        context = {"cost": 1500}
        assert not sample_gate.can_auto_approve(context)
    
    def test_feedback_management(self, sample_gate):
        """Test user feedback management"""
        feedback = UserFeedback(
            user_id="test_user",
            feedback_type="concern",
            content="Timeline seems too aggressive",
            priority=1
        )
        
        sample_gate.add_feedback(feedback)
        
        assert len(sample_gate.user_feedback) == 1
        assert len(sample_gate.get_pending_feedback()) == 1
        assert len(sample_gate.get_high_priority_feedback()) == 1
        
        # Mark feedback as addressed
        feedback.mark_addressed("Timeline adjusted based on feedback")
        
        assert len(sample_gate.get_pending_feedback()) == 0
        assert feedback.addressed
        assert feedback.response == "Timeline adjusted based on feedback"


class TestApprovalWorkflow:
    """Test cases for ApprovalWorkflow"""
    
    @pytest.fixture
    def sample_workflow(self):
        """Create sample ApprovalWorkflow for testing"""
        workflow = ApprovalWorkflow(plan_id="test_plan_123")
        
        # Add gates
        gate1 = VerificationGate(
            name="Initial Review",
            description="Initial plan review",
            plan_id="test_plan_123"
        )
        gate1.add_criteria(ApprovalCriteria(
            name="Basic Validation",
            description="Basic plan validation",
            is_required=True
        ))
        
        gate2 = VerificationGate(
            name="Final Approval",
            description="Final approval to proceed",
            plan_id="test_plan_123"
        )
        gate2.add_criteria(ApprovalCriteria(
            name="Executive Approval",
            description="Executive sign-off",
            is_required=True,
            approval_level=ApprovalLevel.PROJECT_MANAGER
        ))
        
        workflow.add_gate(gate1)
        workflow.add_gate(gate2)
        
        return workflow
    
    def test_workflow_initialization(self, sample_workflow):
        """Test ApprovalWorkflow initialization"""
        assert sample_workflow.plan_id == "test_plan_123"
        assert len(sample_workflow.gates) == 2
        assert sample_workflow.current_gate_index == 0
        assert sample_workflow.workflow_status == VerificationStatus.PENDING
    
    def test_workflow_progression(self, sample_workflow):
        """Test workflow progression through gates"""
        # Get current gate and approve it
        current_gate = sample_workflow.get_current_gate()
        assert current_gate.name == "Initial Review"
        
        # Process approval decision with proper context
        context = {"cost": 500, "duration": 240}  # Provide context for criteria evaluation
        sample_workflow.process_gate_decision(
            current_gate.id, "approve", "test_user", "Looks good", context
        )
        
        # Should advance to next gate
        assert sample_workflow.current_gate_index == 1
        current_gate = sample_workflow.get_current_gate()
        assert current_gate.name == "Final Approval"
        
        # Approve final gate with context
        sample_workflow.process_gate_decision(
            current_gate.id, "approve", "project_manager", "Approved for execution", context
        )
        
        # Workflow should be complete
        assert sample_workflow.workflow_status == VerificationStatus.APPROVED
        assert sample_workflow.is_complete()
        assert sample_workflow.can_proceed_to_execution()
    
    def test_workflow_rejection(self, sample_workflow):
        """Test workflow rejection"""
        current_gate = sample_workflow.get_current_gate()
        
        sample_workflow.process_gate_decision(
            current_gate.id, "reject", "test_user", "Requirements unclear"
        )
        
        assert sample_workflow.workflow_status == VerificationStatus.REJECTED
        assert sample_workflow.is_complete()
        assert not sample_workflow.can_proceed_to_execution()
    
    def test_modification_request(self, sample_workflow):
        """Test modification request handling"""
        current_gate = sample_workflow.get_current_gate()
        
        sample_workflow.process_gate_decision(
            current_gate.id, "modify", "test_user", "Need to adjust timeline"
        )
        
        assert sample_workflow.workflow_status == VerificationStatus.REQUIRES_MODIFICATION
        
        # Apply modification
        modification = PlanModification(
            plan_id="test_plan_123",
            modification_type=ModificationType.TIMELINE_CHANGE,
            description="Extended timeline",
            reason="User requested more time"
        )
        
        sample_workflow.apply_modification(modification)
        
        assert sample_workflow.total_modifications == 1
        assert sample_workflow.workflow_status == VerificationStatus.PENDING
    
    def test_workflow_summary(self, sample_workflow):
        """Test workflow summary generation"""
        summary = sample_workflow.get_workflow_summary()
        
        assert summary["workflow_id"] == sample_workflow.id
        assert summary["plan_id"] == "test_plan_123"
        assert summary["status"] == VerificationStatus.PENDING.value
        assert summary["progress"]["total_gates"] == 2
        assert summary["progress"]["completed_gates"] == 0
        assert summary["progress"]["current_gate"] == 0
        assert summary["modifications"] == 0
    
    def test_approval_history(self, sample_workflow):
        """Test approval history tracking"""
        current_gate = sample_workflow.get_current_gate()
        
        # Make several decisions with proper context
        context = {"cost": 500, "duration": 240}
        sample_workflow.process_gate_decision(
            current_gate.id, "approve", "user1", "Initial approval", context
        )
        
        current_gate = sample_workflow.get_current_gate()
        sample_workflow.process_gate_decision(
            current_gate.id, "approve", "user2", "Final approval", context
        )
        
        # Check history
        assert len(sample_workflow.approval_history) == 2
        
        history_entry = sample_workflow.approval_history[0]
        assert history_entry["decision"] == "approve"
        assert history_entry["user"] == "user1"
        assert history_entry["reason"] == "Initial approval"
        assert "timestamp" in history_entry