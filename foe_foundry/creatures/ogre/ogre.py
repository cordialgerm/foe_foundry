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
from ...skills import Stats, StatScaling
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
        rng = settings.rng

        # STATS

        if variant is OgreBigBrainzVariant:
            hp_multiplier = 1.0
            dmg_multiplier = 1.0
            stats = [
                Stats.STR.scaler(StatScaling.Medium, mod=5),
                Stats.DEX.scaler(StatScaling.Default, -2),
                Stats.CON.scaler(StatScaling.Constitution, 2),
                Stats.INT.scaler(StatScaling.Primary),
                Stats.WIS.scaler(StatScaling.Medium, mod=-2),
                Stats.CHA.scaler(StatScaling.Medium),
            ]
        else:
            hp_multiplier = 1.2
            dmg_multiplier = 1.0
            stats = [
                Stats.STR.scaler(StatScaling.Primary, mod=3 if cr <= 3 else 1),
                Stats.DEX.scaler(StatScaling.Default, -2),
                Stats.CON.scaler(StatScaling.Constitution, 2),
                Stats.INT.scaler(StatScaling.NoScaling, mod=-5),
                Stats.WIS.scaler(StatScaling.NoScaling, mod=-3),
                Stats.CHA.scaler(StatScaling.NoScaling, mod=-3),
            ]

        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=stats,
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
            stats = stats.grant_save_proficiency(Stats.STR, Stats.CON)
        elif variant is OgreBigBrainzVariant:
            stats = stats.grant_save_proficiency(Stats.CON, Stats.WIS, Stats.CHA)

        return stats, [attack, secondary_attack] if secondary_attack else [attack]


OgreTemplate: MonsterTemplate = _OgreTemplate(
    name="Ogre",
    tag_line="Hungry hulking brutes and oafs",
    description="Ogres are massive and brutish ravagers that are constantly hungry and angry.",
    environments=[
        "Arctic",
        "Desert",
        "Forest",
        "Grassland",
        "Hill",
        "Swamp",
        "Underdark",
    ],
    treasure=[],
    variants=[
        OgreVariant,
        OgreWallsmashaVariant,
        OgreBurnbelchaVariant,
        OgreChaincrakkaVariant,
        OgreBigBrainzVariant,
    ],
    species=[],
)
