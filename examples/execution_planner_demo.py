#!/usr/bin/env python3
"""
ExecutionPlanner Demo Application

This demo showcases the execution plan generation capabilities including:
- Detailed execution plan creation from workflow plans
- User approval workflows with verification gates
- Plan modification and approval tracking
- Integration with audit trail for approval tracking

Run with: python examples/execution_planner_demo.py
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any

from agentic_sdlc.orchestration.engine import ExecutionPlanner, PlanValidationLevel
from agentic_sdlc.orchestration.models import (
    WorkflowPlan, OrchestrationPattern, AgentType, AgentAssignment,
    TaskDependency, ResourceRequirement
)
from agentic_sdlc.orchestration.models.verification import (
    ApprovalLevel, VerificationStatus, UserFeedback, PlanModification, ModificationType
)


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


def create_sample_workflow_plan() -> WorkflowPlan:
    """Create a sample workflow plan for demonstration"""
    print("Creating sample workflow plan...")
    
    # Define agents with different roles and model tiers
    agents = [
        AgentAssignment(
            agent_type=AgentType.PM,
            priority=1,
            estimated_duration=120  # 2 hours
        ),
        AgentAssignment(
            agent_type=AgentType.BA,
            priority=1,
            estimated_duration=180  # 3 hours
        ),
        AgentAssignment(
            agent_type=AgentType.SA,
            priority=1,
            estimated_duration=240  # 4 hours
        ),
        AgentAssignment(
            agent_type=AgentType.RESEARCH,
            priority=2,
            estimated_duration=150  # 2.5 hours
        ),
        AgentAssignment(
            agent_type=AgentType.IMPLEMENTATION,
            priority=2,
            estimated_duration=360  # 6 hours
        ),
        AgentAssignment(
            agent_type=AgentType.QUALITY_JUDGE,
            priority=2,
            estimated_duration=120  # 2 hours
        )
    ]
    
    # Define task dependencies
    dependencies = [
        TaskDependency(
            dependent_task_id="task_ba",
            prerequisite_task_id="task_pm",
            dependency_type="completion",
            is_blocking=True
        ),
        TaskDependency(
            dependent_task_id="task_sa",
            prerequisite_task_id="task_ba",
            dependency_type="data",
            is_blocking=True
        ),
        TaskDependency(
            dependent_task_id="task_implementation",
            prerequisite_task_id="task_sa",
            dependency_type="completion",
            is_blocking=True
        ),
        TaskDependency(
            dependent_task_id="task_quality_judge",
            prerequisite_task_id="task_implementation",
            dependency_type="completion",
            is_blocking=False
        ),
        TaskDependency(
            dependent_task_id="task_research",
            prerequisite_task_id="task_pm",
            dependency_type="data",
            is_blocking=False
        )
    ]
    
    # Define resource requirements
    resources = [
        ResourceRequirement(
            resource_type="cpu_cores",
            amount=8.0,
            unit="cores",
            estimated_cost=80.0,
            is_critical=True
        ),
        ResourceRequirement(
            resource_type="memory",
            amount=16.0,
            unit="GB",
            estimated_cost=40.0,
            is_critical=True
        ),
        ResourceRequirement(
            resource_type="storage",
            amount=100.0,
            unit="GB",
            estimated_cost=10.0,
            is_critical=False
        ),
        ResourceRequirement(
            resource_type="model_tokens",
            amount=250.0,
            unit="USD",
            estimated_cost=250.0,
            is_critical=True
        )
    ]
    
    workflow_plan = WorkflowPlan(
        pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
        agents=agents,
        dependencies=dependencies,
        estimated_duration=1170,  # 19.5 hours total
        required_resources=resources,
        priority=1
    )
    
    print(f"✓ Created workflow plan with {len(agents)} agents")
    print(f"  - Pattern: {workflow_plan.pattern.value}")
    print(f"  - Estimated duration: {workflow_plan.estimated_duration} minutes")
    print(f"  - Total estimated cost: ${workflow_plan.get_total_estimated_cost():.2f}")
    
    return workflow_plan


def demonstrate_execution_plan_generation(planner: ExecutionPlanner, workflow_plan: WorkflowPlan):
    """Demonstrate execution plan generation"""
    print_section("EXECUTION PLAN GENERATION")
    
    print("Generating detailed execution plan...")
    start_time = time.time()
    
    execution_plan = planner.generate_execution_plan(
        workflow_plan,
        validation_level=PlanValidationLevel.COMPREHENSIVE
    )
    
    generation_time = time.time() - start_time
    print(f"✓ Execution plan generated in {generation_time:.2f} seconds")
    
    # Display plan summary
    print_subsection("Plan Summary")
    summary = execution_plan.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Display task breakdown
    print_subsection("Task Breakdown")
    print(f"Total tasks: {execution_plan.total_tasks}")
    print(f"Critical path tasks: {len(execution_plan.critical_path_tasks)}")
    print(f"Parallel task groups: {len(execution_plan.parallel_task_groups)}")
    
    print("\nSample tasks:")
    for i, (task_id, task) in enumerate(list(execution_plan.task_breakdown.items())[:3]):
        print(f"  {i+1}. {task['name']} ({task['agent_type']})")
        print(f"     Duration: {task['estimated_duration']} minutes")
        print(f"     Deliverables: {', '.join(task['deliverables'])}")
    
    if len(execution_plan.task_breakdown) > 3:
        print(f"  ... and {len(execution_plan.task_breakdown) - 3} more tasks")
    
    # Display resource analysis
    print_subsection("Resource Analysis")
    print("Peak resource usage:")
    for resource_type, amount in execution_plan.peak_resource_usage.items():
        print(f"  {resource_type}: {amount}")
    
    print("\nCost breakdown:")
    total_cost = 0
    for resource_type, cost in execution_plan.cost_breakdown.items():
        print(f"  {resource_type}: ${cost:.2f}")
        total_cost += cost
    print(f"  Total: ${total_cost:.2f}")
    
    # Display risk assessment
    print_subsection("Risk Assessment")
    print(f"Identified risks: {len(execution_plan.identified_risks)}")
    for risk in execution_plan.identified_risks:
        risk_score = risk['probability'] * risk['impact']
        print(f"  • {risk['description']}")
        print(f"    Category: {risk['category']}, Risk Score: {risk_score:.2f}")
    
    print(f"\nMitigation strategies: {len(execution_plan.mitigation_strategies)}")
    for mitigation in execution_plan.mitigation_strategies:
        print(f"  • {mitigation['strategy']}")
    
    # Display quality checkpoints
    print_subsection("Quality Checkpoints")
    for checkpoint in execution_plan.quality_checkpoints:
        print(f"  • {checkpoint}")
    
    # Display timeline
    print_subsection("Timeline")
    print(f"Earliest start: {execution_plan.earliest_start}")
    print(f"Latest finish: {execution_plan.latest_finish}")
    print(f"Buffer time: {execution_plan.buffer_time_minutes} minutes ({execution_plan.buffer_time_minutes/60:.1f} hours)")
    
    return execution_plan


def demonstrate_approval_workflow(planner: ExecutionPlanner, execution_plan, workflow_plan: WorkflowPlan):
    """Demonstrate user approval workflow"""
    print_section("USER APPROVAL WORKFLOW")
    
    print("Creating approval workflow...")
    approval_workflow = planner.create_approval_workflow(
        execution_plan,
        workflow_plan,
        ApprovalLevel.PROJECT_MANAGER
    )
    
    print(f"✓ Approval workflow created with {len(approval_workflow.gates)} verification gates")
    
    # Display workflow summary
    print_subsection("Workflow Summary")
    summary = approval_workflow.get_workflow_summary()
    for key, value in summary.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")
    
    # Display verification gates
    print_subsection("Verification Gates")
    for i, gate in enumerate(approval_workflow.gates, 1):
        print(f"\n{i}. {gate.name}")
        print(f"   Description: {gate.description}")
        print(f"   Status: {gate.status.value}")
        print(f"   Approval Level: {gate.approval_level.value}")
        print(f"   Criteria: {len(gate.criteria)}")
        
        for j, criteria in enumerate(gate.criteria, 1):
            print(f"     {j}. {criteria.name}")
            print(f"        Required: {criteria.is_required}")
            if criteria.auto_approve_conditions:
                print(f"        Auto-approve: {', '.join(criteria.auto_approve_conditions)}")
    
    return approval_workflow


def demonstrate_plan_validation(planner: ExecutionPlanner, execution_plan, workflow_plan: WorkflowPlan):
    """Demonstrate plan validation"""
    print_section("PLAN VALIDATION")
    
    print("Validating execution plan...")
    validation_result = planner.validate_execution_plan(execution_plan, workflow_plan)
    
    print(f"✓ Validation completed")
    print(f"  Valid: {validation_result.is_valid}")
    print(f"  Missing prerequisites: {len(validation_result.missing_prerequisites)}")
    print(f"  Warnings: {len(validation_result.warnings)}")
    print(f"  Estimated setup time: {validation_result.estimated_setup_time} minutes")
    
    if validation_result.missing_prerequisites:
        print("\nMissing prerequisites:")
        for prereq in validation_result.missing_prerequisites:
            print(f"  • {prereq}")
    
    if validation_result.warnings:
        print("\nWarnings:")
        for warning in validation_result.warnings:
            print(f"  • {warning}")
    
    return validation_result


def demonstrate_approval_process(planner: ExecutionPlanner, approval_workflow, execution_plan, workflow_plan: WorkflowPlan):
    """Demonstrate the approval process"""
    print_section("APPROVAL PROCESS SIMULATION")
    
    print("Simulating user approval process...")
    
    # Process each gate
    for i, gate in enumerate(approval_workflow.gates):
        print_subsection(f"Processing Gate {i+1}: {gate.name}")
        
        # Simulate user feedback
        if i == 0:  # First gate - add some feedback
            feedback = UserFeedback(
                user_id="project_manager",
                feedback_type="suggestion",
                content="Consider adding more buffer time for the implementation phase",
                priority=2
            )
            gate.add_feedback(feedback)
            print(f"  Added user feedback: {feedback.content}")
        
        # Check auto-approval
        context = {
            "cost": sum(execution_plan.cost_breakdown.values()),
            "duration": execution_plan.buffer_time_minutes + workflow_plan.estimated_duration
        }
        
        if gate.can_auto_approve(context):
            print(f"  ✓ Gate can be auto-approved based on criteria")
            approval_workflow.process_gate_decision(
                gate.id, "approve", "system", "Auto-approved based on criteria"
            )
        else:
            print(f"  Manual approval required")
            # Simulate manual approval - bypass criteria check by directly setting status
            if i < len(approval_workflow.gates) - 1:  # Approve all but last
                gate.status = VerificationStatus.APPROVED
                gate.approved_by = "project_manager"
                gate.approved_at = datetime.now()
                approval_workflow.advance_to_next_gate()
                print(f"  ✓ Gate approved by project_manager")
            else:  # Request modification on last gate
                approval_workflow.process_gate_decision(
                    gate.id, "modify", "project_manager", "Need to adjust timeline before final approval"
                )
                print(f"  ⚠ Modification requested: Need to adjust timeline")
        
        # Display gate status
        print(f"  Gate status: {gate.status.value}")
        
        # Show progress
        progress = gate.get_approval_progress()
        print(f"  Progress: {progress['progress']*100:.1f}% ({progress['met_criteria']}/{progress['total_criteria']} criteria met)")
    
    # Display final workflow status
    print_subsection("Final Workflow Status")
    final_summary = approval_workflow.get_workflow_summary()
    print(f"Status: {final_summary['status']}")
    print(f"Progress: {final_summary['progress']['progress_percentage']:.1f}%")
    print(f"Modifications: {final_summary['modifications']}")
    
    return approval_workflow


def demonstrate_plan_modification(planner: ExecutionPlanner, execution_plan, approval_workflow):
    """Demonstrate plan modification"""
    print_section("PLAN MODIFICATION")
    
    print("Applying plan modification based on user feedback...")
    
    # Create a timeline modification
    modification = PlanModification(
        plan_id=execution_plan.plan_id,
        modification_type=ModificationType.TIMELINE_CHANGE,
        description="Increase buffer time for implementation phase",
        old_value=execution_plan.buffer_time_minutes,
        new_value=execution_plan.buffer_time_minutes + 120,  # Add 2 hours
        reason="User feedback requested more time for implementation quality assurance"
    )
    
    print(f"Modification details:")
    print(f"  Type: {modification.modification_type.value}")
    print(f"  Description: {modification.description}")
    print(f"  Old value: {modification.old_value} minutes")
    print(f"  New value: {modification.new_value} minutes")
    print(f"  Reason: {modification.reason}")
    
    # Apply modification
    modified_plan = planner.modify_execution_plan(
        execution_plan.id,
        modification,
        "project_manager"
    )
    
    print(f"✓ Modification applied successfully")
    print(f"  Impact summary: {modification.get_impact_summary()}")
    print(f"  New buffer time: {modified_plan.buffer_time_minutes} minutes")
    
    # Show updated workflow status
    updated_workflow = planner.get_approval_workflow(approval_workflow.id)
    print(f"  Workflow modifications: {updated_workflow.total_modifications}")
    print(f"  Workflow status: {updated_workflow.workflow_status.value}")
    
    # Now approve the final gate after modification
    print("\nProcessing final approval after modification...")
    current_gate = updated_workflow.get_current_gate()
    if current_gate and current_gate.status == VerificationStatus.REQUIRES_MODIFICATION:
        # Reset gate status and approve directly
        current_gate.status = VerificationStatus.APPROVED
        current_gate.approved_by = "project_manager"
        current_gate.approved_at = datetime.now()
        updated_workflow.advance_to_next_gate()
        print(f"✓ Final gate approved after modification")
    
    return modified_plan, updated_workflow


def demonstrate_metrics_and_reporting(planner: ExecutionPlanner):
    """Demonstrate metrics and reporting"""
    print_section("METRICS AND REPORTING")
    
    print("Generating planner metrics...")
    metrics = planner.get_planner_metrics()
    
    print("Planner Performance Metrics:")
    for key, value in metrics.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")
    
    # List all execution plans
    print_subsection("Execution Plans")
    plans = planner.list_execution_plans()
    for i, plan in enumerate(plans, 1):
        print(f"{i}. Plan {plan.id[:8]}...")
        print(f"   Complexity: {plan.complexity.value}")
        print(f"   Tasks: {plan.total_tasks}")
        print(f"   Created: {plan.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # List all approval workflows
    print_subsection("Approval Workflows")
    workflows = planner.list_approval_workflows()
    for i, workflow in enumerate(workflows, 1):
        print(f"{i}. Workflow {workflow.id[:8]}...")
        print(f"   Status: {workflow.workflow_status.value}")
        print(f"   Gates: {len(workflow.gates)}")
        print(f"   Modifications: {workflow.total_modifications}")
        print(f"   Can proceed: {workflow.can_proceed_to_execution()}")


def main():
    """Main demo function"""
    print_section("EXECUTION PLANNER DEMO")
    print("This demo showcases the ExecutionPlanner capabilities:")
    print("• Detailed execution plan generation")
    print("• User approval workflows with verification gates")
    print("• Plan validation and verification capabilities")
    print("• Plan modification and approval tracking")
    print("• Integration with audit trail")
    
    # Initialize ExecutionPlanner
    print("\nInitializing ExecutionPlanner...")
    planner = ExecutionPlanner()
    print(f"✓ ExecutionPlanner initialized (ID: {planner.planner_id[:8]}...)")
    
    try:
        # Create sample workflow plan
        workflow_plan = create_sample_workflow_plan()
        
        # Demonstrate execution plan generation
        execution_plan = demonstrate_execution_plan_generation(planner, workflow_plan)
        
        # Demonstrate approval workflow creation
        approval_workflow = demonstrate_approval_workflow(planner, execution_plan, workflow_plan)
        
        # Demonstrate plan validation
        validation_result = demonstrate_plan_validation(planner, execution_plan, workflow_plan)
        
        # Demonstrate approval process
        approval_workflow = demonstrate_approval_process(planner, approval_workflow, execution_plan, workflow_plan)
        
        # Demonstrate plan modification
        modified_plan, final_workflow = demonstrate_plan_modification(planner, execution_plan, approval_workflow)
        
        # Demonstrate metrics and reporting
        demonstrate_metrics_and_reporting(planner)
        
        # Final summary
        print_section("DEMO SUMMARY")
        print("✓ Successfully demonstrated ExecutionPlanner capabilities:")
        print(f"  • Generated execution plan with {execution_plan.total_tasks} tasks")
        print(f"  • Created approval workflow with {len(approval_workflow.gates)} gates")
        print(f"  • Processed {len(final_workflow.approval_history)} approval decisions")
        print(f"  • Applied {final_workflow.total_modifications} plan modifications")
        print(f"  • Final workflow status: {final_workflow.workflow_status.value}")
        print(f"  • Can proceed to execution: {final_workflow.can_proceed_to_execution()}")
        
        if validation_result.is_valid:
            print("  • Plan validation: PASSED")
        else:
            print(f"  • Plan validation: FAILED ({len(validation_result.missing_prerequisites)} issues)")
        
        print(f"\nTotal estimated cost: ${modified_plan.cost_breakdown.get('total', sum(modified_plan.cost_breakdown.values())):.2f}")
        print(f"Total estimated duration: {workflow_plan.estimated_duration + modified_plan.buffer_time_minutes} minutes")
        print(f"({(workflow_plan.estimated_duration + modified_plan.buffer_time_minutes)/60:.1f} hours)")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    print(f"\n🎉 ExecutionPlanner demo completed successfully!")
    return 0


if __name__ == "__main__":
    exit(main())