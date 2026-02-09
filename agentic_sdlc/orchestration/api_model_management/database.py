"""
Database initialization and migration utilities for API Model Management.

This module provides database schema creation, migration utilities, and
connection management for SQLite database used by the API Model Management system.
"""

import aiosqlite
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime


logger = logging.getLogger(__name__)


# Database schema version for migration tracking
CURRENT_SCHEMA_VERSION = 1


class DatabaseManager:
    """Manages database initialization, migrations, and connections."""
    
    def __init__(self, db_path: Path):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self) -> None:
        """
        Initialize database with all required tables.
        
        Creates all tables if they don't exist and sets up indexes.
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Enable foreign keys
            await db.execute("PRAGMA foreign_keys = ON")
            
            # Create schema version table
            await self._create_schema_version_table(db)
            
            # Check current schema version
            current_version = await self._get_schema_version(db)
            
            if current_version == 0:
                # Fresh database - create all tables
                logger.info("Initializing fresh database")
                await self._create_all_tables(db)
                await self._set_schema_version(db, CURRENT_SCHEMA_VERSION)
            elif current_version < CURRENT_SCHEMA_VERSION:
                # Run migrations
                logger.info(f"Migrating database from version {current_version} to {CURRENT_SCHEMA_VERSION}")
                await self._run_migrations(db, current_version, CURRENT_SCHEMA_VERSION)
            else:
                logger.info(f"Database schema is up to date (version {current_version})")
            
            await db.commit()
    
    async def _create_schema_version_table(self, db: aiosqlite.Connection) -> None:
        """Create schema version tracking table."""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at DATETIME NOT NULL
            )
        """)
    
    async def _get_schema_version(self, db: aiosqlite.Connection) -> int:
        """Get current schema version."""
        cursor = await db.execute("SELECT MAX(version) FROM schema_version")
        row = await cursor.fetchone()
        return row[0] if row[0] is not None else 0
    
    async def _set_schema_version(self, db: aiosqlite.Connection, version: int) -> None:
        """Set schema version."""
        await db.execute(
            "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
            (version, datetime.now())
        )
    
    async def _create_all_tables(self, db: aiosqlite.Connection) -> None:
        """Create all database tables."""
        await self._create_cost_records_table(db)
        await self._create_performance_records_table(db)
        await self._create_cached_responses_table(db)
        await self._create_health_checks_table(db)
        await self._create_rate_limit_events_table(db)
        await self._create_failover_events_table(db)
    
    async def _create_cost_records_table(self, db: aiosqlite.Connection) -> None:
        """Create cost_records table for cost tracking."""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cost_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                model_id TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                task_id TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                cost REAL NOT NULL
            )
        """)
        
        # Create indexes for efficient querying
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_cost_timestamp 
            ON cost_records(timestamp)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_cost_model_id 
            ON cost_records(model_id)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_cost_agent_type 
            ON cost_records(agent_type)
        """)
        
        logger.debug("Created cost_records table")
    
    async def _create_performance_records_table(self, db: aiosqlite.Connection) -> None:
        """Create performance_records table for performance monitoring."""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS performance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                model_id TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                task_id TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                success BOOLEAN NOT NULL,
                quality_score REAL
            )
        """)
        
        # Create indexes for efficient querying
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_perf_timestamp 
            ON performance_records(timestamp)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_perf_model_id 
            ON performance_records(model_id)
        """)
        
        logger.debug("Created performance_records table")
    
    async def _create_cached_responses_table(self, db: aiosqlite.Connection) -> None:
        """Create cached_responses table for response caching."""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cached_responses (
                cache_key TEXT PRIMARY KEY,
                model_id TEXT NOT NULL,
                request_hash TEXT NOT NULL,
                response_data TEXT NOT NULL,
                cached_at DATETIME NOT NULL,
                expires_at DATETIME NOT NULL,
                hit_count INTEGER DEFAULT 0,
                last_accessed DATETIME NOT NULL
            )
        """)
        
        # Create indexes for efficient querying and eviction
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_expires_at 
            ON cached_responses(expires_at)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_last_accessed 
            ON cached_responses(last_accessed)
        """)
        
        logger.debug("Created cached_responses table")
    
    async def _create_health_checks_table(self, db: aiosqlite.Connection) -> None:
        """Create health_checks table for health check history."""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS health_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                model_id TEXT NOT NULL,
                is_available BOOLEAN NOT NULL,
                response_time_ms REAL,
                error_message TEXT
            )
        """)
        
        # Create indexes for efficient querying
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_health_timestamp 
            ON health_checks(timestamp)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_health_model_id 
            ON health_checks(model_id)
        """)
        
        logger.debug("Created health_checks table")
    
    async def _create_rate_limit_events_table(self, db: aiosqlite.Connection) -> None:
        """Create rate_limit_events table for rate limit tracking."""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS rate_limit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                model_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                reset_time DATETIME
            )
        """)
        
        # Create indexes for efficient querying
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_ratelimit_timestamp 
            ON rate_limit_events(timestamp)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_ratelimit_model_id 
            ON rate_limit_events(model_id)
        """)
        
        logger.debug("Created rate_limit_events table")
    
    async def _create_failover_events_table(self, db: aiosqlite.Connection) -> None:
        """Create failover_events table for failover tracking."""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS failover_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                original_model TEXT NOT NULL,
                alternative_model TEXT NOT NULL,
                reason TEXT NOT NULL,
                task_id TEXT NOT NULL
            )
        """)
        
        # Create indexes for efficient querying
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_failover_timestamp 
            ON failover_events(timestamp)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_failover_original_model 
            ON failover_events(original_model)
        """)
        
        logger.debug("Created failover_events table")
    
    async def _run_migrations(
        self, 
        db: aiosqlite.Connection, 
        from_version: int, 
        to_version: int
    ) -> None:
        """
        Run database migrations from one version to another.
        
        Args:
            db: Database connection
            from_version: Current schema version
            to_version: Target schema version
        """
        # Migration logic for future schema changes
        # For now, we only have version 1
        if from_version < 1 <= to_version:
            await self._migrate_to_v1(db)
            await self._set_schema_version(db, 1)
    
    async def _migrate_to_v1(self, db: aiosqlite.Connection) -> None:
        """Migrate to schema version 1."""
        # This is the initial schema, so just create all tables
        await self._create_all_tables(db)
        logger.info("Migrated to schema version 1")
    
    async def verify_schema(self) -> bool:
        """
        Verify that all required tables exist.
        
        Returns:
            True if all tables exist, False otherwise
        """
        required_tables = [
            'cost_records',
            'performance_records',
            'cached_responses',
            'health_checks',
            'rate_limit_events',
            'failover_events',
            'schema_version'
        ]
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            existing_tables = {row[0] for row in await cursor.fetchall()}
            
            missing_tables = set(required_tables) - existing_tables
            
            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False
            
            logger.info("All required tables exist")
            return True
    
    async def get_connection(self) -> aiosqlite.Connection:
        """
        Get a database connection.
        
        Returns:
            Database connection
        """
        return await aiosqlite.connect(self.db_path)
    
    async def cleanup_old_records(
        self, 
        table: str, 
        days_to_keep: int = 90
    ) -> int:
        """
        Clean up old records from a table.
        
        Args:
            table: Table name to clean up
            days_to_keep: Number of days of records to keep
            
        Returns:
            Number of records deleted
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"""
                DELETE FROM {table}
                WHERE timestamp < datetime('now', '-{days_to_keep} days')
            """)
            deleted_count = cursor.rowcount
            await db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old records from {table}")
            return deleted_count


async def initialize_database(db_path: Path) -> DatabaseManager:
    """
    Initialize database and return manager instance.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        Initialized DatabaseManager instance
    """
    manager = DatabaseManager(db_path)
    await manager.initialize()
    return manager
