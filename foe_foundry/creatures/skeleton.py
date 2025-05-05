import numpy as np

from ..ac_templates import Breastplate, Unarmored
from ..attack_template import spell, weapon
from ..creature_types import CreatureType
from ..damage import Condition, DamageType
from ..powers import (
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


class _BasicSkeletonWeights(CustomPowerSelection):
    def __init__(self, rng: np.random.Generator):
        skeletal_powers = skeletal.SkeletalPowers

        martial_powers = [
            soldier.Phalanx,
            soldier.CoordinatedStrike,
            soldier.Disciplined,
            soldier.Lunge,
            soldier.PreciseStrike,
            technique.VexingAttack,
            technique.GrazingAttack,
            technique.Dueling,
            technique.PommelStrike,
            technique.BaitAndSwitch,
            technique.ParryAndRiposte,
        ]

        skeletal_power_index = rng.choice(len(skeletal_powers))
        chosen_skeletal_power: Power = skeletal_powers[skeletal_power_index]
        martial_power_index = rng.choice(len(martial_powers))
        chosen_martial_power: Power = martial_powers[martial_power_index]
        self.force = [chosen_skeletal_power, chosen_martial_power]

    def force_powers(self) -> list[Power]:
        return self.force

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        # everything through force_powers
        return CustomPowerWeight(weight=-1, ignore_usual_requirements=False)


class _AdvancedSkeletonWeights(CustomPowerSelection):
    def __init__(
        self, stats: BaseStatblock, variant: MonsterVariant, rng: np.random.Generator
    ):
        self.stats = stats
        self.variant = variant
        self.cr = stats.cr
        self.rng = rng

        skeletal_powers = skeletal.SkeletalPowers + [
            cursed.CursedWound,
            deathly.WitheringBlow,
            deathly.DrainingBlow,
            fearsome.DreadGaze,
        ]
        special_powers = []
        required_powers = []

        leader_powers = [
            leader.CommandTheAttack,
            leader.CommandTheTroops,
            leader.FanaticFollowers,
        ]

        if self.variant is GraveGuardVariant:
            required_powers = [defender.Protection]
            special_powers = (
                [
                    technique.ArmorMaster,
                    technique.DisarmingAttack,
                    technique.Interception,
                    technique.ShieldMaster,
                    anti_ranged.DeflectMissile,
                    honorable.Challenge,
                ]
                + defender.DefenderPowers
                + leader_powers
            )
            skeletal_powers.remove(skeletal.BoneSpear)
        elif self.variant is BurningSkeletonVariant:
            required_powers = [technique.BurningAttack]
            skeletal_powers.remove(cursed.CursedWound)  # not fire themed
            special_powers += [
                elemental.ElementalFireball,
                elemental.FireBurst,
                elemental.FireElementalAffinity,
                elemental.FireSmite,
                elemental.SuperheatedAura,
            ]
        elif self.variant is FreezingSkeletonVariant:
            required_powers = [technique.FreezingAttack]
            skeletal_powers.remove(cursed.CursedWound)  # not cold themed
            special_powers += [
                undead.SoulChill,
                undead.StygianBurst,
                elemental.IceBurst,
                elemental.IceElementalAffinity,
                elemental.ConeOfCold,
                elemental.IceSmite,
                elemental.ArcticChillAura,
            ] + icy.IcyPowers

        # choose 1 skeletal and 1 special power
        skeletal_power_index = self.rng.choice(len(skeletal_powers))
        chosen_skeletal_power: Power = skeletal_powers[skeletal_power_index]

        special_power_index = self.rng.choice(len(special_powers))
        chosen_special_power: Power = special_powers[special_power_index]

        # if CR 6 or higher, add a leader power as well
        selected_leader_powers = []
        if self.cr >= 6:
            leader_power_index = self.rng.choice(len(leader_powers))
            chosen_leader_power: Power = leader_powers[leader_power_index]
            selected_leader_powers.append(chosen_leader_power)

        self.force = (
            required_powers
            + [chosen_skeletal_power, chosen_special_power]
            + selected_leader_powers
        )

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        # everything through force_powers
        return CustomPowerWeight(weight=-1, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        return self.force


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
        n_attack = 1
    elif variant is GraveGuardVariant:
        attack = weapon.SpearAndShield.with_display_name("Bone Spear")
        secondary_damage_type = DamageType.Piercing
        secondary_attack = weapon.Shortbow.with_display_name("Bone Bow")
        n_attack = 2
    elif variant is BurningSkeletonVariant:
        attack = weapon.Greatsword.with_display_name("Burning Blade")
        secondary_damage_type = DamageType.Fire
        secondary_attack = spell.Firebolt.with_display_name("Hurl Flames").copy(
            damage_scalar=0.9
        )
        n_attack = 2
    elif variant is FreezingSkeletonVariant:
        attack = weapon.Greatsword.with_display_name("Freezing Blade")
        secondary_damage_type = DamageType.Cold
        secondary_attack = spell.Frostbolt.with_display_name("Deathly Freeze").copy(
            damage_scalar=0.9
        )
        n_attack = 2

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=secondary_damage_type,
    )
    stats = stats.with_set_attacks(multiattack=n_attack)

    if secondary_attack is not None:
        stats = secondary_attack.add_as_secondary_attack(stats)

    # ROLES
    if variant is SkeletonVariant:
        primary_role = MonsterRole.Soldier
        additional_roles = []
    elif variant is GraveGuardVariant:
        primary_role = MonsterRole.Defender
        additional_roles = [MonsterRole.Leader]
    else:
        primary_role = MonsterRole.Soldier
        additional_roles = [MonsterRole.Leader] if cr >= 6 else []

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
        custom=_BasicSkeletonWeights(rng)
        if variant is SkeletonVariant
        else _AdvancedSkeletonWeights(stats, variant, rng),
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
