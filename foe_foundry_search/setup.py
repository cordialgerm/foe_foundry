from .documents import load_documents, load_monster_document_metas
from .graph import load_graph
from .search import index_documents


def setup_indexes():
    """Set up all indexes for the search functionality."""

    load_documents()
    load_monster_document_metas()
    load_graph()
    index_documents()
