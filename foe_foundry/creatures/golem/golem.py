from foe_foundry.environs import Affinity, Development
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import NaturalPlating, Unarmored
from ...attack_template import AttackTemplate, natural, spell
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...powers import (
    PowerSelection,
)
from ...role_types import MonsterRole
from ...size import Size
from ...skills import AbilityScore, StatScaling
from ...statblocks import MonsterDials
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

StoneVariant = MonsterVariant(
    name="Stone Golem",
    description="Stone golems take varied forms, such as weathered carvings of ancient deities, lifelike sculptures of heroes, or any other shape their makers imagine. No matter their design or the rock from which they’re crafted, these golems are strengthened by the magic that animates them, allowing them to follow their creators' orders for centuries.",
    monsters=[
        Monster(
            name="Stone Golem",
            cr=10,
            srd_creatures=["Stone Golem"],
        )
    ],
)
ClayVariant = MonsterVariant(
    name="Clay Golem",
    description="TODO",
    monsters=[
        Monster(
            name="Clay Golem",
            cr=9,
            srd_creatures=["Clay Golem"],
        )
    ],
)
IronVariant = MonsterVariant(
    name="Iron Golem",
    description="Their magical cores protected by mighty armor, iron golems defend important sites and objects. These golems are forged in bipedal forms, the details of which are decided by their creators. Many resemble armored guardians or legendary heroes. Iron golems confront their foes with a combination of overwhelming physical force and eruptions from their magical core. These magical blasts take the form of fiery bolts and poisonous emissions.",
    monsters=[
        Monster(
            name="Iron Golem",
            cr=16,
            srd_creatures=["Iron Golem"],
        )
    ],
)
FleshVariant = MonsterVariant(
    name="Flesh Golem",
    description="Flesh golems are roughly human-shaped collections of body parts bound together by misused magic or strange science. They serve their reckless creators, but many possess disjointed memories and instincts from their component parts. If wounded, these golems might go berserk and vent their confusion on anything in their sight, including their creators.",
    monsters=[
        Monster(
            name="Flesh Golem",
            cr=5,
            srd_creatures=["Flesh Golem"],
        )
    ],
)
IceVariant = MonsterVariant(
    name="Ice Golem",
    description="Ice golems are crafted from magically frozen cores specially prepared by their creators. These golems are often used to guard remote locations or to serve as sentinels in icy realms. Their bodies are sculpted from ice and snow, and their creators can imbue them with a variety of powers, such as the ability to freeze foes or to create blizzards.",
    monsters=[Monster(name="Ice Golem", cr=7)],
)
ShieldGuardianVariant = MonsterVariant(
    name="Shield Guardian",
    description="A shield guardian's primary goal is to protect its master. It escorts whoever bears its command amulet and intercedes between the bearer and any threat. Although it isn’t mindless, a shield guardian has no sense of self preservation and will sacrifice itself to protect its master.",
    monsters=[
        Monster(
            name="Shield Guardian",
            cr=7,
            srd_creatures=["Shield Guardian"],
        )
    ],
)


class _GolemTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.variant is ShieldGuardianVariant:
            return PowerSelection(powers.LoadoutShieldGuardian)
        elif settings.variant is StoneVariant:
            return PowerSelection(powers.LoadoutStoneGolem)
        elif settings.variant is ClayVariant:
            return PowerSelection(powers.LoadoutClayGolem)
        elif settings.variant is FleshVariant:
            return PowerSelection(powers.LoadoutFleshGolem)
        elif settings.variant is IronVariant:
            return PowerSelection(powers.LoadoutIronGolem)
        elif settings.variant is IceVariant:
            return PowerSelection(powers.LoadoutIceGolem)
        else:
            raise ValueError(f"Unknown golem variant: {settings.variant.key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        variant = settings.variant

        # STATS

        if variant is not FleshVariant:
            attrs = {
                AbilityScore.STR: StatScaling.Primary,
                AbilityScore.DEX: (StatScaling.NoScaling, -2),
                AbilityScore.CON: (StatScaling.Constitution, 2),
                AbilityScore.INT: (StatScaling.NoScaling, -7),
                AbilityScore.WIS: (StatScaling.Default, -2.5),
                AbilityScore.CHA: (StatScaling.NoScaling, -9),
            }
        else:
            attrs = {
                AbilityScore.STR: StatScaling.Primary,
                AbilityScore.DEX: (StatScaling.NoScaling, -2),
                AbilityScore.CON: (StatScaling.Constitution, 2),
                AbilityScore.INT: (StatScaling.NoScaling, -3),
                AbilityScore.WIS: (StatScaling.Default, -2.5),
                AbilityScore.CHA: (StatScaling.NoScaling, -4),
            }

        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=attrs,
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

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
            secondary_attack = spell.Frostbolt.with_display_name("Ice Shards").copy(
                damage_scalar=0.85
            )
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
            secondary_attack = spell.Firebolt.with_display_name("Fiery Beams").copy(
                damage_scalar=0.9
            )
            secondary_damage_type = DamageType.Fire
        elif variant is ClayVariant:
            attack = natural.Slam.with_display_name("Dissolving Fist")
            secondary_attack = None
            secondary_damage_type = DamageType.Acid
        elif variant is StoneVariant:
            attack = natural.Slam
            secondary_attack = spell.ArcaneBurst.with_display_name(
                "Core Eruption"
            ).copy(damage_scalar=0.85)
            secondary_damage_type = DamageType.Force

        stats = stats.copy(
            secondary_damage_type=secondary_damage_type,
        )
        if secondary_attack is not None:
            secondary_attack = secondary_attack.copy(damage_scalar=0.9)

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
            primary_role=MonsterRole.Defender, additional_roles=[MonsterRole.Soldier]
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
            stats = stats.grant_resistance_or_immunity(
                immunities={secondary_damage_type}
            )

        return stats, [attack, secondary_attack] if secondary_attack else [attack]


GolemTemplate: MonsterTemplate = _GolemTemplate(
    name="Golem",
    tag_line="Constructed Servants",
    description="Golems are magically animated constructs of great strength and durability. They are typically created to serve as guardians, servants, or protectors.",
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
    environments=[
        (
            Development.dungeon,
            Affinity.native,
        ),  # Underground complexes and magical laboratories
        (
            Development.stronghold,
            Affinity.native,
        ),  # Fortified areas they were created to protect
        (
            Development.ruin,
            Affinity.common,
        ),  # Ancient temples, tombs, and abandoned sites
        (
            Development.urban,
            Affinity.uncommon,
        ),  # Cities where powerful wizards create them
        (
            Development.settlement,
            Affinity.rare,
        ),  # Settlements with magical practitioners
    ],
)
