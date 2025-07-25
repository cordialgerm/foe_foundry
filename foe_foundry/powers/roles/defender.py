from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...skills import Skills
from ...statblocks import BaseStatblock
from ..power import (
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class DefenderPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        reference_statblock: str = "Shield Guardian",
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        standard_score_args = dict(
            require_roles=MonsterRole.Defender,
            bonus_skills=Skills.Intimidation,
            bonus_shield=True,
            bonus_attack_types=AttackType.AllMelee(),
            **score_args,
        )
        super().__init__(
            name=name,
            power_category=PowerCategory.Role,
            power_level=power_level,
            source=source,
            icon=icon,
            create_date=create_date,
            theme="Defender",
            reference_statblock=reference_statblock,
            power_types=power_types,
            score_args=standard_score_args,
        )


class _Protection(DefenderPower):
    def __init__(self):
        super().__init__(
            name="Protection",
            source="A5E SRD Protection",
            icon="armor-vest",
            power_level=LOW_POWER,
            power_types=[PowerType.Defense],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Protection",
            description=f"When an ally within 5 feet is targeted by an attack or spell, {stats.roleref} can make themselves the intended target of the attack or spell instead.",
            action=ActionType.Reaction,
        )
        return [feature]


class _Taunt(DefenderPower):
    def __init__(self):
        super().__init__(
            name="Taunt",
            source="A5E SRD Taunting Smite",
            icon="shouting",
            power_types=[PowerType.Attack, PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Taunt",
            description="On a hit, the target has disadvantage on attack rolls against any other creature until the end of its next turn.",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
        )
        return [feature]


class _ZoneOfControl(DefenderPower):
    def __init__(self):
        super().__init__(
            name="Zone Of Control",
            icon="nested-hexagons",
            source="Foe Foundry",
            power_level=LOW_POWER,
            power_types=[PowerType.Environmental, PowerType.Debuff],
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        new_attributes = stats.attributes.grant_proficiency_or_expertise(
            Skills.Athletics
        )
        stats = stats.copy(attributes=new_attributes)
        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Zone of Control",
            action=ActionType.Feature,
            description=f"Any creature that attempts to Disengage from {stats.roleref} must make a DC {dc} Strength save or have their speed reduced to 0 until the end of their next turn.",
        )
        return [feature]


class _SpellReflection(DefenderPower):
    def __init__(self):
        super().__init__(
            name="Spell Reflection",
            source="A5E SRD Demilich Mastermind",
            icon="divert",
            bonus_types={
                CreatureType.Aberration,
                CreatureType.Dragon,
                CreatureType.Fiend,
                CreatureType.Monstrosity,
            },
            power_types=[PowerType.Defense],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Spell Reflection",
            action=ActionType.Reaction,
            description=f"If {stats.roleref} succeeds on a saving throw against a spell or if a spell attack misses it, then {stats.roleref} can choose another creature (including the spellcaster) it can see within 120 feet of it. \
                The spell or attack targets the chosen creature instead.",
        )
        return [feature]


Protection: Power = _Protection()
SpellReflection: Power = _SpellReflection()
Taunt: Power = _Taunt()
ZoneOfControl: Power = _ZoneOfControl()

DefenderPowers = [Protection, SpellReflection, Taunt, ZoneOfControl]
