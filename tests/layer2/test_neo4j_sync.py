
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "tools"))

def test_sync_scripts_import():
    try:
        from knowledge_graph import brain_parallel
        from knowledge_graph import sync_skills_to_neo4j
        assert brain_parallel is not None
        assert sync_skills_to_neo4j is not None
    except ImportError:
        pytest.fail("Failed to import Neo4j sync scripts")

def test_brain_parallel_args():
    from knowledge_graph import brain_parallel
    # Check if argparse setup function exists or main block is structured
    # This is a basic smoke test
    assert hasattr(brain_parallel, 'main') or hasattr(brain_parallel, 'sync_all')
