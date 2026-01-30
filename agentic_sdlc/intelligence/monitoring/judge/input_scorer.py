"""
Input Scorer - Evaluates quality of input requests/prompts.

Part of Layer 2: Intelligence Layer.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class InputQuality(Enum):
    """Input quality levels."""
    EXCELLENT = 5
    GOOD = 4
    ADEQUATE = 3
    POOR = 2
    INSUFFICIENT = 1


@dataclass
class InputScore:
    """Result of input scoring."""
    text: str
    score: float
    quality: InputQuality
    completeness: float
    clarity: float
    specificity: float
    actionability: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    recommendations: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "text": self.text[:100] + "..." if len(self.text) > 100 else self.text,
            "score": self.score,
            "quality": self.quality.name,
            "completeness": self.completeness,
            "clarity": self.clarity,
            "specificity": self.specificity,
            "actionability": self.actionability,
            "timestamp": self.timestamp,
            "recommendations": self.recommendations
        }


class InputScorer:
    """
    Evaluates the quality of input requests and prompts.
    
    Scoring dimensions:
    - Completeness: Does the input have all necessary information?
    - Clarity: Is the input clear and unambiguous?
    - Specificity: Is the input specific enough to act on?
    - Actionability: Can the input be directly acted upon?
    """

    # Keywords that suggest completeness
    COMPLETENESS_KEYWORDS = [
        "requirements", "expected", "should", "must", "output",
        "input", "result", "goal", "objective", "criteria"
    ]

    # Keywords that suggest specificity
    SPECIFICITY_KEYWORDS = [
        "specific", "exactly", "precisely", "particular",
        "detail", "step", "process", "method", "approach"
    ]

    def __init__(self, history_file: Optional[Path] = None):
        self.history_file = history_file or Path(".brain-input-scores.json")
        self.history: list[InputScore] = []
        self._load_history()

    def _load_history(self):
        """Load scoring history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    # Keep only last 100 entries
                    self.history = data.get("scores", [])[-100:]
            except (json.JSONDecodeError, IOError):
                self.history = []

    def _save_history(self, score: InputScore):
        """Save score to history file."""
        history_data = {"scores": self.history[-99:] + [score.to_dict()]}
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
        except IOError:
            pass  # Silent fail for history saving

    def score(self, text: str) -> InputScore:
        """
        Score an input text for quality.
        
        Args:
            text: The input text to score
            
        Returns:
            InputScore with detailed scoring breakdown
        """
        if not text or not text.strip():
            return InputScore(
                text=text,
                score=0.0,
                quality=InputQuality.INSUFFICIENT,
                completeness=0.0,
                clarity=0.0,
                specificity=0.0,
                actionability=0.0,
                recommendations=["Provide a non-empty input"]
            )

        # Calculate individual dimensions
        completeness = self._score_completeness(text)
        clarity = self._score_clarity(text)
        specificity = self._score_specificity(text)
        actionability = self._score_actionability(text)

        # Weighted average score
        score = (
            completeness * 0.25 +
            clarity * 0.30 +
            specificity * 0.25 +
            actionability * 0.20
        )

        # Determine quality level
        quality = self._determine_quality(score)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            completeness, clarity, specificity, actionability
        )

        result = InputScore(
            text=text,
            score=round(score, 2),
            quality=quality,
            completeness=round(completeness, 2),
            clarity=round(clarity, 2),
            specificity=round(specificity, 2),
            actionability=round(actionability, 2),
            recommendations=recommendations
        )

        self._save_history(result)
        return result

    def _score_completeness(self, text: str) -> float:
        """Score completeness (0-1) based on information density."""
        words = text.lower().split()
        word_count = len(words)
        
        # Base score from length
        if word_count < 5:
            base = 0.2
        elif word_count < 15:
            base = 0.5
        elif word_count < 30:
            base = 0.7
        elif word_count < 60:
            base = 0.85
        else:
            base = 0.95

        # Bonus for completeness keywords
        keyword_count = sum(1 for kw in self.COMPLETENESS_KEYWORDS if kw in text.lower())
        bonus = min(keyword_count * 0.08, 0.25)

        return min(base + bonus, 1.0)

    def _score_clarity(self, text: str) -> float:
        """Score clarity (0-1) based on readability."""
        words = text.split()
        
        if not words:
            return 0.0

        # Average word length (shorter is generally clearer)
        avg_word_len = sum(len(w) for w in words) / len(words)
        
        if avg_word_len < 5:
            length_score = 1.0
        elif avg_word_len < 7:
            length_score = 0.8
        elif avg_word_len < 9:
            length_score = 0.6
        else:
            length_score = 0.4

        # Sentence structure (presence of punctuation)
        has_structure = any(c in text for c in '.?!:;')
        structure_score = 0.8 if has_structure else 0.5

        # Penalize excessive use of unclear words
        unclear_words = ["maybe", "perhaps", "somehow", "something", "stuff", "things"]
        unclear_count = sum(1 for uw in unclear_words if uw in text.lower())
        clarity_penalty = min(unclear_count * 0.1, 0.3)

        return max(0, (length_score * 0.4 + structure_score * 0.6) - clarity_penalty)

    def _score_specificity(self, text: str) -> float:
        """Score specificity (0-1) based on detail level."""
        # Check for specific keywords
        keyword_count = sum(1 for kw in self.SPECIFICITY_KEYWORDS if kw in text.lower())
        
        # Check for numbers (usually indicates specificity)
        has_numbers = any(c.isdigit() for c in text)
        
        # Check for technical terms or file paths
        has_technical = any(c in text for c in ['/', '\\', '.py', '.js', '.md'])
        
        base = 0.4
        base += min(keyword_count * 0.15, 0.4)
        base += 0.2 if has_numbers else 0
        base += 0.2 if has_technical else 0
        
        # Length bonus
        if len(text) > 100:
            base += 0.1

        return min(base, 1.0)

    def _score_actionability(self, text: str) -> float:
        """Score actionability (0-1) based on action orientation."""
        action_words = [
            "create", "build", "implement", "add", "remove", "update",
            "fix", "change", "modify", "delete", "refactor", "optimize",
            "test", "deploy", "configure", "setup", "install"
        ]
        
        question_words = ["how", "what", "why", "when", "where", "who"]
        
        text_lower = text.lower()
        
        # Count action words
        action_count = sum(1 for aw in action_words if aw in text_lower)
        
        # Check if it's a question (less actionable directly)
        is_question = any(text.strip().endswith(c) for c in ['?']) or \
                      any(text_lower.startswith(qw) for qw in question_words)
        
        base = 0.4
        base += min(action_count * 0.2, 0.6)
        
        if is_question:
            base = min(base, 0.6)  # Cap question actionability
        
        return min(base, 1.0)

    def _determine_quality(self, score: float) -> InputQuality:
        """Map score to quality level."""
        if score >= 0.80:
            return InputQuality.EXCELLENT
        elif score >= 0.65:
            return InputQuality.GOOD
        elif score >= 0.45:
            return InputQuality.ADEQUATE
        elif score >= 0.25:
            return InputQuality.POOR
        else:
            return InputQuality.INSUFFICIENT

    def _generate_recommendations(
        self, 
        completeness: float, 
        clarity: float, 
        specificity: float,
        actionability: float
    ) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if completeness < 0.5:
            recommendations.append("Add more context and requirements")
        if clarity < 0.5:
            recommendations.append("Use clearer, more concise language")
        if specificity < 0.5:
            recommendations.append("Be more specific about what you need")
        if actionability < 0.5:
            recommendations.append("Include actionable verbs (create, update, fix)")
            
        return recommendations


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Score input quality")
    parser.add_argument("--score", type=str, help="Text to score")
    parser.add_argument("--file", type=str, help="File containing text to score")
    
    args = parser.parse_args()
    
    scorer = InputScorer()
    
    if args.score:
        result = scorer.score(args.score)
        print(json.dumps(result.to_dict(), indent=2))
    elif args.file:
        with open(args.file, 'r') as f:
            text = f.read()
        result = scorer.score(text)
        print(json.dumps(result.to_dict(), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

