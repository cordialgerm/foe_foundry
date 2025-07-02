from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import NaturalArmor
from ...attack_template import AttackTemplate, natural
from ...creature_types import CreatureType
from ...movement import Movement
from ...powers import PowerSelection, flags
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

ManticoreVariant = MonsterVariant(
    name="Manticore",
    description="Medusas are prideful creatures that inhabit sites of fallen glory. They have hair of living snakes and an infamous petrifying gaze.",
    monsters=[
        Monster(name="Manticore", cr=3, srd_creatures=["Manticore"]),
        Monster(name="Manticore Ravager", cr=6),
    ],
)


class _ManticoreTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "manticore":
            return PowerSelection(powers.LoadoutManticore)
        elif settings.monster_key == "manticore-ravager":
            return PowerSelection(powers.LoadoutManticoreRavager)
        else:
            raise ValueError(f"Unknown monster key: {settings.monster_key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        rng = settings.rng

        # STATS
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=[
                Stats.STR.scaler(StatScaling.Primary),
                Stats.DEX.scaler(StatScaling.Medium, mod=3),
                Stats.CON.scaler(StatScaling.Constitution, mod=2),
                Stats.INT.scaler(StatScaling.Default, mod=-5),
                Stats.WIS.scaler(StatScaling.Medium, mod=-2),
                Stats.CHA.scaler(StatScaling.Default, mod=-4),
            ],
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Monstrosity,
            size=Size.Large,
            creature_class="Manticore",
            languages=["Common"],
            senses=stats.senses.copy(darkvision=60),
        )

        # ARMOR CLASS
        stats = stats.add_ac_template(NaturalArmor, ac_modifier=-1)

        # ATTACKS
        attack = natural.Claw.with_display_name("Cruel Claws")

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Artillery,
            additional_roles={
                MonsterRole.Skirmisher,
            },
        )

        # MOVEMENT
        stats = stats.with_flags(flags.NO_TELEPORT).copy(
            speed=Movement(walk=30, fly=50)
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(Skills.Intimidation)

        # SAVES
        if stats.cr >= 6:
            stats = stats.grant_save_proficiency(Stats.WIS)

        return stats, [attack]


ManticoreTemplate: MonsterTemplate = _ManticoreTemplate(
    name="Manticore",
    tag_line="Flying hunters with spiked tails and sharper tongues",
    description="Manticores are bizarre amalgamations with the body of a lion, dragon-like wings, a bristling tail of barbed spines, and the leering face of a voracious human. They are known for their cruel appetites and even crueler wit.",
    environments=["Arctic", "Coasta", "Grassland", "Hill", "Mountain"],
    treasure=[],
    variants=[ManticoreVariant],
    species=[],
)
