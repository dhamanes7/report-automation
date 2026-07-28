# Build with:  pyinstaller build_exe.spec
#   normal windowed build (for the client):   pyinstaller build_exe.spec
#   debug build with a visible console:       DEBUG_BUILD=1 pyinstaller build_exe.spec
#
# Produces a single portable .exe (onefile) — offline, no Python, no pip,
# nothing else to extract or keep alongside it. The client just double-clicks it.
#
# The debug build is for diagnosing a silent failure on the client's machine:
# it opens a console window so you can see the actual traceback instead of the
# window just closing. Use the normal build for anything you hand to the client.

import os

import streamlit
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

block_cipher = None

DEBUG_BUILD = os.environ.get("DEBUG_BUILD") == "1"

streamlit_datas = collect_data_files("streamlit")
streamlit_hidden = collect_submodules("streamlit")
# streamlit.version reads its own package metadata via importlib.metadata at import
# time; PyInstaller doesn't bundle .dist-info by default, so without this the frozen
# exe crashes on startup with "No package metadata was found for streamlit".
streamlit_metadata = copy_metadata("streamlit")

a = Analysis(
    ["run_app.py"],
    pathex=[],
    binaries=[],
    datas=streamlit_datas + streamlit_metadata + [
        ("app.py", "."),
        ("sample_config.json", "."),
        ("engine", "engine"),
    ],
    hiddenimports=streamlit_hidden + ["engine", "engine.config_loader",
                                       "engine.addition_deletion", "engine.monthly_accrual"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Report_Automation_debug" if DEBUG_BUILD else "Report_Automation",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=DEBUG_BUILD,
    icon="assets/app_icon.ico",
)
