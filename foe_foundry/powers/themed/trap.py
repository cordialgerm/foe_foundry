from datetime import datetime
from math import ceil
from typing import List

from ...attributes import Skills
from ...creature_types import CreatureType
from ...damage import Condition
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class Trap(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            power_type=PowerType.Theme,
            power_level=power_level,
            create_date=create_date,
            theme="trap",
            score_args=dict(
                require_types={c for c in CreatureType if c.could_use_equipment},
                require_roles={
                    MonsterRole.Ambusher,
                    MonsterRole.Skirmisher,
                },
                bonus_types=CreatureType.Humanoid,
                bonus_skills=Skills.Survival,
            )
            | score_args,
        )


class _Snare(Trap):
    def __init__(self):
        super().__init__(name="Snare", source="Foe Foundry")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        quantity = ceil(stats.cr / 3)

        feature = Feature(
            name="Snares",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} is a skilled trapper. Unless surprised, {stats.selfref} has placed up to {quantity} snares in its vicinity. \
                When a creature moves within 15 feet of the snare, if it has a passive perception of {dc} or higher it becomes aware of the snare. \
                The snares can also actively be detected by a creature within 30 feet using an action to make a DC {dc} Perception check. \
                A creature that is unaware of an untriggered snare and moves within 5 feet of it must make a DC {dc} Dexterity saving throw. \
                On a failure, it is lifted into the air and {Condition.Restrained.caption} (escape DC {dc}).",
        )

        return [feature]


class _SpikePit(Trap):
    def __init__(self):
        super().__init__(name="Spike Pit", source="Foe Foundry")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        quantity = ceil(stats.cr / 3)
        fall_damage = DieFormula.from_expression("2d6")
        spike_damage = stats.target_value(0.5, force_die=Die.d6)

        feature = Feature(
            name="Spike Traps",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} is a skilled trapper. Unless surprised, {stats.selfref} has placed up to {quantity} spike traps in its vicinity. \
                When a creature moves within 15 feet of the trap, if it has a passive perception of {dc} or higher it becomes aware of the trap. \
                The traps can also actively be detected by a creature within 30 feet using an action to make a DC {dc} Perception check. \
                A creature that moves within 5 feet of it must make a DC {dc} Dexterity saving throw or fall into the pit. \
                A creature that falls inside suffers {fall_damage.description} bludgeoning damage from the fall and {spike_damage.description} piercing damage from the spikes. \
                The pit is 10 feet deep and can be climbed out of using an action to perform a DC 12 Athletics check",
        )

        return [feature]


Snare: Power = _Snare()
SpikePit: Power = _SpikePit()

TrapPowers: List[Power] = [Snare, SpikePit]
