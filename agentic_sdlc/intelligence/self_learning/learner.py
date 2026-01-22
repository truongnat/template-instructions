"""
Learner - Pattern recognition and auto-learning engine.

Part of Layer 2: Intelligence Layer.
Consolidates learning from tools/brain/learner.py
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class PatternType(Enum):
    """Types of patterns recognized."""
    ERROR = "error"
    SUCCESS = "success"
    WORKFLOW = "workflow"
    OPTIMIZATION = "optimization"
    BEHAVIOR = "behavior"


@dataclass
class Pattern:
    """Represents a learned pattern."""
    id: str
    type: PatternType
    description: str
    trigger: str
    response: str
    confidence: float = 0.5
    occurrences: int = 1
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "description": self.description,
            "trigger": self.trigger,
            "response": self.response,
            "confidence": self.confidence,
            "occurrences": self.occurrences,
            "last_seen": self.last_seen,
            "metadata": self.metadata
        }


@dataclass
class LearningEvent:
    """Represents a learning event."""
    event_type: str
    description: str
    context: Dict
    outcome: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "description": self.description,
            "context": self.context,
            "outcome": self.outcome,
            "timestamp": self.timestamp
        }


class Learner:
    """
    Pattern recognition and auto-learning engine.
    
    Features:
    - Recognize patterns from tasks and outcomes
    - Learn from errors and successes
    - Build knowledge over time
    - Provide recommendations based on patterns
    """

    def __init__(self, storage_file: Optional[Path] = None):
        if storage_file is None:
            brain_dir = Path(".brain")
            brain_dir.mkdir(parents=True, exist_ok=True)
            self.storage_file = brain_dir / "learner-log.json"
        else:
            self.storage_file = storage_file
        self.patterns: Dict[str, Pattern] = {}
        self.events: List[LearningEvent] = []
        self._load_data()

    def _load_data(self):
        """Load patterns and events from storage."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    for p in data.get("patterns", []):
                        pattern = Pattern(
                            id=p["id"],
                            type=PatternType(p["type"]),
                            description=p["description"],
                            trigger=p["trigger"],
                            response=p["response"],
                            confidence=p.get("confidence", 0.5),
                            occurrences=p.get("occurrences", 1),
                            last_seen=p.get("last_seen"),
                            metadata=p.get("metadata", {})
                        )
                        self.patterns[pattern.id] = pattern
                    
                    for e in data.get("events", [])[-100:]:  # Keep last 100
                        self.events.append(LearningEvent(**e))
                        
            except (json.JSONDecodeError, IOError):
                pass

    def _save_data(self):
        """Save patterns and events to storage."""
        data = {
            "patterns": [p.to_dict() for p in self.patterns.values()],
            "events": [e.to_dict() for e in self.events[-100:]],
            "updated_at": datetime.now().isoformat()
        }
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def learn(self, description: str, context: Optional[Dict] = None) -> Dict:
        """
        Record a learning event and extract patterns.
        
        Args:
            description: What was learned
            context: Additional context
            
        Returns:
            Learning result with any new patterns
        """
        event = LearningEvent(
            event_type="general",
            description=description,
            context=context or {},
            outcome="recorded"
        )
        self.events.append(event)
        
        # Try to extract patterns
        new_patterns = self._extract_patterns(description, context or {})
        
        self._save_data()
        
        return {
            "recorded": True,
            "description": description,
            "patterns_found": len(new_patterns),
            "total_patterns": len(self.patterns)
        }

    def learn_error(self, error: str, resolution: str, context: Optional[Dict] = None) -> Dict:
        """
        Learn from an error and its resolution.
        """
        pattern_id = f"ERR-{len(self.patterns):04d}"
        
        # Check if similar pattern exists
        for p in self.patterns.values():
            if p.type == PatternType.ERROR and error.lower() in p.trigger.lower():
                p.occurrences += 1
                p.confidence = min(p.confidence + 0.1, 1.0)
                p.last_seen = datetime.now().isoformat()
                self._save_data()
                return {
                    "recorded": True,
                    "pattern": p.id,
                    "message": "Updated existing error pattern"
                }
        
        pattern = Pattern(
            id=pattern_id,
            type=PatternType.ERROR,
            description=f"Error pattern: {error[:50]}",
            trigger=error,
            response=resolution,
            confidence=0.6,
            metadata=context or {}
        )
        
        self.patterns[pattern_id] = pattern
        self.events.append(LearningEvent(
            event_type="error",
            description=error,
            context={"resolution": resolution, **(context or {})},
            outcome="pattern_created"
        ))
        
        self._save_data()
        return {
            "recorded": True,
            "pattern": pattern_id,
            "message": "New error pattern created"
        }

    def learn_success(self, task: str, approach: str, context: Optional[Dict] = None) -> Dict:
        """
        Learn from a successful task completion.
        """
        pattern_id = f"SUC-{len(self.patterns):04d}"
        
        pattern = Pattern(
            id=pattern_id,
            type=PatternType.SUCCESS,
            description=f"Success: {task[:50]}",
            trigger=task,
            response=approach,
            confidence=0.7,
            metadata=context or {}
        )
        
        self.patterns[pattern_id] = pattern
        self.events.append(LearningEvent(
            event_type="success",
            description=task,
            context={"approach": approach, **(context or {})},
            outcome="pattern_created"
        ))
        
        self._save_data()
        return {
            "recorded": True,
            "pattern": pattern_id,
            "message": "Success pattern recorded"
        }

    def find_similar(self, query: str, pattern_type: Optional[PatternType] = None) -> List[Pattern]:
        """
        Find patterns similar to the query.
        """
        query_lower = query.lower()
        results = []
        
        for pattern in self.patterns.values():
            if pattern_type and pattern.type != pattern_type:
                continue
            
            # Simple keyword matching
            if any(word in pattern.trigger.lower() or word in pattern.description.lower() 
                   for word in query_lower.split() if len(word) > 3):
                results.append(pattern)
        
        # Sort by confidence and occurrences
        results.sort(key=lambda p: (p.confidence, p.occurrences), reverse=True)
        return results[:10]

    def get_recommendation(self, task: str) -> Optional[Dict]:
        """
        Get recommendation for a task based on learned patterns.
        """
        similar = self.find_similar(task, PatternType.SUCCESS)
        
        if similar:
            best = similar[0]
            return {
                "recommendation": best.response,
                "confidence": best.confidence,
                "based_on": best.id,
                "occurrences": best.occurrences
            }
        
        return None

    def learn_from_observer(self, violations: List[Dict]) -> Dict:
        """
        Learn from Observer violations.
        
        Args:
            violations: List of violation dictionaries
        """
        learned_count = 0
        for v in violations:
            description = f"Observer violation: {v.get('rule')} in {v.get('location')}"
            context = {"type": "violation", "severity": v.get("severity"), "rule": v.get("rule")}
            
            # Learn error pattern from critical violations
            if v.get("severity") == "CRITICAL":
                self.learn_error(
                    error=description,
                    resolution=v.get("recommendation", "Fix violation"),
                    context=context
                )
                learned_count += 1
                
        return {"learned_count": learned_count, "total_violations": len(violations)}

    def learn_from_judge(self, score_result: Dict) -> Dict:
        """
        Learn from Judge score results.
        
        Args:
            score_result: Score result dictionary
        """
        final_score = score_result.get("finalScore", 0)
        file_path = score_result.get("file", "unknown")
        
        # Learn from low scores
        if final_score < 6.0:
            improvements = score_result.get("improvements", [])
            for imp in improvements:
                self.learn_error(
                    error=f"Low quality score in {file_path}",
                    resolution=imp,
                    context={"score": final_score, "type": "quality_issue"}
                )
            return {"status": "learned_from_issues", "issues_count": len(improvements)}
        
        # Learn from high scores (best practices)
        elif final_score >= 9.0:
            self.learn_success(
                task=f"High quality implementation: {file_path}",
                approach="Followed all quality guidelines",
                context={"score": final_score, "type": "best_practice"}
            )
            return {"status": "learned_success"}
            
        return {"status": "no_significant_learning"}

    def learn_from_ab_test(self, test_result: Dict) -> Dict:
        """
        Learn from A/B test results.
        
        Args:
            test_result: Comparison result dictionary
        """
        winner = test_result.get("recommendation")
        if winner in ["A", "B"]:
            winning_opt = test_result.get(f"option_{winner.lower()}", {})
            name = winning_opt.get("name", "Unknown")
            
            self.learn_success(
                task=f"A/B Test Winner: {test_result.get('title')}",
                approach=f"Chosen approach: {name}",
                context={
                    "test_id": test_result.get("test_id"),
                    "confidence": test_result.get("confidence"),
                    "reason": "Superior metrics in A/B test"
                }
            )
            return {"status": "learned_winner", "winner": name}
            
        return {"status": "no_clear_winner"}

    def _extract_patterns(self, description: str, context: Dict) -> List[Pattern]:
        """Extract patterns from description."""
        new_patterns = []
        
        # Simple heuristics for pattern extraction
        keywords = ["fixed", "resolved", "implemented", "created", "updated"]
        
        for kw in keywords:
            if kw in description.lower():
                pattern_type = PatternType.SUCCESS if kw in ["fixed", "resolved"] else PatternType.WORKFLOW
                # Pattern creation logic here if needed
                break
        
        return new_patterns

    def get_stats(self) -> Dict:
        """Get learning statistics."""
        by_type = {}
        for pattern in self.patterns.values():
            t = pattern.type.value
            by_type[t] = by_type.get(t, 0) + 1
        
        return {
            "total_patterns": len(self.patterns),
            "total_events": len(self.events),
            "patterns_by_type": by_type,
            "avg_confidence": sum(p.confidence for p in self.patterns.values()) / max(len(self.patterns), 1)
        }

    def list_patterns(self, pattern_type: Optional[PatternType] = None) -> List[Pattern]:
        """List all patterns."""
        patterns = list(self.patterns.values())
        if pattern_type:
            patterns = [p for p in patterns if p.type == pattern_type]
        return sorted(patterns, key=lambda p: p.last_seen, reverse=True)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Learner - Layer 2 Intelligence")
    parser.add_argument("--learn", type=str, help="Record a learning")
    parser.add_argument("--error", type=str, help="Learn from error")
    parser.add_argument("--resolution", type=str, help="Error resolution")
    parser.add_argument("--success", type=str, help="Learn from success")
    parser.add_argument("--approach", type=str, help="Success approach")
    parser.add_argument("--find", type=str, help="Find similar patterns")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--patterns", action="store_true", help="List patterns")
    
    args = parser.parse_args()
    learner = Learner()
    
    if args.learn:
        result = learner.learn(args.learn)
        print(json.dumps(result, indent=2))
    
    elif args.error and args.resolution:
        result = learner.learn_error(args.error, args.resolution)
        print(json.dumps(result, indent=2))
    
    elif args.success and args.approach:
        result = learner.learn_success(args.success, args.approach)
        print(json.dumps(result, indent=2))
    
    elif args.find:
        patterns = learner.find_similar(args.find)
        for p in patterns:
            print(f"[{p.confidence:.1f}] {p.id}: {p.description}")
    
    elif args.stats:
        print(json.dumps(learner.get_stats(), indent=2))
    
    elif args.patterns:
        for p in learner.list_patterns():
            print(f"[{p.type.value}] {p.id}: {p.description}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

