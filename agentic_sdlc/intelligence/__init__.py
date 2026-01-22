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
- Concurrent Execution (Swarms-inspired parallel execution)
- Output Synthesis (MixtureOfAgents-inspired aggregation)
"""

# Scorer Module
from .scorer import InputScorer, OutputScorer, QualityMetrics

# Router Module (enhanced with Swarms-inspired complexity analysis)
from .router import WorkflowRouter, AgentRouter, RulesEngine
from .router.workflow_router import TaskComplexity, ExecutionMode, RouteResult

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

# NEW: Concurrent Executor (Swarms-inspired)
try:
    from .concurrent_executor import (
        ConcurrentExecutor, 
        DesignPhaseExecutor, 
        ReviewPhaseExecutor,
        ConcurrentResult,
        RoleResult
    )
except ImportError:
    pass

# NEW: Output Synthesizer (MixtureOfAgents-inspired)
try:
    from .synthesizer import (
        OutputSynthesizer,
        SynthesisResult,
        SynthesisInput,
        SynthesisStrategy
    )
except ImportError:
    pass

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

# NEW: Feedback Protocol (Bidirectional)
try:
    from .feedback_protocol import FeedbackProtocol, FeedbackMessage
except ImportError:
    pass

# NEW: Group Chat (Debate/Collaboration)
try:
    from .group_chat import GroupChat, ChatMessage, GroupChatResult
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

# NEW: Auto Skill Builder (Phase 3.1)
try:
    from .auto_skill_builder import AutoSkillBuilder
except ImportError:
    pass

# NEW: Swarm Router (Phase 3.2)
try:
    from .swarm_router import SwarmRouter, SwarmExecutionResult
except ImportError:
    pass


__all__ = [
    # Scorer
    'InputScorer', 'OutputScorer', 'QualityMetrics',
    # Router (enhanced)
    'WorkflowRouter', 'AgentRouter', 'RulesEngine',
    'TaskComplexity', 'ExecutionMode', 'RouteResult',
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
    # NEW: Concurrent Executor (Swarms-inspired)
    'ConcurrentExecutor', 'DesignPhaseExecutor', 'ReviewPhaseExecutor',
    'ConcurrentResult', 'RoleResult',
    # NEW: Output Synthesizer (MixtureOfAgents-inspired)
    'OutputSynthesizer', 'SynthesisResult', 'SynthesisInput', 'SynthesisStrategy',
    # HITL
    'HITLManager', 'ApprovalGate', 'ApprovalRequest', 'ApprovalResult',
    # State
    'StateManager', 'WorkflowSession', 'Checkpoint',
    # NEW: Feedback Protocol
    'FeedbackProtocol', 'FeedbackMessage',
    # NEW: Group Chat
    'GroupChat', 'ChatMessage', 'GroupChatResult',
    # DSPy
    'DSPY_AVAILABLE', 'AgentOptimizer', 'DSPyLearningBridge',
    # Self-Healing
    'FeedbackLoop', 'SelfHealingOrchestrator', 'Issue', 'HealingResult',
    # Cost
    'NewCostTracker', 'CostReport', 'UsageRecord',
    # Evaluation
    'BenchmarkRunner', 'TestCase', 'EvaluationResult',
    # NEW: Auto Skill Builder
    'AutoSkillBuilder',
    # NEW: Swarm Router
    'SwarmRouter', 'SwarmExecutionResult',
]


__version__ = "1.0.0"




