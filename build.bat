@echo off
echo ============================================
echo   API Automation Framework - Build EXE
echo ============================================
echo.

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist ApiAutomation.spec del ApiAutomation.spec

echo [1/3] Installing dependencies...
pip install -r requirements.txt

echo.
echo [2/3] Building standalone executable with PyInstaller...
pyinstaller --onefile ^
  --name ApiAutomation ^
  --add-data "data;data" ^
  --hidden-import openpyxl ^
  --hidden-import openpyxl.styles ^
  --hidden-import openpyxl.utils ^
  --hidden-import pandas ^
  --hidden-import aiohttp ^
  --hidden-import dotenv ^
  src/main.py

echo.
echo [3/3] Copying data folder to dist...
xcopy /E /I /Y data dist\data

echo.
echo ============================================
echo   BUILD COMPLETE!
echo   Executable: dist\ApiAutomation.exe
echo ============================================
echo.
echo Usage:
echo   dist\ApiAutomation.exe data\input\TestSuite_REST.json
echo   dist\ApiAutomation.exe data\input\TestSuite_SOAP.json --parallel
echo   dist\ApiAutomation.exe --rerun-failed
echo.
pause
