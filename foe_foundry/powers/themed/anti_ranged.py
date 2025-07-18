import math
from datetime import datetime
from typing import List

from ...attack_template import spell
from ...attributes import AbilityScore
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...spells import CasterType
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import (
    HIGH_POWER,
    Power,
    PowerCategory,
    PowerType,
    PowerWithStandardScoring,
)


class _AdaptiveCamouflage(PowerWithStandardScoring):
    def __init__(self):
        score_args = dict(
            require_types=[
                CreatureType.Beast,
                CreatureType.Monstrosity,
                CreatureType.Ooze,
            ],
            require_attack_types=AttackType.MeleeNatural,
            bonus_roles=[MonsterRole.Skirmisher, MonsterRole.Ambusher],
        )

        super().__init__(
            name="Adaptive Camouflage",
            power_category=PowerCategory.Theme,
            power_level=HIGH_POWER,
            source="Foe Foundry",
            theme="Anti-Ranged",
            icon="hidden",
            reference_statblock="Basilisk",
            create_date=datetime(2023, 11, 28),
            score_args=score_args,
            power_types=[PowerType.Stealth, PowerType.Defense],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Adaptive Camouflage",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} cannot be seen by a creature that is more than 15 feet away from it \
                unless that creature first makes a DC {dc} Perception check using an action. On a success, that creature can see {stats.selfref} as normal.",
        )
        return [feature]


class _ArrowWard(PowerWithStandardScoring):
    def __init__(self):
        score_args = dict(
            require_types=[CreatureType.Humanoid, CreatureType.Fey],
            require_attack_types=AttackType.AllSpell(),
        )

        super().__init__(
            name="Arrow Ward",
            power_category=PowerCategory.Theme,
            source="Foe Foundry",
            theme="Anti-Ranged",
            icon="arrows-shield",
            reference_statblock="Shield Guardian",
            create_date=datetime(2023, 11, 28),
            score_args=score_args,
            power_types=[PowerType.Defense],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Arrow Ward",
            action=ActionType.Reaction,
            description=f"After being hit by a ranged attack, {stats.selfref} gains +5 AC against ranged attacks until the beginning of its next turn.",
        )
        return [feature]


class _DeflectMissile(PowerWithStandardScoring):
    def __init__(self):
        score_args = dict(
            require_types=CreatureType.Humanoid,
            require_attack_types=AttackType.MeleeWeapon,
            bonus_roles=[MonsterRole.Defender],
            require_stats=AbilityScore.DEX,
        )

        super().__init__(
            name="Deflect Missile",
            power_category=PowerCategory.Theme,
            source="SRD5.1 Monk",
            theme="Anti-Ranged",
            icon="divert",
            reference_statblock="Warrior",
            create_date=datetime(2023, 11, 28),
            score_args=score_args,
            power_types=[PowerType.Defense],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        reduction = easy_multiple_of_five(
            stats.attributes.stat_mod(AbilityScore.DEX)
            + 2 * stats.attributes.proficiency
        )
        feature = Feature(
            name="Deflect Missile",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} is hit by a ranged attack, it can use its reaction to reduce the damage taken by {reduction}.",
        )
        return [feature]


class _HardToPinDown(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Hard to Pin Down",
            power_category=PowerCategory.Theme,
            source="Foe Foundry",
            theme="Anti-Ranged",
            icon="fast-forward-button",
            reference_statblock="Spy",
            create_date=datetime(2023, 11, 28),
            score_args=dict(
                require_roles=MonsterRole.Skirmisher,
                require_stats=AbilityScore.DEX,
                require_attack_types=AttackType.AllMelee(),
            ),
            power_types=[PowerType.Defense, PowerType.Movement],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Hard to Pin Down",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} is difficult to pin down. Ranged attacks against it are made at disadvantage if there is not at least one hostile creature within 10 feet of {stats.selfref}.",
        )
        return [feature]


def _EyeOfTheStormPowers() -> List[Power]:
    class _EyeOfTheStorm(PowerWithStandardScoring):
        def __init__(self, name: str, damage_type: DamageType):
            self.damage_type = damage_type
            score_args = dict(
                require_damage=damage_type,
                require_damage_exact_match=True,
                require_attack_types=AttackType.AllMelee(),
            )

            super().__init__(
                name=name,
                power_category=PowerCategory.Theme,
                power_level=HIGH_POWER,
                source="Foe Foundry",
                theme="Anti-Ranged",
                icon="entangled-typhoon",
                reference_statblock="Fire Elemental",
                create_date=datetime(2023, 11, 28),
                score_args=score_args,
                power_types=[PowerType.AreaOfEffect, PowerType.Attack],
            )

        def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
            if stats.secondary_damage_type is None:
                stats = stats.copy(secondary_damage_type=self.damage_type)
            return stats

        def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
            dmg = math.ceil(stats.cr / 2.0)
            dmg_type = self.damage_type
            feature = Feature(
                name=self.name,
                action=ActionType.Feature,
                description=f"{stats.selfref.capitalize()} is at the heart of a raging storm that extends from it beginning at 10 feet and extending to 60 feet away from it. \
                    The storm counts as difficult terrain and heavily obscures the area. Any creature that starts its turn with the area of the storm takes {dmg} {dmg_type} damage.",
            )
            return [feature]

    options: list[dict] = [
        dict(name="Eye of the Storm", damage_type=DamageType.Lightning),
        dict(name="Eye of the Hurricane", damage_type=DamageType.Thunder),
        dict(name="Eye of the Blizzard", damage_type=DamageType.Cold),
        dict(name="Heart of the Inferno", damage_type=DamageType.Fire),
    ]

    return [_EyeOfTheStorm(**o) for o in options]


class _Overchannel(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Overchannel",
            power_category=PowerCategory.Theme,
            source="Foe Foundry",
            theme="Anti-Ranged",
            icon="charging",
            reference_statblock="Mage",
            power_level=HIGH_POWER,
            create_date=datetime(2023, 11, 28),
            score_args=dict(
                require_attack_types=AttackType.AllSpell(),
            ),
            power_types=[PowerType.Magic, PowerType.Attack],
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        if not stats.attack_types.intersection(AttackType.AllSpell()):
            stats = stats.grant_spellcasting(CasterType.Innate)
            stats = spell.Firebolt.copy(damage_scalar=0.9).add_as_secondary_attack(
                stats
            )
            return stats
        else:
            return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Overchannel",
            action=ActionType.BonusAction,
            description=f"The {stats.selfref} begins to channel vast amounts of power into its next spell. If it begins its next turn with no creature next to it, then the next spell attack it makes that turn that hits a target deals maximum damage.",
        )
        return [feature]


ArrowWard: Power = _ArrowWard()
AdaptiveCamouflage: Power = _AdaptiveCamouflage()
DeflectMissile: Power = _DeflectMissile()
EyeOfTheStorm: List[Power] = _EyeOfTheStormPowers()
HardToPinDown: Power = _HardToPinDown()
Overchannel: Power = _Overchannel()

AntiRangedPowers: List[Power] = [
    ArrowWard,
    AdaptiveCamouflage,
    DeflectMissile,
    HardToPinDown,
    Overchannel,
] + EyeOfTheStorm


# Drawn to Combat - monstrosity, beast - DC X stealth check at the end of the turn or summon another one of these creatures
