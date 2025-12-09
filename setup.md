# 🚀 SETUP GUIDE - Debug AI

## Read This Like a Recipe! 🍳

Follow each step in order. Don't skip any step!

---

# PART 1: Download & Install (5 minutes)

## Step 1: Download the Project

**Option A: If you have Git**
```powershell
git clone https://github.com/YOUR_USERNAME/debug_ai.git
cd debug_ai
```

**Option B: If you don't have Git**
1. Click the green "Code" button on GitHub
2. Click "Download ZIP"
3. Unzip the folder
4. Open PowerShell and go to that folder:
```powershell
cd C:\Users\YourName\Downloads\debug_ai
```

---

## Step 2: Install Python Packages

Copy and paste this into PowerShell:

```powershell
pip install duckdb pandas mcp
```

Wait until it finishes. You should see "Successfully installed..."

---

## Step 3: Test That It Works

```powershell
python cli.py --help
```

You should see a list of commands. If you see an error, go back to Step 2.

---

# PART 2: Connect Your Database (2 minutes)

## Step 4: Tell Debug AI Where Your Database Is

Replace the path with YOUR database location:

```powershell
python cli.py init --db "C:\PUT\YOUR\PATH\HERE\database.duckdb"
```

**Example paths:**
- `C:\Users\John\Data\warehouse.duckdb`
- `D:\Projects\sales_data.duckdb`
- `.\data\my_database.duckdb` (if it's in the debug_ai folder)

---

## Step 5: Check That It Found Your Database

```powershell
python cli.py scan
```

You should see your tables listed like this:
```
📂 Schemas:
   • raw
   • silver

📋 Tables:
   • raw.customers (1,000 rows)
   • silver.orders (5,000 rows)
```

If you see "❌ Database not found", go back to Step 4 and check the path.

---

## Step 6: Run a Test

```powershell
python cli.py test
```

You should see all ✅ checkmarks. If you see ❌, something is wrong.

---

# PART 3: Connect to Cursor/Claude (3 minutes)

This is the fun part! Now you can TALK to your database!

---

## Step 7: Find Where Your Project Is

Run this command and COPY the output:

```powershell
pwd
```

It will show something like: `C:\Users\John\debug_ai`

You need this path for the next step!

---

## Step 8: Set Up Cursor

### 8a. Open Cursor Settings

1. Open Cursor
2. Press `Ctrl + Shift + P`
3. Type "settings json"
4. Click "Preferences: Open User Settings (JSON)"

### 8b. Add the MCP Server

Add this to your settings (PUT YOUR PATH from Step 7!):

```json
{
  "mcpServers": {
    "debug-ai": {
      "command": "python",
      "args": ["C:\\Users\\John\\debug_ai\\mcp_server.py"]
    }
  }
}
```

⚠️ **IMPORTANT:** 
- Change `C:\\Users\\John\\debug_ai` to YOUR path from Step 7
- Use DOUBLE backslashes `\\` not single `\`

### 8c. Restart Cursor

Close Cursor completely and open it again.

---

## Step 9: Set Up Claude Desktop (Alternative to Cursor)

### 9a. Find the Config File

The config file is at:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

### 9b. Edit the Config File

Open it in Notepad and add:

```json
{
  "mcpServers": {
    "debug-ai": {
      "command": "python",
      "args": ["C:\\Users\\John\\debug_ai\\mcp_server.py"]
    }
  }
}
```

### 9c. Restart Claude Desktop

Close it and open it again.

---

# PART 4: Start Talking! 🎉

## Step 10: Ask Questions About Your Data!

In Cursor or Claude, try these:

> "What tables do I have?"

> "Show me the schema of the customers table"

> "How is the risk_level column calculated?"

> "What tables feed into the sales_report?"

> "Why might the revenue column be empty?"

---

# 🆘 TROUBLESHOOTING

## "Python not found"
Install Python from https://python.org

## "Module not found: duckdb"
Run: `pip install duckdb pandas mcp`

## "Database not found"
Check your path in Step 4. Make sure the file exists.

## "MCP server not connecting"
1. Make sure you restarted Cursor/Claude
2. Check the path has double backslashes `\\`
3. Try running manually: `python mcp_server.py`

## Still stuck?
Run this and send the output:
```powershell
python cli.py test
```

---

# 📁 OPTIONAL: Add Your SQL Files

If you have SQL transformation files (like dbt models), you can build lineage:

```powershell
python cli.py init --db "C:\your\database.duckdb" --sql "C:\your\sql\folder"
python cli.py build
```

This parses your SQL and creates the lineage metadata!

---

# ✅ CHECKLIST

Before asking for help, make sure:

- [ ] Python is installed (`python --version` works)
- [ ] Packages installed (`pip install duckdb pandas mcp`)
- [ ] Database path is correct (`python cli.py scan` shows tables)
- [ ] Tests pass (`python cli.py test` shows ✅)
- [ ] Cursor/Claude config has correct path with `\\`
- [ ] Cursor/Claude was restarted after config change

---

# 🎬 QUICK START (Copy-Paste Version)

For people who just want to copy-paste everything:

```powershell
# 1. Install packages
pip install duckdb pandas mcp

# 2. Set your database (CHANGE THIS PATH!)
python cli.py init --db "C:\YOUR\DATABASE\PATH\database.duckdb"

# 3. Verify it works
python cli.py scan
python cli.py test

# 4. Show the path you need for Cursor/Claude config
echo "Add this to your Cursor/Claude config:"
echo "python path: $(pwd)\mcp_server.py"
```

Then add to Cursor/Claude settings and restart!

---

Made with ❤️ - Questions? Open an issue on GitHub!