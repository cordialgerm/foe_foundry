from datetime import datetime
from typing import List

from ...attack_template import weapon
from ...attributes import Stats
from ...creature_types import CreatureType
from ...damage import DamageType, conditions
from ...die import Die
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...spells import evocation
from ...statblocks import BaseStatblock
from ..power import MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class HolyPower(PowerWithStandardScoring):
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
            theme="holy",
            power_type=PowerType.Theme,
            create_date=create_date,
            power_level=power_level,
            score_args=dict(
                require_stats=[Stats.WIS, Stats.CHA],
                require_types=CreatureType.Humanoid,
                require_damage=DamageType.Radiant,
                bonus_roles=MonsterRole.Leader,
            )
            | score_args,
        )


class _DivineSmite(HolyPower):
    def __init__(self):
        super().__init__(
            name="Divine Smite",
            source="Foe Foundry",
            attack_names=[
                weapon.MaceAndShield,
                weapon.Greatsword,
                weapon.SwordAndShield,
            ],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(0.7, force_die=Die.d10)
        burning = conditions.Burning(dmg, damage_type=DamageType.Radiant)
        feature = Feature(
            name="Divine Smite",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"Immediately after hitting a target, {stats.roleref} forces the target to make a DC {dc} Constitution saving throw. On a failure, the target is {burning}",
        )
        return [feature]


class _MassCureWounds(HolyPower):
    def __init__(self):
        super().__init__(name="Mass Cure Wounds", source="SRD5.1 Mass Cure Wounds")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        spell = evocation.MassCureWounds.for_statblock()
        return stats.add_spell(spell)


class _WordOfRadiance(HolyPower):
    def __init__(self):
        super().__init__(name="Word of Radiance", source="SRD 5.1 Word of Radiance")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        damage = stats.target_value(0.6, force_die=Die.d6)
        dc = stats.difficulty_class

        feature = Feature(
            name="Word of Radiance",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.roleref.capitalize()} utters a divine word and it shines with burning radiance. \
                Each hostile creature within 10 feet must make a DC {dc} Constitution saving throw or take {damage.description} radiant damage.",
        )
        return [feature]


DivineSmite: Power = _DivineSmite()
MassCureWounds: Power = _MassCureWounds()
WordOfRadiance: Power = _WordOfRadiance()

HolyPowers: List[Power] = [DivineSmite, MassCureWounds, WordOfRadiance]
