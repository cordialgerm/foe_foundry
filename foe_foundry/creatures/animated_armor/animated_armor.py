import numpy as np

from ...ac_templates import PlateArmor
from ...attack_template import natural, weapon
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...movement import Movement
from ...powers import (
    NewPowerSelection,
    select_powers,
)
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Stats, StatScaling
from ...statblocks import BaseStatblock
from .._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from ..base_stats import base_stats
from . import powers

AnimatedArmorVariant = MonsterVariant(
    name="Animated Armor",
    description="Animated Armor are constructed suits of armor that have been magically animated to serve as a guardian or protector. It is typically made of metal and has a humanoid shape.",
    monsters=[
        Monster(
            name="Animated Armor",
            cr=1,
            srd_creatures=["Animated Armor"],
        )
    ],
)

RunicSpellplateVariant = MonsterVariant(
    name="Animated Runeplate",
    description="An Animated Runeplate is a suit of rune-etched armor that has been magically animated to serve as a powerful warrior. The runes grant it powerful magical protections and the ability to fly, chasing down arcane foes with deadly precision.",
    monsters=[
        Monster(
            name="Animated Runeplate", cr=4, other_creatures={"Helmed Horror": "mm24"}
        )
    ],
)


def _custom_powers(
    stats: BaseStatblock, variant: MonsterVariant, rng: np.random.Generator
) -> NewPowerSelection:
    if variant is AnimatedArmorVariant:
        return NewPowerSelection(powers.LoadoutAnimatedArmor, rng=rng)
    elif variant is RunicSpellplateVariant:
        return NewPowerSelection(powers.LoadoutRunicSpellplate, rng)
    else:
        raise ValueError(f"Unknown variant: {variant}")


def generate_animated_armor(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    rng = settings.rng

    # STATS
    if variant is AnimatedArmorVariant:
        attrs = [
            Stats.STR.scaler(StatScaling.Primary, mod=1),
            Stats.DEX.scaler(StatScaling.Medium),
            Stats.CON.scaler(StatScaling.Constitution, mod=2),
            Stats.INT.scaler(StatScaling.NoScaling, mod=-9),
            Stats.WIS.scaler(StatScaling.NoScaling, mod=-7),
            Stats.CHA.scaler(StatScaling.NoScaling, mod=-9),
        ]
        hp_multiplier = 1.0
        damage_multiplier = 1.0
    elif variant is RunicSpellplateVariant:
        attrs = [
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Medium),
            Stats.CON.scaler(StatScaling.Constitution, mod=2),
            Stats.INT.scaler(StatScaling.NoScaling, mod=0),
            Stats.WIS.scaler(StatScaling.NoScaling, mod=0),
            Stats.CHA.scaler(StatScaling.NoScaling, mod=0),
        ]
        hp_multiplier = 0.8
        damage_multiplier = 0.9

    stats = base_stats(
        name=name,
        variant_key=settings.variant.key,
        template_key=settings.monster_template,
        monster_key=settings.monster_key,
        cr=cr,
        stats=attrs,
        hp_multiplier=hp_multiplier * settings.hp_multiplier,
        damage_multiplier=damage_multiplier * settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Construct,
        size=Size.Medium,
        languages=["Understands Common but can't speak"],
        creature_class="Animated Armor",
        senses=stats.senses.copy(blindsight=60),
        uses_shield=True if variant is RunicSpellplateVariant else False,
    )

    # SPEED
    stats = stats.copy(speed=Movement(walk=30, fly=30, hover=True))

    # ARMOR CLASS
    stats = stats.add_ac_template(PlateArmor)

    if variant is RunicSpellplateVariant:
        attack = weapon.SwordAndShield.with_display_name("Runic Blade")
        secondary_damage_type = DamageType.Force
    else:
        attack = natural.Slam.with_display_name("Plated Gauntlet")
        secondary_damage_type = None

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=secondary_damage_type,
    )

    # Animated Armor use fewer attacks
    stats = stats.with_set_attacks(multiattack=2)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Defender, additional_roles=[MonsterRole.Soldier]
    )

    # IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        immunities={DamageType.Poison, DamageType.Psychic},
        conditions={
            Condition.Poisoned,
            Condition.Charmed,
            Condition.Blinded,
            Condition.Stunned,
            Condition.Exhaustion,
            Condition.Frightened,
            Condition.Paralyzed,
            Condition.Petrified,
        },
    )

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_custom_powers(stats, variant, rng),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


AnimatedArmorTemplate: MonsterTemplate = MonsterTemplate(
    name="Animated Armor",
    tag_line="Mage-Wrought Animated Guardians",
    description="Animated Armor are constructed suits of armor that have been magically animated to serve as a guardian or protector. It is typically made of metal and has a humanoid shape.",
    environments=[],
    treasure=[],
    variants=[AnimatedArmorVariant, RunicSpellplateVariant],
    species=[],
    callback=generate_animated_armor,
)
