from datetime import datetime
from typing import List

import numpy as np

from foe_foundry.references import Token
from foe_foundry.utils import summoning

from ...creature_types import CreatureType
from ...damage import AttackType, Condition, DamageType, conditions
from ...die import Die
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...spells import CasterType
from ...statblocks import BaseStatblock
from ..power import MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class EmanationPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        power_level: float = MEDIUM_POWER,
        reference_statblock: str = "Mage",
        **kwargs,
    ):
        new_callback = kwargs.pop("require_callback", None)

        def callback(stats: BaseStatblock) -> bool:
            if stats.caster_type is None or stats.caster_type not in {
                CasterType.Arcane,
                CasterType.Innate,
                CasterType.Primal,
                CasterType.Psionic,
            }:
                return False

            if new_callback is not None and not new_callback(stats):
                return False

            return True

        score_args = (
            dict(
                require_callback=callback,
                require_attack_types=AttackType.AllSpell(),
                require_cr=6,
            )
            | kwargs
        )

        super().__init__(
            name=name,
            source="Foe Foundry",
            power_type=PowerType.Theme,
            theme="emanation",
            reference_statblock=reference_statblock,
            create_date=datetime(2025, 3, 9),
            power_level=power_level,
            score_args=score_args,
        )


class _TimeRift(EmanationPower):
    def __init__(self):
        super().__init__(
            name="Time Rift",
            require_types=[
                CreatureType.Fey,
                CreatureType.Fiend,
                CreatureType.Aberration,
            ],
            require_roles=MonsterRole.Controller,
            bonus_damage=DamageType.Force,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        token = Token(name="Time Rift", dc=stats.difficulty_class_token, charges=3)
        dmg = stats.target_value(target=0.7, force_die=Die.d6)
        feature = Feature(
            name="Time Rift",
            action=ActionType.Action,
            replaces_multiattack=2,
            creates_token=True,
            recharge=5,
            description=f"{stats.selfref.capitalize()} creates a Medium {token.caption} in an unoccupied space within 30 feet. \
                Each creature that starts its turn within a 30 foot emanation of the {token.name} must repeat the same action it took on its previous turn. \
                If it chooses not to or is unable to repeat the same action, it takes {dmg.description} force damage.",
        )
        return [feature]


class _RunicWards(EmanationPower):
    def __init__(self):
        super().__init__(name="Runic Wards", require_roles=MonsterRole.Defender)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        token = Token(name="Runic Wards", dc=stats.difficulty_class_token, charges=3)
        feature = Feature(
            name="Runic Wards",
            action=ActionType.Action,
            recharge=5,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} creates a Tiny {token.caption} in an unoccupied space within 30 feet. \
                While the {token.name} is active, it grants immunity to all damage to all friendly creatures within 10 feet.",
        )
        return [feature]


class _SummonersRift(EmanationPower):
    def __init__(self):
        super().__init__(
            name="Summoner's Rift",
            require_types=[
                CreatureType.Fey,
                CreatureType.Fiend,
                CreatureType.Aberration,
            ],
            require_roles=MonsterRole.Support,
        )

    def _summon_formula(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> str | None:
        try:
            summon_cr_target = max(stats.cr / 4, 1)
            _, _, description = summoning.determine_summon_formula(
                summoner=CreatureType.Elemental,
                summon_cr_target=summon_cr_target,
                rng=rng,
                max_quantity=4,
            )
            return description
        except Exception:
            return None

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        description = self._summon_formula(stats, stats.create_rng("summoners rift"))

        rift = Token(name="Summoner's Rift", dc=stats.difficulty_class_token, charges=2)

        feature = Feature(
            name="Summoner's Rift",
            action=ActionType.Action,
            recharge=6,
            replaces_multiattack=2,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} magically creates a Medium {rift.caption} at an unoccupied space it can see within 30 feet. \
                Each turn that the rift is active, on initiative count 0, roll a d20. On a 1-5 a new {rift.name} is created at an unoccupied location within 30 feet of the original. \
                Otherwise, {description}",
        )
        return [feature]


class _RecombinationMatrix(EmanationPower):
    def __init__(self):
        super().__init__(
            name="Recombination Matrix",
            require_types=[
                CreatureType.Aberration,
            ],
            require_roles=MonsterRole.Controller,
            bonus_damage=DamageType.Force,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        ac = min(max(round(stats.cr / 3), 1), 5)

        token = Token(
            name="Recombination Matrix", dc=stats.difficulty_class_token, charges=3
        )
        feature = Feature(
            name="Recombination Matrix",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} creates a Tiny {token.caption} in an unoccupied space within 30 feet. \
                While the {token.name} is active, it creates difficult terrain in a 30 foot emanation and reduces the AC of all non-friendly creatures by {ac}.",
        )
        return [feature]


class _HypnoticLure(EmanationPower):
    def __init__(self):
        super().__init__(
            name="Hypnotic Lure",
            require_types=[
                CreatureType.Fey,
            ],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        token = Token(name="Hypnotic Lure", dc=stats.difficulty_class_token, charges=3)
        feature = Feature(
            name="Hypnotic Lure",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} creates a Tiny {token.caption} in an unoccupied space within 30 feet. \
                While the {token.name} is active, all non-friendly creatures within 30 feet must use their movement and actions to attempt to attack the {token.name}.",
        )

        return [feature]


class _IllusoryReality(EmanationPower):
    def __init__(self):
        super().__init__(
            name="Illusory Reality",
            require_types=[
                CreatureType.Fey,
                CreatureType.Aberration,
            ],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        token = Token(
            name="Illusory Reality", dc=stats.difficulty_class_token, charges=3
        )
        charmed = Condition.Charmed
        feared = Condition.Frightened
        dazed = conditions.Dazed()
        feature = Feature(
            name="Illusory Reality",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} creates a Huge {token.caption} in an unoccupied space within 30 feet. \
                While the {token.name} is active, it creates a 30 foot emanation. Any creature that starts its turn within the emanation must make a DC {token.dc} Intelligence save. \
                On a failure, the creature rolls a d6 and suffers the following effects until the start of its next turn. \
                On a 1-2 it is {charmed.caption}, on a 3-4 it is {feared.caption}, and on a 5-6 it is {dazed.caption}.",
        )

        return [feature]


class _ShadowRift(EmanationPower):
    def __init__(self):
        super().__init__(name="Shadow Rift", require_types=CreatureType.Undead)

    def _summon_formula(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> str | None:
        try:
            summon_cr_target = max(stats.cr / 3, 1)
            _, _, description = summoning.determine_summon_formula(
                summoner=CreatureType.Undead,
                summon_cr_target=summon_cr_target,
                rng=rng,
            )
            return description
        except Exception:
            return None

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        description = self._summon_formula(stats, stats.create_rng("shadow rift"))

        rift = Token(name="Shadow Rift", dc=stats.difficulty_class_token, charges=2)

        feature = Feature(
            name="Shadow Rift",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=2,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} magically creates a Medium {rift.caption} at an unoccupied space it can see within 30 feet. \
                Each turn that the rift is active, on initiative count 0, {description}",
        )
        return [feature]


class _RagingFlames(EmanationPower):
    def __init__(self):
        super().__init__(
            name="Raging Flames",
            bonus_types=[
                CreatureType.Elemental,
            ],
            require_damage=DamageType.Fire,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        token = Token(name="Raging Flames", dc=stats.difficulty_class_token, charges=3)
        dmg = stats.target_value(dpr_proportion=0.25, force_die=Die.d10)

        feature = Feature(
            name="Raging Flames",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} creates a Medium {token.caption} in an unoccupied space within 30 feet. \
                Each creature that starts its turn within a 30 foot emanation of the {token.name} takes {dmg.description} fire damage.",
        )

        return [feature]


class _BitingFrost(EmanationPower):
    def __init__(self):
        super().__init__(
            name="Biting Frost",
            bonus_types=[
                CreatureType.Elemental,
            ],
            require_damage=DamageType.Cold,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        token = Token(name="Biting Frost", dc=stats.difficulty_class_token, charges=3)
        dmg = stats.target_value(dpr_proportion=0.25, force_die=Die.d10)

        feature = Feature(
            name="Biting Frost",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} creates a Medium {token.caption} in an unoccupied space within 30 feet. \
                Each creature that starts its turn within a 30 foot emanation of the {token.name} takes {dmg.description} cold damage.",
        )

        return [feature]


class _LashingWinds(EmanationPower):
    def __init__(self):
        super().__init__(
            name="Lashing Winds",
            bonus_types=[
                CreatureType.Elemental,
            ],
            require_damage=DamageType.Lightning,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        token = Token(name="Lashing Winds", dc=stats.difficulty_class_token, charges=3)
        dmg = stats.target_value(dpr_proportion=0.25, force_die=Die.d10)

        feature = Feature(
            name="Lashing Winds",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} creates a Medium {token.caption} in an unoccupied space within 30 feet. \
                Each creature that starts its turn within a 30 foot emanation of the {token.name} takes {dmg.description} lightning damage.",
        )

        return [feature]


class _FetidMiasma(EmanationPower):
    def __init__(self):
        super().__init__(
            name="Fetid Miasma",
            bonus_types=[
                CreatureType.Elemental,
            ],
            require_damage=DamageType.Poison,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        token = Token(name="Fetid Miasma", dc=stats.difficulty_class_token, charges=3)
        dmg = stats.target_value(dpr_proportion=0.25, force_die=Die.d10)
        poisoned = Condition.Poisoned.caption

        feature = Feature(
            name="Fetid Miasma",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} creates a Medium {token.caption} in an unoccupied space within 30 feet. \
                Each creature that starts its turn within a 30 foot emanation of the {token.name} takes {dmg.description} poison damage and is {poisoned} until the start of its next turn.",
        )

        return [feature]


TimeRift: Power = _TimeRift()
RunicWards: Power = _RunicWards()
SummonersRift: Power = _SummonersRift()
RecombinationMatrix: Power = _RecombinationMatrix()
HypnoticLure: Power = _HypnoticLure()
IllusoryReality: Power = _IllusoryReality()
ShadowRift: Power = _ShadowRift()
RagingFlame: Power = _RagingFlames()
BitingFrost: Power = _BitingFrost()
LashingWinds: Power = _LashingWinds()
FetidMiasma: Power = _FetidMiasma()

EmanationPowers: List[Power] = [
    TimeRift,
    RunicWards,
    SummonersRift,
    RecombinationMatrix,
    HypnoticLure,
    IllusoryReality,
    ShadowRift,
    RagingFlame,
    BitingFrost,
    LashingWinds,
    FetidMiasma,
]
