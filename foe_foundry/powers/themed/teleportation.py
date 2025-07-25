from datetime import datetime
from math import ceil
from typing import List

from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...spells import CasterType
from ...statblocks import BaseStatblock
from .. import flags
from ..power import (
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class TeleportationPower(PowerWithStandardScoring):
    def __init__(
        self,
        *,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        power_types: List[PowerType],
        **score_args,
    ):
        existing_callback = score_args.pop("require_callback", None)

        def humanoid_is_caster(c: BaseStatblock) -> bool:
            if existing_callback is not None and not existing_callback(c):
                return False

            if c.creature_type == CreatureType.Humanoid:
                return (
                    any(t.is_spell() for t in c.attack_types)
                    and c.caster_type is not None
                    and c.caster_type not in {CasterType.Divine, CasterType.Primal}
                )
            else:
                return True

        super().__init__(
            name=name,
            source=source,
            theme="teleportation",
            icon=icon,
            reference_statblock="Transmuter Mage",
            power_level=power_level,
            power_category=PowerCategory.Theme,
            create_date=create_date,
            score_args=dict(
                require_callback=humanoid_is_caster,
                require_types={
                    CreatureType.Fey,
                    CreatureType.Fiend,
                    CreatureType.Aberration,
                    CreatureType.Humanoid,
                },
                require_cr=3,
                bonus_attack_types=AttackType.AllSpell(),
                bonus_roles={MonsterRole.Ambusher, MonsterRole.Controller},
            )
            | score_args,
            power_types=power_types,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        return stats


class _BendSpace(TeleportationPower):
    def __init__(self):
        super().__init__(
            name="Bend Space",
            icon="thrust-bend",
            source="Foe Foundry",
            power_types=[PowerType.Movement, PowerType.Defense],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Bend Space",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} would be hit by an attack, it teleports and exchanges position with an ally it can see within 60 feet of it. The ally is then hit by the attack instead.",
        )
        return [feature]


def no_unique_movement(stats: BaseStatblock) -> bool:
    return not stats.has_unique_movement_manipulation


class _MistyStep(TeleportationPower):
    def __init__(self):
        super().__init__(
            name="Misty Step",
            source="SRD5.1 Misty Step",
            icon="journey",
            power_level=LOW_POWER,
            require_callback=no_unique_movement,
            require_no_flags={flags.HAS_TELEPORT, flags.NO_TELEPORT},
            power_types=[PowerType.Movement],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        distance = 30 if stats.cr <= 7 else 60
        uses = int(min(3, ceil(stats.attributes.proficiency / 2)))

        feature = Feature(
            name="Misty Step",
            action=ActionType.BonusAction,
            uses=uses,
            description=f"{stats.selfref.capitalize()} teleports up to {distance} feet to an unoccupied space it can see.",
        )

        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        return stats.copy(has_unique_movement_manipulation=True)


class _Scatter(TeleportationPower):
    def __init__(self):
        super().__init__(
            name="Scatter",
            icon="misdirection",
            source="Foe Foundry",
            power_types=[PowerType.Movement, PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        distance = 30 if stats.cr <= 6 else 60
        dc = stats.difficulty_class
        count = int(max(2, ceil(stats.cr / 3)))

        feature = Feature(
            name="Scatter",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} forces up to {count} creatures it can see within {distance} feet to make a DC {dc} Charisma save. \
                On a failure, the target is teleported to an unoccupied space within {4 * distance} feet that {stats.selfref} can see. \
                The space must be on the ground or on a floor.",
        )

        return [feature]


BendSpace: Power = _BendSpace()
MistyStep: Power = _MistyStep()
Scatter: Power = _Scatter()

TeleportationPowers: List[Power] = [BendSpace, MistyStep, Scatter]
