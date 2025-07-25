from datetime import datetime
from math import ceil
from typing import List

from num2words import num2words

from ...attributes import AbilityScore, Skills
from ...creature_types import CreatureType
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class PhysicallyTough(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        def humanoid_is_fighter(c: BaseStatblock) -> bool:
            if c.creature_type in {CreatureType.Humanoid, CreatureType.Fey}:
                return c.role in {
                    MonsterRole.Bruiser,
                    MonsterRole.Soldier,
                    MonsterRole.Defender,
                }
            else:
                return True

        super().__init__(
            name=name,
            source=source,
            theme="tough",
            icon=icon,
            reference_statblock="Berserker",
            power_level=power_level,
            power_category=PowerCategory.Theme,
            power_types=power_types or [PowerType.Defense, PowerType.Buff],
            create_date=create_date,
            score_args=dict(
                require_types=[
                    CreatureType.Ooze,
                    CreatureType.Undead,
                    CreatureType.Beast,
                    CreatureType.Monstrosity,
                    CreatureType.Humanoid,
                    CreatureType.Giant,
                    CreatureType.Fey,
                ],
                bonus_roles=[
                    MonsterRole.Bruiser,
                    MonsterRole.Soldier,
                    MonsterRole.Defender,
                ],
                require_stats=AbilityScore.STR,
                bonus_size=Size.Large,
                bonus_skills=Skills.Athletics,
                require_callback=humanoid_is_fighter,
            )
            | score_args,
        )


class MagicallyTough(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            theme="tough",
            icon=icon,
            reference_statblock="Iron Golem",
            power_level=power_level,
            power_category=PowerCategory.Theme,
            power_types=power_types or [PowerType.Defense, PowerType.Magic],
            create_date=create_date,
            score_args=dict(
                require_types=[
                    CreatureType.Fey,
                    CreatureType.Fiend,
                    CreatureType.Celestial,
                    CreatureType.Construct,
                ],
                bonus_roles=[
                    MonsterRole.Defender,
                    MonsterRole.Soldier,
                    MonsterRole.Leader,
                ],
                require_cr=5,
            )
            | score_args,
        )


class _JustAScratch(PhysicallyTough):
    def __init__(self):
        super().__init__(
            name="Just A Scratch",
            icon="strong-man",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            power_types=[PowerType.Defense, PowerType.Healing],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        hp = easy_multiple_of_five(0.5 * stats.hp.average)
        temphp = easy_multiple_of_five(0.25 * stats.hp.average)

        feature = Feature(
            name="Just A Scratch",
            description=f"When {stats.selfref} is reduced to {hp} hit points, it roars in defiance and gains {temphp} temporary hitpoints. \
                While those temporary hitpoints are active, {stats.selfref} has advantage on all attack rolls and saving throws.",
            action=ActionType.Reaction,
            uses=1,
        )
        return [feature]


class _MagicResistance(MagicallyTough):
    def __init__(self):
        super().__init__(
            name="Magic Resistance",
            icon="surrounded-shield",
            source="SRD5.1 Stone Golem",
            power_level=LOW_POWER,
            power_types=[PowerType.Defense, PowerType.Magic],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Magic Resistance",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has advantage on saves against spells and other magical effects.",
        )
        return [feature]


class _LimitedMagicImmunity(MagicallyTough):
    def __init__(self):
        super().__init__(
            name="Limited Magic Immunity",
            source="SRD5.1 Rakshasa",
            icon="cancel",
            power_level=HIGH_POWER,
            power_types=[PowerType.Defense, PowerType.Magic],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        level = f"{num2words(int(min(5, ceil(stats.cr / 3))), to='ordinal')} level spell or lower"

        feature = Feature(
            name="Limited Magic Immunity",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} is attacked by a spell, targeted by a spell, or forced to make a saving throw by a {level} then {stats.selfref} can force the spell attack to miss or can choose to succeed on the saving throw.",
        )

        return [feature]


class _Regeneration(PhysicallyTough):
    def __init__(self):
        super().__init__(
            name="Regeneration",
            source="SRD5.1 Shield Guardian",
            icon="regeneration",
            power_types=[PowerType.Defense, PowerType.Healing],
            require_types=[
                CreatureType.Construct,
                CreatureType.Undead,
                CreatureType.Monstrosity,
                CreatureType.Ooze,
            ],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        weaknesses = {
            CreatureType.Undead: "radiant damage",
            CreatureType.Monstrosity: "acid or fire damage",
            CreatureType.Construct: "acid damage",
            CreatureType.Elemental: "necrotic damage",
        }
        weakness = weaknesses.get(stats.creature_type, "fire damage")
        hp = easy_multiple_of_five(1.5 * stats.cr)

        feature = Feature(
            name="Regeneration",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} regains {hp} hp at the start of its turn. \
                If {stats.selfref} takes {weakness}, this trait doesn't function at the start of {stats.selfref}'s next turn. \
                {stats.selfref.capitalize()} only dies if it starts its turn with 0 hp and doesn't regenerate.",
        )
        return [feature]


class _Stoneskin(MagicallyTough):
    def __init__(self):
        super().__init__(
            name="Stoneskin",
            icon="crenulated-shield",
            source="SRD5.1 Stoneskin",
            power_types=[PowerType.Defense, PowerType.Magic],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Stoneskin",
            action=ActionType.Reaction,
            recharge=5,
            description=f"{stats.selfref.capitalize()} instantly hardens its exterior in response to being hit by an attack. \
                {stats.selfref.capitalize()} gains resistance to non-psychic damage until the end of its next turn",
        )
        return [feature]


JustAScratch: Power = _JustAScratch()
LimitedMagicImmunity: Power = _LimitedMagicImmunity()
MagicResistance: Power = _MagicResistance()
Regeneration: Power = _Regeneration()
Stoneskin: Power = _Stoneskin()

ToughPowers: List[Power] = [
    JustAScratch,
    LimitedMagicImmunity,
    MagicResistance,
    Regeneration,
    Stoneskin,
]
