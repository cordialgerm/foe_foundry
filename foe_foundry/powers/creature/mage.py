from datetime import datetime
from math import ceil
from typing import List

from ...creature_types import CreatureType
from ...features import ActionType, Feature
from ...spells import (
    CasterType,
    abjuration,
    conjuration,
    evocation,
    illusion,
    transmutation,
)
from ...statblocks import BaseStatblock
from ..power import (
    LOW_POWER,
    MEDIUM_POWER,
    RIBBON_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class MagePower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        existing_callback = score_args.pop("require_callback", None)

        def require_callback(s: BaseStatblock) -> bool:
            return s.creature_subtype == "Mage" and (
                existing_callback(s) if existing_callback else True
            )

        super().__init__(
            name=name,
            source=source,
            theme="mage",
            reference_statblock="Mage",
            icon=icon,
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=datetime(2025, 3, 7),
            score_args=dict(
                require_callback=require_callback,
                require_types=[CreatureType.Humanoid],
            )
            | score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        return stats.grant_spellcasting(CasterType.Arcane)


class _ProtectiveMagic(MagePower):
    def __init__(self):
        super().__init__(
            name="Protective Magic",
            source="Foe Foundry",
            icon="shield-reflect",
            power_level=MEDIUM_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        uses = int(min(3, ceil(stats.attributes.proficiency / 2)))

        feature = Feature(
            name="Protective Magic",
            action=ActionType.Reaction,
            uses=uses,
            description=f"{stats.selfref.capitalize()} casts *Shield* or *Counterspell* in response to being attacked or being targeted by a spell",
        )
        return [feature]


class _ApprenticeMage(MagePower):
    def __init__(self):
        super().__init__(
            name="Apprentice Mage",
            source="Foe Foundry",
            icon="spell-book",
            power_level=RIBBON_POWER,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        stats = stats.add_spells(
            [
                evocation.BurningHands.for_statblock(),
                evocation.IceKnife.for_statblock(),
                evocation.Thunderwave.for_statblock(),
            ]
        )
        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return []


class _AdeptMage(MagePower):
    def __init__(self):
        super().__init__(
            name="Adept Mage",
            source="Foe Foundry",
            icon="spell-book",
            power_level=LOW_POWER,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        stats = stats.add_spells(
            [
                illusion.Invisibility.for_statblock(uses=1),
                conjuration.Web.for_statblock(uses=1),
                evocation.Shatter.for_statblock(uses=1),
            ]
        )
        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return []


class _Mage(MagePower):
    def __init__(self):
        super().__init__(
            name="Mage",
            source="Foe Foundry",
            icon="spell-book",
            power_level=MEDIUM_POWER,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        stats = stats.add_spells(
            [
                illusion.GreaterInvisibility.for_statblock(uses=1),
                transmutation.Fly.for_statblock(uses=1),
                evocation.WallOfForce.for_statblock(uses=1),
            ]
        )
        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return []


class _Archmage(MagePower):
    def __init__(self):
        super().__init__(
            name="Mage",
            source="Foe Foundry",
            icon="spell-book",
            power_level=MEDIUM_POWER,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        stats = stats.add_spells(
            [
                illusion.GreaterInvisibility.for_statblock(uses=1),
                evocation.WallOfForce.for_statblock(uses=1),
                abjuration.GlobeOfInvulnerability.for_statblock(uses=1),
                conjuration.Teleport.for_statblock(uses=1),
            ]
        )
        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return []


ProtectiveMagic: Power = _ProtectiveMagic()
ApprenticeMage: Power = _ApprenticeMage()
AdeptMage: Power = _AdeptMage()
Mage: Power = _Mage()
Archmage: Power = _Archmage()


MagePowers: list[Power] = [
    ProtectiveMagic,
    ApprenticeMage,
    AdeptMage,
    Mage,
    Archmage,
]
