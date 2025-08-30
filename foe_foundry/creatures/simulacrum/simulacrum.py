from foe_foundry.environs import Affinity, Development, region
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import ArcaneArmor, StuddedLeatherArmor
from ...attack_template import AttackTemplate, spell, weapon
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...powers import PowerSelection
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
from . import powers

SimulacrumVariant = MonsterVariant(
    name="Simulacrum",
    description="Simulacrums are illusions created by powerful mages to serve as their agents. They are often used to scout, gather information, or perform tasks that the mage cannot do themselves.",
    monsters=[
        Monster(name="Simulacrum", cr=9),
        Monster(name="Mastercraft Simulacrum", cr=12),
    ],
)

SimulacrumWarriorVariant = MonsterVariant(
    name="Simulacrum Mirrorblade",
    description="Simulacrum Mirrorblades are illusory duplicates of warriors created by powerful mages to serve as their agents. They are often used to scout, gather information, or perform tasks that the mage cannot do themselves.",
    monsters=[
        Monster(name="Simulacrum Mirrorblade", cr=7),
    ],
)


class _SimulacrumTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "simulacrum-mirrorblade":
            return PowerSelection(powers.LoadoutMirrorbladeSimulacrum)
        else:
            return PowerSelection(powers.LoadoutSimulacrum)

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr

        if settings.monster_key == "simulacrum-mirrorblade":
            attrs = {
                AbilityScore.STR: (StatScaling.Default, -6),
                AbilityScore.DEX: StatScaling.Primary,
                AbilityScore.INT: (StatScaling.Default, -1),
                AbilityScore.WIS: StatScaling.Medium,
                AbilityScore.CHA: StatScaling.Default,
            }
        else:
            attrs = {
                AbilityScore.STR: (StatScaling.Default, -6),
                AbilityScore.DEX: (StatScaling.Default, 2),
                AbilityScore.INT: StatScaling.Primary,
                AbilityScore.WIS: StatScaling.Medium,
                AbilityScore.CHA: StatScaling.Default,
            }

        # STATS
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=attrs,
            hp_multiplier=0.6
            * settings.hp_multiplier,  # low HP for a CR 9 because we want to be at around 50% of the CR 12 archmage
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            size=Size.Medium,
            languages=["Common"],
            creature_class="Simulacrum",
        ).with_types(
            primary_type=CreatureType.Humanoid, additional_types=CreatureType.Construct
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

        if settings.monster_key == "simulacrum-mirrorblade":
            # SPEED
            stats = stats.copy(speed=stats.speed.delta(10))

            # ARMOR CLASS
            stats = stats.add_ac_template(StuddedLeatherArmor)

            # ATTACKS
            # Boost attack damage to more closely match Archmage
            # don't boost overall damage because we don't want AOE abilities to be too over the top
            attack = weapon.Daggers.copy(
                damage_scalar=1.1, secondary_damage_type=DamageType.Force
            ).with_display_name("Reality-Shred Blades")

            # ROLES
            stats = stats.with_roles(
                primary_role=MonsterRole.Skirmisher,
                additional_roles={MonsterRole.Soldier},
            )

            # SKILLS
            stats = stats.grant_proficiency_or_expertise(
                Skills.Stealth, Skills.Athletics, Skills.Acrobatics
            )

            # SAVES
            stats = stats.grant_save_proficiency(AbilityScore.DEX, AbilityScore.WIS)

        else:
            # SPEED
            stats = stats.copy(speed=stats.speed.grant_flying())

            # ARMOR CLASS
            stats = stats.add_ac_template(ArcaneArmor)

            stats = stats.grant_spellcasting(
                caster_type=CasterType.Arcane,
            )

            # ATTACKS
            # Boost attack damage to more closely match Archmage
            # don't boost overall damage because we don't want AOE abilities to be too over the top
            attack = spell.ArcaneBurst.copy(damage_scalar=1.1).with_display_name(
                "Reality Splinters"
            )

            # ROLES
            stats = stats.with_roles(
                primary_role=MonsterRole.Skirmisher,
                additional_roles={MonsterRole.Artillery},
            )

            # SKILLS
            stats = stats.grant_proficiency_or_expertise(
                Skills.Arcana, Skills.Perception, Skills.History, Skills.Initiative
            )

            # SAVES
            stats = stats.grant_save_proficiency(AbilityScore.WIS, AbilityScore.INT)

            # DCs
            # need to boost DC to match Archmage
            stats = stats.copy(difficulty_class_modifier=1)

        return stats, [attack]


SimulacrumTemplate: MonsterTemplate = _SimulacrumTemplate(
    name="Simulacrum",
    tag_line="Wizard's Illusory Duplicate",
    description="Simulacrums are illusions created by powerful mages to serve as their agents. They are often used to scout, gather information, or perform tasks that the mage cannot do themselves.",
    treasure=["Arcana", "Individual"],
    variants=[SimulacrumVariant, SimulacrumWarriorVariant],
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
