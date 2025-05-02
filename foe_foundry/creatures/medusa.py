from ..ac_templates import NaturalArmor
from ..attack_template import natural, spell
from ..creature_types import CreatureType
from ..damage import DamageType
from ..powers import (
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    flags,
    select_powers,
)
from ..powers.roles import ambusher, artillery, controller, skirmisher
from ..powers.themed import (
    cursed,
    petrifying,
    poison,
    serpentine,
    technique,
)
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..statblocks import BaseStatblock
from .base_stats import base_stats
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

MedusaVariant = CreatureVariant(
    name="Medusa",
    description="Medusas are prideful creatures that inhabit sites of fallen glory. They have hair of living snakes and an infamous petrifying gaze.",
    suggested_crs=[
        SuggestedCr(name="Medusa", cr=6, srd_creatures=["Medusa"]),
        SuggestedCr(name="Medusa Queen", cr=10, is_legendary=True),
    ],
)


class _MedusaWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, is_legendary: bool):
        self.stats = stats
        self.is_legendary = is_legendary

    def force_powers(self) -> list[Power]:
        if self.is_legendary:
            return [
                petrifying.PetrifyingGaze
            ]  # no need for  nimble escape because of legendary actions
        else:
            return [petrifying.PetrifyingGaze, skirmisher.NimbleEscape]

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        powers = [
            technique.PoisonedAttack,
            technique.WeakeningAttack,
            technique.SlowingAttack,
            serpentine.SerpentineHiss,
            serpentine.InterruptingHiss,
            skirmisher.HarassingRetreat,
            ambusher.StealthySneak,
            poison.ToxicPoison,
            poison.WeakeningPoison,
            poison.PoisonousBlood,
            poison.VenemousMiasma,
            artillery.IndirectFire,
        ]

        tier2_powers = [
            artillery.FocusShot,
            artillery.Overwatch,
            artillery.SuppresingFire,
            controller.Eyebite,
            controller.TongueTwister,
            cursed.DisfiguringCurse,
            cursed.RejectDivinity,
        ]

        if p in powers:
            return CustomPowerWeight(2, ignore_usual_requirements=True)
        elif p in tier2_powers:
            # ironically we want to boost these powers more because their default weights are low
            return CustomPowerWeight(2.5, ignore_usual_requirements=True)
        else:
            # Medusa as a Monstrosity ends up getting a bunch of weird default powers
            # Just use the ones assigned above
            return CustomPowerWeight(0, ignore_usual_requirements=False)


def generate_medusa(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    is_legendary = settings.is_legendary
    rng = settings.rng

    # STATS
    stats = base_stats(
        name=name,
        variant_key=settings.variant.key,
        template_key=settings.creature_template,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Default, mod=-2),
            Stats.DEX.scaler(StatScaling.Primary),
            Stats.INT.scaler(StatScaling.Default),
            Stats.WIS.scaler(StatScaling.Default, mod=1),
            Stats.CHA.scaler(StatScaling.Medium, mod=2),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Monstrosity,
        size=Size.Medium,
        creature_class="Medusa",
        senses=stats.senses.copy(darkvision=150),
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    # ARMOR CLASS
    stats = stats.add_ac_template(NaturalArmor)

    # ATTACKS
    attack = spell.Poisonbolt.with_display_name("Poison Ray")
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=DamageType.Poison,
    )

    secondary_attack = natural.Bite.with_display_name("Snake Hair")
    stats = secondary_attack.add_as_secondary_attack(stats)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Skirmisher,
        additional_roles={
            MonsterRole.Ambusher,
            MonsterRole.Controller,
            MonsterRole.Artillery,
        },
    )

    # MOVEMENT
    stats = stats.with_flags(flags.NO_TELEPORT)

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(
        Skills.Initiative, Skills.Deception, Skills.Perception, Skills.Stealth
    )

    # SAVES
    stats = stats.grant_save_proficiency(Stats.WIS)

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_MedusaWeights(stats, is_legendary),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    stats = secondary_attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


MedusaTemplate: CreatureTemplate = CreatureTemplate(
    name="Medusa",
    tag_line="Snake-haired recluse with a petrifying gaze",
    description="Medusas are prideful creatures that inhabit sites of fallen glory. They have hair of living snakes and an infamous petrifying gaze.",
    environments=["Desert", "Dungeon"],
    treasure=[],
    variants=[MedusaVariant],
    species=[],
    callback=generate_medusa,
)
