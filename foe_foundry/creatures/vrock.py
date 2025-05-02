from ..ac_templates import UnholyArmor
from ..attack_template import natural
from ..creature_types import CreatureType
from ..damage import Condition, DamageType
from ..movement import Movement
from ..powers import CustomPowerSelection, CustomPowerWeight, Power, select_powers
from ..powers.creature import vrock
from ..powers.creature_type import demon
from ..powers.roles import bruiser, skirmisher
from ..powers.themed import (
    bestial,
    cruel,
    diseased,
    fearsome,
    flying,
    monstrous,
    poison,
    tough,
)
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Stats, StatScaling
from .base_stats import BaseStatblock, base_stats
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

VrockVariant = CreatureVariant(
    name="Vrock",
    description="Vrocks are screeching vulture-like harbringers of chaos and destruction that carry disease and pestilance from the lower planes.",
    suggested_crs=[
        SuggestedCr(name="Vrock", cr=6, srd_creatures=["Vrock"]),
    ],
)


class _VrockWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock):
        self.stats = stats

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        poison_powers = poison.PoisonPowers.copy()
        poison_powers.remove(poison.PoisonDart)
        disease_powers = diseased.DiseasedPowers

        powers = poison_powers + disease_powers

        secondary_powers = [
            monstrous.Frenzy,
            monstrous.Rampage,
            monstrous.LingeringWound,
            monstrous.TearApart,
            bestial.RetributiveStrike,
            cruel.BloodiedFrenzy,
            cruel.BrutalCritical,
            flying.Flyby,
            fearsome.NightmarishVisions,
            bruiser.Rend,
            skirmisher.HarassingRetreat,
        ]

        if p in powers:
            return CustomPowerWeight(3.0, ignore_usual_requirements=True)
        elif p in secondary_powers:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)
        elif p in demon.DemonPowers:
            return CustomPowerWeight(2.0, ignore_usual_requirements=False)
        else:
            return CustomPowerWeight(0.25, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        return [tough.MagicResistance, vrock.StunningScreech]


def generate_vrock(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    rng = settings.rng

    # STATS
    stats = base_stats(
        name=name,
        variant_key=settings.variant.key,
        template_key=settings.creature_template,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Medium, mod=2),
            Stats.CON.scaler(StatScaling.Constitution, mod=4),
            Stats.INT.scaler(StatScaling.Default, mod=-4),
            Stats.WIS.scaler(StatScaling.Default, mod=2),
            Stats.CHA.scaler(StatScaling.Default, mod=-4),
        ],
        hp_multiplier=1.2 * settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Fiend,
        languages=["Abyssal; telepathy 120 ft."],
        creature_class="Vrock",
        creature_subtype="Demon",
        senses=stats.senses.copy(darkvision=120),
        size=Size.Large,
        speed=Movement(walk=40, fly=60),
    )

    # ARMOR CLASS
    stats = stats.add_ac_template(UnholyArmor)

    # ATTACKS
    attack = natural.Claw.with_display_name("Diseased Talons")
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=DamageType.Poison,
    )

    # Vrocks use two attacks
    stats = stats.with_set_attacks(2)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Bruiser,
        additional_roles=[MonsterRole.Skirmisher, MonsterRole.Controller],
    )

    # SAVES
    stats = stats.grant_save_proficiency(Stats.DEX, Stats.WIS, Stats.CHA)

    # IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        immunities={DamageType.Poison},
        resistances={DamageType.Cold, DamageType.Lightning, DamageType.Fire},
        conditions={Condition.Poisoned},
    )

    # POWERS
    features = []

    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_VrockWeights(stats),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


VrockTemplate: CreatureTemplate = CreatureTemplate(
    name="Vrock",
    tag_line="Demon of Carnage and Ruin",
    description="Vrocks are screeching vulture-like harbringers of chaos and destruction that carry disease and pestilance from the lower planes.",
    environments=["Planar (Abyss)"],
    treasure=[],
    variants=[VrockVariant],
    species=[],
    callback=generate_vrock,
)
