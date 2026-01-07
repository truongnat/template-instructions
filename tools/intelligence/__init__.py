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
from .monitor import Observer, RuleChecker, AuditLogger

# A/B Test Module
from .ab_test import ABTester, OptionComparator

# Self-Learning Module
from .self_learning import Learner, SelfImprover, PatternEngine

# Artifact Generator Module
from .artifact_gen import DocGenerator, ReportGenerator, TemplateEngine

# Proxy Module
from .proxy import ModelProxy, CostTracker

# Task Manager Module
from .task_manager import TaskBoard, SprintManager

# Performance Module
from .performance import MetricsCollector, FlowOptimizer

# Judge Module
from .judge import QualityJudge


__all__ = [
    # Scorer
    'InputScorer', 'OutputScorer', 'QualityMetrics',
    # Router
    'WorkflowRouter', 'AgentRouter', 'RulesEngine',
    # Monitor
    'Observer', 'RuleChecker', 'AuditLogger',
    # A/B Test
    'ABTester', 'OptionComparator',
    # Self-Learning
    'Learner', 'SelfImprover', 'PatternEngine',
    # Artifact Generator
    'DocGenerator', 'ReportGenerator', 'TemplateEngine',
    # Proxy
    'ModelProxy', 'CostTracker',
    # Task Manager
    'TaskBoard', 'SprintManager',
    # Performance
    'MetricsCollector', 'FlowOptimizer',
    # Judge
    'QualityJudge',
]


__version__ = "1.0.0"

