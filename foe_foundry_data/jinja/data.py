from __future__ import annotations

from dataclasses import asdict, dataclass, field
from fractions import Fraction
from typing import List, Set

import numpy as np
from num2words import num2words

from foe_foundry.damage import Attack, Condition, DamageType
from foe_foundry.features import ActionType, Feature
from foe_foundry.skills import Skills, Stats
from foe_foundry.statblocks import Statblock
from foe_foundry.utils import comma_separated, name_to_key

from .utilities import fix_punctuation


@dataclass
class MonsterTemplateData:
    name: str
    template: str
    variant: str
    monster: str
    species: str | None
    selfref: str
    roleref: str
    size: str
    creature_type: str
    ac: str
    initiative: str
    hp: str
    movement: str

    STR: int
    STR_MOD: int
    STR_SAVE: int
    CON: int
    CON_MOD: int
    CON_SAVE: int
    DEX: int
    DEX_MOD: int
    DEX_SAVE: int
    WIS: int
    WIS_MOD: int
    WIS_SAVE: int
    INT: int
    INT_MOD: int
    INT_SAVE: int
    CHA: int
    CHA_MOD: int
    CHA_SAVE: int

    saves: str
    skills: str
    damage_vulnerabilities: str
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

    reaction_header: str
    reactions: List[Feature]

    attacks: List[Attack]
    attack_modifiers: List[Feature]
    legendary_actions: List[Feature]
    legendary_action_header: str

    multiattack: str
    attack: Attack

    spellcasting: str

    key: str = field(init=False)
    attack_modifier_text: str = field(init=False)
    attack_text: str = field(init=False)
    immunities_combined: str = field(init=False)
    challenge_pb_combined: str = field(init=False)

    def __post_init__(self):
        self.key = name_to_key(self.name)
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

        immunities = [
            i for i in [self.damage_immunities, self.condition_immunities] if len(i) > 0
        ]
        if len(immunities) > 0:
            self.immunities_combined = "; ".join(immunities)
        else:
            self.immunities_combined = ""

        self.challenge_pb_combined = (
            f"{self.challenge[:-1]}; PB {self.proficiency_bonus})"
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_statblock(stats: Statblock) -> MonsterTemplateData:
        hp = f"{stats.hp.static} ({stats.hp.dice_formula()})"
        languages = (
            ", ".join(lang for lang in stats.languages)
            if stats.languages is not None
            else ""
        )

        iniative_mod = stats.attributes.skill_mod(Skills.Initiative) or 0
        static_initiative = 10 + iniative_mod
        initiative = f"{iniative_mod:+} ({static_initiative})"

        creature_type_additions = []
        if len(stats.additional_types) > 1:
            additional_types = stats.additional_types.copy()
            if stats.creature_type in additional_types:
                additional_types.remove(stats.creature_type)
            creature_type_additions.extend([f"{ct.name}*" for ct in additional_types])

        if (
            stats.creature_subtype
            and stats.creature_subtype not in creature_type_additions
        ):
            creature_type_additions.append(stats.creature_subtype)
        if stats.creature_class and stats.creature_class not in creature_type_additions:
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

        if isinstance(stats.reaction_count, int):
            if stats.reaction_count > 1:
                reaction_header = f"Reactions ({stats.reaction_count}/turn)"
            else:
                reaction_header = "Reactions"
        else:
            reaction_header = f"Reactions ({stats.reaction_count})"

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
            if stats.multiattack_custom_text is None:
                multiattack = f"{stats.selfref.capitalize()} makes {num2words(stats.multiattack)} {attack_name}."
            else:
                multiattack = stats.multiattack_custom_text

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

            if len(replacements) > 0:
                replacement_amount = max(
                    1, int(np.ceil(np.mean([r[1] for r in replacements])))
                )
                replacement_options = comma_separated(
                    [r[0] for r in replacements], conjunction="or"
                )
                replacement_text = f" It may replace {num2words(replacement_amount)} attack{'s' if replacement_amount > 1 else ''} with a use of its {replacement_options}"
                multiattack += replacement_text

        stat_args: dict = {}
        for attr in Stats.All():
            stat_args[f"{attr.name.upper()}"] = stats.attributes.stat(attr)
            stat_args[f"{attr.name.upper()}_MOD"] = (
                f"{stats.attributes.stat_mod(attr):+}"
            )
            stat_args[f"{attr.name.upper()}_SAVE"] = (
                f"{stats.attributes.save_mod(attr) or stats.attributes.stat_mod(attr):+}"
            )

        t = MonsterTemplateData(
            name=stats.name,
            template=stats.template_key.lower(),
            variant=stats.variant_key.lower(),
            monster=stats.monster_key.lower(),
            species=stats.creature_subtype.lower() if stats.creature_subtype else None,
            selfref=stats.selfref,
            roleref=stats.roleref,
            size=stats.size.name,
            creature_type=creature_type,
            ac=stats.ac.description,
            hp=hp,
            initiative=initiative,
            movement=stats.speed.describe(),
            **stat_args,
            saves=stats.attributes.describe_saves(),
            skills=stats.attributes.describe_skills(skip={Skills.Initiative}),
            damage_vulnerabilities=_damage_list(
                stats.damage_vulnerabilities, nonmagical=False
            ),
            damage_resistances=_damage_list(
                stats.damage_resistances, stats.nonmagical_resistance
            ),
            damage_immunities=_damage_list(
                stats.damage_immunities, stats.nonmagical_immunity
            ),
            condition_immunities=_condition_list(stats.condition_immunities),
            senses=stats.senses.describe(
                stats.attributes.passive_skill(Skills.Perception)
            ),
            languages=languages,
            challenge=cr,
            proficiency_bonus=f"+{stats.attributes.proficiency}",
            passives=passives,
            actions=actions,
            bonus_actions=bonus_actions,
            reaction_header=reaction_header,
            reactions=reactions,
            legendary_actions=legendary_actions,
            legendary_action_header=f"Legendary Actions ({stats.legendary_actions})",
            attack_modifiers=attack_modifiers,
            multiattack=multiattack,
            attack=stats.attack,
            attacks=stats.additional_attacks,
            spellcasting=spellcasting,
        )
        return t


def _damage_list(damage_types: Set[DamageType], nonmagical: bool) -> str:
    sorted_damage_types = sorted(damage_types, key=lambda d: d.name)

    pieces = []
    if len(damage_types) > 0:
        pieces.append(", ".join(d.name.capitalize() for d in sorted_damage_types))
    if nonmagical:
        pieces.append("Bludgeoning, Piercing, and Slashing from Nonmagical Attacks")
    return "; ".join(pieces)


def _condition_list(conditions: Set[Condition]) -> str:
    sorted_conditions = sorted(conditions, key=lambda c: c.name)
    return ", ".join(c.name for c in sorted_conditions)
