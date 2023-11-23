import math
from math import ceil, floor
from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attack_template import natural, spell, weapon
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import HIGH_POWER, PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..power import Power, PowerType
from ..scoring import score

# there's a score multiplier because each of these powers has N different variants (one for each disease)
# so we want to reduce the overall likelyhood of any individual disease power being selected
SCORE_MULTIPLIER = 0.75


def _score(candidate: BaseStatblock) -> float:
    return SCORE_MULTIPLIER * score(
        candidate=candidate,
        require_types=[
            CreatureType.Plant,
            CreatureType.Monstrosity,
            CreatureType.Undead,
            CreatureType.Fiend,
        ],
        bonus_damage=DamageType.Poison,
        require_cr=2,
        attack_names=[
            "-",
            natural.Bite,
            natural.Claw,
            natural.Stinger,
            natural.Tentacle,
            natural.Thrash,
            natural.Spit,
            spell.Poisonbolt,
        ],
    )


def _RottenGrasp(disease: conditions.CustomCondition) -> Power:
    class _RottenGraspInner(Power):
        def __init__(self):
            super().__init__(
                name="Rotten Grasp", power_type=PowerType.Theme, power_level=HIGH_POWER
            )

        def score(self, candidate: BaseStatblock) -> float:
            return _score(candidate)

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            dc = stats.difficulty_class
            hit_die = int(1 + math.floor(stats.cr / 7))

            feature1 = _disease_as_feature(disease)

            feature2 = Feature(
                name="Rotten Grasp",
                action=ActionType.Feature,
                hidden=True,
                modifies_attack=True,
                description=f"On a hit, the target must make a DC {dc} Constitution saving throw. On a failure, the target loses {hit_die} hit die and rolls those die and takes that much poison damage. \
                    If the target is out of hit die, it is diseased with {disease.caption} (see features).",
            )

            return [feature1, feature2]

    return _RottenGraspInner()


def _ToxicBreath(disease: conditions.CustomCondition) -> Power:
    class _ToxicBreathInner(Power):
        def __init__(self):
            super().__init__(
                name="Toxic Breath", power_type=PowerType.Theme, power_level=HIGH_POWER
            )

        def score(self, candidate: BaseStatblock) -> float:
            return _score(candidate)

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            dc = stats.difficulty_class
            dmg = DieFormula.target_value(
                target=stats.attack.average_damage * 1.8, force_die=Die.d6
            )

            feature1 = _disease_as_feature(disease)

            feature2 = Feature(
                name="Toxic Breath",
                action=ActionType.Action,
                recharge=5,
                replaces_multiattack=2,
                description=f"{stats.selfref.capitalize()} exhales toxic gas in a 15-foot cone. Each creature in that area must make a DC {dc} Constitution saving throw. \
                    On a failure, the creature takes {dmg.description} poison damage and is **Poisoned** for 1 minute (save ends at end of turn). \
                    If a creature fails this save three times, it becomes afflicted by {disease.caption} (see features).",
            )

            return [feature1, feature2]

    return _ToxicBreathInner()


### Diseases
def _disease_as_feature(disease: conditions.CustomCondition) -> Feature:
    return Feature(
        name=f"{disease.name} (Disease)",
        action=ActionType.Feature,
        description=f"This creature can inflict the {disease.caption} disease: {disease.description_3rd}",
    )


BlindingSickness = conditions.CustomCondition(
    name="Blinding Sickness",
    caption="**Blinding Sickness**",
    description="Pain grips your mind, and your eyes turn milky white. You have disadvantage on Wisdom checks and Wisdom saving throws and are **Blinded**.",
    description_3rd="An infected creature's mind is gripped by pain and its eyes turn milky white. The creature has disadvantage on Wisdom checks and Wisdom saving throws and is **Blinded**.",
)

_weakened = conditions.Weakened(save_end_of_turn=False)
FilthFever = conditions.CustomCondition(
    name="Filth Fever",
    caption="**Filth Fever**",
    description=f"A raging fever sweeps through your body. You are {_weakened.caption}. {_weakened.description}",
    description_3rd=f"A raging fever sweeps through the creature's body. The creature is {_weakened.caption}. {_weakened.description_3rd}",
)

FleshRot = conditions.CustomCondition(
    name="Flesh Rot",
    caption="**Flesh Rot**",
    description="Your flesh decays. You have disadvantage on Charisma checks and vulnerability to all damage.",
    description_3rd="The creature's flesh decays. The creature has disadvantage on Charisma checks and vulnerability to all damage.",
)

Mindfire = conditions.CustomCondition(
    name="Mindfire",
    caption="**Mindfire**",
    description="Your mind becomes feverish. You have disadvantage on Intelligence checks and Intelligence saving throws, and you behave as if under the effects of the *Confusion* spell during combat.",
    description_3rd="The creature's mind becomes feverish. The creature has disadvantage on Intelligence checks and Intelligence saving throws, and the creature behaves as if under the effects of the *Confusion* spell during combat.",
)

Chronotaenia = conditions.CustomCondition(
    name="Chronotaenia",
    caption="**Chronotaenia**",
    description="Your movements become sluggish. You have disadvantage on initiative rolls and start each combat **Dazed** until the start of your next turn.",
    description_3rd="The creature's movements become sluggish. The creature has disadvantage on initiative rolls and starts each combat **Dazed** until the start of its next turn.",
)

fatigue = conditions.Fatigue()
FatiguesEmbrace = conditions.CustomCondition(
    name="Fatigue's Embrace",
    caption="**Fatigue's Embrace**",
    description=f"Your body is wracked with fatigue. You gain a level of {fatigue.caption} each time you take a long rest. You cannot remove {fatigue.caption} during a long rest. {fatigue.description}",
    description_3rd=f"The creature's body is wracked with fatigue. The creature gains a level of {fatigue.caption} each time it takes a long rest. The creature cannot remove {fatigue.caption} during a long rest. {fatigue.description_3rd}",
)

Diseases: List[conditions.CustomCondition] = [
    BlindingSickness,
    FilthFever,
    FleshRot,
    Mindfire,
    Chronotaenia,
    FatiguesEmbrace,
]
RottenGraspPowers: List[Power] = [_RottenGrasp(d) for d in Diseases]
ToxicBreathPowers: List[Power] = [_ToxicBreath(d) for d in Diseases]
DiseasedPowers: List[Power] = RottenGraspPowers + ToxicBreathPowers
