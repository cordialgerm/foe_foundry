from foe_foundry.environs import Affinity, Biome, Development
from foe_foundry.statblocks import BaseStatblock
from foe_foundry.utils import choose_enum

from ...ac_templates import StuddedLeatherArmor
from ...attack_template import AttackTemplate, weapon
from ...creature_types import CreatureType
from ...damage import DamageType
from ...powers import PowerLoadout, PowerSelection, flags
from ...powers.species import powers_for_role
from ...role_types import MonsterRole
from ...size import Size
from ...skills import AbilityScore, Skills, StatScaling
from ...spells import CasterType
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from ..species import AllSpecies, HumanSpecies
from . import powers

DruidVariant = MonsterVariant(
    name="Druid",
    description="Druids use primal magic to protect the natural world and its inhabitants. They are often found in the wilds, where they can commune with nature and draw upon its power.",
    monsters=[
        Monster(name="Druid", cr=2, srd_creatures=["Druid"]),
        Monster(name="Druid Greenwarden", cr=6),
        Monster(
            name="Archdruid of the Old Way",
            cr=12,
            other_creatures={"Archdruid": "mmotm"},
        ),
        Monster(name="Archdruid of the First Grove", cr=16, is_legendary=True),
    ],
)


class _DruidTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.species is not None:
            species_loadout = PowerLoadout(
                name=f"{settings.species.name} Powers",
                flavor_text=f"{settings.species.name} Powers",
                powers=powers_for_role(
                    species=settings.species.key,
                    role=[MonsterRole.Support],
                ),
            )
        else:
            species_loadout = None

        if settings.monster_key == "druid":
            return PowerSelection(powers.LoadoutDruid, species_loadout)
        elif settings.monster_key == "druid-greenwarden":
            return PowerSelection(powers.LoadoutGreenwarden, species_loadout)
        elif settings.monster_key == "archdruid-of-the-old-way":
            return PowerSelection(powers.LoadoutArchdruid, species_loadout)
        elif settings.monster_key == "archdruid-of-the-first-grove":
            return PowerSelection(powers.LoadoutArchdruid, species_loadout)
        else:
            raise ValueError(f"Unknown monster key: {settings.monster_key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        species = settings.species if settings.species else HumanSpecies
        rng = settings.rng
        is_legendary = settings.is_legendary

        # STATS
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            species_key=species.key,
            cr=cr,
            stats={
                AbilityScore.STR: StatScaling.Default,
                AbilityScore.DEX: StatScaling.Medium,
                AbilityScore.INT: (StatScaling.Default, 2),
                AbilityScore.WIS: StatScaling.Primary,
                AbilityScore.CHA: (StatScaling.Default, 1),
            },
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Humanoid,
            size=Size.Medium,
            languages=["Common", "Druidic", "Sylvan"],
            creature_class="Druid",
            caster_type=CasterType.Primal,
            uses_shield=False,
        )

        # LEGENDARY
        if is_legendary:
            stats = stats.as_legendary()

        # ARMOR CLASS
        stats = stats.add_ac_template(StuddedLeatherArmor)

        # ATTACKS
        attack = weapon.Staff.with_display_name("Staff of the Wild")

        secondary_damage_type = choose_enum(
            rng,
            [DamageType.Poison, DamageType.Fire, DamageType.Cold, DamageType.Lightning],
        )

        stats = stats.copy(secondary_damage_type=secondary_damage_type)

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Support,
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(
            Skills.Medicine, Skills.Nature, Skills.Perception
        )

        # SAVES
        if cr >= 8:
            stats = stats.grant_save_proficiency(AbilityScore.WIS, AbilityScore.CON)

        # FLAGS
        # Druids already have healing
        stats = stats.with_flags(flags.HAS_HEALING)

        return stats, [attack]


DruidTemplate: MonsterTemplate = _DruidTemplate(
    name="Druid",
    tag_line="Stewards and Sages of Nature",
    description="Druids use primal magic to protect the natural world and its inhabitants. They are often found in the wilds, where they can commune with nature and draw upon its power.",
    treasure=["Relics", "Individual"],
    variants=[DruidVariant],
    species=AllSpecies,
    environments=[
        (
            Biome.forest,
            Affinity.native,
        ),  # Sacred groves and natural woodland sanctuaries
        (
            Development.wilderness,
            Affinity.native,
        ),  # Untouched natural areas they protect
        (
            Biome.jungle,
            Affinity.common,
        ),  # Dense tropical forests with rich biodiversity
        (Development.frontier, Affinity.common),  # Edge settlements near wild areas
        (
            Development.countryside,
            Affinity.uncommon,
        ),  # Rural areas where nature and civilization meet
        (Biome.swamp, Affinity.uncommon),  # Wetland ecosystems they may guard
        (Development.ruin, Affinity.uncommon),  # Ancient sites reclaimed by nature
    ],
)
