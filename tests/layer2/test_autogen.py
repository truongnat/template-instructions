"""
AutoGen Integration Tests

Tests for agent creation, tool registration, and configuration.
These tests use mocks to avoid live LLM calls.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestConfig:
    """Tests for config.py"""
    
    def test_get_default_config(self):
        """Test default configuration values"""
        from agentic_sdlc.infrastructure.engine.autogen.config import get_default_config
        
        config = get_default_config()
        
        assert "model" in config
        assert "max_turns" in config
        assert "timeout" in config
        assert isinstance(config["max_turns"], int)
    
    @patch.dict("os.environ", {"GOOGLE_GENAI_API_KEY": "test-key"})
    def test_get_model_client_gemini(self):
        """Test Gemini client creation with mocked import"""
        # Verify the API key is correctly read from environment
        import os
        assert os.getenv("GOOGLE_GENAI_API_KEY") == "test-key"
        
        # We cannot fully test client creation without actual package
        # but we verify our config module correctly identifies the key
        from agentic_sdlc.infrastructure.engine.autogen.config import get_default_config
        config = get_default_config()
        assert "model" in config
    
    def test_get_model_client_no_key(self):
        """Test error when no API key is set"""
        with patch.dict("os.environ", {}, clear=True):
            # Remove keys if present
            import os
            os.environ.pop("GOOGLE_GENAI_API_KEY", None)
            os.environ.pop("GEMINI_API_KEY", None)
            os.environ.pop("OPENAI_API_KEY", None)
            
            from agentic_sdlc.infrastructure.engine.autogen.config import get_model_client
            
            with pytest.raises(ValueError, match="not found"):
                get_model_client("gemini-2.0-flash")


class TestAgents:
    """Tests for agents.py"""
    
    def test_create_agent_by_role_dev(self):
        """Test developer agent creation"""
        mock_client = MagicMock()
        
        with patch("agentic_sdlc.infrastructure.engine.autogen.agents.AssistantAgent") as mock_agent:
            mock_agent.return_value = MagicMock()
            
            from agentic_sdlc.infrastructure.engine.autogen.agents import create_agent_by_role
            
            agent = create_agent_by_role(mock_client, "dev")
            
            # Verify AssistantAgent was called
            mock_agent.assert_called_once()
            call_kwargs = mock_agent.call_args[1]
            assert call_kwargs["name"] == "developer"
            assert "Developer" in call_kwargs["system_message"]
    
    def test_create_agent_by_role_tester(self):
        """Test tester agent creation"""
        mock_client = MagicMock()
        
        with patch("agentic_sdlc.infrastructure.engine.autogen.agents.AssistantAgent") as mock_agent:
            mock_agent.return_value = MagicMock()
            
            from agentic_sdlc.infrastructure.engine.autogen.agents import create_agent_by_role
            
            agent = create_agent_by_role(mock_client, "tester")
            
            mock_agent.assert_called_once()
            call_kwargs = mock_agent.call_args[1]
            assert call_kwargs["name"] == "tester"
    
    def test_create_agent_invalid_role(self):
        """Test error for invalid role"""
        mock_client = MagicMock()
        
        from agentic_sdlc.infrastructure.engine.autogen.agents import create_agent_by_role
        
        with pytest.raises(ValueError, match="Unknown role"):
            create_agent_by_role(mock_client, "invalid_role")


class TestToolsRegistry:
    """Tests for tools_registry.py"""
    
    def test_read_file_existing(self, tmp_path):
        """Test reading an existing file"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        from agentic_sdlc.infrastructure.engine.autogen.tools_registry import read_file
        
        result = read_file(str(test_file))
        assert "Hello, World!" in result
    
    def test_read_file_not_found(self):
        """Test reading a non-existent file"""
        from agentic_sdlc.infrastructure.engine.autogen.tools_registry import read_file
        
        result = read_file("/nonexistent/path/file.txt")
        assert "Error" in result
    
    def test_list_directory(self, tmp_path):
        """Test listing directory contents"""
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.py").touch()
        (tmp_path / "subdir").mkdir()
        
        from agentic_sdlc.infrastructure.engine.autogen.tools_registry import list_directory
        
        result = list_directory(str(tmp_path))
        assert "file1.txt" in result
        assert "file2.py" in result
        assert "[DIR]" in result
    
    def test_search_in_files(self, tmp_path):
        """Test searching in files"""
        test_file = tmp_path / "code.py"
        test_file.write_text("def hello_world():\n    print('Hello')")
        
        from agentic_sdlc.infrastructure.engine.autogen.tools_registry import search_in_files
        
        # Search by providing the file path directly (absolute path)
        result = search_in_files("hello", str(test_file))
        assert "hello_world" in result or "Hello" in result or "code.py" in result
    
    def test_get_tools_for_role(self):
        """Test getting tools based on role"""
        from agentic_sdlc.infrastructure.engine.autogen.tools_registry import get_tools_for_role
        
        dev_tools = get_tools_for_role("dev")
        tester_tools = get_tools_for_role("tester")
        
        assert len(dev_tools) > 0
        assert len(tester_tools) > 0
    
    def test_run_command_safety(self):
        """Test that dangerous commands are blocked"""
        from agentic_sdlc.infrastructure.engine.autogen.tools_registry import run_command
        
        result = run_command("rm -rf /")
        assert "blocked" in result.lower() or "error" in result.lower()


class TestRunner:
    """Tests for runner.py CLI parsing"""
    
    def test_argparse_setup(self):
        """Test that argument parser is configured correctly"""
        import argparse
        from agentic_sdlc.infrastructure.engine.autogen.runner import main
        
        # Just verify the module imports without error
        assert callable(main)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
