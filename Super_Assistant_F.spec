# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)

datas = [('/Users/aguang/Coding/Py_chatGPT/python_venv/lib/python3.9/site-packages/whisper/assets/gpt2/*.txt', './whisper/assets/gpt2'),
        ('/Users/aguang/Coding/Py_chatGPT/python_venv/lib/python3.9/site-packages/whisper/assets/gpt2/*json', './whisper/assets/gpt2'),
        ('/Users/aguang/Coding/Py_chatGPT/python_venv/lib/python3.9/site-packages/whisper/assets/multilingual/*json', './whisper/assets/multilingual'),
        ('/Users/aguang/Coding/Py_chatGPT/python_venv/lib/python3.9/site-packages/whisper/assets/multilingual/*txt', './whisper/assets/multilingual'),
        ('/Users/aguang/Coding/Py_chatGPT/python_venv/lib/python3.9/site-packages/whisper/assets/*npz', './whisper/assets'),]

datas += copy_metadata('tqdm')
datas += copy_metadata('regex')
datas += copy_metadata('requests')
datas += copy_metadata('packaging')
datas += copy_metadata('filelock')
datas += copy_metadata('numpy')
datas += copy_metadata('tokenizers')
datas += copy_metadata('torch')

binaries = []

hookspath=[]

block_cipher = None

a = Analysis(
    ['Super_Assistant.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=hookspath,
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    hooksconfig={},
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
