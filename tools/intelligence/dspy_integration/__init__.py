"""
DSPy Integration - Declarative Self-Improving AI Agents

Part of Layer 2: Intelligence Layer.
"""

try:
    from .dspy_agents import (
        AgentOptimizer,
        DEVAgent,
        DSPyLearningBridge,
        OptimizationResult,
        PMAgent,
        QAAgent,
        SAAgent,
        SecurityAgent,
        DSPY_AVAILABLE,
    )
    
    __all__ = [
        "AgentOptimizer",
        "DEVAgent",
        "DSPyLearningBridge",
        "OptimizationResult",
        "PMAgent",
        "QAAgent",
        "SAAgent",
        "SecurityAgent",
        "DSPY_AVAILABLE",
    ]
except ImportError as e:
    print(f"⚠️ DSPy integration import error: {e}")
    DSPY_AVAILABLE = False
    __all__ = ["DSPY_AVAILABLE"]
