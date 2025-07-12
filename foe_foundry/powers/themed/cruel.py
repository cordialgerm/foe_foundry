from datetime import datetime
from typing import List

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import flags
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class CruelPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        reference_statblock: str = "Berserker",
        **score_args,
    ):
        standard_score_args = dict(
            require_attack_types=AttackType.AllMelee(),
            bonus_types=[
                CreatureType.Fiend,
                CreatureType.Monstrosity,
                CreatureType.Humanoid,
            ],
            bonus_skills=Skills.Intimidation,
            bonus_stats=Stats.CHA,
            require_roles={
                MonsterRole.Ambusher,
                MonsterRole.Bruiser,
                MonsterRole.Soldier,
            },
            **score_args,
        )
        super().__init__(
            name=name,
            power_type=PowerType.Theme,
            source=source,
            theme="cruel",
            icon=icon,
            reference_statblock=reference_statblock,
            create_date=create_date,
            power_level=power_level,
            score_args=standard_score_args,
        )


class _BloodiedFrenzy(CruelPower):
    def __init__(self):
        super().__init__(
            name="Bloodied Frenzy",
            source="Foe Foundry",
            icon="enrage",
            require_cr=3,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        damage_type = stats.secondary_damage_type or stats.primary_damage_type
        dmg = DieFormula.target_value(1 + 0.5 * stats.cr, force_die=Die.d4)
        feature = Feature(
            name="Bloodied Frenzy",
            description=f"The attack deals an additional {dmg.description} {damage_type} damage if the target is at or below half-health.",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
        )
        return [feature]


class _BrutalCritical(CruelPower):
    def __init__(self):
        super().__init__(
            name="Brutal Critical",
            source="SRD5.1 Champion, Barbarian",
            icon="decapitation",
            power_level=HIGH_POWER,
            require_no_flags=flags.MODIFIES_CRITICAL,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        stats = stats.with_flags(flags.MODIFIES_CRITICAL)
        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        crit_lower = 19 if stats.cr <= 7 else 18
        dmg = stats.target_value(target=1.0, force_die=Die.d6)
        dmg_type = stats.secondary_damage_type or stats.primary_damage_type
        feature = Feature(
            name="Brutal Critical",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} scores a critical hit on an unmodified attack roll of {crit_lower}-20. \
                Additionally, a critical hit from {stats.selfref} deals an additional {dmg.description} {dmg_type} damage (do not apply crit modifier to this damage), \
                and the creature dies if this attack reduces its hit points to 0.",
        )
        return [feature]


BloodiedFrenzy: Power = _BloodiedFrenzy()
BrutalCritical: Power = _BrutalCritical()

CruelPowers: List[Power] = [
    BloodiedFrenzy,
    BrutalCritical,
]
