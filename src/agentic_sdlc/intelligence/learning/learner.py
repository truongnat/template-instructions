"""Self-learning engine for pattern recognition and auto-learning."""

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import json
from datetime import datetime


class PatternType(Enum):
    """Types of patterns that can be learned."""
    ERROR = "error"
    SUCCESS = "success"
    TASK = "task"


@dataclass
class Pattern:
    """Represents a learned pattern."""
    pattern_type: PatternType
    description: str
    context: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    frequency: int = 1

    def to_dict(self) -> dict:
        """Convert pattern to dictionary."""
        return {
            **asdict(self),
            "pattern_type": self.pattern_type.value,
        }


@dataclass
class LearningEvent:
    """Represents a learning event."""
    event_type: str
    description: str
    context: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert event to dictionary."""
        return asdict(self)


class Learner:
    """Pattern recognition and auto-learning engine."""

    def __init__(self, storage_file: Optional[Path] = None):
        """Initialize the learner.

        Args:
            storage_file: Optional path to store learned patterns
        """
        self.storage_file = storage_file or Path.home() / ".agentic_sdlc" / "learner.json"
        self.patterns: List[Pattern] = []
        self.events: List[LearningEvent] = []
        self._load_data()

    def _load_data(self):
        """Load previously learned patterns from storage."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r") as f:
                    data = json.load(f)
                    for p in data.get("patterns", []):
                        pattern = Pattern(
                            pattern_type=PatternType(p["pattern_type"]),
                            description=p["description"],
                            context=p["context"],
                            timestamp=p.get("timestamp", datetime.now().isoformat()),
                            frequency=p.get("frequency", 1),
                        )
                        self.patterns.append(pattern)
                    for e in data.get("events", []):
                        event = LearningEvent(
                            event_type=e["event_type"],
                            description=e["description"],
                            context=e["context"],
                            timestamp=e.get("timestamp", datetime.now().isoformat()),
                        )
                        self.events.append(event)
            except Exception:
                pass

    def _save_data(self):
        """Save learned patterns to storage."""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "patterns": [p.to_dict() for p in self.patterns],
            "events": [e.to_dict() for e in self.events],
        }
        with open(self.storage_file, "w") as f:
            json.dump(data, f, indent=2)

    def learn(self, description: str, context: Optional[Dict] = None) -> Dict:
        """Learn a general pattern.

        Args:
            description: Description of the pattern
            context: Optional context information

        Returns:
            Dictionary with learning result
        """
        context = context or {}
        pattern = Pattern(
            pattern_type=PatternType.TASK,
            description=description,
            context=context,
        )
        self.patterns.append(pattern)
        self._save_data()
        return {"status": "learned", "pattern": pattern.to_dict()}

    def learn_error(
        self, error: str, resolution: str, context: Optional[Dict] = None
    ) -> Dict:
        """Learn from an error and its resolution.

        Args:
            error: Description of the error
            resolution: How the error was resolved
            context: Optional context information

        Returns:
            Dictionary with learning result
        """
        context = context or {}
        context["resolution"] = resolution
        pattern = Pattern(
            pattern_type=PatternType.ERROR,
            description=error,
            context=context,
        )
        self.patterns.append(pattern)
        self._save_data()
        return {"status": "error_learned", "pattern": pattern.to_dict()}

    def learn_success(
        self, task: str, approach: str, context: Optional[Dict] = None
    ) -> Dict:
        """Learn from a successful task execution.

        Args:
            task: Description of the task
            approach: The approach that was successful
            context: Optional context information

        Returns:
            Dictionary with learning result
        """
        context = context or {}
        context["approach"] = approach
        pattern = Pattern(
            pattern_type=PatternType.SUCCESS,
            description=task,
            context=context,
        )
        self.patterns.append(pattern)
        self._save_data()
        return {"status": "success_learned", "pattern": pattern.to_dict()}

    def find_similar(
        self, query: str, pattern_type: Optional[PatternType] = None
    ) -> List[Pattern]:
        """Find patterns similar to a query.

        Args:
            query: Query string to search for
            pattern_type: Optional pattern type to filter by

        Returns:
            List of similar patterns
        """
        results = []
        query_lower = query.lower()
        for pattern in self.patterns:
            if pattern_type and pattern.pattern_type != pattern_type:
                continue
            if query_lower in pattern.description.lower():
                results.append(pattern)
        return results

    def get_recommendation(self, task: str) -> Optional[Dict]:
        """Get a recommendation for a task based on learned patterns.

        Args:
            task: Description of the task

        Returns:
            Recommendation dictionary or None
        """
        similar = self.find_similar(task, PatternType.SUCCESS)
        if similar:
            best = max(similar, key=lambda p: p.frequency)
            return {
                "task": task,
                "recommendation": best.context.get("approach"),
                "confidence": min(best.frequency / 10.0, 1.0),
            }
        return None

    def learn_from_observer(self, violations: List[Dict]) -> Dict:
        """Learn from observer violations.

        Args:
            violations: List of violation dictionaries

        Returns:
            Dictionary with learning result
        """
        for violation in violations:
            pattern = Pattern(
                pattern_type=PatternType.ERROR,
                description=f"Violation: {violation.get('type', 'unknown')}",
                context=violation,
            )
            self.patterns.append(pattern)
        self._save_data()
        return {"status": "learned_from_observer", "violations_processed": len(violations)}

    def learn_from_judge(self, score_result: Dict) -> Dict:
        """Learn from judge scoring results.

        Args:
            score_result: Judge scoring result dictionary

        Returns:
            Dictionary with learning result
        """
        pattern = Pattern(
            pattern_type=PatternType.TASK,
            description=f"Judge score: {score_result.get('score', 'unknown')}",
            context=score_result,
        )
        self.patterns.append(pattern)
        self._save_data()
        return {"status": "learned_from_judge", "pattern": pattern.to_dict()}

    def learn_from_ab_test(self, test_result: Dict) -> Dict:
        """Learn from A/B test results.

        Args:
            test_result: A/B test result dictionary

        Returns:
            Dictionary with learning result
        """
        winner = test_result.get("winner", "unknown")
        pattern = Pattern(
            pattern_type=PatternType.SUCCESS,
            description=f"A/B test winner: {winner}",
            context=test_result,
        )
        self.patterns.append(pattern)
        self._save_data()
        return {"status": "learned_from_ab_test", "pattern": pattern.to_dict()}

    def _extract_patterns(self, description: str, context: Dict) -> List[Pattern]:
        """Extract patterns from description and context.

        Args:
            description: Description to extract patterns from
            context: Context information

        Returns:
            List of extracted patterns
        """
        patterns = []
        # Simple pattern extraction - can be enhanced
        if "error" in description.lower():
            patterns.append(
                Pattern(
                    pattern_type=PatternType.ERROR,
                    description=description,
                    context=context,
                )
            )
        elif "success" in description.lower():
            patterns.append(
                Pattern(
                    pattern_type=PatternType.SUCCESS,
                    description=description,
                    context=context,
                )
            )
        return patterns

    def get_stats(self) -> Dict:
        """Get statistics about learned patterns.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_patterns": len(self.patterns),
            "total_events": len(self.events),
            "error_patterns": len([p for p in self.patterns if p.pattern_type == PatternType.ERROR]),
            "success_patterns": len([p for p in self.patterns if p.pattern_type == PatternType.SUCCESS]),
            "task_patterns": len([p for p in self.patterns if p.pattern_type == PatternType.TASK]),
        }

    def list_patterns(self, pattern_type: Optional[PatternType] = None) -> List[Pattern]:
        """List all patterns, optionally filtered by type.

        Args:
            pattern_type: Optional pattern type to filter by

        Returns:
            List of patterns
        """
        if pattern_type:
            return [p for p in self.patterns if p.pattern_type == pattern_type]
        return self.patterns


class LearningStrategy:
    """Base class for learning strategies."""

    def learn(self, data: Dict) -> Dict:
        """Learn from data.

        Args:
            data: Data to learn from

        Returns:
            Learning result
        """
        raise NotImplementedError
