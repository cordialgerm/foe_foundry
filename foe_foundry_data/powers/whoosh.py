import shutil
from pathlib import Path

from whoosh.fields import ID, KEYWORD, TEXT, Schema
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser

from .all import Powers
from .data import PowerModel

INDEX_DIR = Path(__file__).parent.parent.parent / "site" / "whoosh_indx"


def index_powers():
    schema = Schema(
        name=TEXT(sortable=True),
        key=ID(stored=True),
        power_type=KEYWORD,
        creature_types=KEYWORD,
        roles=KEYWORD,
        theme=KEYWORD,
        damage_types=KEYWORD,
        tags=KEYWORD,
        description=TEXT,
    )

    INDEX_DIR.mkdir(exist_ok=True, parents=True)
    ix = create_in(str(INDEX_DIR), schema)
    writer = ix.writer()

    for key, power in Powers.PowerLookup.items():
        creature_types = " ".join(c for c in power.creature_types)
        roles = " ".join(r for r in power.roles)
        damage_types = " ".join(d for d in power.damage_types)
        tags = " ".join(t for t in power.tags)
        fulldescription = (
            f"{power.name} \n {tags} \n {power.key} \n\n {power.feature_descriptions}"
        )

        writer.add_document(
            name=power.name,
            key=key,
            power_type=power.power_type,
            creature_types=creature_types,
            roles=roles,
            theme=power.theme,
            damage_types=damage_types,
            tags=tags,
            description=fulldescription,
        )

    writer.commit()


def load_power_index():
    INDEX_DIR.mkdir(exist_ok=True, parents=True)
    ix = open_dir(str(INDEX_DIR))
    return ix


def clean_power_index():
    shutil.rmtree(INDEX_DIR, ignore_errors=True)


def search_powers(search_term: str, limit: int) -> list[PowerModel]:
    try:
        ix = load_power_index()
    except Exception:
        index_powers()
        ix = load_power_index()

    with ix.searcher() as searcher:
        query = QueryParser("description", ix.schema).parse(search_term)
        results = searcher.search(query, limit=limit, sortedby="name")
        powers = []
        for result in results:
            key = result["key"]
            power = Powers.PowerLookup.get(key)
            if power:
                powers.append(power)

        return powers
