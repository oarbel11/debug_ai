@echo off
REM ════════════════════════════════════════════════════════════════
REM                  DEBUG AI - Windows Setup
REM                  Double-click to run!
REM ════════════════════════════════════════════════════════════════

echo.
echo ============================================================
echo    Debug AI - Setup Wizard
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo         Install from https://python.org
    pause
    exit /b 1
)
echo [OK] Python found

REM Install packages
echo.
echo Installing packages...
pip install duckdb pandas mcp --quiet
echo [OK] Packages installed

REM Get database path
echo.
echo ============================================================
echo    Step 1: Database Path
echo ============================================================
echo.
echo Enter the FULL path to your .duckdb file:
echo Example: C:\Data\warehouse.duckdb
echo.
set /p DB_PATH="Database path: "

REM Get SQL folder path
echo.
echo ============================================================
echo    Step 2: SQL Files Path
echo ============================================================
echo.
echo Enter the FULL path to your SQL files folder:
echo Example: C:\Data\etl\transformations
echo.
set /p SQL_PATH="SQL folder path: "

REM Initialize
echo.
echo [RUNNING] Initializing...
python scripts/cli.py init --db "%DB_PATH%" --sql "%SQL_PATH%"

REM Build metadata
echo.
echo [RUNNING] Building metadata from SQL files...
python scripts/cli.py build

REM Verify
echo.
echo [RUNNING] Scanning database...
python scripts/cli.py scan

REM Test
echo.
echo [RUNNING] Running tests...
python scripts/cli.py test

REM Show Cursor config
echo.
echo ============================================================
echo    Setup Complete!
echo ============================================================
echo.
echo Add this to your Cursor settings (Ctrl+Shift+P, "settings json"):
echo.
echo {
echo   "mcpServers": {
echo     "debug-ai": {
echo       "command": "python",
echo       "args": ["%CD:\=\\%\\mcp_server.py"]
echo     }
echo   }
echo }
echo.
echo Then restart Cursor and start chatting!
echo.
echo See SETUP.md for detailed instructions.
echo.
pause