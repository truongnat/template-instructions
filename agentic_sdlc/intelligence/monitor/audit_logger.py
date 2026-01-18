"""
Audit Logger - Records all actions for audit trail.

Part of Layer 2: Intelligence Layer.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class AuditLogger:
    """
    Records all actions for audit trail and compliance.
    
    Every action in the system should be logged for:
    - Traceability
    - Compliance auditing
    - Pattern analysis
    - Debugging
    """

    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path(__file__).parent.parent.parent.parent / "docs" / "audit"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._current_session: List[Dict] = []

    def _get_log_file(self) -> Path:
        """Get current audit log file."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"audit-{date_str}.json"

    def _load_log(self) -> List[Dict]:
        """Load existing log entries for today."""
        log_file = self._get_log_file()
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save_log(self, entries: List[Dict]):
        """Save log entries."""
        log_file = self._get_log_file()
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)

    def log(
        self,
        action: str,
        category: str,
        details: Optional[Dict] = None,
        agent: Optional[str] = None,
        workflow: Optional[str] = None,
        severity: str = "info"
    ):
        """
        Log an action.
        
        Args:
            action: Description of the action
            category: Category (e.g., 'workflow', 'code', 'deploy')
            details: Additional details
            agent: Agent/role performing the action
            workflow: Current workflow
            severity: Log severity (debug, info, warning, error)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "category": category,
            "agent": agent,
            "workflow": workflow,
            "severity": severity,
            "details": details or {}
        }
        
        self._current_session.append(entry)
        
        # Persist every 10 entries or on error
        if len(self._current_session) >= 10 or severity == "error":
            self.flush()

    def log_workflow_start(self, workflow: str, agent: str, context: Optional[Dict] = None):
        """Log workflow start."""
        self.log(
            action=f"Started workflow: {workflow}",
            category="workflow",
            agent=agent,
            workflow=workflow,
            details=context
        )

    def log_workflow_end(self, workflow: str, agent: str, success: bool, context: Optional[Dict] = None):
        """Log workflow end."""
        self.log(
            action=f"Completed workflow: {workflow}",
            category="workflow",
            agent=agent,
            workflow=workflow,
            severity="info" if success else "warning",
            details={"success": success, **(context or {})}
        )

    def log_phase_transition(self, from_phase: str, to_phase: str, agent: str):
        """Log phase transition."""
        self.log(
            action=f"Phase transition: {from_phase} -> {to_phase}",
            category="phase",
            agent=agent,
            details={"from_phase": from_phase, "to_phase": to_phase}
        )

    def log_error(self, error: str, agent: Optional[str] = None, context: Optional[Dict] = None):
        """Log an error."""
        self.log(
            action=f"Error: {error}",
            category="error",
            agent=agent,
            severity="error",
            details=context
        )

    def log_artifact_created(self, artifact: str, artifact_type: str, agent: Optional[str] = None):
        """Log artifact creation."""
        self.log(
            action=f"Created artifact: {artifact}",
            category="artifact",
            agent=agent,
            details={"artifact": artifact, "type": artifact_type}
        )

    def flush(self):
        """Flush pending log entries to disk."""
        if not self._current_session:
            return
        
        existing = self._load_log()
        existing.extend(self._current_session)
        self._save_log(existing)
        self._current_session = []

    def get_today_logs(self) -> List[Dict]:
        """Get all log entries for today."""
        self.flush()
        return self._load_log()

    def search(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Search log entries."""
        entries = self.get_today_logs()
        results = []
        
        for entry in entries:
            if query.lower() in entry.get("action", "").lower():
                if category is None or entry.get("category") == category:
                    results.append(entry)
        
        return results

    def get_stats(self) -> Dict:
        """Get audit statistics."""
        entries = self.get_today_logs()
        
        by_category = {}
        by_severity = {}
        by_agent = {}
        
        for entry in entries:
            cat = entry.get("category", "unknown")
            sev = entry.get("severity", "info")
            agent = entry.get("agent", "unknown")
            
            by_category[cat] = by_category.get(cat, 0) + 1
            by_severity[sev] = by_severity.get(sev, 0) + 1
            by_agent[agent] = by_agent.get(agent, 0) + 1
        
        return {
            "total_entries": len(entries),
            "by_category": by_category,
            "by_severity": by_severity,
            "by_agent": by_agent
        }


# Global logger instance
_logger: Optional[AuditLogger] = None


def get_logger() -> AuditLogger:
    """Get the global audit logger instance."""
    global _logger
    if _logger is None:
        _logger = AuditLogger()
    return _logger


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Audit Logger - Layer 2 Monitor Component")
    parser.add_argument("--stats", action="store_true", help="Show audit statistics")
    parser.add_argument("--search", type=str, help="Search log entries")
    parser.add_argument("--today", action="store_true", help="Show today's logs")
    parser.add_argument("--log", type=str, help="Log a custom message")
    
    args = parser.parse_args()
    logger = get_logger()
    
    if args.stats:
        stats = logger.get_stats()
        print(json.dumps(stats, indent=2))
    
    elif args.search:
        results = logger.search(args.search)
        print(json.dumps(results, indent=2))
    
    elif args.today:
        logs = logger.get_today_logs()
        for entry in logs[-20:]:  # Show last 20
            print(f"[{entry['timestamp']}] [{entry['severity']}] {entry['action']}")
    
    elif args.log:
        logger.log(args.log, "custom")
        logger.flush()
        print("✅ Logged")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

