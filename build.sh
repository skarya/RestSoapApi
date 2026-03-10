#!/bin/bash
# ============================================
#   API Automation Framework - Build Script
#   Supports: macOS and Linux
# ============================================

set -e  # Exit on any error

echo "============================================"
echo "  API Automation Framework - Build"
echo "  Platform: $(uname -s)"
echo "============================================"
echo

# Detect platform
PLATFORM=$(uname -s)
if [[ "$PLATFORM" == "Darwin" ]]; then
    EXT=""
    PLATFORM_LABEL="macOS"
elif [[ "$PLATFORM" == "Linux" ]]; then
    EXT=""
    PLATFORM_LABEL="Linux"
else
    echo "Unsupported platform: $PLATFORM"
    exit 1
fi

# Clean previous builds
echo "[1/3] Cleaning previous builds..."
rm -rf build/ dist/

# Install dependencies
echo
echo "[2/3] Installing dependencies..."
pip install -r requirements.txt

# Build with PyInstaller
echo
echo "[3/3] Building standalone executable with PyInstaller..."
pyinstaller --onefile \
  --name ApiAutomation \
  --add-data "data:data" \
  --hidden-import openpyxl \
  --hidden-import openpyxl.styles \
  --hidden-import openpyxl.utils \
  --hidden-import pandas \
  --hidden-import aiohttp \
  --hidden-import dotenv \
  src/main.py

# Copy data folder to dist
echo
echo "Copying data folder to dist..."
cp -r data dist/data

echo
echo "============================================"
echo "  BUILD COMPLETE!"
echo "  Platform   : $PLATFORM_LABEL"
echo "  Executable : dist/ApiAutomation"
echo "============================================"
echo
echo "Usage:"
echo "  ./dist/ApiAutomation data/input/TestSuite_REST.json"
echo "  ./dist/ApiAutomation data/input/TestSuite_SOAP.json --parallel"
echo "  ./dist/ApiAutomation data/input/TestSuite_REST.json data/input/TestSuite_SOAP.json"
echo
