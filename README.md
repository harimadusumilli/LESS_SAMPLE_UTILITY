# LESS_SAMPLE_UTILITY
Did this project for learning to code with the spec kit and used github copilot to build a simple RAG based DB using Chroma DB for chunking and storing all pdfs text, so that, I can get to search based of the meaning and context instead of doing a keyword search

---

## Installation (run from source)

```bash
pip install -r requirements.txt
pip install -e .
less-search --help
```

## CLI usage

```bash
# Ingest a PDF (or a whole folder of PDFs)
less-search ingest path/to/file.pdf
less-search ingest path/to/pdf_folder/

# Search by meaning / context
less-search search "what are the termination clauses?"

# Clear the vector store
less-search clear
```

---

## Building a standalone executable (`.exe` / binary)

PyInstaller bundles the tool and all its dependencies into a single file that
runs on any machine **without** a Python installation.

### Prerequisites

```bash
pip install pyinstaller
```

> **Note:** build on the **same OS** you want to deploy to (Windows → `.exe`,
> Linux → Linux binary, macOS → macOS binary).

### Build

```bash
# From the project root
pyinstaller less_search.spec
```

The output is written to the `dist/` folder:

| OS      | Executable                  |
|---------|-----------------------------|
| Windows | `dist\less-search.exe`      |
| Linux   | `dist/less-search`          |
| macOS   | `dist/less-search`          |

### Run the built executable

```bash
# Windows
dist\less-search.exe ingest C:\docs\contract.pdf
dist\less-search.exe search "termination clause"

# Linux / macOS
./dist/less-search ingest ~/docs/contract.pdf
./dist/less-search search "termination clause"
```

### Tips

* The first run is slower because the embedding model is loaded from disk.
* The `chroma_db/` folder (vector store) is created in the **current working
  directory** unless you pass `--persist-dir`.
* To reduce the binary size, exclude unused torch extensions in the spec file
  (`excludes` list).
