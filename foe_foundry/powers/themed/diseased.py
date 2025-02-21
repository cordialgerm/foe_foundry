import math
from datetime import datetime
from typing import List

from ...attack_template import natural, spell
from ...creature_types import CreatureType
from ...damage import DamageType, conditions
from ...die import Die
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class DiseasePower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        super().__init__(
            name=name,
            power_type=PowerType.Theme,
            source="Foe Foundry",
            create_date=datetime(2023, 11, 20),
            theme="disease",
            power_level=power_level,
            score_args=dict(
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
                # there's a score multiplier because each of these powers has N different variants (one for each disease)
                # so we want to reduce the overall likelyhood of any individual disease power being selected
                score_multiplier=0.75,
                **score_args,
            ),
        )


def _RottenGrasp(disease: conditions.CustomCondition) -> Power:
    class _RottenGraspInner(DiseasePower):
        def __init__(self):
            super().__init__(
                name=f"Rotten Grasp ({disease.name.title()})", power_level=HIGH_POWER
            )

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
    class _ToxicBreathInner(DiseasePower):
        def __init__(self):
            super().__init__(
                name=f"Toxic Breath ({disease.name.title()})", power_level=HIGH_POWER
            )

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            dc = stats.difficulty_class
            dmg = stats.target_value(target=1.8, force_die=Die.d6)

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

FatiguesEmbrace = conditions.CustomCondition(
    name="Fatigue's Embrace",
    caption="**Fatigue's Embrace**",
    description="Your body is wracked with fatigue. You gain a level of **Exhaustion** each time you take a long rest. You cannot remove **Exhaustion** during a long rest.",
    description_3rd="The creature's body is wracked with fatigue. The creature gains a level of **Exhaustion** each time it takes a long rest. The creature cannot remove **Exhaustion** during a long rest.",
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
