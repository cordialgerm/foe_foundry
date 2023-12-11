import shutil
from pathlib import Path

from whoosh.fields import ID, KEYWORD, TEXT, Schema
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser

from foe_foundry.powers.all import AllPowers

from ...data.power import PowerModel

INDEX_DIR = Path(__file__).parent / "index"

PowerLookup = {power.key: PowerModel.from_power(power) for power in AllPowers}
Themes = {power.theme.lower() for power in AllPowers if power.theme}


def index_powers():
    schema = Schema(
        name=TEXT(sortable=True),
        key=ID(stored=True),
        creature_types=KEYWORD,
        roles=KEYWORD,
        theme=KEYWORD,
        damage_types=KEYWORD,
        tags=KEYWORD,
        description=TEXT,
    )

    INDEX_DIR.mkdir(exist_ok=True)
    ix = create_in(str(INDEX_DIR), schema)
    writer = ix.writer()

    for key, power in PowerLookup.items():
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
            creature_types=creature_types,
            roles=roles,
            theme=power.theme,
            damage_types=damage_types,
            tags=tags,
            description=fulldescription,
        )

    writer.commit()


def load_index():
    ix = open_dir(str(INDEX_DIR))
    return ix


def clean_index():
    shutil.rmtree(INDEX_DIR, ignore_errors=True)


def search(search_term: str, limit: int) -> list[PowerModel]:
    try:
        ix = load_index()
    except:
        index_powers()
        ix = load_index()

    with ix.searcher() as searcher:
        query = QueryParser("description", ix.schema).parse(search_term)
        results = searcher.search(query, limit=limit, sortedby="name")
        powers = []
        for result in results:
            key = result["key"]
            power = PowerLookup.get(key)
            if power:
                powers.append(power)

        return powers
