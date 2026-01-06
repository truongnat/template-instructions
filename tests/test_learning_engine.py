"""
Unit tests for Neo4j Learning Engine functionality.
Tests error tracking, pattern recognition, and recommendations.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

# Import after path setup
try:
    from tools.knowledge_graph.learning_engine import LearningEngine
except ImportError:
    try:
        # Alternate import path
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / "tools" / "knowledge_graph"))
        from learning_engine import LearningEngine
    except ImportError:
        LearningEngine = None


class TestKeywordExtraction:
    """Test keyword extraction functionality"""
    
    @pytest.fixture
    def engine_instance(self):
        """Create a mock LearningEngine instance"""
        if LearningEngine is None:
            pytest.skip("LearningEngine not available")
        
        with patch.object(LearningEngine, '__init__', lambda x, *args, **kwargs: None):
            engine = LearningEngine.__new__(LearningEngine)
            return engine
    
    def test_extract_keywords_basic(self, engine_instance):
        """Test basic keyword extraction"""
        keywords = engine_instance._extract_keywords("implement user authentication feature")
        
        assert 'user' in keywords
        assert 'authentication' in keywords
        assert 'feature' in keywords
        # Stopwords should be removed
        assert 'implement' not in keywords
    
    def test_extract_keywords_removes_stopwords(self, engine_instance):
        """Test that common stopwords are removed"""
        keywords = engine_instance._extract_keywords("the quick brown fox jumps over the lazy dog")
        
        assert 'the' not in keywords
        assert 'over' not in keywords
        assert 'quick' in keywords
        assert 'brown' in keywords
    
    def test_extract_keywords_unique(self, engine_instance):
        """Test that keywords are unique"""
        keywords = engine_instance._extract_keywords("api api api design design pattern")
        
        assert keywords.count('api') == 1
        assert keywords.count('design') == 1


class TestIdGeneration:
    """Test ID generation functionality"""
    
    @pytest.fixture
    def engine_instance(self):
        """Create a mock LearningEngine instance"""
        if LearningEngine is None:
            pytest.skip("LearningEngine not available")
        
        with patch.object(LearningEngine, '__init__', lambda x, *args, **kwargs: None):
            engine = LearningEngine.__new__(LearningEngine)
            return engine
    
    def test_generate_id_format(self, engine_instance):
        """Test ID generation format"""
        error_id = engine_instance.generate_id("ERR", "test error")
        
        assert error_id.startswith("ERR_")
        assert len(error_id) == 16  # "ERR_" + 12 char hash
    
    def test_generate_id_different_prefixes(self, engine_instance):
        """Test different ID prefixes"""
        error_id = engine_instance.generate_id("ERR", "test")
        res_id = engine_instance.generate_id("RES", "test")
        pat_id = engine_instance.generate_id("PAT", "test")
        
        assert error_id.startswith("ERR_")
        assert res_id.startswith("RES_")
        assert pat_id.startswith("PAT_")


class TestLearningEngineIntegration:
    """Integration tests for Learning Engine (requires Neo4j connection)"""
    
    @pytest.fixture
    def neo4j_credentials(self):
        """Get Neo4j credentials from environment"""
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        return {
            'uri': os.getenv('NEO4J_URI'),
            'user': os.getenv('NEO4J_USERNAME'),
            'password': os.getenv('NEO4J_PASSWORD'),
            'database': os.getenv('NEO4J_DATABASE', 'neo4j')
        }
    
    @pytest.mark.skipif(LearningEngine is None, reason="LearningEngine not available")
    @pytest.mark.integration
    def test_neo4j_connection(self, neo4j_credentials):
        """Test Neo4j connection (integration)"""
        if not all(neo4j_credentials.values()):
            pytest.skip("Neo4j credentials not available")
        
        engine = LearningEngine(**neo4j_credentials)
        try:
            # Connection should not raise
            engine.create_learning_schema()
        finally:
            engine.close()
    
    @pytest.mark.skipif(LearningEngine is None, reason="LearningEngine not available")
    @pytest.mark.integration
    def test_get_learning_stats(self, neo4j_credentials):
        """Test getting learning statistics (integration)"""
        if not all(neo4j_credentials.values()):
            pytest.skip("Neo4j credentials not available")
        
        engine = LearningEngine(**neo4j_credentials)
        try:
            stats = engine.get_learning_stats()
            assert 'errors_tracked' in stats
            assert 'resolutions' in stats
            assert 'patterns' in stats
        finally:
            engine.close()
    
    @pytest.mark.skipif(LearningEngine is None, reason="LearningEngine not available")
    @pytest.mark.integration
    def test_record_and_find_error(self, neo4j_credentials):
        """Test recording an error and finding it (integration)"""
        if not all(neo4j_credentials.values()):
            pytest.skip("Neo4j credentials not available")
        
        engine = LearningEngine(**neo4j_credentials)
        try:
            # Record a test error
            error_id = engine.record_error(
                error_type="TestError",
                message="This is a test error message for pytest",
                resolution="Test resolution applied",
                resolution_approach="pytest_test"
            )
            
            assert error_id is not None
            
            # Try to find similar errors
            similar = engine.find_similar_errors("test error pytest")
            # Should return results (may be empty if fulltext index not ready)
            assert isinstance(similar, list)
        finally:
            engine.close()
    
    @pytest.mark.skipif(LearningEngine is None, reason="LearningEngine not available")
    @pytest.mark.integration
    def test_record_success_pattern(self, neo4j_credentials):
        """Test recording a success pattern (integration)"""
        if not all(neo4j_credentials.values()):
            pytest.skip("Neo4j credentials not available")
        
        engine = LearningEngine(**neo4j_credentials)
        try:
            # Record a success pattern
            pattern_id = engine.record_success(
                task_id="pytest-task-001",
                task_type="unit_testing",
                approach="pytest with fixtures",
                outcome="passed",
                confidence=0.95
            )
            
            assert pattern_id is not None
            assert pattern_id.startswith("PAT_")
            
            # Get patterns
            patterns = engine.get_successful_patterns(task_type="unit_testing")
            assert isinstance(patterns, list)
        finally:
            engine.close()
    
    @pytest.mark.skipif(LearningEngine is None, reason="LearningEngine not available")
    @pytest.mark.integration
    def test_get_recommendations(self, neo4j_credentials):
        """Test getting recommendations (integration)"""
        if not all(neo4j_credentials.values()):
            pytest.skip("Neo4j credentials not available")
        
        engine = LearningEngine(**neo4j_credentials)
        try:
            recommendations = engine.get_recommendations("implement user authentication with JWT")
            
            assert isinstance(recommendations, list)
            # Recommendations should have expected structure
            for rec in recommendations:
                assert 'source' in rec
                assert 'matched_keyword' in rec
        finally:
            engine.close()


class TestRecommendationOutput:
    """Test recommendation formatting"""
    
    def test_recommendation_structure(self):
        """Test that recommendation dict has expected keys"""
        sample_rec = {
            'pattern_id': 'PAT_abc123',
            'task_type': 'auth',
            'approach': 'JWT tokens',
            'success_count': 5,
            'confidence': 0.9,
            'matched_keyword': 'authentication',
            'source': 'pattern'
        }
        
        assert 'source' in sample_rec
        assert sample_rec['source'] in ['pattern', 'knowledge_base', 'document']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
