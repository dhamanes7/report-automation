# Build with:  pyinstaller build_exe.spec
# Produces a single-folder (or --onefile, see below) offline executable.
# The client double-clicks the result — no Python, no pip, no internet, ever.

import streamlit
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

block_cipher = None

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
        ("sample_data", "sample_data"),
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
    [],
    exclude_binaries=True,
    name="HR_Reporting_Automation",
    debug=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="HR_Reporting_Automation",
)
