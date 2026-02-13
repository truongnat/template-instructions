"""Unit tests for lifecycle manager components."""

import pytest
from agentic_sdlc.infrastructure.lifecycle import LifecycleManager, Phase


class TestPhase:
    """Tests for Phase enum."""
    
    def test_phase_values(self):
        """Test that all phase values are defined."""
        assert Phase.INITIALIZED.value == "initialized"
        assert Phase.STARTED.value == "started"
        assert Phase.RUNNING.value == "running"
        assert Phase.PAUSED.value == "paused"
        assert Phase.STOPPED.value == "stopped"
        assert Phase.SHUTDOWN.value == "shutdown"
        assert Phase.ERROR.value == "error"


class TestLifecycleManager:
    """Tests for LifecycleManager class."""
    
    def test_lifecycle_manager_initialization(self):
        """Test that LifecycleManager initializes in INITIALIZED phase."""
        manager = LifecycleManager()
        assert manager.get_phase() == Phase.INITIALIZED
    
    def test_transition_to_started(self):
        """Test transitioning from INITIALIZED to STARTED."""
        manager = LifecycleManager()
        manager.transition_to(Phase.STARTED)
        assert manager.get_phase() == Phase.STARTED
    
    def test_transition_to_running(self):
        """Test transitioning to RUNNING phase."""
        manager = LifecycleManager()
        manager.transition_to(Phase.STARTED)
        manager.transition_to(Phase.RUNNING)
        assert manager.get_phase() == Phase.RUNNING
    
    def test_transition_to_paused(self):
        """Test transitioning to PAUSED phase."""
        manager = LifecycleManager()
        manager.transition_to(Phase.STARTED)
        manager.transition_to(Phase.RUNNING)
        manager.transition_to(Phase.PAUSED)
        assert manager.get_phase() == Phase.PAUSED
    
    def test_transition_to_stopped(self):
        """Test transitioning to STOPPED phase."""
        manager = LifecycleManager()
        manager.transition_to(Phase.STARTED)
        manager.transition_to(Phase.RUNNING)
        manager.transition_to(Phase.STOPPED)
        assert manager.get_phase() == Phase.STOPPED
    
    def test_transition_to_shutdown(self):
        """Test transitioning to SHUTDOWN phase."""
        manager = LifecycleManager()
        manager.transition_to(Phase.SHUTDOWN)
        assert manager.get_phase() == Phase.SHUTDOWN
    
    def test_invalid_transition(self):
        """Test that invalid transitions raise error."""
        manager = LifecycleManager()
        # Cannot go directly from INITIALIZED to RUNNING
        with pytest.raises(ValueError, match="Invalid transition"):
            manager.transition_to(Phase.RUNNING)
    
    def test_invalid_transition_from_shutdown(self):
        """Test that transitions from SHUTDOWN are invalid."""
        manager = LifecycleManager()
        manager.transition_to(Phase.SHUTDOWN)
        
        with pytest.raises(ValueError, match="Invalid transition"):
            manager.transition_to(Phase.STARTED)
    
    def test_register_callback(self):
        """Test registering a callback for a phase."""
        manager = LifecycleManager()
        callback_called = []
        
        def callback():
            callback_called.append(True)
        
        manager.register_callback(Phase.STARTED, callback)
        manager.transition_to(Phase.STARTED)
        
        assert len(callback_called) == 1
    
    def test_multiple_callbacks(self):
        """Test multiple callbacks for same phase."""
        manager = LifecycleManager()
        calls = []
        
        def callback1():
            calls.append(1)
        
        def callback2():
            calls.append(2)
        
        manager.register_callback(Phase.STARTED, callback1)
        manager.register_callback(Phase.STARTED, callback2)
        manager.transition_to(Phase.STARTED)
        
        assert len(calls) == 2
        assert 1 in calls
        assert 2 in calls
    
    def test_callback_not_called_for_other_phase(self):
        """Test that callbacks are not called for other phases."""
        manager = LifecycleManager()
        callback_called = []
        
        def callback():
            callback_called.append(True)
        
        manager.register_callback(Phase.RUNNING, callback)
        manager.transition_to(Phase.STARTED)
        
        assert len(callback_called) == 0
    
    def test_is_running(self):
        """Test is_running method."""
        manager = LifecycleManager()
        assert not manager.is_running()
        
        manager.transition_to(Phase.STARTED)
        assert not manager.is_running()
        
        manager.transition_to(Phase.RUNNING)
        assert manager.is_running()
        
        manager.transition_to(Phase.PAUSED)
        assert not manager.is_running()
    
    def test_is_stopped(self):
        """Test is_stopped method."""
        manager = LifecycleManager()
        assert not manager.is_stopped()
        
        manager.transition_to(Phase.STARTED)
        assert not manager.is_stopped()
        
        manager.transition_to(Phase.RUNNING)
        assert not manager.is_stopped()
        
        manager.transition_to(Phase.STOPPED)
        assert manager.is_stopped()
        
        manager.transition_to(Phase.SHUTDOWN)
        assert manager.is_stopped()
    
    def test_error_phase_transition(self):
        """Test transitioning to ERROR phase."""
        manager = LifecycleManager()
        manager.transition_to(Phase.STARTED)
        manager.transition_to(Phase.RUNNING)
        manager.transition_to(Phase.ERROR)
        assert manager.get_phase() == Phase.ERROR
    
    def test_error_phase_to_stopped(self):
        """Test transitioning from ERROR to STOPPED."""
        manager = LifecycleManager()
        manager.transition_to(Phase.STARTED)
        manager.transition_to(Phase.RUNNING)
        manager.transition_to(Phase.ERROR)
        manager.transition_to(Phase.STOPPED)
        assert manager.get_phase() == Phase.STOPPED
    
    def test_callback_exception_handling(self):
        """Test that callback exceptions don't break lifecycle."""
        manager = LifecycleManager()
        
        def failing_callback():
            raise RuntimeError("Callback failed")
        
        def success_callback():
            pass
        
        manager.register_callback(Phase.STARTED, failing_callback)
        manager.register_callback(Phase.STARTED, success_callback)
        
        # Should not raise even though first callback fails
        manager.transition_to(Phase.STARTED)
        assert manager.get_phase() == Phase.STARTED
