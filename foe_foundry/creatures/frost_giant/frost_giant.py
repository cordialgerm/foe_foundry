from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import PatchworkArmor
from ...attack_template import AttackTemplate, spell, weapon
from ...creature_types import CreatureType
from ...damage import DamageType
from ...environs import Affinity, Biome, region
from ...movement import Movement
from ...powers import PowerSelection
from ...role_types import MonsterRole
from ...size import Size
from ...skills import AbilityScore, Skills, StatScaling
from .._template import GenerationSettings, Monster, MonsterTemplate, MonsterVariant
from ..base_stats import base_stats
from . import powers

FrostGiantVariant = MonsterVariant(
    name="Frost Giant",
    description="Frost giants are towering, cold-hearted warriors from the frozen wastes.",
    monsters=[
        Monster(
            name="Frost Giant Reaver",
            cr=8,
            srd_creatures=["Frost Giant"],
        ),
        Monster(
            name="Frost Giant Challenger",
            cr=10,
        ),
        Monster(
            name="Frost Giant Rimepriest",
            cr=12,
        ),
        Monster(
            name="Frost Giant Thane",
            cr=16,
            is_legendary=True,
        ),
    ],
)


class _FrostGiantTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "frost-giant-reaver":
            return PowerSelection(powers.LoadoutFrostGiant)
        elif settings.monster_key == "frost-giant-challenger":
            return PowerSelection(powers.LoadoutChallenger)
        elif settings.monster_key == "frost-giant-rimepriest":
            return PowerSelection(powers.LoadoutShaman)
        elif settings.monster_key == "frost-giant-thane":
            return PowerSelection(powers.LoadoutThane)
        else:
            raise ValueError(f"Unknown monster key: {settings.monster_key}. ")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr

        # Special stat scaling for Rimepriest
        if settings.monster_key == "frost-giant-rimepriest":
            attrs = {
                AbilityScore.STR: (StatScaling.Default, 4),  # good STR
                AbilityScore.DEX: (StatScaling.Default, -3),
                AbilityScore.CON: (StatScaling.Constitution, 4),  # really good CON
                AbilityScore.INT: (StatScaling.Default, 0),
                AbilityScore.WIS: (StatScaling.Primary),  # primary WIS
                AbilityScore.CHA: (StatScaling.Default, 2),
            }
        else:
            attrs = {
                AbilityScore.STR: (StatScaling.Primary, 3),
                AbilityScore.DEX: (StatScaling.Default, -3),
                AbilityScore.CON: (StatScaling.Constitution, 4),  # really good CON
                AbilityScore.INT: (StatScaling.Default, -3),
                AbilityScore.WIS: (StatScaling.Default, -2),
                AbilityScore.CHA: (StatScaling.Default, 2),
            }

        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=attrs,  # type: ignore
            hp_multiplier=settings.hp_multiplier * 1.15,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Giant,
            size=Size.Huge,
            languages=["Common", "Giant"],
            creature_class="Frost Giant",
            speed=Movement(walk=40),
            damage_immunities={DamageType.Cold},
        )

        # AC
        stats = stats.add_ac_template(PatchworkArmor)

        # ROLES
        stats = stats.with_roles(primary_role=MonsterRole.Bruiser)

        # SAVES
        stats = stats.grant_save_proficiency(
            AbilityScore.STR, AbilityScore.CON, AbilityScore.WIS, AbilityScore.CHA
        )

        # SKILLS
        if settings.monster_key == "frost-giant-rimepriest":
            stats = stats.grant_proficiency_or_expertise(
                Skills.Insight, Skills.Perception, Skills.Initiative
            )
        else:
            stats = stats.grant_proficiency_or_expertise(
                Skills.Athletics, Skills.Perception, Skills.Survival, Skills.Initiative
            )

        # ATTACKS

        # Giants typically have fewer, powerful attacks
        stats = stats.with_set_attacks(2)

        if settings.monster_key == "frost-giant-rimepriest":
            attack = spell.Frostbolt.with_display_name("Arctic Blast")
        else:
            attack = weapon.Greataxe.with_display_name("Biting Greataxe").copy(
                reach=10, secondary_damage_type=DamageType.Cold
            )

        return stats, [attack]


FrostGiantTemplate: MonsterTemplate = _FrostGiantTemplate(
    name="Frost Giant",
    tag_line="Towering warriors of the frozen wastes",
    description="Frost giants are massive, cold-hearted warriors who thrive in icy realms.",
    variants=[FrostGiantVariant],
    treasure=[],
    species=[],
    environments=[
        (region.FrozenWastes, Affinity.native),
        (region.LoftyMountains, Affinity.common),  # Icy mountain ranges
        (Biome.arctic, Affinity.native),  # Frozen tundras and ice fields
        (region.RestlessSea, Affinity.uncommon),  # Underwater Frost Giants
    ],
)
