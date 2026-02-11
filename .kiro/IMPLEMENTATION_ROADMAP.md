# Implementation Roadmap: Fixing Core Modules

## Overview
This document provides exact file locations and implementation guidance for fixing all identified gaps in the Agentic SDLC system.

---

## PART 1: CRITICAL ENTRY POINT FIXES

### Fix 1.1: asdlc.py Path Error

**File:** `asdlc.py`  
**Line:** 10  
**Current:**
```python
REPO_ROOT = Path(__file__).resolve().parent.parent
```

**Fix:**
```python
REPO_ROOT = Path(__file__).resolve().parent
```

**Reason:** The script is at the root level, so `.parent` gets the repo root. `.parent.parent` goes up one level too far.

---

### Fix 1.2: pyproject.toml Entry Point Error

**File:** `pyproject.toml`  
**Line:** ~280 (in `[project.scripts]` section)  
**Current:**
```toml
[project.scripts]
agentic = "agentic_sdlc.cli:main"
agentic-sdlc = "agentic_sdlc.cli:main"
asdlc = "agentic_sdlc.cli:main"
```

**Fix:**
```toml
[project.scripts]
agentic = "agentic_sdlc.cli.main:main"
agentic-sdlc = "agentic_sdlc.cli.main:main"
asdlc = "agentic_sdlc.cli.main:main"
```

**Reason:** The entry point should reference the `main` function in the `main.py` module, not the `cli` package itself.

---

## PART 2: MISSING CLASS IMPLEMENTATIONS

### Missing Class 1: WorkflowRunner

**File:** `src/agentic_sdlc/infrastructure/automation/workflow_engine.py`  
**Location:** Add after the `WorkflowEngine` class  
**Status:** Currently exported from `__init__.py` but not defined

**Implementation:**
```python
class WorkflowRunner:
    """Executes workflows with state management and error handling."""
    
    def __init__(self, engine: Optional[WorkflowEngine] = None) -> None:
        """Initialize the workflow runner.
        
        Args:
            engine: Optional WorkflowEngine instance. If None, creates a new one.
        """
        self.engine = engine or WorkflowEngine()
        self.running_workflows: Dict[str, Dict[str, Any]] = {}
    
    def run(self, workflow: "Workflow") -> Dict[str, Any]:
        """Execute a workflow.
        
        Args:
            workflow: The workflow to execute.
            
        Returns:
            Dictionary containing execution results.
        """
        # Implementation placeholder
        return {"status": "completed", "workflow_id": workflow.name}
    
    def get_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a running workflow.
        
        Args:
            workflow_id: The ID of the workflow.
            
        Returns:
            Status dictionary or None if not found.
        """
        return self.running_workflows.get(workflow_id)
```

**Update `__init__.py`:**
```python
from .workflow_engine import WorkflowEngine, WorkflowRunner

__all__ = [
    "WorkflowEngine",
    "WorkflowRunner",
]
```

---

### Missing Class 2: BridgeRegistry

**File:** `src/agentic_sdlc/infrastructure/bridge/bridge.py`  
**Location:** Add after the `Bridge` class  
**Status:** Currently exported from `__init__.py` but not defined

**Implementation:**
```python
class BridgeRegistry:
    """Registry for managing bridge instances."""
    
    def __init__(self) -> None:
        """Initialize the bridge registry."""
        self._bridges: Dict[str, Bridge] = {}
    
    def register(self, bridge: Bridge) -> None:
        """Register a bridge.
        
        Args:
            bridge: The bridge to register.
        """
        self._bridges[bridge.name] = bridge
    
    def unregister(self, name: str) -> None:
        """Unregister a bridge.
        
        Args:
            name: The name of the bridge to unregister.
        """
        if name in self._bridges:
            del self._bridges[name]
    
    def get(self, name: str) -> Optional[Bridge]:
        """Get a bridge by name.
        
        Args:
            name: The name of the bridge.
            
        Returns:
            The bridge or None if not found.
        """
        return self._bridges.get(name)
    
    def list_bridges(self) -> List[str]:
        """List all registered bridge names.
        
        Returns:
            List of bridge names.
        """
        return list(self._bridges.keys())
```

**Update `__init__.py`:**
```python
from .bridge import Bridge, BridgeRegistry

__all__ = [
    "Bridge",
    "BridgeRegistry",
]
```

---

### Missing Class 3: LearningStrategy

**File:** `src/agentic_sdlc/intelligence/learning/learner.py`  
**Location:** Add after the `Learner` class  
**Status:** Currently exported from `__init__.py` but not defined

**Implementation:**
```python
class LearningStrategy:
    """Base class for learning strategies."""
    
    def __init__(self, name: str) -> None:
        """Initialize the learning strategy.
        
        Args:
            name: The name of the strategy.
        """
        self.name = name
    
    def learn(self, event: LearningEvent) -> None:
        """Learn from an event.
        
        Args:
            event: The learning event.
        """
        pass
    
    def predict(self, context: Dict[str, Any]) -> Any:
        """Make a prediction based on learned patterns.
        
        Args:
            context: The context for prediction.
            
        Returns:
            The prediction result.
        """
        pass
    
    def get_patterns(self) -> List[Pattern]:
        """Get learned patterns.
        
        Returns:
            List of learned patterns.
        """
        return []
```

**Update `__init__.py`:**
```python
from .learner import Learner, LearningStrategy

__all__ = [
    "Learner",
    "LearningStrategy",
]
```

---

### Missing Class 4: MetricsCollector

**File:** `src/agentic_sdlc/intelligence/monitoring/monitor.py`  
**Location:** Add after the `Monitor` class  
**Status:** Currently exported from `__init__.py` but not defined

**Implementation:**
```python
class MetricsCollector:
    """Collects and aggregates metrics."""
    
    def __init__(self) -> None:
        """Initialize the metrics collector."""
        self.metrics: Dict[str, List[Any]] = {}
    
    def collect(self, metric_name: str, value: Any) -> None:
        """Collect a metric.
        
        Args:
            metric_name: The name of the metric.
            value: The metric value.
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(value)
    
    def get_metrics(self, metric_name: str) -> List[Any]:
        """Get collected metrics.
        
        Args:
            metric_name: The name of the metric.
            
        Returns:
            List of metric values.
        """
        return self.metrics.get(metric_name, [])
    
    def aggregate(self, metric_name: str) -> Dict[str, Any]:
        """Aggregate metrics.
        
        Args:
            metric_name: The name of the metric.
            
        Returns:
            Dictionary with aggregated statistics.
        """
        values = self.metrics.get(metric_name, [])
        if not values:
            return {}
        return {
            "count": len(values),
            "min": min(values) if all(isinstance(v, (int, float)) for v in values) else None,
            "max": max(values) if all(isinstance(v, (int, float)) for v in values) else None,
        }
```

**Update `__init__.py`:**
```python
from .monitor import Monitor, MetricsCollector

__all__ = [
    "Monitor",
    "MetricsCollector",
]
```

---

### Missing Class 5: DecisionEngine

**File:** `src/agentic_sdlc/intelligence/reasoning/reasoner.py`  
**Location:** Add after the `Reasoner` class  
**Status:** Currently exported from `__init__.py` but not defined

**Implementation:**
```python
class DecisionEngine:
    """Engine for making decisions based on reasoning."""
    
    def __init__(self, reasoner: Optional[Reasoner] = None) -> None:
        """Initialize the decision engine.
        
        Args:
            reasoner: Optional Reasoner instance.
        """
        self.reasoner = reasoner or Reasoner()
    
    def decide(self, context: Dict[str, Any]) -> Any:
        """Make a decision based on context.
        
        Args:
            context: The decision context.
            
        Returns:
            The decision result.
        """
        # Implementation placeholder
        return {"decision": "pending", "confidence": 0.0}
    
    def evaluate_options(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate multiple options.
        
        Args:
            options: List of options to evaluate.
            
        Returns:
            Evaluation results.
        """
        return {"best_option": None, "scores": {}}
```

**Update `__init__.py`:**
```python
from .reasoner import Reasoner, DecisionEngine

__all__ = [
    "Reasoner",
    "DecisionEngine",
]
```

---

### Missing Class 6: TeamCoordinator

**File:** `src/agentic_sdlc/intelligence/collaboration/collaborator.py`  
**Location:** Add after the `Collaborator` class  
**Status:** Currently exported from `__init__.py` but not defined

**Implementation:**
```python
class TeamCoordinator:
    """Coordinates collaboration between multiple agents."""
    
    def __init__(self) -> None:
        """Initialize the team coordinator."""
        self.team_members: Dict[str, Collaborator] = {}
        self.messages: List[CollaborationMessage] = []
    
    def add_member(self, member: Collaborator) -> None:
        """Add a team member.
        
        Args:
            member: The collaborator to add.
        """
        self.team_members[member.agent_name] = member
    
    def remove_member(self, agent_name: str) -> None:
        """Remove a team member.
        
        Args:
            agent_name: The name of the agent to remove.
        """
        if agent_name in self.team_members:
            del self.team_members[agent_name]
    
    def broadcast_message(self, message: CollaborationMessage) -> None:
        """Broadcast a message to all team members.
        
        Args:
            message: The message to broadcast.
        """
        self.messages.append(message)
    
    def coordinate_task(self, task: Dict[str, Any]) -> CollaborationResult:
        """Coordinate a task among team members.
        
        Args:
            task: The task to coordinate.
            
        Returns:
            The coordination result.
        """
        return CollaborationResult(
            success=True,
            result={"status": "coordinated"},
            messages=[]
        )
```

**Update `__init__.py`:**
```python
from .collaborator import Collaborator, TeamCoordinator

__all__ = [
    "Collaborator",
    "TeamCoordinator",
]
```

---

## PART 3: MISSING FUNCTION IMPLEMENTATIONS

### Missing Functions 1-2: Core Config Functions

**File:** `src/agentic_sdlc/core/config.py`  
**Location:** Add at the end of the file  
**Status:** Functions are exported from `__init__.py` but not defined

**Implementation:**
```python
def get_config() -> Config:
    """Get the global configuration instance.
    
    Returns:
        The global Config instance.
    """
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config


def load_config(config_path: Optional[Union[str, Path]] = None) -> Config:
    """Load configuration from a file.
    
    Args:
        config_path: Path to the configuration file. If None, uses default.
        
    Returns:
        The loaded Config instance.
    """
    config = Config(config_path=config_path)
    config.validate()
    return config


# Add at module level
_global_config: Optional[Config] = None
```

**Update `__init__.py` exports:**
```python
from .config import Config, get_config, load_config
```

---

### Missing Functions 3-4: Agent Registry Functions

**File:** `src/agentic_sdlc/orchestration/agents/__init__.py`  
**Location:** Add at the end of the file  
**Status:** Functions are exported but not defined

**Implementation:**
```python
# Add to agents/__init__.py

_agent_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry.
    
    Returns:
        The global AgentRegistry instance.
    """
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry


def create_agent(
    name: str,
    role: str,
    capabilities: Optional[List[str]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Agent:
    """Create and register a new agent.
    
    Args:
        name: The agent name.
        role: The agent role.
        capabilities: Optional list of capabilities.
        config: Optional configuration dictionary.
        
    Returns:
        The created Agent instance.
    """
    agent = Agent(
        id=name,
        name=name,
        role=role,
        capabilities=capabilities or [],
        config=config or {},
    )
    registry = get_agent_registry()
    registry.register(agent)
    return agent
```

**Update `__init__.py` exports:**
```python
from .agent import Agent
from .registry import AgentRegistry
from . import create_agent, get_agent_registry

__all__ = [
    "Agent",
    "AgentRegistry",
    "create_agent",
    "get_agent_registry",
]
```

---

### Missing Functions 5-7: Model Client Functions

**File:** `src/agentic_sdlc/orchestration/models/__init__.py`  
**Location:** Add at the end of the file  
**Status:** Functions are exported but not defined

**Implementation:**
```python
# Add to models/__init__.py

_model_clients: Dict[str, ModelClient] = {}


def create_model_client(
    provider: str,
    model_name: str,
    config: Optional[Dict[str, Any]] = None,
) -> ModelClient:
    """Create a new model client.
    
    Args:
        provider: The model provider (e.g., 'openai', 'anthropic').
        model_name: The model name.
        config: Optional configuration dictionary.
        
    Returns:
        The created ModelClient instance.
    """
    model_config = ModelConfig(
        provider=provider,
        model_name=model_name,
        config=config or {},
    )
    client = ModelClient(config=model_config)
    return client


def get_model_client(provider: str, model_name: str) -> Optional[ModelClient]:
    """Get a registered model client.
    
    Args:
        provider: The model provider.
        model_name: The model name.
        
    Returns:
        The ModelClient instance or None if not found.
    """
    key = f"{provider}:{model_name}"
    return _model_clients.get(key)


def register_model_client(
    provider: str,
    model_name: str,
    client: ModelClient,
) -> None:
    """Register a model client.
    
    Args:
        provider: The model provider.
        model_name: The model name.
        client: The ModelClient instance to register.
    """
    key = f"{provider}:{model_name}"
    _model_clients[key] = client
```

**Update `__init__.py` exports:**
```python
from .client import ModelClient, create_model_client, get_model_client, register_model_client
from .model_config import ModelConfig

__all__ = [
    "ModelConfig",
    "ModelClient",
    "create_model_client",
    "get_model_client",
    "register_model_client",
]
```

---

## PART 4: CLI COMMAND IMPLEMENTATIONS

### File: `src/agentic_sdlc/cli/main.py`

**Current Status:** Has 3 stub commands, needs implementation and additional commands

**Implementation Strategy:**

1. **Replace stub commands with real implementations**
2. **Add missing command groups**
3. **Integrate with SDK components**

**Recommended Structure:**
```python
# Keep the basic CLI structure but enhance commands

@cli.command()
@click.option('--name', required=True, help='Project name')
@click.option('--template', default='basic', help='Project template')
def init(name: str, template: str) -> None:
    """Initialize a new Agentic SDLC project."""
    # Implementation using SDK components
    pass

@cli.group()
def agent() -> None:
    """Manage agents."""
    pass

@agent.command()
@click.option('--name', required=True)
@click.option('--role', required=True)
def create(name: str, role: str) -> None:
    """Create a new agent."""
    pass

@cli.group()
def workflow() -> None:
    """Manage workflows."""
    pass

@workflow.command()
@click.argument('workflow_name')
def run(workflow_name: str) -> None:
    """Run a workflow."""
    pass

# ... and so on for other command groups
```

---

## PART 5: VERIFICATION CHECKLIST

After implementing all fixes, verify:

### Entry Points
- [ ] `asdlc.py` runs without path errors
- [ ] `pip install -e .` installs correctly
- [ ] `asdlc --version` works
- [ ] `agentic --version` works
- [ ] `agentic-sdlc --version` works

### Imports
- [ ] `from agentic_sdlc import WorkflowRunner` works
- [ ] `from agentic_sdlc import BridgeRegistry` works
- [ ] `from agentic_sdlc import LearningStrategy` works
- [ ] `from agentic_sdlc import MetricsCollector` works
- [ ] `from agentic_sdlc import DecisionEngine` works
- [ ] `from agentic_sdlc import TeamCoordinator` works
- [ ] `from agentic_sdlc import get_config` works
- [ ] `from agentic_sdlc import load_config` works
- [ ] `from agentic_sdlc import create_agent` works
- [ ] `from agentic_sdlc import get_agent_registry` works
- [ ] `from agentic_sdlc import create_model_client` works
- [ ] `from agentic_sdlc import get_model_client` works
- [ ] `from agentic_sdlc import register_model_client` works

### Functionality
- [ ] `get_config()` returns a Config instance
- [ ] `load_config()` loads configuration
- [ ] `create_agent()` creates and registers agents
- [ ] `get_agent_registry()` returns the registry
- [ ] `create_model_client()` creates model clients
- [ ] `get_model_client()` retrieves registered clients
- [ ] `register_model_client()` registers clients
- [ ] CLI commands execute without errors

---

## PART 6: TESTING STRATEGY

After implementation, add tests:

```python
# tests/unit/test_missing_implementations.py

def test_workflow_runner_creation():
    from agentic_sdlc import WorkflowRunner
    runner = WorkflowRunner()
    assert runner is not None

def test_bridge_registry_creation():
    from agentic_sdlc import BridgeRegistry
    registry = BridgeRegistry()
    assert registry is not None

def test_get_config():
    from agentic_sdlc import get_config
    config = get_config()
    assert config is not None

def test_create_agent():
    from agentic_sdlc import create_agent
    agent = create_agent(name="test", role="developer")
    assert agent.name == "test"
    assert agent.role == "developer"

# ... and so on for all new implementations
```

---

## PART 7: TIMELINE ESTIMATE

| Task | Effort | Priority |
|------|--------|----------|
| Fix entry points (2 files) | 5 min | 🔴 Critical |
| Create 6 missing classes | 30 min | 🔴 Critical |
| Implement 7 missing functions | 1 hour | 🔴 Critical |
| Implement CLI commands | 2-4 hours | 🟠 High |
| Add tests | 2-4 hours | 🟡 Medium |
| Documentation | 1-2 hours | 🟡 Medium |
| **Total** | **6-12 hours** | |

---

## PART 8: NEXT STEPS

1. **Start with Part 1** - Fix the 2 entry point errors (5 minutes)
2. **Then Part 2** - Create the 6 missing classes (30 minutes)
3. **Then Part 3** - Implement the 7 missing functions (1 hour)
4. **Then Part 4** - Implement CLI commands (2-4 hours)
5. **Then Part 5** - Verify all fixes work (30 minutes)
6. **Then Part 6** - Add comprehensive tests (2-4 hours)

This systematic approach ensures all critical gaps are fixed before moving to enhancements.

