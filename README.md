# 🔍 Debug AI - Talk to Your Data Lake!

Ask questions about your data in plain English:

> *"How is the risk_level column calculated?"*

> *"What tables feed into the sales report?"*

> *"Why is this customer marked as high risk?"*

And get answers based on your **actual SQL transformations**!

---

## 🚀 Quick Start

### 1. Install
```powershell
pip install duckdb pandas mcp
```

### 2. Setup (point to YOUR database and SQL files)
```powershell
python scripts/cli.py init --db "C:\path\to\your\database.duckdb" --sql "C:\path\to\sql\files"
python scripts/cli.py build
python scripts/cli.py test
```

### 3. Connect to Cursor
Add to Cursor settings, then restart Cursor:
```json
{
  "mcpServers": {
    "debug-ai": {
      "command": "python",
      "args": ["C:\\path\\to\\debug_ai\\mcp_server.py"]
    }
  }
}
```

### 4. Start Asking Questions!
Open Cursor and chat with your data.

---

## 📖 Full Setup Guide

**See [SETUP.md](SETUP.md)** for detailed step-by-step instructions.

---

## 📋 CLI Commands

| Command | What It Does |
|---------|--------------|
| `python scripts/cli.py init --db "..." --sql "..."` | Configure paths |
| `python scripts/cli.py build` | Parse SQL → Create metadata |
| `python scripts/cli.py scan` | Show tables & metadata status |
| `python scripts/cli.py test` | Verify everything works |
| `python scripts/cli.py query table column` | Quick lineage lookup |

---

## 🤔 How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Your SQL       │ ──▶ │  build command  │ ──▶ │  Metadata       │
│  Files          │     │  (parses SQL)   │     │  Tables         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  You ask        │ ◀── │  Cursor/Claude  │ ◀── │  MCP Server     │
│  questions!     │     │  (AI)           │     │  (answers)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

1. **build** parses your SQL files and stores lineage in metadata tables
2. **MCP server** exposes tools for AI to query that lineage
3. **Cursor/Claude** uses those tools to answer your questions!

---

## 📁 What You Need

- ✅ A `.duckdb` database file
- ✅ SQL files with your transformations (`CREATE TABLE ... AS SELECT ...`)
- ✅ Python 3.8+
- ✅ Cursor or Claude Desktop

---

## 🆘 Need Help?

1. Check [SETUP.md](SETUP.md) for detailed instructions
2. Run `python cli.py test` to diagnose issues
3. Open an issue on GitHub

---

Made with ❤️ for Data Engineers