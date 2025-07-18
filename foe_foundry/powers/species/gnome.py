from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import Condition, conditions
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import RIBBON_POWER, Power, PowerCategory, PowerWithStandardScoring


class GnomePower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        icon: str,
        power_level: float = RIBBON_POWER,
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        self.species = "gnome"

        def is_gnome(stats: BaseStatblock) -> bool:
            return (
                stats.creature_subtype is not None
                and stats.creature_subtype.lower() == "gnome"
            )

        standard_score_args = dict(
            require_types=CreatureType.Humanoid,
            require_callback=is_gnome,
            **score_args,
        )
        super().__init__(
            name=name,
            power_category=PowerCategory.Species,
            power_level=power_level,
            icon=icon,
            source="Foe Foundry",
            reference_statblock="Spy",
            create_date=datetime(2025, 3, 2),
            theme="Gnome",
            power_types=power_types,
            score_args=standard_score_args,
        )


class _GnomeCunning(GnomePower):
    def __init__(self):
        super().__init__(
            name="Gnome Cunning",
            icon="fox",
            bonus_roles={
                MonsterRole.Artillery,
                MonsterRole.Controller,
                MonsterRole.Soldier,
            },
            power_types=[PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        weakened = conditions.Weakened(save_end_of_turn=False)
        feature = Feature(
            name="Gnomeish Cunning",
            description=f"Immediately after hitting an enemy with an attack, {stats.selfref} causes the target to be {weakened.caption}. {weakened.description_3rd}",
            action=ActionType.BonusAction,
            uses=1,
        )
        return [feature]


class _GnomeIngenuity(GnomePower):
    def __init__(self):
        super().__init__(
            name="Gnome Ingenuity",
            icon="gears",
            bonus_roles={
                MonsterRole.Support,
                MonsterRole.Leader,
                MonsterRole.Bruiser,
                MonsterRole.Defender,
            },
            power_types=[PowerType.Buff, PowerType.Defense],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        temp_hp = easy_multiple_of_five(2 * stats.attributes.proficiency, min_val=5)
        feature = Feature(
            name="Gnomeish Ingenuity",
            description=f"Once per day, {stats.selfref} succeeds on a failed WIS, CHA, or INT saving throw. {stats.selfref.capitalize()} also gains {temp_hp} temporary hit points.",
            action=ActionType.Reaction,
            uses=1,
        )
        return [feature]


class _GnomishInvisibility(GnomePower):
    def __init__(self):
        super().__init__(
            name="Gnomish Invisibility",
            icon="invisible",
            bonus_roles={MonsterRole.Skirmisher, MonsterRole.Ambusher},
            power_types=[PowerType.Stealth],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        invisible = Condition.Invisible
        feature = Feature(
            name="Gnomish Invisibility",
            description=f"{stats.selfref.capitalize()} becomes {invisible.caption} until the beginning of its next turn or until it attacks or casts a spell",
            action=ActionType.Action,
            replaces_multiattack=1,
            uses=1,
        )
        return [feature]


GnomeCunning: Power = _GnomeCunning()
GnomeIngenuity: Power = _GnomeIngenuity()
GnomeishInvisibility: Power = _GnomishInvisibility()

GnomePowers: list[Power] = [
    GnomeCunning,
    GnomeIngenuity,
    GnomeishInvisibility,
]
