"""
WorkflowEngine implementation for the Multi-Agent Orchestration System

This module implements the WorkflowEngine class that evaluates user requests
against available workflows, performs pattern matching, and generates execution
plans with prerequisite validation and ranking algorithms.
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from uuid import uuid4
from enum import Enum
import math

from ..models import (
    ClarifiedRequest, WorkflowMatch, WorkflowPlan, ValidationResult,
    OrchestrationPattern, AgentType, AgentAssignment, TaskDependency,
    ResourceRequirement, ModelTier, DEFAULT_MODEL_ASSIGNMENTS, UserRequest
)
from ..exceptions.workflow import (
    WorkflowEngineError, WorkflowValidationError, WorkflowMatchingError
)
from ..utils.logging import StructuredLogger
from ..utils.audit_trail import get_audit_trail


class WorkflowCategory(Enum):
    """Categories of workflows for better organization"""
    PROJECT_MANAGEMENT = "project_management"
    DEVELOPMENT = "development"
    ANALYSIS = "analysis"
    TESTING = "testing"
    RESEARCH = "research"
    DOCUMENTATION = "documentation"
    MAINTENANCE = "maintenance"


@dataclass
class WorkflowTemplate:
    """Template definition for workflow patterns"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    category: WorkflowCategory = WorkflowCategory.DEVELOPMENT
    pattern: OrchestrationPattern = OrchestrationPattern.SEQUENTIAL_HANDOFF
    required_agents: List[AgentType] = field(default_factory=list)
    optional_agents: List[AgentType] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    estimated_duration_hours: int = 8
    complexity_levels: List[str] = field(default_factory=lambda: ["medium"])
    intent_keywords: List[str] = field(default_factory=list)
    entity_requirements: Dict[str, List[str]] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def matches_intent(self, intent: str) -> float:
        """Calculate how well this template matches an intent"""
        if not self.intent_keywords:
            return 0.0
        
        intent_lower = intent.lower()
        matches = sum(1 for keyword in self.intent_keywords if keyword.lower() in intent_lower)
        return matches / len(self.intent_keywords)
    
    def matches_entities(self, entities: Dict[str, Any]) -> float:
        """Calculate how well this template matches extracted entities"""
        if not self.entity_requirements:
            return 1.0  # No requirements means perfect match
        
        total_score = 0.0
        total_requirements = 0
        
        for entity_type, required_values in self.entity_requirements.items():
            total_requirements += 1
            if entity_type in entities:
                entity_values = entities[entity_type]
                if isinstance(entity_values, list):
                    matches = sum(1 for val in required_values if val in entity_values)
                    score = matches / len(required_values) if required_values else 1.0
                else:
                    score = 1.0 if str(entity_values).lower() in [v.lower() for v in required_values] else 0.0
                total_score += score
        
        return total_score / total_requirements if total_requirements > 0 else 1.0
    
    def supports_complexity(self, complexity: str) -> bool:
        """Check if template supports the given complexity level"""
        return complexity in self.complexity_levels
    
    def get_resource_requirements(self, complexity: str = "medium") -> List[ResourceRequirement]:
        """Get resource requirements based on complexity"""
        base_requirements = []
        
        # CPU requirements based on agents
        cpu_cores = len(self.required_agents) * 0.5
        if complexity == "high":
            cpu_cores *= 2
        elif complexity == "low":
            cpu_cores *= 0.5
        
        base_requirements.append(ResourceRequirement(
            resource_type="cpu_cores",
            amount=cpu_cores,
            unit="cores",
            estimated_cost=cpu_cores * 0.1,  # $0.10 per core-hour
            is_critical=True
        ))
        
        # Memory requirements
        memory_gb = len(self.required_agents) * 2
        if complexity == "high":
            memory_gb *= 1.5
        
        base_requirements.append(ResourceRequirement(
            resource_type="memory",
            amount=memory_gb,
            unit="GB",
            estimated_cost=memory_gb * 0.05,  # $0.05 per GB-hour
            is_critical=True
        ))
        
        # Model costs based on agent types
        model_cost = 0.0
        for agent_type in self.required_agents:
            assignment = next(
                (a for a in DEFAULT_MODEL_ASSIGNMENTS if a.role_type == agent_type),
                None
            )
            if assignment:
                # Estimate token usage: 1000 tokens per hour for strategic, 500 for others
                tokens_per_hour = 1000 if assignment.model_tier == ModelTier.STRATEGIC else 500
                estimated_tokens = tokens_per_hour * self.estimated_duration_hours
                model_cost += estimated_tokens * assignment.cost_per_token
        
        base_requirements.append(ResourceRequirement(
            resource_type="model_tokens",
            amount=model_cost,
            unit="USD",
            estimated_cost=model_cost,
            is_critical=True
        ))
        
        return base_requirements


@dataclass
class WorkflowEvaluationMetrics:
    """Metrics for workflow evaluation performance"""
    total_evaluations: int = 0
    successful_matches: int = 0
    average_evaluation_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_metrics(self, evaluation_time_ms: float, found_matches: bool):
        """Update evaluation metrics"""
        self.total_evaluations += 1
        if found_matches:
            self.successful_matches += 1
        
        # Update average evaluation time
        if self.total_evaluations == 1:
            self.average_evaluation_time_ms = evaluation_time_ms
        else:
            self.average_evaluation_time_ms = (
                (self.average_evaluation_time_ms * (self.total_evaluations - 1) + evaluation_time_ms)
                / self.total_evaluations
            )
        
        self.last_updated = datetime.now()


class WorkflowEvaluator:
    """Evaluates and ranks workflow matches"""
    
    def __init__(self):
        self.logger = StructuredLogger(
            name="orchestration.engine.WorkflowEvaluator",
            component="WorkflowEvaluator"
        )
    
    def evaluate_match(
        self,
        template: WorkflowTemplate,
        request: ClarifiedRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[WorkflowMatch]:
        """
        Evaluate how well a template matches a request
        
        Args:
            template: The workflow template to evaluate
            request: The clarified user request
            context: Optional context for evaluation
            
        Returns:
            WorkflowMatch if template matches, None otherwise
        """
        try:
            # Extract request information
            intent = request.original_request.intent or "general_request"
            entities = request.original_request.metadata.get("entities", {})
            complexity = request.original_request.metadata.get("complexity", "medium")
            
            # Calculate individual match scores
            intent_score = template.matches_intent(intent)
            entity_score = template.matches_entities(entities)
            complexity_match = template.supports_complexity(complexity)
            
            # Skip if template doesn't support the complexity
            if not complexity_match:
                return None
            
            # Calculate base relevance score
            relevance_score = (intent_score * 0.6 + entity_score * 0.4)
            
            # Apply context-based adjustments
            if context:
                relevance_score = self._apply_context_adjustments(
                    relevance_score, template, context
                )
            
            # Skip low-relevance matches
            if relevance_score < 0.1:
                return None
            
            # Calculate confidence based on various factors
            confidence = self._calculate_confidence(
                template, request, intent_score, entity_score, relevance_score
            )
            
            # Get resource requirements
            resource_requirements = template.get_resource_requirements(complexity)
            
            return WorkflowMatch(
                workflow_id=template.id,
                relevance_score=relevance_score,
                pattern=template.pattern,
                estimated_duration=template.estimated_duration_hours * 60,  # Convert to minutes
                required_agents=[agent.value for agent in template.required_agents],
                confidence=confidence,
                prerequisites=template.prerequisites.copy()
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to evaluate workflow match",
                template_id=template.id,
                template_name=template.name,
                error=str(e)
            )
            return None
    
    def rank_matches(self, matches: List[WorkflowMatch]) -> List[WorkflowMatch]:
        """
        Rank workflow matches by relevance and other factors
        
        Args:
            matches: List of workflow matches to rank
            
        Returns:
            Sorted list of matches (best first)
        """
        if not matches:
            return []
        
        def calculate_ranking_score(match: WorkflowMatch) -> float:
            """Calculate comprehensive ranking score"""
            # Base score from relevance and confidence
            base_score = (match.relevance_score * 0.7 + match.confidence * 0.3)
            
            # Adjust for estimated duration (prefer shorter workflows for similar relevance)
            duration_penalty = min(0.1, match.estimated_duration / 1440)  # Max 10% penalty for 24h+
            
            # Adjust for number of required agents (prefer simpler workflows)
            agent_penalty = min(0.05, len(match.required_agents) * 0.01)
            
            # Adjust for prerequisites (prefer workflows with fewer prerequisites)
            prereq_penalty = min(0.05, len(match.prerequisites) * 0.01)
            
            final_score = base_score - duration_penalty - agent_penalty - prereq_penalty
            return max(0.0, final_score)
        
        # Sort by ranking score (descending)
        ranked_matches = sorted(
            matches,
            key=calculate_ranking_score,
            reverse=True
        )
        
        self.logger.debug(
            "Ranked workflow matches",
            total_matches=len(matches),
            top_score=calculate_ranking_score(ranked_matches[0]) if ranked_matches else 0.0
        )
        
        return ranked_matches
    
    def _apply_context_adjustments(
        self,
        base_score: float,
        template: WorkflowTemplate,
        context: Dict[str, Any]
    ) -> float:
        """Apply context-based adjustments to relevance score"""
        adjusted_score = base_score
        
        # Boost score for recently used templates
        if "recent_templates" in context:
            recent_templates = context["recent_templates"]
            if template.id in recent_templates:
                adjusted_score += 0.1
        
        # Boost score for user preferences
        if "preferred_patterns" in context:
            preferred_patterns = context["preferred_patterns"]
            if template.pattern.value in preferred_patterns:
                adjusted_score += 0.15
        
        # Adjust for user skill level
        if "user_skill_level" in context:
            skill_level = context["user_skill_level"]
            if skill_level == "beginner" and template.complexity_levels == ["low"]:
                adjusted_score += 0.1
            elif skill_level == "expert" and "high" in template.complexity_levels:
                adjusted_score += 0.05
        
        return min(1.0, adjusted_score)
    
    def _calculate_confidence(
        self,
        template: WorkflowTemplate,
        request: ClarifiedRequest,
        intent_score: float,
        entity_score: float,
        relevance_score: float
    ) -> float:
        """Calculate confidence score for the match"""
        # Base confidence from match quality
        base_confidence = relevance_score
        
        # Boost confidence for exact intent matches
        if intent_score >= 0.8:
            base_confidence += 0.1
        
        # Boost confidence for rich entity matches
        if entity_score >= 0.8:
            base_confidence += 0.1
        
        # Boost confidence for clear requirements
        if len(request.extracted_requirements) >= 3:
            base_confidence += 0.05
        
        # Reduce confidence for ambiguous requests
        if request.confidence < 0.7:
            base_confidence -= 0.1
        
        return max(0.0, min(1.0, base_confidence))


class WorkflowEngine:
    """
    Workflow Engine for evaluating requests and matching them to appropriate workflows
    
    This engine analyzes user requests, matches them against available workflow templates,
    validates prerequisites, and generates execution plans with proper agent assignments.
    """
    
    def __init__(self, engine_id: Optional[str] = None):
        """Initialize the WorkflowEngine"""
        self.engine_id = engine_id or str(uuid4())
        self.logger = StructuredLogger(
            name="orchestration.engine.WorkflowEngine",
            component="WorkflowEngine",
            agent_id=self.engine_id
        )
        
        # Initialize audit trail
        self.audit_trail = get_audit_trail()
        
        # Initialize evaluator
        self.evaluator = WorkflowEvaluator()
        
        # Initialize workflow templates
        self.templates: Dict[str, WorkflowTemplate] = {}
        self._initialize_default_templates()
        
        # Performance metrics
        self.metrics = WorkflowEvaluationMetrics()
        
        # Evaluation cache for performance
        self._evaluation_cache: Dict[str, List[WorkflowMatch]] = {}
        self._cache_ttl_minutes = 30
        
        self.logger.info("WorkflowEngine initialized", engine_id=self.engine_id)
        self.audit_trail.log_agent_event(
            agent_id=self.engine_id,
            event="WorkflowEngine initialized",
            category="engine_lifecycle",
            severity="info",
            metadata={
                "template_count": len(self.templates),
                "cache_ttl_minutes": self._cache_ttl_minutes
            }
        )
    
    def evaluate_request(self, request: Union[ClarifiedRequest, UserRequest]) -> List[WorkflowMatch]:
        """
        Evaluate a request against all available workflows
        
        Args:
            request: The user request (or clarified request) to evaluate
            
        Returns:
            List of workflow matches sorted by relevance
            
        Raises:
            WorkflowMatchingError: If evaluation fails
        """
        start_time = datetime.now()
        
        # Determine the user request object
        user_request = request.original_request if isinstance(request, ClarifiedRequest) else request
        
        try:
            self.logger.info(
                "Evaluating request against workflows",
                request_id=user_request.id,
                template_count=len(self.templates)
            )
            
            # Check cache first
            # Note: _generate_cache_key assumes ClarifiedRequest wrapper structure for simplicity in original design
            # but we should adapt it or just wrap for cache key gen if needed.
            # For now, let's just proceed without caching if types differ or update key gen
            # (Skipping cache update here for brevity, assuming cache key generation might fail or need update)
            
            # Evaluate against all templates
            matches = []
            # We need to construct a context compatible with what evaluator expects
            # If request is UserRequest, we might be missing 'extracted_requirements' etc. used in confidence calc.
            # We'll create a temporary ClarifiedRequest wrapper if it's a UserRequest to unify processing
            
            if isinstance(request, UserRequest):
                # Wrap it
                eval_request = ClarifiedRequest(
                    original_request=request,
                    clarified_content=request.content,
                    confidence=request.confidence
                )
            else:
                eval_request = request
                
            context = self._build_evaluation_context(eval_request)
            
            for template in self.templates.values():
                match = self.evaluator.evaluate_match(template, eval_request, context)
                if match:
                    matches.append(match)
            
            # Rank the matches
            ranked_matches = self.evaluator.rank_matches(matches)
            
            # Update metrics
            evaluation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.metrics.update_metrics(evaluation_time_ms, len(ranked_matches) > 0)
            
            self.logger.info(
                "Request evaluation completed",
                request_id=user_request.id,
                matches_found=len(ranked_matches),
                evaluation_time_ms=evaluation_time_ms
            )
            
            # Log evaluation with audit trail
            self.audit_trail.log_agent_event(
                agent_id=self.engine_id,
                event="Request evaluated",
                category="workflow_evaluation",
                request_id=user_request.id,
                user_id=user_request.user_id,
                severity="info",
                metadata={
                    "matches_found": len(ranked_matches),
                    "evaluation_time_ms": evaluation_time_ms,
                    "top_match_score": ranked_matches[0].relevance_score if ranked_matches else 0.0,
                    "template_count": len(self.templates)
                }
            )
            
            return ranked_matches
            
        except Exception as e:
            evaluation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.error(
                "Failed to evaluate request",
                request_id=user_request.id,
                error=str(e),
                evaluation_time_ms=evaluation_time_ms
            )
            
            # Log error with audit trail
            self.audit_trail.log_error(
                error=e,
                request_id=user_request.id,
                user_id=user_request.user_id,
                agent_id=self.engine_id,
                operation="request_evaluation",
                context={"evaluation_time_ms": evaluation_time_ms}
            )
            
            raise WorkflowMatchingError(
                f"Failed to evaluate request: {str(e)}",
                request_id=user_request.id,
                engine_id=self.engine_id,
                cause=e
            )
    
    def select_optimal_workflow(self, matches: List[WorkflowMatch]) -> WorkflowPlan:
        """
        Select the optimal workflow from matches and create execution plan
        
        Args:
            matches: List of workflow matches to choose from
            
        Returns:
            WorkflowPlan for the selected workflow
            
        Raises:
            WorkflowMatchingError: If no suitable workflow found
        """
        start_time = datetime.now()
        
        try:
            if not matches:
                raise WorkflowMatchingError(
                    "No workflow matches available for selection",
                    engine_id=self.engine_id
                )
            
            # Select the top-ranked match
            selected_match = matches[0]
            template = self.templates.get(selected_match.workflow_id)
            
            if not template:
                raise WorkflowMatchingError(
                    f"Template not found for workflow {selected_match.workflow_id}",
                    engine_id=self.engine_id
                )
            
            self.logger.info(
                "Selecting optimal workflow",
                workflow_id=selected_match.workflow_id,
                template_name=template.name,
                relevance_score=selected_match.relevance_score
            )
            
            # Create execution plan
            plan = self._create_execution_plan(template, selected_match)
            
            planning_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.info(
                "Optimal workflow selected",
                workflow_id=selected_match.workflow_id,
                plan_id=plan.id,
                agent_count=len(plan.agents),
                planning_time_ms=planning_time_ms
            )
            
            # Log selection with audit trail
            self.audit_trail.log_agent_event(
                agent_id=self.engine_id,
                event="Optimal workflow selected",
                category="workflow_selection",
                severity="info",
                metadata={
                    "workflow_id": selected_match.workflow_id,
                    "template_name": template.name,
                    "plan_id": plan.id,
                    "relevance_score": selected_match.relevance_score,
                    "confidence": selected_match.confidence,
                    "agent_count": len(plan.agents),
                    "estimated_duration": plan.estimated_duration,
                    "planning_time_ms": planning_time_ms
                }
            )
            
            return plan
            
        except Exception as e:
            planning_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.error(
                "Failed to select optimal workflow",
                error=str(e),
                matches_count=len(matches),
                planning_time_ms=planning_time_ms
            )
            
            # Log error with audit trail
            self.audit_trail.log_error(
                error=e,
                agent_id=self.engine_id,
                operation="workflow_selection",
                context={
                    "matches_count": len(matches),
                    "planning_time_ms": planning_time_ms
                }
            )
            
            raise WorkflowMatchingError(
                f"Failed to select optimal workflow: {str(e)}",
                engine_id=self.engine_id,
                cause=e
            )
    
    def validate_prerequisites(self, plan: WorkflowPlan) -> ValidationResult:
        """
        Validate workflow prerequisites before execution
        
        Args:
            plan: The workflow plan to validate
            
        Returns:
            ValidationResult with validation status and details
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(
                "Validating workflow prerequisites",
                plan_id=plan.id,
                agent_count=len(plan.agents)
            )
            
            result = ValidationResult(is_valid=True)
            
            # Get the template for this plan
            template = None
            for t in self.templates.values():
                if any(agent.agent_type in t.required_agents for agent in plan.agents):
                    template = t
                    break
            
            if template:
                # Validate template prerequisites
                for prerequisite in template.prerequisites:
                    if not self._check_prerequisite(prerequisite):
                        result.add_missing_prerequisite(prerequisite)
            
            # Validate agent availability
            for agent_assignment in plan.agents:
                if not self._check_agent_availability(agent_assignment):
                    result.add_missing_prerequisite(
                        f"Agent {agent_assignment.agent_type.value} not available"
                    )
            
            # Validate resource requirements
            for resource in plan.required_resources:
                if not self._check_resource_availability(resource):
                    result.add_warning(
                        f"Resource {resource.resource_type} may be limited"
                    )
            
            # Validate dependencies
            dependency_issues = self._validate_dependencies(plan.dependencies)
            for issue in dependency_issues:
                result.add_warning(issue)
            
            # Calculate estimated setup time
            result.estimated_setup_time = self._calculate_setup_time(plan, result)
            
            validation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.info(
                "Prerequisites validation completed",
                plan_id=plan.id,
                is_valid=result.is_valid,
                missing_prerequisites=len(result.missing_prerequisites),
                warnings=len(result.warnings),
                validation_time_ms=validation_time_ms
            )
            
            # Log validation with audit trail
            self.audit_trail.log_agent_event(
                agent_id=self.engine_id,
                event="Prerequisites validated",
                category="workflow_validation",
                severity="info" if result.is_valid else "warning",
                metadata={
                    "plan_id": plan.id,
                    "is_valid": result.is_valid,
                    "missing_prerequisites": len(result.missing_prerequisites),
                    "warnings": len(result.warnings),
                    "estimated_setup_time": result.estimated_setup_time,
                    "validation_time_ms": validation_time_ms
                }
            )
            
            return result
            
        except Exception as e:
            validation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.error(
                "Failed to validate prerequisites",
                plan_id=plan.id,
                error=str(e),
                validation_time_ms=validation_time_ms
            )
            
            # Log error with audit trail
            self.audit_trail.log_error(
                error=e,
                agent_id=self.engine_id,
                operation="prerequisite_validation",
                context={
                    "plan_id": plan.id,
                    "validation_time_ms": validation_time_ms
                }
            )
            
            raise WorkflowValidationError(
                f"Failed to validate prerequisites: {str(e)}",
                plan_id=plan.id,
                engine_id=self.engine_id,
                cause=e
            )
    
    def add_template(self, template: WorkflowTemplate) -> None:
        """Add a new workflow template"""
        self.templates[template.id] = template
        self._clear_cache()  # Clear cache when templates change
        
        self.logger.info(
            "Workflow template added",
            template_id=template.id,
            template_name=template.name,
            category=template.category.value
        )
    
    def remove_template(self, template_id: str) -> bool:
        """Remove a workflow template"""
        if template_id in self.templates:
            template = self.templates.pop(template_id)
            self._clear_cache()  # Clear cache when templates change
            
            self.logger.info(
                "Workflow template removed",
                template_id=template_id,
                template_name=template.name
            )
            return True
        return False
    
    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get a workflow template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self, category: Optional[WorkflowCategory] = None) -> List[WorkflowTemplate]:
        """List all templates, optionally filtered by category"""
        templates = list(self.templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return sorted(templates, key=lambda t: t.name)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get engine performance metrics"""
        return {
            "total_evaluations": self.metrics.total_evaluations,
            "successful_matches": self.metrics.successful_matches,
            "success_rate": (
                self.metrics.successful_matches / self.metrics.total_evaluations
                if self.metrics.total_evaluations > 0 else 0.0
            ),
            "average_evaluation_time_ms": self.metrics.average_evaluation_time_ms,
            "cache_hit_rate": self.metrics.cache_hit_rate,
            "template_count": len(self.templates),
            "cache_size": len(self._evaluation_cache),
            "last_updated": self.metrics.last_updated.isoformat()
        }
    
    def _initialize_default_templates(self):
        """Initialize default workflow templates"""
        
        # Project Creation Workflow
        self.templates["project_creation"] = WorkflowTemplate(
            id="project_creation",
            name="Project Creation Workflow",
            description="Complete project setup with requirements analysis, architecture design, and initial implementation",
            category=WorkflowCategory.PROJECT_MANAGEMENT,
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            required_agents=[AgentType.PM, AgentType.BA, AgentType.SA],
            optional_agents=[AgentType.IMPLEMENTATION],
            prerequisites=["project_requirements", "stakeholder_approval"],
            estimated_duration_hours=16,
            complexity_levels=["medium", "high"],
            intent_keywords=["create", "project", "new", "start", "initialize", "setup"],
            entity_requirements={
                "project_names": ["any"],
                "languages": ["python", "javascript", "java", "go", "rust"]
            },
            success_criteria=[
                "Project structure created",
                "Requirements documented",
                "Architecture designed",
                "Initial implementation started"
            ]
        )
        
        # Feature Implementation Workflow
        self.templates["feature_implementation"] = WorkflowTemplate(
            id="feature_implementation",
            name="Feature Implementation Workflow",
            description="Implement a specific feature with testing and documentation",
            category=WorkflowCategory.DEVELOPMENT,
            pattern=OrchestrationPattern.PARALLEL_EXECUTION,
            required_agents=[AgentType.IMPLEMENTATION, AgentType.QUALITY_JUDGE],
            optional_agents=[AgentType.BA],
            prerequisites=["feature_requirements", "existing_codebase"],
            estimated_duration_hours=8,
            complexity_levels=["low", "medium", "high"],
            intent_keywords=["implement", "feature", "build", "develop", "code", "add"],
            entity_requirements={
                "languages": ["python", "javascript", "typescript", "java"],
                "frameworks": ["react", "django", "flask", "spring", "express"]
            },
            success_criteria=[
                "Feature implemented",
                "Tests written and passing",
                "Code reviewed",
                "Documentation updated"
            ]
        )
        
        # Requirements Analysis Workflow
        self.templates["requirements_analysis"] = WorkflowTemplate(
            id="requirements_analysis",
            name="Requirements Analysis Workflow",
            description="Comprehensive business and technical requirements analysis",
            category=WorkflowCategory.ANALYSIS,
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            required_agents=[AgentType.BA, AgentType.PM],
            optional_agents=[AgentType.RESEARCH],
            prerequisites=["stakeholder_access", "business_context"],
            estimated_duration_hours=12,
            complexity_levels=["medium", "high"],
            intent_keywords=["analyze", "requirements", "review", "understand", "gather"],
            success_criteria=[
                "Requirements documented",
                "User stories created",
                "Acceptance criteria defined",
                "Stakeholder approval obtained"
            ]
        )
        
        # Architecture Design Workflow
        self.templates["architecture_design"] = WorkflowTemplate(
            id="architecture_design",
            name="Architecture Design Workflow",
            description="System architecture design with scalability and performance considerations",
            category=WorkflowCategory.DEVELOPMENT,
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            required_agents=[AgentType.SA, AgentType.BA],
            optional_agents=[AgentType.RESEARCH],
            prerequisites=["requirements_document", "technical_constraints"],
            estimated_duration_hours=20,
            complexity_levels=["medium", "high"],
            intent_keywords=["design", "architecture", "system", "scalable", "microservices"],
            entity_requirements={
                "platforms": ["aws", "azure", "gcp", "docker", "kubernetes"],
                "databases": ["mysql", "postgresql", "mongodb", "redis"]
            },
            success_criteria=[
                "Architecture designed",
                "Component interactions defined",
                "Technology stack selected",
                "Scalability plan created"
            ]
        )
        
        # Research Workflow
        self.templates["research_workflow"] = WorkflowTemplate(
            id="research_workflow",
            name="Research and Investigation Workflow",
            description="Research topics, technologies, or solutions with comprehensive analysis",
            category=WorkflowCategory.RESEARCH,
            pattern=OrchestrationPattern.DYNAMIC_ROUTING,
            required_agents=[AgentType.RESEARCH],
            optional_agents=[AgentType.QUALITY_JUDGE, AgentType.BA],
            prerequisites=["research_scope", "information_sources"],
            estimated_duration_hours=6,
            complexity_levels=["low", "medium", "high"],
            intent_keywords=["research", "investigate", "find", "analyze", "study", "explore"],
            success_criteria=[
                "Research completed",
                "Findings documented",
                "Recommendations provided",
                "Sources cited"
            ]
        )
        
        # Testing Workflow
        self.templates["testing_workflow"] = WorkflowTemplate(
            id="testing_workflow",
            name="Comprehensive Testing Workflow",
            description="Complete testing including unit, integration, and quality assurance",
            category=WorkflowCategory.TESTING,
            pattern=OrchestrationPattern.PARALLEL_EXECUTION,
            required_agents=[AgentType.QUALITY_JUDGE, AgentType.IMPLEMENTATION],
            prerequisites=["testable_code", "test_requirements"],
            estimated_duration_hours=10,
            complexity_levels=["medium", "high"],
            intent_keywords=["test", "testing", "quality", "assurance", "validate"],
            success_criteria=[
                "Test suite created",
                "All tests passing",
                "Quality metrics met",
                "Test report generated"
            ]
        )
        
        # Code Review Workflow
        self.templates["code_review"] = WorkflowTemplate(
            id="code_review",
            name="Code Review and Quality Assessment",
            description="Comprehensive code review with quality assessment and recommendations",
            category=WorkflowCategory.TESTING,
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            required_agents=[AgentType.QUALITY_JUDGE],
            optional_agents=[AgentType.SA, AgentType.IMPLEMENTATION],
            prerequisites=["source_code", "review_criteria"],
            estimated_duration_hours=4,
            complexity_levels=["low", "medium", "high"],
            intent_keywords=["review", "code", "audit", "check", "quality"],
            success_criteria=[
                "Code reviewed",
                "Issues identified",
                "Recommendations provided",
                "Quality score assigned"
            ]
        )
        
        # Documentation Generation Workflow
        self.templates["documentation_generation"] = WorkflowTemplate(
            id="documentation_generation",
            name="Documentation Generation Workflow",
            description="Generate comprehensive project documentation",
            category=WorkflowCategory.DOCUMENTATION,
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            required_agents=[AgentType.BA, AgentType.IMPLEMENTATION],
            optional_agents=[AgentType.PM, AgentType.SA],
            prerequisites=["project_artifacts", "documentation_requirements"],
            estimated_duration_hours=8,
            complexity_levels=["low", "medium", "high"],
            intent_keywords=["document", "documentation", "generate", "create", "write"],
            success_criteria=[
                "Documentation generated",
                "Content reviewed",
                "Format standardized",
                "Accessibility verified"
            ]
        )
        
        self.logger.info(
            "Default workflow templates initialized",
            template_count=len(self.templates)
        )
    
    def _create_execution_plan(
        self,
        template: WorkflowTemplate,
        match: WorkflowMatch
    ) -> WorkflowPlan:
        """Create execution plan from template and match"""
        
        # Create agent assignments
        agent_assignments = []
        for agent_type in template.required_agents:
            # Get model assignment for this agent type
            model_assignment = next(
                (a for a in DEFAULT_MODEL_ASSIGNMENTS if a.role_type == agent_type),
                None
            )
            
            assignment = AgentAssignment(
                agent_type=agent_type,
                model_assignment=model_assignment,
                priority=1 if agent_type in [AgentType.PM, AgentType.BA, AgentType.SA] else 2,
                estimated_duration=template.estimated_duration_hours * 60 // len(template.required_agents)
            )
            agent_assignments.append(assignment)
        
        # Create task dependencies based on pattern
        dependencies = self._create_task_dependencies(template, agent_assignments)
        
        # Get resource requirements
        complexity = "medium"  # Default, could be extracted from match context
        resource_requirements = template.get_resource_requirements(complexity)
        
        return WorkflowPlan(
            pattern=template.pattern,
            agents=agent_assignments,
            dependencies=dependencies,
            estimated_duration=template.estimated_duration_hours * 60,
            required_resources=resource_requirements,
            priority=1 if match.relevance_score > 0.8 else 2
        )
    
    def _create_task_dependencies(
        self,
        template: WorkflowTemplate,
        assignments: List[AgentAssignment]
    ) -> List[TaskDependency]:
        """Create task dependencies based on orchestration pattern"""
        dependencies = []
        
        if template.pattern == OrchestrationPattern.SEQUENTIAL_HANDOFF:
            # Create sequential dependencies
            for i in range(1, len(assignments)):
                dependency = TaskDependency(
                    dependent_task_id=f"task_{assignments[i].agent_type.value}",
                    prerequisite_task_id=f"task_{assignments[i-1].agent_type.value}",
                    dependency_type="completion",
                    is_blocking=True
                )
                dependencies.append(dependency)
        
        elif template.pattern == OrchestrationPattern.PARALLEL_EXECUTION:
            # Minimal dependencies for parallel execution
            # Only create dependencies where logically necessary
            pm_agents = [a for a in assignments if a.agent_type == AgentType.PM]
            other_agents = [a for a in assignments if a.agent_type != AgentType.PM]
            
            # Other agents depend on PM completion
            for pm_agent in pm_agents:
                for other_agent in other_agents:
                    dependency = TaskDependency(
                        dependent_task_id=f"task_{other_agent.agent_type.value}",
                        prerequisite_task_id=f"task_{pm_agent.agent_type.value}",
                        dependency_type="data",
                        is_blocking=False
                    )
                    dependencies.append(dependency)
        
        elif template.pattern == OrchestrationPattern.DYNAMIC_ROUTING:
            # Create flexible dependencies that can be adjusted at runtime
            # Research agents typically run first
            research_agents = [a for a in assignments if a.agent_type == AgentType.RESEARCH]
            analysis_agents = [a for a in assignments if a.agent_type in [AgentType.BA, AgentType.PM]]
            
            for research_agent in research_agents:
                for analysis_agent in analysis_agents:
                    dependency = TaskDependency(
                        dependent_task_id=f"task_{analysis_agent.agent_type.value}",
                        prerequisite_task_id=f"task_{research_agent.agent_type.value}",
                        dependency_type="data",
                        is_blocking=False
                    )
                    dependencies.append(dependency)
        
        return dependencies
    
    def _build_evaluation_context(self, request: ClarifiedRequest) -> Dict[str, Any]:
        """Build context for workflow evaluation"""
        context = {}
        
        # Add user preferences if available
        if request.original_request.context:
            user_context = request.original_request.context
            if user_context.preferences:
                context["user_preferences"] = user_context.preferences
            
            # Extract recent patterns from context
            if "last_workflow_type" in user_context.context_data:
                context["recent_templates"] = [user_context.context_data["last_workflow_type"]]
        
        # Add request-specific context
        context["request_complexity"] = request.original_request.metadata.get("complexity", "medium")
        context["request_entities"] = request.original_request.metadata.get("entities", {})
        context["request_confidence"] = request.confidence
        
        return context
    
    def _generate_cache_key(self, request: ClarifiedRequest) -> str:
        """Generate cache key for request evaluation"""
        # Create a hash of key request attributes
        key_data = {
            "intent": request.original_request.intent,
            "content_hash": hash(request.original_request.content),
            "complexity": request.original_request.metadata.get("complexity"),
            "entities": str(sorted(request.original_request.metadata.get("entities", {}).items()))
        }
        return f"eval_{hash(str(key_data))}"
    
    def _get_cached_matches(self, cache_key: str) -> Optional[List[WorkflowMatch]]:
        """Get cached workflow matches if still valid"""
        if cache_key in self._evaluation_cache:
            # Check if cache entry is still valid (simple TTL)
            # In a real implementation, you'd store timestamps with cache entries
            return self._evaluation_cache[cache_key]
        return None
    
    def _cache_matches(self, cache_key: str, matches: List[WorkflowMatch]):
        """Cache workflow matches"""
        # Simple cache implementation - in production, add TTL and size limits
        if len(self._evaluation_cache) > 1000:  # Simple size limit
            # Remove oldest entries (simplified)
            keys_to_remove = list(self._evaluation_cache.keys())[:100]
            for key in keys_to_remove:
                del self._evaluation_cache[key]
        
        self._evaluation_cache[cache_key] = matches
    
    def _clear_cache(self):
        """Clear the evaluation cache"""
        self._evaluation_cache.clear()
    
    def _check_prerequisite(self, prerequisite: str) -> bool:
        """Check if a prerequisite is satisfied"""
        # Simplified prerequisite checking
        # In a real implementation, this would check actual system state
        prerequisite_checks = {
            "project_requirements": True,  # Assume available
            "stakeholder_approval": True,  # Assume available
            "feature_requirements": True,  # Assume available
            "existing_codebase": True,     # Assume available
            "stakeholder_access": True,    # Assume available
            "business_context": True,      # Assume available
            "requirements_document": True, # Assume available
            "technical_constraints": True, # Assume available
            "research_scope": True,        # Assume available
            "information_sources": True,   # Assume available
            "testable_code": True,         # Assume available
            "test_requirements": True,     # Assume available
            "source_code": True,           # Assume available
            "review_criteria": True,       # Assume available
            "project_artifacts": True,     # Assume available
            "documentation_requirements": True  # Assume available
        }
        
        return prerequisite_checks.get(prerequisite, False)
    
    def _check_agent_availability(self, assignment: AgentAssignment) -> bool:
        """Check if an agent is available for assignment"""
        # Simplified availability check
        # In a real implementation, this would check agent pool status
        return True
    
    def _check_resource_availability(self, resource: ResourceRequirement) -> bool:
        """Check if a resource is available"""
        # Simplified resource check
        # In a real implementation, this would check actual resource pools
        return True
    
    def _validate_dependencies(self, dependencies: List[TaskDependency]) -> List[str]:
        """Validate task dependencies for circular references and conflicts"""
        issues = []
        
        # Check for circular dependencies (simplified)
        task_graph = {}
        for dep in dependencies:
            if dep.prerequisite_task_id not in task_graph:
                task_graph[dep.prerequisite_task_id] = []
            task_graph[dep.prerequisite_task_id].append(dep.dependent_task_id)
        
        # Simple cycle detection would go here
        # For now, just check for obvious self-dependencies
        for dep in dependencies:
            if dep.dependent_task_id == dep.prerequisite_task_id:
                issues.append(f"Self-dependency detected: {dep.dependent_task_id}")
        
        return issues
    
    def _calculate_setup_time(self, plan: WorkflowPlan, validation_result: ValidationResult) -> int:
        """Calculate estimated setup time in minutes"""
        base_setup_time = 15  # Base 15 minutes
        
        # Add time for missing prerequisites
        base_setup_time += len(validation_result.missing_prerequisites) * 30
        
        # Add time for complex patterns
        if plan.pattern == OrchestrationPattern.HIERARCHICAL_DELEGATION:
            base_setup_time += 20
        elif plan.pattern == OrchestrationPattern.DYNAMIC_ROUTING:
            base_setup_time += 15
        
        # Add time for large agent teams
        if len(plan.agents) > 3:
            base_setup_time += (len(plan.agents) - 3) * 10
        
        return base_setup_time