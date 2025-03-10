from datetime import datetime
from typing import List

from foe_foundry.references import creature_ref

from ...attributes import Stats
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


def as_psychic_fey(stats: BaseStatblock) -> BaseStatblock:
    if stats.secondary_damage_type is None:
        stats = stats.copy(secondary_damage_type=DamageType.Psychic)

    return stats


def as_cursed_fey(stats: BaseStatblock) -> BaseStatblock:
    if stats.secondary_damage_type is None:
        stats = stats.copy(secondary_damage_type=DamageType.Necrotic)

    return stats


class FeyPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(require_types=CreatureType.Fey, **score_args)
        super().__init__(
            name=name,
            source=source,
            power_type=PowerType.CreatureType,
            power_level=power_level,
            create_date=create_date,
            score_args=standard_score_args,
            theme="Fey",
        )


class _FaerieStep(FeyPower):
    def __init__(self):
        super().__init__(
            name="Faerie Step",
            source="A5ESRD Fey Noble",
            create_date=datetime(2023, 11, 21),
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        distance = stats.speed.walk
        feature = Feature(
            name="Faerie Step",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} teleports up to {distance} feet to an unoccupied space they can see.",
        )
        return [feature]


class _FaePresence(FeyPower):
    def __init__(self):
        super().__init__(
            name="Fae Presence",
            source="Foe Foundry",
            create_date=datetime(2023, 11, 21),
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return as_psychic_fey(stats)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        charmed = Condition.Charmed
        feature = Feature(
            name="Fae Presence",
            action=ActionType.Feature,
            description=f"An enemy of {stats.selfref} that starts their turn within 25 feet of {stats.selfref} must succeed on a DC {dc} Wisdom saving throw or be {charmed.caption} by {stats.selfref} until the end of their turn.",
        )
        return [feature]


class _BloodContract(FeyPower):
    def __init__(self):
        super().__init__(
            name="Blood Curse",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            create_date=datetime(2023, 11, 21),
            bonus_damage=DamageType.Necrotic,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return as_cursed_fey(stats)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(1.5, suggested_die=Die.d8)
        healing = easy_multiple_of_five(dmg.average, min_val=5, max_val=45)
        dc = stats.difficulty_class

        feature = Feature(
            name="Blood Curse",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} curses the blood of its opponents, siphoning their life to heal its its wounds. {stats.selfref.capitalize()} targets up to three creatures it can see within 60 feet of itself. \
                Each target must make a DC {dc} Constitution saving throw, taking {dmg.description} necrotic damage on a failed save, or half as much damage on a successful one. \
                {stats.selfref.capitalize()} then regains {healing} hit points.",
        )
        return [feature]


class _FaeCounterspell(FeyPower):
    def __init__(self):
        super().__init__(
            name="Fae Counterspell",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            require_stats=Stats.INT,
            bonus_damage=DamageType.Psychic,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return as_psychic_fey(stats)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(0.75, suggested_die=Die.d6)
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Fae Counterspell",
            action=ActionType.Reaction,
            description=f"{stats.selfref.capitalize()} attempts to interrupt a creature it can see within 60 feet \
                that is casting a spell with verbal, somatic, or material components. \
                The caster takes {dmg.description} psychic damage and must make a DC {dc} Charisma saving throw. \
                On a failed save, the spell fails and has no effect, but the casting creature is immune to this effect for 24 hours.",
        )
        return [feature]


class _Awaken(FeyPower):
    def __init__(self):
        super().__init__(
            name="Awaken", source="Foe Foundry", power_level=HIGH_POWER, require_cr=4
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        if stats.cr >= 5:
            creature = creature_ref("Awakened Tree")
            formula = DieFormula.target_value(1 + stats.cr / 4, force_die=Die.d4)
        else:
            creature = creature_ref("Awakened Shrub")
            formula = DieFormula.target_value(3 + 4 * stats.cr, force_die=Die.d4)

        feature = Feature(
            name="Awaken",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} magically awakens {formula.description} {creature}. They act in initiative immediately after {stats.selfref} and obey its verbal commands (no action required).",
        )
        return [feature]


class _FaeBargain(FeyPower):
    def __init__(self):
        super().__init__(
            name="Fae Bargain",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            require_cr=4,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return as_psychic_fey(stats)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        uncommon = 10
        rare = 20
        very_rare = 40
        legendary = 80
        artifact = 160
        dc = stats.difficulty_class

        feature = Feature(
            name="Fae Bargain",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=3,
            description=f"{stats.selfref.capitalize()} magically bargains with a creature it can see within 60 feet. The creature must make a DC {dc} Charisma save. \
                On a failure, the highest rarity magical item in that creature's possession becomes cursed and loses all magical powers and abilities and acts as a mundane item of the corresponding type. \
                {stats.selfref.capitalize()} then gains temporary hitpoints based on the rarity of the magical item: {uncommon} for an uncommon item, {rare} for a rare item, {very_rare} for a very rare item, \
                {legendary} for a legendary item and {artifact} for an artifact. This curse lasts until the fae verbally renounces the bargain, the fae is destroyed, or the curse is removed via *Remove Curse* or similar effect.",
        )
        return [feature]


class _DanceTune(FeyPower):
    def __init__(self):
        super().__init__(
            name="Dance Tune",
            source="A5ESRD Satyr",
            create_date=datetime(2023, 11, 21),
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Dance Tune",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} plays a dance tune. Each humanoid, fey, or giant within 30 feet that can hear {stats.selfref} must make a DC {dc} Wisdom saving throw. \
                On a failure, it is magically charmed and must dance until the beginning of {stats.selfref}'s next turn. While dancing, its movement speed is halved, and it has disadvantage on attack rolls. \
                Fey don't suffer the negative consequences of dancing.",
        )
        return [feature]


class _ShadowyDoppelganger(FeyPower):
    def __init__(self):
        super().__init__(
            name="Shadowy Doppelganger", source="Foe Foundry", power_level=HIGH_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        hp = easy_multiple_of_five(1.25 * stats.cr, min_val=5)

        feature = Feature(
            name="Shadowy Doppleganger",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} forces each non-fey creature of its choice within 30 feet to make a DC {dc} Charisma saving throw. \
                On a failure, a Shadow Doppleganger copy of that creature materializes in the nearest unoccupied space to that creature and acts in initiative immediately after {stats.selfref}. \
                The Shadow Doppleganger has {hp} hp and has an AC equal to the creature it was copied from and is a Fey. On its turn, the Shadow Doppleganger attempts to move and attack the creature it was copied from. \
                It makes a single attack using the stats of {stats.selfref}'s Attack action. It otherwise has the movement, stats, skills, and saves of the creature it was copied from.",
        )
        return [feature]


Awaken: Power = _Awaken()
BloodContract: Power = _BloodContract()
DanceTune: Power = _DanceTune()
FaeBargain: Power = _FaeBargain()
FaeCounterspell: Power = _FaeCounterspell()
FaePresence: Power = _FaePresence()
FaeryStep: Power = _FaerieStep()
ShadowyDoppelganger: Power = _ShadowyDoppelganger()

FeyPowers: List[Power] = [
    Awaken,
    BloodContract,
    FaeBargain,
    FaeCounterspell,
    FaePresence,
    FaeryStep,
    ShadowyDoppelganger,
]
