from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class FearsomePower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            power_type=PowerType.Theme,
            theme="fearsome",
            create_date=create_date,
            power_level=power_level,
            score_args=dict(
                require_types={
                    CreatureType.Dragon,
                    CreatureType.Fiend,
                    CreatureType.Monstrosity,
                    CreatureType.Beast,
                },
                require_cr=1,
                bonus_cr=7,
                **score_args,
            ),
        )


class HorrifyingPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            power_type=PowerType.Theme,
            theme="fearsome",
            create_date=create_date,
            power_level=power_level,
            score_args=dict(
                require_types=[CreatureType.Aberration, CreatureType.Undead],
                require_cr=1,
                bonus_cr=7,
                bonus_damage=DamageType.Psychic,
                bonus_attack_types=AttackType.AllSpell(),
                **score_args,
            ),
        )


class _FearsomeRoar(FearsomePower):
    def __init__(self):
        super().__init__(name="Fearsome Roar", source="FoeFoundryOriginal")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Fearsome Roar",
            description=f"{stats.selfref.capitalize()} targets up to eight creatures they can see within 60 ft. Each must make a DC {dc} Charisma saving throw.\
                On a failure, the affected target is **Frightened** for 1 minute (save ends at end of turn) and must immediately use its reaction, if available, to move their speed away from {stats.selfref} \
                avoiding hazards or dangerous terrain if possible.",
            uses=1,
            replaces_multiattack=1,
            action=ActionType.Action,
        )
        return [feature]


class _HorrifyingPresence(HorrifyingPower):
    def __init__(self):
        super().__init__(name="Horrifying Presence", source="FoeFoundryOriginal")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Horrifying Presence",
            description=f"{stats.selfref.capitalize()} targets up to eight creatures they can see within 60 ft. Each must make a DC {dc} Charisma saving throw.\
                On a failure, the affected target is **Frightened** for 1 minute (save ends at end of turn) and must immediately use its reaction, if available, to move their speed away from {stats.selfref} \
                avoiding hazards or dangerous terrain if possible.",
            uses=1,
            replaces_multiattack=1,
            action=ActionType.Action,
        )
        return [feature]


class _HorrifyingVisage(HorrifyingPower):
    def __init__(self):
        super().__init__(name="Horrifying Visage", source="SRD5.1 Ghost")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        aging = f"1d4 x {5 if stats.cr < 4 else 10} years"
        dc = stats.difficulty_class

        feature = Feature(
            name="Horrifying Visage",
            action=ActionType.Reaction,
            description=f"When a creature looks at {stats.selfref}, it must immediately make a DC {dc} Wisdom saving throw. \
                On a failure, the target is **Frightened** of {stats.selfref} (save ends at end of turn). \
                If the save fails by 5 or more, the target also ages {aging}. \
                A creature that succeeds on the save is immune to this effect for 1 hour.",
        )

        return [feature]


class _DreadGaze(HorrifyingPower):
    def __init__(self):
        super().__init__(name="Dread Gaze", source="SRD5.1 Mummy")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class

        feature = Feature(
            name="Dread Gaze",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} targets one creature it can see within 60 feet. If the target can see {stats.selfref} \
                it must succeed on a DC {dc} Wisdom save or become **Frightened** of the {stats.selfref} (save ends at end of turn). \
                If the target fails the save by 5 or more, it is also **Paralyzed** while frightened in this way. \
                A creature that succeeds on the save is immune to this effect for 1 hour.",
        )

        return [feature]


class _MindShatteringScream(HorrifyingPower):
    def __init__(self):
        super().__init__(
            name="Mind-Shattering Scream", source="SRD5.1 Banshee", power_level=HIGH_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = DieFormula.target_value(5 + 2.5 * stats.cr, force_die=Die.d6)
        dc = stats.difficulty_class

        feature = Feature(
            name="Mind-Shattering Scream",
            action=ActionType.Action,
            recharge=6,
            description=f"{stats.selfref.capitalize()} releases a mind-shattering scream. All other creatures within 30 ft that can hear {stats.selfref} \
                must make a DC {dc} Intelligence saving throw. On a failure, a creature takes {dmg.description} psychic damage and is **Stunned** until the end of its next turn. \
                On a success, a creature takes half damage and is not Stunned. Creatures that are **Frightened** have disadvantage on this save.",
        )
        return [feature]


class _NightmarishVisions(HorrifyingPower):
    def __init__(self):
        super().__init__(name="Nightmarish Visions", source="FoeFoundryOriginal")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = DieFormula.target_value(max(5, 1.5 * stats.cr), force_die=Die.d6)
        dc = stats.difficulty_class_easy
        bleeding = conditions.Bleeding(dmg, damage_type=DamageType.Psychic)
        feature = Feature(
            name="Nightmarish Visions",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=5,
            description=f"{stats.selfref.capitalize()} targets a creature that it can see within 30 feet and forces it to confront its deepest fears. \
                The target must succeed on a DC {dc} Wisdom save or become **Frightened** of {stats.selfref} for 1 minute (save ends at end of turn). \
                While frightened in this way, the creature gains {bleeding.caption}. {bleeding.description_3rd}",
        )
        return [feature]


FearsomeRoar: Power = _FearsomeRoar()
HorrifyingPresence: Power = _HorrifyingPresence()
HorrifyingVisage: Power = _HorrifyingVisage()
DreadGaze: Power = _DreadGaze()
MindShatteringScream: Power = _MindShatteringScream()
NightmarishVisions: Power = _NightmarishVisions()

FearsomePowers: List[Power] = [
    FearsomeRoar,
    HorrifyingPresence,
    HorrifyingVisage,
    DreadGaze,
    MindShatteringScream,
    NightmarishVisions,
]
