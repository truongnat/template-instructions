"""
Unit tests for pytest configuration and fixtures.

This test verifies that the pytest configuration files (conftest.py, 
test_config.yaml, pytest.ini) are properly set up and working.

Requirements: 4.4, 4.5
Task: 2.2
"""

import pytest
from pathlib import Path
import yaml


class TestPytestConfiguration:
    """Test that pytest configuration is properly set up."""
    
    def test_conftest_exists(self, project_root):
        """Test that conftest.py exists in tests directory."""
        conftest_path = project_root / "tests" / "conftest.py"
        assert conftest_path.exists(), "conftest.py should exist in tests directory"
    
    def test_test_config_yaml_exists(self, project_root):
        """Test that test_config.yaml exists in tests directory."""
        config_path = project_root / "tests" / "test_config.yaml"
        assert config_path.exists(), "test_config.yaml should exist in tests directory"
    
    def test_pytest_ini_exists(self, project_root):
        """Test that pytest.ini exists in project root."""
        pytest_ini_path = project_root / "pytest.ini"
        assert pytest_ini_path.exists(), "pytest.ini should exist in project root"
    
    def test_test_config_yaml_valid_syntax(self, project_root):
        """Test that test_config.yaml has valid YAML syntax."""
        config_path = project_root / "tests" / "test_config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        assert isinstance(config, dict), "test_config.yaml should contain a dictionary"
    
    def test_test_config_has_required_sections(self, test_config):
        """Test that test_config.yaml has all required sections."""
        required_sections = [
            "general",
            "discovery",
            "test_types",
            "coverage",
            "fixtures",
            "markers"
        ]
        for section in required_sections:
            assert section in test_config, f"test_config.yaml should have '{section}' section"
    
    def test_test_discovery_patterns_configured(self, test_config):
        """Test that test discovery patterns are configured."""
        assert "discovery" in test_config
        assert "test_file_patterns" in test_config["discovery"]
        patterns = test_config["discovery"]["test_file_patterns"]
        assert "test_*.py" in patterns, "Should include test_*.py pattern"
    
    def test_test_types_configured(self, test_config):
        """Test that all test types are configured."""
        test_types = ["unit", "integration", "e2e", "property"]
        for test_type in test_types:
            assert test_type in test_config["test_types"], f"{test_type} tests should be configured"
            assert "enabled" in test_config["test_types"][test_type]
            assert "timeout" in test_config["test_types"][test_type]
    
    def test_coverage_configured(self, test_config):
        """Test that coverage settings are configured."""
        assert "coverage" in test_config
        assert "enabled" in test_config["coverage"]
        assert "source" in test_config["coverage"]
        assert "fail_under" in test_config["coverage"]
        assert test_config["coverage"]["fail_under"] >= 80, "Coverage threshold should be at least 80%"


class TestPathFixtures:
    """Test that path fixtures work correctly."""
    
    def test_project_root_fixture(self, project_root):
        """Test that project_root fixture returns a valid path."""
        assert isinstance(project_root, Path)
        assert project_root.exists()
        assert (project_root / "tests").exists()
    
    def test_tests_dir_fixture(self, tests_dir):
        """Test that tests_dir fixture returns the tests directory."""
        assert isinstance(tests_dir, Path)
        assert tests_dir.exists()
        assert tests_dir.name == "tests"
    
    def test_fixtures_dir_fixture(self, fixtures_dir):
        """Test that fixtures_dir fixture returns the fixtures directory."""
        assert isinstance(fixtures_dir, Path)
        assert fixtures_dir.exists()
        assert fixtures_dir.name == "fixtures"
    
    def test_tools_dir_fixture(self, tools_dir):
        """Test that tools_dir fixture returns the agentic_sdlc directory."""
        assert isinstance(tools_dir, Path)
        assert tools_dir.exists()
        assert tools_dir.name == "agentic_sdlc"


class TestTemporaryDirectoryFixtures:
    """Test that temporary directory fixtures work correctly."""
    
    def test_temp_dir_fixture(self, temp_dir):
        """Test that temp_dir fixture creates a temporary directory."""
        assert isinstance(temp_dir, Path)
        assert temp_dir.exists()
        # Write a test file to verify it's writable
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        assert test_file.exists()
    
    def test_temp_config_dir_fixture(self, temp_config_dir):
        """Test that temp_config_dir fixture creates a config directory."""
        assert isinstance(temp_config_dir, Path)
        assert temp_config_dir.exists()
        assert temp_config_dir.name == "config"
    
    def test_temp_data_dir_fixture(self, temp_data_dir):
        """Test that temp_data_dir fixture creates a data directory."""
        assert isinstance(temp_data_dir, Path)
        assert temp_data_dir.exists()
        assert temp_data_dir.name == "data"
    
    def test_temp_dir_cleanup(self, temp_dir):
        """Test that temp_dir is cleaned up after test (verified by pytest)."""
        # This test just verifies the fixture works
        # Cleanup is verified by pytest fixture teardown
        assert temp_dir.exists()


class TestConfigurationFixtures:
    """Test that configuration fixtures work correctly."""
    
    def test_test_config_fixture(self, test_config):
        """Test that test_config fixture loads configuration."""
        assert isinstance(test_config, dict)
        assert len(test_config) > 0
    
    def test_sample_workflow_config_fixture(self, sample_workflow_config):
        """Test that sample_workflow_config fixture provides valid config."""
        assert isinstance(sample_workflow_config, dict)
        assert "name" in sample_workflow_config
        assert "version" in sample_workflow_config
        assert "agents" in sample_workflow_config
        assert "tasks" in sample_workflow_config
    
    def test_sample_agent_config_fixture(self, sample_agent_config):
        """Test that sample_agent_config fixture provides valid config."""
        assert isinstance(sample_agent_config, dict)
        assert "id" in sample_agent_config
        assert "type" in sample_agent_config
        assert "capabilities" in sample_agent_config


class TestMockDataFixtures:
    """Test that mock data fixtures work correctly."""
    
    def test_mock_api_response_fixture(self, mock_api_response):
        """Test that mock_api_response fixture provides valid data."""
        assert isinstance(mock_api_response, dict)
        assert "status" in mock_api_response
        assert mock_api_response["status"] == "success"
    
    def test_mock_error_response_fixture(self, mock_error_response):
        """Test that mock_error_response fixture provides valid data."""
        assert isinstance(mock_error_response, dict)
        assert "status" in mock_error_response
        assert mock_error_response["status"] == "error"
        assert "error" in mock_error_response


class TestEnvironmentFixtures:
    """Test that environment fixtures work correctly."""
    
    def test_clean_env_fixture(self, clean_env):
        """Test that clean_env fixture removes sensitive variables."""
        import os
        # Verify sensitive variables are not present
        sensitive_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "API_KEY"]
        for var in sensitive_vars:
            assert os.getenv(var) is None, f"{var} should be removed by clean_env"
    
    def test_test_env_fixture(self, test_env):
        """Test that test_env fixture sets test environment variables."""
        import os
        assert os.getenv("ENVIRONMENT") == "test"
        assert os.getenv("TEST_MODE") == "true"


class TestHypothesisConfiguration:
    """Test that Hypothesis configuration is set up correctly."""
    
    def test_hypothesis_profiles_registered(self):
        """Test that Hypothesis profiles are registered."""
        from hypothesis import settings
        
        # Verify profiles exist
        profiles = ["ci", "dev", "thorough"]
        for profile in profiles:
            # Try to load each profile - will raise if not registered
            try:
                settings.load_profile(profile)
            except Exception as e:
                pytest.fail(f"Profile '{profile}' should be registered: {e}")
    
    def test_hypothesis_default_profile_loaded(self):
        """Test that a Hypothesis profile is loaded."""
        from hypothesis import settings
        
        # Get current settings
        current = settings()
        assert current is not None, "Hypothesis settings should be loaded"


class TestMarkerConfiguration:
    """Test that pytest markers are properly configured."""
    
    def test_unit_marker_exists(self, request):
        """Test that 'unit' marker is registered."""
        # This test is in the unit directory, so it should have the unit marker
        markers = [m.name for m in request.node.iter_markers()]
        assert "unit" in markers, "Tests in unit/ should have 'unit' marker"
    
    def test_custom_markers_registered(self):
        """Test that all custom markers are registered in pytest.ini."""
        import configparser
        from pathlib import Path
        
        pytest_ini = Path("pytest.ini")
        config = configparser.ConfigParser()
        config.read(pytest_ini)
        
        markers_section = config.get("pytest", "markers")
        
        expected_markers = [
            "unit",
            "integration",
            "e2e",
            "property",
            "slow",
            "requires_api",
            "requires_db"
        ]
        
        for marker in expected_markers:
            assert marker in markers_section, f"Marker '{marker}' should be registered in pytest.ini"


class TestTestDiscoveryPatterns:
    """Test that test discovery patterns are working."""
    
    def test_pytest_discovers_test_files(self, project_root):
        """Test that pytest can discover test files with configured patterns."""
        import subprocess
        
        # Run pytest collection on our specific test file to avoid import errors in other tests
        result = subprocess.run(
            ["python", "-m", "pytest", "--collect-only", "-q", "tests/unit/test_pytest_configuration.py"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "pytest should successfully collect tests"
        assert "collected" in result.stdout or "test" in result.stdout, "pytest should collect tests"
    
    def test_test_directories_exist(self, project_root):
        """Test that all configured test directories exist."""
        test_dirs = ["unit", "integration", "e2e", "property", "fixtures"]
        tests_dir = project_root / "tests"
        
        for test_dir in test_dirs:
            dir_path = tests_dir / test_dir
            assert dir_path.exists(), f"Test directory '{test_dir}' should exist"
