from ...ac_templates import ArcaneArmor
from ...attack_template import spell
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...powers import PowerSelection, select_powers
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from ...spells import CasterType
from ...statblocks import MonsterDials
from .._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
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


def choose_powers(settings: GenerationSettings) -> PowerSelection:
    return PowerSelection(powers.LoadoutSimulacrum)


def generate_simulacrum(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    rng = settings.rng

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

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Controller, additional_roles={MonsterRole.Artillery}
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(
        Skills.Arcana, Skills.Perception, Skills.History, Skills.Initiative
    )

    # IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        resistances={DamageType.Bludgeoning, DamageType.Piercing, DamageType.Slashing},
        conditions={Condition.Exhaustion, Condition.Poisoned},
    )

    # SAVES
    stats = stats.grant_save_proficiency(Stats.WIS, Stats.INT)

    # POWERS
    features = []

    # DCs
    stats = stats.apply_monster_dials(
        dials=MonsterDials(difficulty_class_modifier=1)
    )  # need to boost DC to match Archmage

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=choose_powers(settings),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


SimulacrumTemplate: MonsterTemplate = MonsterTemplate(
    name="Simulacrum",
    tag_line="Wizard's Illusory Duplicate",
    description="Simulacrums are illusions created by powerful mages to serve as their agents. They are often used to scout, gather information, or perform tasks that the mage cannot do themselves.",
    environments=[],
    treasure=["Arcana", "Individual"],
    variants=[SimulacrumVariant],
    species=[],
    callback=generate_simulacrum,
)
