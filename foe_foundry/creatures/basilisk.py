import numpy as np

from ..ac_templates import NaturalPlating
from ..attack_template import natural
from ..creature_types import CreatureType
from ..damage import DamageType
from ..powers import (
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    select_powers,
)
from ..powers.creature import basilisk
from ..powers.creature_type import beast
from ..powers.roles import controller
from ..powers.spellcaster import SpellcasterPowers
from ..powers.themed import (
    anti_ranged,
    bestial,
    breath,
    diseased,
    flying,
    monstrous,
    petrifying,
    poison,
    reckless,
    serpentine,
    technique,
    tough,
)
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Stats, StatScaling
from ..statblocks import BaseStatblock
from .base_stats import base_stats
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

BasiliskVariant = CreatureVariant(
    name="Basilisk",
    description="Basilisks are large, reptilian creatures with the ability to turn flesh to stone with their gaze. They are often found in rocky areas and caves, where they use their petrifying gaze to protect their territory.",
    suggested_crs=[
        SuggestedCr(name="Basilisk", cr=3, srd_creatures=["Basilisk"]),
        SuggestedCr(name="Basilisk Broodmother", cr=8),
    ],
)


class _BasiliskWeights(CustomPowerSelection):
    def __init__(
        self, stats: BaseStatblock, variant: CreatureVariant, rng: np.random.Generator
    ):
        self.stats = stats
        self.variant = variant
        self.rng = rng

        petrifying_powers = petrifying.PetrifyingPowers
        index = rng.choice(len(petrifying_powers))
        self.petrifying_power = petrifying_powers[index]

    def force_powers(self) -> list[Power]:
        force = [self.petrifying_power]
        if self.stats.cr >= 8:
            force += [basilisk.BasiliskBrood]

        return force

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        powers = [
            basilisk.StoneMolt,
            basilisk.StoneEater,
            anti_ranged.AdaptiveCamouflage,
            bestial.RetributiveStrike,
            beast.WildInstinct,
            beast.FeedingFrenzy,
            bestial.BurrowingAmbush,
            beast.BestialRampage,
            monstrous.Rampage,
            monstrous.TearApart,
            monstrous.JawClamp,
            monstrous.Frenzy,
            poison.PoisonousBlood,
            reckless.Charger,
            tough.MagicResistance,
            tough.LimitedMagicImmunity,
            breath.PoisonBreath,
            breath.NerveGasBreath,
            technique.BleedingAttack,
            technique.ProneAttack,
            technique.PoisonedAttack,
            serpentine.SerpentineHiss,
        ]

        suppress = (
            flying.FlyingPowers
            + SpellcasterPowers
            + controller.ControllingSpells
            + diseased.DiseasedPowers
        )

        if p in suppress or p in petrifying.PetrifyingPowers:
            return CustomPowerWeight(0, ignore_usual_requirements=True)
        elif p in powers:
            return CustomPowerWeight(2, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(0.25, ignore_usual_requirements=False)


def generate_basilisk(settings: GenerationSettings) -> StatsBeingGenerated:
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
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Default, mod=-2),
            Stats.INT.scaler(StatScaling.Default, mod=-6),
            Stats.WIS.scaler(StatScaling.Medium, mod=-4),
            Stats.CHA.scaler(StatScaling.Default, mod=-3),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Monstrosity,
        size=Size.Medium,
        creature_class="Basilisk",
        senses=stats.senses.copy(darkvision=60),
    )

    # ARMOR CLASS
    stats = stats.add_ac_template(NaturalPlating)

    # ATTACKS
    attack = natural.Bite.with_display_name("Venomous Bite")
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=DamageType.Poison,
    )
    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Bruiser, additional_roles=MonsterRole.Controller
    )

    # SAVES
    if cr >= 8:
        stats = stats.grant_save_proficiency(Stats.CON, Stats.STR, Stats.WIS)

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_BasiliskWeights(stats, variant, rng),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


BasiliskTemplate: CreatureTemplate = CreatureTemplate(
    name="Basilisk",
    tag_line="Reptilian guardian with a petrifying gaze",
    description="Basilisks are large, reptilian creatures with the ability to turn flesh to stone with their gaze. They are often found in rocky areas and caves, where they use their petrifying gaze to protect their territory.",
    environments=["Mountain", "Underdark"],
    treasure=[],
    variants=[BasiliskVariant],
    species=[],
    callback=generate_basilisk,
)
