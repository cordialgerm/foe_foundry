from foe_foundry.environs import Affinity, Biome, Development, Terrain
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import NaturalPlating
from ...attack_template import AttackTemplate, natural
from ...creature_types import CreatureType
from ...damage import Condition
from ...powers import (
    MEDIUM_POWER,
    PowerSelection,
)
from ...role_types import MonsterRole
from ...size import Size
from ...skills import AbilityScore, Skills, StatScaling
from ...statblocks import MonsterDials
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

GorgonVariant = MonsterVariant(
    name="Gorgon",
    description="Gorgon are iron bulls that exhale a toxic petrifying breath",
    monsters=[
        Monster(name="Gorgon", cr=5, srd_creatures=["Gorgon"]),
    ],
)


class _GorgonTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "gorgon":
            return PowerSelection(powers.LoadoutGorgon)
        else:
            raise ValueError(f"Unknown monster key: {settings.monster_key}. ")

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
                AbilityScore.STR.scaler(StatScaling.Primary, mod=2),
                AbilityScore.DEX.scaler(StatScaling.Default, mod=-1),
                AbilityScore.CON.scaler(StatScaling.Constitution, mod=4),
                AbilityScore.INT.scaler(StatScaling.Default, mod=-9),
                AbilityScore.WIS.scaler(StatScaling.Default, mod=1),
                AbilityScore.CHA.scaler(StatScaling.Default, mod=-5),
            ],
            hp_multiplier=1.2 * settings.hp_multiplier,
            damage_multiplier=0.95 * settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Construct,
            size=Size.Large,
            creature_class="Gorgon",
            senses=stats.senses.copy(darkvision=60),
        )

        # SPEED
        stats = stats.copy(speed=stats.speed.delta(10))

        # ARMOR CLASS
        stats = stats.add_ac_template(NaturalPlating, ac_modifier=2)

        # ATTACKS
        attack = natural.Stomp.with_display_name("Iron Hooves")

        # fewer, more powerful attacks
        stats = stats.with_set_attacks(2)

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Bruiser,
            additional_roles={
                MonsterRole.Defender,
            },
        )

        # IMMUNITIES
        stats = stats.grant_resistance_or_immunity(
            conditions={Condition.Exhaustion, Condition.Petrified}
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(
            Skills.Perception
        ).grant_proficiency_or_expertise(Skills.Perception)  # expertise

        # ADDITIONAL POWERS

        stats = stats.apply_monster_dials(
            dials=MonsterDials(recommended_powers_modifier=MEDIUM_POWER)
        )

        return stats, [attack]


GorgonTemplate: MonsterTemplate = _GorgonTemplate(
    name="Gorgon",
    tag_line="Bull-Like Constructs with Petrifying Breath",
    description="Gorgons are ferocious bull-like constructs with with iron plates and a toxic, petrifying breath",
    treasure=[],
    variants=[GorgonVariant],
    species=[],
    environments=[
        (
            Terrain.mountain,
            Affinity.native,
        ),  # Remote mountain valleys where they guard territory
        (
            Biome.forest,
            Affinity.common,
        ),  # Dense forests providing cover for these territorial beasts
        (
            Development.wilderness,
            Affinity.common,
        ),  # Untamed lands far from civilization
        (Terrain.hill, Affinity.uncommon),  # Elevated terrain they may roam
        (
            Development.ruin,
            Affinity.uncommon,
        ),  # Ancient sites they might claim as territory
    ],
)
