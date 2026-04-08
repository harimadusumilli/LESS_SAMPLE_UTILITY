# Tasks: PDF Index and Search CLI

**Input**: Design documents from `specs/001-pdf-index-search/`
**Prerequisites**: spec.md ✅, plan.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- **File paths**: Exact locations where implementation goes

## Path Conventions

Single-project layout with structure per plan.md:
- `src/cli/`, `src/models/`, `src/services/`, `src/utils/`
- `tests/unit/`, `tests/integration/`, `tests/contract/`
- `docs/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan in src/, tests/, docs/
- [X] T002 [P] Initialize Python 3.10+ project with dependencies (requirements.txt with chromadb, pypdf, spacy, pytest)
- [ ] T003 [P] Configure development environment setup (linting, formatting, pre-commit hooks)
- [X] T004 [P] Download and cache spaCy English model (en_core_web_sm) for NLP sentence tokenization
- [X] T005 Create package markers (__init__.py) in src/cli/, src/models/, src/services/, src/utils/
- [X] T006 [P] Create tests/ package markers in tests/unit/, tests/integration/, tests/contract/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 [P] Create configuration module in src/utils/config.py (index path resolution, default settings)
- [X] T008 [P] Create feedback/logging module in src/utils/feedback.py (user-facing messages, exit codes)
- [X] T009 [P] Create ChromaDB wrapper (vector_db.py) initialization and connection in src/services/vector_db.py
- [X] T010 [P] Create data model classes in src/models/pdf_document.py (PDFDocument dataclass with validation)
- [X] T011 [P] Create SearchResult model in src/models/search_result.py (ranked match representation)
- [X] T012 [P] Create CLI argument parsing and main entry point in src/cli/main.py (dispatch to index_cmd, search_cmd)
- [X] T013 [P] Setup pytest fixtures and test utilities in tests/conftest.py (sample PDFs, mock ChromaDB, temp index)
- [X] T014 Create architecture documentation in docs/architecture.md (system design overview)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Index PDF files into the vector database (Priority: P1) 🎯 MVP

**Goal**: Implement the `less index <directory>` command to scan directories, extract PDF text, chunk into sentences, generate embeddings, and store in ChromaDB.

**Independent Test**: Run `less index <sample_dir>` on a folder with test PDFs and verify CLI reports progress, completes successfully, and produces an index.

### Contract Tests for User Story 1

- [X] T015 [P] [US1] Create contract test for index command in tests/contract/test_index_command.py (CLI argument parsing, exit codes)
- [X] T016 [P] [US1] Create contract test for index command output format in tests/contract/test_index_command.py (progress messages, error format)

### Unit Tests for User Story 1

- [X] T017 [P] [US1] Create unit test for PDF text extraction in tests/unit/test_pdf_processor.py (PyPDF integration, text recovery from PDFs)
- [X] T018 [P] [US1] Create unit test for sentence-level text chunking in tests/unit/test_pdf_processor.py (spaCy tokenization, empty/whitespace handling)
- [X] T019 [P] [US1] Create unit test for ChromaDB document storage in tests/unit/test_vector_db.py (add documents, update metadata)
- [X] T020 [P] [US1] Create unit test for directory scanning in tests/unit/test_pdf_processor.py (recursive PDF discovery, case-insensitive matching)

### Integration Tests for User Story 1

- [X] T021 [P] [US1] Create integration test for full index workflow in tests/integration/test_index_workflow.py (directory scan → extraction → chunking → storage)

### Implementation for User Story 1

- [X] T022 [P] [US1] Implement PDFProcessor.scan_directory() in src/services/pdf_processor.py (recursive PDF discovery, file filtering)
- [X] T023 [P] [US1] Implement PDFProcessor.extract_text() in src/services/pdf_processor.py (PyPDF text extraction with error handling)
- [X] T024 [P] [US1] Implement PDFProcessor.chunk_text() in src/services/pdf_processor.py (spaCy sentence tokenization, metadata tracking)
- [X] T025 [US1] Implement VectorDB.add_documents() in src/services/vector_db.py (ChromaDB storage, embedding generation)
- [X] T026 [US1] Implement VectorDB.update_metadata() in src/services/vector_db.py (track PDFDocument and IndexMetadata)
- [X] T027 [US1] Implement index command handler in src/cli/index_cmd.py (argument validation, orchestrate PDF processing, user feedback)
- [X] T028 [US1] Implement error handling for index command in src/cli/index_cmd.py (invalid directory, permission errors, disk space)
- [X] T029 [US1] Implement progress feedback in src/cli/index_cmd.py (scanning, processing per-file, completion summary)

**Checkpoint**: User Story 1 should be fully functional and independently testable

---

## Phase 4: User Story 2 - Search the indexed database (Priority: P2)

**Goal**: Implement the `less search "<query>"` command to query the vector database and return ranked, relevant results with source references.

**Independent Test**: Run `less search` after indexing and verify the CLI returns relevant results with source paths and completion status.

### Contract Tests for User Story 2

- [X] T030 [P] [US2] Create contract test for search command in tests/contract/test_search_command.py (argument parsing, options validation)
- [X] T030b [P] [US2] Create contract test for search output format in tests/contract/test_search_command.py (result ranking, score display, source paths)

### Unit Tests for User Story 2

- [ ] T031 [P] [US2] Create unit test for query embedding in tests/unit/test_search_engine.py (ChromaDB embedding consistency)
- [ ] T032 [P] [US2] Create unit test for search ranking in tests/unit/test_search_engine.py (relevance score sorting, top-k filtering)
- [ ] T033 [P] [US2] Create unit test for ChromaDB querying in tests/unit/test_vector_db.py (similarity search, metadata retrieval)

### Integration Tests for User Story 2

- [ ] T034 [P] [US2] Create integration test for full search workflow in tests/integration/test_search_workflow.py (query → embedding → search → ranking → display)

### Implementation for User Story 2

- [X] T035 [P] [US2] Implement SearchEngine.query() in src/services/search_engine.py (embedding generation, ChromaDB similarity search)
- [X] T036 [P] [US2] Implement SearchEngine.rank_results() in src/services/search_engine.py (score sorting, top-k selection, threshold filtering)
- [ ] T037 [US2] Implement VectorDB.search() in src/services/vector_db.py (ChromaDB query wrapper, metadata unpacking)
- [X] T038 [US2] Implement search command handler in src/cli/search_cmd.py (argument validation, query orchestration, result formatting)
- [ ] T039 [US2] Implement result display in src/cli/search_cmd.py (rank, file path, matching text, score, page number)
- [ ] T040 [US2] Implement search error handling in src/cli/search_cmd.py (no index, empty index, no results, invalid top-k)

**Checkpoint**: User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Report errors and cleanly exit on invalid input (Priority: P3)

**Goal**: Ensure robust error handling, user-facing guidance, and clean exit codes for all failure scenarios.

**Independent Test**: Run the CLI with invalid directories, missing indexes, and empty queries, verify clear error messages and correct exit codes.

### Contract Tests for User Story 3

- [ ] T041 [P] [US3] Create contract test for error handling in tests/contract/test_*_command.py (invalid inputs, missing resources, exit codes)
- [ ] T042 [P] [US3] Create contract test for error message formatting in tests/contract/test_*_command.py (user-friendly, no stack traces)

### Unit Tests for User Story 3

- [ ] T043 [P] [US3] Create unit test for input validation in tests/unit/test_pdf_processor.py (invalid paths, empty queries)
- [ ] T044 [P] [US3] Create unit test for graceful degradation in tests/unit/test_pdf_processor.py (corrupted PDFs, unreadable files)

### Integration Tests for User Story 3

- [ ] T045 [P] [US3] Create integration test for error workflows in tests/integration/test_error_handling.py (invalid index → repair or recreate)

### Implementation for User Story 3

- [ ] T046 [P] [US3] Add input validation to both commands in src/cli/main.py (directory exists, empty query check)
- [ ] T047 [P] [US3] Add file permission checks in src/services/pdf_processor.py (readable directory, readable files)
- [ ] T048 [US3] Add disk space checking in src/cli/index_cmd.py (graceful failure notification)
- [ ] T049 [US3] Add recovery guidance in error messages in src/utils/feedback.py (suggest `less index` if no index, etc.)
- [ ] T050 [US3] Ensure all error exits use correct codes in src/cli/index_cmd.py and src/cli/search_cmd.py (0 for success/empty, 1 for errors)

**Checkpoint**: All user stories should be independently functional with robust error handling

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T051 [P] Create user-facing CLI documentation in docs/cli-reference.md (command examples, option explanations)
- [ ] T052 Update architecture documentation with implementation details in docs/architecture.md
- [ ] T053 [P] Code cleanup and PEP 8 compliance across all src/ modules
- [ ] T054 [P] Add comprehensive docstrings to all public functions and classes
- [ ] T055 Run full test suite and verify coverage in tests/ (unit, integration, contract)
- [ ] T056 [P] Security review (input sanitization, path traversal prevention, no hardcoded secrets)
- [ ] T057 Performance testing for large PDF collections (index 100+ files, search on 1000+ chunks)
- [ ] T058 Validate quickstart.md against actual project structure and commands
- [ ] T059 Final commit and documentation of known limitations or future enhancements

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - Can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational - No dependencies on other stories
- **US2 (P2)**: Can start after Foundational - May integrate with US1 but independent test criteria
- **US3 (P3)**: Can start after Foundational - Cross-cutting error handling, all stories depend on it

### Within Each User Story

- Contract tests written FIRST and FAIL before implementation
- Unit tests for services before CLI implementation
- Integration tests after service implementations
- CLI handlers last (orchestrate already-tested components)

### Parallel Opportunities

**Phase 1 Setup**:
- T002, T003, T004, T005, T006 all [P] and independent

**Phase 2 Foundational**:
- T007-T013 all [P] (different files, can be parallel)
- T014 depends on T007-T013 being understood

**Phase 3 US1**:
- T015-T016 (contract tests, should fail first)
- T017-T020 (unit tests for services)
- T021 (integration test)
- T022-T024 (PDF processing services, parallel)
- T025-T026 (ChromaDB operations, parallel after services)
- T027-T029 (CLI handler, after services)

**Phase 4 US2**:
- T030-T030b (contract tests)
- T031-T033 (unit tests, parallel)
- T034 (integration test)
- T035-T036 (search service, parallel)
- T037 (ChromaDB integration)
- T038-T040 (CLI handler)

**Phase 5 US3**:
- T041-T042 (contract tests)
- T043-T044 (unit tests, parallel)
- T045 (integration test)
- T046-T050 (validation/error handling across CLI and services)

**Phase 6 Polish**:
- T051, T052, T053, T054, T056, T057 all [P]

---

## Parallel Example: User Story 1

```bash
# Write all tests first (should fail):
Task: T015 - contract test for index command
Task: T016 - contract test for index output format
Task: T017 - PDF extraction unit test
Task: T018 - sentence chunking unit test
Task: T019 - ChromaDB storage unit test
Task: T020 - directory scanning unit test

# Then implement services in parallel:
Task: T022 - scan_directory()
Task: T023 - extract_text()
Task: T024 - chunk_text()

# Then implement storage:
Task: T025 - add_documents()
Task: T026 - update_metadata()

# Finally integrate into CLI:
Task: T027 - index command handler
Task: T028 - error handling
Task: T029 - progress feedback

# Integration test validates entire flow:
Task: T021 - full index workflow
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (index)
4. **STOP and VALIDATE**: Test US1 independently
5. Demo/deploy if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Index) → Test independently → Deploy/Demo (MVP!)
3. Add US2 (Search) → Test independently → Deploy/Demo
4. Add US3 (Error handling) → Test independently → Deploy/Demo
5. Polish & cross-cutting → Final release

### Parallel Team Strategy

With 3 developers:

1. **Team together**: Phases 1 & 2 (Setup + Foundational)
2. **Once Foundational is done**:
   - **Developer A**: User Story 1 (Indexing) - tasks T015-T029
   - **Developer B**: User Story 2 (Searching) - tasks T030-T040
   - **Developer C**: User Story 3 (Error handling) + tests for A & B
3. Stories complete and integrate independently
4. **Team together**: Phase 6 (Polish)

---

## Notes

- [P] tasks = different files, no dependencies; can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Contract tests should fail before implementation (TDD)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks follow Constitution principles: code quality, comprehensive testing, UX consistency
