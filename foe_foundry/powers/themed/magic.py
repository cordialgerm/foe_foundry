from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import DamageType
from ...role_types import MonsterRole
from ...spells import StatblockSpell, abjuration, evocation, necromancy, transmutation
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, Power
from ..spell import SpellPower


def humanoid_is_spellcaster(c: BaseStatblock) -> bool:
    if c.creature_type == CreatureType.Humanoid:
        return any(t.is_spell() for t in c.attack_types)
    else:
        return True


class _MagicPower(SpellPower):
    def __init__(self, spell: StatblockSpell, **kwargs):
        super().__init__(
            spell=spell,
            theme="magic",
            create_date=datetime(2023, 12, 10),
            **kwargs,
        )


class _DispelMagic(_MagicPower):
    def __init__(self):
        super().__init__(
            spell=abjuration.DispelMagic.for_statblock(),
            score_args=dict(
                require_types=[
                    CreatureType.Fey,
                    CreatureType.Fiend,
                    CreatureType.Celestial,
                    CreatureType.Humanoid,
                ],
                require_callback=humanoid_is_spellcaster,
                require_cr=4,
                bonus_roles=[
                    MonsterRole.Defender,
                    MonsterRole.Leader,
                    MonsterRole.Controller,
                ],
            ),
        )


class _Disintigrate(_MagicPower):
    def __init__(self):
        super().__init__(
            spell=transmutation.Disintegrate.for_statblock(),
            power_level=HIGH_POWER,
            score_args=dict(
                require_types=[
                    CreatureType.Humanoid,
                ],
                require_callback=humanoid_is_spellcaster,
                require_damage=[DamageType.Force, DamageType.Necrotic],
                require_cr=7,
            ),
        )


class _FingerOfDeath(_MagicPower):
    def __init__(self):
        super().__init__(
            spell=necromancy.FingerOfDeath.for_statblock(),
            power_level=HIGH_POWER,
            score_args=dict(
                require_types=[CreatureType.Humanoid, CreatureType.Undead],
                require_callback=humanoid_is_spellcaster,
                require_damage=[DamageType.Necrotic],
                require_cr=8,
            ),
        )


class _ChainLightning(_MagicPower):
    def __init__(self):
        super().__init__(
            spell=evocation.ChainLightning.for_statblock(),
            power_level=HIGH_POWER,
            score_args=dict(
                require_types=[
                    CreatureType.Humanoid,
                    CreatureType.Elemental,
                    CreatureType.Giant,
                ],
                require_callback=humanoid_is_spellcaster,
                require_damage=[DamageType.Lightning, DamageType.Thunder],
                require_cr=7,
            ),
        )


class _Banishment(_MagicPower):
    def __init__(self):
        super().__init__(
            spell=abjuration.Banishment.for_statblock(),
            power_level=HIGH_POWER,
            score_args=dict(
                require_types=[
                    CreatureType.Humanoid,
                ],
                bonus_roles=MonsterRole.Controller,
                require_damage=[DamageType.Radiant],
                require_callback=humanoid_is_spellcaster,
                require_cr=5,
            ),
        )


class _Fireball(_MagicPower):
    def __init__(self):
        super().__init__(
            spell=evocation.Fireball.for_statblock(),
            power_level=HIGH_POWER,
            score_args=dict(
                require_types=[
                    CreatureType.Humanoid,
                    CreatureType.Fiend,
                    CreatureType.Elemental,
                ],
                require_damage=[DamageType.Fire],
                require_callback=humanoid_is_spellcaster,
                require_cr=5,
            ),
        )


class _LightningBolt(_MagicPower):
    def __init__(self):
        super().__init__(
            spell=evocation.LightningBolt.for_statblock(),
            power_level=HIGH_POWER,
            score_args=dict(
                require_types=[
                    CreatureType.Humanoid,
                    CreatureType.Elemental,
                    CreatureType.Giant,
                ],
                require_damage=[DamageType.Lightning, DamageType.Thunder],
                require_callback=humanoid_is_spellcaster,
                require_cr=5,
            ),
        )


Banishment: Power = _Banishment()
ChainLightning: Power = _ChainLightning()
DispelMagic: Power = _DispelMagic()
Disintigrate: Power = _Disintigrate()
FingerOfDeath: Power = _FingerOfDeath()
Fireball: Power = _Fireball()
LightningBolt: Power = _LightningBolt()


MagicPowers: List[Power] = [
    Banishment,
    ChainLightning,
    DispelMagic,
    Disintigrate,
    FingerOfDeath,
    Fireball,
    LightningBolt,
]
