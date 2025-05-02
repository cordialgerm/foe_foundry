from ..ac_templates import Unarmored, UnholyArmor
from ..attack_template import natural, spell
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
from ..powers.creature import ghoul
from ..powers.creature_type import undead
from ..powers.roles import bruiser, skirmisher
from ..powers.spellcaster import necromancer
from ..powers.themed import (
    cruel,
    cursed,
    deathly,
    diseased,
    fearsome,
    poison,
    reckless,
    technique,
)
from ..role_types import MonsterRole
from ..skills import Stats, StatScaling
from ..spells import CasterType
from .base_stats import BaseStatblock, base_stats
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

GhoulVariant = CreatureVariant(
    name="Ghoul",
    description="Ghouls rise from the bodies of cannibals and villains with depraved hungers. They form packs out of shared voracity.",
    suggested_crs=[
        SuggestedCr(name="Ghoul", cr=1, srd_creatures=["Ghoul"]),
    ],
)

GhastVariant = CreatureVariant(
    name="Ghast",
    description="Ghasts are reeking, undying corpses closely related to ghouls. They hunger for the vices they enjoyed in life as much as they do for rotting flesh.",
    suggested_crs=[
        SuggestedCr(name="Ghast", cr=2, srd_creatures=["Ghast"]),
    ],
)

GravelordVariant = CreatureVariant(
    name="Gravelord",
    description="Gravelords are ghouls that have been blessed by a dark power, granting them the ability to raise the dead.",
    suggested_crs=[
        SuggestedCr(
            name="Ghast Gravelord", cr=6, other_creatures={"Ghast Dreadcaller": "mm25"}
        )
    ],
)


class _GhoulWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, variant: CreatureVariant):
        self.stats = stats
        self.variant = variant

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        powers = [undead.StenchOfDeath, poison.VileVomit, poison.PoisonousBurst]

        # ghouls can spread physical diseases
        desired_diseases = {
            diseased.FilthFever,
            diseased.FleshRot,
            diseased.BlindingSickness,
        }
        disease_powers = [
            p
            for p in diseased.ToxicBreathPowers
            if p.disease in desired_diseases  # type: ignore
        ]

        suppress = [
            undead.UndeadFortitude,
            fearsome.MindShatteringScream,
            fearsome.HorrifyingVisage,
        ]

        if self.variant is GravelordVariant:
            powers += [
                deathly.EndlessServitude,
                deathly.FleshPuppets,
                undead.StygianBurst,
                cursed.AuraOfDespair,
                cursed.BestowCurse,
                cursed.RejectDivinity,
                cursed.UnholyAura,
                cursed.VoidSiphon,
            ]
            secondary_powers = []
            suppress += diseased.DiseasedPowers
        else:
            powers += [
                bruiser.Rend,
                cruel.BloodiedFrenzy,
                reckless.BloodiedRage,
                reckless.Charger,
                reckless.RecklessFlurry,
                skirmisher.HarassingRetreat,
            ]
            secondary_powers = disease_powers

        if self.variant is GravelordVariant:
            suppress += [deathly.WitheringBlow]

        if p in suppress:
            return CustomPowerWeight(weight=-1, ignore_usual_requirements=False)
        elif p in powers:
            return CustomPowerWeight(weight=2.5, ignore_usual_requirements=True)
        elif p in secondary_powers:
            return CustomPowerWeight(weight=1.5, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(weight=0.25)

    def force_powers(self) -> list[Power]:
        if self.variant is GhoulVariant:
            return [technique.WeakeningAttack, ghoul.Cannibal]
        elif self.variant is GhastVariant:
            return [technique.WeakeningAttack, ghoul.Cannibal, undead.StenchOfDeath]
        elif self.variant is GravelordVariant:
            return [
                technique.WeakeningAttack,
                ghoul.Cannibal,
                undead.StenchOfDeath,
                necromancer.NecromancerMaster,
            ]
        else:
            raise ValueError(f"Unknown ghoul variant: {self.variant}")

    def power_delta(self) -> float:
        if self.variant is GravelordVariant:
            return 0.0  # gravelord is spellcaster with lots of stuff already
        else:
            return MEDIUM_POWER if self.stats.cr <= 1 else LOW_POWER


def generate_ghoul(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    rng = settings.rng

    # STATS
    hp_multiplier = 0.825

    if variant is GravelordVariant:
        stats = [
            Stats.STR.scaler(StatScaling.Medium, mod=-1),
            Stats.DEX.scaler(StatScaling.Medium, mod=2),
            Stats.CON.scaler(StatScaling.Constitution, mod=-2),
            Stats.INT.scaler(StatScaling.Primary),
            Stats.WIS.scaler(StatScaling.Default, mod=-0.5),
            Stats.CHA.scaler(StatScaling.Medium),
        ]
    else:
        stats = [
            Stats.STR.scaler(StatScaling.Medium, mod=2),
            Stats.DEX.scaler(StatScaling.Primary),
            Stats.CON.scaler(StatScaling.Constitution, mod=-2),
            Stats.INT.scaler(StatScaling.Default, mod=-3),
            Stats.WIS.scaler(StatScaling.Default, mod=-0.5),
            Stats.CHA.scaler(StatScaling.Default, mod=-4),
        ]

    stats = base_stats(
        name=name,
        variant_key=settings.variant.key,
        template_key=settings.creature_template,
        cr=cr,
        stats=stats,
        hp_multiplier=hp_multiplier * settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Undead,
        languages=["Common"],
        creature_class="Ghoul",
        senses=stats.senses.copy(darkvision=60),
    )

    # ARMOR CLASS
    if variant is GravelordVariant:
        stats = stats.add_ac_template(UnholyArmor)
    else:
        stats = stats.add_ac_template(Unarmored)

    # ATTACKS
    attack = natural.Claw.with_display_name("Paralytic Claw")
    secondary_damage_type = DamageType.Poison

    if variant is GravelordVariant:
        secondary_attack = spell.Deathbolt.copy(damage_scalar=0.9).with_display_name(
            "Dread Bolt"
        )
    else:
        secondary_attack = None

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=secondary_damage_type,
    )

    if secondary_attack is not None:
        stats = secondary_attack.add_as_secondary_attack(stats)

    ## SPELLCASTING
    if variant is GravelordVariant:
        stats = stats.grant_spellcasting(caster_type=CasterType.Arcane)

    # ROLES
    if variant is GravelordVariant:
        stats = stats.with_roles(
            primary_role=MonsterRole.Leader, additional_roles=MonsterRole.Skirmisher
        )
    else:
        stats = stats.with_roles(
            primary_role=MonsterRole.Bruiser, additional_roles=MonsterRole.Skirmisher
        )

    # SAVES
    if stats.cr >= 2:
        stats = stats.grant_save_proficiency(Stats.WIS)

    # IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        immunities={DamageType.Poison},
        resistances={DamageType.Necrotic} if stats.cr >= 2 else set(),
        conditions={Condition.Poisoned, Condition.Charmed, Condition.Poisoned},
    )

    # POWERS
    features = []

    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_GhoulWeights(stats, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)

    if secondary_attack is not None:
        secondary_attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


GhoulTemplate: CreatureTemplate = CreatureTemplate(
    name="Ghoul",
    tag_line="Undead cannibals",
    description="Ghouls are horrid creatures that feast on the flesh of the living and the dead.",
    environments=["Swamp", "Underdark", "Urban"],
    treasure=[],
    variants=[GhoulVariant, GhastVariant, GravelordVariant],
    species=[],
    callback=generate_ghoul,
)
