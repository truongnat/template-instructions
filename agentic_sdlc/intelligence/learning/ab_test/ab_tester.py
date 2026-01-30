"""
A/B Tester - Decision comparison and selection engine.

Part of Layer 2: Intelligence Layer.
Migrated and enhanced from tools/brain/ab_tester.py
"""

import json
import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """Test status states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OptionResult(Enum):
    """Option result types."""
    WINNER = "winner"
    LOSER = "loser"
    TIE = "tie"
    PENDING = "pending"


@dataclass
class TestOption:
    """Represents a test option (A or B)."""
    id: str
    name: str
    description: str
    value: Any
    score: float = 0.0
    votes: int = 0
    metadata: Dict = field(default_factory=dict)
    
    # New fields for enrichment
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "score": self.score,
            "votes": self.votes,
            "metadata": self.metadata,
            "pros": self.pros,
            "cons": self.cons,
            "risks": self.risks
        }


@dataclass
class ABTest:
    """Represents an A/B test."""
    id: str
    title: str
    description: str
    option_a: TestOption
    option_b: TestOption
    status: TestStatus = TestStatus.PENDING
    winner: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    criteria: Dict = field(default_factory=dict)
    
    # New fields for research context
    kb_insights: List[str] = field(default_factory=list)
    memgraph_related_nodes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "option_a": self.option_a.to_dict(),
            "option_b": self.option_b.to_dict(),
            "status": self.status.value,
            "winner": self.winner,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "criteria": self.criteria,
            "kb_insights": self.kb_insights,
            "memgraph_related_nodes": self.memgraph_related_nodes
        }


class ABTester:
    """
    A/B Testing engine for comparing options and making decisions.
    
    Features:
    - Create comparison tests between two options
    - Score and evaluate options
    - Track test history
    - Make data-driven selections
    - Integrate with KB and Memgraph for context (Simulated/Placeholder)
    """

    def __init__(self, storage_file: Optional[Path] = None):
        if storage_file is None:
            brain_dir = Path(".brain")
            brain_dir.mkdir(parents=True, exist_ok=True)
            self.storage_file = brain_dir / "ab-tests.json"
        else:
            self.storage_file = storage_file
        self.tests: Dict[str, ABTest] = {}
        self._load_tests()

    def _load_tests(self):
        """Load tests from storage."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for test_data in data.get("tests", []):
                        test = self._dict_to_test(test_data)
                        self.tests[test.id] = test
            except (json.JSONDecodeError, IOError):
                self.tests = {}

    def _save_tests(self):
        """Save tests to storage."""
        data = {
            "tests": [t.to_dict() for t in self.tests.values()],
            "updated_at": datetime.now().isoformat()
        }
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _dict_to_test(self, data: dict) -> ABTest:
        """Convert dict to ABTest."""
        option_a = TestOption(**data["option_a"])
        option_b = TestOption(**data["option_b"])
        return ABTest(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            option_a=option_a,
            option_b=option_b,
            status=TestStatus(data.get("status", "pending")),
            winner=data.get("winner"),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
            criteria=data.get("criteria", {}),
            kb_insights=data.get("kb_insights", []),
            memgraph_related_nodes=data.get("memgraph_related_nodes", data.get("neo4j_related_nodes", []))
        )

    def _enrich_with_kb(self, test: ABTest):
        """
        Search Knowledge Base for insights related to the test (Placeholder).
        In a real implementation, this would call the KB search API.
        """
        # TODO: Implement actual KB search logic
        # Example: search_results = kb_client.search(f"{test.title} {test.description}")
        logger.info(f"Searching KB for insights on: {test.title}")
        test.kb_insights.append(f"Simulated insight[KB]: Best practices for '{test.title}' suggest considering scalability.")

    def _enrich_with_memgraph(self, test: ABTest):
        """
        Query Memgraph for related technologies/nodes (Placeholder).
        In a real implementation, this would call the Memgraph client.
        """
        # TODO: Implement actual Memgraph query logic
        logger.info(f"Querying Memgraph for nodes related to: {test.title}")
        test.memgraph_related_nodes.append("Simulated node[Memgraph]: HighCorrelationWith(Performance)")

    def create_test(
        self,
        title: str,
        description: str,
        option_a_name: str,
        option_a_value: Any,
        option_b_name: str,
        option_b_value: Any,
        criteria: Optional[Dict] = None,
        auto_enrich: bool = True
    ) -> ABTest:
        """
        Create a new A/B test.
        
        Args:
            title: Test title
            description: What is being tested
            option_a_name: Name for option A
            option_a_value: Value/content of option A
            option_b_name: Name for option B
            option_b_value: Value/content of option B
            criteria: Optional evaluation criteria
            auto_enrich: Whether to automatically research from KB/Memgraph
            
        Returns:
            Created ABTest
        """
        test_id = f"TEST-{uuid.uuid4().hex[:8].upper()}"
        
        option_a = TestOption(
            id="A",
            name=option_a_name,
            description=f"Option A: {option_a_name}",
            value=option_a_value
        )
        
        option_b = TestOption(
            id="B",
            name=option_b_name,
            description=f"Option B: {option_b_name}",
            value=option_b_value
        )
        
        test = ABTest(
            id=test_id,
            title=title,
            description=description,
            option_a=option_a,
            option_b=option_b,
            status=TestStatus.RUNNING,
            criteria=criteria or {}
        )

        if auto_enrich:
            self._enrich_with_kb(test)
            self._enrich_with_memgraph(test)
        
        self.tests[test_id] = test
        self._save_tests()
        
        return test

    def score_option(self, test_id: str, option: str, score: float, reason: str = ""):
        """
        Score an option in a test.
        
        Args:
            test_id: Test ID
            option: "A" or "B"
            score: Score to add (0-10)
            reason: Reason for score
        """
        if test_id not in self.tests:
            raise ValueError(f"Test not found: {test_id}")
        
        test = self.tests[test_id]
        
        if option.upper() == "A":
            test.option_a.score += score
            test.option_a.votes += 1
            test.option_a.metadata.setdefault("reasons", []).append(reason)
        elif option.upper() == "B":
            test.option_b.score += score
            test.option_b.votes += 1
            test.option_b.metadata.setdefault("reasons", []).append(reason)
        else:
            raise ValueError(f"Invalid option: {option}")
        
        self._save_tests()

    def compare(self, test_id: str) -> Dict:
        """
        Compare options and get results.
        
        Returns comparison with scores and recommendation.
        """
        if test_id not in self.tests:
            raise ValueError(f"Test not found: {test_id}")
        
        test = self.tests[test_id]
        
        # Calculate average scores
        avg_a = test.option_a.score / max(test.option_a.votes, 1)
        avg_b = test.option_b.score / max(test.option_b.votes, 1)
        
        # Determine recommendation
        if avg_a > avg_b:
            recommendation = "A"
            confidence = min((avg_a - avg_b) / 2, 1.0)
        elif avg_b > avg_a:
            recommendation = "B"
            confidence = min((avg_b - avg_a) / 2, 1.0)
        else:
            recommendation = "TIE"
            confidence = 0.5
        
        return {
            "test_id": test_id,
            "title": test.title,
            "option_a": {
                "name": test.option_a.name,
                "total_score": test.option_a.score,
                "votes": test.option_a.votes,
                "average": round(avg_a, 2),
                "pros": test.option_a.pros,
                "cons": test.option_a.cons
            },
            "option_b": {
                "name": test.option_b.name,
                "total_score": test.option_b.score,
                "votes": test.option_b.votes,
                "average": round(avg_b, 2),
                "pros": test.option_b.pros,
                "cons": test.option_b.cons
            },
            "recommendation": recommendation,
            "confidence": round(confidence, 2),
            "status": test.status.value,
            "kb_insights": test.kb_insights,
            "memgraph_related": test.memgraph_related_nodes
        }

    def select_winner(self, test_id: str, winner: str) -> ABTest:
        """
        Select a winner and complete the test.
        
        Args:
            test_id: Test ID  
            winner: "A" or "B"
            
        Returns:
            Updated test
        """
        if test_id not in self.tests:
            raise ValueError(f"Test not found: {test_id}")
        
        test = self.tests[test_id]
        test.winner = winner.upper()
        test.status = TestStatus.COMPLETED
        test.completed_at = datetime.now().isoformat()
        
        self._save_tests()
        return test

    def get_test(self, test_id: str) -> Optional[ABTest]:
        """Get a test by ID."""
        return self.tests.get(test_id)

    def list_tests(self, status: Optional[TestStatus] = None) -> List[ABTest]:
        """List tests, optionally filtered by status."""
        tests = list(self.tests.values())
        if status:
            tests = [t for t in tests if t.status == status]
        return sorted(tests, key=lambda t: t.created_at, reverse=True)

    def cancel_test(self, test_id: str):
        """Cancel a test."""
        if test_id in self.tests:
            self.tests[test_id].status = TestStatus.CANCELLED
            self._save_tests()


class OptionComparator:
    """
    Compares multiple options and recommends the best one.
    
    Used for quick comparisons without full A/B testing.
    """

    def __init__(self):
        self.comparison_history: List[Dict] = []

    def compare_options(
        self,
        options: List[Dict[str, Any]],
        criteria: Optional[List[str]] = None
    ) -> Dict:
        """
        Compare multiple options and recommend the best.
        
        Args:
            options: List of options with "name", "value", and optional scores
            criteria: Criteria to evaluate against
            
        Returns:
            Comparison result with recommendation
        """
        if not options:
            return {"error": "No options provided"}
        
        if len(options) == 1:
            return {
                "recommendation": options[0]["name"],
                "confidence": 1.0,
                "reason": "Only one option provided"
            }
        
        # Score each option
        scored_options = []
        for opt in options:
            score = opt.get("score", 5)  # Default score
            scored_options.append({
                "name": opt["name"],
                "value": opt.get("value"),
                "score": score
            })
        
        # Sort by score
        scored_options.sort(key=lambda x: x["score"], reverse=True)
        
        best = scored_options[0]
        second = scored_options[1] if len(scored_options) > 1 else None
        
        # Calculate confidence
        if second:
            diff = best["score"] - second["score"]
            confidence = min(0.5 + (diff / 10), 1.0)
        else:
            confidence = 1.0
        
        result = {
            "recommendation": best["name"],
            "confidence": round(confidence, 2),
            "ranked_options": scored_options,
            "criteria_used": criteria or []
        }
        
        self.comparison_history.append(result)
        return result


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="A/B Tester - Layer 2 Intelligence")
    parser = argparse.ArgumentParser(description="A/B Tester - Layer 2 Intelligence")
    parser.add_argument("--create", type=str, help="Create new test with description")
    parser.add_argument("--prompt", type=str, help="Alias for --create")
    parser.add_argument("--compare", action="store_true", help="Compare test options")
    parser.add_argument("--score", nargs=3, metavar=("TEST_ID", "OPTION", "SCORE"), help="Score an option (ID, A/B, 0-10)")
    parser.add_argument("--select", type=str, choices=["A", "B"], help="Select winner")
    parser.add_argument("--winner", type=str, choices=["A", "B"], help="Alias for --select")
    parser.add_argument("--test-id", type=str, help="Test ID for operations")
    parser.add_argument("--list", action="store_true", help="List all tests")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    tester = ABTester()
    
    test_description = args.create or args.prompt
    if test_description:
        test = tester.create_test(
            title=test_description,
            description=test_description,
            option_a_name="Option A",
            option_a_value="First approach",
            option_b_name="Option B",
            option_b_value="Second approach"
        )
        if args.json:
            print(json.dumps(test.to_dict(), indent=2))
        else:
            print(f"✅ Created test: {test.id}")
            print(f"   Title: {test.title}")
            print(f"   Insights: {len(test.kb_insights)}")
    
    elif args.score:
        test_id, option, score = args.score
        try:
            tester.score_option(test_id, option, float(score))
            print(f"✅ Scored Option {option} for test {test_id}: {score}")
        except Exception as e:
            print(f"❌ Error scoring option: {e}")

    elif args.compare and args.test_id:
        result = tester.compare(args.test_id)
        print(json.dumps(result, indent=2))
    
    elif (args.select or args.winner) and args.test_id:
        winner = args.select or args.winner
        test = tester.select_winner(args.test_id, winner)
        print(f"✅ Winner selected: Option {winner}")
    
    elif args.list:
        tests = tester.list_tests()
        if args.json:
            print(json.dumps([t.to_dict() for t in tests], indent=2))
        else:
            for t in tests:
                print(f"[{t.status.value}] {t.id}: {t.title}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
