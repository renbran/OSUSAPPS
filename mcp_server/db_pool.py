"""
Odoo 17 MCP Server - Database Connection Pooling

This module provides:
- PostgreSQL connection pooling for better performance
- Async database operations
- Connection lifecycle management
- Query result caching
- Transaction management
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Tuple
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
import time
import hashlib

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    logging.warning("asyncpg not available. Install with: pip install asyncpg")

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2 import pool as psycopg2_pool
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logging.warning("psycopg2 not available. Install with: pip install psycopg2-binary")

from async_utils import AsyncCache

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result of a database query."""
    rows: List[Dict[str, Any]]
    row_count: int
    duration: float
    cached: bool = False

    def __len__(self) -> int:
        return self.row_count

    def __iter__(self):
        return iter(self.rows)

    def __getitem__(self, index):
        return self.rows[index]


class AsyncDatabasePool:
    """
    Async PostgreSQL connection pool using asyncpg.
    Best for async operations with high performance.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "odoo",
        password: str = "odoo",
        min_size: int = 2,
        max_size: int = 10,
        command_timeout: float = 60.0
    ):
        if not ASYNCPG_AVAILABLE:
            raise ImportError("asyncpg is required for AsyncDatabasePool. Install with: pip install asyncpg")

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.min_size = min_size
        self.max_size = max_size
        self.command_timeout = command_timeout
        self._pool: Optional[asyncpg.Pool] = None
        self._cache = AsyncCache(ttl=300, max_size=100)
        self.logger = logger

    async def initialize(self) -> None:
        """Initialize the connection pool."""
        if self._pool is not None:
            self.logger.warning("Pool already initialized")
            return

        try:
            self._pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                min_size=self.min_size,
                max_size=self.max_size,
                command_timeout=self.command_timeout
            )
            self.logger.info(f"Database pool initialized (min={self.min_size}, max={self.max_size})")
        except Exception as e:
            self.logger.error(f"Failed to initialize database pool: {e}")
            raise

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            self.logger.info("Database pool closed")

    @asynccontextmanager
    async def acquire(self):
        """Acquire a connection from the pool."""
        if self._pool is None:
            await self.initialize()

        async with self._pool.acquire() as connection:
            yield connection

    async def execute(
        self,
        database: str,
        query: str,
        *args,
        use_cache: bool = True
    ) -> QueryResult:
        """
        Execute a SELECT query with optional caching.

        Args:
            database: Database name
            query: SQL query
            *args: Query parameters
            use_cache: Use query result caching

        Returns:
            QueryResult with rows and metadata
        """
        start_time = time.time()

        # Generate cache key
        cache_key = None
        if use_cache:
            cache_key = self._generate_cache_key(database, query, args)
            cached_result = await self._cache.get(cache_key)
            if cached_result is not None:
                self.logger.debug(f"Cache hit for query: {query[:50]}...")
                return QueryResult(
                    rows=cached_result,
                    row_count=len(cached_result),
                    duration=time.time() - start_time,
                    cached=True
                )

        try:
            if self._pool is None:
                await self.initialize()

            # Connect to specific database
            conn = await asyncpg.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=database,
                timeout=self.command_timeout
            )

            try:
                rows = await conn.fetch(query, *args)
                result_dicts = [dict(row) for row in rows]

                duration = time.time() - start_time
                self.logger.debug(f"Query executed in {duration:.3f}s: {query[:50]}...")

                # Cache result
                if use_cache and cache_key:
                    await self._cache.set(cache_key, result_dicts)

                return QueryResult(
                    rows=result_dicts,
                    row_count=len(result_dicts),
                    duration=duration,
                    cached=False
                )
            finally:
                await conn.close()

        except asyncpg.PostgresError as e:
            duration = time.time() - start_time
            self.logger.error(f"Query failed after {duration:.3f}s: {e}")
            raise
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Unexpected error after {duration:.3f}s: {e}")
            raise

    async def execute_many(
        self,
        database: str,
        queries: List[Tuple[str, tuple]]
    ) -> List[QueryResult]:
        """
        Execute multiple queries in parallel.

        Args:
            database: Database name
            queries: List of (query, args) tuples

        Returns:
            List of QueryResults
        """
        tasks = [
            self.execute(database, query, *args)
            for query, args in queries
        ]
        return await asyncio.gather(*tasks)

    def _generate_cache_key(self, database: str, query: str, args: tuple) -> str:
        """Generate cache key for query."""
        key_str = f"{database}:{query}:{args}"
        return hashlib.md5(key_str.encode()).hexdigest()

    async def invalidate_cache(self, database: Optional[str] = None) -> None:
        """Invalidate cache entries."""
        await self._cache.clear()


class SyncDatabasePool:
    """
    Synchronous PostgreSQL connection pool using psycopg2.
    For compatibility with synchronous code.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "odoo",
        password: str = "odoo",
        min_connections: int = 2,
        max_connections: int = 10
    ):
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 is required for SyncDatabasePool. Install with: pip install psycopg2-binary")

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.min_connections = min_connections
        self.max_connections = max_connections
        self._pools: Dict[str, psycopg2_pool.ThreadedConnectionPool] = {}
        self.logger = logger

    def _get_pool(self, database: str) -> psycopg2_pool.ThreadedConnectionPool:
        """Get or create connection pool for database."""
        if database not in self._pools:
            try:
                self._pools[database] = psycopg2_pool.ThreadedConnectionPool(
                    self.min_connections,
                    self.max_connections,
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=database
                )
                self.logger.info(f"Created connection pool for database: {database}")
            except Exception as e:
                self.logger.error(f"Failed to create connection pool for {database}: {e}")
                raise

        return self._pools[database]

    def execute_query(
        self,
        database: str,
        query: str,
        params: tuple = None
    ) -> QueryResult:
        """
        Execute a SELECT query.

        Args:
            database: Database name
            query: SQL query
            params: Query parameters

        Returns:
            QueryResult with rows and metadata
        """
        start_time = time.time()
        pool = self._get_pool(database)
        conn = None

        try:
            conn = pool.getconn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            result_dicts = [dict(row) for row in rows]

            cursor.close()

            duration = time.time() - start_time
            self.logger.debug(f"Query executed in {duration:.3f}s: {query[:50]}...")

            return QueryResult(
                rows=result_dicts,
                row_count=len(result_dicts),
                duration=duration,
                cached=False
            )

        except psycopg2.Error as e:
            duration = time.time() - start_time
            self.logger.error(f"Query failed after {duration:.3f}s: {e}")
            raise
        finally:
            if conn:
                pool.putconn(conn)

    def close_all(self) -> None:
        """Close all connection pools."""
        for database, pool in self._pools.items():
            pool.closeall()
            self.logger.info(f"Closed connection pool for database: {database}")
        self._pools.clear()


class DatabaseManager:
    """
    High-level database manager that chooses appropriate pool.
    Supports both async and sync operations.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "odoo",
        password: str = "odoo",
        min_connections: int = 2,
        max_connections: int = 10,
        prefer_async: bool = True
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.prefer_async = prefer_async and ASYNCPG_AVAILABLE

        self._async_pool: Optional[AsyncDatabasePool] = None
        self._sync_pool: Optional[SyncDatabasePool] = None
        self.logger = logger

    async def get_async_pool(self) -> AsyncDatabasePool:
        """Get async database pool."""
        if not ASYNCPG_AVAILABLE:
            raise ImportError("asyncpg not available for async operations")

        if self._async_pool is None:
            self._async_pool = AsyncDatabasePool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                min_size=self.min_connections,
                max_size=self.max_connections
            )
            await self._async_pool.initialize()

        return self._async_pool

    def get_sync_pool(self) -> SyncDatabasePool:
        """Get sync database pool."""
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 not available for sync operations")

        if self._sync_pool is None:
            self._sync_pool = SyncDatabasePool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                min_connections=self.min_connections,
                max_connections=self.max_connections
            )

        return self._sync_pool

    async def query_async(
        self,
        database: str,
        query: str,
        *args,
        use_cache: bool = True
    ) -> QueryResult:
        """Execute query asynchronously."""
        pool = await self.get_async_pool()
        return await pool.execute(database, query, *args, use_cache=use_cache)

    def query_sync(
        self,
        database: str,
        query: str,
        params: tuple = None
    ) -> QueryResult:
        """Execute query synchronously."""
        pool = self.get_sync_pool()
        return pool.execute_query(database, query, params)

    async def close(self) -> None:
        """Close all connections."""
        if self._async_pool:
            await self._async_pool.close()
            self._async_pool = None

        if self._sync_pool:
            self._sync_pool.close_all()
            self._sync_pool = None

        self.logger.info("All database connections closed")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(
    host: str = "localhost",
    port: int = 5432,
    user: str = "odoo",
    password: str = "odoo",
    **kwargs
) -> DatabaseManager:
    """Get global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(
            host=host,
            port=port,
            user=user,
            password=password,
            **kwargs
        )
    return _db_manager


async def query_database(
    database: str,
    query: str,
    *args,
    use_cache: bool = True,
    **db_params
) -> QueryResult:
    """
    Convenience function to execute a database query.

    Args:
        database: Database name
        query: SQL query
        *args: Query parameters
        use_cache: Enable query caching
        **db_params: Database connection parameters

    Returns:
        QueryResult
    """
    manager = get_db_manager(**db_params)
    return await manager.query_async(database, query, *args, use_cache=use_cache)


# Testing
if __name__ == "__main__":
    async def test_async_pool():
        """Test async database pool."""
        print("Testing Async Database Pool...")

        if not ASYNCPG_AVAILABLE:
            print("⚠️ asyncpg not available, skipping async tests")
            return

        # Create pool
        pool = AsyncDatabasePool(
            host="localhost",
            user="odoo",
            password="odoo"
        )

        try:
            await pool.initialize()
            print("✅ Pool initialized")

            # Test query
            result = await pool.execute(
                "postgres",
                "SELECT current_database(), current_user, version()"
            )

            print(f"✅ Query executed: {result.row_count} rows in {result.duration:.3f}s")
            for row in result:
                print(f"   {row}")

            # Test cached query
            result2 = await pool.execute(
                "postgres",
                "SELECT current_database(), current_user",
                use_cache=True
            )

            if result2.cached:
                print(f"✅ Cache hit: {result2.duration:.3f}s")

        finally:
            await pool.close()
            print("✅ Pool closed")

    def test_sync_pool():
        """Test sync database pool."""
        print("\nTesting Sync Database Pool...")

        if not PSYCOPG2_AVAILABLE:
            print("⚠️ psycopg2 not available, skipping sync tests")
            return

        pool = SyncDatabasePool(
            host="localhost",
            user="odoo",
            password="odoo"
        )

        try:
            result = pool.execute_query(
                "postgres",
                "SELECT current_database(), current_user"
            )

            print(f"✅ Query executed: {result.row_count} rows in {result.duration:.3f}s")
            for row in result:
                print(f"   {row}")

        finally:
            pool.close_all()
            print("✅ Pool closed")

    # Run tests
    print("=" * 60)
    print("Database Pool Tests")
    print("=" * 60)
    asyncio.run(test_async_pool())
    test_sync_pool()
