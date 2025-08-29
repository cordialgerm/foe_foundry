from foe_foundry.environs import Affinity, Development, region

from ...ac_templates import PlateArmor
from ...attack_template import AttackTemplate, natural, weapon
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...movement import Movement
from ...powers import (
    PowerSelection,
)
from ...role_types import MonsterRole
from ...size import Size
from ...skills import AbilityScore, StatScaling
from ...statblocks import BaseStatblock
from .._data import (
    GenerationSettings,
    Monster,
    MonsterVariant,
)
from .._template import MonsterTemplate
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


class _AnimatedArmorTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == 'animated-armor':
            return PowerSelection(powers.LoadoutAnimatedArmor)
        elif settings.monster_key == 'animated-runeplate':
            return PowerSelection(powers.LoadoutRunicSpellplate)
        else:
            raise ValueError(f"Unknown monster_key: {settings.monster_key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        variant = settings.variant

        # STATS
        if variant is AnimatedArmorVariant:
            attrs = {
                AbilityScore.STR: (StatScaling.Primary, 1),
                AbilityScore.DEX: StatScaling.Medium,
                AbilityScore.CON: (StatScaling.Constitution, 2),
                AbilityScore.INT: (StatScaling.NoScaling, -9),
                AbilityScore.WIS: (StatScaling.NoScaling, -7),
                AbilityScore.CHA: (StatScaling.NoScaling, -9),
            }
            hp_multiplier = 1.0
            damage_multiplier = 1.0
        elif variant is RunicSpellplateVariant:
            attrs = {
                AbilityScore.STR: StatScaling.Primary,
                AbilityScore.DEX: StatScaling.Medium,
                AbilityScore.CON: (StatScaling.Constitution, 2),
                AbilityScore.INT: (StatScaling.NoScaling, 0),
                AbilityScore.WIS: (StatScaling.NoScaling, 0),
                AbilityScore.CHA: (StatScaling.NoScaling, 0),
            }
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
        if variant is RunicSpellplateVariant:
            stats = stats.copy(speed=Movement(walk=30, fly=30, hover=True))

        # ARMOR CLASS
        stats = stats.add_ac_template(PlateArmor)

        if variant is RunicSpellplateVariant:
            attack = weapon.SwordAndShield.with_display_name("Runic Blade")
            secondary_damage_type = DamageType.Force
        else:
            attack = natural.Slam.with_display_name("Plated Gauntlet")
            secondary_damage_type = None

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
        return stats, [attack]


AnimatedArmorTemplate: MonsterTemplate = _AnimatedArmorTemplate(
    name="Animated Armor",
    tag_line="Mage-Wrought Animated Guardians",
    description="Animated Armor are constructed suits of armor that have been magically animated to serve as a guardian or protector. It is typically made of metal and has a humanoid shape.",
    treasure=[],
    environments=[
        (
            Development.stronghold,
            Affinity.native,
        ),  # created to guard fortified locations
        (
            Development.ruin,
            Affinity.common,
        ),  # found in ancient magical ruins and towers
        (region.UrbanTownship, Affinity.common),  # created by urban mages as guardians
        (
            Development.settlement,
            Affinity.uncommon,
        ),  # occasionally guard important buildings
        (Development.dungeon, Affinity.uncommon),  # sometimes found in magical dungeons
        (Development.wilderness, Affinity.rare),  # rarely found outside civilized areas
    ],
    variants=[AnimatedArmorVariant, RunicSpellplateVariant],
    species=[],
)
