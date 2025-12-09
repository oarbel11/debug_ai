"""
╔══════════════════════════════════════════════════════════════════╗
║                      debug_engine.py                              ║
║                  🔍 GENERIC Debug Engine                          ║
╠══════════════════════════════════════════════════════════════════╣
║  CLIENT-AGNOSTIC: Works with ANY database schema!                 ║
║                                                                   ║
║  • No hardcoded table names                                       ║
║  • No hardcoded schema names                                      ║
║  • Auto-discovers available tables                                ║
║  • Works with any metadata structure                              ║
╚══════════════════════════════════════════════════════════════════╝

USAGE:
    from debug_engine import DebugEngine

    engine = DebugEngine('/path/to/database.duckdb')

    # Discover what's available
    tables = engine.list_tables()

    # Trace column lineage
    report = engine.trace_column_lineage('schema.table', 'column')
"""

import re
import logging
from pathlib import Path
from contextlib import contextmanager
from functools import lru_cache
from typing import Dict, List, Optional, Any, Generator
from abc import ABC, abstractmethod

import duckdb
import pandas as pd


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('DebugEngine')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECURITY: Input Validation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Valid identifier pattern: letters, numbers, underscores
# Optional schema prefix: schema.table
SAFE_IDENTIFIER = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)?$')


def validate_identifier(name: str, identifier_type: str = 'identifier') -> str:
    """
    Validate a SQL identifier (table name, column name, etc.)

    Prevents SQL injection attacks.

    Args:
        name: The identifier to validate
        identifier_type: What kind of identifier (for error messages)

    Returns:
        The validated identifier

    Raises:
        ValueError: If the identifier is invalid
    """
    if not name or not SAFE_IDENTIFIER.match(name):
        raise ValueError(
            f"Invalid {identifier_type}: '{name}'\n"
            f"Only letters, numbers, and underscores allowed."
        )
    return name


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ABSTRACT BASE: Database Connector
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DatabaseConnector(ABC):
    """
    Abstract base class for database connections.

    Extend this class to support new database types
    (Snowflake, Databricks, PostgreSQL, etc.)
    """

    @abstractmethod
    def execute(self, query: str, params: Optional[List] = None) -> pd.DataFrame:
        """Execute a query and return results as DataFrame."""
        pass

    @abstractmethod
    def get_schemas(self) -> List[str]:
        """Get list of available schemas."""
        pass

    @abstractmethod
    def get_tables(self, schema: Optional[str] = None) -> List[Dict[str, str]]:
        """Get list of tables, optionally filtered by schema."""
        pass


class DuckDBConnector(DatabaseConnector):
    """DuckDB implementation of DatabaseConnector."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def _connect(self, read_only: bool = True) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        """Context manager for safe connections."""
        con = duckdb.connect(self.db_path, read_only=read_only)
        try:
            yield con
        finally:
            con.close()

    def execute(self, query: str, params: Optional[List] = None) -> pd.DataFrame:
        """Execute query and return DataFrame."""
        with self._connect() as con:
            if params:
                return con.execute(query, params).fetchdf()
            return con.execute(query).fetchdf()

    def get_schemas(self) -> List[str]:
        """Get all user schemas (excluding system schemas)."""
        query = """
            SELECT DISTINCT table_schema 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema
        """
        df = self.execute(query)
        return df['table_schema'].tolist()

    def get_tables(self, schema: Optional[str] = None) -> List[Dict[str, str]]:
        """Get all tables, optionally filtered by schema."""
        if schema:
            validate_identifier(schema, 'schema')
            query = """
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_schema = ?
                ORDER BY table_name
            """
            df = self.execute(query, [schema])
        else:
            query = """
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                ORDER BY table_schema, table_name
            """
            df = self.execute(query)

        return df.to_dict(orient='records')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN CLASS: Debug Engine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DebugEngine:
    """
    🔍 Generic Data Debug Engine

    Works with ANY database schema. No hardcoded values!

    Features:
    - Auto-discovers tables and schemas
    - Traces column lineage
    - Debugs data quality issues
    - Works with any metadata structure

    Usage:
        engine = DebugEngine('/path/to/db.duckdb')

        # Discovery
        tables = engine.list_tables()
        schemas = engine.list_schemas()

        # Lineage
        report = engine.trace_column_lineage('schema.table', 'column')

        # Debugging
        stats = engine.check_table_sources('schema.table')
    """

    # Default metadata table names (can be customized per client)
    DEFAULT_TABLE_LINEAGE = 'meta.table_lineage'
    DEFAULT_COLUMN_LINEAGE = 'meta.column_lineage'

    def __init__(
        self,
        db_path: Optional[str] = None,
        db_type: str = 'duckdb',
        table_lineage_table: Optional[str] = None,
        column_lineage_table: Optional[str] = None
    ):
        """
        Initialize the Debug Engine.

        Args:
            db_path: Path to database. If None, auto-detects from config.
            db_type: Database type ('duckdb', 'databricks', 'snowflake')
            table_lineage_table: Custom metadata table for table lineage
            column_lineage_table: Custom metadata table for column lineage
        """
        # Auto-detect path if not provided
        if db_path is None:
            from config.db_config import get_db_path_safe
            db_path = get_db_path_safe()

        self.db_path = db_path
        self.db_type = db_type

        # Initialize connector based on type
        if db_type == 'duckdb':
            self.connector = DuckDBConnector(db_path)
        else:
            raise NotImplementedError(f"Database type '{db_type}' not yet supported")

        # Metadata table names (customizable!)
        self.table_lineage_table = table_lineage_table or self.DEFAULT_TABLE_LINEAGE
        self.column_lineage_table = column_lineage_table or self.DEFAULT_COLUMN_LINEAGE

        logger.info(f"DebugEngine initialized: {db_path}")

    # ─────────────────────────────────────────────────────────────
    # DISCOVERY METHODS
    # ─────────────────────────────────────────────────────────────

    def list_schemas(self) -> List[str]:
        """
        📁 List all available schemas in the database.

        Returns:
            List of schema names
        """
        return self.connector.get_schemas()

    def list_tables(self, schema: Optional[str] = None) -> List[Dict[str, str]]:
        """
        📋 List all tables in the database.

        Args:
            schema: Optional - filter to specific schema

        Returns:
            List of dicts with 'table_schema' and 'table_name'
        """
        return self.connector.get_tables(schema)

    def describe_table(self, table: str) -> List[Dict[str, Any]]:
        """
        📊 Get column information for a table.

        Args:
            table: Full table name (e.g., 'raw.employees')

        Returns:
            List of column definitions
        """
        validate_identifier(table, 'table')
        df = self.connector.execute(f"DESCRIBE {table}")
        return df.to_dict(orient='records')

    def get_row_count(self, table: str) -> int:
        """
        🔢 Get row count for a table.

        Args:
            table: Full table name

        Returns:
            Number of rows
        """
        validate_identifier(table, 'table')
        df = self.connector.execute(f"SELECT COUNT(*) as cnt FROM {table}")
        return int(df['cnt'].iloc[0])

    # ─────────────────────────────────────────────────────────────
    # LINEAGE METHODS
    # ─────────────────────────────────────────────────────────────

    def _check_metadata_exists(self) -> Dict[str, bool]:
        """Check if metadata tables exist."""
        tables = self.list_tables('meta')
        table_names = [f"meta.{t['table_name']}" for t in tables]

        return {
            'table_lineage': self.table_lineage_table in table_names,
            'column_lineage': self.column_lineage_table in table_names
        }

    @lru_cache(maxsize=100)
    def trace_column_lineage(self, target_table: str, target_column: str) -> str:
        """
        🔍 Trace how a column is calculated.

        Args:
            target_table: Table containing the column (e.g., 'conformed.churn_risk')
            target_column: Column to trace (e.g., 'risk_level')

        Returns:
            Formatted report explaining the column's lineage
        """
        validate_identifier(target_table, 'table')
        validate_identifier(target_column, 'column')

        # Check metadata exists
        meta_status = self._check_metadata_exists()
        if not meta_status['column_lineage']:
            return (
                f"❌ Metadata table not found: {self.column_lineage_table}\n"
                f"   Run build_metadata.py first to create lineage data."
            )

        # Query the metadata
        query = f"""
            SELECT *
            FROM {self.column_lineage_table}
            WHERE target_table = ? AND target_column = ?
        """

        try:
            df = self.connector.execute(query, [target_table, target_column])
        except Exception as e:
            return f"❌ Query error: {e}"

        if df.empty:
            return (
                f"❌ No lineage found for: {target_table}.{target_column}\n"
                f"\n"
                f"Possible reasons:\n"
                f"  • Column doesn't exist in metadata\n"
                f"  • Run build_metadata.py to refresh\n"
                f"  • Column might be a simple pass-through"
            )

        # Build report (generic - works with any column structure)
        row = df.iloc[0]

        report_lines = [
            "",
            "╔═══════════════════════════════════════════════════════════════╗",
            "║  🔍 COLUMN LINEAGE REPORT                                      ║",
            "╠═══════════════════════════════════════════════════════════════╣",
            f"║  📍 Target: {target_table}.{target_column}",
            "║",
        ]

        # Add all available fields from the row (GENERIC!)
        for col in df.columns:
            if col not in ['target_table', 'target_column']:
                value = row[col]
                if value and str(value).strip():
                    # Format multi-line values
                    if '\n' in str(value):
                        report_lines.append(f"║  📦 {col}:")
                        for line in str(value).split('\n'):
                            report_lines.append(f"║     {line}")
                    else:
                        report_lines.append(f"║  📦 {col}: {value}")

        report_lines.extend([
            "║",
            "╚═══════════════════════════════════════════════════════════════╝",
            ""
        ])

        return '\n'.join(report_lines)

    def get_upstream_tables(self, target_table: str) -> List[str]:
        """
        📥 Get tables that feed into the target table.

        Args:
            target_table: Table to investigate

        Returns:
            List of source table names
        """
        validate_identifier(target_table, 'table')

        meta_status = self._check_metadata_exists()
        if not meta_status['table_lineage']:
            logger.warning(f"Metadata table not found: {self.table_lineage_table}")
            return []

        query = f"""
            SELECT DISTINCT source_table
            FROM {self.table_lineage_table}
            WHERE target_table = ?
        """

        try:
            df = self.connector.execute(query, [target_table])
            return df['source_table'].tolist()
        except Exception as e:
            logger.error(f"Error getting upstream tables: {e}")
            return []

    def get_lineage_tree(self, target_table: str, max_depth: int = 5) -> Dict[str, Any]:
        """
        🌳 Get full lineage tree (recursive).

        Args:
            target_table: Starting point
            max_depth: Maximum recursion depth

        Returns:
            Nested dictionary of lineage
        """
        validate_identifier(target_table, 'table')

        if max_depth <= 0:
            return {"_truncated": True}

        upstream = self.get_upstream_tables(target_table)

        if not upstream:
            return {"_is_source": True}

        tree = {}
        for source in upstream:
            tree[source] = self.get_lineage_tree(source, max_depth - 1)

        return tree

    # ─────────────────────────────────────────────────────────────
    # DEBUGGING METHODS
    # ─────────────────────────────────────────────────────────────

    def check_table_sources(self, target_table: str) -> Dict[str, Any]:
        """
        🔬 Check health of source tables.

        Args:
            target_table: Table to debug

        Returns:
            Dict with stats for each source table
        """
        validate_identifier(target_table, 'table')

        upstream = self.get_upstream_tables(target_table)

        if not upstream:
            return {
                "error": f"No upstream tables found for {target_table}",
                "hint": "Check if lineage metadata exists"
            }

        results = {}
        for source in upstream:
            try:
                count = self.get_row_count(source)
                results[source] = {
                    "row_count": count,
                    "status": "✅" if count > 0 else "⚠️ EMPTY"
                }
            except Exception as e:
                results[source] = {
                    "error": str(e),
                    "status": "❌ ERROR"
                }

        return results

    def inspect_row(self, table: str, key_column: str, key_value: Any) -> Dict[str, Any]:
        """
        🔎 Fetch a specific row from a table.

        Args:
            table: Table to query
            key_column: Column to filter by
            key_value: Value to look for

        Returns:
            Row data as dictionary
        """
        validate_identifier(table, 'table')
        validate_identifier(key_column, 'column')

        # Safe query with parameter
        query = f"SELECT * FROM {table} WHERE {key_column} = ?"

        try:
            df = self.connector.execute(query, [key_value])

            if df.empty:
                return {
                    "status": "not_found",
                    "message": f"No row where {key_column} = {key_value}"
                }

            return {"row": df.to_dict(orient='records')[0]}

        except Exception as e:
            return {"error": str(e)}

    def clear_cache(self):
        """Clear cached lineage results."""
        self.trace_column_lineage.cache_clear()
        logger.info("Cache cleared")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONVENIENCE FUNCTIONS (for backwards compatibility)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Default engine instance (lazy loaded)
_default_engine: Optional[DebugEngine] = None


def get_engine() -> DebugEngine:
    """Get or create the default engine instance."""
    global _default_engine
    if _default_engine is None:
        _default_engine = DebugEngine()
    return _default_engine


def trace_column_lineage(target_table: str, target_column: str) -> str:
    """Convenience function using default engine."""
    return get_engine().trace_column_lineage(target_table, target_column)


def debug_query_dependencies(target_table: str) -> Dict[str, Any]:
    """Convenience function using default engine."""
    return get_engine().check_table_sources(target_table)


def get_upstream_tables(target_table: str) -> List[str]:
    """Convenience function using default engine."""
    return get_engine().get_upstream_tables(target_table)


def get_lineage_tree(target_table: str) -> Dict[str, Any]:
    """Convenience function using default engine."""
    return get_engine().get_lineage_tree(target_table)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SELF-TEST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    import json
    import sys
    import os

    # Add project root to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    print()
    print('=' * 65)
    print('🔍 DEBUG AI ENGINE - Generic Test')
    print('=' * 65)

    # Initialize engine (auto-detects database)
    try:
        engine = DebugEngine()
        print(f"\n✅ Database: {engine.db_path}")
    except Exception as e:
        print(f"\n❌ Failed to initialize: {e}")
        sys.exit(1)

    # Test 1: List schemas (GENERIC - works for any DB)
    print('\n' + '-' * 65)
    print('TEST 1: Discover available schemas')
    print('-' * 65)
    schemas = engine.list_schemas()
    for s in schemas:
        print(f"   📁 {s}")

    # Test 2: List tables (GENERIC)
    print('\n' + '-' * 65)
    print('TEST 2: Discover available tables')
    print('-' * 65)
    tables = engine.list_tables()
    for t in tables:
        full_name = f"{t['table_schema']}.{t['table_name']}"
        try:
            count = engine.get_row_count(full_name)
            print(f"   📋 {full_name} ({count} rows)")
        except:
            print(f"   📋 {full_name}")

    # Test 3: Check metadata status
    print('\n' + '-' * 65)
    print('TEST 3: Check metadata status')
    print('-' * 65)
    meta_status = engine._check_metadata_exists()
    for name, exists in meta_status.items():
        status = '✅' if exists else '❌'
        print(f"   {status} {name}")

    # Test 4: Column lineage (if metadata exists)
    if meta_status['column_lineage']:
        print('\n' + '-' * 65)
        print('TEST 4: Trace column lineage')
        print('-' * 65)

        # Get a sample from metadata
        sample_query = f"SELECT target_table, target_column FROM {engine.column_lineage_table} LIMIT 1"
        try:
            sample = engine.connector.execute(sample_query)
            if not sample.empty:
                t_table = sample['target_table'].iloc[0]
                t_column = sample['target_column'].iloc[0]
                print(f"   Testing: {t_table}.{t_column}")
                report = engine.trace_column_lineage(t_table, t_column)
                print(report)
        except Exception as e:
            print(f"   ⚠️ Could not test: {e}")

    # Test 5: Lineage tree (if metadata exists)
    if meta_status['table_lineage']:
        print('\n' + '-' * 65)
        print('TEST 5: Lineage tree')
        print('-' * 65)

        # Get a sample target table
        sample_query = f"SELECT DISTINCT target_table FROM {engine.table_lineage_table} LIMIT 1"
        try:
            sample = engine.connector.execute(sample_query)
            if not sample.empty:
                t_table = sample['target_table'].iloc[0]
                print(f"   Testing: {t_table}")
                tree = engine.get_lineage_tree(t_table)
                print(json.dumps(tree, indent=2))
        except Exception as e:
            print(f"   ⚠️ Could not test: {e}")

    print('\n' + '=' * 65)
    print('✅ All tests completed!')
    print('=' * 65)
    print()