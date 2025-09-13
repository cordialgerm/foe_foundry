import logging
import shutil
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from whoosh.analysis import NgramWordAnalyzer, StemmingAnalyzer
from whoosh.fields import ID, TEXT, Schema
from whoosh.index import FileIndex, create_in, open_dir
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.query import Or, Term

from ..documents import DocType, Document, get_document, iter_documents

INDEX_DIR = Path.cwd() / "cache" / "whoosh_indx"
log = logging.getLogger(__name__)


@dataclass
class DocumentSearchResult:
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
    ngram_analyzer = NgramWordAnalyzer(minsize=2, maxsize=4)
    schema = Schema(
        doc_id=ID(stored=True),
        name=TEXT(sortable=True, stored=True),
        content_stemmed=TEXT(analyzer=StemmingAnalyzer(), stored=True),
        content_ngram=TEXT(analyzer=ngram_analyzer, stored=True),
    )

    INDEX_DIR.mkdir(exist_ok=True, parents=True)
    ix = create_in(str(INDEX_DIR), schema)
    writer = ix.writer()

    log.info(f"Indexing documents at {INDEX_DIR}...")
    for doc in iter_documents():
        writer.add_document(
            doc_id=doc.doc_id,
            name=doc.name,
            content_stemmed=doc.content.lower(),
            content_ngram=doc.content.lower(),
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


def search_documents(
    search_query: str, limit: int, doc_type_weights: dict[DocType, float] | None = None
) -> list[DocumentSearchResult]:
    """
    Search the document index and return detailed results with highlights.

    Args:
        search_query: The query string to search for.
        limit: The maximum number of documents to return.

    Returns:
        An iterable of SearchResult objects with match details and highlights.
    """

    if doc_type_weights is None:
        doc_type_weights = {}

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
            "content_stemmed",
            "content_ngram",
        ]
        fieldboosts = {
            "name": 3.0,
            "content_stemmed": 1.0,
            "content_ngram": 1.0,
        }

        # Phrase Search: split by comma, search each phrase
        phrase_results = []
        phrases = [p.strip() for p in search_query.split(",") if p.strip()]
        phrase_parser = MultifieldParser(
            fields, schema=ix.schema, fieldboosts=fieldboosts
        )
        for phrase in phrases:
            if phrase:
                phrase_query = phrase_parser.parse(f'"{phrase.lower()}"')
                results = searcher.search(phrase_query, limit=limit, terms=True)
                phrase_results.extend(results)

        # Ngram search: generate ngrams from query and search in content_ngram
        ngram_terms = set()
        for phrase in phrases:
            words = phrase.lower().replace(",", " ").split()
            for n in range(2, min(5, len(words) + 1)):
                for i in range(len(words) - n + 1):
                    ngram = " ".join(words[i : i + n])
                    ngram_terms.add(ngram)
        ngram_queries = [Term("content_ngram", ngram) for ngram in ngram_terms]
        ngram_results = []
        if ngram_queries:
            ngram_query = Or(ngram_queries)
            ngram_results = searcher.search(ngram_query, limit=limit, terms=True)

        # Individual term search (bag of words)
        or_parser = MultifieldParser(
            fields, schema=ix.schema, fieldboosts=fieldboosts, group=OrGroup
        )
        or_query = or_parser.parse(search_query.lower())
        or_results = searcher.search(or_query, limit=limit, terms=True)

        all_results = []
        result_ids = set()

        all_results.extend(
            process_results(
                phrase_results, result_ids, doc_type_weights, multiplier=2.0
            )
        )
        all_results.extend(
            process_results(ngram_results, result_ids, doc_type_weights, multiplier=1.5)
        )
        all_results.extend(process_results(or_results, result_ids, doc_type_weights))

    all_results.sort(key=lambda r: r.score, reverse=True)
    return all_results[:limit]


def process_results(
    results,
    result_ids: set[str],
    doc_type_weights: dict[DocType, float],
    multiplier: float = 1.0,
) -> list:
    all_results = []
    for result in results:
        doc_id = result["doc_id"]
        if doc_id in result_ids:
            continue

        doc = get_document(doc_id)
        if not doc:
            continue

        doc_type_weight = doc_type_weights.get(doc.doc_type, 1.0)
        score = multiplier * result.score * doc_type_weight  # type: ignore

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

        all_results.append(
            DocumentSearchResult(
                document=doc,
                score=score,
                matched_fields=matched_fields,
                matched_terms=decoded_terms,
                highlighted_match=highlighted_name
                if highlighted_name
                else highlighted_content,
            )
        )
        result_ids.add(doc_id)

    return all_results
