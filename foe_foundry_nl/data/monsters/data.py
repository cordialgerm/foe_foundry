from dataclasses import dataclass
from pathlib import Path


@dataclass
class MonsterInfo:
    key: str
    name: str
    is_srd: bool
    path: Path
    creature_type: str
    source: str
    type: str
    text: str


@dataclass
class CanonicalMonster:
    key: str
    name: str
    is_srd: bool
    creature_type: str
    infos: list[MonsterInfo]
    summary: str | None
    description: str | None
    natural_language: str | None

    def save(self, path: Path):

        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            f.write(f"<MonsterName/>{self.name}</MonsterName>\n")
            f.write(f"<CreatureType/>{self.creature_type}</CreatureType>\n\n")
            if self.description is not None:
                f.write(f"<summary>{self.description}</summary>\n\n")
            if self.summary is not None:
                f.write(f"<summary>{self.summary}</summary>\n\n")

            if self.natural_language is not None:
                if self.summary is not None and self.natural_language.startswith(
                    self.summary
                ):
                    nl = self.natural_language[len(self.summary) :]
                else:
                    nl = self.natural_language

                summarized_nl = nl

                f.write(f"<detail>{summarized_nl}</detail>\n\n")
            for info in self.infos:
                f.write("\n\n")
                f.write("---\n\n")
                f.write(f"Source: {info.source}\n\n")
                f.write(info.text)
                f.write("\n\n")
