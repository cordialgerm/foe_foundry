from foe_foundry.environs import Affinity, Development, region
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import ArcaneArmor
from ...attack_template import AttackTemplate, spell
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...powers import PowerSelection
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from ...spells import CasterType
from ...statblocks import MonsterDials
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

SimulacrumVariant = MonsterVariant(
    name="Simulacrum",
    description="Simulacrums are illusions created by powerful mages to serve as their agents. They are often used to scout, gather information, or perform tasks that the mage cannot do themselves.",
    monsters=[
        Monster(name="Simulacrum", cr=9),
    ],
)


class _SimulacrumTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        return PowerSelection(powers.LoadoutSimulacrum)

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
                Stats.STR.scaler(StatScaling.Default, mod=-6),
                Stats.DEX.scaler(StatScaling.Default, mod=2),
                Stats.INT.scaler(StatScaling.Primary),
                Stats.WIS.scaler(StatScaling.Medium),
                Stats.CHA.scaler(StatScaling.Default),
            ],
            hp_multiplier=0.6
            * settings.hp_multiplier,  # low HP for a CR 9 because we want to be at around 50% of the CR 12 archmage
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            size=Size.Medium,
            languages=["Common"],
            creature_class="Simulacrum",
            caster_type=CasterType.Arcane,
            # mages have many bonus actions, reactions, and limited use abilities
            selection_target_args=dict(
                limited_uses_target=-1,
                limited_uses_max=3 if cr <= 11 else 4,
                reaction_target=1,
                reaction_max=2,
                spellcasting_powers_target=-1,
                spellcasting_powers_max=-1,
                bonus_action_target=-1,
                bonus_action_max=2,
                recharge_target=1,
                recharge_max=1,
            ),
        ).with_types(
            primary_type=CreatureType.Humanoid, additional_types=CreatureType.Construct
        )

        # SPEED
        stats = stats.copy(speed=stats.speed.grant_flying())

        # ARMOR CLASS
        stats = stats.add_ac_template(ArcaneArmor)

        # ATTACKS
        # Boost attack damage to more closely match Archmage
        # don't boost overall damage because we don't want AOE abilities to be too over the top
        attack = spell.ArcaneBurst.copy(damage_scalar=1.1).with_display_name(
            "Reality Splinters"
        )

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Controller,
            additional_roles={MonsterRole.Artillery},
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(
            Skills.Arcana, Skills.Perception, Skills.History, Skills.Initiative
        )

        # IMMUNITIES
        stats = stats.grant_resistance_or_immunity(
            resistances={
                DamageType.Bludgeoning,
                DamageType.Piercing,
                DamageType.Slashing,
            },
            conditions={Condition.Exhaustion, Condition.Poisoned},
        )

        # SAVES
        stats = stats.grant_save_proficiency(Stats.WIS, Stats.INT)

        # DCs
        stats = stats.apply_monster_dials(
            dials=MonsterDials(difficulty_class_modifier=1)
        )  # need to boost DC to match Archmage

        return stats, [attack]


SimulacrumTemplate: MonsterTemplate = _SimulacrumTemplate(
    name="Simulacrum",
    tag_line="Wizard's Illusory Duplicate",
    description="Simulacrums are illusions created by powerful mages to serve as their agents. They are often used to scout, gather information, or perform tasks that the mage cannot do themselves.",
    treasure=["Arcana", "Individual"],
    variants=[SimulacrumVariant],
    species=[],
    environments=[
        (
            region.UrbanTownship,
            Affinity.native,
        ),  # City arcane academies and wizard colleges
        (
            Development.stronghold,
            Affinity.native,
        ),  # Fortified wizard towers and magical keeps
        (
            Development.urban,
            Affinity.common,
        ),  # Urban mage guilds and magical institutions
        (
            Development.settlement,
            Affinity.common,
        ),  # Town magical practitioners and their laboratories
        (
            Development.dungeon,
            Affinity.uncommon,
        ),  # Hidden magical sanctums and secret workshops
        (
            Development.ruin,
            Affinity.uncommon,
        ),  # Ancient magical sites and abandoned towers
        (
            Development.countryside,
            Affinity.rare,
        ),  # Remote hermitages and secluded studies
    ],
)
