"""Lifecycle management for SDK components."""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class Phase(Enum):
    """Lifecycle phases for SDK components."""
    
    INITIALIZED = "initialized"
    STARTED = "started"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    SHUTDOWN = "shutdown"
    ERROR = "error"


class LifecycleManager:
    """Manager for component lifecycle.
    
    The LifecycleManager handles the lifecycle of SDK components,
    managing transitions between phases and executing callbacks.
    """
    
    def __init__(self) -> None:
        """Initialize the lifecycle manager."""
        self._phase = Phase.INITIALIZED
        self._callbacks: Dict[Phase, List[Callable[[], Any]]] = {
            phase: [] for phase in Phase
        }
    
    def get_phase(self) -> Phase:
        """Get the current lifecycle phase.
        
        Returns:
            The current phase.
        """
        return self._phase
    
    def transition_to(self, phase: Phase) -> None:
        """Transition to a new lifecycle phase.
        
        Args:
            phase: The target phase.
            
        Raises:
            ValueError: If the transition is invalid.
        """
        # Validate transition
        valid_transitions = {
            Phase.INITIALIZED: [Phase.STARTED, Phase.SHUTDOWN],
            Phase.STARTED: [Phase.RUNNING, Phase.STOPPED, Phase.SHUTDOWN],
            Phase.RUNNING: [Phase.PAUSED, Phase.STOPPED, Phase.ERROR, Phase.SHUTDOWN],
            Phase.PAUSED: [Phase.RUNNING, Phase.STOPPED, Phase.SHUTDOWN],
            Phase.STOPPED: [Phase.STARTED, Phase.SHUTDOWN],
            Phase.SHUTDOWN: [],
            Phase.ERROR: [Phase.STOPPED, Phase.SHUTDOWN],
        }
        
        if phase not in valid_transitions.get(self._phase, []):
            raise ValueError(
                f"Invalid transition from {self._phase.value} to {phase.value}"
            )
        
        self._phase = phase
        self._execute_callbacks(phase)
    
    def register_callback(self, phase: Phase, callback: Callable[[], Any]) -> None:
        """Register a callback for a lifecycle phase.
        
        Args:
            phase: The phase to register the callback for.
            callback: The callback function to execute.
        """
        self._callbacks[phase].append(callback)
    
    def _execute_callbacks(self, phase: Phase) -> None:
        """Execute all callbacks for a phase.
        
        Args:
            phase: The phase to execute callbacks for.
        """
        for callback in self._callbacks[phase]:
            try:
                callback()
            except Exception as e:
                # Log but don't raise to prevent callback errors from breaking lifecycle
                pass
    
    def is_running(self) -> bool:
        """Check if the component is running.
        
        Returns:
            True if in RUNNING phase, False otherwise.
        """
        return self._phase == Phase.RUNNING
    
    def is_stopped(self) -> bool:
        """Check if the component is stopped.
        
        Returns:
            True if in STOPPED or SHUTDOWN phase, False otherwise.
        """
        return self._phase in (Phase.STOPPED, Phase.SHUTDOWN)
