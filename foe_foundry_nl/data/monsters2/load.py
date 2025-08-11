import json
from collections.abc import Iterable
from functools import cached_property
from pathlib import Path

from foe_foundry import CreatureType, DamageType, MonsterRole

from ..paragraph import TrainingParagraph
from ..utils import name_to_key
from .data import MonsterInfo


class _Loader:
    @cached_property
    def monsters(self) -> dict[str, MonsterInfo]:
        return load_monsters()


_loader = _Loader()


def get_monsters() -> dict[str, MonsterInfo]:
    return _loader.monsters


def load_monsters() -> dict[str, MonsterInfo]:
    dir = Path(__file__).parent.parent.parent.parent / "data" / "5e_nl2"
    monsters = dict()
    for path in dir.glob("*.json"):
        with path.open("r", encoding="utf-8") as f:
            args: dict = json.load(f)

            args.update(
                key=name_to_key(args["name"]),
                path=path,
                creature_type=CreatureType.parse(args["creature_type"]),
                creature_subtypes=_cleanup_subtypes(args.pop("creature_subtype", None)),
                role=_cleanup_role(args.get("role")),
                damage_types=_cleanup_damage_types(args["damage_types"]),
                skills=args.pop("skills", None),
                senses=args.pop("senses", None),
            )
            monster = MonsterInfo(**args)
            monsters[monster.key] = monster
    return monsters


def iter_monster_paragraphs() -> Iterable[TrainingParagraph]:
    dir = Path(__file__).parent.parent.parent.parent / "data" / "5e_paragraphs"

    for path in dir.glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        yield TrainingParagraph(topic="monster", name=path.stem, text=text)


def _cleanup_role(role: str | None) -> MonsterRole | None:
    if role is None or role.lower() in {"none", "unknown", "null"}:
        return None
    elif role.lower() in {"support", "supporter"}:
        return MonsterRole.Leader
    elif role.lower() in {
        "hindering enemy",
        "hindering foe",
        "disruptor",
        "manipulator",
    }:
        return MonsterRole.Controller
    return MonsterRole.parse(role)


def _cleanup_damage_types(damage_types: str | list[str] | None) -> list[DamageType]:
    if damage_types is None:
        return []
    elif isinstance(damage_types, str):
        damage_types = [d.strip() for d in damage_types.split(",")]

    results: list[DamageType] = []
    for d in damage_types:
        if d.lower() in {"none", "unknown", "null", "nonmagical"}:
            continue
        results.append(DamageType.parse(d))
    return results


def _cleanup_subtypes(subtypes: str | list[str] | None) -> list[str] | None:
    if subtypes is None:
        return None
    elif isinstance(subtypes, str):
        subtypes = subtypes.split(",")
    return [s.strip() for s in subtypes]
