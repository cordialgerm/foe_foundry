from foe_foundry.environs import Affinity, Biome, Development, Terrain, region
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import HideArmor, UnholyArmor
from ...attack_template import AttackTemplate, natural, spell, weapon
from ...creature_types import CreatureType
from ...damage import DamageType
from ...movement import Movement
from ...powers import (
    PowerSelection,
)
from ...role_types import MonsterRole
from ...size import Size
from ...skills import AbilityScore, StatScaling
from ...spells import CasterType
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

OgreVariant = MonsterVariant(
    name="Ogre",
    description="Ogres are massive and brutish ravagers. Their hunger and anger is matched only by their strength and stupidity.",
    monsters=[
        Monster(
            name="Ogre",
            cr=2,
            srd_creatures=["Ogre"],
        )
    ],
)

OgreWallsmashaVariant = MonsterVariant(
    name="Ogre Wallsmasha",
    description="Ogres occasionally uproot whole trees and fashion them into crude battering rams that can smash through walls and anything else dumb enough to get in the way.",
    monsters=[
        Monster(
            name="Ogre Wallsmasha",
            cr=4,
            other_creatures={"Ogre Battering Ram": "motm"},
        )
    ],
)

OgreBurnbelchaVariant = MonsterVariant(
    name="Ogre Burnbelcha",
    description="Some ogres ritually imbibe a horrendous and highly flammable concoction that they belch on unsuspecting foes.",
    monsters=[
        Monster(
            name="Ogre Burnbelcha",
            cr=4,
        )
    ],
)

OgreChaincrakkaVariant = MonsterVariant(
    name="Ogre Chaincrakka",
    description="Chaincrakka ogres wield deadly whips and vicious barbed nets to capture prey for the cooking pots.",
    monsters=[
        Monster(
            name="Ogre Chaincrakka",
            cr=4,
            other_creatures={"Ogre Chain Brute": "motm"},
        )
    ],
)

OgreBigBrainzVariant = MonsterVariant(
    name="Ogre Big Brainz",
    description="Ogre magi are rare freaks among their brutish kin, born with wicked cunning and gifted with dark, unnatural powers.",
    monsters=[
        Monster(
            name="Ogre Big Brainz",
            cr=7,
            srd_creatures=["Oni"],
        )
    ],
)


class _OgreTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.variant is OgreVariant:
            return PowerSelection(powers.LoadoutOgreBase)
        elif settings.variant is OgreBigBrainzVariant:
            return PowerSelection(powers.LoadoutTrickster)
        elif settings.variant is OgreWallsmashaVariant:
            return PowerSelection(powers.LoadoutSmasha)
        elif settings.variant is OgreBurnbelchaVariant:
            return PowerSelection(powers.LoadoutBelcha)
        elif settings.variant is OgreChaincrakkaVariant:
            return PowerSelection(powers.LoadoutChainCrakka)
        else:
            raise ValueError(f"Unknown ogre variant: {settings.variant}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        variant = settings.variant

        # STATS

        if variant is OgreBigBrainzVariant:
            hp_multiplier = 1.0
            dmg_multiplier = 1.0
            attrs = {
                AbilityScore.STR: (StatScaling.Medium, 5),
                AbilityScore.DEX: (StatScaling.Default, -2),
                AbilityScore.CON: (StatScaling.Constitution, 2),
                AbilityScore.INT: (StatScaling.Primary, 0),
                AbilityScore.WIS: (StatScaling.Medium, -2),
                AbilityScore.CHA: (StatScaling.Medium, 0),
            }
        else:
            hp_multiplier = 1.2
            dmg_multiplier = 1.0
            attrs = {
                AbilityScore.STR: (StatScaling.Primary, 3 if cr <= 3 else 1),
                AbilityScore.DEX: (StatScaling.Default, -2),
                AbilityScore.CON: (StatScaling.Constitution, 2),
                AbilityScore.INT: (StatScaling.NoScaling, -5),
                AbilityScore.WIS: (StatScaling.NoScaling, -3),
                AbilityScore.CHA: (StatScaling.NoScaling, -3),
            }

        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=attrs,
            hp_multiplier=hp_multiplier * settings.hp_multiplier,
            damage_multiplier=dmg_multiplier * settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Giant,
            size=Size.Large,
            languages=["Common"],
            creature_class="Ogre",
        )

        # SPEED
        if variant is OgreBigBrainzVariant:
            stats = stats.copy(speed=Movement(walk=30, fly=30, hover=True))

        # ARMOR CLASS
        if variant is OgreBigBrainzVariant:
            stats = stats.add_ac_template(UnholyArmor)
        else:
            stats = stats.add_ac_template(HideArmor)

        # SPELLCASTING
        if variant is OgreBigBrainzVariant:
            stats = stats.grant_spellcasting(caster_type=CasterType.Arcane)

        # ATTACKS
        if variant is OgreBigBrainzVariant:
            attack = spell.Gaze.with_display_name("Nightmare Shards")
            secondary_attack = natural.Claw.with_display_name("Cursed Grasp").copy(
                damage_scalar=0.9
            )
            secondary_damage_type = DamageType.Psychic
        else:
            attack = weapon.Maul.with_display_name("Bonebreaker Club").copy(reach=10)
            secondary_damage_type = None
            secondary_attack = None

        stats = stats.copy(secondary_damage_type=secondary_damage_type)

        if stats.cr <= 3:
            stats = stats.with_set_attacks(multiattack=1)

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Bruiser
            if variant is not OgreBigBrainzVariant
            else MonsterRole.Artillery
        )

        # SAVES
        if cr >= 4 and variant is not OgreBigBrainzVariant:
            stats = stats.grant_save_proficiency(AbilityScore.STR, AbilityScore.CON)
        elif variant is OgreBigBrainzVariant:
            stats = stats.grant_save_proficiency(
                AbilityScore.CON, AbilityScore.WIS, AbilityScore.CHA
            )

        return stats, [attack, secondary_attack] if secondary_attack else [attack]


OgreTemplate: MonsterTemplate = _OgreTemplate(
    name="Ogre",
    tag_line="Hungry hulking brutes and oafs",
    description="Ogres are massive and brutish ravagers that are constantly hungry and angry.",
    treasure=[],
    variants=[
        OgreVariant,
        OgreWallsmashaVariant,
        OgreBurnbelchaVariant,
        OgreChaincrakkaVariant,
        OgreBigBrainzVariant,
    ],
    species=[],
    environments=[
        (
            region.WartornKingdom,
            Affinity.native,
        ),  # Ogres often inhabit war-torn regions
        (Terrain.hill, Affinity.native),  # Hinterland hills where ogre clans dwell
        (Biome.underground, Affinity.native),  # Cave systems and underground lairs
        (Development.wilderness, Affinity.common),  # Wild areas away from civilization
        (
            Terrain.mountain,
            Affinity.common,
        ),  # Mountainous regions with caves and passes
        (Development.frontier, Affinity.common),  # Remote settlements they raid
        (Biome.forest, Affinity.uncommon),  # Wooded areas where they might hunt
        (
            Development.countryside,
            Affinity.uncommon,
        ),  # Rural areas they occasionally attack
        (
            Development.settlement,
            Affinity.rare,
        ),  # Towns they might raid for food and treasure
    ],
)
