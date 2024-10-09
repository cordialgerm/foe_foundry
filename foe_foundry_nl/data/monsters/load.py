import json
import re
from collections.abc import Iterable
from pathlib import Path

from foe_foundry.creature_types import CreatureType

from .data import CanonicalMonster, MonsterInfo


def get_canonical_monsters() -> dict[str, CanonicalMonster]:
    # load SRD monsters
    srd_monsters = [m for m in iter_srd_md_monsters()]

    # load a5e and black flag monsters
    artisinal_monsters = [m for m in iter_artisinal_monster_markdown()]

    # load descriptions
    descriptions = get_5e_srd_monster_descriptions()

    # load natural language
    natural_language_descriptions = {}
    artisinal_dir = (
        Path(__file__).parent.parent.parent.parent / "data" / "5e_artisinal_monsters"
    )
    for nl_path, nl_text in iter_5e_monster_nl():
        artisinal_path = artisinal_dir / nl_path.name
        artisinal_monster = markdown_to_monster(
            artisinal_path, source="5e_artisinal_monsters"
        )
        key = artisinal_monster.key

        if key in natural_language_descriptions:
            natural_language_descriptions[key] += "\n\n" + nl_text
        else:
            natural_language_descriptions[key] = nl_text

    all_monster_keys = {m.key for m in srd_monsters} | {
        m.key for m in artisinal_monsters
    }
    lookups: dict[str, list[MonsterInfo]] = {m: [] for m in all_monster_keys}
    for monster in srd_monsters:
        lookups[monster.key].append(monster)
    for monster in artisinal_monsters:
        lookups[monster.key].append(monster)

    all_monsters = {}
    for key in all_monster_keys:
        monsters = lookups[key]

        srd = next((m for m in monsters if m.is_srd), None)
        if srd is None:
            artisinal = monsters[0]
        else:
            artisinal = next((m for m in monsters if m is not srd), srd)

        if srd is None and artisinal is None:
            raise ValueError("unexpected error")

        description = descriptions.get(key)
        natural_language = natural_language_descriptions.get(key)

        name = srd.name if srd is not None else artisinal.name
        creature_type = (
            srd.creature_type if srd is not None else artisinal.creature_type
        )

        if natural_language is not None:
            summary = natural_language.split("\n")[0]
        else:
            summary = None

        all_monsters[key] = CanonicalMonster(
            key=key,
            name=name,
            creature_type=creature_type,
            is_srd=srd is not None,
            infos=monsters,
            summary=summary,
            description=description,
            natural_language=natural_language,
        )

    return all_monsters


def creature_type_from_markdown(text: str):
    all_creature_types = CreatureType.all()

    first_lines = "\n".join(
        t.lower() for t in text.splitlines()[1:6]
    )  # skip title because of "Giant Elk" for example
    creature_types = [ct for ct in all_creature_types if ct.lower() in first_lines]
    if len(creature_types) == 0:
        return None
    else:
        return creature_types[0].title()


def name_to_key(name: str) -> str:
    key = name.lower()

    prefix = None
    if ", giant" in key:
        key = key.replace(", giant", "")
        prefix = "giant_"

    # Remove any text within parentheses
    key = re.sub(r"\s*\(.*?\)\s*", "", key)
    key = (
        key.replace(", ", "_")
        .replace(": ", "_")
        .replace(":", "_")
        .replace(",", "_")
        .replace(" ", "_")
        .replace("-", "_")
        .strip()
    )

    if prefix:
        key = prefix + key

    return key


def iter_srd_md_monsters() -> Iterable[MonsterInfo]:
    dir = Path(__file__).parent.parent.parent.parent / "data" / "5esrd" / "Monsters"

    for monster_file in dir.glob("*.md"):
        try:
            yield markdown_to_monster(monster_file, source="5e_srd", is_srd=True)
        except Exception as x:
            print(f"Unable to parse {monster_file}. {x}")


def iter_artisinal_monster_markdown() -> Iterable[MonsterInfo]:
    dir = Path(__file__).parent.parent.parent.parent / "data" / "5e_artisinal_monsters"

    for monster_file in dir.glob("*.md"):
        try:
            yield markdown_to_monster(
                monster_file, source="5e_artisinal_monsters", encoding="utf-8"
            )
        except Exception as x:
            print(f"Unable to parse {monster_file}. {x}")


def get_5e_srd_monster_descriptions() -> dict[str, str]:
    path = (
        Path(__file__).parent.parent.parent.parent
        / "data"
        / "custom"
        / "descriptions_5esrd.json"
    )

    descriptions = {}
    with path.open("r", encoding="utf-8") as f:
        creature_descriptions = json.load(f)
        for descr in creature_descriptions:
            name = descr["name"]
            key = name_to_key(name)
            description = descr["description"]
            descriptions[key] = description
    return descriptions


def markdown_to_monster(
    monster_path: Path, source: str, encoding="utf-8", is_srd: bool = False
) -> MonsterInfo:
    with monster_path.open("r", encoding=encoding) as f:
        monster_name = f.readline().replace("#", "").strip()
        f.seek(0)

        text = f.read()
        try:
            index = text.index("### License")
            text = text[:index]
        except ValueError:
            pass

        ct = creature_type_from_markdown(text)
        if ct is None:
            raise ValueError("Cannot parse creature_type")
        key = name_to_key(monster_name)

        return MonsterInfo(
            key=key,
            name=monster_name,
            creature_type=ct,
            source=source,
            path=monster_path,
            type="markdown",
            text=text,
            is_srd=is_srd,
        )


def iter_5e_monster_nl() -> Iterable[tuple[Path, str]]:
    dir = Path(__file__).parent.parent.parent.parent / "data" / "5e_nl"

    for monster_file in dir.glob("*.md"):
        try:
            yield monster_file, _read(monster_file)
        except Exception as x:
            print(f"Unable to load {monster_file}. {x}")


def _read(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        with path.open("r", encoding="cp1252") as f:
            return f.read()


def save_monsters():
    monsters = get_canonical_monsters()
    print(f"Loaded {len(monsters)} canonical monsters")
    dir = Path(__file__).parent.parent.parent.parent / "data" / "5e_canonical"
    for key, monster in monsters.items():
        path = dir / f"{key}.md"
        monster.save(path)
