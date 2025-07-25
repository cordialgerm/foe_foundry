from foe_foundry.environs import Affinity, Biome, Development
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import UnholyArmor
from ...attack_template import AttackTemplate, spell
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...powers import (
    PowerSelection,
)
from ...role_types import MonsterRole
from ...size import Size
from ...skills import AbilityScore, Skills, StatScaling
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

HollowGazerVariant = MonsterVariant(
    name="Hollow Gazer",
    description="Hollow Gazers are seekers of dark and forbidden knowledge that have been driven insane by cursed knowledge best left unknown.",
    monsters=[
        Monster(name="Hollow Gazer", cr=2, other_creatures={"Nothic": "mm24"}),
        Monster(name="Hollow Gazer of Ruin", cr=6),
    ],
)


class _HollowGazerTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "hollow-gazer":
            return PowerSelection(powers.LoadoutHollowGazer)
        elif settings.monster_key == "hollow-gazer-of-ruin":
            return PowerSelection(powers.LoadoutHollowGazerOfRuin)
        else:
            raise ValueError(
                f"Unexpected monster key {settings.monster_key} for Hollow Gazer generation."
            )

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr

        # STATS
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats={
                AbilityScore.STR: (StatScaling.Default, -2),
                AbilityScore.DEX: StatScaling.Medium,
                AbilityScore.INT: StatScaling.Primary,
                AbilityScore.WIS: (StatScaling.Medium, 1),
                AbilityScore.CHA: (StatScaling.Default, -3),
            },
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Aberration,
            size=Size.Medium,
            creature_class="Hollow Gazer",
            languages=["Almost Comprehensible Gibberish"],
            senses=stats.senses.copy(truesight=120),
        )

        # ARMOR CLASS
        stats = stats.add_ac_template(UnholyArmor)

        # ATTACKS
        attack = spell.Gaze.with_display_name("Pitying Gaze")
        stats = stats.copy(secondary_damage_type=DamageType.Psychic)

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Controller,
        )

        # SKILLS
        expertise = [Skills.Arcana, Skills.Insight, Skills.Perception]
        stats = stats.grant_proficiency_or_expertise(
            Skills.Stealth, *expertise
        ).grant_proficiency_or_expertise(*expertise)

        # SAVES
        if cr >= 6:
            stats = stats.grant_save_proficiency(AbilityScore.WIS, AbilityScore.CON)

        # RESISTANCES / IMMUNITIES
        stats = stats.grant_resistance_or_immunity(
            conditions={Condition.Charmed}, resistances={DamageType.Psychic}
        )

        return stats, [attack]


HollowGazerTemplate: MonsterTemplate = _HollowGazerTemplate(
    name="Hollow Gazer",
    tag_line="Insane Seekers of Twisted Knowledge",
    description="Hollow Gazers are seekers of dark and forbidden knowledge that have been driven insane by cursed knowledge best left unknown.",
    treasure=[],
    variants=[HollowGazerVariant],
    species=[],
    environments=[
        (
            Biome.underground,
            Affinity.native,
        ),  # Dark underground lairs where they study forbidden lore
        (
            Development.ruin,
            Affinity.native,
        ),  # Ancient ruins filled with cursed knowledge
        (
            Development.dungeon,
            Affinity.common,
        ),  # Deep dungeons with hidden secrets to uncover
        (
            Development.stronghold,
            Affinity.uncommon,
        ),  # Abandoned towers and libraries they've taken over
        (
            Development.wilderness,
            Affinity.rare,
        ),  # Remote areas where they might hide their research
        (
            Development.settlement,
            Affinity.rare,
        ),  # Occasionally infiltrating towns to steal knowledge
    ],
)
