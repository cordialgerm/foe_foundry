from foe_foundry.powers.selection.custom import CustomPowerWeight

from ..ac_templates import HideArmor, UnholyArmor
from ..attack_template import natural, spell, weapon
from ..creature_types import CreatureType
from ..damage import DamageType
from ..movement import Movement
from ..powers import LOW_POWER, CustomPowerSelection, Power, select_powers
from ..powers.creature import ogre
from ..powers.creature_type import giant
from ..powers.roles import bruiser
from ..powers.spellcaster import shaman
from ..powers.themed import (
    clever,
    cruel,
    cursed,
    fearsome,
    illusory,
    reckless,
    technique,
    thuggish,
    totemic,
)
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Stats, StatScaling
from ..spells import CasterType
from ._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from .base_stats import base_stats

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


class _OgrePowers(CustomPowerSelection):
    def __init__(self, variant: MonsterVariant):
        self.variant = variant

        suppress = (
            ogre.OgrePowers + giant.GiantPowers + [cruel.BloodiedFrenzy]
        )  # these will be hard coded via force

        if variant is OgreBigBrainzVariant:
            general = [
                technique.FrighteningAttack,
                fearsome.FearsomeRoar,
                cursed.RayOfEnfeeblement,
                cursed.CurseOfVengeance,
                clever.IdentifyWeaknes,
                totemic.SpiritChainsTotem,
                totemic.GuardianTotem,
                illusory.PhantomMirage,
            ]
        else:
            general = [
                giant.BigWindup,
                giant.GrabAndGo,
                bruiser.CleavingBlows,
                bruiser.StunningBlow,
                technique.ProneAttack,
                technique.PushingAttack,
                technique.CleavingAttack,
                technique.GrazingAttack,
                technique.DazingAttacks,
                reckless.Toss,
                reckless.Charger,
                reckless.Overrun,
                fearsome.FearsomeRoar,
                reckless.Reckless,
                reckless.WildCleave,
                reckless.RecklessFlurry,
                thuggish.KickTheLickspittle,
                cruel.BrutalCritical,
            ]

        self.general = general

        suppress = set(suppress) - set(general)
        self.suppress = suppress

        if variant is OgreWallsmashaVariant:
            force = [ogre.Wallsmash]
        elif variant is OgreBurnbelchaVariant:
            force = [ogre.Burnbelch]
        elif variant is OgreChaincrakkaVariant:
            force = [ogre.ChainCrack]
        elif variant is OgreBigBrainzVariant:
            force = [shaman.OniTrickster]
        else:
            force = []

        self.force = force

    def custom_weight(self, power: Power) -> CustomPowerWeight:
        if power in self.suppress:
            return CustomPowerWeight(-1, ignore_usual_requirements=True)
        elif power in self.general:
            return CustomPowerWeight(1.75, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(0.25, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        return self.force

    def power_delta(self) -> float:
        return LOW_POWER - 0.2 * sum(p.power_level for p in self.force_powers())


def generate_ogre(settings: GenerationSettings) -> StatsBeingGenerated:
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

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    if secondary_attack is not None:
        stats = secondary_attack.add_as_secondary_attack(stats)
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

    # DC
    stats = stats.copy(
        difficulty_class_modifier=-1
    )  # ogres have high primary stat so don't want DCs to be too high

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_OgrePowers(variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    if secondary_attack is not None:
        stats = secondary_attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


OgreTemplate: MonsterTemplate = MonsterTemplate(
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
    callback=generate_ogre,
)
