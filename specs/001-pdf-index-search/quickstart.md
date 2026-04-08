# Quickstart: PDF Index and Search CLI

**Feature**: PDF Index and Search CLI  
**Created**: 2026-04-07

## Overview

This guide helps developers set up the development environment, understand the project structure, and run a quick test of both indexing and searching.

## Prerequisites

- **Python**: 3.10 or later
- **pip**: Python package manager
- **git**: For cloning the repository (if applicable)
- **Terminal**: Any shell (bash, zsh, PowerShell, cmd)

## Environment Setup

### 1. Clone or Navigate to Repository

```bash
cd c:\Projects\LESS
```

### 2. Create a Virtual Environment

```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# On Windows (cmd)
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected dependencies** (should be in `requirements.txt`):
- `chromadb>=0.3.21` - Vector database
- `pypdf>=3.0.0` - PDF text extraction
- `spacy>=3.0.0` - NLP and text chunking
- `pytest>=7.0.0` - Testing framework
- `pytest-cov` - Code coverage reporting

### 4. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

This downloads the English language model needed for sentence tokenization during indexing.

## Project Structure

```
src/
├── cli/
│   ├── main.py          # CLI entry point; parse commands
│   ├── index_cmd.py     # Index command implementation
│   └── search_cmd.py    # Search command implementation
├── models/
│   └── pdf_document.py  # Data classes and validation
├── services/
│   ├── pdf_processor.py # PDF extraction and chunking
│   ├── vector_db.py     # ChromaDB wrapper
│   └── search_engine.py # Query and ranking logic
└── utils/
    ├── feedback.py      # User-facing messages
    └── config.py        # Configuration (index path, etc.)

tests/
├── unit/
│   ├── test_pdf_processor.py
│   ├── test_vector_db.py
│   └── test_search_engine.py
├── integration/
│   ├── test_index_workflow.py
│   └── test_search_workflow.py
└── contract/
    ├── test_index_command.py
    └── test_search_command.py

docs/
├── architecture.md      # System design
└── cli-reference.md     # User documentation
```

## Running the Tool

### Start the CLI

```bash
# Make the CLI executable (on macOS/Linux)
chmod +x src/cli/main.py

# Run the index command (from repository root)
python -m src.cli.main index /path/to/pdf/directory

# Run the search command
python -m src.cli.main search "your query here"
```

**On Windows**, use:
```powershell
python -m src.cli.main index C:\path\to\pdf\directory
python -m src.cli.main search "your query here"
```

### Example Workflow

1. **Create a test directory with sample PDFs**:
   ```bash
   mkdir test_pdfs
   # Add a few PDF files to test_pdfs/
   ```

2. **Index the PDFs**:
   ```bash
   python -m src.cli.main index test_pdfs
   ```
   Expected output:
   ```
   Scanning directory: test_pdfs
   Found 3 PDF files.
   Processing: document1.pdf
   ✓ Indexed document1.pdf (45 chunks)
   ...
   Indexing complete. 3 files indexed, 128 chunks created.
   ```

3. **Search the index**:
   ```bash
   python -m src.cli.main search "summary of findings"
   ```
   Expected output:
   ```
   Searching index...
   Query: "summary of findings"
   3 results found.

   1. File: test_pdfs/document1.pdf
      Text: "Summary of findings shows an increase in efficiency."
      Score: 0.89
   ...
   ```

## Running Tests

### Unit Tests

```bash
pytest tests/unit/ -v
```

### Integration Tests

```bash
pytest tests/integration/ -v
```

### Contract Tests (CLI interface)

```bash
pytest tests/contract/ -v
```

### All Tests with Coverage

```bash
pytest --cov=src tests/ -v
```

## Troubleshooting

### spaCy Model Not Found

If you get an error about a missing spaCy model:
```bash
python -m spacy download en_core_web_sm
```

### Index Not Found

If `less search` says no index exists, run `less index` first:
```bash
python -m src.cli.main index /path/to/pdfs
```

### Permission Errors

Ensure the directory and its files are readable:
```bash
# On macOS/Linux
chmod -R u+r /path/to/pdfs
```

### ChromaDB Initialization Issues

ChromaDB stores index data locally. If you want to reset the index, delete the index directory (default: `~/.less/index/` or `.less/index/` in current directory) and re-run `less index`.

## Code Quality Checks

### Linting

```bash
# If using flake8
flake8 src tests --max-line-length=120

# If using pylint
pylint src tests
```

### Type Checking

```bash
mypy src --strict
```

### Code Formatting

```bash
black src tests
```

## Next Steps

1. **Read [data-model.md](data-model.md)** to understand entity definitions
2. **Review [contracts/](contracts/)** for detailed CLI specs
3. **Check [../src/](../src/) for source code structure**
4. **Run tests** to ensure everything functions correctly
5. **Contribute** by following the Constitution principles (code quality, comprehensive testing, UX consistency)

## Documentation Links

- [Data Model](data-model.md) - Entity definitions and relationships
- [Architecture](../docs/architecture.md) - System design overview
- [CLI Reference](../docs/cli-reference.md) - User-facing documentation
- [Index Command Contract](contracts/index-command.md) - Detailed spec
- [Search Command Contract](contracts/search-command.md) - Detailed spec

## Support

For issues, questions, or contributions, refer to the main repository README and the Constitution requirements for code quality and testing standards.
