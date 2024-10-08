from dataclasses import dataclass
from pathlib import Path
import re
from collections.abc import Iterable
import json


@dataclass
class Creature:
    name: str
    creature_type: str
    text: str

    def to_dict(self) -> dict:
        return dict(
            type="monster",
            name=self.name,
            text=f"<Entity>monster</Entity><MonsterName>{self.name}</MonsterName><CreatureType>{self.creature_type}</CreatureType>.\n {self.text}",
        )


def creature_type(text: str):
    all_creature_types = [
        "Aberration",
        "Beast",
        "Celestial",
        "Construct",
        "Dragon",
        "Elemental",
        "Fey",
        "Fiend",
        "Giant",
        "Humanoid",
        "Monstrosity",
        "Ooze",
        "Plant",
        "Undead",
    ]

    regex = (
        r"\*?(?P<size>Tiny|Small|Large|Medium|Huge|Gargantuan) (?P<ct>[a-zA-Z]+).+\*?"
    )

    match = re.search(regex, text, re.MULTILINE)
    if match:
        return match.group("ct")

    ltxt = text.lower()
    creature_types = [ct for ct in all_creature_types if f"{ct}*".lower() in ltxt]
    if len(creature_types) != 1:
        return None
    return creature_types[0]


def iter_all_monsters() -> Iterable[Creature]:
    yield from iter_srd_md_monsters()
    yield from iter_artisinal_5e_md_monsters()
    yield from iter_open5e_monsters()


def load_all_monsters() -> list[Creature]:
    return list(iter_all_monsters())


def iter_srd_md_monsters() -> Iterable[Creature]:
    dir = Path(__file__).parent.parent.parent / "data" / "5esrd" / "Monsters"

    for monster_file in dir.glob("*.md"):
        try:
            with monster_file.open("r", encoding="utf-8") as f:
                monster = monster_file.name[:-3]
                if "(" in monster:
                    monster = monster.split("(")[0]
                monster = monster.strip()
                text = f.read()
                ct = creature_type(text)
                if ct is None:
                    raise ValueError("Cannot parse creature_type")

                yield Creature(name=monster, creature_type=ct, text=text)
        except Exception as x:
            print(f"UNABLE TO PARSE {monster_file}. {x}")


def iter_artisinal_5e_md_monsters() -> Iterable[Creature]:
    dir = Path(__file__).parent.parent.parent / "data" / "5e_artisinal_monsters"

    for monster_file in dir.glob("*.md"):
        with monster_file.open("r", encoding="utf-8") as f:
            try:
                monster = f.readline().replace("#", "").strip()
                f.seek(0)

                monster = monster_file.name[:-3]
                if "(" in monster:
                    monster = monster.split("(")[0]
                monster = monster.strip()
                text = f.read()
                ct = creature_type(text)
                if ct is None:
                    raise ValueError("Cannot parse creature type")

                yield Creature(name=monster, creature_type=ct, text=text)
            except Exception as x:
                print(f"ERROR IN ARTISINAL MONSTER: {monster_file}. {x}")


def iter_open5e_monsters() -> Iterable[Creature]:
    dir = Path(__file__).parent.parent.parent / "data" / "open5e" / "data"

    for creature_path in dir.rglob("**/Creature.json"):
        with creature_path.open("r", encoding="utf-8") as f:
            json_data = json.load(f)
            for item in json_data:
                name = item["fields"]["name"]
                creature_type = item["fields"]["type"]
                text = "\n".join(
                    [
                        f"{f}:{val}"
                        for f, val in item["fields"].items()
                        if val is not None
                    ]
                )
                yield Creature(name=name, creature_type=creature_type, text=text)
