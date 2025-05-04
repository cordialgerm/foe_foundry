import numpy as np

from ..ac_templates import Breastplate, Unarmored
from ..attack_template import spell, weapon
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
from ..powers.creature import skeletal
from ..powers.creature_type import elemental, undead
from ..powers.roles import defender, leader, soldier
from ..powers.themed import (
    anti_ranged,
    cursed,
    deathly,
    fearsome,
    honorable,
    icy,
    technique,
)
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Stats, StatScaling
from ._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from .base_stats import BaseStatblock, base_stats

SkeletonVariant = MonsterVariant(
    name="Skeleton",
    description="Skeletons are reanimated Humanoid bones bearing the equipment they had in life. They have rudimentary faculties and greater agility than zombies and similar shambling corpses. While they aren't capable of creating plans of their own, they avoid obvious barriers and self-destructive situations.",
    monsters=[
        Monster(name="Skeleton", cr=1 / 4, srd_creatures=["Skeleton"]),
    ],
)

GraveGuardVariant = MonsterVariant(
    name="Skeletal Grave Guard",
    description="Grave guards are skeletal warriors that have been reanimated with a greater degree of intelligence and purpose. They are often used as guardians for tombs or other sacred sites.",
    monsters=[
        Monster(name="Skeletal Grave Guard", cr=4),
    ],
)

BurningSkeletonVariant = MonsterVariant(
    name="Burning Skeleton",
    description="Flaming skeletons burn with unbridled necromantic energy. This magic grants them blazing attacks and greater awareness, which they use to command lesser Undead.",
    monsters=[
        Monster(
            name="Burning Skeleton", cr=3, other_creatures={"Flaming Skeleton": "mm25"}
        ),
        Monster(name="Burning Skeletal Champion", cr=6),
    ],
)

FreezingSkeletonVariant = MonsterVariant(
    name="Freezing Skeleton",
    description="Freezing skeletons are wreathed in the icy cold of the deathly river Styx.",
    monsters=[
        Monster(name="Freezing Skeleton", cr=3),
        Monster(name="Freezing Skeletal Champion", cr=6),
    ],
)


class _SkeletonWeights(CustomPowerSelection):
    def __init__(
        self, stats: BaseStatblock, variant: MonsterVariant, rng: np.random.Generator
    ):
        self.stats = stats
        self.variant = variant
        self.cr = stats.cr
        self.rng = rng

        general_powers = skeletal.SkeletalPowers + soldier.SoldierPowers

        force = []
        techniques = [
            technique.VexingAttack,
            technique.GrazingAttack,
            technique.Dueling,
            technique.PommelStrike,
            technique.BaitAndSwitch,
            technique.ParryAndRiposte,
        ]

        if self.cr >= 3:
            force = []
            general_powers += [
                cursed.CursedWound,
                deathly.WitheringBlow,
                deathly.DrainingBlow,
                fearsome.DreadGaze,
                leader.CommandTheAttack,
                leader.CommandTheTroops,
            ]

        if self.variant is GraveGuardVariant:
            force = [defender.Protection]
            techniques = [
                technique.ArmorMaster,
                technique.DisarmingAttack,
                technique.Interception,
                technique.ShieldMaster,
            ]
            general_powers += [
                anti_ranged.DeflectMissile,
                honorable.Challenge,
            ] + defender.DefenderPowers

        if self.variant is BurningSkeletonVariant:
            force = [technique.BurningAttack]
            general_powers += [
                elemental.ElementalFireball,
                elemental.FireBurst,
                elemental.FireElementalAffinity,
                elemental.FireSmite,
                elemental.SuperheatedAura,
            ]

        if self.variant is FreezingSkeletonVariant:
            force = [technique.FreezingAttack]
            general_powers += [
                undead.SoulChill,
                undead.StygianBurst,
                elemental.IceBurst,
                elemental.IceElementalAffinity,
                elemental.ConeOfCold,
                elemental.IceSmite,
                elemental.ArcticChillAura,
            ] + icy.IcyPowers

        technique_index = self.rng.choice(len(techniques))
        chosen_technique: Power = techniques[technique_index]

        self.force = force + [chosen_technique]
        self.general_powers = general_powers
        self.techniques = techniques

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        # use a very flat power weight to try to make them all more or less likely to see
        if p in self.general_powers:
            return CustomPowerWeight(weight=0.1, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(weight=-1, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        return self.force

    def power_delta(self) -> float:
        return (LOW_POWER if self.cr <= 2 else MEDIUM_POWER) - 0.2 * sum(
            p.power_level for p in self.force
        )


def generate_skeleton(settings: GenerationSettings) -> StatsBeingGenerated:
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
            Stats.STR.scaler(StatScaling.Default),
            Stats.DEX.scaler(StatScaling.Primary),
            Stats.INT.scaler(StatScaling.Default, mod=-4),
            Stats.WIS.scaler(StatScaling.Default, mod=-2),
            Stats.CHA.scaler(StatScaling.Default, mod=-5),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Undead,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Skeleton",
        senses=stats.senses.copy(darkvision=60),
    )

    # ARMOR CLASS
    if stats.cr >= 3:
        stats = stats.add_ac_template(Breastplate)
    else:
        stats = stats.add_ac_template(Unarmored)

    # ATTACKS
    if variant is SkeletonVariant:
        attack = weapon.Daggers.with_display_name("Bone Blades").copy(
            damage_scalar=0.75
        )  # dual wielding too scary at low CR
        secondary_damage_type = None
        secondary_attack = weapon.Shortbow.with_display_name("Bone Bow")
    elif variant is GraveGuardVariant:
        attack = weapon.SpearAndShield.with_display_name("Bone Spear")
        secondary_damage_type = DamageType.Piercing
        secondary_attack = weapon.Shortbow.with_display_name("Bone Bow")
    elif variant is BurningSkeletonVariant:
        attack = weapon.Greatsword.with_display_name("Burning Blade")
        secondary_damage_type = DamageType.Fire
        secondary_attack = spell.Firebolt.with_display_name("Hurl Flames").copy(
            damage_scalar=0.9
        )
    elif variant is FreezingSkeletonVariant:
        attack = weapon.Greatsword.with_display_name("Freezing Blade")
        secondary_damage_type = DamageType.Cold
        secondary_attack = spell.Frostbolt.with_display_name("Deathly Freeze").copy(
            damage_scalar=0.9
        )

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=secondary_damage_type,
    )

    if secondary_attack is not None:
        stats = secondary_attack.add_as_secondary_attack(stats)

    # ROLES
    if variant is GraveGuardVariant:
        primary_role = MonsterRole.Soldier
        additional_roles = [MonsterRole.Defender]
    else:
        primary_role = MonsterRole.Soldier
        additional_roles = []

    stats = stats.with_roles(
        primary_role=primary_role,
        additional_roles=additional_roles,
    )

    # SAVES
    if cr >= 3:
        stats = stats.grant_save_proficiency(Stats.CON)

    # IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        immunities={DamageType.Poison},
        conditions={Condition.Poisoned},
        vulnerabilities={DamageType.Bludgeoning},
    )
    if secondary_damage_type is not None:
        stats = stats.grant_resistance_or_immunity(immunities={secondary_damage_type})

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_SkeletonWeights(stats, variant, rng),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    if secondary_attack is not None:
        stats = secondary_attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


SkeletonTemplate: MonsterTemplate = MonsterTemplate(
    name="Skeleton",
    tag_line="Ossified Evil",
    description="Skeletons rise at the summons of necromancers and foul spirits. Whether they’re the remains of the ancient dead or fresh bones bound to morbid ambitions, they commit deathless work for whatever forces reanimated them, often serving as guardians, soldiers, or laborers.",
    environments=["Planar (Shadowfel)", "Underdark", "Urban"],
    treasure=[],
    variants=[
        SkeletonVariant,
        GraveGuardVariant,
        BurningSkeletonVariant,
        FreezingSkeletonVariant,
    ],
    species=[],
    callback=generate_skeleton,
)
