# Layer 2: Intelligence

> The Brain's intelligence layer - self-learning, routing, monitoring, and optimization.

## Architecture

```
Layer 3 (Infrastructure) → Layer 2 (Intelligence) → Layer 1 (Core)
```

## Components (10 Total)

| Component | Files | Purpose |
|-----------|-------|---------|
| **scorer** | `input_scorer.py`, `output_scorer.py`, `metrics.py` | Quality evaluation |
| **router** | `workflow_router.py`, `agent_router.py`, `rules_engine.py` | Request routing |
| **monitor** | `observer.py`, `rule_checker.py`, `audit_logger.py` | Compliance |
| **ab_test** | `ab_tester.py`, `comparator.py` | A/B testing |
| **self_learning** | `learner.py`, `self_improver.py`, `pattern_engine.py` | Pattern recognition |
| **artifact_gen** | `doc_generator.py`, `report_generator.py`, `template_engine.py` | Doc generation |
| **proxy** | `model_proxy.py`, `cost_tracker.py` | Model selection |
| **task_manager** | `task_board.py`, `sprint_manager.py` | Kanban board |
| **performance** | `metrics_collector.py`, `flow_optimizer.py` | Optimization |
| **judge** | `quality_judge.py` | Artifact scoring |

## Usage

### CLI

```bash
agentic-sdlc score --score "request"
agentic-sdlc route --route "fix bug"
agentic-sdlc monitor --status
```

### Python

```python
from tools.layer2 import InputScorer, QualityJudge, WorkflowRouter

scorer = InputScorer()
judge = QualityJudge()
router = WorkflowRouter()
```

---

*Layer 2: Intelligence - 10 components, 22 Python files.*
