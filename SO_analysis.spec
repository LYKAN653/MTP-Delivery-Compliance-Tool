# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['SO_analysis.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pandas', 'pandas._libs.tslibs.np_datetime', 'pandas._libs.tslibs.nattype', 'numpy', 'fuzzywuzzy', 'Levenshtein', 'openpyxl', 'tkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SalesOrderAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
