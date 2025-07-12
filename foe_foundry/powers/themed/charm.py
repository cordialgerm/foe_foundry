from datetime import datetime
from typing import List

from ...attack_template import spell
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...spells import CasterType, enchantment
from ...statblocks import BaseStatblock
from ..power import (
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class CharmingPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        reference_statblock: str = "Enchanter Mage",
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        def humanoid_is_psychic_spellcaster(candidate: BaseStatblock) -> bool:
            if candidate.creature_type == CreatureType.Humanoid:
                return any(t.is_spell() for t in candidate.attack_types) and (
                    candidate.secondary_damage_type == DamageType.Psychic
                    or candidate.caster_type == CasterType.Psionic
                )
            return True

        standard_score_args = dict(
            require_types=[
                CreatureType.Fey,
                CreatureType.Fiend,
                CreatureType.Humanoid,
            ],
            require_stats=Stats.CHA,
            require_callback=humanoid_is_psychic_spellcaster,
            bonus_roles=[
                MonsterRole.Controller,
                MonsterRole.Leader,
                MonsterRole.Support,
            ],
            bonus_skills=[Skills.Deception, Skills.Persuasion],
            attack_names=spell.Gaze,
            bonus_damage=DamageType.Psychic,
            **score_args,
        )

        super().__init__(
            name=name,
            theme="Charm",
            reference_statblock=reference_statblock,
            source=source,
            icon=icon,
            power_level=power_level,
            power_category=PowerCategory.Theme,
            create_date=create_date,
            score_args=standard_score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        stats = stats.grant_spellcasting(CasterType.Psionic)

        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Psychic)

        return stats


class _MentalSummons(CharmingPower):
    def __init__(self):
        super().__init__(
            name="Mental Summons",
            icon="telepathy",
            source="A5E SRD Murmuring Worm",
            create_date=datetime(2023, 11, 23),
            power_level=LOW_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Mental Summons",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} targets a creature with an Intelligence score greater than 3 within 120 feet. \
                The target makes a DC {dc} Wisdom saving throw. On a failure, it uses its reaction to move up to its speed towards {stats.selfref} \
                by the shortest route possible, avoiding hazards but not opportunity attacks. This is a magical charm effect.",
        )
        return [feature]


class _SweetPromises(CharmingPower):
    def __init__(self):
        super().__init__(
            name="Sweet Promises",
            source="A5E SRD Rakshasa",
            icon="smitten",
            create_date=datetime(2023, 11, 23),
            power_level=LOW_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        charmed = Condition.Charmed
        stunned = Condition.Stunned
        feature = Feature(
            name="Sweet Promises",
            action=ActionType.Action,
            replaces_multiattack=1,
            uses=1,
            description=f"{stats.selfref.capitalize()} targets a creature that can hear it within 60 feet, offering something the target covets. \
                The target makes a DC {dc} Wisdom saving throw. On a failure, the target is {charmed.caption} until the end of its next turn, and {stunned.caption} while {charmed.caption} in this way.",
        )
        return [feature]


class _WardingCharm(CharmingPower):
    def __init__(self):
        super().__init__(
            name="Warding Charm",
            icon="heart-shield",
            source="A5E SRD Vampire",
            create_date=datetime(2023, 11, 23),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Warding Charm",
            action=ActionType.Reaction,
            uses=1,
            description=f"When a creature {stats.selfref} can see targets it with a melee attack but before the attack is made, \
                {stats.selfref} casts *Charm Person* with a DC of {dc} on that target.",
        )
        return [feature]


class _CharmingWords(CharmingPower):
    def __init__(self):
        super().__init__(
            name="Charming Words",
            source="SRD5.1 Charm Person",
            icon="convince",
            power_level=LOW_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.grant_spellcasting(CasterType.Psionic)
        spell = enchantment.CharmPerson.copy(upcast=False).for_statblock()
        return stats.add_spell(spell)


CharmingWords: Power = _CharmingWords()
MentalSummons: Power = _MentalSummons()
SweetPromises: Power = _SweetPromises()
WardingCharm: Power = _WardingCharm()

CharmPowers: List[Power] = [CharmingWords, MentalSummons, SweetPromises, WardingCharm]
