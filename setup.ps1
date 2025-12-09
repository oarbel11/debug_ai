# ════════════════════════════════════════════════════════════════
#                   DEBUG AI - PowerShell Setup
#        Run: powershell -ExecutionPolicy Bypass .\setup.ps1
# ════════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Debug AI - Setup Wizard" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $null = python --version 2>&1
    Write-Host "[OK] Python found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found!" -ForegroundColor Red
    Write-Host "        Install from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install packages
Write-Host ""
Write-Host "Installing packages..." -ForegroundColor Yellow
pip install duckdb pandas mcp --quiet
Write-Host "[OK] Packages installed" -ForegroundColor Green

# Get database path
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Step 1: Database Path" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Enter the FULL path to your .duckdb file:"
Write-Host "Example: C:\Data\warehouse.duckdb" -ForegroundColor Gray
Write-Host ""
$dbPath = Read-Host "Database path"

# Get SQL folder path
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Step 2: SQL Files Path" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Enter the FULL path to your SQL files folder:"
Write-Host "Example: C:\Data\etl\transformations" -ForegroundColor Gray
Write-Host ""
$sqlPath = Read-Host "SQL folder path"

# Initialize
Write-Host ""
Write-Host "[RUNNING] Initializing..." -ForegroundColor Yellow
python scripts/cli.py init --db $dbPath --sql $sqlPath

# Build metadata
Write-Host ""
Write-Host "[RUNNING] Building metadata from SQL files..." -ForegroundColor Yellow
python scripts/cli.py build

# Verify
Write-Host ""
Write-Host "[RUNNING] Scanning database..." -ForegroundColor Yellow
python scripts/cli.py scan

# Test
Write-Host ""
Write-Host "[RUNNING] Running tests..." -ForegroundColor Yellow
python scripts/cli.py test

# Show Cursor config
$escapedPath = (Get-Location).Path -replace '\\', '\\'
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "   Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Add this to your Cursor settings (Ctrl+Shift+P, 'settings json'):" -ForegroundColor White
Write-Host ""
Write-Host '{' -ForegroundColor Cyan
Write-Host '  "mcpServers": {' -ForegroundColor Cyan
Write-Host '    "debug-ai": {' -ForegroundColor Cyan
Write-Host '      "command": "python",' -ForegroundColor Cyan
Write-Host "      `"args`": [`"$escapedPath\\mcp_server.py`"]" -ForegroundColor Cyan
Write-Host '    }' -ForegroundColor Cyan
Write-Host '  }' -ForegroundColor Cyan
Write-Host '}' -ForegroundColor Cyan
Write-Host ""
Write-Host "Then restart Cursor and start chatting!" -ForegroundColor White
Write-Host ""
Write-Host "See SETUP.md for detailed instructions." -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to exit"