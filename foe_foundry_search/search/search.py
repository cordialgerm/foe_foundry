from typing import Iterable

from ..documents import MonsterDocument, iter_monster_docs


def search_documents(query: str) -> Iterable[MonsterDocument]:
    """
    Search for documents matching the query.

    Args:
        query: The search query string.

    Returns:
        An iterable of matching Document objects.
    """
    # Normalize the query
    query = query.lower().strip()

    # Search in the monster documents
    for doc in iter_monster_docs():
        if query in doc.text.lower():
            yield doc
