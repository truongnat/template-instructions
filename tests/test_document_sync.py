"""
Unit tests for Neo4j Document Sync functionality.
Tests document parsing, metadata extraction, and sync operations.
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
    from tools.knowledge_graph.document_sync import DocumentSyncNeo4j, find_documents, DOCUMENT_TYPES
except ImportError:
    try:
        # Alternate import path
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / "tools" / "knowledge_graph"))
        from document_sync import DocumentSyncNeo4j, find_documents, DOCUMENT_TYPES
    except ImportError:
        DocumentSyncNeo4j = None
        find_documents = None
        DOCUMENT_TYPES = {}


class TestDocumentParsing:
    """Test document parsing functionality"""
    
    @pytest.fixture
    def sample_document_content(self):
        """Sample markdown document with frontmatter"""
        return """---
title: Test Project Plan
author: @PM
date: 2026-01-02
category: planning
---

# Test Project Plan

## Overview
This is a test document.

## References
- [Related Doc](./other-doc.md)

#planning #test
"""
    
    @pytest.fixture
    def mock_file(self, tmp_path, sample_document_content):
        """Create a temporary test file"""
        doc_path = tmp_path / "docs" / "sprints" / "sprint-1" / "Project-Plan-v1.md"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(sample_document_content, encoding='utf-8')
        return doc_path
    
    @pytest.mark.skipif(DocumentSyncNeo4j is None, reason="DocumentSyncNeo4j not available")
    def test_generate_document_id(self, mock_file):
        """Test document ID generation is consistent"""
        with patch.object(DocumentSyncNeo4j, '__init__', lambda x, *args, **kwargs: None):
            sync = DocumentSyncNeo4j.__new__(DocumentSyncNeo4j)
            
            id1 = sync.generate_document_id(mock_file)
            id2 = sync.generate_document_id(mock_file)
            
            assert id1 == id2
            assert len(id1) == 16  # SHA256 truncated to 16 chars
    
    @pytest.mark.skipif(DocumentSyncNeo4j is None, reason="DocumentSyncNeo4j not available")
    def test_extract_version(self):
        """Test version extraction from filenames"""
        with patch.object(DocumentSyncNeo4j, '__init__', lambda x, *args, **kwargs: None):
            sync = DocumentSyncNeo4j.__new__(DocumentSyncNeo4j)
            
            assert sync.extract_version("Project-Plan-v1.md") == (1, "-v1")
            assert sync.extract_version("Project-Plan-v2.md") == (2, "-v2")
            assert sync.extract_version("Project-Plan.md") == (1, None)
            assert sync.extract_version("Report_v10.md") == (10, "_v10")
    
    @pytest.mark.skipif(DocumentSyncNeo4j is None, reason="DocumentSyncNeo4j not available")
    def test_extract_sprint(self, tmp_path):
        """Test sprint extraction from file path"""
        with patch.object(DocumentSyncNeo4j, '__init__', lambda x, *args, **kwargs: None):
            sync = DocumentSyncNeo4j.__new__(DocumentSyncNeo4j)
            
            path1 = tmp_path / "docs" / "sprints" / "sprint-1" / "plan.md"
            path2 = tmp_path / "docs" / "sprints" / "sprint-5" / "report.md"
            path3 = tmp_path / "docs" / "general" / "readme.md"
            
            assert sync.extract_sprint(path1) == "sprint-1"
            assert sync.extract_sprint(path2) == "sprint-5"
            assert sync.extract_sprint(path3) is None
    
    @pytest.mark.skipif(DocumentSyncNeo4j is None, reason="DocumentSyncNeo4j not available")
    def test_parse_frontmatter(self, sample_document_content):
        """Test YAML frontmatter parsing"""
        with patch.object(DocumentSyncNeo4j, '__init__', lambda x, *args, **kwargs: None):
            sync = DocumentSyncNeo4j.__new__(DocumentSyncNeo4j)
            
            metadata = sync.parse_frontmatter(sample_document_content)
            
            assert metadata['title'] == 'Test Project Plan'
            assert metadata['author'] == '@PM'
            assert metadata['date'] == '2026-01-02'
            assert metadata['category'] == 'planning'
    
    @pytest.mark.skipif(DocumentSyncNeo4j is None, reason="DocumentSyncNeo4j not available")
    def test_determine_document_type(self, tmp_path):
        """Test document type determination"""
        with patch.object(DocumentSyncNeo4j, '__init__', lambda x, *args, **kwargs: None):
            sync = DocumentSyncNeo4j.__new__(DocumentSyncNeo4j)
            
            assert sync.determine_document_type(Path("KB-2026-01-01-test.md")) == "KBEntry"
            assert sync.determine_document_type(Path("Project-Plan-v1.md")) == "Plan"
            assert sync.determine_document_type(Path("Phase-Report-Sprint-1.md")) == "Report"
            assert sync.determine_document_type(Path("Backend-Spec-v1.md")) == "Artifact"
    
    @pytest.mark.skipif(DocumentSyncNeo4j is None, reason="DocumentSyncNeo4j not available")
    def test_chunk_content(self):
        """Test content chunking for large documents"""
        with patch.object(DocumentSyncNeo4j, '__init__', lambda x, *args, **kwargs: None):
            sync = DocumentSyncNeo4j.__new__(DocumentSyncNeo4j)
            
            content = """
## Section 1
This is section one with some content.

## Section 2
This is section two with more content.

## Section 3
This is section three with even more content.
"""
            chunks = sync.chunk_content(content, chunk_size=100)
            
            assert len(chunks) >= 1
            assert all('header' in chunk for chunk in chunks)
            assert all('content' in chunk for chunk in chunks)


class TestDocumentTypes:
    """Test document type configurations"""
    
    def test_document_types_defined(self):
        """Test that all expected document types are defined"""
        expected_types = ['plans', 'reports', 'artifacts', 'workflows', 'knowledge', 'conversations']
        
        for doc_type in expected_types:
            assert doc_type in DOCUMENT_TYPES
            assert 'patterns' in DOCUMENT_TYPES[doc_type]
            assert 'label' in DOCUMENT_TYPES[doc_type]
            assert 'directories' in DOCUMENT_TYPES[doc_type]


class TestFindDocuments:
    """Test document discovery functionality"""
    
    @pytest.fixture
    def project_structure(self, tmp_path):
        """Create a mock project structure"""
        # Create directories
        (tmp_path / "docs" / "sprints" / "sprint-1" / "plans").mkdir(parents=True)
        (tmp_path / "docs" / "sprints" / "sprint-1" / "reports").mkdir(parents=True)
        (tmp_path / ".agent" / "workflows").mkdir(parents=True)
        (tmp_path / ".agent" / "knowledge-base" / "features").mkdir(parents=True)
        
        # Create sample files
        (tmp_path / "docs" / "sprints" / "sprint-1" / "plans" / "Project-Plan-v1.md").write_text("# Plan", encoding='utf-8')
        (tmp_path / "docs" / "sprints" / "sprint-1" / "reports" / "Phase-Report.md").write_text("# Report", encoding='utf-8')
        (tmp_path / ".agent" / "workflows" / "dev.md").write_text("# Dev Workflow", encoding='utf-8')
        (tmp_path / ".agent" / "knowledge-base" / "features" / "KB-2026-01-01-test.md").write_text("# KB", encoding='utf-8')
        
        return tmp_path
    
    @pytest.mark.skipif(find_documents is None, reason="find_documents not available")
    def test_find_all_documents(self, project_structure):
        """Test finding all documents"""
        documents = find_documents(project_structure, ['all'])
        
        assert len(documents) >= 1
    
    @pytest.mark.skipif(find_documents is None, reason="find_documents not available")
    def test_find_specific_type(self, project_structure):
        """Test finding specific document types"""
        documents = find_documents(project_structure, ['knowledge'])
        
        kb_files = [d for d in documents if 'KB-' in d.name]
        assert len(kb_files) >= 1


class TestNeo4jIntegration:
    """Integration tests for Neo4j operations (requires Neo4j connection)"""
    
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
    
    @pytest.mark.skipif(DocumentSyncNeo4j is None, reason="DocumentSyncNeo4j not available")
    @pytest.mark.integration
    def test_neo4j_connection(self, neo4j_credentials):
        """Test Neo4j connection (integration)"""
        if not all(neo4j_credentials.values()):
            pytest.skip("Neo4j credentials not available")
        
        sync = DocumentSyncNeo4j(**neo4j_credentials)
        try:
            # Connection should not raise
            sync.create_document_schema()
        finally:
            sync.close()
    
    @pytest.mark.skipif(DocumentSyncNeo4j is None, reason="DocumentSyncNeo4j not available")
    @pytest.mark.integration
    def test_get_stats(self, neo4j_credentials):
        """Test getting document statistics (integration)"""
        if not all(neo4j_credentials.values()):
            pytest.skip("Neo4j credentials not available")
        
        sync = DocumentSyncNeo4j(**neo4j_credentials)
        try:
            stats = sync.get_document_stats()
            assert 'documents' in stats
            assert 'plans' in stats
            assert 'reports' in stats
        finally:
            sync.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
