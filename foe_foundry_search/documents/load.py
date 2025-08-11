import json
from functools import cached_property
from pathlib import Path
from typing import Iterable

from foe_foundry import CreatureType, DamageType, MonsterRole
from foe_foundry.utils import key_to_name, name_to_key
from foe_foundry_data.monsters.all import Monsters
from foe_foundry_data.powers import Powers

from .doc import DocType, Document
from .meta import MonsterDocumentMeta


class _Loader:
    def __init__(self):
        self.cache_dir = Path.cwd() / "cache" / "documents"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @cached_property
    def document_metas(self) -> dict[str, MonsterDocumentMeta]:
        return {meta.key: meta for meta in self.iter_document_metas()}

    @cached_property
    def documents(self) -> dict[str, Document]:
        return {doc.doc_id: doc for doc in self.iter_documents()}

    def iter_documents(self) -> Iterable[Document]:
        items = [item for item in self.cache_dir.glob("*.json")]
        if len(items) == 0:
            for doc in self._cache_and_iter_documents():
                yield doc

        for item in items:
            with item.open("r", encoding="utf-8") as f:
                data = json.load(f)
                yield Document.from_json(data)

    def _cache_and_iter_documents(self) -> Iterable[Document]:
        for doc in self._do_iter_documents():
            path = self.cache_dir / f"{doc.doc_id}.json"
            if not path.exists():
                with path.open("w", encoding="utf-8") as f:
                    json.dump(doc.to_json(), f, ensure_ascii=False, indent=4)

            yield doc

    def _do_iter_documents(self) -> Iterable[Document]:
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
            yield Document(
                doc_id=f"monster-{path.stem}",
                doc_type=DocType.monster_other,
                monster_key=monster_key,
                power_key=None,
                name=key_to_name(key),
                content=text,
            )

        for monster in Monsters.one_of_each_monster:
            if not monster.has_lore or monster.overview_html is None:
                continue
            yield Document(
                doc_id=f"monster-{monster.key}-lore",
                monster_key=monster.key,
                doc_type=DocType.monster_ff,
                power_key=None,
                name=monster.name,
                content=monster.overview_html,
            )

        for power in Powers.AllPowers:
            roles = " ".join(r for r in power.roles)
            damage_types = " ".join(d for d in power.damage_types)
            tags = " ".join(t for t in power.tags)
            searchblob = " ".join(
                [power.name, power.feature_descriptions, tags, roles, damage_types]
            )

            yield Document(
                doc_id=f"power-{power.key}",
                monster_key=None,
                power_key=power.key,
                doc_type=DocType.power_ff,
                name=power.name,
                content=searchblob,
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


def iter_documents() -> Iterable[Document]:
    """Iterate over monster documents."""
    return _loader.iter_documents()


def load_documents() -> list[Document]:
    """Load all monster documents. Cached for performance"""
    return list(_loader.documents.values())


def load_monster_document_metas() -> dict[str, MonsterDocumentMeta]:
    """Load metadata about monster documents. Cached for performance"""
    return _loader.document_metas


def get_document(id: str) -> Document | None:
    """
    Get a specific document by its ID.

    Args:
        id: The document ID

    Returns:
        The Document object if found, otherwise None
    """
    return _loader.documents.get(id)


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
