# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Get current directory
current_dir = Path.cwd()

a = Analysis(
    ['main.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=[
        ('*.py', '.'),
        ('../config.py', '.'),
        ('../credentials.py', '.'),
        ('../comment_remover.py', '.'),
    ],
    hiddenimports=[
        'playwright',
        'playwright.async_api',
        'playwright._impl',
        'tkinter',
        'tkinter.messagebox',
        'tkinter.ttk',
        'pyperclip',
        'keyboard',
        'asyncio',
        'threading',
        'json',
        'requests',
        'sqlite3',
        'ctypes',
        're',
        'time',
        'datetime',
        'pathlib',
        'os',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CodeTantraAutomation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
