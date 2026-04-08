# PyInstaller spec file for building less-search as a standalone executable.
#
# Usage (from the project root):
#   pip install pyinstaller
#   pyinstaller less_search.spec
#
# The resulting executable is written to:
#   dist/less-search          (Linux / macOS)
#   dist\less-search.exe      (Windows)

import sys
from PyInstaller.utils.hooks import collect_all, collect_data_files

# ------------------------------------------------------------------
# Collect hidden imports and data files required by heavy dependencies
# ------------------------------------------------------------------
chroma_datas, chroma_binaries, chroma_hiddenimports = collect_all("chromadb")
st_datas, st_binaries, st_hiddenimports = collect_all("sentence_transformers")
torch_datas, torch_binaries, torch_hiddenimports = collect_all("torch")

a = Analysis(
    ["less_sample_utility/cli.py"],
    pathex=["."],
    binaries=chroma_binaries + st_binaries + torch_binaries,
    datas=chroma_datas + st_datas + torch_datas,
    hiddenimports=(
        chroma_hiddenimports
        + st_hiddenimports
        + torch_hiddenimports
        + [
            "pypdf",
            "tqdm",
            "click",
        ]
    ),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="less-search",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    # Build a single self-contained file
    onefile=True,
    console=True,
)
