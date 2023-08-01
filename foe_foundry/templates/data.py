from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import List, Set

from num2words import num2words

from ..damage import Attack, DamageType
from ..features import ActionType, Feature
from ..skills import Skills
from ..statblocks import Statblock


@dataclass
class MonsterTemplateData:
    name: str
    size: str
    creature_type: str
    ac: str
    hp: str
    movement: str

    STR: int
    CON: int
    DEX: int
    WIS: int
    INT: int
    CHA: int

    saves: str
    skills: str
    damage_resistances: str
    damage_immunities: str
    condition_immunities: str
    senses: str
    languages: str
    challenge: str
    proficiency_bonus: str

    passives: List[Feature]
    actions: List[Feature]
    bonus_actions: List[Feature]
    reactions: List[Feature]

    multiattack: str
    attack: Attack

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_statblock(stats: Statblock) -> MonsterTemplateData:
        selfref = stats.creature_type.name

        hp = f"{stats.hp.static} ({stats.hp.dice_formula()})"
        languages = ", ".join(l for l in stats.languages) if stats.languages is not None else ""

        cr_fraction = Fraction.from_float(stats.cr).limit_denominator(10)
        cr_fraction = (
            f"{cr_fraction.numerator}"
            if cr_fraction.denominator == 1
            else f"{cr_fraction.numerator}/{cr_fraction.denominator}"
        )
        cr = f"{cr_fraction} ({stats.xp:,.0f} XP)"

        passives, actions, bonus_actions, reactions = [], [], [], []
        for feature in [f for f in stats.features if not f.hidden]:
            if feature.action == ActionType.Feature:
                passives.append(feature)
            elif feature.action == ActionType.Action:
                actions.append(feature)
            elif feature.action == ActionType.BonusAction:
                bonus_actions.append(feature)
            elif feature.action == ActionType.Reaction:
                reactions.append(feature)

        if stats.multiattack == 0:
            multiattack = ""
        else:
            multiattack = f"The {selfref} makes {num2words(stats.multiattack)} attacks"

            replace_multiattacks = [
                f
                for f in stats.features
                if f.replaces_multiattack > 0 and f.replaces_multiattack <= stats.multiattack
            ]
            lines = []
            for feature in replace_multiattacks:
                replace_attacks = f"{num2words(feature.replaces_multiattack)} attack{'s' if feature.replaces_multiattack > 1 else ''}"
                lines.append(f"{replace_attacks} with a use of its {feature.name}")
            if len(lines) > 0:
                multiattack += ". It may replace " + "or ".join(lines)

        t = MonsterTemplateData(
            name=stats.name,
            size=stats.size.name,
            creature_type=stats.creature_type.name,
            ac=stats.ac.describe(),
            hp=hp,
            movement=stats.speed.describe(),
            STR=stats.attributes.STR,
            CON=stats.attributes.CON,
            DEX=stats.attributes.DEX,
            WIS=stats.attributes.WIS,
            INT=stats.attributes.INT,
            CHA=stats.attributes.CHA,
            saves=stats.attributes.describe_saves(),
            skills=stats.attributes.describe_skills(),
            damage_resistances=_damage_list(
                stats.damage_resistances, stats.nonmagical_resistance
            ),
            damage_immunities=_damage_list(stats.damage_immunities, stats.nonmagical_immunity),
            condition_immunities=", ".join(c.name for c in stats.condition_immunities),
            senses=stats.senses.describe(stats.attributes.passive_skill(Skills.Perception)),
            languages=languages,
            challenge=cr,
            proficiency_bonus=f"+{stats.attributes.proficiency}",
            passives=passives,
            actions=actions,
            bonus_actions=bonus_actions,
            reactions=reactions,
            multiattack=multiattack,
            attack=stats.attack,
        )
        return t


def _damage_list(damage_types: Set[DamageType], nonmagical: bool) -> str:
    pieces = []
    if len(damage_types) > 0:
        pieces.append(", ".join(d.name for d in damage_types))
    if nonmagical:
        pieces.append("Bludgeoning, Piercing, and Slashing from Nonmagical Attacks")
    return "; ".join(pieces)
