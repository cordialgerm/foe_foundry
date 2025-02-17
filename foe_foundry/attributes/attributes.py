from __future__ import annotations

from dataclasses import asdict, field
from typing import Set

import numpy as np
from pydantic.dataclasses import dataclass

from ..skills import Skills, Stats


@dataclass(kw_only=True)
class Attributes:
    proficiency: int

    STR: int
    DEX: int
    CON: int
    INT: int
    WIS: int
    CHA: int

    proficient_saves: Set[Stats] = field(default_factory=set)
    proficient_skills: Set[Skills] = field(default_factory=set)
    expertise_skills: Set[Skills] = field(default_factory=set)

    @property
    def primary_attribute(self) -> Stats:
        stats = [Stats.STR, Stats.DEX, Stats.INT, Stats.WIS, Stats.CHA]
        scores = [self.stat(s) for s in stats]
        i = np.argmax(scores)
        primary_attribute = stats[i]
        return primary_attribute

    @property
    def primary_attribute_score(self) -> int:
        return self.stat(self.primary_attribute)

    @property
    def primary_mod(self) -> int:
        return self.stat_mod(self.primary_attribute)

    @property
    def spellcasting_mod(self) -> int:
        stat = self.spellcasting_stat
        return self.stat_mod(stat)

    @property
    def spellcasting_stat(self) -> Stats:
        stats = [Stats.INT, Stats.CHA, Stats.WIS]
        scores = [self.stat(s) for s in stats]
        i = np.argmax(scores)
        return stats[i]

    @property
    def spellcasting_dc(self) -> int:
        return 8 + self.proficiency + self.spellcasting_mod

    @property
    def is_sapient(self) -> bool:
        mentals = np.array([self.INT, self.WIS, self.CHA])
        baseline = (mentals >= 6).all()
        intelligent = (mentals >= 9).any()
        return bool(baseline and intelligent)

    def stat(self, stat: Stats) -> int:
        return getattr(self, stat.value)

    def stat_mod(self, stat: Stats) -> int:
        return (self.stat(stat) - 10) // 2

    def save_mod(self, stat: Stats) -> int | None:
        if stat in self.proficient_saves:
            return self.stat_mod(stat) + self.proficiency
        else:
            return None

    def skill_mod(
        self, skill: Skills, even_if_not_proficient: bool = False
    ) -> int | None:
        if skill in self.expertise_skills:
            return self.stat_mod(skill.stat) + 2 * self.proficiency
        elif skill in self.proficient_skills:
            return self.stat_mod(skill.stat) + self.proficiency
        elif even_if_not_proficient:
            return self.stat_mod(skill.stat)
        else:
            return None

    def has_proficiency_or_expertise(self, skill: Skills) -> bool:
        return skill in self.proficient_skills or skill in self.expertise_skills

    def passive_skill(self, skill: Skills) -> int:
        return 10 + (self.skill_mod(skill, even_if_not_proficient=True) or 0)

    def copy(self, **args) -> Attributes:
        kwargs = asdict(self)
        kwargs.update(args)
        return Attributes(**kwargs)

    def grant_proficiency_or_expertise(self, *skills: Skills) -> Attributes:
        new_profs = set(self.proficient_skills)
        new_expertise = set(self.expertise_skills)

        for skill in skills:
            if skill in self.proficient_skills:
                new_profs.remove(skill)
                new_expertise.add(skill)
            elif skill not in self.expertise_skills:
                new_profs.add(skill)

        return self.copy(proficient_skills=new_profs, expertise_skills=new_expertise)

    def grant_save_proficiency(self, *saves: Stats) -> Attributes:
        new_saves = self.proficient_saves | set(saves)
        return self.copy(proficient_saves=new_saves)

    def change_primary(self, primary: Stats) -> Attributes:
        args = {
            "primary_attribute": primary,
            primary.value: self.primary_attribute_score,
        }
        return self.copy(**args)

    def boost(self, stat: Stats, value: int, limit: bool = True) -> Attributes:
        new_val = self.stat(stat) + value
        if limit:
            new_val = min(new_val, self.primary_attribute_score)
        args = {stat.value: new_val}
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

    def describe_saves(self) -> str:
        pieces = []
        for stat, mod in self.saves.items():
            sign = "-" if mod < 0 else "+"
            pieces.append(f"{stat.name.upper()} {sign}{abs(mod)}")
        return ", ".join(pieces)

    def describe_skills(self) -> str:
        pieces = []
        for skill, mod in self.skills.items():
            sign = "-" if mod < 0 else "+"
            pieces.append(f"{skill.name} {sign}{abs(mod)}")
        return ", ".join(pieces)
