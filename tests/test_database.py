"""
Unit tests for database initialization and schema management.
"""

import unittest
import asyncio
import aiosqlite
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from agentic_sdlc.orchestration.api_model_management.database import (
    DatabaseManager,
    initialize_database,
    CURRENT_SCHEMA_VERSION
)


class DatabaseTestCase(unittest.TestCase):
    """Base test case with async support and temp database."""
    
    def setUp(self):
        """Create temporary database for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.temp_db_path = self.temp_dir / "test.db"
    
    def tearDown(self):
        """Clean up temporary database."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def run_async(self, coro):
        """Helper to run async coroutines in tests."""
        return asyncio.run(coro)


class TestDatabaseInitialization(DatabaseTestCase):
    """Test database initialization."""
    
    def test_database_initialization(self):
        """Test that database initializes with all required tables."""
        async def test():
            manager = DatabaseManager(self.temp_db_path)
            await manager.initialize()
            
            # Verify all tables exist
            self.assertTrue(await manager.verify_schema())
            
            # Verify schema version is set
            async with aiosqlite.connect(self.temp_db_path) as db:
                cursor = await db.execute("SELECT version FROM schema_version")
                row = await cursor.fetchone()
                self.assertEqual(row[0], CURRENT_SCHEMA_VERSION)
        
        self.run_async(test())
    
    def test_database_idempotent_initialization(self):
        """Test that initializing database multiple times is safe."""
        async def test():
            manager = DatabaseManager(self.temp_db_path)
            
            # Initialize twice
            await manager.initialize()
            await manager.initialize()
            
            # Should still have valid schema
            self.assertTrue(await manager.verify_schema())
        
        self.run_async(test())
    
    def test_initialize_database_helper(self):
        """Test initialize_database helper function."""
        async def test():
            manager = await initialize_database(self.temp_db_path)
            
            self.assertIsInstance(manager, DatabaseManager)
            self.assertTrue(await manager.verify_schema())
        
        self.run_async(test())


class TestTableStructures(DatabaseTestCase):
    """Test database table structures."""
    
    def test_cost_records_table_structure(self):
        """Test cost_records table has correct structure."""
        async def test():
            manager = DatabaseManager(self.temp_db_path)
            await manager.initialize()
            
            async with aiosqlite.connect(self.temp_db_path) as db:
                # Check table exists
                cursor = await db.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='cost_records'
                """)
                self.assertIsNotNone(await cursor.fetchone())
                
                # Check columns
                cursor = await db.execute("PRAGMA table_info(cost_records)")
                columns = {row[1] for row in await cursor.fetchall()}
                expected_columns = {
                    'id', 'timestamp', 'model_id', 'agent_type', 
                    'task_id', 'input_tokens', 'output_tokens', 'cost'
                }
                self.assertEqual(columns, expected_columns)
                
                # Check indexes exist
                cursor = await db.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='index' AND tbl_name='cost_records'
                """)
                indexes = {row[0] for row in await cursor.fetchall()}
                self.assertIn('idx_cost_timestamp', indexes)
                self.assertIn('idx_cost_model_id', indexes)
                self.assertIn('idx_cost_agent_type', indexes)
        
        self.run_async(test())
    
    def test_performance_records_table_structure(self):
        """Test performance_records table has correct structure."""
        async def test():
            manager = DatabaseManager(self.temp_db_path)
            await manager.initialize()
            
            async with aiosqlite.connect(self.temp_db_path) as db:
                # Check table exists
                cursor = await db.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='performance_records'
                """)
                self.assertIsNotNone(await cursor.fetchone())
                
                # Check columns
                cursor = await db.execute("PRAGMA table_info(performance_records)")
                columns = {row[1] for row in await cursor.fetchall()}
                expected_columns = {
                    'id', 'timestamp', 'model_id', 'agent_type', 
                    'task_id', 'latency_ms', 'success', 'quality_score'
                }
                self.assertEqual(columns, expected_columns)
        
        self.run_async(test())
    
    def test_cached_responses_table_structure(self):
        """Test cached_responses table has correct structure."""
        async def test():
            manager = DatabaseManager(self.temp_db_path)
            await manager.initialize()
            
            async with aiosqlite.connect(self.temp_db_path) as db:
                # Check table exists
                cursor = await db.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='cached_responses'
                """)
                self.assertIsNotNone(await cursor.fetchone())
                
                # Check columns
                cursor = await db.execute("PRAGMA table_info(cached_responses)")
                columns = {row[1] for row in await cursor.fetchall()}
                expected_columns = {
                    'cache_key', 'model_id', 'request_hash', 'response_data',
                    'cached_at', 'expires_at', 'hit_count', 'last_accessed'
                }
                self.assertEqual(columns, expected_columns)
        
        self.run_async(test())
    
    def test_health_checks_table_structure(self):
        """Test health_checks table has correct structure."""
        async def test():
            manager = DatabaseManager(self.temp_db_path)
            await manager.initialize()
            
            async with aiosqlite.connect(self.temp_db_path) as db:
                # Check table exists
                cursor = await db.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='health_checks'
                """)
                self.assertIsNotNone(await cursor.fetchone())
                
                # Check columns
                cursor = await db.execute("PRAGMA table_info(health_checks)")
                columns = {row[1] for row in await cursor.fetchall()}
                expected_columns = {
                    'id', 'timestamp', 'model_id', 'is_available',
                    'response_time_ms', 'error_message'
                }
                self.assertEqual(columns, expected_columns)
        
        self.run_async(test())
    
    def test_rate_limit_events_table_structure(self):
        """Test rate_limit_events table has correct structure."""
        async def test():
            manager = DatabaseManager(self.temp_db_path)
            await manager.initialize()
            
            async with aiosqlite.connect(self.temp_db_path) as db:
                # Check table exists
                cursor = await db.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='rate_limit_events'
                """)
                self.assertIsNotNone(await cursor.fetchone())
                
                # Check columns
                cursor = await db.execute("PRAGMA table_info(rate_limit_events)")
                columns = {row[1] for row in await cursor.fetchall()}
                expected_columns = {
                    'id', 'timestamp', 'model_id', 'event_type', 'reset_time'
                }
                self.assertEqual(columns, expected_columns)
        
        self.run_async(test())
    
    def test_failover_events_table_structure(self):
        """Test failover_events table has correct structure."""
        async def test():
            manager = DatabaseManager(self.temp_db_path)
            await manager.initialize()
            
            async with aiosqlite.connect(self.temp_db_path) as db:
                # Check table exists
                cursor = await db.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='failover_events'
                """)
                self.assertIsNotNone(await cursor.fetchone())
                
                # Check columns
                cursor = await db.execute("PRAGMA table_info(failover_events)")
                columns = {row[1] for row in await cursor.fetchall()}
                expected_columns = {
                    'id', 'timestamp', 'original_model', 'alternative_model',
                    'reason', 'task_id'
                }
                self.assertEqual(columns, expected_columns)
        
        self.run_async(test())


class TestDatabaseOperations(DatabaseTestCase):
    """Test database operations."""
    
    def test_cleanup_old_records(self):
        """Test cleanup of old records."""
        async def test():
            manager = DatabaseManager(self.temp_db_path)
            await manager.initialize()
            
            # Insert some test records
            async with aiosqlite.connect(self.temp_db_path) as db:
                # Insert old record (100 days ago)
                await db.execute("""
                    INSERT INTO cost_records 
                    (timestamp, model_id, agent_type, task_id, input_tokens, output_tokens, cost)
                    VALUES (datetime('now', '-100 days'), 'test-model', 'test-agent', 'task-1', 100, 50, 0.5)
                """)
                
                # Insert recent record
                await db.execute("""
                    INSERT INTO cost_records 
                    (timestamp, model_id, agent_type, task_id, input_tokens, output_tokens, cost)
                    VALUES (datetime('now'), 'test-model', 'test-agent', 'task-2', 100, 50, 0.5)
                """)
                
                await db.commit()
            
            # Cleanup records older than 90 days
            deleted_count = await manager.cleanup_old_records('cost_records', days_to_keep=90)
            
            # Should have deleted 1 record
            self.assertEqual(deleted_count, 1)
            
            # Verify only recent record remains
            async with aiosqlite.connect(self.temp_db_path) as db:
                cursor = await db.execute("SELECT COUNT(*) FROM cost_records")
                row = await cursor.fetchone()
                self.assertEqual(row[0], 1)
        
        self.run_async(test())
    
    def test_get_connection(self):
        """Test getting a database connection."""
        async def test():
            manager = DatabaseManager(self.temp_db_path)
            await manager.initialize()
            
            conn = await manager.get_connection()
            self.assertIsInstance(conn, aiosqlite.Connection)
            
            # Verify connection works
            cursor = await conn.execute("SELECT 1")
            row = await cursor.fetchone()
            self.assertEqual(row[0], 1)
            
            await conn.close()
        
        self.run_async(test())
    
    def test_verify_schema_missing_tables(self):
        """Test schema verification fails when tables are missing."""
        async def test():
            # Create database without initializing
            async with aiosqlite.connect(self.temp_db_path) as db:
                await db.execute("CREATE TABLE dummy (id INTEGER)")
                await db.commit()
            
            manager = DatabaseManager(self.temp_db_path)
            
            # Should fail verification
            self.assertFalse(await manager.verify_schema())
        
        self.run_async(test())


if __name__ == "__main__":
    unittest.main()
