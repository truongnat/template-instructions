"""
Output Scorer - Evaluates quality of output/responses.

Part of Layer 2: Intelligence Layer.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class OutputQuality(Enum):
    """Output quality levels."""
    EXCELLENT = 5
    GOOD = 4
    ADEQUATE = 3
    POOR = 2
    INSUFFICIENT = 1


@dataclass
class OutputScore:
    """Result of output scoring."""
    text: str
    score: float
    quality: OutputQuality
    completeness: float
    correctness: float
    formatting: float
    usefulness: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    issues: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "text": self.text[:100] + "..." if len(self.text) > 100 else self.text,
            "score": self.score,
            "quality": self.quality.name,
            "completeness": self.completeness,
            "correctness": self.correctness,
            "formatting": self.formatting,
            "usefulness": self.usefulness,
            "timestamp": self.timestamp,
            "issues": self.issues
        }


class OutputScorer:
    """
    Evaluates the quality of output/responses.
    
    Scoring dimensions:
    - Completeness: Does the output address the request fully?
    - Correctness: Is the output accurate and error-free?
    - Formatting: Is the output well-formatted and readable?
    - Usefulness: Is the output directly usable?
    """

    def __init__(self, history_file: Optional[Path] = None):
        self.history_file = history_file or Path(".brain-output-scores.json")
        self.history: list[OutputScore] = []
        self._load_history()

    def _load_history(self):
        """Load scoring history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.history = data.get("scores", [])[-100:]
            except (json.JSONDecodeError, IOError):
                self.history = []

    def _save_history(self, score: OutputScore):
        """Save score to history file."""
        history_data = {"scores": self.history[-99:] + [score.to_dict()]}
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
        except IOError:
            pass

    def score(self, text: str, context: Optional[str] = None) -> OutputScore:
        """
        Score an output text for quality.
        
        Args:
            text: The output text to score
            context: Optional original request for context
            
        Returns:
            OutputScore with detailed scoring breakdown
        """
        if not text or not text.strip():
            return OutputScore(
                text=text,
                score=0.0,
                quality=OutputQuality.INSUFFICIENT,
                completeness=0.0,
                correctness=0.0,
                formatting=0.0,
                usefulness=0.0,
                issues=["Empty output"]
            )

        # Calculate individual dimensions
        completeness = self._score_completeness(text, context)
        correctness = self._score_correctness(text)
        formatting = self._score_formatting(text)
        usefulness = self._score_usefulness(text)

        # Weighted average score
        score = (
            completeness * 0.30 +
            correctness * 0.25 +
            formatting * 0.20 +
            usefulness * 0.25
        )

        # Determine quality level
        quality = self._determine_quality(score)

        # Identify issues
        issues = self._identify_issues(completeness, correctness, formatting, usefulness)

        result = OutputScore(
            text=text,
            score=round(score, 2),
            quality=quality,
            completeness=round(completeness, 2),
            correctness=round(correctness, 2),
            formatting=round(formatting, 2),
            usefulness=round(usefulness, 2),
            issues=issues
        )

        self._save_history(result)
        return result

    def _score_completeness(self, text: str, context: Optional[str]) -> float:
        """Score completeness (0-1)."""
        # Base score from length
        word_count = len(text.split())
        
        if word_count < 10:
            base = 0.1
        elif word_count < 50:
            base = 0.55
        elif word_count < 150:
            base = 0.75
        elif word_count < 300:
            base = 0.9
        else:
            base = 0.95

        # Check for conclusion/summary indicators
        conclusion_words = ["summary", "conclusion", "in summary", "therefore", "result"]
        has_conclusion = any(cw in text.lower() for cw in conclusion_words)
        if has_conclusion:
            base += 0.1

        return min(base, 1.0)

    def _score_correctness(self, text: str) -> float:
        """Score correctness (0-1)."""
        # Check for error indicators
        error_indicators = [
            "error", "failed", "exception", "undefined", "null",
            "traceback", "syntax error", "type error"
        ]
        
        text_lower = text.lower()
        error_count = sum(1 for ei in error_indicators if ei in text_lower)
        
        # Start high, penalize for errors
        base = 0.9
        base -= min(error_count * 0.15, 0.5)

        # Check for code blocks (usually indicates working examples)
        has_code = "```" in text or "    " in text
        if has_code and error_count == 0:
            base += 0.1

        return max(0.2, min(base, 1.0))

    def _score_formatting(self, text: str) -> float:
        """Score formatting (0-1)."""
        score = 0.5  # Base score

        # Check for markdown formatting
        if "```" in text:
            score += 0.15  # Code blocks
        if "#" in text:
            score += 0.1   # Headers
        if "- " in text or "* " in text:
            score += 0.1   # Lists
        if "|" in text:
            score += 0.1   # Tables

        # Check line breaks (proper structure)
        line_count = len(text.split('\n'))
        if line_count > 3:
            score += 0.1

        # Penalize walls of text
        if line_count == 1 and len(text) > 300:
            score -= 0.3

        return max(0.2, min(score, 1.0))

    def _score_usefulness(self, text: str) -> float:
        """Score usefulness (0-1)."""
        useful_indicators = [
            "example", "code", "step", "first", "then", "next",
            "solution", "fix", "resolved", "complete", "done"
        ]
        
        text_lower = text.lower()
        useful_count = sum(1 for ui in useful_indicators if ui in text_lower)
        
        base = 0.4
        base += min(useful_count * 0.08, 0.4)

        # Check for actionable content
        has_code = "```" in text
        has_commands = "$" in text or ">" in text
        
        if has_code:
            base += 0.15
        if has_commands:
            base += 0.1

        return min(base, 1.0)

    def _determine_quality(self, score: float) -> OutputQuality:
        """Map score to quality level."""
        if score >= 0.75:
            return OutputQuality.EXCELLENT
        elif score >= 0.60:
            return OutputQuality.GOOD
        elif score >= 0.45:
            return OutputQuality.ADEQUATE
        elif score >= 0.25:
            return OutputQuality.POOR
        else:
            return OutputQuality.INSUFFICIENT

    def _identify_issues(
        self,
        completeness: float,
        correctness: float,
        formatting: float,
        usefulness: float
    ) -> list[str]:
        """Identify quality issues."""
        issues = []
        
        if completeness < 0.5:
            issues.append("Output may be incomplete")
        if correctness < 0.5:
            issues.append("Output may contain errors")
        if formatting < 0.5:
            issues.append("Output formatting could be improved")
        if usefulness < 0.5:
            issues.append("Output may not be directly actionable")
            
        return issues


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Score output quality")
    parser.add_argument("--score", type=str, help="Text to score")
    parser.add_argument("--file", type=str, help="File containing text to score")
    
    args = parser.parse_args()
    
    scorer = OutputScorer()
    
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

