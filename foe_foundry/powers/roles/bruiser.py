from datetime import datetime
from typing import List

from ...attack_template import natural as natural_attacks
from ...attack_template import weapon
from ...attributes import Skills, Stats
from ...damage import Attack, AttackType, Bleeding, Condition, DamageType
from ...die import Die
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class BruiserPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        reference_statblock: str = "Ogre",
        **score_args,
    ):
        standard_score_args = dict(
            require_roles=MonsterRole.Bruiser,
            bonus_stats=[Stats.STR, Stats.CON],
            bonus_skills=Skills.Athletics,
            **score_args,
        )
        super().__init__(
            name=name,
            power_type=PowerCategory.Role,
            power_level=power_level,
            source=source,
            create_date=create_date,
            icon=icon,
            theme="Bruiser",
            reference_statblock=reference_statblock,
            score_args=standard_score_args,
        )


class _GrapplingStrike(BruiserPower):
    def __init__(self):
        super().__init__(
            name="Grappler",
            source="A5E SRD Grappler",
            icon="grab",
            attack_names={natural_attacks.Slam},
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Athletics)
        stats = stats.copy(attributes=new_attrs)
        grappled = Condition.Grappled
        restrained = Condition.Restrained

        dc = stats.difficulty_class

        stats = stats.add_attack(
            scalar=0.7,
            damage_type=DamageType.Bludgeoning,
            attack_type=AttackType.MeleeNatural,
            die=Die.d6,
            name="Grappling Strike",
            additional_description=f"On a hit, the target must make a DC {dc} Strength save or be {grappled.caption} (escape DC {dc}). \
                 While grappled in this way, the creature is also {restrained.caption}",
        )

        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return []


class _CleavingBlows(BruiserPower):
    def __init__(self):
        super().__init__(
            name="Cleaving Blows",
            source="Foe Foundry",
            icon="meat-cleaver",
            attack_names={weapon.Greataxe, natural_attacks.Claw},
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Cleaving Blows",
            action=ActionType.BonusAction,
            description=f"Immediately after the {stats.selfref} hits with a weapon attack, it may make the same attack against another target within its reach.",
            recharge=4,
        )
        return [feature]


class _StunningBlow(BruiserPower):
    def __init__(self):
        super().__init__(
            name="Stunning Blow",
            source="Foe Foundry",
            icon="wood-club",
            power_level=HIGH_POWER,
            require_cr=1,
            attack_names={weapon.Maul, weapon.MaceAndShield, natural_attacks.Slam},
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        stunned = Condition.Stunned

        feature = Feature(
            name="Stunning Blow",
            action=ActionType.BonusAction,
            description=f"Immediately after {stats.roleref} hits with a weapon attack, it may force the target to succeed on a DC {dc} Constitution save or be {stunned.caption} until the end of the {stats.selfref}'s next turn.",
            recharge=6,
        )

        return [feature]


class _Rend(BruiserPower):
    def __init__(self):
        super().__init__(
            name="Rend",
            source="Foe Foundry",
            icon="tearing",
            attack_names={
                natural_attacks.Bite,
                natural_attacks.Horns,
                weapon.Daggers,
            },
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        dc = stats.difficulty_class
        attack_type = (
            AttackType.MeleeWeapon
            if stats.attack.attack_type != AttackType.MeleeNatural
            else AttackType.MeleeNatural
        )

        def customize(a: Attack) -> Attack:
            dmg = a.damage.formula.copy(mod=0)
            bleeding = Bleeding(damage=dmg)
            return a.copy(
                additional_description=f"On a hit, the target must succeed on a DC {dc} Constitution saving throw or gain {bleeding}",
            )

        stats = stats.add_attack(
            scalar=0.7,
            damage_type=DamageType.Piercing,
            attack_type=attack_type,
            name="Rend",
            callback=customize,
        )

        return stats


CleavingBlows: Power = _CleavingBlows()
GrapplingStrike: Power = _GrapplingStrike()
Rend: Power = _Rend()
StunningBlow: Power = _StunningBlow()


BruiserPowers: List[Power] = [CleavingBlows, GrapplingStrike, Rend, StunningBlow]
