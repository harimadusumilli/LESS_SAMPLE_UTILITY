# Contract: `less index` Command

**Feature**: PDF Index and Search CLI  
**Command**: `less index <directory>`  
**Status**: Specification

## Purpose

Scan a directory for PDF files, extract text using PyPDF, chunk the text into sentences using spaCy, generate embeddings using ChromaDB, and store the results in a local vector database.

## CLI Interface

```
Usage: less index <directory> [OPTIONS]

Arguments:
  <directory>          Path to directory containing PDF files to index

Options:
  --index-path PATH    Custom path where the index database is stored (optional)
  --force              Reindex all files, even if already indexed (optional)
  --verbose            Print detailed progress for each file (optional)
  -h, --help          Show this help message and exit

Examples:
  less index /path/to/documents
  less index . --force
  less index ~/reports --index-path ~/.less/my_index
```

## Behavior

### Input Validation

1. **Directory Exists**: Return user-friendly error if the directory path does not exist or is not readable.
   - Exit code: 1
   - Message: `"Error: Directory '<path>' not found or not readable."`

2. **Empty Directory**: If directory contains no PDF files, report cleanly without error.
   - Exit code: 0
   - Message: `"No PDF files found in '<path>'. Index unchanged."`

3. **Invalid Characters**: Handle paths with spaces and special characters correctly.

### Indexing Process

1. **Directory Scan** (user feedback: `"Scanning directory..."`):
   - Recursively discover all files with `.pdf` extension (case-insensitive)
   - Count discovered files and report to user

2. **File Processing Loop** (user feedback for each: `"Processing: <filename>"` then `"✓ Indexed <filename>" or "✗ Failed to index <filename>"`):
   - For each PDF:
     - Read file into memory (handle failures gracefully)
     - Extract text using PyPDF (handle corrupted PDFs by skipping or reporting partial results)
     - Chunk text into sentences using spaCy
     - Generate embeddings via ChromaDB
     - Store chunks and metadata
     - Report progress to user

3. **Completion** (user feedback: `"Indexing complete. <N> files indexed, <M> chunks created."`):
   - Report summary: total files indexed, total chunks created
   - Exit code: 0

### Error Handling

- **Unreadable PDF**: Skip the file, report in summary, continue processing other files
  - Message in progress: `"✗ Failed to index <filename>: <reason>"`
  - Message in summary: `"1 file failed to process"`
  - Exit code: 0 (partial success is acceptable)

- **No Read Permission on Directory**: Exit immediately
  - Message: `"Error: Directory '<path>' is not readable. Check permissions."`
  - Exit code: 1

- **Disk Full**: Report error and stop gracefully
  - Message: `"Error: Not enough disk space to store index."`
  - Exit code: 1

### Output Format

Output is line-oriented, human-readable text suitable for Terminal display.

```
Scanning directory: /home/user/documents
Found 42 PDF files.
Processing: report1.pdf
✓ Indexed report1.pdf (125 chunks)
Processing: report2.pdf
✓ Indexed report2.pdf (89 chunks)
Processing: invalid.pdf
✗ Failed to index invalid.pdf: Corrupted PDF structure
...
Indexing complete. 41 files indexed, 5423 chunks created.
```

## Data Model

**Input**:
- Directory path (string)
- Optional: custom index path, force flag, verbose flag

**Output**:
- Vector database updated with new PDFDocuments and TextChunks
- IndexMetadata updated with total counts and timestamp

**Side Effects**:
- Creates or updates local ChromaDB index
- Writes to filesystem at the specified index path

## Success Criteria

- All valid PDF files in the directory are discovered
- Text extraction completes without crashing the CLI
- User receives clear, step-by-step feedback
- Index is stored and retrievable by the `less search` command
- CLI exits with code 0 on success or partial success, code 1 on total failure

## Assumptions

- Directory paths may contain spaces and special characters
- PDF files may be large (100+ MB); memory usage should be reasonable
- spaCy model is pre-downloaded and available (e.g., `en_core_web_sm`)
- ChromaDB is available and working
