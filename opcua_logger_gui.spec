# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Analysis for the main GUI application
a = Analysis(
    ['opcua_logger_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.yaml', '.'),  # Include default config
        ('generate_cert.py', '.'),  # Certificate generation script
        ('json_to_csv.py', '.'),  # JSON to CSV conversion script
        ('opcua_logger.py', '.'),  # Main logger script
    ],
    hiddenimports=[
        'asyncua',
        'asyncua.client',
        'asyncua.common',
        'asyncua.crypto',
        'cryptography',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.asymmetric',
        'cryptography.hazmat.primitives.serialization',
        'cryptography.x509',
        'cryptography.x509.oid',
        'yaml',
        'pandas',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'queue',
        'threading',
        'subprocess',
        'datetime',
        'json',
        'csv',
        'os',
        'sys',
        'time',
        'typing',
        'base64',
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

# PYZ for the main application
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE for the main application
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OPCUALoggerGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='opcua_icon.ico' if os.path.exists('opcua_icon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)