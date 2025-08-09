from dataclasses import dataclass
from pathlib import Path


@dataclass(kw_only=True)
class MonsterDocument:
    path: Path
    monster_key: str
    text: str

    @property
    def doc_id(self) -> str:
        return self.path.stem
