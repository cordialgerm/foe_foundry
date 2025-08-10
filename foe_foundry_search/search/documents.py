import logging
import shutil
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Iterable

from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import ID, TEXT, Schema
from whoosh.index import FileIndex, create_in, open_dir
from whoosh.qparser import MultifieldParser

from ..documents import Document, get_document, iter_documents

INDEX_DIR = Path.cwd() / "cache" / "whoosh_indx"
log = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """
    A search result containing the document, score, and match metadata.
    """

    document: Document
    score: float
    matched_fields: list[
        str
    ]  # Fields that matched the query (e.g., ['name', 'content'])
    matched_terms: list[tuple[str, str]]  # (field, term) pairs that matched
    highlighted_match: str | None  # Highlighted content with match markers


class _IndexCache:
    @cached_property
    def index(self) -> FileIndex:
        INDEX_DIR.mkdir(exist_ok=True, parents=True)
        log.info(f"Loading index from {INDEX_DIR}")
        ix = open_dir(str(INDEX_DIR))
        return ix


_cache = _IndexCache()


def index_documents():
    """
    Index all documents for search.
    """

    schema = Schema(
        doc_id=ID(stored=True),
        name=TEXT(sortable=True, stored=True),
        content=TEXT(analyzer=StemmingAnalyzer(), stored=True),
    )

    INDEX_DIR.mkdir(exist_ok=True, parents=True)
    ix = create_in(str(INDEX_DIR), schema)
    writer = ix.writer()

    log.info(f"Indexing documents at {INDEX_DIR}...")
    for doc in iter_documents():
        writer.add_document(
            doc_id=doc.doc_id, name=doc.name, content=doc.content.lower()
        )

    writer.commit()
    log.info("Indexing complete.")


def load_document_index() -> FileIndex:
    """Load the document index from the cache."""
    return _cache.index


def clean_document_index():
    """Clear the document index cache."""
    log.info(f"Removing index at {INDEX_DIR}...")
    shutil.rmtree(INDEX_DIR, ignore_errors=True)


def search_documents(search_query: str, limit: int) -> Iterable[SearchResult]:
    """
    Search the document index and return detailed results with highlights.

    Args:
        search_query: The query string to search for.
        limit: The maximum number of documents to return.

    Returns:
        An iterable of SearchResult objects with match details and highlights.
    """

    try:
        ix = _cache.index
    except Exception:
        log.exception("Error retrieving document index. Re-indexing...")
        index_documents()
        ix = _cache.index

    with ix.searcher() as searcher:
        # Define which fields to search and boost
        fields = [
            "name",
            "content",
        ]
        fieldboosts = {
            "name": 3.0,
            "content": 1.0,
        }

        parser = MultifieldParser(fields, schema=ix.schema, fieldboosts=fieldboosts)
        query = parser.parse(search_query.lower())

        # Perform the search with terms=True to enable matched_terms()
        results = searcher.search(query, limit=limit, terms=True)
        for result in results:
            doc_id = result["doc_id"]
            doc = get_document(doc_id)

            if not doc:
                continue

            score: float = result.score  # type: ignore
            # Get match details
            matched_terms = list(result.matched_terms())
            matched_fields = list(
                {
                    field.decode() if isinstance(field, bytes) else field
                    for field, term in matched_terms
                }
            )

            # Decode matched terms
            decoded_terms = [
                (
                    field.decode() if isinstance(field, bytes) else field,
                    term.decode() if isinstance(term, bytes) else term,
                )
                for field, term in matched_terms
            ]

            # Get highlights
            highlighted_name = None
            highlighted_content = None

            try:
                if "name" in matched_fields:
                    highlighted_name = result.highlights("name")
            except Exception:
                pass

            try:
                if "content" in matched_fields:
                    highlighted_content = result.highlights("content")
            except Exception:
                pass

            yield SearchResult(
                document=doc,
                score=score,
                matched_fields=matched_fields,
                matched_terms=decoded_terms,
                highlighted_match=highlighted_name
                if highlighted_name
                else highlighted_content,
            )
