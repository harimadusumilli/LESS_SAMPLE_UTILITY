# Contract: `less search` Command

**Feature**: PDF Index and Search CLI  
**Command**: `less search "<query>"`  
**Status**: Specification

## Purpose

Search the vector database for text chunks most relevant to a user's natural language query, and return ranked results with source file references.

## CLI Interface

```
Usage: less search "<query>" [OPTIONS]

Arguments:
  <query>              Natural language query string (must be quoted if contains spaces)

Options:
  --index-path PATH    Custom path where the index database is stored (optional)
  --top-k N            Return top N results (default: 5)
  --threshold SCORE    Minimum relevance score to return (optional, default: none)
  -h, --help          Show this help message and exit

Examples:
  less search "project timeline"
  less search "budget allocation" --top-k 10
  less search "meeting notes" --index-path ~/.less/my_index
```

## Behavior

### Input Validation

1. **Query Required**: Return error if query is empty or whitespace-only.
   - Exit code: 1
   - Message: `"Error: Query cannot be empty."`

2. **Index Exists**: Return user-friendly error if no index is found.
   - Exit code: 1
   - Message: `"Error: No index found at '<path>'. Run 'less index <directory>' first."`

3. **Top-K Value**: Ensure --top-k is a positive integer.
   - Exit code: 1
   - Message: `"Error: --top-k must be a positive integer."`

### Search Process

1. **Check Index** (user feedback: `"Searching index..."`):
   - Verify the vector database exists and is accessible
   - Report if index is empty (no documents indexed)

2. **Query Processing** (internal, no user output):
   - Generate embedding for the query using ChromaDB's embedding model
   - Query ChromaDB for nearest neighbors

3. **Result Ranking** (user feedback: `"<N> results found."`):
   - Sort results by relevance score (descending)
   - Limit to top-k results
   - Apply optional relevance threshold filter

4. **Display Results**:
   - For each result, show: rank, file path, matching text snippet, relevance score
   - Provide context (e.g., page number if available from metadata)

### Error Handling

- **No Index Found**: Exit immediately, guide user to create an index
  - Message: `"Error: No index found. Run 'less index <directory>' to get started."`
  - Exit code: 1

- **Empty Index**: Return success but with a user-friendly message
  - Message: `"Query: '<query>'\nNo documents indexed. Run 'less index <directory>' to add documents."`
  - Exit code: 0

- **No Results Above Threshold**: Return success with an informative message
  - Message: `"Query: '<query>'\nNo results found. Try a broader query or index more documents."`
  - Exit code: 0

- **Query Processing Error**: Report and exit gracefully
  - Message: `"Error: Query processing failed. <reason>"`
  - Exit code: 1

### Output Format

Output is human-readable, line-oriented text suitable for terminal display.

```
Searching index...
Query: "project timeline"
5 results found.

1. File: /home/user/documents/project_plan.pdf
   Text: "The project timeline spans from January to June 2024."
   Score: 0.92

2. File: /home/user/documents/report2.pdf
   Text: "Timeline adjustments were made in March."
   Score: 0.78

3. File: /home/user/documents/status.pdf
   Text: "Current timeline is on schedule."
   Score: 0.71

...
```

**Alternate output when no results**:

```
Searching index...
Query: "nonexistent topic"
No results found. Try a broader query or index more documents.
```

## Data Model

**Input**:
- Query string (non-empty)
- Optional: custom index path, top-k count, relevance threshold

**Output**:
- List of SearchResult objects (ranked by relevance score)
- Summary message (count of results)

**Side Effects**:
- Reads from vector database only; no modifications

## Success Criteria

- Valid queries return relevant results from the index
- Results are ranked by relevance score
- File paths and text snippets are clearly displayed
- Empty queries are rejected with a clear message
- Missing index is detected and reported with actionable guidance
- CLI exits with code 0 on success or graceful failure, code 1 on errors
- Performance: search completes in reasonable time even with large indexes

## Assumptions

- ChromaDB embedding model is consistent between index and search time
- User queries are in the same language as indexed documents (English in v1)
- Relevance scores are meaningful for the chosen embedding model
- No real-time index updates; index must be recreated via `less index` for updates
