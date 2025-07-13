from datetime import datetime
from typing import List

from foe_foundry.references import Token
from foe_foundry.utils import easy_multiple_of_five

from ...creature_types import CreatureType
from ...damage import Condition
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...spells import CasterType
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, Power, PowerCategory, PowerWithStandardScoring


class TotemicPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = HIGH_POWER,
        create_date: datetime | None = datetime(2025, 3, 31),
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            power_category=PowerCategory.Theme,
            icon=icon,
            power_level=power_level,
            power_types=power_types or [PowerType.Magic, PowerType.Summon],
            theme="totemic",
            reference_statblock="Druid",
            create_date=create_date,
            score_args=dict(
                require_types=CreatureType.Humanoid,
                require_spellcasting=CasterType.Primal,
            )
            | score_args,
        )


class _AncestralTotem(TotemicPower):
    def __init__(self):
        super().__init__(
            name="Ancestral Totem",
            source="Foe Foundry",
            icon="totem",
            power_types=[PowerType.Magic, PowerType.Summon, PowerType.Buff],
            require_roles=[MonsterRole.Support, MonsterRole.Leader],
            require_cr=1,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        token = Token(
            name="Ancestral Totem", dc=stats.difficulty_class_token, charges=3
        )
        feature = Feature(
            name="Ancestral Totem",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} creates a {token.caption} in an unoccupied space within 5 feet. Whenever a friendly creature within 30 feet of the totem fails a d20 test, the totem consumes a charge and turns the failure into a success.",
        )
        return [feature]


class _EarthbindTotem(TotemicPower):
    def __init__(self):
        super().__init__(
            name="Earthbind Totem",
            source="Foe Foundry",
            icon="bug-net",
            power_types=[PowerType.Magic, PowerType.Summon, PowerType.Debuff],
            require_roles=[MonsterRole.Controller, MonsterRole.Artillery],
            require_cr=1,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_token
        restrained = Condition.Restrained
        token = Token(name="Earthbind Totem", dc=dc, charges=3)

        feature = Feature(
            name="Earthbind Totem",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} creates a {token.caption} in an unoccupied space within 5 feet. \
                Whenever a creature ends its turn within 30 feet of the the totem it must make a DC {dc} Strength save or become {restrained.caption} (save ends end of turn).",
        )
        return [feature]


class _WindfuryToten(TotemicPower):
    def __init__(self):
        super().__init__(
            name="Windfury Totem",
            source="Foe Foundry",
            icon="tornado",
            power_types=[PowerType.Magic, PowerType.Summon, PowerType.Buff],
            require_roles=[
                MonsterRole.Support,
                MonsterRole.Leader,
                MonsterRole.Soldier,
            ],
            require_cr=1,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_token
        token = Token(name="Windfury Totem", dc=dc, charges=3)

        feature = Feature(
            name="Windfury Totem",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} creates a {token.caption} in an unoccupied space within 5 feet. \
                Friendly creatures in a 30 foot emanation gain an extra attack.",
        )
        return [feature]


class _GuardianTotem(TotemicPower):
    def __init__(self):
        super().__init__(
            name="Guardian Totem",
            source="Foe Foundry",
            icon="totem-mask",
            power_types=[PowerType.Magic, PowerType.Summon, PowerType.Defense],
            require_roles=[
                MonsterRole.Defender,
                MonsterRole.Support,
                MonsterRole.Leader,
            ],
            require_cr=1,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_token
        token = Token(name="Guardian Totem", dc=dc, charges=3)

        feature = Feature(
            name="Guardian Totem",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} creates a {token.caption} in an unoccupied space within 5 feet. \
                Whenever a friendly creature within 30 feet would be hit by a ranged attack, that attack instead hits the totem and destroys one of its charges. \
                Additionally, whenever a friendly creature within 30 feet would be targeted by a spell, or if a spell's area of effect would overlap to include the totem's emanation, the spell instead targes the totem and destroys one of its charges.",
        )
        return [feature]


class _HealingTotem(TotemicPower):
    def __init__(self):
        super().__init__(
            name="Healing Totem",
            source="Foe Foundry",
            icon="caduceus",
            power_types=[PowerType.Magic, PowerType.Summon, PowerType.Healing],
            require_roles=[MonsterRole.Support, MonsterRole.Leader],
            require_cr=1,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        token = Token(name="Healing Totem", dc=stats.difficulty_class_token, charges=3)
        hp = easy_multiple_of_five(1.25 * stats.cr, min_val=5)
        feature = Feature(
            name="Healing Totem",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} creates a {token.caption} in an unoccupied space within 5 feet. \
                Whenever a friendly creature within 30 feet of the totem is reduced to 0 hit points, the totem consumes a charge and restores that creature to {hp} hit points.",
        )
        return [feature]


class _SpiritChainsTotem(TotemicPower):
    def __init__(self):
        super().__init__(
            name="Spirit Chains Totem",
            icon="crossed-chains",
            source="Foe Foundry",
            power_types=[PowerType.Magic, PowerType.Summon, PowerType.Debuff],
            require_roles=[
                MonsterRole.Controller,
                MonsterRole.Support,
                MonsterRole.Artillery,
            ],
            require_cr=1,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_token
        restrained = Condition.Restrained
        token = Token(name="Spirit Chains Totem", dc=dc, charges=3)
        feature = Feature(
            name="Spirit Chains Totem",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} creates a {token.caption} in an unoccupied space within 5 feet. \
                Whenever a hostile creature ends its turn within 30 feet of the totem, it must make a DC {dc} Wisdom saving throw. \
                On a failure, the creature is {restrained.caption} (save ends at end of turn).",
        )
        return [feature]


AncestralTotem: Power = _AncestralTotem()
EarthbindTotem: Power = _EarthbindTotem()
GuardianTotem: Power = _GuardianTotem()
HealingTotem: Power = _HealingTotem()
SpiritChainsTotem: Power = _SpiritChainsTotem()
WindfuryTotem: Power = _WindfuryToten()

TotemicPowers: List[Power] = [
    AncestralTotem,
    EarthbindTotem,
    HealingTotem,
    WindfuryTotem,
]
