from datetime import datetime
from math import ceil
from typing import List

from num2words import num2words

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...spells import CasterType
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class DomineeringPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        reference_statblock: str = "Vampire",
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        magical_creatures = {
            CreatureType.Fiend,
            CreatureType.Fey,
            CreatureType.Dragon,
            CreatureType.Celestial,
            CreatureType.Undead,
        }
        required_creatures = magical_creatures | {CreatureType.Humanoid}

        def is_magical(c: BaseStatblock) -> bool:
            if c.creature_type in magical_creatures:
                return True

            # psychic humanoids
            if (
                any(t.is_spell() for t in c.attack_types)
                and c.secondary_damage_type == DamageType.Psychic
            ):
                return True

            return False

        super().__init__(
            name=name,
            source=source,
            power_category=PowerCategory.Theme,
            theme="domineering",
            reference_statblock=reference_statblock,
            create_date=create_date,
            power_level=power_level,
            icon=icon,
            power_types=power_types or [PowerType.Magic, PowerType.Debuff],
            score_args=dict(
                require_types=required_creatures,
                require_callback=is_magical,
                bonus_damage=DamageType.Psychic,
                bonus_roles=[MonsterRole.Leader, MonsterRole.Controller],
                require_stats=Stats.CHA,
                **score_args,
            ),
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        new_attributes = stats.attributes.boost(
            Stats.CHA, 4
        ).grant_proficiency_or_expertise(Skills.Persuasion)
        stats = stats.copy(attributes=new_attributes)
        stats = stats.grant_spellcasting(CasterType.Innate)
        return stats


class _CommandingPresence(DomineeringPower):
    def __init__(self):
        super().__init__(
            name="Commanding Presence",
            source="Foe Foundry",
            icon="overlord-helm",
            power_level=HIGH_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class

        targets = num2words(int(ceil(max(5, stats.cr / 3))))

        feature = Feature(
            name="Commanding Presence",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} chooses up to {targets} creatures it can see within 60 feet and attempts to magically compell them \
                 to grovel. The creatures must make a DC {dc} Wisdom save or be affected as by the *Command* spell. A creature that saves is immune to this effect for 24 hours.",
        )
        return [feature]


class _Dominate(DomineeringPower):
    def __init__(self):
        super().__init__(
            name="Charm",
            source="Foe Foundry",
            icon="smitten",
            power_level=HIGH_POWER,
            require_cr=7,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        charmed = Condition.Charmed

        feature = Feature(
            name="Dominate",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} targets one humanoid it can see within 30 feet of it. If the target can see {stats.selfref} \
                then it must succeed on a DC {dc} Wisdom save against this magic or be {charmed.caption} by {stats.selfref}. \
                While charmed in this way, the target treats {stats.selfref} as a trusted friend to be heeded and protected. \
                It takes {stats.selfref}'s requests or actions in the most favorable way it can.  \
                Each time the target takes damage, it may repeat the save to end the condition. \
                Otherwise, the effect lasts for 24 hours or until {stats.selfref} dies or is on anther plane of existence. \
                A creature that saves is immune to this effect for 24 hours.",
        )
        return [feature]


CommandingPresence: Power = _CommandingPresence()
Dominate: Power = _Dominate()

DomineeringPowers: List[Power] = [CommandingPresence, Dominate]
