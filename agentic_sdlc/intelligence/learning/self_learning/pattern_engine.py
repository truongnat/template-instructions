"""
Pattern Engine - Advanced pattern recognition.

Part of Layer 2: Intelligence Layer.
"""

import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class DetectedPattern:
    """A detected pattern."""
    pattern_type: str
    signature: str
    occurrences: int
    confidence: float
    examples: List[Any] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "pattern_type": self.pattern_type,
            "signature": self.signature,
            "occurrences": self.occurrences,
            "confidence": self.confidence,
            "examples": self.examples[:3],  # Limit examples
            "metadata": self.metadata
        }


class PatternEngine:
    """
    Advanced pattern recognition engine.
    
    Detects patterns in:
    - Event sequences
    - Error messages
    - User behavior
    - Workflow executions
    """

    def __init__(self):
        self.pattern_cache: Dict[str, DetectedPattern] = {}

    def detect_sequence_patterns(self, events: List[Dict]) -> List[DetectedPattern]:
        """
        Detect sequential patterns in events.
        
        Args:
            events: List of event dictionaries with 'type' field
            
        Returns:
            List of detected sequence patterns
        """
        if len(events) < 3:
            return []
        
        patterns = []
        types = [e.get("type", str(e)) for e in events]
        
        # Detect 2-grams
        bigrams = [(types[i], types[i+1]) for i in range(len(types)-1)]
        bigram_counts = Counter(bigrams)
        
        for bigram, count in bigram_counts.most_common(5):
            if count >= 2:
                patterns.append(DetectedPattern(
                    pattern_type="sequence_2",
                    signature=f"{bigram[0]} → {bigram[1]}",
                    occurrences=count,
                    confidence=min(count / len(events), 1.0),
                    metadata={"elements": list(bigram)}
                ))
        
        # Detect 3-grams
        if len(types) >= 3:
            trigrams = [(types[i], types[i+1], types[i+2]) for i in range(len(types)-2)]
            trigram_counts = Counter(trigrams)
            
            for trigram, count in trigram_counts.most_common(3):
                if count >= 2:
                    patterns.append(DetectedPattern(
                        pattern_type="sequence_3",
                        signature=f"{trigram[0]} → {trigram[1]} → {trigram[2]}",
                        occurrences=count,
                        confidence=min(count / len(events), 1.0),
                        metadata={"elements": list(trigram)}
                    ))
        
        return patterns

    def detect_frequency_patterns(self, values: List[Any]) -> List[DetectedPattern]:
        """
        Detect frequency patterns in values.
        """
        if not values:
            return []
        
        patterns = []
        counts = Counter(values)
        total = len(values)
        
        for value, count in counts.most_common(5):
            if count >= 2:
                patterns.append(DetectedPattern(
                    pattern_type="frequency",
                    signature=str(value),
                    occurrences=count,
                    confidence=count / total,
                    examples=[value],
                    metadata={"percentage": round(count / total * 100, 1)}
                ))
        
        return patterns

    def detect_error_patterns(self, errors: List[str]) -> List[DetectedPattern]:
        """
        Detect patterns in error messages.
        """
        if not errors:
            return []
        
        patterns = []
        
        # Group by common prefixes
        prefix_groups: Dict[str, List[str]] = {}
        for error in errors:
            # Extract first meaningful word
            words = error.split()
            if words:
                prefix = words[0].lower()
                prefix_groups.setdefault(prefix, []).append(error)
        
        for prefix, group in prefix_groups.items():
            if len(group) >= 2:
                patterns.append(DetectedPattern(
                    pattern_type="error_group",
                    signature=f"Errors starting with '{prefix}'",
                    occurrences=len(group),
                    confidence=len(group) / len(errors),
                    examples=group[:3],
                    metadata={"prefix": prefix}
                ))
        
        return patterns

    def detect_time_patterns(self, timestamps: List[datetime]) -> List[DetectedPattern]:
        """
        Detect time-based patterns.
        """
        if len(timestamps) < 3:
            return []
        
        patterns = []
        
        # Hour distribution
        hours = [t.hour for t in timestamps]
        hour_counts = Counter(hours)
        peak_hour, peak_count = hour_counts.most_common(1)[0]
        
        if peak_count >= len(timestamps) * 0.3:
            patterns.append(DetectedPattern(
                pattern_type="time_peak",
                signature=f"Peak activity at hour {peak_hour}:00",
                occurrences=peak_count,
                confidence=peak_count / len(timestamps),
                metadata={"hour": peak_hour, "distribution": dict(hour_counts)}
            ))
        
        # Day of week distribution
        weekdays = [t.weekday() for t in timestamps]
        weekday_counts = Counter(weekdays)
        peak_day, day_count = weekday_counts.most_common(1)[0]
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        if day_count >= len(timestamps) * 0.3:
            patterns.append(DetectedPattern(
                pattern_type="weekly_pattern",
                signature=f"Peak activity on {day_names[peak_day]}",
                occurrences=day_count,
                confidence=day_count / len(timestamps),
                metadata={"weekday": peak_day}
            ))
        
        return patterns

    def analyze_all(self, data: Dict) -> Dict:
        """
        Run all pattern detection on provided data.
        
        Args:
            data: Dict with optional keys: events, values, errors, timestamps
            
        Returns:
            Analysis result with all detected patterns
        """
        all_patterns = []
        
        if "events" in data:
            all_patterns.extend(self.detect_sequence_patterns(data["events"]))
        
        if "values" in data:
            all_patterns.extend(self.detect_frequency_patterns(data["values"]))
        
        if "errors" in data:
            all_patterns.extend(self.detect_error_patterns(data["errors"]))
        
        if "timestamps" in data:
            all_patterns.extend(self.detect_time_patterns(data["timestamps"]))
        
        # Cache patterns
        for p in all_patterns:
            self.pattern_cache[p.signature] = p
        
        return {
            "total_patterns": len(all_patterns),
            "patterns": [p.to_dict() for p in all_patterns],
            "timestamp": datetime.now().isoformat()
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pattern Engine")
    parser.add_argument("--demo", action="store_true", help="Run demo analysis")
    
    args = parser.parse_args()
    engine = PatternEngine()
    
    if args.demo:
        # Demo with sample data
        result = engine.analyze_all({
            "events": [
                {"type": "start"}, {"type": "work"}, {"type": "complete"},
                {"type": "start"}, {"type": "work"}, {"type": "complete"},
                {"type": "start"}, {"type": "error"}, {"type": "retry"}, {"type": "complete"}
            ],
            "values": ["A", "B", "A", "C", "A", "B", "A"],
            "errors": [
                "ConnectionError: timeout",
                "ConnectionError: refused", 
                "ValueError: invalid",
                "ConnectionError: reset"
            ]
        })
        print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

