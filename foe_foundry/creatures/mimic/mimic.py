from foe_foundry.environs import Affinity, Biome, Development
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import flat
from ...attack_template import AttackTemplate, natural
from ...creature_types import CreatureType
from ...damage import DamageType
from ...movement import Movement
from ...powers import PowerSelection, flags
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

MimicVariant = MonsterVariant(
    name="Mimic",
    description="Mimics disguise themselves as inanimate objects such as treasure chests, doors, or furniture to lure and ambush prey",
    monsters=[
        Monster(name="Mimic", cr=2, srd_creatures=["Mimic"]),
        Monster(
            name="Greater Mimic",
            cr=4,
            other_creatures={"Giant Mimic": "Waterdeep: Dragon Heist"},
        ),
        Monster(
            name="Vault Mimic",
            cr=8,
            other_creatures={"Hoard Mimic": "Fizzban's Treasury of Dragons"},
        ),
    ],
)


class _MimicTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "mimic":
            return PowerSelection(powers.LoadoutMimic)
        elif settings.monster_key == "greater-mimic":
            return PowerSelection(powers.LoadoutGreaterMimic)
        elif settings.monster_key == "vault-mimic":
            return PowerSelection(powers.LoadoutVaultMimic)
        else:
            raise ValueError(f"Unknown monster key: {settings.monster_key}")

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
            stats=[
                AbilityScore.STR.scaler(StatScaling.Primary, mod=1),
                AbilityScore.DEX.scaler(StatScaling.Default, mod=2),
                AbilityScore.INT.scaler(StatScaling.Default, mod=-5),
                AbilityScore.WIS.scaler(StatScaling.Medium, mod=2),
                AbilityScore.CHA.scaler(StatScaling.Default, mod=-2),
            ],
            hp_multiplier=1.25 * settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Monstrosity,
            creature_class="Mimic",
            senses=stats.senses.copy(darkvision=60),
        )

        # SIZE
        if cr >= 8:
            size = Size.Huge
        elif cr >= 4:
            size = Size.Large
        else:
            size = Size.Medium

        stats = stats.copy(size=size)

        # ARMOR CLASS
        stats = stats.add_ac_template(flat(12))

        # ATTACKS
        attack = natural.Slam.with_display_name("Sticky Pseudopod")
        stats = stats.copy(
            secondary_damage_type=DamageType.Acid,
        )

        # ROLES
        stats = stats.with_roles(primary_role=MonsterRole.Ambusher)

        # MOVEMENT
        stats = stats.with_flags(flags.NO_TELEPORT)
        stats = stats.copy(speed=Movement(walk=20, climb=20))

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(
            Skills.Stealth
        ).grant_proficiency_or_expertise(Skills.Stealth)  # expertise

        # SAVES
        if cr >= 4:
            stats = stats.grant_save_proficiency(AbilityScore.CON)
        if cr >= 8:
            stats = stats.grant_save_proficiency(AbilityScore.WIS)

        return stats, [attack]


MimicTemplate: MonsterTemplate = _MimicTemplate(
    name="Mimic",
    tag_line="Paranoia-Inducing Shapeshifting Ambusher",
    description="Mimics disguise themselves as inanimate objects such as treasure chests, doors, or furniture to lure and ambush prey",
    treasure=[],
    variants=[MimicVariant],
    species=[],
    environments=[
        (
            Development.dungeon,
            Affinity.native,
        ),  # Their primary domain - underground treasures and traps
        (
            Development.ruin,
            Affinity.native,
        ),  # Ancient ruins with forgotten treasures they mimic
        (
            Development.stronghold,
            Affinity.common,
        ),  # Castles and fortresses with valuables to copy
        (Biome.underground, Affinity.common),  # Cave systems and underground complexes
        (
            Development.settlement,
            Affinity.uncommon,
        ),  # Towns where they might infiltrate buildings
        (
            Development.urban,
            Affinity.uncommon,
        ),  # Cities with valuable objects and wealthy districts
        (
            Development.countryside,
            Affinity.rare,
        ),  # Rural areas with occasional treasures to mimic
        (Development.wilderness, Affinity.rare),  # Remote locations with hidden caches
    ],
)
