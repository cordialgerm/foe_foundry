import json
from functools import cached_property
from pathlib import Path
from typing import Iterable

from foe_foundry import CreatureType, DamageType, MonsterRole
from foe_foundry.utils import name_to_key
from foe_foundry_data.monsters.all import Monsters

from .doc import DocType, MonsterDocument
from .meta import MonsterDocumentMeta


class _Loader:
    @cached_property
    def document_metas(self) -> dict[str, MonsterDocumentMeta]:
        return {meta.key: meta for meta in self.iter_document_metas()}

    def iter_documents(self) -> Iterable[MonsterDocument]:
        dir = Path(__file__).parent.parent.parent / "data" / "5e_paragraphs"

        suffixes = [
            "_additional_info",
            "_background",
            "_description",
            "_skills",
        ]

        for path in dir.glob("*.txt"):
            if not path.stem.endswith(tuple(suffixes)):
                continue

            # extract monster key form filename by removing suffixes
            key = path.stem
            for suffix in suffixes:
                if key.endswith(suffix):
                    key = key[: -len(suffix)]
                    break

            text = path.read_text(encoding="utf-8")
            monster_key = name_to_key(key)
            yield MonsterDocument(
                doc_id=path.stem,
                doc_type=DocType.background,
                monster_key=monster_key,
                text=text,
            )

        for monster in Monsters.one_of_each_monster:
            if not monster.has_lore or monster.overview_html is None:
                continue
            yield MonsterDocument(
                doc_id=monster.key + "-lore",
                monster_key=monster.key,
                doc_type=DocType.lore,
                text=monster.overview_html,
            )

    def iter_document_metas(self) -> Iterable[MonsterDocumentMeta]:
        dir = Path(__file__).parent.parent.parent / "data" / "5e_nl2"
        for path in dir.glob("*.json"):
            with path.open("r", encoding="utf-8") as f:
                args: dict = json.load(f)

                args.update(
                    key=name_to_key(args["name"]),
                    path=path,
                    creature_type=CreatureType.parse(args["creature_type"]),
                    creature_subtypes=_cleanup_subtypes(
                        args.pop("creature_subtype", None)
                    ),
                    role=_cleanup_role(args.get("role")),
                    damage_types=_cleanup_damage_types(args["damage_types"]),
                    skills=args.pop("skills", None),
                    senses=args.pop("senses", None),
                )
                monster = MonsterDocumentMeta(**args)
                yield monster


_loader = _Loader()


def iter_monster_doc_metas() -> Iterable[MonsterDocumentMeta]:
    """Iterate over metadata about monster documents."""
    return _loader.iter_document_metas()


def iter_monster_docs() -> Iterable[MonsterDocument]:
    """Iterate over monster documents."""
    return _loader.iter_documents()


def load_monster_doc_metas() -> dict[str, MonsterDocumentMeta]:
    """Load metadata about monster documents. Cached for performance"""
    return _loader.document_metas


def _cleanup_role(role: str | None) -> MonsterRole | None:
    if role is None or role.lower() in {"none", "unknown", "null"}:
        return None
    elif role.lower() in {"support", "supporter"}:
        return MonsterRole.Support
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
