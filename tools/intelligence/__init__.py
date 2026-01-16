"""
Layer 2: Intelligence

The Brain's intelligence layer providing:
- Quality scoring (input/output evaluation)
- Routing (workflow and agent selection)
- Monitoring (compliance and audit)
- A/B Testing (decision comparison)
- Self-Learning (pattern recognition)
- Artifact Generation (documentation)
- Proxy (model selection and cost)
- Task Management (Kanban and sprints)
- Performance (metrics and optimization)
- Judge (quality scoring for artifacts)
"""

# Scorer Module
from .scorer import InputScorer, OutputScorer, QualityMetrics

# Router Module
from .router import WorkflowRouter, AgentRouter, RulesEngine

# Monitor Module
from .monitor import RuleChecker, AuditLogger
from .observer.observer import Observer

# A/B Test Module
from .ab_test import ABTester, OptionComparator

# Self-Learning Module
from .self_learning import Learner, SelfImprover, PatternEngine

# Artifact Generator Module
from .artifact_gen import ArtifactGenerator

# Proxy Module
from .proxy import ModelProxy, CostTracker

# Task Manager Module
from .task_manager import TaskBoard, SprintManager

# Performance Module
from .performance import MetricsCollector, FlowOptimizer

# Judge Module
from .judge import Judge

# HITL Module (Human-in-the-Loop)
try:
    from .hitl import HITLManager, ApprovalGate, ApprovalRequest, ApprovalResult
except ImportError:
    pass

# State Module (Workflow State Persistence)
try:
    from .state import StateManager, WorkflowSession, Checkpoint
except ImportError:
    pass

# DSPy Integration Module
try:
    from .dspy_integration import DSPY_AVAILABLE, AgentOptimizer, DSPyLearningBridge
except ImportError:
    DSPY_AVAILABLE = False

# Self-Healing Module
try:
    from .self_healing import FeedbackLoop, SelfHealingOrchestrator, Issue, HealingResult
except ImportError:
    pass

# Cost Tracking Module
try:
    from .cost import CostTracker as NewCostTracker, CostReport, UsageRecord
except ImportError:
    pass

# Evaluation Module
try:
    from .evaluation import BenchmarkRunner, TestCase, EvaluationResult
except ImportError:
    pass


__all__ = [
    # Scorer
    'InputScorer', 'OutputScorer', 'QualityMetrics',
    # Router
    'WorkflowRouter', 'AgentRouter', 'RulesEngine',
    # Monitor
    'RuleChecker', 'AuditLogger', 'Observer',
    # A/B Test
    'ABTester', 'OptionComparator',
    # Self-Learning
    'Learner', 'SelfImprover', 'PatternEngine',
    # Artifact Generator
    'ArtifactGenerator',
    # Proxy
    'ModelProxy', 'CostTracker',
    # Task Manager
    'TaskBoard', 'SprintManager',
    # Performance
    'MetricsCollector', 'FlowOptimizer',
    # Judge
    'Judge',
    # NEW: HITL
    'HITLManager', 'ApprovalGate', 'ApprovalRequest', 'ApprovalResult',
    # NEW: State
    'StateManager', 'WorkflowSession', 'Checkpoint',
    # NEW: DSPy
    'DSPY_AVAILABLE', 'AgentOptimizer', 'DSPyLearningBridge',
    # NEW: Self-Healing
    'FeedbackLoop', 'SelfHealingOrchestrator', 'Issue', 'HealingResult',
    # NEW: Cost
    'NewCostTracker', 'CostReport', 'UsageRecord',
    # NEW: Evaluation
    'BenchmarkRunner', 'TestCase', 'EvaluationResult',
]


__version__ = "1.0.0"




