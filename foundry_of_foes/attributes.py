from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Set

from .skills import Skills, Stats


@dataclass
class Attributes:
    proficiency: int
    primary_attribute: Stats

    STR: int
    DEX: int
    CON: int
    INT: int
    WIS: int
    CHA: int

    proficient_saves: Set[Stats] = field(default_factory=set)
    proficient_skills: Set[Skills] = field(default_factory=set)
    expertise_skills: Set[Skills] = field(default_factory=set)

    def stat(self, stat: Stats) -> int:
        return getattr(self, stat.value)

    def stat_mod(self, stat: Stats) -> int:
        return (self.stat(stat) - 10) // 2

    def save_mod(self, stat: Stats) -> int | None:
        if stat in self.proficient_saves:
            return self.stat_mod(stat) + self.proficiency
        else:
            return None

    def skill_mod(self, skill: Skills) -> int | None:
        if skill in self.expertise_skills:
            return self.stat_mod(skill.stat) + 2 * self.proficiency
        elif skill in self.proficient_skills:
            return self.stat_mod(skill.stat) + self.proficiency
        else:
            return None

    def copy(self, **args) -> Attributes:
        kwargs = asdict(self)
        kwargs.update(args)
        return Attributes(**kwargs)

    def update_primary_attribute(
        self,
        primary_attribute: Stats,
        primary_attribute_score: int,
        primary_attribute_backup_score: int = 10,
    ) -> Attributes:
        args = {
            primary_attribute.value: primary_attribute_score,
            self.primary_attribute.value: primary_attribute_backup_score,
        }
        return self.copy(**args)

    @property
    def saves(self) -> dict[Stats, int]:
        results = {}
        for stat in Stats.All():
            save = self.save_mod(stat)
            if save is not None:
                results[stat] = save
        return results

    @property
    def skills(self) -> dict[Skills, int]:
        results = {}
        for skill in Skills.All():
            skill_mod = self.skill_mod(skill)
            if skill_mod is not None:
                results[skill] = skill_mod
        return results
