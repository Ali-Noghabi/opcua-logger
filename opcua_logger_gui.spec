# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for OPC UA Logger GUI
Creates standalone executable for Windows, Linux, and macOS
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(SPEC))

block_cipher = None

a = Analysis(
    ['opcua_logger_gui.py'],
    pathex=[current_dir],
    binaries=[],
    datas=[
        ('config.yaml', '.'),
        ('generate_cert.py', '.'),
        ('jsonl_to_csv.py', '.'),
        ('opcua_logger.py', '.'),
        ('sample_tags.csv', '.'),
    ],
    hiddenimports=[
        'asyncua',
        'asyncua.client',
        'asyncua.common.methods',
        'asyncua.crypto',
        'cryptography',
        'yaml',
        'pandas',
        'tkinter',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.filedialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OPCUALoggerGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='opcua_icon.ico' if sys.platform == 'win32' else None,
)

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='OPCUALoggerGUI.app',
        icon=None,  # macOS uses .icns files, not .ico
        bundle_identifier='com.opcua.logger',
        info_plist={
            'CFBundleName': 'OPC UA Logger GUI',
            'CFBundleDisplayName': 'OPC UA Logger GUI',
            'CFBundleVersion': '1.2.0',
            'CFBundleShortVersionString': '1.2.0',
            'NSHighResolutionCapable': 'True',
            'LSUIElement': 'False',
        },
    )
elif sys.platform == 'win32':
    # For Windows, create single executable
    coll = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        name='OPCUALoggerGUI',
        debug=False,
        strip=False,
        upx=True,
        console=False,
        icon='opcua_icon.ico',
    )
else:
    # For Linux, create single executable
    coll = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        name='OPCUALoggerGUI',
        debug=False,
        strip=False,
        upx=True,
        console=False,
    )

# AppImage specific configuration for Linux
if '--appimage' in sys.argv:
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='OPCUALoggerGUI',
        debug=False,
        bootloader_ignore_signals=False,
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    
    # For AppImage, we need a different structure
    app = BUNDLE(
        coll,
        name='OPCUALoggerGUI.AppImage',
        icon=None,
        bundle_identifier=None,
        info_plist=None,
        version=None,
    )