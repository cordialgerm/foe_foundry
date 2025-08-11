from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from foe_foundry import CreatureType, DamageType

from ..utils import list_to_sentence


def _sentence(text: str):
    text = text.strip()
    if not text.endswith("."):
        text += "."
    text += " "
    return text


@dataclass(kw_only=True)
class MonsterInfo:
    key: str
    name: str
    size: str
    srd: bool
    path: Path
    creature_type: CreatureType
    creature_subtypes: list[str]
    damage_types: list[DamageType]
    alignment: str
    cr: str
    ac: int
    ac_description: str | None = None
    hp: int
    movement: str
    role: str | None
    tags: list[str]
    adjectives: list[str]
    description: str
    memorable: str
    goals: str
    relations: str
    environment: str
    strengths: str
    weaknesses: str
    attacks: str
    most_powerful_ability: str
    additional_information: list[str]
    equipment: str | None = None
    senses: str | None
    skills: str | None
    spellcasting: str | None
    test_queries: list[str]

    @property
    def cr_numeric(self) -> float:
        ## CR is either a fraction like 1/8, 1/4, 1/2, or a whole number
        if isinstance(self.cr, str):
            if "/" in self.cr:
                numerator, denominator = self.cr.split("/")
                return float(numerator) / float(denominator)
            else:
                return float(self.cr)
        else:
            return float(self.cr)

    def overview_sentence(self, rng: np.random.Generator) -> str:
        overview = f"{self.name} is a {self.size} {self.alignment} {self.creature_type} CR {self.cr} monster with {self.hp} hit points (HP) and an Armor Class (AC) of {self.ac}."

        tags = list_to_sentence(self.tags + self.adjectives)

        if len(self.damage_types) > 0:
            overview += f" It often deals {list_to_sentence(self.damage_types)} damage and can be described as {tags}. "
        else:
            overview += f" It can be described as {tags}. "

        return _sentence(overview)

    def description_sentence(self, rng: np.random.Generator) -> str:
        synonyms = [
            "has the following appearance",
            "is often described as",
            "is known as",
            "is referred to as",
            "is described as",
            "has the following description",
        ]
        return _sentence(f"{self.name} {rng.choice(synonyms)}: {self.description}")

    def memorable_sentence(self, rng: np.random.Generator) -> str:
        return _sentence(
            f"{self.name} {rng.choice(['is memorable for', 'is noteworthy for', 'is remarkable for', 'is known for'])}: {self.memorable}"
        )

    def goals_sentence(self, rng: np.random.Generator) -> str:
        return _sentence(
            f"{self.name} {rng.choice(['has the following goals', 'is driven by', 'is motivated by', 'is focused on'])}: {self.goals}"
        )

    def relations_sentence(self, rng: np.random.Generator) -> str:
        return _sentence(
            f"{self.name} {rng.choice(['has the following relations', 'is connected to', 'is associated with', 'is linked to'])}: {self.relations}"
        )

    def environment_sentence(self, rng: np.random.Generator) -> str:
        return _sentence(
            f"{self.name} {rng.choice(['is found in the following environments', 'is located in', 'is present in', 'is situated in', 'prefers these habitats'])}: {self.environment}"
        )

    def strengths_sentence(self, rng: np.random.Generator) -> str:
        return _sentence(
            f"{self.name} {rng.choice(['has the following strengths', 'is strong in', 'is proficient in', 'is skilled in', 'is good at'])}: {self.strengths}"
        )

    def weaknesses_sentence(self, rng: np.random.Generator) -> str:
        return _sentence(
            f"{self.name} {rng.choice(['has the following weaknesses', 'is weak to', 'is vulnerable to', 'is susceptible to', 'is not good at'])}: {self.weaknesses}"
        )

    def attacks_sentence(self, rng: np.random.Generator) -> str:
        return _sentence(
            f"{self.name} {rng.choice(['has the following attacks', 'can use', 'can perform', 'can execute', 'can unleash'])}: {self.attacks}"
        )

    def most_powerful_ability_sentence(self, rng: np.random.Generator) -> str:
        return _sentence(
            f"{self.name} {rng.choice(['has the following most powerful ability', 'can use', 'can perform', 'can execute', 'can unleash'])}: {self.most_powerful_ability}"
        )

    def equipment_sentence(self, rng: np.random.Generator) -> str | None:
        if self.equipment is None:
            return None
        return _sentence(
            f"{self.name} {rng.choice(['has the following equipment', 'is equipped with', 'carries', 'possesses'])}: {self.equipment}"
        )

    def sensenses_sentence(self, rng: np.random.Generator) -> str | None:
        if self.senses is None:
            return None
        return _sentence(
            f"{self.name} {rng.choice(['has the following senses', 'can sense', 'is aware of', 'can detect', 'can perceive'])}: {self.senses}"
        )

    def skills_sentence(self, rng: np.random.Generator) -> str | None:
        if self.skills is None:
            return None
        return _sentence(
            f"{self.name} {rng.choice(['boasts', 'has the following skills', 'is skilled in', 'is proficient in', 'is good at', 'is capable of'])}: {self.skills}"
        )

    def spellcasting_sentence(self, rng: np.random.Generator) -> str | None:
        if self.spellcasting is None:
            return None
        return _sentence(
            f"{self.name} {rng.choice(['has the following spellcasting abilities', 'can cast spells such as', 'can use spells like', 'can magically perform', 'can magically unleash'])}: {self.spellcasting}"
        )

    def additional_information_sentence(self, rng: np.random.Generator) -> str | None:
        if not len(self.additional_information):
            return None

        prefix = rng.choice(
            [
                "Here are some interesting facts about",
                "Did you know that",
                "Interesting facts about",
                "Useful tidbits about",
            ]
        )
        sentences = " ".join(self.additional_information)
        return _sentence(f"{prefix} {self.name}: {sentences}")

    def iter_sentences(self, rng: np.random.Generator) -> Iterable[str]:
        yield self.overview_sentence(rng)
        yield self.description_sentence(rng)
        yield self.memorable_sentence(rng)
        yield self.goals_sentence(rng)
        yield self.relations_sentence(rng)
        yield self.environment_sentence(rng)
        yield self.strengths_sentence(rng)
        yield self.weaknesses_sentence(rng)
        yield self.attacks_sentence(rng)
        yield self.most_powerful_ability_sentence(rng)

        # Handle conditional facts
        optional_facts = [
            self.equipment_sentence(rng),
            self.sensenses_sentence(rng),
            self.skills_sentence(rng),
            self.spellcasting_sentence(rng),
            self.additional_information_sentence(rng),
        ]
        for fact in optional_facts:
            if fact:
                yield fact

    def iter_paragraphs(self, rng: np.random.Generator) -> Iterable[tuple[str, str]]:
        ## Overview & Description & Memorable paragraph
        yield (
            "description",
            self.description_sentence(rng) + self.memorable_sentence(rng),
        )

        ## Environment & Relations & Goals paragraph
        yield (
            "background",
            self.environment_sentence(rng)
            + self.relations_sentence(rng)
            + self.goals_sentence(rng),
        )

        ## Strengths & Weakness & Attacks paragraph
        skills = self.skills_sentence(rng)
        spells = self.spellcasting_sentence(rng)
        yield (
            "skills",
            self.strengths_sentence(rng)
            + (skills if skills is not None else "")
            + self.most_powerful_ability_sentence(rng)
            + (spells if spells is not None else "")
            + self.attacks_sentence(rng)
            + self.weaknesses_sentence(rng),
        )

        # additional info paragraph
        additional_info = self.additional_information_sentence(rng)
        if additional_info is not None:
            yield "additional_info", additional_info
