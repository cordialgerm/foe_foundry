import os
from pathlib import Path

from .documents import load_documents, load_monster_document_metas
from .graph import load_graph
from .search import index_documents


def _should_rebuild_search_index() -> bool:
    """Check if search index needs to be rebuilt based on cache freshness."""
    # Skip check if explicitly requested to skip
    if os.environ.get("SKIP_INDEX_REBUILD", "false").lower() == "true":
        return False

    index_dir = Path.cwd() / "cache" / "whoosh_indx"
    monsters_cache = Path.cwd() / "cache" / "monsters"
    documents_cache = Path.cwd() / "cache" / "documents"

    # If index doesn't exist, rebuild
    if not index_dir.exists():
        return True

    # If any cache directory is missing, rebuild
    if not monsters_cache.exists() or not documents_cache.exists():
        return True

    # Check if index is older than cache directories
    index_time = max((f.stat().st_mtime for f in index_dir.iterdir()), default=0)
    monsters_time = max(
        (f.stat().st_mtime for f in monsters_cache.iterdir()), default=0
    )
    documents_time = max(
        (f.stat().st_mtime for f in documents_cache.iterdir()), default=0
    )

    # Rebuild if index is older than any cache
    return index_time < max(monsters_time, documents_time)


def setup_indexes():
    """Set up all indexes for the search functionality."""
    print("Loading documents and metadata...")
    load_documents()
    load_monster_document_metas()

    print("Loading graph data...")
    load_graph()

    # Conditionally rebuild search index for performance
    if _should_rebuild_search_index():
        print("Search index needs rebuilding...")
        index_documents()
    else:
        print("Search index is up to date, skipping rebuild for performance.")
