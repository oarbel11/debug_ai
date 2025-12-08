"""
╔══════════════════════════════════════════════════════════════════╗
║                      mcp_server.py                                ║
║                 🌐 GENERIC MCP Server                             ║
╠══════════════════════════════════════════════════════════════════╣
║  CLIENT-AGNOSTIC: Works with ANY database!                        ║
║                                                                   ║
║  Exposes the Debug Engine as an MCP server that AI agents         ║
║  (Claude, Cursor, etc.) can connect to.                           ║
║                                                                   ║
║  All tools are generic - no hardcoded table names or schemas!    ║
╚══════════════════════════════════════════════════════════════════╝

USAGE:
    python mcp_server.py

ENVIRONMENT VARIABLES:
    DEBUG_AI_DB_PATH - Path to database (optional, auto-detects)
    DEBUG_AI_DB_TYPE - Database type (default: duckdb)
"""

import os
import sys
from typing import Optional, List, Any

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import our generic debug engine
from debug_engine import DebugEngine, validate_identifier

# Import MCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("❌ MCP library not installed!")
    print("   Install with: pip install mcp")
    sys.exit(1)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MCP SERVER SETUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Create MCP server
mcp = FastMCP("DebugAI", json_response=True)

# Create debug engine instance (lazy loading)
_engine: Optional[DebugEngine] = None


def get_engine() -> DebugEngine:
    """Get or create the engine instance."""
    global _engine
    if _engine is None:
        _engine = DebugEngine()
    return _engine


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DISCOVERY TOOLS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@mcp.tool()
def list_schemas() -> dict:
    """
    📁 List all available schemas in the database.

    Use this first to discover what data is available.

    Returns:
        List of schema names.

    Example:
        list_schemas()
        → {"schemas": ["raw", "silver", "gold", "meta"]}
    """
    try:
        schemas = get_engine().list_schemas()
        return {"schemas": schemas}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_tables(schema: Optional[str] = None) -> dict:
    """
    📋 List all tables, optionally filtered by schema.

    Args:
        schema: Optional schema name to filter by.
                If not provided, lists ALL tables.

    Returns:
        List of tables with schema and name.

    Example:
        list_tables()
        → {"tables": [{"table_schema": "raw", "table_name": "employees"}, ...]}

        list_tables(schema="raw")
        → Only tables in the 'raw' schema
    """
    try:
        tables = get_engine().list_tables(schema)
        return {"tables": tables}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def describe_table(table_name: str) -> dict:
    """
    📊 Get column information for a table.

    Args:
        table_name: Full table name (e.g., "raw.employees")

    Returns:
        List of columns with their data types.

    Example:
        describe_table("raw.employees")
        → {"columns": [{"column_name": "emp_id", "column_type": "INTEGER"}, ...]}
    """
    try:
        columns = get_engine().describe_table(table_name)
        return {"columns": columns}
    except ValueError as e:
        return {"error": f"Invalid table name: {e}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_row_count(table_name: str) -> dict:
    """
    🔢 Get the number of rows in a table.

    Args:
        table_name: Full table name (e.g., "raw.employees")

    Returns:
        Row count.

    Example:
        get_row_count("raw.employees")
        → {"table": "raw.employees", "row_count": 1000}
    """
    try:
        count = get_engine().get_row_count(table_name)
        return {"table": table_name, "row_count": count}
    except Exception as e:
        return {"error": str(e)}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LINEAGE TOOLS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@mcp.tool()
def explain_column(target_table: str, target_column: str) -> str:
    """
    🔍 Explain how a column is calculated (THE MAIN FEATURE!)

    Use this to answer questions like:
    - "Why is this employee marked as HIGH RISK?"
    - "How is the total_revenue calculated?"
    - "What logic determines the status field?"

    Args:
        target_table: Table containing the column (e.g., "conformed.churn_risk")
        target_column: Column to explain (e.g., "risk_level")

    Returns:
        Detailed report showing:
        - Source tables
        - Transformation logic (SQL)
        - File where it's defined

    Example:
        explain_column("conformed.churn_risk", "risk_level")
        → Shows the CASE WHEN logic that calculates risk
    """
    try:
        return get_engine().trace_column_lineage(target_table, target_column)
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
def get_table_sources(target_table: str) -> dict:
    """
    📥 Get the upstream tables that feed into a target table.

    Args:
        target_table: Table to investigate (e.g., "silver.fact_jobs")

    Returns:
        List of source table names.

    Example:
        get_table_sources("silver.fact_jobs")
        → {"target": "silver.fact_jobs", "sources": ["raw.job_history", "raw.companies"]}
    """
    try:
        sources = get_engine().get_upstream_tables(target_table)
        return {"target": target_table, "sources": sources}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_lineage_tree(target_table: str) -> dict:
    """
    🌳 Get the complete lineage tree for a table.

    Traces ALL the way back to source data.

    Args:
        target_table: Starting point (e.g., "conformed.churn_risk")

    Returns:
        Nested tree showing all upstream dependencies.

    Example:
        get_lineage_tree("conformed.churn_risk")
        → {
            "lineage": {
                "silver.dim_employees": {
                    "raw.employees": {"_is_source": true}
                }
            }
          }
    """
    try:
        tree = get_engine().get_lineage_tree(target_table)
        return {"target": target_table, "lineage": tree}
    except Exception as e:
        return {"error": str(e)}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DEBUGGING TOOLS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@mcp.tool()
def check_table_health(target_table: str) -> dict:
    """
    🔬 Check the health of source tables (debugging tool).

    Use this when something looks wrong:
    - "Why is my result empty?"
    - "Why are there missing values?"

    Checks:
    - Row counts in all source tables
    - Whether any sources are empty

    Args:
        target_table: Table having issues (e.g., "silver.fact_jobs")

    Returns:
        Stats for each source table.

    Example:
        check_table_health("silver.fact_jobs")
        → {
            "raw.job_history": {"row_count": 100, "status": "✅"},
            "raw.companies": {"row_count": 0, "status": "⚠️ EMPTY"}
          }
    """
    try:
        return get_engine().check_table_sources(target_table)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def inspect_row(table: str, key_column: str, key_value: str) -> dict:
    """
    🔎 Fetch a specific row from a table.

    Use this to see actual data values.

    Args:
        table: Table to query (e.g., "raw.employees")
        key_column: Column to search by (e.g., "emp_id")
        key_value: Value to look for (e.g., "101")

    Returns:
        The row data as a dictionary.

    Example:
        inspect_row("raw.employees", "emp_id", "101")
        → {"row": {"emp_id": 101, "name": "Alice", "dept": "Sales"}}
    """
    try:
        # Convert value to appropriate type
        try:
            typed_value = int(key_value)
        except ValueError:
            typed_value = key_value

        return get_engine().inspect_row(table, key_column, typed_value)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def run_query(sql: str) -> dict:
    """
    ⚡ Run a custom SQL query (read-only).

    Use this for ad-hoc analysis not covered by other tools.

    Args:
        sql: SQL query to execute (SELECT only)

    Returns:
        Query results as list of rows.

    Example:
        run_query("SELECT * FROM raw.employees LIMIT 5")
        → {"rows": [...], "row_count": 5}

    SECURITY: Only SELECT queries allowed.
    """
    # Security: only allow SELECT queries
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith('SELECT'):
        return {"error": "Only SELECT queries are allowed"}

    # Block dangerous keywords
    dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
    for keyword in dangerous:
        if keyword in sql_upper:
            return {"error": f"Keyword '{keyword}' is not allowed"}

    try:
        df = get_engine().connector.execute(sql)
        return {
            "rows": df.to_dict(orient='records'),
            "row_count": len(df),
            "columns": list(df.columns)
        }
    except Exception as e:
        return {"error": str(e)}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN ENTRY POINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    from config.db_config import DB_PATH

    print()
    print('=' * 60)
    print('🌐 DEBUG AI - MCP Server (Generic)')
    print('=' * 60)
    print()
    print(f'📁 Database: {DB_PATH}')
    print()
    print('🔧 Available Tools:')
    print('   Discovery:')
    print('     • list_schemas       - Show available schemas')
    print('     • list_tables        - Show available tables')
    print('     • describe_table     - Show column info')
    print('     • get_row_count      - Count rows in a table')
    print()
    print('   Lineage:')
    print('     • explain_column     - How is a column calculated?')
    print('     • get_table_sources  - What feeds into this table?')
    print('     • get_lineage_tree   - Full dependency tree')
    print()
    print('   Debugging:')
    print('     • check_table_health - Debug data quality')
    print('     • inspect_row        - Look at specific data')
    print('     • run_query          - Custom SQL (read-only)')
    print()
    print('🚀 Starting server...')
    print('=' * 60)
    print()

    mcp.run()