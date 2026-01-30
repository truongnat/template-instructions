"""
Execution Tracker - Track AI agent actions during workflow execution
"""

import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum


class ActionType(Enum):
    """Types of actions that can be tracked"""
    COMMAND = "command"
    FILE_CREATE = "file_create"
    FILE_EDIT = "file_edit"
    FILE_DELETE = "file_delete"
    WORKFLOW_START = "workflow_start"
    WORKFLOW_END = "workflow_end"
    USER_NOTIFY = "user_notify"
    TOOL_CALL = "tool_call"
    OTHER = "other"


@dataclass
class Action:
    """Represents a single tracked action"""
    action_type: ActionType
    timestamp: float
    details: Dict[str, Any]
    step_number: Optional[int] = None
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['action_type'] = self.action_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        """Create from dictionary"""
        data['action_type'] = ActionType(data['action_type'])
        return cls(**data)


@dataclass
class ExecutionSession:
    """Represents a workflow execution session"""
    workflow_name: str
    start_time: float
    end_time: Optional[float] = None
    actions: List[Action] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def duration(self) -> float:
        """Get session duration in seconds"""
        end = self.end_time or time.time()
        return end - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'workflow_name': self.workflow_name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration(),
            'actions': [action.to_dict() for action in self.actions],
            'metadata': self.metadata
        }


class ExecutionTracker:
    """Track AI agent execution against workflow steps"""
    
    def __init__(self, session_dir: Optional[Path] = None):
        """
        Initialize tracker
        
        Args:
            session_dir: Directory to store session files (defaults to .brain/)
        """
        if session_dir is None:
            # Default to project root .brain directory
            session_dir = Path(__file__).parent.parent.parent.parent / '.brain' / 'sessions'
        
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_session: Optional[ExecutionSession] = None
    
    def start_tracking(self, workflow_name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Start tracking a new workflow execution session
        
        Args:
            workflow_name: Name of the workflow being executed
            metadata: Optional metadata about the session
        """
        if self.current_session:
            # Auto-end previous session
            self.end_tracking()
        
        self.current_session = ExecutionSession(
            workflow_name=workflow_name,
            start_time=time.time(),
            metadata=metadata or {}
        )
        
        # Log workflow start
        self.log_action(
            ActionType.WORKFLOW_START,
            {'workflow': workflow_name}
        )
    
    def end_tracking(self):
        """End the current tracking session and save"""
        if not self.current_session:
            return
        
        self.current_session.end_time = time.time()
        
        # Log workflow end
        self.log_action(
            ActionType.WORKFLOW_END,
            {'workflow': self.current_session.workflow_name}
        )
        
        # Save session
        self._save_session()
        
        # Clear current session
        self.current_session = None
    
    def log_action(
        self,
        action_type: ActionType,
        details: Dict[str, Any],
        step_number: Optional[int] = None,
        success: bool = True,
        error: Optional[str] = None
    ):
        """
        Log an action during workflow execution
        
        Args:
            action_type: Type of action
            details: Action details
            step_number: Optional workflow step number this relates to
            success: Whether action succeeded
            error: Optional error message if failed
        """
        if not self.current_session:
            # No active session, create a default one
            self.start_tracking("unknown")
        
        action = Action(
            action_type=action_type,
            timestamp=time.time(),
            details=details,
            step_number=step_number,
            success=success,
            error=error
        )
        
        self.current_session.actions.append(action)
    
    def log_command(self, command: str, cwd: str, success: bool = True, output: str = ""):
        """Convenience method to log a command execution"""
        self.log_action(
            ActionType.COMMAND,
            {
                'command': command,
                'cwd': cwd,
                'output': output[:500]  # Truncate long output
            },
            success=success
        )
    
    def log_file_operation(self, operation: str, filepath: str, success: bool = True):
        """Convenience method to log file operations"""
        action_type_map = {
            'create': ActionType.FILE_CREATE,
            'edit': ActionType.FILE_EDIT,
            'delete': ActionType.FILE_DELETE
        }
        
        self.log_action(
            action_type_map.get(operation, ActionType.OTHER),
            {'filepath': filepath},
            success=success
        )
    
    def get_execution_log(self) -> List[Action]:
        """Get all logged actions from current session"""
        if not self.current_session:
            return []
        return self.current_session.actions.copy()
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        if not self.current_session:
            return {}
        
        return {
            'workflow': self.current_session.workflow_name,
            'duration': self.current_session.duration(),
            'total_actions': len(self.current_session.actions),
            'action_types': self._count_action_types(),
            'success_rate': self._calculate_success_rate()
        }
    
    def _count_action_types(self) -> Dict[str, int]:
        """Count actions by type"""
        if not self.current_session:
            return {}
        
        counts = {}
        for action in self.current_session.actions:
            type_name = action.action_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        
        return counts
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate of actions"""
        if not self.current_session or not self.current_session.actions:
            return 100.0
        
        successful = sum(1 for action in self.current_session.actions if action.success)
        return (successful / len(self.current_session.actions)) * 100
    
    def _save_session(self):
        """Save current session to file"""
        if not self.current_session:
            return
        
        # Generate filename with timestamp
        timestamp = datetime.fromtimestamp(self.current_session.start_time)
        filename = f"{timestamp.strftime('%Y%m%d-%H%M%S')}_{self.current_session.workflow_name}.json"
        filepath = self.session_dir / filename
        
        # Save as JSON
        with open(filepath, 'w') as f:
            json.dump(self.current_session.to_dict(), f, indent=2)
    
    @classmethod
    def load_session(cls, session_file: Path) -> ExecutionSession:
        """Load a session from file"""
        with open(session_file, 'r') as f:
            data = json.load(f)
        
        # Reconstruct actions
        actions = [Action.from_dict(action_data) for action_data in data['actions']]
        
        return ExecutionSession(
            workflow_name=data['workflow_name'],
            start_time=data['start_time'],
            end_time=data.get('end_time'),
            actions=actions,
            metadata=data.get('metadata', {})
        )
    
    def get_latest_session(self, workflow_name: Optional[str] = None) -> Optional[ExecutionSession]:
        """
        Get the most recent session
        
        Args:
            workflow_name: Optional filter by workflow name
            
        Returns:
            Most recent ExecutionSession or None
        """
        session_files = sorted(self.session_dir.glob('*.json'), reverse=True)
        
        for session_file in session_files:
            if workflow_name and workflow_name not in session_file.name:
                continue
            
            try:
                return self.load_session(session_file)
            except Exception:
                continue
        
        return None


# Global tracker instance
_global_tracker = None


def get_tracker() -> ExecutionTracker:
    """Get global tracker instance"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = ExecutionTracker()
    return _global_tracker


if __name__ == "__main__":
    # Test tracking
    tracker = ExecutionTracker()
    
    # Start tracking
    tracker.start_tracking("commit")
    
    # Log some actions
    tracker.log_command("git status", "/project")
    tracker.log_command("git add .", "/project")
    tracker.log_command("git commit -m 'test'", "/project")
    
    # End tracking
    tracker.end_tracking()
    
    print("Session saved!")
    print(f"Latest session: {tracker.get_latest_session()}")
