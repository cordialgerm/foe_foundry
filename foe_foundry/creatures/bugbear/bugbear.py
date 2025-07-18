from foe_foundry.environs import Affinity, Biome, Development, region
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import HideArmor
from ...attack_template import AttackTemplate, natural
from ...creature_types import CreatureType
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

BugbearVariant = MonsterVariant(
    name="Bugbear",
    description="Bugbears are large, hairy humanoids with a reputation for stealth and ambush tactics. They are often found in dark forests or caves, where they can use their natural camouflage to surprise their prey.",
    monsters=[
        Monster(
            name="Bugbear",
            cr=1,
            srd_creatures=["Bugbear"],
        ),
        Monster(
            name="Bugbear Brute",
            cr=3,
            other_creatures={"Bugbear Stalker": "mm25"},
        ),
        Monster(
            name="Bugbear Shadowstalker",
            cr=5,
        ),
    ],
)


class _BugbearTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "bugbear":
            return PowerSelection(powers.LoadoutBugbear)
        elif settings.monster_key == "bugbear-brute":
            return PowerSelection(powers.LoadoutBugbearBrute)
        elif settings.monster_key == "bugbear-shadowstalker":
            return PowerSelection(powers.LoadoutBugbearShadowstalker)
        else:
            raise ValueError(f"Unknown bugbear variant: {settings.monster_key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        variant = settings.variant

        # STATS
        attrs = {
            AbilityScore.STR: (StatScaling.Primary, 0.5),
            AbilityScore.DEX: (StatScaling.Medium, 3),
            AbilityScore.INT: (StatScaling.Medium, -4),
            AbilityScore.WIS: (StatScaling.Default, 2),
            AbilityScore.CHA: (StatScaling.Medium, -3),
        }

        stats = base_stats(
            name=variant.name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=attrs,
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            name=name,
            size=Size.Medium,
            languages=["Common", "Goblin"],
            creature_class="Bugbear",
            creature_subtype="Goblinoid",
        ).with_types(
            primary_type=CreatureType.Humanoid, additional_types=CreatureType.Fey
        )

        # SENSES
        stats = stats.copy(senses=stats.senses.copy(darkvision=60))

        # ARMOR CLASS
        stats = stats.add_ac_template(HideArmor)

        # ATTACKS
        attack = natural.Slam.with_display_name("Skull Smash").copy(reach=10)

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Ambusher, additional_roles=MonsterRole.Bruiser
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(
            Skills.Stealth
        ).grant_proficiency_or_expertise(Skills.Stealth)

        # SAVES
        if cr >= 3:
            stats = stats.grant_save_proficiency(AbilityScore.CON, AbilityScore.WIS)

        return stats, [attack]


BugbearTemplate: MonsterTemplate = _BugbearTemplate(
    name="Bugbear",
    tag_line="Lurking abductors and ambushers",
    description="Bugbears are large, hairy humanoids with a reputation for stealth and ambush tactics. They are often found in dark forests or caves, where they can use their natural camouflage to surprise their prey.",
    treasure=["Any"],
    environments=[
        (region.TangledForest, Affinity.native),  # native to dark, dense forests
        (Biome.underground, Affinity.native),  # found in caves and underground lairs
        (Development.wilderness, Affinity.common),  # common in wild, undeveloped areas
        (Development.ruin, Affinity.common),  # use ruins as ambush sites and lairs
        (Development.frontier, Affinity.common),  # ambush settlers and travelers
        (region.Feywood, Affinity.uncommon),  # occasionally found in magical forests
        (Development.countryside, Affinity.uncommon),  # raid rural areas
        (Development.settlement, Affinity.rare),  # avoid populated areas
    ],
    variants=[BugbearVariant],
    species=[],
    is_sentient_species=True,
)
