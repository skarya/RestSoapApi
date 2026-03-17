#!/bin/bash
# ============================================================
#   API Automation Framework - Build Script
#   Platforms : macOS  →  dist/ApiAutomation   (portable binary)
#               Linux  →  dist/ApiAutomation   (portable binary)
# ============================================================

set -e  # Exit on any error

# ── Detect platform ──────────────────────────────────────────
PLATFORM=$(uname -s)
case "$PLATFORM" in
  Darwin)
    PLATFORM_LABEL="macOS"
    EXT=""
    ;;
  Linux)
    PLATFORM_LABEL="Linux"
    EXT=""
    ;;
  *)
    echo "❌ Unsupported platform: $PLATFORM"
    echo "   Use build.bat on Windows."
    exit 1
    ;;
esac

echo "============================================================"
echo "  API Automation Framework - Build"
echo "  Platform : $PLATFORM_LABEL"
echo "============================================================"
echo

# ── [1/4] Clean previous builds ──────────────────────────────
echo "[1/4] Cleaning previous builds..."
rm -rf build/ dist/
echo "  Done."
echo

# ── [2/4] Install / upgrade dependencies ─────────────────────
echo "[2/4] Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "  Done."
echo

# ── [3/4] Build portable binary via PyInstaller spec ─────────
echo "[3/4] Building portable binary with PyInstaller..."

pyinstaller \
  --clean \
  --onefile \
  --name ApiAutomation \
  --add-data "data:data" \
  --hidden-import openpyxl \
  --hidden-import openpyxl.styles \
  --hidden-import openpyxl.utils \
  --hidden-import openpyxl.styles.fills \
  --hidden-import openpyxl.styles.alignment \
  --hidden-import openpyxl.styles.borders \
  --hidden-import pandas \
  --hidden-import aiohttp \
  --hidden-import aiohttp.connector \
  --hidden-import aiohttp.client \
  --hidden-import dotenv \
  $( [[ "$PLATFORM" == "Darwin" ]] && echo "--argv-emulation" ) \
  src/main.py

echo "  Done."
echo

# ── [4/4] Copy data folder next to the binary ─────────────────
echo "[4/4] Copying data folder to dist/..."
cp -r data dist/data
echo "  Done."
echo

# Make the binary executable
chmod +x dist/ApiAutomation

echo "============================================================"
echo "  ✅ BUILD COMPLETE!"
echo "  Platform   : $PLATFORM_LABEL"
echo "  Executable : dist/ApiAutomation"
echo "============================================================"
echo
echo "Usage:"
echo "  ./dist/ApiAutomation data/input/TestSuite_REST.json"
echo "  ./dist/ApiAutomation data/input/TestSuite_SOAP.json --parallel"
echo "  ./dist/ApiAutomation --rerun-failed"
echo
