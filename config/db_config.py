"""
╔══════════════════════════════════════════════════════════════════╗
║                   config/db_config.py                             ║
║                  📒 GENERIC Configuration                         ║
╠══════════════════════════════════════════════════════════════════╣
║  This file is CLIENT-AGNOSTIC.                                    ║
║                                                                   ║
║  It auto-detects paths OR reads from environment variables.       ║
║  Works for any client without code changes!                       ║
║                                                                   ║
║  CUSTOMIZATION OPTIONS:                                           ║
║  1. Set environment variables (recommended for production)        ║
║  2. Place files in default locations                              ║
║  3. Modify this file directly (not recommended)                   ║
╚══════════════════════════════════════════════════════════════════╝

ENVIRONMENT VARIABLES (optional):
    DEBUG_AI_DB_PATH  = Path to the DuckDB database file
    DEBUG_AI_ETL_DIR  = Path to the folder containing SQL files
    DEBUG_AI_DB_TYPE  = Database type (duckdb, databricks, snowflake)
"""

from pathlib import Path
from typing import Optional, Dict, Any
import os


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PATH DETECTION (Generic - works anywhere!)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _find_project_root() -> Path:
    """
    Find the project root directory.

    Looks for common markers like:
    - A 'config' folder (we're in it!)
    - A '.git' folder
    - A 'pyproject.toml' or 'setup.py'

    Falls back to parent of this file's directory.
    """
    current = Path(__file__).resolve().parent  # config/

    # Go up to project root
    if current.name == 'config':
        return current.parent

    return current


def _find_database() -> Optional[Path]:
    """
    Auto-detect the database file.

    Search order:
    1. Environment variable DEBUG_AI_DB_PATH
    2. Common locations relative to project root
    """
    # Check environment variable first
    env_path = os.getenv('DEBUG_AI_DB_PATH')
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path

    # Search common locations
    root = _find_project_root()
    common_locations = [
        root / 'data' / '*.duckdb',
        root / 'companies_data' / '*.duckdb',
        root / '*.duckdb',
        root / 'database' / '*.duckdb',
        root / 'db' / '*.duckdb',
    ]

    for pattern in common_locations:
        matches = list(pattern.parent.glob(pattern.name)) if pattern.parent.exists() else []
        if matches:
            return matches[0]  # Return first match

    return None


def _find_etl_dir() -> Optional[Path]:
    """
    Auto-detect the ETL directory (where SQL files live).

    Search order:
    1. Environment variable DEBUG_AI_ETL_DIR
    2. Common locations relative to project root
    """
    # Check environment variable first
    env_path = os.getenv('DEBUG_AI_ETL_DIR')
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path

    # Search common locations
    root = _find_project_root()
    common_locations = [
        root / 'etl',
        root / 'sql',
        root / 'transformations',
        root / 'data' / 'etl',
        root / 'companies_data' / 'etl',
        root / 'dbt' / 'models',
    ]

    for loc in common_locations:
        if loc.exists() and loc.is_dir():
            return loc

    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURATION VALUES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Project root directory
PROJECT_ROOT: Path = _find_project_root()

# Database path (auto-detected or from environment)
DB_PATH: Optional[Path] = _find_database()

# ETL directory (auto-detected or from environment)
ETL_DIR: Optional[Path] = _find_etl_dir()

# Database type (from environment or default to duckdb)
DB_TYPE: str = os.getenv('DEBUG_AI_DB_TYPE', 'duckdb')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATABASE CONFIGURATION (Generic structure)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_db_config() -> Dict[str, Any]:
    """
    Get database configuration dictionary.

    Returns a generic structure that works for any database type.
    Extend this for new database types (Snowflake, Databricks, etc.)
    """
    config = {
        'type': DB_TYPE,
        'connection_details': {}
    }

    if DB_TYPE == 'duckdb':
        config['connection_details'] = {
            'path': str(DB_PATH) if DB_PATH else None
        }

    elif DB_TYPE == 'databricks':
        # Databricks connection (extend as needed)
        config['connection_details'] = {
            'host': os.getenv('DATABRICKS_HOST'),
            'token': os.getenv('DATABRICKS_TOKEN'),
            'warehouse_id': os.getenv('DATABRICKS_WAREHOUSE_ID'),
        }

    elif DB_TYPE == 'snowflake':
        # Snowflake connection (extend as needed)
        config['connection_details'] = {
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'user': os.getenv('SNOWFLAKE_USER'),
            'password': os.getenv('SNOWFLAKE_PASSWORD'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': os.getenv('SNOWFLAKE_DATABASE'),
        }

    return config


# For backwards compatibility
DB_CONFIGURATION = get_db_config()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def check_setup() -> Dict[str, Any]:
    """
    Verify all required paths exist.

    Returns a status report useful for debugging setup issues.
    """
    return {
        'project_root': {
            'path': str(PROJECT_ROOT),
            'exists': PROJECT_ROOT.exists(),
            'status': '✅' if PROJECT_ROOT.exists() else '❌'
        },
        'database': {
            'path': str(DB_PATH) if DB_PATH else 'NOT FOUND',
            'exists': DB_PATH.exists() if DB_PATH else False,
            'status': '✅' if (DB_PATH and DB_PATH.exists()) else '❌'
        },
        'etl_directory': {
            'path': str(ETL_DIR) if ETL_DIR else 'NOT FOUND',
            'exists': ETL_DIR.exists() if ETL_DIR else False,
            'status': '✅' if (ETL_DIR and ETL_DIR.exists()) else '⚠️ Optional'
        },
        'db_type': DB_TYPE
    }


def get_db_path_safe() -> str:
    """
    Get database path with validation.

    Raises FileNotFoundError if database not found.
    """
    if not DB_PATH:
        raise FileNotFoundError(
            "❌ DATABASE NOT FOUND!\n"
            "\n"
            "Options to fix:\n"
            "  1. Set environment variable: export DEBUG_AI_DB_PATH=/path/to/db.duckdb\n"
            "  2. Place your .duckdb file in: {PROJECT_ROOT}/data/ or {PROJECT_ROOT}/\n"
            f"\n"
            f"Current project root: {PROJECT_ROOT}"
        )

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"❌ DATABASE FILE NOT FOUND!\n"
            f"   Expected: {DB_PATH}\n"
            f"   Please check the path exists."
        )

    return str(DB_PATH)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SELF-TEST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    print()
    print('=' * 60)
    print('📒 DEBUG AI - Configuration Check')
    print('=' * 60)

    status = check_setup()

    print()
    for name, info in status.items():
        if isinstance(info, dict):
            print(f"  {info.get('status', '?')} {name}")
            print(f"     └─ {info.get('path', info)}")
        else:
            print(f"  ℹ️  {name}: {info}")

    print()
    print('=' * 60)
    print()