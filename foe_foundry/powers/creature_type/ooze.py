from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import DamageType, conditions
from ...die import Die
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...size import Size
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    RIBBON_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class OozePower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(require_types=CreatureType.Ooze, **score_args)
        super().__init__(
            name=name,
            power_type=PowerType.CreatureType,
            source=source,
            create_date=create_date,
            power_level=power_level,
            theme="Ooze",
            score_args=standard_score_args,
        )


class _EngulfInSlime(OozePower):
    def __init__(self):
        super().__init__(
            name="Engulf in Slime",
            source="Foe Foundry",
            create_date=datetime(2023, 11, 23),
            require_size=Size.Large,
            bonus_damage=DamageType.Acid,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        swallowed = conditions.Swallowed(
            damage=stats.target_value(0.75, force_die=Die.d6),
            damage_type=DamageType.Acid,
        )
        feature = Feature(
            name="Engulf in Slime",
            action=ActionType.Action,
            description=f"{stats.selfref.capitalize()} moves up to its speed. While doing so, it can enter Medium or smaller creatures' spaces. \
                Whenever {stats.selfref} enters a creature's space, the creature must make a DC {stats.difficulty_class} Dexterity saving throw. \
                On a failure, the creature is {swallowed.caption}. {swallowed.description_3rd}",
        )
        return [feature]


class _Quicksand(OozePower):
    def __init__(self):
        super().__init__(
            name="Quicksand",
            source="Foe Foundry",
            create_date=datetime(2023, 11, 23),
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature1 = Feature(
            name="Quicksand",
            uses=3,
            action=ActionType.Action,
            description=f"{stats.selfref.capitalize()} creates a 10-foot square of quicksand centered on a point within 60 feet of it. \
                The quicksand lasts for 1 minute. Any creature that enters the quicksand or starts its turn there must succeed on a DC {stats.difficulty_class} Strength saving throw or be **Grappled** (escape DC {dc}). \
                While grappled in this way, the creature is **Restrained**.",
        )
        feature2 = Feature(
            name="Quagmire Step",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} disappears into the ground and reappears at a quicksand location within 120 feet.",
        )
        return [feature1, feature2]


class _Split(OozePower):
    def __init__(self):
        super().__init__(
            name="Split",
            source="SRD 5.1 Ochre Jelly",
            power_level=HIGH_POWER,
            require_size=Size.Medium,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Split",
            action=ActionType.Reaction,
            description=f"Whenever {stats.selfref} takes lightning or slashing damage and it is Medium or larger, it splits in two if it has at least 10 hit points. Each new ooze has hit points equal to half the original ooze's, rounding down. New oozes are one size smaller than the original ooze.",
        )
        return [feature]


class _Transparent(OozePower):
    def __init__(self):
        super().__init__(
            name="Transparent",
            source="SRD5.1 Gelatinous Cube",
            power_level=RIBBON_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Transparent",
            action=ActionType.Feature,
            description=f"Even when {stats.selfref} is in plain sight, it takes a successful DC 15 Perception check to spot {stats.selfref} if it has neither moved nor attacked. \
                A creature that tries to enter {stats.selfref}'s space is surprised by {stats.selfref}",
        )
        return [feature]


class _LeechingGrasp(OozePower):
    def __init__(self):
        super().__init__(
            name="Leeching Grasp",
            source="Foe Foundry",
            create_date=datetime(2023, 11, 22),
            power_level=HIGH_POWER,
            bonus_damage=DamageType.Necrotic,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(0.5, suggested_die=Die.d6)
        bleeding = conditions.Bleeding(damage=dmg, damage_type=DamageType.Necrotic)

        feature = Feature(
            name="Leeching Grasp",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"One Medium or smaller creature that {stats.selfref} can see within 5 feet of it must succeed on a DC {dc} Dexterity saving throw or be **Grappled** (escape DC {dc}). \
                Until this grapple ends, the target is {bleeding.caption}. {bleeding.description_3rd}. \
                While grappling the target, {stats.selfref} takes only half of any damage dealt to it (rounded down), and the target takes the other half.",
        )
        return [feature]


class _SlimeSpray(OozePower):
    def __init__(self):
        super().__init__(
            name="Slime Spray", source="Foe Foundry", bonus_damage=DamageType.Acid
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(1.5, suggested_die=Die.d6)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Slime Spray",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=6,
            description=f"{stats.selfref.capitalize()} sprays slimy goo in a 30-foot cone. Each creature in that area must make a DC {dc} Dexterity saving throw. \
                On a failure, the creature takes {dmg.description} acid damage and is **Grappled** (escape DC {dc}). On a success, the creature takes half as much damage instead.",
        )
        return [feature]


EngulfInSlime: Power = _EngulfInSlime()
LeechingGrasp: Power = _LeechingGrasp()
Quicksand: Power = _Quicksand()
SlimeSpray: Power = _SlimeSpray()
Split: Power = _Split()
Transparent: Power = _Transparent()


OozePowers: List[Power] = [
    EngulfInSlime,
    LeechingGrasp,
    Quicksand,
    SlimeSpray,
    Split,
    Transparent,
]
