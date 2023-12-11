import math
from dataclasses import dataclass, field
from typing import List

from num2words import num2words

from ..features import ActionType, Feature
from ..statblocks import BaseStatblock
from .power import MEDIUM_POWER, PowerType, PowerWithStandardScoring


@dataclass
class Spell:
    name: str
    level: int
    upcast: bool
    action_type: ActionType = ActionType.Action
    power_level: float = MEDIUM_POWER
    score_args: dict = field(default_factory=dict)


class SpellPower(PowerWithStandardScoring):
    def __init__(self, spell: Spell, power_type: PowerType, theme: str, **kwargs):
        super().__init__(
            name=f"Spellcasting - {spell.name}",
            power_level=spell.power_level,
            power_type=power_type,
            theme=theme,
            source="SRD 5.1",
            score_args=spell.score_args,
            **kwargs,
        )
        self.spell = spell

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class

        # if the spell can be upcast, use the higher of the upcast level or the monster's CR/2
        if self.spell.upcast:
            level = int(max(math.floor(stats.cr / 2), self.spell.level))
            level = f"at {num2words(level, ordinal=True)} level"
        else:
            level = ""

        uses = min(3, int(math.ceil(stats.cr / 4)))

        if self.spell.action_type == ActionType.Action:
            replaces_multiattack = 2 if self.spell.power_level > MEDIUM_POWER else 1
        else:
            replaces_multiattack = 0

        feature = Feature(
            name=self.spell.name,
            action=self.spell.action_type,
            uses=uses,
            replaces_multiattack=replaces_multiattack,
            description=f"{stats.selfref.capitalize()} casts *{self.spell.name}* {level} using a DC of {dc}.",
        )
        return [feature]
