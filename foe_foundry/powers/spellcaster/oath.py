from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...spells import CasterType, abjuration, enchantment
from ...statblocks import BaseStatblock
from .. import flags
from ..power import HIGH_POWER, LOW_POWER, Power
from .base import _Spellcaster
from .utils import spell_list

_adept = [
    enchantment.Command,
    abjuration.CureWounds,
    abjuration.LesserRestoration,
]
_master = [abjuration.DispelEvilAndGood, abjuration.GreaterRestoration]

OathAdeptSpells = spell_list(_adept, uses=1)
OathMasterSpells = spell_list(
    _adept, uses=1, exclude={abjuration.LesserRestoration}
) + spell_list(_master, uses=1)


def is_oath_caster(stats: BaseStatblock) -> bool:
    return stats.creature_type == CreatureType.Celestial or (
        stats.creature_type == CreatureType.Humanoid
        and (
            stats.secondary_damage_type == DamageType.Radiant
            or stats.caster_type == CasterType.Divine
        )
    )


class _OathCaster(_Spellcaster):
    def __init__(self, **kwargs):
        args: dict = (
            dict(
                theme="Oath",
                reference_statblock="Questing Knight",
                icon="knight-banner",
                power_types=[PowerType.Magic, PowerType.Healing],
                score_args=dict(
                    require_callback=is_oath_caster,
                    require_types=[CreatureType.Celestial, CreatureType.Humanoid],
                    require_attack_types=None,  # overwrite requirement in base class
                    bonus_attack_types=AttackType.MeleeWeapon,
                    bonus_roles=[
                        MonsterRole.Defender,
                        MonsterRole.Leader,
                        MonsterRole.Soldier,
                        MonsterRole.Support,
                    ],
                ),
                caster_type=CasterType.Divine,
            )
            | kwargs
        )

        super().__init__(**args)

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return super().modify_stats_inner(stats).with_flags(flags.HAS_HEALING)


OathAdept: Power = _OathCaster(
    name="Oath Adept",
    min_cr=6,
    max_cr=11,
    spells=OathAdeptSpells,
    power_level=LOW_POWER,
)
OathMaster: Power = _OathCaster(
    name="Oath Master",
    min_cr=12,
    spells=OathMasterSpells,
    power_level=HIGH_POWER,
)


OathCasters: list[Power] = [
    OathAdept,
    OathMaster,
]
