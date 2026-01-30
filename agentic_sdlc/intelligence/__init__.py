"""
Layer 2: Intelligence

The Brain's intelligence layer organized by concern:
- Reasoning (Discovery & Planning)
- Monitoring (Quality & Safety)
- Learning (Optimization & Adaptability)
- Collaborating (Orchestration & Outputs)
"""

# --- MONITORING CONCERNS (Quality & Safety) ---
from .monitoring.judge import (
    Judge, 
    InputScorer, 
    OutputScorer, 
    QualityMetrics,
    InputQuality,
    OutputQuality
)
from .monitoring.observer.observer import Observer, Violation
from .monitoring.monitor.audit_logger import AuditLogger
try:
    from .monitoring.hitl import HITLManager, ApprovalGate, ApprovalRequest, ApprovalResult
except ImportError:
    pass
try:
    from .monitoring.evaluation import BenchmarkRunner, TestCase, EvaluationResult
except ImportError:
    pass
try:
    from .monitoring.workflow_validator import WorkflowValidator
except ImportError:
    # Handle if validator exports differently
    pass

# --- REASONING CONCERNS (Discovery & Planning) ---
from .reasoning.router import (
    WorkflowRouter, 
    AgentRouter, 
    RulesEngine, 
    ModelRouter,
    SwarmRouter,
    SwarmExecutionResult,
    ExecutionMode,
    RouteResult
)
from .reasoning.task_manager import TaskBoard, SprintManager
try:
    from .reasoning.skills import AutoSkillBuilder
except ImportError:
    pass

# --- LEARNING CONCERNS (Optimization & Adaptability) ---
from .learning.ab_test import ABTester, OptionComparator
from .learning.self_learning import Learner, SelfImprover, PatternEngine
from .learning.performance import MetricsCollector, FlowOptimizer
try:
    from .learning.dspy_integration import DSPY_AVAILABLE, AgentOptimizer, DSPyLearningBridge
except ImportError:
    DSPY_AVAILABLE = False
try:
    from .learning.self_healing import FeedbackLoop, SelfHealingOrchestrator, Issue, HealingResult
except ImportError:
    pass

# --- COLLABORATING CONCERNS (Orchestration & Outputs) ---
from .collaborating.artifact_gen import ArtifactGenerator
try:
    from .collaborating.concurrent import (
        ConcurrentExecutor, 
        DesignPhaseExecutor, 
        ReviewPhaseExecutor,
        ConcurrentResult,
        RoleResult
    )
except ImportError:
    pass
try:
    from .collaborating.synthesis import (
        OutputSynthesizer,
        SynthesisResult,
        SynthesisInput,
        SynthesisStrategy
    )
except ImportError:
    pass
try:
    from .collaborating.state import StateManager, WorkflowSession, Checkpoint
except ImportError:
    pass
try:
    from .collaborating.communication import (
        FeedbackProtocol, FeedbackMessage,
        GroupChat, ChatMessage, GroupChatResult
    )
except ImportError:
    pass


__all__ = [
    # Monitoring
    'InputScorer', 'OutputScorer', 'QualityMetrics', 'Judge',
    'InputQuality', 'OutputQuality', 'Observer', 'Violation', 'AuditLogger',
    'HITLManager', 'ApprovalGate', 'ApprovalRequest', 'ApprovalResult',
    'BenchmarkRunner', 'TestCase', 'EvaluationResult',
    # Reasoning
    'WorkflowRouter', 'AgentRouter', 'RulesEngine', 'ModelRouter',
    'SwarmRouter', 'SwarmExecutionResult', 'ExecutionMode', 'RouteResult',
    'TaskBoard', 'SprintManager', 'AutoSkillBuilder',
    # Learning
    'ABTester', 'OptionComparator', 'Learner', 'SelfImprover', 'PatternEngine',
    'MetricsCollector', 'FlowOptimizer', 'DSPY_AVAILABLE', 'AgentOptimizer', 
    'DSPyLearningBridge', 'FeedbackLoop', 'SelfHealingOrchestrator', 'Issue', 'HealingResult',
    # Collaborating
    'ArtifactGenerator', 'ConcurrentExecutor', 'DesignPhaseExecutor', 'ReviewPhaseExecutor',
    'ConcurrentResult', 'RoleResult', 'OutputSynthesizer', 'SynthesisResult', 
    'SynthesisInput', 'SynthesisStrategy', 'StateManager', 'WorkflowSession', 'Checkpoint',
    'FeedbackProtocol', 'FeedbackMessage', 'GroupChat', 'ChatMessage', 'GroupChatResult'
]

__version__ = "2.0.0"
