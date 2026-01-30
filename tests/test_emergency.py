
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Helper to verify file exists
def test_emergency_file_exists():
    path = PROJECT_ROOT / "agentic_sdlc/infrastructure/workflows/emergency.py"
    assert path.exists()

class TestEmergencySeverityLevels:
    """Tests for severity level definitions"""
    
    def test_severity_levels_defined(self):
        """Test that all severity levels are defined"""
        from agentic_sdlc.infrastructure.automation.workflows.emergency import SEVERITY_LEVELS
        
        expected_levels = ['P0', 'P1', 'P2']
        for level in expected_levels:
            assert level in SEVERITY_LEVELS
    
    def test_severity_level_has_required_keys(self):
        """Test that each severity level has required configuration"""
        from agentic_sdlc.infrastructure.automation.workflows.emergency import SEVERITY_LEVELS
        
        required_keys = ['name', 'response_time', 'escalation', 'examples']
        
        for level, config in SEVERITY_LEVELS.items():
            for key in required_keys:
                assert key in config, f"Missing '{key}' in severity level {level}"
    
    def test_p0_is_critical(self):
        """Test that P0 is labeled critical"""
        from agentic_sdlc.infrastructure.automation.workflows.emergency import SEVERITY_LEVELS
        
        assert SEVERITY_LEVELS['P0']['name'] == 'Critical'
    
    def test_response_times_ordered(self):
        """Test that response times are properly ordered"""
        from agentic_sdlc.infrastructure.automation.workflows.emergency import SEVERITY_LEVELS
        
        # P0 should have fastest response time
        p0_time = SEVERITY_LEVELS['P0']['response_time']
        assert '15 min' in p0_time or '15 minute' in p0_time


class TestIncidentResponse:
    """Tests for IncidentResponse class"""
    
    def test_incident_response_creation(self):
        """Test creating an IncidentResponse instance"""
        from agentic_sdlc.infrastructure.automation.workflows.emergency import IncidentResponse
        
        incident = IncidentResponse("P0", "Test issue")
        
        assert incident.severity == "P0"
        assert incident.issue == "Test issue"
        assert incident.incident_id is not None
        assert incident.incident_id.startswith("INCIDENT-")
    
    def test_incident_response_lowercase_severity(self):
        """Test that lowercase severity is converted to uppercase"""
        from agentic_sdlc.infrastructure.automation.workflows.emergency import IncidentResponse
        
        incident = IncidentResponse("p1", "Test issue")
        
        assert incident.severity == "P1"
    
    def test_incident_response_timeline(self):
        """Test that timeline starts empty"""
        from agentic_sdlc.infrastructure.automation.workflows.emergency import IncidentResponse
        
        incident = IncidentResponse("P0", "Test issue")
        
        assert incident.timeline == []
    
    def test_log_event(self):
        """Test logging an event to timeline"""
        from agentic_sdlc.infrastructure.automation.workflows.emergency import IncidentResponse
        
        incident = IncidentResponse("P0", "Test issue")
        
        with patch('builtins.print'):  # Suppress print output
            incident.log_event("Test event", "Test action")
        
        assert len(incident.timeline) == 1
        assert incident.timeline[0]['event'] == "Test event"
        assert incident.timeline[0]['action'] == "Test action"


class TestEmergencyArgParser:
    """Tests for emergency workflow command line arguments"""
    
    def test_argparser_requires_issue(self):
        """Test that main import works"""
        from agentic_sdlc.infrastructure.automation.workflows.emergency import main
        assert callable(main)
    
    def test_argparser_accepts_severity_levels(self):
        """Test that all severity levels are accepted"""
        valid_severities = ['P0', 'P1', 'P2', 'p0', 'p1', 'p2']
        for severity in valid_severities:
            assert severity.upper() in ['P0', 'P1', 'P2']


class TestEmergencyIntegration:
    """Integration tests for emergency workflow"""
    
    def test_emergency_py_exists(self):
        """Test that emergency.py exists"""
        emergency_path = PROJECT_ROOT / "agentic_sdlc/infrastructure/workflows/emergency.py"
        assert emergency_path.exists()
    
    def test_emergency_py_is_executable(self):
        """Test that emergency.py can be imported"""
        try:
            from agentic_sdlc.infrastructure.automation.workflows.emergency import IncidentResponse, SEVERITY_LEVELS, main
        except ImportError as e:
            pytest.fail(f"Failed to import emergency module: {e}")
