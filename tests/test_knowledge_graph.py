#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Knowledge Graph Components

Tests for: Neo4j Query Construction, Graceful Failure handling
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock neo4j driver before importing module
sys.modules['neo4j'] = MagicMock()
sys.modules['dotenv'] = MagicMock()

from tools.intelligence.knowledge_graph.query_skills_neo4j import Neo4jSkillQuery

class TestNeo4jSkillQuery:
    """Tests for Neo4j Query Component."""
    
    @pytest.fixture
    def mock_driver(self):
        with patch('tools.intelligence.knowledge_graph.query_skills_neo4j.GraphDatabase') as mock_gd:
            mock_driver = MagicMock()
            mock_gd.driver.return_value = mock_driver
            yield mock_driver

    def test_init(self, mock_driver):
        """Test initialization connects to driver."""
        query = Neo4jSkillQuery("bolt://localhost", "user", "pass")
        assert query.driver == mock_driver

    def test_get_all_skills(self, mock_driver):
        """Test get_all_skills query execution."""
        query = Neo4jSkillQuery("uri", "u", "p")
        
        # Mock session and result
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        mock_result = [
            {"skill": "Python", "level": "expert", "kb_count": 5, "kb_entries": ["doc1"]}
        ]
        mock_session.run.return_value = mock_result
        
        skills = query.get_all_skills()
        
        assert len(skills) == 1
        assert skills[0]["skill"] == "Python"
        # Verify query structure
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args[0][0]
        assert "MATCH (s:Skill)" in call_args

    def test_search_skills(self, mock_driver):
        """Test search_skills query execution."""
        query = Neo4jSkillQuery("uri", "u", "p")
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        query.search_skills("java")
        
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        assert "toLower(s.name) CONTAINS" in call_args[0][0]
        assert call_args[1]["query"] == "java"

    def test_graceful_close(self, mock_driver):
        """Test driver closure."""
        query = Neo4jSkillQuery("uri", "u", "p")
        query.close()
        mock_driver.close.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
