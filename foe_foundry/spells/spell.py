from __future__ import annotations

from dataclasses import asdict, dataclass

from num2words import num2words

from ..features import ActionType
from ..skills import Stats


@dataclass
class Spell:
    name: str
    level: int
    school: str
    source: str
    description: str
    upcast: bool = False
    concentration: bool = False
    action_type: ActionType = ActionType.Action
    save: Stats | None = None
    upcast_description: str | None = None
    range: str | None = None

    def copy(self, **kwargs) -> Spell:
        args = asdict(self)
        args.update(kwargs)
        return Spell(**args)

    def for_statblock(self, uses: int | None = None) -> StatblockSpell:
        return StatblockSpell(
            name=self.name, level=self.level, upcastable=self.upcast, uses=uses
        )


@dataclass
class StatblockSpell:
    name: str
    level: int
    upcastable: bool
    upcast_level: int | None = None
    uses: int | None = None

    def copy(self, **kwargs) -> StatblockSpell:
        args = asdict(self)
        args.update(kwargs)
        return StatblockSpell(**args)

    def upcast(self, level: int) -> StatblockSpell:
        if self.upcastable and level > self.level:
            return self.copy(upcast_level=level)
        else:
            return self

    @property
    def caption_md(self) -> str:
        level = (
            f" ({num2words(self.upcast_level, to='ordinal_num')})"
            if self.upcast_level is not None
            else ""
        )
        return f'<span class="spell"><i>{self.name}</i></span>{level}'
