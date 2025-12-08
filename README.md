# 🔍 Debug AI - Generic Data Observability Engine
**Autor: Omer Arbel**

**CLIENT-AGNOSTIC** data lineage and debugging tool. Works with ANY database schema!

## 🎯 What Does It Do?

Answers questions like:
- **"Why is this value calculated this way?"** → Shows exact SQL logic
- **"What tables feed into this report?"** → Shows full lineage tree
- **"Why is my result empty?"** → Checks source table health

## ✨ Key Features

- ✅ **100% Generic** - No hardcoded table names, schemas, or paths
- ✅ **Auto-Detection** - Finds your database and SQL files automatically
- ✅ **Secure** - SQL injection prevention, safe connection handling
- ✅ **Extensible** - Easy to add new database types (Snowflake, Databricks)
- ✅ **MCP Ready** - AI agents can connect via MCP protocol

---

## 📁 Project Structure

```
debug_ai/
├── config/
│   ├── __init__.py
│   └── db_config.py      ← Auto-detects paths, customizable via env vars
│
├── scripts/
│   ├── __init__.py
│   └── build_metadata.py ← Parses SQL files, builds lineage metadata
│
├── debug_engine.py       ← Main engine - answers lineage questions
├── mcp_server.py         ← MCP server for AI agents
└── README.md
```

---

## 🚀 Quick Start

### 1. Place Your Database

Put your `.duckdb` file anywhere. The engine auto-detects it from:
- `./data/*.duckdb`
- `./companies_data/*.duckdb`
- `./*.duckdb`
- Or set `DEBUG_AI_DB_PATH` environment variable

### 2. Test the Engine

```bash
python debug_engine.py
```

This will:
- Auto-detect your database
- List all schemas and tables
- Show sample lineage queries

### 3. (Optional) Build Metadata from SQL Files

If you have SQL transformation files:

```bash
python scripts/build_metadata.py --sql-dir /path/to/sql/files
```

### 4. Start MCP Server (for AI agents)

```bash
python mcp_server.py
```

---

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG_AI_DB_PATH` | Path to database file | Auto-detected |
| `DEBUG_AI_ETL_DIR` | Path to SQL files | Auto-detected |
| `DEBUG_AI_DB_TYPE` | Database type | `duckdb` |

### Example: Custom Paths

```bash
export DEBUG_AI_DB_PATH=/data/warehouse.duckdb
export DEBUG_AI_ETL_DIR=/etl/transformations
python debug_engine.py
```

---

## 📖 Usage Examples

### Python API

```python
from debug_engine import DebugEngine

# Auto-detect database
engine = DebugEngine()

# Or specify path
engine = DebugEngine('/path/to/database.duckdb')

# Discovery
schemas = engine.list_schemas()
tables = engine.list_tables()
columns = engine.describe_table('raw.employees')

# Lineage
report = engine.trace_column_lineage('gold.report', 'total_sales')
sources = engine.get_upstream_tables('silver.fact_orders')
tree = engine.get_lineage_tree('gold.report')

# Debugging
health = engine.check_table_sources('silver.fact_orders')
row = engine.inspect_row('raw.customers', 'customer_id', 12345)
```

### MCP Tools (for AI Agents)

| Tool | Description |
|------|-------------|
| `list_schemas()` | Show available schemas |
| `list_tables(schema?)` | Show available tables |
| `describe_table(table)` | Show columns |
| `explain_column(table, column)` | **Main feature!** Show how column is calculated |
| `get_table_sources(table)` | Show upstream dependencies |
| `get_lineage_tree(table)` | Full dependency tree |
| `check_table_health(table)` | Debug data quality |
| `inspect_row(table, key_col, value)` | Look at specific data |
| `run_query(sql)` | Custom SQL (read-only) |

---

## 🏦 Client Examples

### Bank A
```python
engine = DebugEngine('/data/bank_warehouse.duckdb')
engine.trace_column_lineage('risk.customer_score', 'credit_rating')
```

### Hospital B  
```python
engine = DebugEngine('/data/hospital_data.duckdb')
engine.trace_column_lineage('analytics.patient_risk', 'readmission_probability')
```

### Retail C
```python
engine = DebugEngine('/data/retail.duckdb')
engine.trace_column_lineage('gold.sales_report', 'total_revenue')
```

**Same code, different databases!**

---

## 🔒 Security Features

- ✅ SQL injection prevention (identifier validation)
- ✅ Parameterized queries where possible
- ✅ Read-only connections by default
- ✅ Query keyword filtering (blocks DROP, DELETE, etc.)

---

## 🔌 Extending for New Databases

Add a new connector in `debug_engine.py`:

```python
class SnowflakeConnector(DatabaseConnector):
    def __init__(self, config: dict):
        # Initialize Snowflake connection
        pass
    
    def execute(self, query: str, params=None) -> pd.DataFrame:
        # Execute query
        pass
    
    def get_schemas(self) -> List[str]:
        # Return schemas
        pass
    
    def get_tables(self, schema=None) -> List[Dict]:
        # Return tables
        pass
```

Then update `DebugEngine.__init__()`:
```python
if db_type == 'snowflake':
    self.connector = SnowflakeConnector(config)
```

---

## 📝 Metadata Schema

The engine expects these tables in a `meta` schema:

### `meta.table_lineage`
| Column | Type | Description |
|--------|------|-------------|
| target_table | VARCHAR | Table being created |
| source_table | VARCHAR | Table it reads from |
| sql_text | VARCHAR | Full SQL statement |

### `meta.column_lineage`
| Column | Type | Description |
|--------|------|-------------|
| target_table | VARCHAR | Table containing the column |
| target_column | VARCHAR | Column name |
| source_table | VARCHAR | Source table(s) |
| source_column | VARCHAR | Source column or 'COMPUTED' |
| transformation_logic | VARCHAR | SQL logic (CASE, AGG, etc.) |
| sql_file_name | VARCHAR | Source file name |

---

## 🤝 Contributing

1. Fork the repo
2. Add your database connector
3. Submit a PR

---

Built with ❤️ for Data Engineers everywhere

**Created By: Omer Arbel**