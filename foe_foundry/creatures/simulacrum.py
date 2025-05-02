from ..ac_templates import ArcaneArmor
from ..attack_template import spell
from ..creature_types import CreatureType
from ..damage import Condition, DamageType
from ..powers import (
    LOW_POWER,
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    select_powers,
)
from ..powers.creature import simulacrum
from ..powers.creature.mage import (
    ProtectiveMagic,
)
from ..powers.roles import artillery, controller
from ..powers.spellcaster import magic, metamagic
from ..powers.themed import (
    anti_ranged,
    emanation,
    gadget,
    icy,
    illusory,
    technique,
    teleportation,
    tough,
)
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..spells import CasterType
from ..statblocks import BaseStatblock, MonsterDials
from .base_stats import base_stats
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

SimulacrumVariant = CreatureVariant(
    name="Simulacrum",
    description="Simulacrums are illusions created by powerful mages to serve as their agents. They are often used to scout, gather information, or perform tasks that the mage cannot do themselves.",
    suggested_crs=[
        SuggestedCr(name="Simulacrum", cr=9),
    ],
)


class _SimulacrumWeights(CustomPowerSelection):
    def __init__(
        self, stats: BaseStatblock, name: str, cr: float, variant: CreatureVariant
    ):
        self.stats = stats
        self.variant = variant

        force = [
            teleportation.MistyStep,
            tough.MagicResistance,
            ProtectiveMagic,
            simulacrum.SimulacrumSpellcasting,
        ]

        powers = [
            technique.FreezingAttack,
            technique.SlowingAttack,
            metamagic.ArcaneMastery,
            anti_ranged.Overchannel,
            artillery.TwinSpell,
            artillery.SuppresingFire,
            emanation.IllusoryReality,
            emanation.RunicWards,
            teleportation.BendSpace,
            teleportation.Scatter,
            emanation.TimeRift,
            emanation.SummonersRift,
            emanation.HypnoticLure,
            emanation.RecombinationMatrix,
            emanation.BitingFrost,
        ] + icy.IcyPowers

        # the Controlling spells don't really fit with the themes of the mages
        # supress indirect fire because it comes up so much and we want variety
        # suppress Magic Powers because these mages already have spell lists
        ignore = (
            controller.ControllingSpells
            + [
                illusory.HypnoticPatern,
                artillery.IndirectFire,
                gadget.PotionOfHealing,
            ]
            + magic.MagicPowers
        )

        self.force = force
        self.powers = powers
        self.ignore = ignore

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        if p in self.force or p in self.ignore:
            return CustomPowerWeight(-1, ignore_usual_requirements=False)
        elif p in self.powers:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(0.5, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        return self.force

    def power_delta(self) -> float:
        return -1 * LOW_POWER


def generate_simulacrum(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    rng = settings.rng

    # STATS
    stats = base_stats(
        name=name,
        variant_key=settings.variant.key,
        template_key=settings.creature_template,
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
        custom=_SimulacrumWeights(stats, name, cr, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


SimulacrumTemplate: CreatureTemplate = CreatureTemplate(
    name="Simulacrum",
    tag_line="Wizard's Illusory Duplicate",
    description="Simulacrums are illusions created by powerful mages to serve as their agents. They are often used to scout, gather information, or perform tasks that the mage cannot do themselves.",
    environments=[],
    treasure=["Arcana", "Individual"],
    variants=[SimulacrumVariant],
    species=[],
    callback=generate_simulacrum,
)
