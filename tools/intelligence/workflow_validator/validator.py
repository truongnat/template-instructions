"""
Compliance Validator - Validate execution against workflow definition
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from .parser import WorkflowDefinition, WorkflowStep
from .tracker import ExecutionSession, Action, ActionType


class ViolationType(Enum):
    """Types of workflow violations"""
    SKIPPED_STEP = "skipped_step"
    WRONG_ORDER = "wrong_order"
    WRONG_COMMAND = "wrong_command"
    MISSING_CRITICAL = "missing_critical"
    EXTRA_STEP = "extra_step"


class ImpactLevel(Enum):
    """Impact levels for violations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Violation:
    """Represents a workflow compliance violation"""
    violation_type: ViolationType
    impact: ImpactLevel
    step_number: Optional[int]
    description: str
    recommendation: str
    detected_action: Optional[Action] = None


@dataclass
class StepResult:
    """Result of validating a single workflow step"""
    step: WorkflowStep
    completed: bool = False
    matched_actions: List[Action] = field(default_factory=list)
    violations: List[Violation] = field(default_factory=list)


@dataclass
class ComplianceReport:
    """Comprehensive compliance validation report"""
    workflow_name: str
    workflow_definition: WorkflowDefinition
    execution_session: ExecutionSession
    step_results: List[StepResult]
    violations: List[Violation]
    compliance_score: float
    overall_status: str  # PASS, PARTIAL, FAIL
    summary: str
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'workflow_name': self.workflow_name,
            'compliance_score': self.compliance_score,
            'overall_status': self.overall_status,
            'summary': self.summary,
            'total_steps': len(self.step_results),
            'completed_steps': sum(1 for r in self.step_results if r.completed),
            'violations': [
                {
                    'type': v.violation_type.value,
                    'impact': v.impact.value,
                    'description': v.description,
                    'recommendation': v.recommendation
                }
                for v in self.violations
            ],
            'recommendations': self.recommendations
        }


class ComplianceValidator:
    """Validate workflow execution against definition"""
    
    def __init__(self):
        self.command_similarity_threshold = 0.7  # For fuzzy command matching
    
    def validate(
        self,
        workflow_def: WorkflowDefinition,
        execution_session: ExecutionSession
    ) -> ComplianceReport:
        """
        Validate execution session against workflow definition
        
        Args:
            workflow_def: Parsed workflow definition
            execution_session: Recorded execution session
            
        Returns:
            ComplianceReport with detailed results
        """
        step_results = []
        all_violations = []
        
        # Validate each step
        for step in workflow_def.steps:
            result = self._validate_step(step, execution_session, workflow_def.turbo_all)
            step_results.append(result)
            all_violations.extend(result.violations)
        
        # Check for extra steps (actions not mapped to any workflow step)
        extra_violations = self._detect_extra_steps(workflow_def, execution_session, step_results)
        all_violations.extend(extra_violations)
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(step_results, all_violations)
        
        # Determine overall status
        overall_status = self._determine_status(compliance_score, all_violations)
        
        # Generate summary
        summary = self._generate_summary(step_results, all_violations, compliance_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_violations, step_results)
        
        return ComplianceReport(
            workflow_name=workflow_def.name,
            workflow_definition=workflow_def,
            execution_session=execution_session,
            step_results=step_results,
            violations=all_violations,
            compliance_score=compliance_score,
            overall_status=overall_status,
            summary=summary,
            recommendations=recommendations
        )
    
    def _validate_step(
        self,
        step: WorkflowStep,
        session: ExecutionSession,
        turbo_all: bool
    ) -> StepResult:
        """Validate a single workflow step"""
        result = StepResult(step=step)
        
        # Find matching actions
        matched_actions = self._find_matching_actions(step, session.actions)
        result.matched_actions = matched_actions
        
        if matched_actions:
            result.completed = True
            
            # Check command accuracy if step has defined commands
            if step.commands:
                # Find if any of the matched commands match any of the expected ones
                command_actions = [a for a in matched_actions if a.action_type == ActionType.COMMAND]
                
                if command_actions:
                    has_match = False
                    for expected_cmd in step.commands:
                        if any(self._commands_match(expected_cmd, a.details.get('command', '')) for a in command_actions):
                            has_match = True
                            break
                    
                    if not has_match:
                        # None of the commands match any of the expected ones
                        best_action = command_actions[-1]
                        detected = best_action.details.get('command', '')
                        expected_display = " or ".join([f"'{c}'" for c in step.commands])
                        result.violations.append(Violation(
                            violation_type=ViolationType.WRONG_COMMAND,
                            impact=ImpactLevel.MEDIUM,
                            step_number=step.number,
                            description=f"Step {step.number} executed different command than expected. Found: '{detected}'",
                            recommendation=f"Use one of: {expected_display}",
                            detected_action=best_action
                        ))
        else:
            # Step not completed
            impact = ImpactLevel.CRITICAL if step.is_critical else ImpactLevel.MEDIUM
            result.violations.append(Violation(
                violation_type=ViolationType.SKIPPED_STEP,
                impact=impact,
                step_number=step.number,
                description=f"Step {step.number} was skipped: {step.description}",
                recommendation=f"Ensure step {step.number} is executed in future runs"
            ))
        
        return result
    
    def _find_matching_actions(self, step: WorkflowStep, actions: List[Action]) -> List[Action]:
        """Find actions that match a workflow step"""
        matched = []
        
        for action in actions:
            # Match by step number if annotated
            if action.step_number is not None:
                if action.step_number == step.number:
                    matched.append(action)
                # If it has a different step number, don't match it here
                continue
            
            # Match by command similarity
            if step.commands and action.action_type == ActionType.COMMAND:
                cmd = action.details.get('command', '')
                if any(self._commands_match(expected, cmd) for expected in step.commands):
                    matched.append(action)
                    continue
            
            # Match by description keywords
            if self._description_matches(step.description, action):
                matched.append(action)
        
        return matched
    
    def _commands_match(self, expected: str, actual: str) -> bool:
        """Check if two commands match (with some flexibility)"""
        exp = expected.strip()
        act = actual.strip()
        
        # Exact match
        if exp == act:
            return True
        
        # Check if the core command is the same
        expected_parts = exp.split()
        actual_parts = act.split()
        
        if not expected_parts or not actual_parts:
            return False
            
        expected_base = expected_parts[0]
        actual_base = actual_parts[0]
        
        if expected_base == actual_base:
            # Special case for git commit with message
            if expected_base == "git" and len(expected_parts) > 1 and expected_parts[1] == "commit":
                # If expected has "type(scope): description" placeholder
                if "type(scope): description" in exp:
                    # Just check if it has -m and some message
                    return "-m" in actual_parts or "--message" in actual_parts
            
            # Same base command, check similarity
            return self._text_similarity(exp, act) > self.command_similarity_threshold
        
        return False
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity (percentage of matching words)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        common = words1.intersection(words2)
        return len(common) / max(len(words1), len(words2))
    
    def _description_matches(self, step_desc: str, action: Action) -> bool:
        """Check if action matches step description"""
        # Simple keyword matching
        keywords = ['status', 'diff', 'commit', 'push', 'review', 'verify']
        
        step_lower = step_desc.lower()
        
        for keyword in keywords:
            if keyword in step_lower:
                # Check if action relates to this keyword
                if action.action_type == ActionType.COMMAND:
                    cmd = action.details.get('command', '').lower()
                    if keyword in cmd:
                        return True
        
        return False
    
    def _detect_extra_steps(
        self,
        workflow_def: WorkflowDefinition,
        session: ExecutionSession,
        step_results: List[StepResult]
    ) -> List[Violation]:
        """Detect actions not mapped to any workflow step"""
        violations = []
        
        # Get all matched actions
        matched_action_ids = set()
        for result in step_results:
            for action in result.matched_actions:
                matched_action_ids.add(id(action))
        
        # Find unmatched actions
        for action in session.actions:
            if id(action) not in matched_action_ids:
                # Skip workflow start/end actions
                if action.action_type in [ActionType.WORKFLOW_START, ActionType.WORKFLOW_END]:
                    continue
                
                # Extra step detected (not necessarily bad, just informational)
                violations.append(Violation(
                    violation_type=ViolationType.EXTRA_STEP,
                    impact=ImpactLevel.LOW,
                    step_number=None,
                    description=f"Extra action detected: {action.action_type.value}",
                    recommendation="This action was not defined in the workflow (may be intentional)",
                    detected_action=action
                ))
        
        return violations
    
    def _calculate_compliance_score(
        self,
        step_results: List[StepResult],
        violations: List[Violation]
    ) -> float:
        """Calculate overall compliance score (0-100)"""
        if not step_results:
            return 100.0
        
        # Base score: percentage of steps completed
        completed_steps = sum(1 for r in step_results if r.completed)
        base_score = (completed_steps / len(step_results)) * 100
        
        # Deduct points for violations
        deduction = 0
        for violation in violations:
            if violation.impact == ImpactLevel.CRITICAL:
                deduction += 20
            elif violation.impact == ImpactLevel.HIGH:
                deduction += 10
            elif violation.impact == ImpactLevel.MEDIUM:
                deduction += 5
            elif violation.impact == ImpactLevel.LOW:
                deduction += 2
        
        final_score = max(0, base_score - deduction)
        return round(final_score, 2)
    
    def _determine_status(self, score: float, violations: List[Violation]) -> str:
        """Determine overall compliance status"""
        # Check for critical violations
        has_critical = any(v.impact == ImpactLevel.CRITICAL for v in violations)
        
        if has_critical or score < 50:
            return "FAIL"
        elif score < 80:
            return "PARTIAL"
        else:
            return "PASS"
    
    def _generate_summary(
        self,
        step_results: List[StepResult],
        violations: List[Violation],
        score: float
    ) -> str:
        """Generate human-readable summary"""
        completed = sum(1 for r in step_results if r.completed)
        total = len(step_results)
        
        summary = f"Completed {completed}/{total} steps ({score:.1f}% compliance). "
        
        if score >= 95:
            summary += "Excellent workflow adherence!"
        elif score >= 80:
            summary += "Good workflow compliance with minor deviations."
        elif score >= 50:
            summary += "Partial compliance with several issues detected."
        else:
            summary += "Poor compliance - significant workflow violations."
        
        return summary
    
    def _generate_recommendations(
        self,
        violations: List[Violation],
        step_results: List[StepResult]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Group violations by type
        skipped = [v for v in violations if v.violation_type == ViolationType.SKIPPED_STEP]
        wrong_cmd = [v for v in violations if v.violation_type == ViolationType.WRONG_COMMAND]
        
        if skipped:
            recommendations.append(f"Ensure all {len(skipped)} skipped steps are executed")
        
        if wrong_cmd:
            recommendations.append("Use exact commands as specified in workflow for consistency")
        
        # Check completion rate
        completed = sum(1 for r in step_results if r.completed)
        if completed < len(step_results):
            recommendations.append("Review workflow definition to ensure all steps are necessary")
        
        return recommendations
