"""
Option Comparator - Quick comparison without full A/B testing.

Part of Layer 2: Intelligence Layer.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ComparisonResult:
    """Result of a comparison."""
    winner: str
    winner_value: Any
    confidence: float
    scores: Dict[str, float]
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "winner": self.winner,
            "winner_value": self.winner_value,
            "confidence": self.confidence,
            "scores": self.scores,
            "reason": self.reason,
            "timestamp": self.timestamp
        }


class OptionComparator:
    """
    Quick option comparison utility.
    
    For rapid decision-making without full A/B test setup.
    """

    # Comparison criteria weights
    DEFAULT_CRITERIA = {
        "complexity": 0.2,
        "maintainability": 0.25,
        "performance": 0.2,
        "readability": 0.2,
        "testability": 0.15
    }

    def __init__(self):
        self.history: List[ComparisonResult] = []

    def compare(
        self,
        options: Dict[str, Any],
        criteria: Optional[Dict[str, float]] = None,
        scores: Optional[Dict[str, Dict[str, float]]] = None
    ) -> ComparisonResult:
        """
        Compare options and determine best choice.
        
        Args:
            options: Dict of option_name -> option_value
            criteria: Optional criteria weights
            scores: Optional pre-computed scores per option per criterion
            
        Returns:
            ComparisonResult with winner and analysis
        """
        if not options:
            raise ValueError("No options provided")
        
        if len(options) == 1:
            name = list(options.keys())[0]
            return ComparisonResult(
                winner=name,
                winner_value=options[name],
                confidence=1.0,
                scores={name: 10.0},
                reason="Only one option available"
            )
        
        criteria = criteria or self.DEFAULT_CRITERIA
        
        # Calculate weighted scores
        final_scores = {}
        for opt_name, opt_value in options.items():
            if scores and opt_name in scores:
                opt_scores = scores[opt_name]
                weighted_score = sum(
                    opt_scores.get(c, 5) * w 
                    for c, w in criteria.items()
                )
            else:
                # Default scoring based on value analysis
                weighted_score = self._auto_score(opt_value, criteria)
            
            final_scores[opt_name] = round(weighted_score, 2)
        
        # Find winner
        sorted_options = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        winner_name = sorted_options[0][0]
        winner_score = sorted_options[0][1]
        
        # Calculate confidence
        if len(sorted_options) > 1:
            second_score = sorted_options[1][1]
            diff = winner_score - second_score
            confidence = min(0.5 + (diff / 5), 1.0)
        else:
            confidence = 1.0
        
        result = ComparisonResult(
            winner=winner_name,
            winner_value=options[winner_name],
            confidence=round(confidence, 2),
            scores=final_scores,
            reason=self._generate_reason(winner_name, sorted_options)
        )
        
        self.history.append(result)
        return result

    def _auto_score(self, value: Any, criteria: Dict[str, float]) -> float:
        """Automatically score a value based on heuristics."""
        base_score = 5.0
        
        if isinstance(value, str):
            # Shorter is often simpler
            length = len(value)
            if length < 100:
                base_score += 1
            elif length > 500:
                base_score -= 0.5
        
        elif isinstance(value, dict):
            # Check structure
            if "description" in value:
                base_score += 0.5
            if "example" in value:
                base_score += 0.5
        
        return base_score

    def _generate_reason(self, winner: str, sorted_options: List) -> str:
        """Generate explanation for the decision."""
        if len(sorted_options) == 1:
            return f"{winner} is the only option"
        
        second = sorted_options[1]
        diff = sorted_options[0][1] - second[1]
        
        if diff > 2:
            return f"{winner} significantly outperforms alternatives"
        elif diff > 0.5:
            return f"{winner} has better overall score"
        else:
            return f"{winner} marginally better (close decision)"

    def quick_compare(self, option_a: Any, option_b: Any) -> str:
        """Quick comparison between two options, returns 'A' or 'B'."""
        result = self.compare({
            "A": option_a,
            "B": option_b
        })
        return result.winner

    def get_history(self) -> List[Dict]:
        """Get comparison history."""
        return [r.to_dict() for r in self.history[-50:]]


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Option Comparator")
    parser.add_argument("--compare", nargs=2, metavar=("A", "B"), help="Compare two options")
    parser.add_argument("--history", action="store_true", help="Show comparison history")
    
    args = parser.parse_args()
    comparator = OptionComparator()
    
    if args.compare:
        result = comparator.compare({
            "Option A": args.compare[0],
            "Option B": args.compare[1]
        })
        print(json.dumps(result.to_dict(), indent=2))
    
    elif args.history:
        print(json.dumps(comparator.get_history(), indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

