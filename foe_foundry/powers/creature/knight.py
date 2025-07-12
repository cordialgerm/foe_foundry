from foe_foundry.references import creature_ref

from ...creature_types import CreatureType
from ...features import ActionType, Feature
from ...skills import Skills
from ...statblocks import BaseStatblock
from ..power import MEDIUM_POWER, Power, PowerCategory, PowerWithStandardScoring


def is_knight(c: BaseStatblock) -> bool:
    return c.creature_class == "Knight"


class KnightPower(PowerWithStandardScoring):
    def __init__(self, name: str, icon: str, power_level: float = MEDIUM_POWER):
        super().__init__(
            name=name,
            power_category=PowerCategory.Creature,
            power_level=power_level,
            source="Foe Foundry",
            icon=icon,
            theme="knight",
            reference_statblock="Knight",
            score_args=dict(
                require_callback=is_knight,
                require_types=CreatureType.Humanoid,
            ),
        )


class _MountedWarrior(KnightPower):
    def __init__(self):
        super().__init__(
            name="Mounted Warrior",
            icon="mounted-knight",
            power_level=MEDIUM_POWER,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        stats = stats.grant_proficiency_or_expertise(Skills.AnimalHandling)
        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> list[Feature]:
        steed = creature_ref("Warhorse")
        feature = Feature(
            name="Trusty Steed",
            action=ActionType.BonusAction,
            uses=1,
            description=f"""{stats.selfref.capitalize()} calls its trusty {steed} to its side. The steed uses its movement and action to move next to {stats.selfref}, who can then mount it as part of this bonus action. \
                The {steed} then acts as a Controlled Mount for {stats.selfref}.""",
        )
        return [feature]


class _GriffinKnight(KnightPower):
    def __init__(self):
        super().__init__(
            name="Griffin Knight",
            icon="griffin-symbol",
            power_level=MEDIUM_POWER,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        stats = stats.grant_proficiency_or_expertise(Skills.AnimalHandling)
        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> list[Feature]:
        griffon = creature_ref("Griffon")
        feature = Feature(
            name="Griffon Mount",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} calls its bonded {griffon} to its side. The {griffon} joins initiative immediately after {stats.selfref} and uses its movement and action to swoop in and pick up {stats.selfref}. The {griffon} then acts as an Independent Mount for {stats.selfref}.",
        )
        return [feature]


MountedWarrior: Power = _MountedWarrior()
GriffinKnight: Power = _GriffinKnight()

KnightPowers: list[Power] = [
    MountedWarrior,
    GriffinKnight,
]
