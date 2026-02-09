"""
State Manager Implementation

This module implements the StateManager class responsible for persisting workflow state,
managing checkpoints, and handling recovery from interruptions.

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import json
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from ..models.workflow import WorkflowState, Checkpoint
from ..utils.logging import get_logger


class StateManager:
    """
    State Manager for workflow persistence and recovery.
    
    Features:
    - State Persistence (File-based for MVP)
    - Checkpoint Management
    - Crash Recovery
    - Audit Trail
    """
    
    def __init__(self, persistence_dir: str = ".brain/states"):
        self.logger = get_logger(__name__)
        self.persistence_dir = persistence_dir
        self.active_states: Dict[str, WorkflowState] = {}
        self._lock = threading.RLock()
        
        # Ensure persistence directory exists
        os.makedirs(self.persistence_dir, exist_ok=True)
        
    def save_state(self, state: WorkflowState) -> bool:
        """
        Save the current state of a workflow
        
        Args:
            state: Workflow state to save
            
        Returns:
            True if successful
        """
        try:
            with self._lock:
                self.active_states[state.execution_id] = state
                
                # Serialize state
                # For MVP, we'll use a simplified serialization
                # In production, we would use proper schema validation/serialization
                state_data = self._serialize_state(state)
                
                file_path = os.path.join(self.persistence_dir, f"{state.execution_id}.json")
                with open(file_path, 'w') as f:
                    json.dump(state_data, f, indent=2, default=str)
                    
                self.logger.info(f"Saved state for execution {state.execution_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
            return False
            
    def load_state(self, execution_id: str) -> Optional[WorkflowState]:
        """
        Load a workflow state from persistence
        
        Args:
            execution_id: ID of the execution
            
        Returns:
            Loaded WorkflowState or None
        """
        try:
            with self._lock:
                # Check cache first
                if execution_id in self.active_states:
                    return self.active_states[execution_id]
                
                # Load from file
                file_path = os.path.join(self.persistence_dir, f"{execution_id}.json")
                if not os.path.exists(file_path):
                    return None
                    
                with open(file_path, 'r') as f:
                    state_data = json.load(f)
                    
                state = self._deserialize_state(state_data)
                self.active_states[execution_id] = state
                
                self.logger.info(f"Loaded state for execution {execution_id}")
                return state
                
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            return None
            
    def create_checkpoint(self, execution_id: str, phase: str, description: str = "") -> Optional[Checkpoint]:
        """
        Create a checkpoint for a workflow execution
        
        Args:
            execution_id: ID of the execution
            phase: Current phase
            description: Description of the checkpoint
            
        Returns:
            Created Checkpoint or None
        """
        state = self.load_state(execution_id)
        if not state:
            return None
            
        checkpoint = Checkpoint(
            timestamp=datetime.now(),
            phase=phase,
            description=description,
            recoverable=True,
            metadata={"execution_id": execution_id}
        )
        
        # In a full implementation, we would deep copy the state into the checkpoint
        # For now, we just track the metadata
        
        state.add_checkpoint(checkpoint)
        self.save_state(state)
        
        return checkpoint
        
    def list_active_executions(self) -> List[str]:
        """List IDs of all persisted executions"""
        try:
            files = os.listdir(self.persistence_dir)
            return [f.replace('.json', '') for f in files if f.endswith('.json')]
        except Exception:
            return []
            
    def _serialize_state(self, state: WorkflowState) -> Dict[str, Any]:
        """Serialize WorkflowState to dict"""
        return {
            "execution_id": state.execution_id,
            "current_phase": state.current_phase,
            "completed_phases": state.completed_phases,
            "last_updated": state.last_updated.isoformat(),
            "metadata": state.metadata,
            "checkpoints": [
                {
                    "id": cp.id,
                    "timestamp": cp.timestamp.isoformat(),
                    "phase": cp.phase,
                    "description": cp.description,
                    "recoverable": cp.recoverable
                } for cp in state.checkpoints
            ]
        }
        
    def _deserialize_state(self, data: Dict[str, Any]) -> WorkflowState:
        """Deserialize dict to WorkflowState"""
        state = WorkflowState(
            execution_id=data["execution_id"],
            current_phase=data["current_phase"],
            completed_phases=data.get("completed_phases", []),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            metadata=data.get("metadata", {})
        )
        
        # Restore checkpoints
        for cp_data in data.get("checkpoints", []):
            cp = Checkpoint(
                id=cp_data.get("id", str(uuid4())),
                timestamp=datetime.fromisoformat(cp_data["timestamp"]),
                phase=cp_data["phase"],
                description=cp_data["description"],
                recoverable=cp_data["recoverable"]
            )
            state.checkpoints.append(cp)
            
        return state
