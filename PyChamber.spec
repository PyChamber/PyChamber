# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata

datas = []
datas += collect_data_files('skrf')
datas += collect_data_files('aquarel')
datas += copy_metadata('pychamber')


block_cipher = None


a = Analysis(
    ['pychamber/launch.py'],
    pathex=['pychamber'],
    binaries=[],
    datas=datas,
    hiddenimports=['pyvisa_py', 'pyqtgraph.console.template_pyqt5'],
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

splash = Splash(
    './resources/splash.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=(10, 465),
    text_size=12,
    text_color='white'
)

exe = EXE(
    pyz,
    a.scripts,
    splash,
    splash.binaries,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PyChamber',
    icon='./resources/logo.png',
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