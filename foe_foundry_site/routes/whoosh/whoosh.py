from pathlib import Path

from whoosh.fields import ID, KEYWORD, TEXT, Schema
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser

from foe_foundry.powers.creatures import aberration, beast, celestial, construct

from ...data.power import PowerModel

# TODO - add all powers
AllPowers = (
    aberration.AberrationPowers
    + beast.BeastPowers
    + celestial.CelestialPowers
    + construct.ConstructPowers
)
_lookup = {power.key: PowerModel.from_power(power) for power in AllPowers}


def index_powers():
    schema = Schema(
        name=TEXT,
        key=ID(stored=True),
        creature_types=KEYWORD,
        roles=KEYWORD,
        damage_types=KEYWORD,
        description=TEXT,
    )

    dir = Path(__file__).parent / "index"
    dir.mkdir(exist_ok=True)
    ix = create_in(str(dir), schema)
    writer = ix.writer()

    for key, power in _lookup.items():
        writer.add_document(
            name=power.name,
            key=key,
            creature_types=" ".join(c for c in power.creature_types),
            roles=" ".join(r for r in power.roles),
            damage_types=" ".join(d for d in power.damage_types),
            description=power.feature_descriptions,
        )

    writer.commit()


def load_index():
    dir = Path(__file__).parent / "index"
    ix = open_dir(str(dir))
    return ix


def search(search_term: str, limit: int) -> list[PowerModel]:
    try:
        ix = load_index()
    except:
        index_powers()
        ix = load_index()

    with ix.searcher() as searcher:
        query = QueryParser("description", ix.schema).parse(search_term)
        results = searcher.search(query, limit=limit)
        powers = []
        for result in results:
            key = result["key"]
            power = _lookup.get(key)
            if power:
                powers.append(power)

        return powers
