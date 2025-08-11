import logging
import shutil
from functools import cached_property
from pathlib import Path

from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import ID, KEYWORD, TEXT, Schema
from whoosh.index import FileIndex, create_in, open_dir
from whoosh.qparser import MultifieldParser

from .all import Powers
from .data import PowerModel

INDEX_DIR = Path(__file__).parent.parent.parent / "site" / "whoosh_indx"


class _IndexCache:
    @cached_property
    def index(self) -> FileIndex:
        return load_power_index()


log = logging.getLogger(__name__)
cache = _IndexCache()


def index_powers():
    schema = Schema(
        name=TEXT(sortable=True, analyzer=StemmingAnalyzer()),
        key=ID(stored=True),
        power_category=KEYWORD,
        creature_types=KEYWORD,
        roles=KEYWORD,
        theme=KEYWORD,
        damage_types=KEYWORD,
        tags=KEYWORD,
        description=TEXT(analyzer=StemmingAnalyzer()),
    )

    INDEX_DIR.mkdir(exist_ok=True, parents=True)
    ix = create_in(str(INDEX_DIR), schema)
    writer = ix.writer()

    log.info(f"Indexing powers at {INDEX_DIR}...")
    for key, power in Powers.PowerLookup.items():
        creature_types = " ".join(c for c in power.creature_types)
        roles = " ".join(r for r in power.roles)
        damage_types = " ".join(d for d in power.damage_types)
        tags = " ".join(t for t in power.tags)
        searchblob = " ".join(
            [power.name, power.feature_descriptions, tags, roles, damage_types]
        )

        writer.add_document(
            name=power.name,
            key=key,
            power_category=power.power_category,
            creature_types=creature_types,
            roles=roles,
            theme=power.theme,
            damage_types=damage_types,
            tags=tags,
            description=searchblob,
        )

    writer.commit()
    log.info("Indexing complete.")


def load_power_index() -> FileIndex:
    INDEX_DIR.mkdir(exist_ok=True, parents=True)
    log.info(f"Loading index from {INDEX_DIR}")
    ix = open_dir(str(INDEX_DIR))
    return ix


def clean_power_index():
    log.info(f"Cleaning index at {INDEX_DIR}...")
    shutil.rmtree(INDEX_DIR, ignore_errors=True)


def search_powers(search_term: str, limit: int) -> list[PowerModel]:
    try:
        ix = cache.index
    except Exception:
        log.exception("Error searching powers. Unable to load index. Re-indexing...")
        index_powers()
        ix = load_power_index()

    with ix.searcher() as searcher:
        # Define which fields to search and boost
        fields = [
            "name",
            "description",
            "tags",
            "roles",
            "creature_types",
            "damage_types",
        ]
        fieldboosts = {
            "name": 3.0,  # Power name is highly important
            "tags": 2.0,  # Tags are usually thematic and relevant
            "roles": 1.5,  # Moderate importance
            "description": 1.0,  # Default
            "creature_types": 1.2,  # Slight boost for thematic matching
            "damage_types": 1.2,  # Useful for keyword like "fire"
        }

        parser = MultifieldParser(fields, schema=ix.schema, fieldboosts=fieldboosts)
        query = parser.parse(search_term)

        # Perform the search
        results = searcher.search(query, limit=limit)
        powers = []
        for result in results:
            key = result["key"]
            power = Powers.PowerLookup.get(key)
            if power:
                powers.append(power)

        return powers
