# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [('src/app', 'app'), ('src', 'src'), ('data', 'data')]
datas += collect_data_files('matplotlib')
datas += collect_data_files('numpy')


a = Analysis(
    ['piacere_main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['sqlite3', 'logging.handlers', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'PySide6.QtPrintSupport', 'matplotlib', 'matplotlib.backends.backend_qt5agg', 'matplotlib.backends.backend_agg', 'matplotlib.figure', 'numpy', 'numpy.core', 'numpy.core._multiarray_umath', 'PIL', 'PIL.Image', 'pyparsing', 'cycler', 'kiwisolver', 'contourpy', 'packaging'],
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
    name='Piacere',
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
)
