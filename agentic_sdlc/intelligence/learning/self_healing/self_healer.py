"""
Self-Healing - QA→DEV Feedback Loop with Auto-Retry.

Part of Layer 2: Intelligence Layer.
Implements automatic error detection, retry logic, and escalation paths.
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


class FixStatus(str, Enum):
    """Status of a fix attempt."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    FAILED = "failed"
    ESCALATED = "escalated"


class IssueSeverity(str, Enum):
    """Severity of detected issues."""
    LOW = "low"           # Style, formatting
    MEDIUM = "medium"     # Logic issues, missing tests
    HIGH = "high"         # Bugs, security issues
    CRITICAL = "critical" # Breaking changes, data loss risk


@dataclass
class Issue:
    """Represents an issue detected by QA."""
    id: str
    type: str  # test_failure, code_review, security, lint
    severity: IssueSeverity
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "severity": self.severity.value,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "suggested_fix": self.suggested_fix
        }


@dataclass
class FixAttempt:
    """Represents an attempt to fix an issue."""
    iteration: int
    issue_id: str
    fix_description: str
    success: bool
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "iteration": self.iteration,
            "issue_id": self.issue_id,
            "fix_description": self.fix_description,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": self.timestamp
        }


@dataclass
class HealingResult:
    """Result of a self-healing attempt."""
    session_id: str
    success: bool
    iterations: int
    issues_found: int
    issues_fixed: int
    escalated: bool
    fix_attempts: List[FixAttempt]
    final_code: Optional[str] = None
    escalation_reason: Optional[str] = None
    duration_seconds: float = 0
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "success": self.success,
            "iterations": self.iterations,
            "issues_found": self.issues_found,
            "issues_fixed": self.issues_fixed,
            "escalated": self.escalated,
            "fix_attempts": [a.to_dict() for a in self.fix_attempts],
            "final_code": self.final_code,
            "escalation_reason": self.escalation_reason,
            "duration_seconds": self.duration_seconds
        }


class FeedbackLoop:
    """
    QA → DEV → QA feedback loop until all tests pass.
    
    Features:
    - Detect issues via QA Agent
    - Request fixes from DEV Agent
    - Retry until success or max iterations
    - Escalate to human if stuck
    - Learn from error patterns
    """
    
    def __init__(
        self,
        max_iterations: int = 3,
        storage_dir: Optional[Path] = None
    ):
        self.max_iterations = max_iterations
        self.storage_dir = storage_dir or Path(__file__).resolve().parent.parent.parent.parent / "docs" / ".self-healing"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.storage_dir / "healing_history.json"
        self.patterns_file = self.storage_dir / "error_patterns.json"
        
        # Callbacks for actual agent execution (to be set externally)
        self._qa_callback: Optional[Callable] = None
        self._dev_callback: Optional[Callable] = None
        self._test_callback: Optional[Callable] = None
        
    def set_qa_agent(self, callback: Callable[[str, str], List[Issue]]) -> None:
        """Set the QA agent callback: (code, requirements) -> List[Issue]"""
        self._qa_callback = callback
        
    def set_dev_agent(self, callback: Callable[[str, List[Issue]], str]) -> None:
        """Set the DEV agent callback: (code, issues) -> fixed_code"""
        self._dev_callback = callback
        
    def set_test_runner(self, callback: Callable[[str, str], List[Issue]]) -> None:
        """Set the test runner callback: (code, tests) -> List[Issue]"""
        self._test_callback = callback
        
    def run(
        self,
        code: str,
        requirements: str,
        tests: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> HealingResult:
        """
        Run the feedback loop until success or max iterations.
        
        Args:
            code: Initial code to validate
            requirements: Requirements to validate against
            tests: Optional test code to run
            session_id: Optional session ID for tracking
            
        Returns:
            HealingResult with details of the healing process
        """
        import time
        import uuid
        
        session_id = session_id or str(uuid.uuid4())[:8]
        start_time = time.time()
        
        fix_attempts: List[FixAttempt] = []
        current_code = code
        total_issues_found = 0
        total_issues_fixed = 0
        
        print(f"🔄 Starting self-healing loop (max {self.max_iterations} iterations)")
        
        for iteration in range(1, self.max_iterations + 1):
            print(f"\n--- Iteration {iteration}/{self.max_iterations} ---")
            
            # Step 1: Run QA review
            issues = self._run_qa(current_code, requirements)
            
            # Step 2: Run tests if provided
            if tests and self._test_callback:
                test_issues = self._test_callback(current_code, tests)
                issues.extend(test_issues)
                
            total_issues_found += len(issues)
            
            if not issues:
                print(f"✅ No issues found! Code is clean.")
                return HealingResult(
                    session_id=session_id,
                    success=True,
                    iterations=iteration,
                    issues_found=total_issues_found,
                    issues_fixed=total_issues_fixed,
                    escalated=False,
                    fix_attempts=fix_attempts,
                    final_code=current_code,
                    duration_seconds=time.time() - start_time
                )
                
            print(f"⚠️ Found {len(issues)} issues:")
            for issue in issues:
                print(f"   [{issue.severity.value}] {issue.description}")
                
            # Step 3: Check for known patterns
            patterns = self._check_patterns(issues)
            if patterns:
                print(f"💡 Found {len(patterns)} known patterns, applying fixes...")
                
            # Step 4: Request fix from DEV
            fixed_code = self._run_dev_fix(current_code, issues)
            
            # Record attempt
            fix_attempt = FixAttempt(
                iteration=iteration,
                issue_id=issues[0].id if issues else "unknown",
                fix_description=f"Fixed {len(issues)} issues",
                success=fixed_code != current_code
            )
            fix_attempts.append(fix_attempt)
            
            if fixed_code == current_code:
                print(f"⚠️ DEV could not fix the issues")
                fix_attempt.success = False
                fix_attempt.error_message = "No changes made"
            else:
                total_issues_fixed += len(issues)
                current_code = fixed_code
                
                # Learn from fix
                self._learn_pattern(issues, fixed_code)
                
        # Max iterations reached - escalate
        print(f"\n🚨 Max iterations ({self.max_iterations}) reached. Escalating to human...")
        
        return HealingResult(
            session_id=session_id,
            success=False,
            iterations=self.max_iterations,
            issues_found=total_issues_found,
            issues_fixed=total_issues_fixed,
            escalated=True,
            fix_attempts=fix_attempts,
            final_code=current_code,
            escalation_reason=f"Could not resolve all issues after {self.max_iterations} iterations",
            duration_seconds=time.time() - start_time
        )
        
    def _run_qa(self, code: str, requirements: str) -> List[Issue]:
        """Run QA review on code."""
        if self._qa_callback:
            return self._qa_callback(code, requirements)
            
        # Default: simple syntax/lint check
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if 'TODO' in line or 'FIXME' in line:
                issues.append(Issue(
                    id=f"todo-{i}",
                    type="code_review",
                    severity=IssueSeverity.LOW,
                    description=f"TODO/FIXME found on line {i}",
                    line_number=i
                ))
            if 'print(' in line and 'debug' in line.lower():
                issues.append(Issue(
                    id=f"debug-{i}",
                    type="code_review",
                    severity=IssueSeverity.MEDIUM,
                    description=f"Debug print statement on line {i}",
                    line_number=i
                ))
                
        return issues
        
    def _run_dev_fix(self, code: str, issues: List[Issue]) -> str:
        """Request fix from DEV agent."""
        if self._dev_callback:
            return self._dev_callback(code, issues)
            
        # Default: no fix capability
        return code
        
    def _check_patterns(self, issues: List[Issue]) -> List[dict]:
        """Check if issues match known error patterns."""
        if not self.patterns_file.exists():
            return []
            
        try:
            patterns = json.loads(self.patterns_file.read_text(encoding='utf-8'))
            
            matched = []
            for issue in issues:
                for pattern in patterns:
                    if pattern.get("description_match") in issue.description:
                        matched.append({
                            "issue": issue.to_dict(),
                            "pattern": pattern,
                            "suggested_fix": pattern.get("fix")
                        })
                        
            return matched
        except:
            return []
            
    def _learn_pattern(self, issues: List[Issue], fixed_code: str) -> None:
        """Learn from successful fix for future use."""
        patterns = []
        if self.patterns_file.exists():
            try:
                patterns = json.loads(self.patterns_file.read_text(encoding='utf-8'))
            except:
                pass
                
        for issue in issues:
            pattern = {
                "type": issue.type,
                "severity": issue.severity.value,
                "description_match": issue.description[:50],  # First 50 chars for matching
                "fix": issue.suggested_fix or "Applied automatic fix",
                "learned_at": datetime.now().isoformat()
            }
            patterns.append(pattern)
            
        # Keep last 100 patterns
        patterns = patterns[-100:]
        self.patterns_file.write_text(json.dumps(patterns, indent=2), encoding='utf-8')
        
    def _save_history(self, result: HealingResult) -> None:
        """Save healing result to history."""
        history = []
        if self.history_file.exists():
            try:
                history = json.loads(self.history_file.read_text(encoding='utf-8'))
            except:
                pass
                
        history.append(result.to_dict())
        history = history[-100:]
        
        self.history_file.write_text(json.dumps(history, indent=2), encoding='utf-8')
        
    def get_stats(self) -> Dict[str, Any]:
        """Get self-healing statistics."""
        if not self.history_file.exists():
            return {
                "total_sessions": 0,
                "successful": 0,
                "success_rate": 0,
                "escalated": 0,
                "escalation_rate": 0,
                "avg_iterations": 0,
                "avg_duration_seconds": 0
            }
            
        history = json.loads(self.history_file.read_text(encoding='utf-8'))
        
        total = len(history)
        successful = len([h for h in history if h["success"]])
        escalated = len([h for h in history if h["escalated"]])
        
        avg_iterations = sum(h["iterations"] for h in history) / total if total else 0
        avg_duration = sum(h["duration_seconds"] for h in history) / total if total else 0
        
        if total == 0:
            return {
                "total_sessions": 0,
                "successful": 0,
                "success_rate": 0,
                "escalated": 0,
                "escalation_rate": 0,
                "avg_iterations": 0,
                "avg_duration_seconds": 0
            }
            
        return {
            "total_sessions": total,
            "successful": successful,
            "success_rate": successful / total if total else 0,
            "escalated": escalated,
            "escalation_rate": escalated / total if total else 0,
            "avg_iterations": avg_iterations,
            "avg_duration_seconds": avg_duration
        }


class SelfHealingOrchestrator:
    """
    High-level orchestrator for self-healing workflows.
    
    Integrates with HITL for escalation and State Manager for checkpointing.
    """
    
    def __init__(self):
        self.feedback_loop = FeedbackLoop()
        self._hitl_manager = None
        self._state_manager = None
        
    def set_hitl_manager(self, manager) -> None:
        """Set HITL manager for escalation."""
        self._hitl_manager = manager
        
    def set_state_manager(self, manager) -> None:
        """Set State manager for checkpointing."""
        self._state_manager = manager
        
    def heal(
        self,
        code: str,
        requirements: str,
        session_id: Optional[str] = None
    ) -> HealingResult:
        """
        Run self-healing with checkpointing and escalation support.
        """
        result = self.feedback_loop.run(code, requirements, session_id=session_id)
        
        # Checkpoint result if state manager available
        if self._state_manager and session_id:
            self._state_manager.save_checkpoint(
                session_id,
                "self_healing",
                {"result": result.to_dict()}
            )
            
        # Escalate to HITL if needed
        if result.escalated and self._hitl_manager:
            from agentic_sdlc.intelligence.monitoring.hitl import ApprovalGate
            
            self._hitl_manager.request_approval(
                gate=ApprovalGate.CODE_REVIEW,
                session_id=session_id or "unknown",
                artifact_paths=[],
                context={
                    "reason": "Self-healing could not resolve all issues",
                    "iterations": result.iterations,
                    "issues_remaining": result.issues_found - result.issues_fixed
                }
            )
            
        return result


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Healing - QA→DEV Feedback Loop")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run healing
    run_parser = subparsers.add_parser("run", help="Run self-healing on code")
    run_parser.add_argument("--code", required=True, help="Code to heal (or path to file)")
    run_parser.add_argument("--requirements", default="", help="Requirements to validate against")
    run_parser.add_argument("--max-iterations", type=int, default=3, help="Max iterations")
    
    # Stats
    subparsers.add_parser("stats", help="Show self-healing statistics")
    
    # Patterns
    subparsers.add_parser("patterns", help="List learned error patterns")
    
    args = parser.parse_args()
    
    if args.command == "run":
        code = args.code
        if Path(code).exists():
            code = Path(code).read_text(encoding='utf-8')
            
        loop = FeedbackLoop(max_iterations=args.max_iterations)
        result = loop.run(code, args.requirements)
        
        print(f"\n📊 Result:")
        print(f"   Success: {result.success}")
        print(f"   Iterations: {result.iterations}")
        print(f"   Issues Found: {result.issues_found}")
        print(f"   Issues Fixed: {result.issues_fixed}")
        print(f"   Escalated: {result.escalated}")
        
    elif args.command == "stats":
        loop = FeedbackLoop()
        stats = loop.get_stats()
        print("📊 Self-Healing Statistics:\n")
        print(f"  Total Sessions: {stats['total_sessions']}")
        print(f"  Successful: {stats['successful']} ({stats['success_rate']*100:.1f}%)")
        print(f"  Escalated: {stats['escalated']} ({stats['escalation_rate']*100:.1f}%)")
        print(f"  Avg Iterations: {stats['avg_iterations']:.1f}")
        print(f"  Avg Duration: {stats['avg_duration_seconds']:.1f}s")
        
    elif args.command == "patterns":
        loop = FeedbackLoop()
        if loop.patterns_file.exists():
            patterns = json.loads(loop.patterns_file.read_text(encoding='utf-8'))
            print(f"📚 Learned Error Patterns ({len(patterns)}):\n")
            for p in patterns[-10:]:  # Show last 10
                print(f"  [{p['severity']}] {p['type']}")
                print(f"     Match: {p['description_match'][:40]}...")
                print(f"     Fix: {p['fix'][:50]}...")
                print()
        else:
            print("📭 No patterns learned yet")
            
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
