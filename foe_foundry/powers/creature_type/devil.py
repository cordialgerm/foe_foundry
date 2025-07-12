from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...features import ActionType, Feature
from ...spells import CasterType, evocation
from ...statblocks import BaseStatblock
from ...utils import summoning
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


def is_devil(c: BaseStatblock) -> bool:
    return c.creature_subtype == "Devil"


class DevilPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(require_types=CreatureType.Fiend, **score_args)
        super().__init__(
            name=name,
            source=source,
            power_type=PowerType.CreatureType,
            power_level=power_level,
            create_date=create_date,
            icon=icon,
            theme="Devil",
            reference_statblock="Pit Fiend",
            score_args=standard_score_args,
        )


class _WallOfFire(DevilPower):
    def __init__(self):
        super().__init__(
            name="Wall of Fire",
            source="SRD5.1 Wall of Fire",
            icon="fire-wave",
            require_cr=5,
            bonus_damage=DamageType.Fire,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.cr <= 7:
            uses = 1
            concentration = True
        else:
            uses = 1
            concentration = False

        spell = evocation.WallOfFire.for_statblock(
            uses=uses, concentration=concentration
        )

        stats = stats.grant_spellcasting(CasterType.Innate)
        return stats.add_spell(spell)


class _DevilishMinions(DevilPower):
    def __init__(self):
        super().__init__(
            name="Devilish Minions",
            source="Foe Foundry",
            icon="minions",
            power_level=HIGH_POWER,
            require_cr=3,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        _, _, description = summoning.determine_summon_formula(
            summoner=summoning.Devils,
            summon_cr_target=stats.cr / 2.5,
            rng=stats.create_rng("devilish minions"),
        )

        feature = Feature(
            name="Devilish Minions",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} summons forth additional Devil allies. {description}",
        )

        return [feature]


class _TemptingOffer(DevilPower):
    def __init__(self):
        super().__init__(
            name="Tempting Offer", source="Foe Foundry", icon="cash", require_cr=3
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        exhaustion = Condition.Exhaustion
        feature = Feature(
            name="Tempting Offer",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} makes a tempting offer to a creature that can hear it within 60 feet. \
                That creature must make a DC {dc} Wisdom saving throw. On a failure, the creature gains a level of {exhaustion.caption}. \
                The creature may instead accept the offer. In doing so, it loses all levels of exhaustion gained in this way but is contractually bound to the offer",
        )
        return [feature]


class _DevilsSight(DevilPower):
    def __init__(self):
        super().__init__(
            name="Devil's Sight",
            source="Foe Foundry",
            icon="night-vision",
            bonus_damage=DamageType.Fire,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        level = 2 if stats.cr <= 5 else 4

        devils_sight = Feature(
            name="Devil's Sight",
            action=ActionType.Feature,
            description=f"Magical darkness doesn't impede {stats.selfref}'s darkvision, and it can see through Hellish Darkness.",
        )

        darkness = Feature(
            name="Hellish Darkness",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.selfref.capitalize()} causes shadowy black flames to fill a 15-foot radius sphere with obscuring darkness centered at a point within 60 feet that {stats.selfref} can see. \
                The darkness spreads around corners. Creatures without Devil's Sight can't see through this darkness and nonmagical light can't illuminate it. \
                If any of this spell's area overlaps with an area of light created by a spell of level {level} or lower, the spell that created the light is dispelled. \
                Creatures of {stats.selfref}'s choice lose any resistance to fire damage while in the darkness, and immunity to fire damage is instead treated as resistance to fire damage.",
        )

        return [devils_sight, darkness]


DevilsSight: Power = _DevilsSight()
DevlishMinions: Power = _DevilishMinions()
TemptingOffer: Power = _TemptingOffer()
WallOfFire: Power = _WallOfFire()

DevilPowers: list[Power] = [
    DevilsSight,
    DevlishMinions,
    TemptingOffer,
    WallOfFire,
]
