from foe_foundry.environs import Affinity, Biome, Development
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import NaturalArmor
from ...attack_template import AttackTemplate, natural
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...powers import PowerSelection
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

HydraVariant = MonsterVariant(
    name="Hydra",
    description="Hydras are massive, multi-headed serpents that dwell in swamps and marshes. They are fearsome predators, capable of regenerating lost heads and limbs. Their blood is a potent poison, and their breath can melt flesh and bone.",
    monsters=[Monster(name="Hydra", cr=8, srd_creatures=["Hydra"])],
)
HydraFoulbloodVariant = MonsterVariant(
    name="Foulblood Hydra",
    description="Foulblood Hydras are born of a fell curse that blends foul demonic blood with the hydra's own. Their blood is a viscous, black ichor that can corrupt the land around them.",
    monsters=[Monster(name="Foulblood Hydra", cr=12, is_legendary=True)],
)


class _HydraTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "hydra":
            return PowerSelection(powers.LoadoutHydra)
        elif settings.monster_key == "foulblood-hydra":
            return PowerSelection(powers.LoadoutHydraFoulblooded)
        else:
            raise ValueError(f"Unknown monster key: {settings.monster_key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        is_legendary = settings.is_legendary

        # STATS
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats={
                AbilityScore.STR: StatScaling.Primary,
                AbilityScore.DEX: (StatScaling.Default, 2),
                AbilityScore.CON: (StatScaling.Constitution, 2),
                AbilityScore.INT: StatScaling.Low,
                AbilityScore.WIS: StatScaling.Default,
                AbilityScore.CHA: (StatScaling.Default, -3),
            },
            hp_multiplier=1.3 * settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Monstrosity,
            size=Size.Huge,
            creature_class="Hydra",
            senses=stats.senses.copy(darkvision=60),
        )
        stats = stats.with_types(
            primary_type=CreatureType.Monstrosity, additional_types=CreatureType.Fiend
        )

        stats = stats.copy(speed=stats.speed.delta(10).grant_swim())

        # LEGENDARY
        if is_legendary:
            stats = stats.as_legendary()

        # ARMOR CLASS
        stats = stats.add_ac_template(NaturalArmor)

        # ATTACKS
        attack = natural.Bite.with_display_name("Flesh-Dissolving Bites")
        stats = stats.copy(
            secondary_damage_type=DamageType.Acid,
        )
        stats = stats.with_set_attacks(5).copy(
            multiattack_custom_text="The hydra makes one attack for each of its heads"
        )
        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Bruiser,
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(
            Skills.Perception, Skills.Initiative
        )
        stats = stats.grant_proficiency_or_expertise(Skills.Perception)  # expertise

        # SAVES
        if cr >= 10:
            stats = stats.grant_save_proficiency(
                AbilityScore.CON, AbilityScore.STR, AbilityScore.WIS
            )

        # IMMUNITIES
        stats = stats.grant_resistance_or_immunity(
            resistances={DamageType.Acid},
            conditions={
                Condition.Blinded,
                Condition.Charmed,
                Condition.Deafened,
                Condition.Frightened,
                Condition.Stunned,
                Condition.Unconscious,
            },
        )

        # REACTIONS
        stats = stats.copy(reaction_count="One Per Head")

        return stats, [attack]


HydraTemplate: MonsterTemplate = _HydraTemplate(
    name="Hydra",
    tag_line="Multiheaded serpent of legend",
    description="Hydras are massive, multi-headed serpents that dwell in swamps and marshes. They are fearsome predators, capable of regenerating lost heads and limbs. Their blood is a potent poison, and their breath can melt flesh and bone.",
    treasure=[],
    variants=[HydraVariant, HydraFoulbloodVariant],
    species=[],
    environments=[
        (Biome.swamp, Affinity.native),  # Primary habitat in marshes and wetlands
        (Biome.lake, Affinity.native),  # Large bodies of freshwater they inhabit
        (Biome.river, Affinity.common),  # Flowing waters where they hunt
        (Biome.underground, Affinity.common),  # Caves near bodies of water
        (Development.wilderness, Affinity.common),  # Remote wetland areas
        (Development.ruin, Affinity.uncommon),  # Ancient sites reclaimed by water
    ],
)
