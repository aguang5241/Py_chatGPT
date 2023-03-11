# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)

datas = []

binaries = [('/Users/aguang/Coding/Py_chatGPT/python_venv/lib/python3.9/site-packages/speech_recognition/flac-mac', './speech_recognition/flac-mac')]

hookspath=['pyinstaller-hooks/']

block_cipher = None


a = Analysis(
    ['Super_Assistant.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=['pyinstaller-hooks/'],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Super_Assistant',
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
app = BUNDLE(
    exe,
    name='Super_Assistant.app',
    icon=None,
    bundle_identifier=None,
)
