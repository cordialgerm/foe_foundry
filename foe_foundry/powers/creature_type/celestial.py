from datetime import datetime
from math import ceil
from typing import List

from ...creature_types import CreatureType
from ...damage import Condition, DamageType, Dazed
from ...die import Die
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


class CelestialPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(require_types=CreatureType.Celestial, **score_args)

        super().__init__(
            name=name,
            power_type=PowerType.CreatureType,
            power_level=power_level,
            create_date=create_date,
            source=source,
            theme="Celestial",
            reference_statblock="Deva",
            score_args=standard_score_args,
        )


class _AbsoluteConviction(CelestialPower):
    def __init__(self):
        super().__init__(
            name="Absolute Conviction",
            source="Foe Foundry",
            create_date=datetime(2023, 11, 21),
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        temphp = easy_multiple_of_five(3 * stats.cr)
        feature = Feature(
            name="Absolute Conviction",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} is targeted by a spell or effect that would cause it to make a Wisdom, Intelligence, or Charisma saving throw, \
                it automatically succeeds. It then gains {temphp} temporary hit points",
        )
        return [feature]


class _HealingTouch(CelestialPower):
    def __init__(self):
        super().__init__(name="Healing Touch", source="SRD5.1 Deva")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        hp = easy_multiple_of_five(int(ceil(max(5, 2 * stats.cr))))

        feature = Feature(
            name="Healing Touch",
            action=ActionType.Action,
            replaces_multiattack=1,
            uses=3,
            description=f"{stats.selfref.capitalize()} touches another creature. It magically regains {hp} hp and is freed from any curse, disease, poison, blindness, or deafness",
        )

        return [feature]


class _RighteousJudgement(CelestialPower):
    def __init__(self):
        super().__init__(
            name="Righteous Judgement",
            source="Foe Foundry",
            bonus_damage=DamageType.Radiant,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(target=1.5, force_die=Die.d6)
        blinded = Condition.Blinded

        feature = Feature(
            name="Righteous Judgment",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} targets a creature it can see within 60 feet. If the target can hear {stats.selfref}, it must make a DC {dc} Charisma save. \
                On a failure, it takes {dmg.description} radiant damage and is {blinded.caption} until the end of its next turn. On a success, it takes half as much damage. \
                {stats.selfref.capitalize()} can also choose another friendly creature within 60 feet to gain temporary hp equal to the radiant damage dealt.",
        )

        return [feature]


class _DivineLaw(CelestialPower):
    def __init__(self):
        super().__init__(
            name="Divine Law",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            require_cr=7,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(target=1.25, force_die=Die.d6)
        blinded = Condition.Blinded
        stunned = Condition.Stunned

        feature = Feature(
            name="Divine Law",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} pronounces a divine law. \
                Each humanoid creature within 60 feet that can hear {stats.selfref} must make DC {dc} Charisma saving throw. \
                A creature that worships the same deity or follows the same precepts as {stats.selfref} automatically fails this save. \
                On a failure, the creature is bound by the divine law for 24 hours. On a success, the creature is immune to this effect for 24 hours. \
                At the start of each of its turns, the affected creature may choose to break the divine law. If it does so, it suffers {dmg.description} radiant damage and may repeat the save to end the effect.  \
                The game master may choose an appropriate divine law, or roll a d6 and select one of the following:   \
                <ol> \
                <li>**Tranquility**: Affected creatures immediately end concentrating on any spells or abilities and may not cast a new spell that requires concentration.</li>\
                <li>**Peace**: Affected creatures may not wield weapons of a specified type. </li>\
                <li>**Forbiddance**: Affected creatures may not cast spells from a specified school of magic. </li>\
                <li>**Awe**: Affected creatures may not look upon {stats.selfref} or any Celestial beings and are {blinded.caption} while within 60 feet of {stats.selfref} or a Celestial. </li>\
                <li>**Adherance**: Affected creatures cannot take hostile actions towards creatures of a specified alignment</li>\
                <li>**Repentance**: Affected creatures must confess their darkest or most shameful transgressions or become {stunned.caption} for 1 minute. </li>\
                </ol>",
        )
        return [feature]


class _DivineMercy(CelestialPower):
    def __init__(self):
        super().__init__(
            name="Divine Mercy",
            source="Foe Foundry",
            create_date=datetime(2023, 11, 21),
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        healing = easy_multiple_of_five(4 * stats.cr)
        charmed = Condition.Charmed

        feature = Feature(
            name="Divine Mercy",
            action=ActionType.Reaction,
            description=f"Whenever a creature that is within 60 feet of {stats.selfref} that can see or hear it is hit by an attack, fails a saving throw, or is reduced to 0 hitpoints, \
                {stats.selfref} may offer divine mercy to that creature. If the creature accepts, it heals {healing} hitpoints and {stats.selfref} may choose to end any negative conditions affecting that creature. \
                The creature becomes {charmed.caption} by {stats.selfref} and follows its instructions to the best of its ability. \
                Whenever the creature completes a long rest, it may make a DC {dc} Charisma saving throw. On a success, the creature is no longer charmed. \
                After three failures, the creature is permanently charmed and its alignment changes to match {stats.selfref}",
        )

        return [feature]


class _WordsOfRighteousness(CelestialPower):
    def __init__(self):
        super().__init__(
            name="Words of Righteousness",
            source="Foe Foundry",
            bonus_damage=DamageType.Radiant,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        damage = stats.target_value(target=1.25, suggested_die=Die.d6)
        dazed = Dazed()
        dc = stats.difficulty_class_easy
        distance = easy_multiple_of_five(6 * stats.cr, min_val=20, max_val=60)

        feature = Feature(
            name="Words of Righteousness",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} speaks words of utter righteousness. Each creature of {stats.selfref}'s choice within {distance} feet \
                that can hear it must make a DC {dc} Charisma saving throw. On a failure, the target takes {damage.description} radiant damage and is {dazed.caption}. \
                The DM may decide that a creature has advantage or disadvantage on this save based on its actions and alignment. {dazed.description_3rd}",
        )

        return [feature]


class _AweInspiringGaze(CelestialPower):
    def __init__(self):
        super().__init__(
            name="Awe-Inspiring Gaze",
            source="A5E SRD Planetar",
            power_level=HIGH_POWER,
            create_date=datetime(2023, 11, 22),
            require_cr=7,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        frightened = Condition.Frightened
        feature = Feature(
            name="Awe-Inspiring Gaze",
            action=ActionType.Reaction,
            description=f"When a creature within 90 feet looks at {stats.selfref} it must make a DC {dc} Wisdom saving throw. \
                On a failure, it is {frightened.caption} until the end of its next turn. On a success, it is immune to Awes-Inspiring Gaze for the next 24 hours.",
        )
        return [feature]


AbsoluteConviction: Power = _AbsoluteConviction()
AweInspiringGaze: Power = _AweInspiringGaze()
DivineLaw: Power = _DivineLaw()
DivineMercy: Power = _DivineMercy()
HealingTouch: Power = _HealingTouch()
RighteousJudgement: Power = _RighteousJudgement()
WordsOfRighteousness: Power = _WordsOfRighteousness()

CelestialPowers: List[Power] = [
    AbsoluteConviction,
    AweInspiringGaze,
    DivineLaw,
    DivineMercy,
    HealingTouch,
    RighteousJudgement,
    WordsOfRighteousness,
]
