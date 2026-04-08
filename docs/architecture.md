# LESS Architecture

## System Overview

LESS is a command-line tool for indexing PDF files and performing semantic search over their contents. It uses ChromaDB for vector storage and spaCy for natural language processing.

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Layer (main.py)                   │
│  - Argument parsing (argparse)                           │
│  - Command routing & validation                          │
│  - Error handling & user feedback                        │
└─────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴────────────┐
                │                          │
    ┌───────────▼──────────┐   ┌──────────▼──────────┐
    │   Index Handler      │   │   Search Handler    │
    │  (index_cmd.py)      │   │  (search_cmd.py)    │
    │                      │   │                     │
    │  - Scans directory   │   │  - Validates query  │
    │  - Extracts PDFs     │   │  - Searches index   │
    │  - Stores embeddings │   │  - Formats results  │
    └───────────┬──────────┘   └──────────┬──────────┘
                │                          │
    ┌───────────▼──────────┐   ┌──────────▼──────────┐
    │     Services Layer    │   │    Services Layer    │
    │  ┌────────────────┐   │   │  ┌────────────────┐  │
    │  │ PDFProcessor   │   │   │  │ SearchEngine   │  │
    │  ├────────────────┤   │   │  ├────────────────┤  │
    │  │ - scan()       │   │   │  │ - query()      │  │
    │  │ - extract()    │   │   │  │ - rank()       │  │
    │  │ - chunk()      │   │   │  │ - filter()     │  │
    │  └────────────────┘   │   │  └────────────────┘  │
    │  ┌────────────────┐   │   │                      │
    │  │   VectorDB     │   │   │                      │
    │  ├────────────────┤   │   │                      │
    │  │ - add()        │   │   │                      │
    │  │ - search()     │   │   │                      │
    │  │ - delete()     │   │   │                      │
    │  └────────────────┘   │   │                      │
    └───────────┬──────────┘   └──────────┬──────────┘
                │                          │
                └─────────────┬────────────┘
                              │
                ┌─────────────▼──────────────────┐
                │      Data Models (models/)     │
                │  - PDFDocument                 │
                │  - SearchResult                │
                │  - TextChunk (implicit)        │
                └─────────────┬──────────────────┘
                              │
                ┌─────────────▼──────────────────┐
                │   Persistence Layer            │
                │  - ChromaDB (vector storage)   │
                │  - Local filesystem            │
                │  - duckdb+parquet backend      │
                └────────────────────────────────┘
```

## Module Breakdown

### CLI Layer (`src/cli/`)

#### main.py
- **Purpose**: Entry point, argument parsing, command dispatch
- **Key Classes/Functions**:
  - `create_parser()`: Builds argparse parser with subcommands
  - `validate_index_command()`: Validates index arguments
  - `validate_search_command()`: Validates search arguments
  - `main()`: Entry point that routes to handlers
- **Responsibilities**:
  - Parse command-line arguments
  - Validate arguments before passing to handlers
  - Route to appropriate command handler
  - Handle top-level errors gracefully

#### index_cmd.py (Phase 3 - User Story 1)
- **Purpose**: Implement `less index <directory>` command
- **Key Functions**:
  - `handle_index()`: Main handler for index command
  - **Coordinates**: PDFProcessor → VectorDB → Feedback
- **Responsibilities**:
  - Orchestrate directory scanning
  - Show progress feedback to user
  - Collect results and report summary
  - Return appropriate exit codes

#### search_cmd.py (Phase 4 - User Story 2)
- **Purpose**: Implement `less search "<query>"` command
- **Key Functions**:
  - `handle_search()`: Main handler for search command
  - **Coordinates**: SearchEngine → VectorDB → Feedback
- **Responsibilities**:
  - Query the indexed documents
  - Format and display results
  - Handle no-results scenario
  - Return appropriate exit codes

### Services Layer (`src/services/`)

#### vector_db.py
- **Purpose**: Wrapper around ChromaDB for consistent interface
- **Key Class**: `VectorDB`
  - `__init__(index_path)`: Initialize with persistent storage
  - `add_documents(ids, metadatas, documents)`: Store chunks with embeddings
  - `search(query_text, n_results, min_score)`: Semantic search
  - `get_collection_stats()`: Get index statistics
  - `delete_document(document_id)`: Remove a document's chunks
  - `clear_index()`: Remove all documents
  - `persist()`: Explicitly flush to disk
- **Dependencies**: chromadb
- **Responsibilities**:
  - Manage ChromaDB client lifecycle
  - Store/retrieve embeddings
  - Handle semantic search queries
  - Provide stats for CLI feedback

#### pdf_processor.py (Phase 3 - User Story 1)
- **Purpose**: Extract text from PDFs and chunk into sentences
- **Key Functions**:
  - `scan_directory(path, recursive=True)`: Find all PDF files
  - `extract_text(pdf_path)`: Get text from PDF using PyPDF
  - `chunk_text(text)`: Split into sentences using spaCy
  - `process_document(pdf_path)`: Coordinate extraction + chunking
- **Dependencies**: pypdf, spacy (en_core_web_sm)
- **Responsibilities**:
  - Locate PDF files recursively
  - Extract text from PDFs robustly
  - Segment text into sentence-level chunks
  - Handle various PDF formats and corruptions

#### search_engine.py (Phase 4 - User Story 2)
- **Purpose**: Query execution and result ranking
- **Key Functions**:
  - `execute_query(query, vector_db, top_k, threshold)`: Run search
  - `rank_results(raw_results)`: Sort by relevance
  - `format_results(ranked, max_chars=100)`: Prepare for display
- **Dependencies**: VectorDB
- **Responsibilities**:
  - Execute semantic search queries
  - Rank results by relevance score
  - Convert ChromaDB distances to similarity scores
  - Format for user display

### Models Layer (`src/models/`)

#### pdf_document.py
- **Purpose**: Metadata tracking for indexed PDFs
- **Key Class**: `PDFDocument`
  - **Attributes**:
    - `file_path`: Path to PDF on disk
    - `filename`: Just the filename
    - `file_size_bytes`: Size in bytes
    - `id`: Unique identifier
    - `indexed_at`: Timestamp
    - `extraction_status`: PENDING/IN_PROGRESS/SUCCESS/FAILED/PARTIAL
    - `extraction_error`: Error message if failed
    - `total_chunks`: Number of chunks indexed
  - **Methods**:
    - `__post_init__()`: Validates file exists and readable
    - `mark_indexed(chunks)`: Set as successfully indexed
    - `mark_failed(error)`: Set as failed
    - `mark_partial(chunks, error)`: Set as partially indexed
    - `to_dict()`: Serialize for storage
- **Responsibilities**:
  - Track document metadata
  - Validate file access
  - Store extraction status
  - Provide serialization

#### search_result.py
- **Purpose**: Ranked search result for display
- **Key Class**: `SearchResult`
  - **Attributes**:
    - `chunk_id`: Identifier of matching chunk
    - `document_id`: Source document ID
    - `file_path`: Path to PDF
    - `matching_text`: Text snippet
    - `relevance_score`: 0.0-1.0 (higher = better)
    - `rank`: Position in results (1-based)
    - `page_number`: Optional page reference
  - **Methods**:
    - `__post_init__()`: Validates all fields
    - `to_dict()`: Serialize for storage
    - `formatted_snippet(max_length=100)`: Truncated text for display
- **Responsibilities**:
  - Represent a single result
  - Validate result data
  - Provide formatting for CLI display

### Utilities Layer (`src/utils/`)

#### config.py
- **Purpose**: Configuration and environment setup
- **Key Class**: `Config`
  - `get_index_path(custom_path)`: Resolve index location
    - Precedence: custom arg → LESS_INDEX_PATH env var → ~/.less/index
  - `ensure_index_directory(index_path)`: Create and validate
- **Responsibilities**:
  - Centralize configuration
  - Handle environment variables
  - Validate paths and permissions
  - Provide defaults

#### feedback.py
- **Purpose**: User-facing messages and exit codes
- **Key Classes**:
  - `ExitCode`: Enum with SUCCESS=0, ERROR=1
  - `Feedback`: Base class for all output
  - `IndexFeedback`: Index-specific messages
  - `SearchFeedback`: Search-specific messages
  - `ErrorMessages`: Standardized error strings
  - `exit_with_error()`: Print error and exit
  - `exit_success()`: Print message and exit
- **Responsibilities**:
  - Consistent message formatting
  - Proper output stream selection (stdout/stderr)
  - User-friendly error messages
  - Exit code standardization

### Testing Layer (`tests/`)

#### tests/conftest.py
- **Purpose**: pytest fixtures and shared test setup
- **Key Fixtures**:
  - `temp_index_dir`: Temporary ChromaDB directory
  - `sample_pdf_path`: Minimal valid PDF file
  - `mock_vector_db`: Mocked VectorDB
  - `sample_query`: Test query string
  - `sample_search_results`: ChromaDB response format
  - `sample_pdf_documents`: Document metadata
  - `mock_chroma_client`: Mocked ChromaDB client
  - `config_with_temp_index`: Config with temp paths

#### tests/contract/
- **Purpose**: CLI interface contract testing
- Tests that verify command-line behavior matches specification
- Contract tests written FIRST (TDD)
- Tests validate:
  - Argument parsing
  - Error message formatting
  - Exit codes
  - Output structure

#### tests/unit/
- **Purpose**: Component unit tests
- **Coverage**:
  - Config module (path resolution)
  - VectorDB wrapper (CRUD operations)
  - Models (validation, serialization)
  - Services (extraction, search logic)

#### tests/integration/
- **Purpose**: End-to-end workflow tests
- **Scenarios**:
  - Full index workflow (scan → extract → embed → store)
  - Full search workflow (query → embed → search → rank)

## Data Flow

### Indexing Flow

```
User: less index /path/to/pdfs

    ↓

[main.py] Parse arguments → validate → call handle_index()

    ↓

[index_cmd.py] handle_index()
    - Initializes VectorDB(index_path)
    - Calls pdf_processor.scan_directory()
    
        ↓
    
    [pdf_processor.py] For each PDF:
        - extract_text() → PyPDF extracts page text
        - chunk_text() → spaCy chunks into sentences
        - Creates metadata with document_id, page_number
    
        ↓
    
    [vector_db.py] VectorDB.add_documents()
        - Calls ChromaDB.add(ids, metadatas, documents)
        - ChromaDB auto-generates embeddings
        - Persists to duckdb+parquet backend
    
    ↓

[feedback.py] Report: "✓ Indexed file.pdf (25 chunks)"

    ↓

User sees summary: "Indexing complete. 5 files indexed, 125 chunks created."
```

### Search Flow

```
User: less search "machine learning algorithms"

    ↓

[main.py] Parse arguments → validate → call handle_search()

    ↓

[search_cmd.py] handle_search()
    - Validates query non-empty
    - Initializes VectorDB(index_path)
    - Calls search_engine.execute_query()
    
        ↓
    
    [search_engine.py] execute_query()
        - Calls VectorDB.search(query_text, n_results=5)
    
            ↓
        
        [vector_db.py] VectorDB.search()
            - Calls ChromaDB.query() with query_text
            - ChromaDB embeds query, computes similarity
            - Returns ids, documents, metadatas, distances
    
        ↓
    
    search_engine.rank_results() → Sort by score
    
    ↓

[feedback.py] For each result:
    - print_result_item(rank, file_path, text, score)

    ↓

User sees: "1. File: analysis.pdf\n   Text: ...\n   Score: 0.92"
```

## Dependency Injection Pattern

The handlers (index_cmd, search_cmd) receive services as parameters:

```python
def handle_index(directory: Path, index_path: Optional[str] = None, ...):
    config = Config.get_index_path(index_path)
    vector_db = VectorDB(config)
    processor = PDFProcessor()
    
    # Services are initialized fresh, not globally
    # This enables testing with mocks
```

This pattern allows:
- Easy mocking in tests
- No global state
- Parallel test execution
- Configuration flexibility

## Error Handling Strategy

1. **Validation Layer** (main.py, handlers): Reject bad arguments early
2. **Service Layer**: Catch low-level errors, re-raise with context
3. **Handler Layer**: Catch service errors, convert to feedback + exit code
4. **CLI Layer**: Catch all unhandled errors, display generic message

```
User input
    ↓
Validation (main.py) → ValueError → ExitCode.INVALID_INPUT
    ↓
Service call → OSError → Custom error message → ExitCode.ERROR
    ↓
Unhandled exception → "Something went wrong" → ExitCode.ERROR
```

## Storage Architecture

### ChromaDB Backend

- **Type**: duckdb+parquet (local, persistent)
- **Location**: `~/.less/index/` (configurable)
- **Collection**: `pdf_documents`
- **Auto-features**:
  - Automatic embedding generation (default: all-MiniLM-L6-v2)
  - Persistent on disk
  - In-memory cache for performance
  - Automatic index maintenance

### Data Structure

```
ChromaDB Collection: pdf_documents
├── IDs: [chunk_001, chunk_002, ..., chunk_NNN]
├── Documents: ["Text of chunk 1", "Text of chunk 2", ...]
├── Metadatas:
│   ├── chunk_001: {
│   │   document_id: "doc_001",
│   │   file_path: "/path/to/file.pdf",
│   │   page_number: 1
│   │ }
│   └── ... (more chunks)
└── Embeddings: (auto-generated, not returned in search)
```

## Resilience Features

1. **Partial Indexing**: Continue even if some files fail
2. **Duplicate Handling**: Overwrite chunks with `--force`
3. **Permission Errors**: Skip unreadable files, report count
4. **PDF Corruption**: Use PyPDF error handling, mark as FAILED
5. **Disk Space**: Validate before adding, report if full
6. **Query Failures**: Report "no results" instead of crashing

## Configuration & Extensibility

### Future Extensions (Phase 6 +)

1. **Authentication**: Add index access control
2. **Incremental Updates**: Track document hashes, skip unchanged files
3. **Custom Embeddings**: Allow swapping embedding models
4. **Distributed Search**: Add PostgreSQL backend option
5. **Web Interface**: Add HTTP API wrapper
6. **Batch Operations**: Add `less import` for bulk loading

### Configuration Points

- Index path (env var: LESS_INDEX_PATH)
- Embedding model (currently hardcoded, could be configurable)
- Chunk size (currently spaCy sentences, could be tokens)
- Search threshold (--threshold flag)
- Result count (--top-k flag)

## Testing Strategy

### Test Pyramid

```
         △
        ╱ ╲     Integration Tests (5 tests)
       ╱   ╲    - Full workflow end-to-end
      ╱─────╲
     ╱       ╲   Unit Tests (30+ tests)
    ╱         ╱ - Component validation
   ╱─────────╱  - Service logic
  ╱___________╲
 Contract Tests (10+ tests)
 - CLI interface compliance
```

### Test Layers (TDD Order)

1. **Contract Tests**: Write FIRST, verify CLI behavior matches spec
2. **Unit Tests**: Mock dependencies, test components in isolation
3. **Integration Tests**: End-to-end workflows with real ChromaDB

## Performance Considerations

1. **Lazy Loading**: VectorDB client initialized only when needed
2. **Batch Operations**: ChromaDB add/search optimized for batches
3. **Sentence Chunking**: Semantic boundaries preserve meaning while limiting embedding count
4. **Index Filtering**: `--threshold` reduces result processing
5. **Caching**: ChromaDB caches frequently accessed embeddings

---

**Last Updated**: 2026-04-07  
**Architecture Version**: 1.0  
**Status**: Design Phase Complete
