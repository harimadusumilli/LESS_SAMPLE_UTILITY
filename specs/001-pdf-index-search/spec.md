# Feature Specification: PDF Index and Search CLI

**Feature Branch**: `001-pdf-index-search`  
**Created**: 2026-04-07  
**Status**: Draft  
**Input**: User description: "LESS will be a command-line tool with just two commands, at least to start. One command will index all PDF files in a given directory into the vector database. The other will search a query against that database and return the most relevant results. When a command is executed, the application should provide clear, step by step feedback about what it’s doing. Once the task is complete, or if any errors occur, it should exit cleanly."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Index PDF files into the vector database (Priority: P1)

A user runs the CLI `less index <directory>` to scan a directory, discover PDF files, and ingest their content into a local vector database.

**Why this priority**: Indexing documents is the core capability needed before searches can return relevant results.

**Independent Test**: Run the `less index` command on a sample folder with at least one PDF and verify the CLI reports each step, completes successfully, and produces an index artifact.

**Acceptance Scenarios**:

1. **Given** a directory containing PDF files, **when** the user runs `less index <directory>`, **then** the CLI displays step-by-step progress, processes each PDF, and reports completion.
2. **Given** a directory with no PDFs, **when** the user runs `less index <directory>`, **then** the CLI reports that no PDF files were found and exits cleanly with a clear message.

---

### User Story 2 - Search the indexed database (Priority: P2)

A user runs the CLI `less search "<query>"` to retrieve the most relevant PDF-based results from the previously created vector database.

**Why this priority**: Search is the primary value of the tool once documents are indexed.

**Independent Test**: Run `less search` after indexing and verify the CLI returns relevant results with source references and a clean completion status.

**Acceptance Scenarios**:

1. **Given** an existing index, **when** the user runs `less search "project summary"`, **then** the CLI returns the top matching results with document locations and brief relevance context.

---

### User Story 3 - Report errors and cleanly exit on invalid input (Priority: P3)

A user provides an invalid directory path, missing index, or unsupported input, and the CLI responds with a clear error message and exits without crashing.

**Why this priority**: Reliable error handling ensures users understand failures and can correct their commands without confusion.

**Independent Test**: Run the CLI with an invalid directory and a missing index, then verify the output describes the issue and the process exits cleanly.

**Acceptance Scenarios**:

1. **Given** a non-existent path, **when** the user runs `less index <invalid-path>`, **then** the CLI reports the directory is unavailable and exits with a user-facing error.
2. **Given** no index exists, **when** the user runs `less search "query"`, **then** the CLI reports that no indexed database is available and suggests indexing first.

---

### Edge Cases

- What happens when a PDF file is corrupted or unreadable during indexing?
- How does the CLI behave when the directory is accessible but contains zero PDF files?
- How does the system handle an empty or whitespace-only search query?
- How does the CLI report progress when indexing large collections of PDF files?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The CLI MUST provide an `index` command that accepts a directory path and discovers all PDF files inside that directory.
- **FR-002**: The `index` command MUST process each PDF and store searchable vector data in a local vector database artifact.
- **FR-003**: The CLI MUST provide a `search` command that accepts a query string and returns the most relevant results from the current index.
- **FR-004**: Both commands MUST emit clear, step-by-step feedback describing what the application is doing and what completed successfully.
- **FR-005**: The CLI MUST exit cleanly after each command, reporting success or failure without dumping raw stack traces.
- **FR-006**: The tool MUST return a user-facing error when inputs are invalid, missing, or when the index is unavailable.
- **FR-007**: The CLI MUST operate as a command-line utility only, without requiring persistent background services for these two commands.

### Key Entities *(include if feature involves data)*

- **PDF Document**: Represents a discovered PDF file, its path, and the extracted content used to build search vectors.
- **Vector Database**: Represents the local searchable store containing vector embeddings, document metadata, and references to source PDFs.
- **Search Result**: Represents a ranked match returned for a query, including source document location and relevance context.
- **Operation Feedback**: Represents the step-by-step messages shown to the user during indexing and searching.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can index a directory of PDFs and receive progress feedback at each major step, with the command completing successfully in a single run.
- **SC-002**: Users can search the indexed database and receive the top relevant results with source references for a valid query.
- **SC-003**: The CLI exits cleanly after success or error, and non-zero exit codes are used only for failure conditions.
- **SC-004**: Error conditions such as invalid directories, missing indexes, or unreadable PDFs are reported with clear user-facing messages.

## Assumptions

- The tool is delivered as a CLI-only application for the initial version.
- The vector database is stored locally and managed by the tool, not by an external service.
- PDF indexing runs on demand via the `index` command and does not require continuous monitoring.
- No authentication or remote PDF ingestion is required for the first release.
- Command output is intended for terminal users and may include progress phrases such as "Scanning directory", "Indexing file", "Saving index", and "Search complete."
