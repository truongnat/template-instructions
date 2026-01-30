"""
DSPy Integration - Declarative Self-Improving AI Agents.

Part of Layer 2: Intelligence Layer.
Uses DSPy framework for programming (not prompting) language models with auto-optimization.
"""

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Avoid DSPy "readonly database" error by forcing local cache
try:
    from agentic_sdlc.core.utils.common import get_project_root
    root = get_project_root()
    if (root / ".brain").exists():
        cache_dir = root / ".brain" / "dspy_cache"
    else:
        # Fallback to user home directory to avoid polluting new projects
        cache_dir = Path.home() / ".agentic_sdlc" / "dspy_cache"
        
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["DSPY_CACHEDIR"] = str(cache_dir)
except Exception:
    pass

# Try to import dspy, provide fallback if not installed
try:
    import dspy
    DSPY_AVAILABLE = True
    # Configure dspy to use the local cache dir if available
    try:
        if "DSPY_CACHEDIR" in os.environ:
            dspy.settings.configure(cache_dir=os.environ["DSPY_CACHEDIR"])
    except:
        pass
except ImportError:
    DSPY_AVAILABLE = False
    print("⚠️ DSPy not installed. Run: pip install dspy")

def get_dspy_lm(model_name: str, **kwargs):
    """
    Factory to create a DSPy LM instance from a model name.
    
    Args:
        model_name: Name of the model (e.g., 'gemini-2.5-pro', 'gpt-4o')
    """
    if not DSPY_AVAILABLE:
        return None
        
    # Map model name to provider (simplified, in production use Router.MODELS)
    model_lower = model_name.lower()
    
    if "gemini" in model_lower:
        # Google Generative AI
        try:
            return dspy.Google(model=model_name, **kwargs)
        except AttributeError:
            # Fallback for different DSPy versions
            return None
    elif "gpt" in model_lower:
        # OpenAI
        try:
            return dspy.OpenAI(model=model_name, **kwargs)
        except AttributeError:
            return None
    elif "claude" in model_lower or "sonnet" in model_lower or "opus" in model_lower:
        # Anthropic
        try:
            return dspy.Anthropic(model=model_name, **kwargs)
        except AttributeError:
            return None
    else:
        # Fallback to OpenAI compatible
        try:
            return dspy.OpenAI(model=model_name, **kwargs)
        except AttributeError:
            return None



# ==================== Agent Role Signatures ====================

if DSPY_AVAILABLE:
    
    class PMSignature(dspy.Signature):
        """Project Manager: Creates project plans from requirements."""
        requirements: str = dspy.InputField(desc="User requirements or feature request")
        context: str = dspy.InputField(desc="Existing project context and constraints", default="")
        
        project_plan: str = dspy.OutputField(desc="Structured project plan in markdown format")
        success_criteria: str = dspy.OutputField(desc="Measurable success criteria")
        
    class BASignature(dspy.Signature):
        """Business Analyst: Creates user stories with acceptance criteria."""
        project_plan: str = dspy.InputField(desc="Project plan from PM")
        domain_context: str = dspy.InputField(desc="Domain-specific context", default="")
        
        user_stories: str = dspy.OutputField(desc="User stories in Gherkin format")
        acceptance_criteria: str = dspy.OutputField(desc="Acceptance criteria for each story")
        
    class SASignature(dspy.Signature):
        """Solution Architect: Designs technical architecture."""
        project_plan: str = dspy.InputField(desc="Project plan from PM")
        user_stories: str = dspy.InputField(desc="User stories from BA")
        codebase_context: str = dspy.InputField(desc="Existing codebase structure", default="")
        
        architecture: str = dspy.OutputField(desc="Technical architecture document in markdown")
        tech_stack: str = dspy.OutputField(desc="Recommended technology stack")
        diagrams: str = dspy.OutputField(desc="Architecture diagrams in Mermaid format")
        
    class DEVSignature(dspy.Signature):
        """Developer: Implements code based on design."""
        task: str = dspy.InputField(desc="Specific development task")
        architecture: str = dspy.InputField(desc="Architecture from SA")
        existing_code: str = dspy.InputField(desc="Relevant existing code", default="")
        
        code: str = dspy.OutputField(desc="Implementation code")
        tests: str = dspy.OutputField(desc="Unit tests for the code")
        explanation: str = dspy.OutputField(desc="Brief explanation of implementation decisions")
        
    class TesterSignature(dspy.Signature):
        """QA Tester: Reviews code and creates test scenarios."""
        code: str = dspy.InputField(desc="Code to review")
        requirements: str = dspy.InputField(desc="Requirements to validate against")
        
        issues: str = dspy.OutputField(desc="List of identified issues")
        test_cases: str = dspy.OutputField(desc="Test cases to validate functionality")
        suggestions: str = dspy.OutputField(desc="Improvement suggestions")
        
    class SECASignature(dspy.Signature):
        """Security Analyst: Performs security review."""
        code: str = dspy.InputField(desc="Code to analyze")
        architecture: str = dspy.InputField(desc="System architecture", default="")
        
        vulnerabilities: str = dspy.OutputField(desc="Identified security vulnerabilities")
        risk_level: str = dspy.OutputField(desc="Overall risk assessment: LOW, MEDIUM, HIGH, CRITICAL")
        recommendations: str = dspy.OutputField(desc="Security recommendations")


# ==================== DSPy Modules (Agents) ====================

if DSPY_AVAILABLE:
    
    class PMAgent(dspy.Module):
        """Project Manager Agent with chain-of-thought reasoning."""
        
        def __init__(self):
            super().__init__()
            self.generate_plan = dspy.ChainOfThought(PMSignature)
            
        def forward(self, requirements: str, context: str = "") -> dspy.Prediction:
            return self.generate_plan(requirements=requirements, context=context)
            
    class SAAgent(dspy.Module):
        """Solution Architect Agent with structured reasoning."""
        
        def __init__(self):
            super().__init__()
            self.design = dspy.ChainOfThought(SASignature)
            
        def forward(
            self,
            project_plan: str,
            user_stories: str = "",
            codebase_context: str = ""
        ) -> dspy.Prediction:
            return self.design(
                project_plan=project_plan,
                user_stories=user_stories,
                codebase_context=codebase_context
            )
            
    class DEVAgent(dspy.Module):
        """Developer Agent with code generation."""
        
        def __init__(self):
            super().__init__()
            self.implement = dspy.ChainOfThought(DEVSignature)
            
        def forward(
            self,
            task: str,
            architecture: str = "",
            existing_code: str = ""
        ) -> dspy.Prediction:
            return self.implement(
                task=task,
                architecture=architecture,
                existing_code=existing_code
            )
            
    class QAAgent(dspy.Module):
        """QA Agent with self-improvement through feedback."""
        
        def __init__(self):
            super().__init__()
            self.review = dspy.ChainOfThought(TesterSignature)
            
        def forward(self, code: str, requirements: str) -> dspy.Prediction:
            return self.review(code=code, requirements=requirements)
            
    class SecurityAgent(dspy.Module):
        """Security Agent for vulnerability analysis."""
        
        def __init__(self):
            super().__init__()
            self.analyze = dspy.ChainOfThought(SECASignature)
            
        def forward(self, code: str, architecture: str = "") -> dspy.Prediction:
            return self.analyze(code=code, architecture=architecture)


# ==================== Agent Optimizer ====================

@dataclass
class OptimizationResult:
    """Result of agent optimization."""
    agent_name: str
    before_score: float
    after_score: float
    improvement: float
    examples_used: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "before_score": self.before_score,
            "after_score": self.after_score,
            "improvement": self.improvement,
            "examples_used": self.examples_used,
            "timestamp": self.timestamp
        }


class AgentOptimizer:
    """
    Optimizes agent prompts using DSPy.
    
    Features:
    - Bootstrap from successful examples
    - MIPRO for production optimization
    - Track optimization history
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path(__file__).resolve().parent.parent.parent.parent / "docs" / ".dspy"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.examples_file = self.storage_dir / "training_examples.json"
        self.history_file = self.storage_dir / "optimization_history.json"
        
    def _load_examples(self, agent_name: str) -> List[dict]:
        """Load training examples for an agent."""
        if not self.examples_file.exists():
            return []
        try:
            data = json.loads(self.examples_file.read_text(encoding='utf-8'))
            return data.get(agent_name, [])
        except:
            return []
            
    def _save_example(self, agent_name: str, example: dict) -> None:
        """Save a training example."""
        data = {}
        if self.examples_file.exists():
            try:
                data = json.loads(self.examples_file.read_text(encoding='utf-8'))
            except:
                pass
                
        if agent_name not in data:
            data[agent_name] = []
            
        data[agent_name].append(example)
        
        # Keep last 100 examples per agent
        data[agent_name] = data[agent_name][-100:]
        
        self.examples_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
        
    def add_successful_example(
        self,
        agent_name: str,
        inputs: Dict[str, str],
        outputs: Dict[str, str],
        score: float = 1.0
    ) -> None:
        """
        Add a successful task as training example.
        
        Args:
            agent_name: Name of the agent (PM, SA, DEV, etc.)
            inputs: Input fields and values
            outputs: Output fields and values
            score: Quality score (0-1)
        """
        example = {
            "inputs": inputs,
            "outputs": outputs,
            "score": score,
            "timestamp": datetime.now().isoformat()
        }
        self._save_example(agent_name, example)
        print(f"📚 Added training example for {agent_name}")
        
    def optimize_with_bootstrap(
        self,
        agent: "dspy.Module",
        agent_name: str,
        metric: Callable,
        max_examples: int = 10
    ) -> Tuple["dspy.Module", OptimizationResult]:
        """
        Optimize agent using BootstrapFewShot.
        
        Args:
            agent: DSPy module to optimize
            agent_name: Name for tracking
            metric: Evaluation metric function
            max_examples: Maximum examples to use
            
        Returns:
            Optimized agent and result
        """
        if not DSPY_AVAILABLE:
            raise RuntimeError("DSPy not available")
            
        from dspy.teleprompt import BootstrapFewShot
        
        # Load examples
        raw_examples = self._load_examples(agent_name)[:max_examples]
        
        if len(raw_examples) < 3:
            print(f"⚠️ Not enough examples for {agent_name} (need at least 3, have {len(raw_examples)})")
            return agent, OptimizationResult(
                agent_name=agent_name,
                before_score=0,
                after_score=0,
                improvement=0,
                examples_used=len(raw_examples)
            )
            
        # Convert to DSPy examples
        trainset = []
        for ex in raw_examples:
            dspy_ex = dspy.Example(**ex["inputs"], **ex["outputs"])
            trainset.append(dspy_ex.with_inputs(*ex["inputs"].keys()))
            
        # Evaluate before
        before_score = self._evaluate(agent, trainset, metric)
        
        # Optimize
        optimizer = BootstrapFewShot(metric=metric, max_bootstrapped_demos=4)
        optimized_agent = optimizer.compile(agent, trainset=trainset)
        
        # Evaluate after
        after_score = self._evaluate(optimized_agent, trainset, metric)
        
        result = OptimizationResult(
            agent_name=agent_name,
            before_score=before_score,
            after_score=after_score,
            improvement=after_score - before_score,
            examples_used=len(trainset)
        )
        
        self._save_history(result)
        
        print(f"✨ Optimized {agent_name}: {before_score:.2f} → {after_score:.2f} (+{result.improvement:.2f})")
        
        return optimized_agent, result
        
    def _evaluate(
        self,
        agent: "dspy.Module",
        examples: List,
        metric: Callable
    ) -> float:
        """Evaluate agent on examples."""
        if not examples:
            return 0.0
            
        scores = []
        for ex in examples:
            try:
                pred = agent(**{k: getattr(ex, k) for k in ex.inputs().keys()})
                score = metric(ex, pred)
                scores.append(score)
            except Exception as e:
                scores.append(0.0)
                
        return sum(scores) / len(scores) if scores else 0.0
        
    def _save_history(self, result: OptimizationResult) -> None:
        """Save optimization result to history."""
        history = []
        if self.history_file.exists():
            try:
                history = json.loads(self.history_file.read_text(encoding='utf-8'))
            except:
                pass
                
        history.append(result.to_dict())
        history = history[-100:]  # Keep last 100
        
        self.history_file.write_text(json.dumps(history, indent=2), encoding='utf-8')
        
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        if not self.history_file.exists():
            return {"total_optimizations": 0, "by_agent": {}}
            
        history = json.loads(self.history_file.read_text(encoding='utf-8'))
        
        stats = {
            "total_optimizations": len(history),
            "by_agent": {},
            "avg_improvement": 0
        }
        
        improvements = []
        for entry in history:
            agent = entry["agent_name"]
            if agent not in stats["by_agent"]:
                stats["by_agent"][agent] = {"count": 0, "total_improvement": 0}
            stats["by_agent"][agent]["count"] += 1
            stats["by_agent"][agent]["total_improvement"] += entry["improvement"]
            improvements.append(entry["improvement"])
            
        if improvements:
            stats["avg_improvement"] = sum(improvements) / len(improvements)
            
        return stats


# ==================== Integration with Self-Learning ====================

class DSPyLearningBridge:
    """
    Bridge between DSPy and Self-Learning system.
    
    Converts successful tasks into DSPy training examples
    and triggers optimization cycles.
    """
    
    def __init__(self):
        self.optimizer = AgentOptimizer()
        self.pending_examples: Dict[str, List[dict]] = {}
        self.optimization_threshold = 10  # Trigger optimization after 10 new examples
        
    def record_success(
        self,
        agent_name: str,
        inputs: Dict[str, str],
        outputs: Dict[str, str],
        score: float = 1.0
    ) -> None:
        """
        Record a successful task for learning.
        
        Args:
            agent_name: PM, SA, DEV, TESTER, etc.
            inputs: What was given to the agent
            outputs: What the agent produced
            score: Quality score (0-1), e.g., from Judge
        """
        self.optimizer.add_successful_example(agent_name, inputs, outputs, score)
        
        # Track pending for optimization trigger
        if agent_name not in self.pending_examples:
            self.pending_examples[agent_name] = []
        self.pending_examples[agent_name].append({"inputs": inputs, "outputs": outputs})
        
        # Check if we should trigger optimization
        if len(self.pending_examples.get(agent_name, [])) >= self.optimization_threshold:
            print(f"🔄 Optimization threshold reached for {agent_name}")
            self.pending_examples[agent_name] = []
            
    def create_metric(self, output_fields: List[str]) -> Callable:
        """Create a simple metric function for optimization."""
        def metric(example, prediction, trace=None):
            score = 0
            for field in output_fields:
                if hasattr(prediction, field):
                    pred_value = getattr(prediction, field)
                    expected = getattr(example, field, "")
                    
                    # Simple length-based scoring (can be enhanced)
                    if pred_value and len(pred_value) > 50:
                        score += 0.5
                    if expected and pred_value:
                        # Check for key terms overlap
                        expected_terms = set(expected.lower().split())
                        pred_terms = set(pred_value.lower().split())
                        overlap = len(expected_terms & pred_terms) / max(len(expected_terms), 1)
                        score += overlap * 0.5
                        
            return score / len(output_fields) if output_fields else 0
            
        return metric


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="DSPy Integration - Declarative Self-Improving Agents")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add example
    add_parser = subparsers.add_parser("add-example", help="Add training example")
    add_parser.add_argument("--agent", required=True, help="Agent name (PM, SA, DEV, etc.)")
    add_parser.add_argument("--inputs", required=True, help="JSON inputs")
    add_parser.add_argument("--outputs", required=True, help="JSON outputs")
    add_parser.add_argument("--score", type=float, default=1.0, help="Quality score")
    
    # Stats
    subparsers.add_parser("stats", help="Show optimization statistics")
    
    # Check
    subparsers.add_parser("check", help="Check DSPy availability")
    
    args = parser.parse_args()
    
    if args.command == "add-example":
        optimizer = AgentOptimizer()
        inputs = json.loads(args.inputs)
        outputs = json.loads(args.outputs)
        optimizer.add_successful_example(args.agent, inputs, outputs, args.score)
        
    elif args.command == "stats":
        optimizer = AgentOptimizer()
        stats = optimizer.get_optimization_stats()
        print("📊 DSPy Optimization Statistics:\n")
        print(f"  Total Optimizations: {stats['total_optimizations']}")
        print(f"  Avg Improvement: {stats['avg_improvement']:.3f}")
        print("\n  By Agent:")
        for agent, data in stats["by_agent"].items():
            print(f"    {agent}: {data['count']} optimizations, +{data['total_improvement']:.3f} total improvement")
            
    elif args.command == "check":
        if DSPY_AVAILABLE:
            print("✅ DSPy is installed and available")
            print(f"   Version: {dspy.__version__ if hasattr(dspy, '__version__') else 'unknown'}")
        else:
            print("❌ DSPy is not installed")
            print("   Install with: pip install dspy")
            
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
