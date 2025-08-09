from dataclasses import dataclass

from backports.strenum import StrEnum


class DocType(StrEnum):
    background = "background"
    lore = "lore"


@dataclass(kw_only=True)
class MonsterDocument:
    doc_id: str
    monster_key: str
    doc_type: DocType
    text: str
