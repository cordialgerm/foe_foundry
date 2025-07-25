from ...damage import AttackType
from ...power_types import PowerType
from ...spells import CasterType, abjuration, enchantment, evocation, necromancy
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, MEDIUM_POWER, Power
from .base import _Spellcaster
from .utils import spell_list

_adept = [enchantment.Command, enchantment.HoldPerson]
_master = [abjuration.MassCureWounds, evocation.FlameStrike]
_expert = [enchantment.MassSuggestion, necromancy.FingerOfDeath]

CultAdeptSpells = spell_list(_adept, uses=1)
CultMasterSpells = spell_list(_adept, uses=1) + spell_list(_master, uses=1)
CultExpertSpells = (
    spell_list(_adept, uses=1)
    + spell_list(_master, uses=1)
    + spell_list(_expert, uses=1)
)


def is_cultist(c: BaseStatblock):
    return c.creature_class and "cult" in c.creature_class.lower()


class _CultCaster(_Spellcaster):
    def __init__(self, **kwargs):
        args: dict = (
            dict(
                theme="cult",
                caster_type=CasterType.Pact,
                icon="cultist",
                reference_statblock="Cultist Fanatic",
                power_types=[PowerType.Magic, PowerType.Debuff],
                score_args=dict(
                    require_attack_types=AttackType.AllSpell(),
                    require_callback=is_cultist,
                ),
            )
            | kwargs
        )

        super().__init__(**args)


def spellcaster_for_cr(cr: float) -> Power | None:
    """
    Returns the appropriate spellcaster for a given CR.
    """
    if cr < 2:
        return None
    elif cr <= 4:
        return CultSpellcastingAdpet
    elif cr <= 10:
        return CultSpellcastingMaster
    else:
        return CultSpellcastingExpert


CultSpellcastingAdpet = _CultCaster(
    name="Cult Spellcasting Adept",
    min_cr=2,
    max_cr=4,
    spells=CultAdeptSpells,
    power_level=MEDIUM_POWER,
)
CultSpellcastingMaster = _CultCaster(
    name="Cult Spellcasting Master",
    min_cr=5,
    max_cr=10,
    spells=CultMasterSpells,
    power_level=HIGH_POWER,
)
CultSpellcastingExpert = _CultCaster(
    name="Cult Spellcasting Expert",
    min_cr=11,
    max_cr=40,
    spells=CultExpertSpells,
    power_level=HIGH_POWER,
)

CultCasters: list[Power] = [
    CultSpellcastingAdpet,
    CultSpellcastingMaster,
    CultSpellcastingExpert,
]
