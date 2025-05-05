import numpy as np

from ..ac_templates import flat
from ..attack_template import natural
from ..creature_types import CreatureType
from ..damage import DamageType
from ..movement import Movement
from ..powers import (
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    flags,
    select_powers,
)
from ..powers.creature import mimic
from ..powers.creature_type import ooze
from ..powers.roles import ambusher
from ..powers.themed import (
    aberrant,
    anti_magic,
    bestial,
    breath,
    illusory,
    monstrous,
    technique,
)
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..statblocks import BaseStatblock
from ._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from .base_stats import base_stats

MimicVariant = MonsterVariant(
    name="Mimic",
    description="Mimics disguise themselves as inanimate objects such as treasure chests, doors, or furniture to lure and ambush prey",
    monsters=[
        Monster(name="Mimic", cr=2, srd_creatures=["Mimic"]),
        Monster(
            name="Greater Mimic",
            cr=4,
            other_creatures={"Giant Mimic": "Waterdeep: Dragon Heist"},
        ),
        Monster(
            name="Vault Mimic",
            cr=8,
            other_creatures={"Hoard Mimic": "Fizzban's Treasury of Dragons"},
        ),
    ],
)


class _MimicWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, cr: float, rng: np.random.Generator):
        self.stats = stats
        self.cr = cr
        self.rng = rng

        flavor_powers = [
            mimic.ComfortingFamiliarty,
            bestial.MarkTheMeal,
            mimic.MagneticAttraction,
        ]
        general_powers = [
            ooze.LeechingGrasp,
            ambusher.DeadlyAmbusher,
            anti_magic.RedirectTeleport,
            mimic.InhabitArmor,
            mimic.SplinterStep,
        ]
        elite_powers = [
            ooze.SlimeSpray,
            breath.FleshMeltingBreath,
            illusory.PhantomMirage,
            mimic.HollowHome,
        ]

        if cr >= 8:
            n_flavor = 1
            n_regular = 1
            regular_powers = general_powers + elite_powers
        elif cr >= 4:
            n_flavor = 1
            n_regular = 1
            regular_powers = general_powers
        else:
            regular_powers = general_powers
            n_flavor = 1
            n_regular = 0

        force = [aberrant.Adhesive, monstrous.Swallow, technique.GrapplingAttack]

        flavor_indexes = rng.choice(len(flavor_powers), size=n_flavor, replace=False)
        force += [flavor_powers[i] for i in flavor_indexes]

        regular_indexes = rng.choice(len(regular_powers), size=n_regular, replace=False)
        force += [regular_powers[i] for i in regular_indexes]

        self.force = force

    def force_powers(self) -> list[Power]:
        return self.force

    def power_delta(self) -> float:
        return -100

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        return CustomPowerWeight(-1)


def generate_mimic(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    rng = settings.rng

    # STATS
    stats = base_stats(
        name=name,
        variant_key=settings.variant.key,
        template_key=settings.monster_template,
        monster_key=settings.monster_key,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Primary, mod=1),
            Stats.DEX.scaler(StatScaling.Default, mod=2),
            Stats.INT.scaler(StatScaling.Default, mod=-5),
            Stats.WIS.scaler(StatScaling.Medium, mod=2),
            Stats.CHA.scaler(StatScaling.Default, mod=-2),
        ],
        hp_multiplier=1.25 * settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Monstrosity,
        creature_class="Mimic",
        senses=stats.senses.copy(darkvision=60),
    )

    # SIZE
    if cr >= 8:
        size = Size.Huge
    elif cr >= 4:
        size = Size.Large
    else:
        size = Size.Medium

    stats = stats.copy(size=size)

    # ARMOR CLASS
    stats = stats.add_ac_template(flat(12))

    # ATTACKS
    attack = natural.Slam.with_display_name("Sticky Pseudopod")
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=DamageType.Acid,
    )

    # ROLES
    stats = stats.with_roles(primary_role=MonsterRole.Ambusher)

    # MOVEMENT
    stats = stats.with_flags(flags.NO_TELEPORT)
    stats = stats.copy(speed=Movement(walk=20, climb=20))

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(
        Skills.Stealth
    ).grant_proficiency_or_expertise(Skills.Stealth)  # expertise

    # SAVES
    if cr >= 4:
        stats = stats.grant_save_proficiency(Stats.CON)
    if cr >= 8:
        stats = stats.grant_save_proficiency(Stats.WIS)

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_MimicWeights(stats, cr, rng),
    )
    features += power_features

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


MimicTemplate: MonsterTemplate = MonsterTemplate(
    name="Mimic",
    tag_line="Paranoia-Inducing Shapeshifting Ambusher",
    description="Mimics disguise themselves as inanimate objects such as treasure chests, doors, or furniture to lure and ambush prey",
    environments=["Dungeon", "Urban"],
    treasure=[],
    variants=[MimicVariant],
    species=[],
    callback=generate_mimic,
)
