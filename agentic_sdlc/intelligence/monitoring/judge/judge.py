"""
Judge - Quality Scorer

Scores artifacts, code, and A/B test results for quality and compliance.
Part of Layer 2: Intelligence Layer.
Migrated and enhanced from tools/brain/judge.py
"""

import json
import re
import sys
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


from agentic_sdlc.core.utils.common import get_project_root


def get_scores_path() -> Path:
    """Get the scores database path."""
    brain_dir = get_project_root() / ".brain"
    brain_dir.mkdir(parents=True, exist_ok=True)
    return brain_dir / "scores.json"


@dataclass
class ScoreResult:
    """Score result for a file."""
    file: str
    file_type: str
    scores: Dict[str, float]
    final_score: float
    passed: bool
    threshold: float
    improvements: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "type": self.file_type,
            "scores": self.scores,
            "finalScore": self.final_score,
            "passed": self.passed,
            "threshold": self.threshold,
            "improvements": self.improvements,
            "timestamp": self.timestamp
        }


class Judge:
    """
    Scores reports, code, and A/B tests for quality and compliance.
    
    Features:
    - Score reports (completeness, quality, compliance)
    - Score code (structure, quality, completeness)
    - Score A/B test results (decision quality, confidence)
    - Track scores over time
    - Provide improvement suggestions
    """

    # Code extensions
    CODE_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.astro', '.vue', '.svelte', '.css', '.scss', '.rs', '.go', '.java'}
    
    # Report extensions
    REPORT_EXTENSIONS = {'.md', '.txt', '.rst'}

    # Scoring rubrics
    REPORT_RUBRIC = {
        "completeness": {"weight": 3},
        "quality": {"weight": 3},
        "compliance": {"weight": 4}
    }

    CODE_RUBRIC = {
        "structure": {"weight": 3},
        "quality": {"weight": 4},
        "completeness": {"weight": 3}
    }
    
    AB_TEST_RUBRIC = {
        "confidence": {"weight": 4},
        "impact": {"weight": 3},
        "documentation": {"weight": 3}
    }

    def __init__(self, scores_file: Optional[Path] = None):
        self.scores_file = scores_file or get_scores_path()
        self.scores_data = self._load_scores()

    def _load_scores(self) -> Dict:
        """Load scores database."""
        if self.scores_file.exists():
            try:
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {
            "scores": [],
            "averageScore": 0,
            "totalReviews": 0,
            "passThreshold": 6,
            "createdAt": datetime.now().isoformat()
        }

    def _save_scores(self):
        """Save scores database."""
        self.scores_file.parent.mkdir(parents=True, exist_ok=True)
        self.scores_data["lastUpdated"] = datetime.now().isoformat()
        
        if self.scores_data["scores"]:
            total = sum(s.get("finalScore", 0) for s in self.scores_data["scores"])
            self.scores_data["averageScore"] = round(total / len(self.scores_data["scores"]), 2)
            self.scores_data["totalReviews"] = len(self.scores_data["scores"])
        
        with open(self.scores_file, 'w', encoding='utf-8') as f:
            json.dump(self.scores_data, f, indent=2, ensure_ascii=False)

    def score(self, file_path: str) -> ScoreResult:
        """Score a file (auto-detect type)."""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext in self.CODE_EXTENSIONS:
            return self.score_code(file_path)
        else:
            return self.score_report(file_path)

    def score_code(self, file_path: str) -> ScoreResult:
        """Score a code file."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return ScoreResult(
                file=str(path),
                file_type="code",
                scores={},
                final_score=0,
                passed=False,
                threshold=self.scores_data.get("passThreshold", 6),
                improvements=["File not found"]
            )
        
        content = path.read_text(encoding='utf-8')
        scores = {}
        improvements = []
        
        # Score structure
        structure_score = 2
        import_pattern = r'^import |^from |^const |^let |^use |package '
        if re.search(import_pattern, content, re.M):
            structure_score += 2.5
        else:
            improvements.append("Add imports/package decl → +2.5 structure")
            
        if re.search(r'""".*"""|//.*$|/\*', content, re.M | re.S):
            structure_score += 2.5
        else:
            improvements.append("Add docstrings/comments → +2.5 structure")
            
        def_pattern = r'^(def |class |function |fn |pub fn |struct |interface )'
        if re.search(def_pattern, content, re.M):
            structure_score += 2
        else:
            improvements.append("Add functions/classes/structs → +2 structure")
        structure_score += 1
        scores["structure"] = min(structure_score, 10)
        
        # Score quality
        quality_score = 5
        if "TODO" not in content.upper() and "FIXME" not in content.upper():
            quality_score += 2
        else:
            improvements.append("Remove TODO/FIXME → +2 quality")
        
        # Simple security/config check
        if not re.search(r'(password\s*=|api_key\s*=)', content, re.I):
            quality_score += 2
        else:
            improvements.append("Remove hardcoded secrets → +2 quality")
            
        # Error handling check
        error_pattern = r'try:|except:|catch|\.catch\(|Result<|Option<|if err != nil'
        if re.search(error_pattern, content, re.I):
            quality_score += 1
        else:
            improvements.append("Add error handling → +1 quality")
        scores["quality"] = min(quality_score, 10)
        
        # Score completeness
        completeness_score = 5
        if "pass" not in content or content.count("pass") <= 2:
            completeness_score += 2
        else:
            improvements.append("Implement pass statements → +2 completeness")
            
        if re.search(def_pattern, content):
            completeness_score += 2
        else:
            improvements.append("Add logic implementation → +2 completeness")
            
        if "__main__" in content or "export" in content or "pub " in content:
            completeness_score += 1
        else:
            improvements.append("Expose module (export/main) → +1 completeness")
        scores["completeness"] = min(completeness_score, 10)
        
        # Calculate final
        final_score = self._calculate_weighted_score(scores, self.CODE_RUBRIC)
        threshold = self.scores_data.get("passThreshold", 6)
        
        result = ScoreResult(
            file=str(path),
            file_type="code",
            scores=scores,
            final_score=final_score,
            passed=final_score >= threshold,
            threshold=threshold,
            improvements=improvements if final_score < 10 else []
        )
        
        self.scores_data["scores"].append(result.to_dict())
        self._save_scores()
        
        return result

    def score_report(self, file_path: str) -> ScoreResult:
        """Score a report file."""
        path = Path(file_path)
        if not path.exists():
            return ScoreResult(
                file=str(path),
                file_type="report",
                scores={},
                final_score=0,
                passed=False,
                threshold=self.scores_data.get("passThreshold", 6),
                improvements=["File not found"]
            )
        
        content = path.read_text(encoding='utf-8')
        scores = {}
        improvements = []
        
        # Score completeness
        completeness_score = 0
        if re.search(r'##.*problem|##.*challenge|##.*goal', content, re.I):
            completeness_score += 2.5
        else:
            improvements.append("Add Problem/Goal section → +2.5")
            
        if re.search(r'##.*solution|##.*implementation|##.*approach', content, re.I):
            completeness_score += 2.5
        else:
            improvements.append("Add Solution/Approach section → +2.5")
            
        if re.search(r'##.*artifact|##.*output|##.*result', content, re.I):
            completeness_score += 2.5
        else:
            improvements.append("Add Artifacts/Results section → +2.5")
            
        if re.search(r'##.*next|##.*action|##.*conclusion', content, re.I):
            completeness_score += 2.5
        else:
            improvements.append("Add Next Steps/Conclusion section → +2.5")
        scores["completeness"] = min(completeness_score, 10)
        
        # Score quality
        quality_score = 5
        if len(content) > 500:
            quality_score += 2
        else:
            improvements.append("Add more content (>500 chars) → +2")
        if "```" in content:
            quality_score += 1.5
        else:
            improvements.append("Add code blocks/examples → +1.5")
        if "[TODO]" not in content and "[PLACEHOLDER]" not in content:
            quality_score += 1.5
        else:
            improvements.append("Remove placeholders → +1.5")
        scores["quality"] = min(quality_score, 10)
        
        # Score compliance
        compliance_score = 0
        if content.startswith("---") or content.strip().startswith("#"):
             compliance_score += 4 # Relaxed check, either fontmatter or H1 is good start
        else:
            improvements.append("Start with title (#) or YAML frontmatter → +4")
            
        if re.search(r'#[a-z-]+', content):
            compliance_score += 3
        else:
            improvements.append("Add hashtags/tags → +3")
            
        if re.search(r'\[.*\]\(.*\.md\)', content) or re.search(r'http', content):
            compliance_score += 3
        else:
            improvements.append("Add links/references → +3")
        scores["compliance"] = min(compliance_score, 10)
        
        # Calculate final
        final_score = self._calculate_weighted_score(scores, self.REPORT_RUBRIC)
        threshold = self.scores_data.get("passThreshold", 6)
        
        result = ScoreResult(
            file=str(path),
            file_type="report",
            scores=scores,
            final_score=final_score,
            passed=final_score >= threshold,
            threshold=threshold,
            improvements=improvements if final_score < 10 else []
        )
        
        self.scores_data["scores"].append(result.to_dict())
        self._save_scores()
        
        return result
        
    def score_ab_test(self, test_result: Dict) -> ScoreResult:
        """
        Score an A/B test result.
        
        Args:
            test_result: Dict containing AB test data (from ABTester.compare)
        """
        scores = {}
        improvements = []
        
        # Score confidence
        confidence = test_result.get("confidence", 0.0)
        confidence_score = confidence * 10
        if confidence < 0.5:
            improvements.append("Run test longer to increase confidence")
        scores["confidence"] = confidence_score
        
        # Score impact (Mock - based on vote count or margin)
        # Assuming higher vote count might imply higher impact/data validity
        opt_a = test_result.get("option_a", {})
        opt_b = test_result.get("option_b", {})
        total_votes = opt_a.get("votes", 0) + opt_b.get("votes", 0)
        
        impact_score = min(total_votes, 10) # 1 vote = 1 point, max 10 (simple heuristic)
        if total_votes < 5:
            improvements.append("Get more votes/data points")
        scores["impact"] = impact_score
        
        # Score documentation/clarity
        doc_score = 10 
        if not test_result.get("kb_insights"):
            doc_score -= 2
            improvements.append("Link KB insights")
        if not test_result.get("memgraph_related"):
            doc_score -= 2
            improvements.append("Link Memgraph nodes")
            
        scores["documentation"] = doc_score
        
        final_score = self._calculate_weighted_score(scores, self.AB_TEST_RUBRIC)
        threshold = self.scores_data.get("passThreshold", 6)
        
        # Create a dummy path for the record
        test_id = test_result.get("test_id", "unknown")
        
        result = ScoreResult(
            file=f"ab_test_{test_id}",
            file_type="ab_test",
            scores=scores,
            final_score=final_score,
            passed=final_score >= threshold,
            threshold=threshold,
            improvements=improvements
        )
        
        self.scores_data["scores"].append(result.to_dict())
        self._save_scores()
        
        return result


    def _calculate_weighted_score(self, scores: Dict[str, float], rubric: Dict) -> float:
        """Calculate weighted score."""
        total_weight = 0
        weighted_score = 0
        
        for category, details in rubric.items():
            if category in scores:
                weighted_score += scores[category] * details["weight"]
                total_weight += details["weight"] * 10
        
        if total_weight == 0:
            return 0
        
        return round((weighted_score / total_weight) * 10, 1)

    def set_threshold(self, value: int):
        """Set pass threshold."""
        self.scores_data["passThreshold"] = value
        self._save_scores()

    def get_stats(self) -> Dict:
        """Get scoring statistics."""
        return {
            "totalReviews": self.scores_data.get("totalReviews", 0),
            "averageScore": self.scores_data.get("averageScore", 0),
            "passThreshold": self.scores_data.get("passThreshold", 6),
            "lastUpdated": self.scores_data.get("lastUpdated")
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Judge - Layer 2 Intelligence")
    parser.add_argument("--score", type=str, help="Score a file")
    parser.add_argument("--threshold", type=int, help="Set pass threshold")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    judge = Judge()
    
    if args.score:
        result = judge.score(args.score)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(f"⚖️ Score: {result.final_score}/10")
            print(f"   Status: {'✅ PASSED' if result.passed else '❌ FAILED'}")
            for cat, score in result.scores.items():
                print(f"   {cat}: {score}/10")
            if result.improvements:
                print("\n💡 Improvements:")
                for imp in result.improvements[:5]:
                    print(f"   • {imp}")
    
    elif args.threshold:
        judge.set_threshold(args.threshold)
        print(f"✅ Threshold set to {args.threshold}")
    
    elif args.stats:
        stats = judge.get_stats()
        print(json.dumps(stats, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
