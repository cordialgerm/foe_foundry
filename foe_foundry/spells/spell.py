from __future__ import annotations

import math
from dataclasses import asdict, dataclass

from num2words import num2words

from ..features import ActionType
from ..skills import AbilityScore


@dataclass(frozen=True)
class Spell:
    name: str
    level: int
    school: str
    source: str
    description: str
    upcast: bool = False
    concentration: bool = False
    action_type: ActionType = ActionType.Action
    save: AbilityScore | None = None
    upcast_description: str | None = None
    range: str | None = None
    concentration_spell_level: int | None = None
    concentration_overridden: bool = False

    def copy(self, **kwargs) -> Spell:
        if "concentration" in kwargs:
            kwargs.update(concentration_overridden=True)

        args = asdict(self)
        args.update(kwargs)
        return Spell(**args)

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Spell):
            return False
        else:
            return self.name == other.name

    def for_statblock(
        self,
        uses: int | None = None,
        notes: str | None = None,
        concentration: bool | None = None,
        **kwargs,
    ) -> StatblockSpell:
        if concentration is None:
            concentration = self.concentration

        concentration_overriden = (
            self.concentration_overridden or concentration != self.concentration
        )

        # some spells can be upcast to a higher level and remove their concentraiton requirement
        # for example Bestow Curse loses concentration at fifth level
        if self.concentration_spell_level is None and concentration:
            concentration_spell_level = 10
        else:
            concentration_spell_level = self.concentration_spell_level

        args: dict = (
            dict(
                name=self.name,
                level=self.level,
                upcastable=self.upcast,
                uses=uses,
                notes=notes,
                concentration_spell_level=concentration_spell_level,
                concentration_overriden=concentration_overriden,
            )
            | kwargs
        )

        return StatblockSpell(**args)


@dataclass(frozen=True)
class StatblockSpell:
    name: str
    level: int
    upcastable: bool
    upcast_level: int | None = None
    uses: int | None = None
    notes: str | None = None
    symbols: str | None = None
    concentration_spell_level: int | None = None
    concentration_overriden: bool = False

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StatblockSpell):
            return False
        else:
            return self.name == other.name

    @property
    def level_resolved(self) -> int:
        return self.upcast_level or self.level

    @property
    def recommended_min_cr(self) -> float:
        return self.level * 1.5

    @property
    def concentration(self) -> bool:
        if self.concentration_spell_level is None:
            return False
        else:
            level = self.upcast_level or self.level
            return level < self.concentration_spell_level

    def copy(self, **kwargs) -> StatblockSpell:
        args = asdict(self)
        args.update(kwargs)
        return StatblockSpell(**args)

    def scale_for_cr(self, cr: float) -> StatblockSpell:
        if self.uses is not None:
            uses = self.uses
        else:
            cr_surplus = max(cr - self.recommended_min_cr, 0)
            uses = min(3, max(1, math.ceil(cr_surplus / 2.5)))

        if self.upcast_level is not None:
            upcast_level = self.upcast_level
        elif self.upcastable:
            proposed_upcast_level = min(5, math.ceil(cr / 2.5))
            upcast_level = (
                proposed_upcast_level if proposed_upcast_level > self.level else None
            )
        else:
            upcast_level = None

        return self.copy(uses=uses, upcast_level=upcast_level)

    @property
    def caption_md(self) -> str:
        level = (
            f"{num2words(self.upcast_level, to='ordinal_num')}"
            if self.upcast_level is not None
            else ""
        )
        notes = self.notes if self.notes is not None else ""

        asides = [level, notes]
        asides = [a for a in asides if a != ""]
        asides = f" ({', '.join(asides)})" if len(asides) > 0 else ""

        symbols = self.symbols if self.symbols is not None else ""

        if self.concentration_overriden and self.concentration:
            concentration = "<sup><b>c</b></sup>"  # bolded C
        elif self.concentration_overriden and not self.concentration:
            concentration = "<sup>\u023b</sup>"  # crossed out C
        elif self.concentration:
            concentration = "<sup>c</sup>"  # regular C
        else:
            concentration = ""

        return f'<span class="spell"><i>{self.name}{concentration}{symbols}</i></span>{asides}'
