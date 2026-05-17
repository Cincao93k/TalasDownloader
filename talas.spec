# talas.spec
# ==========
# PyInstaller spec fajl za Talas Downloader.
# Pokreni: pyinstaller talas.spec
#
# Ovaj fajl govori PyInstaller-u šta da uključi u .exe

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Putanja do projekta
PROJECT_DIR = os.path.dirname(os.path.abspath(SPEC))

# ---- Šta uključiti kao DATA fajlove ----
datas = [
    # assets folder (ikone, slike)
    (os.path.join(PROJECT_DIR, 'assets'), 'assets'),
    # version.json
    (os.path.join(PROJECT_DIR, 'version.json'), '.'),
    # FFmpeg binaries - VAŽNO!
    (os.path.join(PROJECT_DIR, 'ffmpeg', 'ffmpeg.exe'), 'ffmpeg'),
    (os.path.join(PROJECT_DIR, 'ffmpeg', 'ffprobe.exe'), 'ffmpeg'),
]

# ---- yt-dlp data fajlovi ----
datas += collect_data_files('yt_dlp')

# ---- Hidden imports (moduli koje PyInstaller ne detektuje automatski) ----
hidden_imports = [
    'yt_dlp',
    'yt_dlp.extractor',
    'yt_dlp.extractor.youtube',
    'yt_dlp.postprocessor',
    'yt_dlp.postprocessor.ffmpeg',
    'certifi',
    'requests',
    'PIL',
    'PIL.Image',
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtWidgets',
    'PySide6.QtGui',
    'packaging',
    'packaging.version',
]

hidden_imports += collect_submodules('yt_dlp.extractor')

# ---- Analysis ----
a = Analysis(
    ['main.py'],
    pathex=[PROJECT_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Isključi nepotrebne module da smanjimo veličinu
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'tkinter',
        '_tkinter',
        'wx',
        'gtk',
        'unittest',
        'doctest',
        'pdb',
        'pydoc',
    ],
    noarchive=False,
    optimize=1,
)

# ---- PYZ arhiva ----
pyz = PYZ(a.pure)

# ---- EXE fajl ----
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TalasDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # UPX kompresija — smanji veličinu
    console=False,      # Bez crnog CMD prozora
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Ikonica aplikacije
    icon=os.path.join(PROJECT_DIR, 'assets', 'icon.ico'),
    # Metapodaci u .exe
    version_file=None,
)

# ---- COLLECT — skupi sve u jedan folder ----
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TalasDownloader',
)
