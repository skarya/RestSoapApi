@echo off
echo ============================================================
echo   API Automation Framework - Build EXE  (Windows)
echo ============================================================
echo.

REM ── [1/4] Clean previous builds ──────────────────────────────
echo [1/4] Cleaning previous builds...
if exist dist   rmdir /s /q dist
if exist build  rmdir /s /q build
echo   Done.
echo.

REM ── [2/4] Install / upgrade dependencies ─────────────────────
echo [2/4] Installing dependencies...
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo   Done.
echo.

REM ── [3/4] Build standalone .exe via PyInstaller ───────────────
echo [3/4] Building standalone .exe with PyInstaller...
pyinstaller --clean --onefile ^
  --name ApiAutomation ^
  --add-data "data;data" ^
  --hidden-import openpyxl ^
  --hidden-import openpyxl.styles ^
  --hidden-import openpyxl.utils ^
  --hidden-import openpyxl.styles.fills ^
  --hidden-import openpyxl.styles.alignment ^
  --hidden-import openpyxl.styles.borders ^
  --hidden-import pandas ^
  --hidden-import aiohttp ^
  --hidden-import aiohttp.connector ^
  --hidden-import aiohttp.client ^
  --hidden-import dotenv ^
  src/main.py
echo   Done.
echo.

REM ── [4/4] Copy data folder next to the executable ─────────────
echo [4/4] Copying data folder to dist\...
xcopy /E /I /Y data dist\data > nul
echo   Done.
echo.

echo ============================================================
echo   BUILD COMPLETE!
echo   Platform   : Windows
echo   Executable : dist\ApiAutomation.exe
echo ============================================================
echo.
echo Usage:
echo   dist\ApiAutomation.exe data\input\TestSuite_REST.json
echo   dist\ApiAutomation.exe data\input\TestSuite_SOAP.json --parallel
echo   dist\ApiAutomation.exe --rerun-failed
echo.
pause
