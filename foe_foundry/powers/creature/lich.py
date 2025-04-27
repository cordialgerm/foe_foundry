from datetime import datetime
from typing import List

from foe_foundry.references import Token, creature_ref
from foe_foundry.utils import easy_multiple_of_five

from ...creature_types import CreatureType
from ...die import DieFormula
from ...features import ActionType, Feature
from ...spells import (
    CasterType,
    abjuration,
    conjuration,
    enchantment,
    evocation,
    illusion,
    necromancy,
    transmutation,
)
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


def is_lich(s: BaseStatblock) -> bool:
    return s.creature_subtype == "Lich"


class LichPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str = "Foe Foundry",
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            theme="lich",
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=datetime(2025, 4, 27),
            score_args=dict(
                require_callback=is_lich,
                require_spellcasting=CasterType.Arcane,
                require_types=[CreatureType.Undead],
            )
            | score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        return stats.grant_spellcasting(CasterType.Arcane)


class _LichSpellcasting(LichPower):
    def __init__(self):
        super().__init__(
            name="Lich Spellcasting",
            power_level=HIGH_POWER,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        stats = stats.add_spells(
            [
                # 3/day
                evocation.Fireball.for_statblock(uses=3),
                evocation.LightningBolt.for_statblock(uses=3),
                conjuration.Cloudkill.for_statblock(uses=3),
                abjuration.DispelMagic.for_statblock(uses=3),
                # 2/day
                illusion.GreaterInvisibility.for_statblock(uses=2),
                necromancy.FingerOfDeath.for_statblock(uses=2),
                transmutation.Disintegrate.for_statblock(uses=2),
                evocation.ChainLightning.for_statblock(uses=2),
                evocation.WallOfForce.for_statblock(uses=2),
                # 1/day
                conjuration.Teleport.for_statblock(uses=1),
                enchantment.PowerWordKill.for_statblock(uses=1),
                abjuration.PrismaticWall.for_statblock(uses=1),
            ]
        )

        if stats.cr >= 26:
            stats = stats.add_spells(
                [
                    conjuration.Wish.for_statblock(uses=1),
                ]
            )

        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature1 = Feature(
            name="Eldritch Mastery",
            action=ActionType.Feature,
            description="The lich can change the damage type of any of its spells, abilities, attacks to fire, cold, lightning, poison, or necrotic damage.",
        )
        feature2 = Feature(
            name="Spirit Anchor",
            action=ActionType.Feature,
            description="If the lich is destroyed, and its soul anchor is intact, it returns to life in 1d10 days.",
        )
        return [feature1, feature2]


class _SoulHarvest(LichPower):
    def __init__(self):
        super().__init__(
            name="Soul Harvest",
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        temp_hp = easy_multiple_of_five(stats.hp.average * 0.1)
        feature = Feature(
            name="Soul Harvest",
            action=ActionType.Reaction,
            description=f"Whenever a creature within 30 feet of {stats.selfref} is reduced to 0 hp, \
                {stats.selfref} can choose to recharge an expended spell usage, recharge an ability, or gain {temp_hp} temp hp",
        )
        return [feature]


class _EverlastingImmortality(LichPower):
    def __init__(self):
        super().__init__(
            name="Everlasting Immortality",
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        token = Token(
            name="Soul Anchor Echo", dc=stats.difficulty_class_token, charges=3
        )
        feature = Feature(
            name="Everlasting Immortality",
            action=ActionType.Reaction,
            creates_token=True,
            uses=1,
            description=f"The lich summons an {token.caption} to an unoccupied space within 30 feet of it. While {stats.selfref} is within 30 feet of the token, it is immune to all damage.",
        )
        return [feature]


class _UndyingServants(LichPower):
    def __init__(self):
        super().__init__(
            name="Undying Servants",
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        steed = creature_ref("Young Black Dragon" if stats.cr >= 26 else "Nightmare")
        grave_guard_amount = (
            DieFormula.from_expression("1d4 + 1")
            if stats.cr >= 26
            else DieFormula.from_expression("6d6")
        )
        spirit_amount = 2 if stats.cr >= 26 else 1
        wraith = creature_ref("Wraiths" if stats.cr >= 26 else "Wraith")
        grave_guard = creature_ref(
            "Skeletal Grave Guard" if stats.cr >= 26 else "Skeleton"
        )

        options = [
            f"Dread Steed: a {steed}",
            f"Grave Guard: {grave_guard_amount.description} {grave_guard}",
            f"Bound Spirits: {spirit_amount} {wraith}",
        ]
        options = "\n".join(f"<li>{o}</li>\n" for o in options)
        ul = f"<ul>{options}</ul>"

        feature = Feature(
            name="Undying Servants",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} magically summons undead servants to unoccupied spaces within 60 feet. \
                The summoned creatures act on initiative count 0. Whenever {stats.selfref} takes damage, it can instead choose to transfer that damage to one of its summons (no action required). \
                Any excess damage is applied to the lich itself.\
                <br /> \
                {stats.selfref.capitalize()} can choose from the following options:\n"
            + ul,
        )
        return [feature]


LichSpellcasting: Power = _LichSpellcasting()
SoulHarvest: Power = _SoulHarvest()
EverlastingImmortality: Power = _EverlastingImmortality()
UndyingServants: Power = _UndyingServants()
LichPowers: list[LichPower] = [
    LichSpellcasting,
    SoulHarvest,
    EverlastingImmortality,
    UndyingServants,
]
