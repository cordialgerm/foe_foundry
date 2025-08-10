from __future__ import annotations

from dataclasses import asdict, dataclass

from backports.strenum import StrEnum


class DocType(StrEnum):
    monster_other = "monster_other"
    monster_ff = "monster_ff"
    power_ff = "power_ff"


@dataclass(kw_only=True)
class Document:
    doc_id: str
    monster_key: str | None
    power_key: str | None
    doc_type: DocType
    name: str
    content: str

    def to_json(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_json(data: dict) -> Document:
        return Document(**data)
