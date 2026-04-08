"""Command-line interface for the LESS Sample Utility RAG PDF search tool."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from tqdm import tqdm

from less_sample_utility.pdf_processor import process_pdf, process_pdf_directory
from less_sample_utility.search import SemanticSearch
from less_sample_utility.vector_store import VectorStore

PERSIST_DIR = "chroma_db"


@click.group()
def cli() -> None:
    """LESS Sample Utility – semantic PDF search powered by ChromaDB."""


# ---------------------------------------------------------------------------
# ingest
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--chunk-size",
    default=500,
    show_default=True,
    help="Maximum number of characters per chunk.",
)
@click.option(
    "--chunk-overlap",
    default=50,
    show_default=True,
    help="Character overlap between consecutive chunks.",
)
@click.option(
    "--persist-dir",
    default=PERSIST_DIR,
    show_default=True,
    help="ChromaDB persistence directory.",
)
def ingest(path: str, chunk_size: int, chunk_overlap: int, persist_dir: str) -> None:
    """Ingest a PDF file or a directory of PDFs into the vector store.

    PATH can be a single .pdf file or a directory containing .pdf files.
    """
    input_path = Path(path)
    store = VectorStore(persist_dir=persist_dir)

    if input_path.is_dir():
        click.echo(f"Scanning directory: {input_path}")
        pdf_chunks = process_pdf_directory(
            input_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        if not pdf_chunks:
            click.echo("No PDF files found in the directory.", err=True)
            sys.exit(1)
        for filename, chunks in tqdm(pdf_chunks.items(), desc="Ingesting PDFs"):
            store.add_chunks(chunks, source=filename)
            click.echo(f"  ✓ {filename}: {len(chunks)} chunks")
    else:
        chunks = process_pdf(input_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        store.add_chunks(chunks, source=input_path.name)
        click.echo(f"✓ Ingested {input_path.name}: {len(chunks)} chunks")

    click.echo(f"\nTotal documents in store: {store.count()}")


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("query")
@click.option(
    "--n-results",
    default=5,
    show_default=True,
    help="Number of results to return.",
)
@click.option(
    "--source",
    default=None,
    help="Restrict results to a specific source PDF filename.",
)
@click.option(
    "--persist-dir",
    default=PERSIST_DIR,
    show_default=True,
    help="ChromaDB persistence directory.",
)
def search(query: str, n_results: int, source: str | None, persist_dir: str) -> None:
    """Search the vector store using a natural-language QUERY."""
    searcher = SemanticSearch(persist_dir=persist_dir)

    if searcher.store.count() == 0:
        click.echo("The vector store is empty. Run `ingest` first.", err=True)
        sys.exit(1)

    results = searcher.search(query, n_results=n_results, source_filter=source)

    if not results:
        click.echo("No results found.")
        return

    for i, result in enumerate(results, start=1):
        click.echo(f"\n{'='*60}")
        click.echo(f"Result {i}  |  source: {result.source}  |  chunk: {result.chunk_index}  |  distance: {result.distance:.4f}")
        click.echo(f"{'='*60}")
        click.echo(result.document)


# ---------------------------------------------------------------------------
# clear
# ---------------------------------------------------------------------------

@cli.command()
@click.option(
    "--persist-dir",
    default=PERSIST_DIR,
    show_default=True,
    help="ChromaDB persistence directory.",
)
@click.confirmation_option(prompt="This will delete all ingested data. Are you sure?")
def clear(persist_dir: str) -> None:
    """Clear all documents from the vector store."""
    store = VectorStore(persist_dir=persist_dir)
    store.delete_collection()
    click.echo("Vector store cleared.")


if __name__ == "__main__":
    cli()
