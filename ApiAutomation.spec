# -*- mode: python ; coding: utf-8 -*-
# ============================================================
#  ApiAutomation.spec  —  Cross-platform PyInstaller spec
#  Produces:
#    Windows  →  dist/ApiAutomation.exe
#    macOS    →  dist/ApiAutomation   (Mach-O binary)
#    Linux    →  dist/ApiAutomation   (ELF binary)
# ============================================================

import sys
import os

_is_mac   = sys.platform == "darwin"
_is_win   = sys.platform == "win32"
_is_linux = sys.platform.startswith("linux")

# ----------------------------------------------------------
#  Path separator for --add-data differs per platform:
#    Windows : "src;dest"
#    macOS /
#    Linux   : "src:dest"
# ----------------------------------------------------------
_sep = ";" if _is_win else ":"

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        (f'data{_sep}data',),   # bundle the entire data/ folder
    ],
    hiddenimports=[
        'openpyxl',
        'openpyxl.styles',
        'openpyxl.utils',
        'openpyxl.styles.fills',
        'openpyxl.styles.alignment',
        'openpyxl.styles.borders',
        'pandas',
        'aiohttp',
        'aiohttp.connector',
        'aiohttp.client',
        'dotenv',
        'python_dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ApiAutomation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    # macOS-specific: emulate sys.argv[0] being the real script path
    argv_emulation=_is_mac,
    target_arch=None,           # None → native arch; set 'universal2' for fat binary
    codesign_identity=None,     # set to your Apple Developer ID for signed binaries
    entitlements_file=None,
)
