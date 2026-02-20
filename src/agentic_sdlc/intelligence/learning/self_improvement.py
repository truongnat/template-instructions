"""Self-Improvement Engine - Autonomous learning and improvement system.

Analyzes execution patterns, identifies areas for improvement, and
generates improvement proposals including new skills, refined prompts,
and self-reports.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ImprovementProposal:
    """A proposed improvement based on learned patterns.

    Attributes:
        id: Unique proposal identifier.
        type: Type of improvement (skill, prompt, workflow, config).
        title: Short title describing the improvement.
        description: Detailed description.
        rationale: Why this improvement is needed.
        priority: Priority score (0.0 - 1.0).
        status: Current status (proposed, applied, rejected, verified).
        metadata: Additional metadata.
        created_at: When the proposal was created.
    """

    id: str
    type: str  # "skill", "prompt", "workflow", "config"
    title: str
    description: str
    rationale: str
    priority: float = 0.5
    status: str = "proposed"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SelfReport:
    """A self-generated performance report.

    Attributes:
        period: Report period description.
        total_executions: Total task executions in period.
        success_rate: Overall success rate.
        top_patterns: Most frequent patterns.
        improvements: Applied improvements.
        proposals: Pending improvement proposals.
        metrics: Key performance metrics.
        generated_at: When the report was generated.
    """

    period: str
    total_executions: int = 0
    success_rate: float = 0.0
    top_patterns: List[Dict[str, Any]] = field(default_factory=list)
    improvements: List[Dict[str, Any]] = field(default_factory=list)
    proposals: List[ImprovementProposal] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class SelfImprovementEngine:
    """Autonomous self-improvement engine.

    Analyzes execution history, identifies patterns (both positive
    and negative), and generates actionable improvement proposals.

    Improvement cycle:
    1. Collect execution data (success/failure/scores)
    2. Analyze patterns (frequent errors, successful approaches)
    3. Generate improvement proposals
    4. Apply improvements (new skills, refined prompts)
    5. Verify improvements via A/B testing
    6. Generate self-reports

    Example:
        >>> engine = SelfImprovementEngine(
        ...     data_dir=Path(".agentic_sdlc/learning")
        ... )
        >>> proposals = engine.analyze_and_propose()
        >>> report = engine.generate_report()
    """

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        min_samples: int = 5,
    ):
        """Initialize the self-improvement engine.

        Args:
            data_dir: Directory for persisting learning data.
            min_samples: Minimum samples before generating proposals.
        """
        self._data_dir = data_dir
        self._min_samples = min_samples
        self._execution_log: List[Dict[str, Any]] = []
        self._proposals: List[ImprovementProposal] = []
        self._reports: List[SelfReport] = []

        if data_dir:
            data_dir.mkdir(parents=True, exist_ok=True)
            self._load_data()

    def record_execution(
        self,
        task: str,
        success: bool,
        score: float = 0.0,
        domain: str = "",
        strategy: str = "",
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a task execution for analysis.

        Args:
            task: Task description.
            success: Whether the execution succeeded.
            score: Quality score (0.0 - 1.0).
            domain: Domain of the task.
            strategy: Strategy/approach used.
            error: Error message if failed.
            metadata: Additional metadata.
        """
        entry = {
            "task": task[:200],
            "success": success,
            "score": score,
            "domain": domain,
            "strategy": strategy,
            "error": error,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }
        self._execution_log.append(entry)
        self._save_data()

    def analyze_and_propose(self) -> List[ImprovementProposal]:
        """Analyze execution history and generate improvement proposals.

        Returns:
            List of new improvement proposals.
        """
        if len(self._execution_log) < self._min_samples:
            logger.info(
                f"Not enough data for analysis ({len(self._execution_log)}/{self._min_samples})"
            )
            return []

        new_proposals = []

        # Analyze failure patterns
        failure_proposals = self._analyze_failures()
        new_proposals.extend(failure_proposals)

        # Analyze success patterns
        success_proposals = self._analyze_successes()
        new_proposals.extend(success_proposals)

        # Analyze domain gaps
        domain_proposals = self._analyze_domain_gaps()
        new_proposals.extend(domain_proposals)

        # Add to proposals list
        self._proposals.extend(new_proposals)
        self._save_data()

        logger.info(f"Generated {len(new_proposals)} improvement proposals")
        return new_proposals

    def generate_report(self, period: str = "all") -> SelfReport:
        """Generate a self-improvement report.

        Args:
            period: Report period ("all", "last_7d", "last_30d").

        Returns:
            SelfReport with analysis and recommendations.
        """
        executions = self._execution_log
        total = len(executions)
        successes = sum(1 for e in executions if e.get("success"))
        success_rate = successes / total if total > 0 else 0.0

        # Top patterns
        patterns = self._extract_top_patterns(executions)

        # Metrics
        scores = [e.get("score", 0) for e in executions if e.get("score", 0) > 0]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        domains = {}
        for e in executions:
            d = e.get("domain", "unknown")
            if d not in domains:
                domains[d] = {"total": 0, "success": 0}
            domains[d]["total"] += 1
            if e.get("success"):
                domains[d]["success"] += 1

        report = SelfReport(
            period=period,
            total_executions=total,
            success_rate=success_rate,
            top_patterns=patterns,
            improvements=[
                {"id": p.id, "title": p.title, "status": p.status}
                for p in self._proposals
                if p.status == "applied"
            ],
            proposals=[p for p in self._proposals if p.status == "proposed"],
            metrics={
                "avg_score": round(avg_score, 3),
                "total_proposals": len(self._proposals),
                "applied_proposals": sum(
                    1 for p in self._proposals if p.status == "applied"
                ),
                "domain_stats": {
                    d: {
                        "success_rate": round(
                            s["success"] / s["total"] if s["total"] > 0 else 0, 3
                        )
                    }
                    for d, s in domains.items()
                },
            },
        )

        self._reports.append(report)
        self._save_report(report)

        logger.info(
            f"Generated self-report: {total} executions, "
            f"{success_rate:.1%} success rate"
        )
        return report

    def generate_report_markdown(self, period: str = "all") -> str:
        """Generate a markdown-formatted self-improvement report.

        Args:
            period: Report period.

        Returns:
            Markdown string.
        """
        report = self.generate_report(period)
        lines = [
            f"# Self-Improvement Report",
            f"**Generated**: {report.generated_at}",
            f"**Period**: {report.period}",
            "",
            "## Summary",
            f"- **Total Executions**: {report.total_executions}",
            f"- **Success Rate**: {report.success_rate:.1%}",
            f"- **Average Score**: {report.metrics.get('avg_score', 0):.3f}",
            "",
        ]

        # Domain stats
        domain_stats = report.metrics.get("domain_stats", {})
        if domain_stats:
            lines.append("## Domain Performance")
            lines.append("| Domain | Success Rate |")
            lines.append("|--------|-------------|")
            for domain, stats in domain_stats.items():
                lines.append(
                    f"| {domain} | {stats.get('success_rate', 0):.1%} |"
                )
            lines.append("")

        # Top patterns
        if report.top_patterns:
            lines.append("## Top Patterns")
            for i, pattern in enumerate(report.top_patterns[:5]):
                lines.append(
                    f"{i+1}. **{pattern.get('type', 'unknown')}**: "
                    f"{pattern.get('description', '')} "
                    f"(frequency: {pattern.get('frequency', 0)})"
                )
            lines.append("")

        # Proposals
        if report.proposals:
            lines.append("## Improvement Proposals")
            for proposal in report.proposals:
                lines.append(
                    f"- [{proposal.type.upper()}] **{proposal.title}** "
                    f"(priority: {proposal.priority:.1f})\n"
                    f"  {proposal.description}"
                )
            lines.append("")

        return "\n".join(lines)

    def get_proposals(
        self, status: Optional[str] = None
    ) -> List[ImprovementProposal]:
        """Get improvement proposals.

        Args:
            status: Optional status filter.

        Returns:
            List of proposals.
        """
        if status:
            return [p for p in self._proposals if p.status == status]
        return self._proposals.copy()

    def apply_proposal(self, proposal_id: str) -> bool:
        """Mark a proposal as applied.

        Args:
            proposal_id: ID of the proposal.

        Returns:
            True if found and updated.
        """
        for p in self._proposals:
            if p.id == proposal_id:
                p.status = "applied"
                self._save_data()
                return True
        return False

    def _analyze_failures(self) -> List[ImprovementProposal]:
        """Analyze failure patterns and generate proposals."""
        failures = [e for e in self._execution_log if not e.get("success")]
        if not failures:
            return []

        proposals = []

        # Group failures by domain
        domain_failures: Dict[str, List] = {}
        for f in failures:
            domain = f.get("domain", "unknown")
            domain_failures.setdefault(domain, []).append(f)

        for domain, fails in domain_failures.items():
            if len(fails) >= 2:
                # Look for common error patterns
                errors = [f.get("error", "") for f in fails if f.get("error")]
                common_errors = self._find_common_terms(errors)

                if common_errors:
                    proposal = ImprovementProposal(
                        id=f"fix_{domain}_{datetime.now().strftime('%Y%m%d%H%M')}",
                        type="skill",
                        title=f"Fix recurring failures in {domain}",
                        description=(
                            f"Domain '{domain}' has {len(fails)} failures. "
                            f"Common error terms: {', '.join(common_errors[:5])}. "
                            "Consider creating defensive skills or improved prompts."
                        ),
                        rationale=f"{len(fails)} failures detected in {domain} domain",
                        priority=min(len(fails) / 10, 1.0),
                    )
                    proposals.append(proposal)

        return proposals

    def _analyze_successes(self) -> List[ImprovementProposal]:
        """Analyze success patterns and propose reusable skills."""
        successes = [
            e for e in self._execution_log
            if e.get("success") and e.get("score", 0) >= 0.8
        ]
        if len(successes) < 3:
            return []

        proposals = []

        # Group by strategy
        strategy_scores: Dict[str, List[float]] = {}
        for s in successes:
            strategy = s.get("strategy", "unknown")
            strategy_scores.setdefault(strategy, []).append(s.get("score", 0))

        for strategy, scores in strategy_scores.items():
            if len(scores) >= 3:
                avg = sum(scores) / len(scores)
                if avg >= 0.85:
                    proposal = ImprovementProposal(
                        id=f"reuse_{strategy}_{datetime.now().strftime('%Y%m%d%H%M')}",
                        type="prompt",
                        title=f"Promote strategy '{strategy}' as default",
                        description=(
                            f"Strategy '{strategy}' has consistently high scores "
                            f"(avg: {avg:.2f}, {len(scores)} successes). "
                            "Consider making this the default strategy for similar tasks."
                        ),
                        rationale=f"High avg score {avg:.2f} with {len(scores)} samples",
                        priority=avg,
                    )
                    proposals.append(proposal)

        return proposals

    def _analyze_domain_gaps(self) -> List[ImprovementProposal]:
        """Identify domains with insufficient coverage."""
        domain_counts: Dict[str, int] = {}
        for e in self._execution_log:
            d = e.get("domain", "unknown")
            domain_counts[d] = domain_counts.get(d, 0) + 1

        proposals = []
        for domain, count in domain_counts.items():
            if count <= 2 and domain != "unknown":
                proposal = ImprovementProposal(
                    id=f"gap_{domain}_{datetime.now().strftime('%Y%m%d%H%M')}",
                    type="skill",
                    title=f"Expand coverage for '{domain}' domain",
                    description=(
                        f"Domain '{domain}' has only {count} recorded executions. "
                        "Consider creating more skills and workflows for this domain."
                    ),
                    rationale=f"Low coverage: {count} executions",
                    priority=0.3,
                )
                proposals.append(proposal)

        return proposals

    def _extract_top_patterns(
        self, executions: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Extract top patterns from execution history."""
        patterns = []

        # Pattern: most common domains
        domains: Dict[str, int] = {}
        for e in executions:
            d = e.get("domain", "unknown")
            domains[d] = domains.get(d, 0) + 1

        for domain, freq in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:3]:
            patterns.append({
                "type": "domain_usage",
                "description": f"Domain '{domain}' is most frequently used",
                "frequency": freq,
            })

        # Pattern: most common strategies
        strategies: Dict[str, int] = {}
        for e in executions:
            s = e.get("strategy", "unknown")
            if s:
                strategies[s] = strategies.get(s, 0) + 1

        for strategy, freq in sorted(strategies.items(), key=lambda x: x[1], reverse=True)[:3]:
            patterns.append({
                "type": "strategy_usage",
                "description": f"Strategy '{strategy}' is frequently used",
                "frequency": freq,
            })

        return patterns

    def _find_common_terms(self, texts: List[str]) -> List[str]:
        """Find common terms across a list of texts."""
        if not texts:
            return []

        from collections import Counter

        all_terms: List[str] = []
        for text in texts:
            words = text.lower().split()
            # Filter short/common words
            terms = [w for w in words if len(w) > 3]
            all_terms.extend(terms)

        counter = Counter(all_terms)
        return [term for term, _ in counter.most_common(10) if _ > 1]

    def _load_data(self) -> None:
        """Load persisted data."""
        if not self._data_dir:
            return

        log_file = self._data_dir / "execution_log.json"
        if log_file.exists():
            try:
                with open(log_file) as f:
                    self._execution_log = json.load(f)
            except Exception:
                pass

        proposals_file = self._data_dir / "proposals.json"
        if proposals_file.exists():
            try:
                with open(proposals_file) as f:
                    data = json.load(f)
                    self._proposals = [
                        ImprovementProposal(**p) for p in data
                    ]
            except Exception:
                pass

    def _save_data(self) -> None:
        """Persist data to disk."""
        if not self._data_dir:
            return

        try:
            log_file = self._data_dir / "execution_log.json"
            with open(log_file, "w") as f:
                json.dump(self._execution_log, f, indent=2)

            proposals_file = self._data_dir / "proposals.json"
            with open(proposals_file, "w") as f:
                json.dump(
                    [
                        {
                            "id": p.id, "type": p.type, "title": p.title,
                            "description": p.description, "rationale": p.rationale,
                            "priority": p.priority, "status": p.status,
                            "metadata": p.metadata, "created_at": p.created_at,
                        }
                        for p in self._proposals
                    ],
                    f,
                    indent=2,
                )
        except Exception as e:
            logger.error(f"Failed to save learning data: {e}")

    def _save_report(self, report: SelfReport) -> None:
        """Save report to disk as markdown."""
        if not self._data_dir:
            return

        reports_dir = self._data_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"report_{timestamp}.md"

        try:
            md = self.generate_report_markdown.__wrapped__(self, report.period) if hasattr(self.generate_report_markdown, '__wrapped__') else ""
            # Just save the raw data as JSON since we already generated the report
            data_file = reports_dir / f"report_{timestamp}.json"
            with open(data_file, "w") as f:
                json.dump({
                    "period": report.period,
                    "total_executions": report.total_executions,
                    "success_rate": report.success_rate,
                    "metrics": report.metrics,
                    "generated_at": report.generated_at,
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
