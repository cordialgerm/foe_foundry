from dataclasses import dataclass
from pathlib import Path


@dataclass
class MonsterInfo:
    key: str
    name: str
    is_srd: bool
    path: Path
    creature_type: str
    creature_subtypes: list[str]
    cr: str
    ac: int
    hp: int
    ac_detail: str | None
    source: str
    type: str
    text: str


@dataclass
class CanonicalMonster:
    key: str
    name: str
    is_srd: bool
    creature_type: str
    creature_subtypes: list[str]
    cr: str
    ac: int
    hp: int
    ac_detail: str | None
    infos: list[MonsterInfo]
    summary: str | None
    description: str | None
    natural_language: str | None

    @property
    def cr_numeric(self) -> float:
        return float(self.cr)

    def save(self, path: Path):
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            f.write(f"<MonsterName/>{self.name}</MonsterName>\n")
            f.write(f"<CreatureType/>{self.creature_type}</CreatureType>\n")
            for subtype in self.creature_subtypes:
                f.write(f"<Subtype/>{subtype}</Subtype>\n")
            f.write(f"<CR/>{self.cr}</CR>\n")

            if self.ac_detail is not None:
                f.write(f"<AC/>{self.ac} ({self.ac_detail})</AC>\n")
            else:
                f.write(f"<AC/>{self.ac}</AC>\n")

            f.write(f"<HP/>{self.hp}</HP>\n")

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

                f.write("<statblock>\n")
                f.write(info.text)
                f.write("</statblock>\n")
                f.write("\n\n")
