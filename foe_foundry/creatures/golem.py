import numpy as np

from ..ac_templates import NaturalPlating, Unarmored
from ..attack_template import natural, spell
from ..creature_types import CreatureType
from ..damage import Condition, DamageType
from ..powers import CustomPowerWeight, Power, select_powers
from ..powers.creature_type import construct
from ..powers.creature_type.construct import ImmutableForm
from ..powers.roles import defender
from ..powers.themed import breath
from ..powers.themed.reckless import BloodiedRage
from ..powers.themed.technique import GrapplingAttack, PushingAttack, SappingAttack
from ..powers.themed.tough import MagicResistance
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Stats, StatScaling
from ..statblocks import BaseStatblock, MonsterDials
from .base_stats import base_stats
from .template import (
    CreatureSpecies,
    CreatureTemplate,
    CreatureVariant,
    StatsBeingGenerated,
    SuggestedCr,
)

StoneVariant = CreatureVariant(
    name="Stone Golem",
    description="Stone golems take varied forms, such as weathered carvings of ancient deities, lifelike sculptures of heroes, or any other shape their makers imagine. No matter their design or the rock from which they’re crafted, these golems are strengthened by the magic that animates them, allowing them to follow their creators' orders for centuries.",
    suggested_crs=[
        SuggestedCr(
            name="Stone Golem",
            cr=10,
            srd_creatures=["Stone Golem"],
        )
    ],
)
ClayVariant = CreatureVariant(
    name="Clay Golem",
    description="TODO",
    suggested_crs=[
        SuggestedCr(
            name="Clay Golem",
            cr=9,
            srd_creatures=["Clay Golem"],
        )
    ],
)
IronVariant = CreatureVariant(
    name="Iron Golem",
    description="Their magical cores protected by mighty armor, iron golems defend important sites and objects. These golems are forged in bipedal forms, the details of which are decided by their creators. Many resemble armored guardians or legendary heroes. Iron golems confront their foes with a combination of overwhelming physical force and eruptions from their magical core. These magical blasts take the form of fiery bolts and poisonous emissions.",
    suggested_crs=[
        SuggestedCr(
            name="Iron Golem",
            cr=16,
            srd_creatures=["Iron Golem"],
        )
    ],
)
FleshVariant = CreatureVariant(
    name="Flesh Golem",
    description="Flesh golems are roughly human-shaped collections of body parts bound together by misused magic or strange science. They serve their reckless creators, but many possess disjointed memories and instincts from their component parts. If wounded, these golems might go berserk and vent their confusion on anything in their sight, including their creators.",
    suggested_crs=[
        SuggestedCr(
            name="Flesh Golem",
            cr=5,
            srd_creatures=["Flesh Golem"],
        )
    ],
)
IceVariant = CreatureVariant(
    name="Ice Golem",
    description="Ice golems are crafted from magically frozen cores specially prepared by their creators. These golems are often used to guard remote locations or to serve as sentinels in icy realms. Their bodies are sculpted from ice and snow, and their creators can imbue them with a variety of powers, such as the ability to freeze foes or to create blizzards.",
    suggested_crs=[SuggestedCr(name="Ice Golem", cr=7)],
)
ShieldGuardianVariant = CreatureVariant(
    name="Shield Guardian",
    description="A shield guardian's primary goal is to protect its master. It escorts whoever bears its command amulet and intercedes between the bearer and any threat. Although it isn’t mindless, a shield guardian has no sense of self preservation and will sacrifice itself to protect its master.",
    suggested_crs=[
        SuggestedCr(
            name="Shield Guardian",
            cr=7,
            srd_creatures=["Shield Guardian"],
        )
    ],
)


class _CustomWeights:
    def __init__(self, stats: BaseStatblock, variant: CreatureVariant):
        self.stats = stats
        self.variant = variant

    def __call__(self, p: Power) -> CustomPowerWeight:
        # powers that any Golem can have
        boost_powers = [
            construct.ConstructedGuardian,
            construct.ProtectivePlating,
            construct.ExplosiveCore,
            defender.Protection,
            defender.ZoneOfControl,
            defender.SpellReflection,
        ]

        # attack powers any golem can have
        attack_powers = [
            GrapplingAttack,
            SappingAttack,
            PushingAttack,
        ]

        suppress_powers = [construct.Smother, construct.Retrieval]

        # variant-specific powers
        variant_powers = []

        if self.variant is ShieldGuardianVariant:
            suppress_powers.append(construct.ConstructedGuardian)
            suppress_powers.append(construct.ProtectivePlating)
            variant_powers.append(defender.Protection)

        if self.variant is FleshVariant:
            suppress_powers += [
                construct.ConstructedGuardian,
                construct.ProtectivePlating,
                construct.ExplosiveCore,
            ]

        if self.variant in {StoneVariant, ShieldGuardianVariant}:
            variant_powers += [construct.SpellStoring]

        if self.variant is IronVariant:
            variant_powers += [breath.NerveGasBreath]

        if self.variant is IceVariant:
            variant_powers += [breath.FlashFreezeBreath]

        if p in suppress_powers:
            return CustomPowerWeight(-1, ignore_usual_requirements=True)
        elif p in variant_powers:
            return CustomPowerWeight(2.5, ignore_usual_requirements=True)
        elif p in attack_powers:
            return CustomPowerWeight(2.5, ignore_usual_requirements=True)
        elif p in boost_powers:
            return CustomPowerWeight(1.5, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(0.25, ignore_usual_requirements=False)


def generate_golem(
    name: str,
    cr: float,
    variant: CreatureVariant,
    rng: np.random.Generator,
    species: CreatureSpecies | None = None,
) -> StatsBeingGenerated:
    # STATS

    if variant is not FleshVariant:
        attrs = [
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.NoScaling, mod=-2),
            Stats.CON.scaler(StatScaling.Constitution, mod=2),
            Stats.INT.scaler(StatScaling.NoScaling, mod=-7),
            Stats.WIS.scaler(StatScaling.Default, mod=-2.5),
            Stats.CHA.scaler(StatScaling.NoScaling, mod=-9),
        ]
    else:
        attrs = [
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.NoScaling, mod=-2),
            Stats.CON.scaler(StatScaling.Constitution, mod=2),
            Stats.INT.scaler(StatScaling.NoScaling, mod=-3),
            Stats.WIS.scaler(StatScaling.Default, mod=-2.5),
            Stats.CHA.scaler(StatScaling.NoScaling, mod=-4),
        ]

    stats = base_stats(name=name, cr=cr, stats=attrs)

    stats = stats.copy(
        creature_type=CreatureType.Construct,
        size=Size.Large,
        languages=["Understands commands given in any language but can't speak"],
        creature_class="Golem",
        senses=stats.senses.copy(darkvision=120),
    )

    # ARMOR CLASS
    if variant is FleshVariant:
        stats = stats.add_ac_template(Unarmored)
    else:
        stats = stats.add_ac_template(NaturalPlating)

    # ATTACKS
    if variant is IceVariant:
        attack = natural.Slam.with_display_name("Frozen Fist")
        secondary_attack = spell.Frostbolt.with_display_name("Ice Shards")
        secondary_damage_type = DamageType.Cold
    elif variant is ShieldGuardianVariant:
        attack = natural.Slam.with_display_name("Protective Fist")
        secondary_attack = None
        secondary_damage_type = DamageType.Force
    elif variant is FleshVariant:
        attack = natural.Slam.with_display_name("Mutilated Fist")
        secondary_attack = None
        secondary_damage_type = DamageType.Lightning
    elif variant is IronVariant:
        attack = natural.Slam.with_display_name("Iron Fist")
        secondary_attack = spell.Firebolt.with_display_name("Fiery Beams")
        secondary_damage_type = DamageType.Fire
    elif variant is ClayVariant:
        attack = natural.Slam.with_display_name("Dissolving Fist")
        secondary_attack = None
        secondary_damage_type = DamageType.Acid
    elif variant is StoneVariant:
        attack = natural.Slam
        secondary_attack = spell.ArcaneBurst.with_display_name("Core Eruption")
        secondary_damage_type = DamageType.Force

    stats = attack.alter_base_stats(stats, rng)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=secondary_damage_type,
    )
    if secondary_attack is not None:
        stats = secondary_attack.add_as_secondary_attack(stats)

    # Golems have a slow attack speed, but attacks hit hard
    stats = stats.with_reduced_attacks(reduce_by=2, min_attacks=2)

    # Golems have high HP and AC and lower damage
    # Flesh Golems are a bit more aggressive since they're unarmored
    if variant is FleshVariant:
        stats = stats.apply_monster_dials(
            MonsterDials(hp_multiplier=1.4, attack_damage_multiplier=0.9)
        )
    else:
        stats = stats.apply_monster_dials(
            MonsterDials(hp_multiplier=1.25, attack_damage_multiplier=0.8)
        )

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Defender, additional_roles=[MonsterRole.Bruiser]
    )

    # IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        immunities={DamageType.Poison, DamageType.Psychic}
        if variant is not FleshVariant
        else {DamageType.Poison},
        conditions={
            Condition.Poisoned,
            Condition.Charmed,
            Condition.Exhaustion,
            Condition.Frightened,
            Condition.Paralyzed,
            Condition.Petrified,
        },
    )
    if secondary_damage_type is not None and variant in {
        IceVariant,
        IronVariant,
        FleshVariant,
        ClayVariant,
    }:
        stats = stats.grant_resistance_or_immunity(immunities={secondary_damage_type})

    # POWERS
    features = []

    # construct.BoundProtector,
    default_powers = [ImmutableForm, MagicResistance]
    if variant is ShieldGuardianVariant:
        default_powers += [construct.BoundProtector]
    elif variant in {FleshVariant, ClayVariant}:
        default_powers += [BloodiedRage]

    for power in default_powers:
        stats = power.modify_stats(stats)
        features += power.generate_features(stats)

    stats = stats.apply_monster_dials(
        MonsterDials(
            recommended_powers_modifier=-1
            / 4
            * sum(p.power_level for p in default_powers)
        )
    )

    def custom_filter(p: Power) -> bool:
        return p not in default_powers

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        power_level=stats.recommended_powers,
        custom_weights=_CustomWeights(stats, variant),
        custom_filter=custom_filter,
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    if secondary_attack is not None:
        stats = secondary_attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


GolemTemplate: CreatureTemplate = CreatureTemplate(
    name="Golem",
    tag_line="Constructed Servants",
    description="Golems are magically animated constructs of great strength and durability. They are typically created to serve as guardians, servants, or protectors.",
    environments=[],
    treasure=[],
    variants=[
        StoneVariant,
        ClayVariant,
        IronVariant,
        FleshVariant,
        IceVariant,
        ShieldGuardianVariant,
    ],
    species=[],
    callback=generate_golem,
)
