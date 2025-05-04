from ..ac_templates import NaturalArmor
from ..attack_template import natural
from ..creature_types import CreatureType
from ..damage import Condition, DamageType
from ..powers import (
    LOW_POWER,
    MEDIUM_POWER,
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    select_powers,
)
from ..powers.creature import hydra
from ..powers.creature_type import beast, demon
from ..powers.themed import (
    aquatic,
    breath,
    cruel,
    cursed,
    diseased,
    fearsome,
    monstrous,
    reckless,
    serpentine,
)
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from .base_stats import BaseStatblock, base_stats

HydraVariant = MonsterVariant(
    name="Hydra",
    description="Hydras are massive, multi-headed serpents that dwell in swamps and marshes. They are fearsome predators, capable of regenerating lost heads and limbs. Their blood is a potent poison, and their breath can melt flesh and bone.",
    monsters=[Monster(name="Hydra", cr=8, srd_creatures=["Hydra"])],
)
HydraFoulbloodVariant = MonsterVariant(
    name="Foulblood Hydra",
    description="Foulblood Hydras are born of a fell curse that blends foul demonic blood with the hydra's own. Their blood is a viscous, black ichor that can corrupt the land around them.",
    monsters=[Monster(name="Foulblood Hydra", cr=12, is_legendary=True)],
)


class _HydraWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, variant: MonsterVariant):
        self.stats = stats
        self.variant = variant

    def force_powers(self) -> list[Power]:
        if self.variant is HydraFoulbloodVariant:
            return [hydra.HydraHeads, demon.BlackBlood]
        else:
            return [hydra.HydraHeads]

    def power_delta(self) -> float:
        if self.variant is HydraFoulbloodVariant:
            return -1 * demon.BlackBlood.power_level - MEDIUM_POWER
        else:
            return -1 * LOW_POWER

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        powers = [
            beast.WildInstinct,
            beast.FeedingFrenzy,
            beast.BestialRampage,
            breath.FleshMeltingBreath,
            cruel.BloodiedFrenzy,
            fearsome.FearsomeRoar,
            monstrous.Rampage,
            monstrous.TearApart,
            reckless.Charger,
            reckless.Toss,
            serpentine.SerpentineHiss,
        ]
        suppress = [
            reckless.RecklessFlurry  # don't work well with many attack
        ] + aquatic.AquaticPowers  # not exciting

        if self.variant is HydraFoulbloodVariant:
            powers += [
                cursed.VoidSiphon,
                cursed.RejectDivinity,
                cursed.CursedWound,
                demon.EchoOfRage,
                demon.FeastOfSouls,
            ]

        if p in suppress:
            return CustomPowerWeight(-1)
        elif p == breath.FleshMeltingBreath:
            return CustomPowerWeight(3.5, ignore_usual_requirements=True)
        elif p in powers:
            return CustomPowerWeight(2, ignore_usual_requirements=True)
        elif p in diseased.DiseasedPowers:
            return CustomPowerWeight(1.5, ignore_usual_requirements=False)
        else:
            return CustomPowerWeight(0.5, ignore_usual_requirements=False)


def generate_hydra(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    rng = settings.rng
    is_legendary = settings.is_legendary

    # STATS
    stats = base_stats(
        name=name,
        variant_key=settings.variant.key,
        template_key=settings.monster_template,
        monster_key=settings.monster_key,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Default, mod=2),
            Stats.CON.scaler(StatScaling.Constitution, mod=2),
            Stats.INT.scaler(StatScaling.Low),
            Stats.WIS.scaler(StatScaling.Default),
            Stats.CHA.scaler(StatScaling.Default, mod=-3),
        ],
        hp_multiplier=1.3 * settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Monstrosity,
        size=Size.Huge,
        creature_class="Hydra",
        senses=stats.senses.copy(darkvision=60),
    )
    stats = stats.with_types(
        primary_type=CreatureType.Monstrosity, additional_types=CreatureType.Fiend
    )

    stats = stats.copy(speed=stats.speed.delta(10).grant_swim())

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    # ARMOR CLASS
    stats = stats.add_ac_template(NaturalArmor)

    # ATTACKS
    attack = natural.Bite.with_display_name("Flesh-Disolving Bites")
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=DamageType.Acid,
    )
    stats = stats.with_set_attacks(5).copy(
        multiattack_custom_text="The hydra makes one attack for each of its heads"
    )
    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Bruiser,
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Perception, Skills.Initiative)
    stats = stats.grant_proficiency_or_expertise(Skills.Perception)  # expertise

    # SAVES
    if cr >= 10:
        stats = stats.grant_save_proficiency(Stats.CON, Stats.STR, Stats.WIS)

    # IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        resistances={DamageType.Acid},
        conditions={
            Condition.Blinded,
            Condition.Charmed,
            Condition.Deafened,
            Condition.Frightened,
            Condition.Stunned,
            Condition.Unconscious,
        },
    )

    # REACTIONS
    stats = stats.copy(reaction_count="One Per Head")

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_HydraWeights(stats, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


HydraTemplate: MonsterTemplate = MonsterTemplate(
    name="Hydra",
    tag_line="Multiheaded serpent of legend",
    description="Hydras are massive, multi-headed serpents that dwell in swamps and marshes. They are fearsome predators, capable of regenerating lost heads and limbs. Their blood is a potent poison, and their breath can melt flesh and bone.",
    environments=["Coastal", "Swamp"],
    treasure=[],
    variants=[HydraVariant, HydraFoulbloodVariant],
    species=[],
    callback=generate_hydra,
)
