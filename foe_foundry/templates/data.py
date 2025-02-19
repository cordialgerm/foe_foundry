from __future__ import annotations

from dataclasses import asdict, dataclass, field
from fractions import Fraction
from typing import List, Set

from num2words import num2words

from ..benchmarks import Benchmark
from ..damage import Attack, DamageType
from ..features import ActionType, Feature
from ..skills import Skills
from ..statblocks import Statblock
from .utilities import fix_punctuation


@dataclass
class MonsterTemplateData:
    name: str
    selfref: str
    roleref: str
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
    attacks: List[Attack]
    attack_modifiers: List[Feature]
    legendary_actions: List[Feature]

    multiattack: str
    attack: Attack

    spellcasting: str

    benchmarks: List[Benchmark] | None = None

    attack_modifier_text: str = field(init=False)
    attack_text: str = field(init=False)

    def __post_init__(self):
        self.attack_modifier_text = (
            " ".join([fix_punctuation(f.description) for f in self.attack_modifiers])
            if len(self.attack_modifiers) > 0
            else ""
        )
        if self.attack_modifier_text != "":
            self.attack_text = (
                fix_punctuation(self.attack.description)
                + " "
                + fix_punctuation(self.attack_modifier_text)
            )
        else:
            self.attack_text = fix_punctuation(self.attack.description)

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_statblock(
        stats: Statblock, benchmarks: List[Benchmark] | None = None
    ) -> MonsterTemplateData:
        hp = f"{stats.hp.static} ({stats.hp.dice_formula()})"
        languages = (
            ", ".join(l for l in stats.languages) if stats.languages is not None else ""
        )

        creature_type_additions = []
        if stats.creature_subtype:
            creature_type_additions.append(stats.creature_subtype)
        if stats.creature_class:
            creature_type_additions.append(stats.creature_class)
        creature_type_additions = ", ".join(creature_type_additions)

        creature_type = (
            f"{stats.creature_type.capitalize()} ({creature_type_additions})"
            if creature_type_additions
            else stats.creature_type.capitalize()
        )

        cr_fraction = Fraction.from_float(stats.cr).limit_denominator(10)
        cr_fraction = (
            f"{cr_fraction.numerator}"
            if cr_fraction.denominator == 1
            else f"{cr_fraction.numerator}/{cr_fraction.denominator}"
        )
        cr = f"{cr_fraction} ({stats.xp:,.0f} XP)"

        passives, actions, bonus_actions, reactions, legendary_actions = (
            [],
            [],
            [],
            [],
            [],
        )
        for feature in stats.features:
            if feature.hidden:
                continue
            if feature.action == ActionType.Feature:
                passives.append(feature)
            elif feature.action == ActionType.Action:
                actions.append(feature)
            elif feature.action == ActionType.BonusAction:
                bonus_actions.append(feature)
            elif feature.action == ActionType.Reaction:
                reactions.append(feature)
            elif feature.action == ActionType.Legendary:
                legendary_actions.append(feature)

        spellcasting = stats.spellcasting_md

        attack_modifiers = []
        for feature in stats.features:
            if feature.modifies_attack:
                attack_modifiers.append(feature)

        if stats.attack.name == "Attack":
            attack_name = "attacks"
        else:
            primary_attacks = [stats.attack]
            primary_attacks += [
                a for a in stats.additional_attacks if a.is_equivalent_to_primary_attack
            ]
            if len(primary_attacks) == 1:
                attack_name = f"{stats.attack.display_name} attacks"
            else:
                attack_name = (
                    " or ".join(a.display_name for a in primary_attacks) + " attacks"
                )

        if stats.multiattack <= 1:
            multiattack = ""
        else:
            multiattack = f"{stats.selfref.capitalize()} makes {num2words(stats.multiattack)} {attack_name}."

            replacements = []
            replacements += [
                (
                    a.display_name,
                    max(1, a.replaces_multiattack),
                )  # assume all additional attacks can be swapped out as part of multiattack
                for a in stats.additional_attacks
                if a.replaces_multiattack < stats.multiattack
                and not a.is_equivalent_to_primary_attack
            ]
            replacements += [
                (f.name, f.replaces_multiattack)
                for f in stats.features
                if f.replaces_multiattack > 0
                and f.replaces_multiattack < stats.multiattack
            ]

            # spellcasting can replace two multiattacks for creatures with 3+ attacks
            if spellcasting and stats.multiattack >= 3:
                replacements.append(("Spellcasting", 2))

            lines = []
            for name, replacement in replacements:
                replace_attacks = (
                    f"{num2words(replacement)} attack{'s' if replacement > 1 else ''}"
                )
                lines.append(f"{replace_attacks} with a use of its {name}")
            if len(lines) > 0:
                multiattack += " It may replace " + " or ".join(lines)

        t = MonsterTemplateData(
            name=stats.name,
            selfref=stats.selfref,
            roleref=stats.roleref,
            size=stats.size.name,
            creature_type=creature_type,
            ac=stats.ac.description,
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
            damage_immunities=_damage_list(
                stats.damage_immunities, stats.nonmagical_immunity
            ),
            condition_immunities=", ".join(c.name for c in stats.condition_immunities),
            senses=stats.senses.describe(
                stats.attributes.passive_skill(Skills.Perception)
            ),
            languages=languages,
            challenge=cr,
            proficiency_bonus=f"+{stats.attributes.proficiency}",
            passives=passives,
            actions=actions,
            bonus_actions=bonus_actions,
            reactions=reactions,
            legendary_actions=legendary_actions,
            attack_modifiers=attack_modifiers,
            multiattack=multiattack,
            attack=stats.attack,
            attacks=stats.additional_attacks,
            benchmarks=benchmarks,
            spellcasting=spellcasting,
        )
        return t


def _damage_list(damage_types: Set[DamageType], nonmagical: bool) -> str:
    pieces = []
    if len(damage_types) > 0:
        pieces.append(", ".join(d.name.capitalize() for d in damage_types))
    if nonmagical:
        pieces.append("Bludgeoning, Piercing, and Slashing from Nonmagical Attacks")
    return "; ".join(pieces)
