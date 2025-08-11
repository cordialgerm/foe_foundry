from foe_foundry.environs import Affinity, Biome, Development, region
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import NaturalArmor
from ...attack_template import AttackTemplate, natural
from ...creature_types import CreatureType
from ...movement import Movement
from ...powers import (
    PowerSelection,
    flags,
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

OwlbearVariant = MonsterVariant(
    name="Owlbear",
    description="Owlbears are ferocious hybrid creatures, combining the strength and frame of a bear with the sharp beak and keen senses of an owl. They are known for their territorial nature and relentless aggression.",
    monsters=[
        Monster(name="Owlbear", cr=3, srd_creatures=["Owlbear"]),
        Monster(
            name="Savage Owlbear", cr=7, other_creatures={"Primeval Owlbear": "mm24"}
        ),
        Monster(name="Owlbear Cub", cr=1 / 2),
    ],
)


class _OwlbearTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "owlbear-cub":
            return PowerSelection(powers.LoadoutOwlbearCub)
        elif settings.monster_key == "owlbear":
            return PowerSelection(powers.LoadoutOwlbear)
        elif settings.monster_key == "savage-owlbear":
            return PowerSelection(powers.LoadoutSavageOwlbear)
        else:
            raise ValueError(f"Unknown monster key: {settings.monster_key}. ")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr

        hp_multiplier = 0.95
        damage_multiplier = 1.0 if cr >= 6 else 1.15

        # STATS
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats={
                AbilityScore.STR: (StatScaling.Primary, 4 if cr >= 6 else 2),
                AbilityScore.DEX: (StatScaling.Medium, 0.5),
                AbilityScore.CON: (StatScaling.Constitution, 4 if cr >= 6 else 2),
                AbilityScore.INT: (StatScaling.NoScaling, -2 if cr >= 6 else -7),
                AbilityScore.WIS: (StatScaling.Medium, 2 if cr >= 6 else 0.5),
                AbilityScore.CHA: (StatScaling.Default, -3),
            },
            hp_multiplier=hp_multiplier * settings.hp_multiplier,
            damage_multiplier=damage_multiplier * settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Monstrosity,
            size=Size.Large,
            creature_class="Owlbear",
            senses=stats.senses.copy(darkvision=60),
        )

        # ARMOR CLASS
        stats = stats.add_ac_template(NaturalArmor, ac_modifier=0 if cr >= 6 else -1)

        # ATTACKS
        attack = natural.Claw.with_display_name("Vicious Rend")

        # ROLES
        stats = stats.with_roles(primary_role=MonsterRole.Bruiser)

        # MOVEMENT
        stats = stats.with_flags(flags.NO_TELEPORT).copy(
            speed=Movement(walk=40, climb=40)
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(
            Skills.Perception
        ).grant_proficiency_or_expertise(Skills.Perception)

        if cr >= 6:
            stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

        # SAVES
        if cr >= 6:
            stats = stats.grant_save_proficiency(AbilityScore.WIS, AbilityScore.CON)

        return stats, [attack]


OwlbearTemplate: MonsterTemplate = _OwlbearTemplate(
    name="Owlbear",
    tag_line="Unnaturally Territorial Predators",
    description="An Owlbear is a fearsome hybrid creature, combining the powerful frame of a bear with the hooked beak, feathers, and piercing eyes of a giant owl.",
    environments=[
        (region.TangledForest, Affinity.native),  # native to dense forests
        (Development.wilderness, Affinity.common),  # Common in wild areas
        (region.LoftyMountains, Affinity.uncommon),  # Could nest in rocky mountains
        (region.CountryShire, Affinity.rare),  # could encroach on farmland
        (Development.frontier, Affinity.uncommon),  # Found in less developed areas
        (Biome.forest, Affinity.native),  # Native to forests
        (Biome.jungle, Affinity.common),  # Uncommon in dense jungles
    ],
    treasure=[],
    variants=[OwlbearVariant],
    species=[],
)
