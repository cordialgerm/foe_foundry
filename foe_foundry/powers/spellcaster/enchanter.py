from typing import List

from ...attack_template import spell
from ...creature_types import CreatureType
from ...damage import DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...spells import enchantment, illusion
from ...statblocks import BaseStatblock
from ..power import EXTRA_HIGH_POWER, HIGH_POWER, MEDIUM_POWER, Power
from .base import _Wizard
from .utils import spell_list

_adept = [
    enchantment.CharmPerson,
    enchantment.Suggestion,
    enchantment.Command,
    illusion.Invisibility,
]
_master = [
    illusion.HypnoticPattern,
    illusion.Fear,
    enchantment.HoldPerson,
]
_expert = [enchantment.Feeblemind, enchantment.DominateMonster]

EnchanterAdeptSpells = spell_list(spells=_adept, uses=1, mark_schools={"enchantment"})
EnchanterMasterSpells = spell_list(
    spells=_adept, uses=2, exclude={illusion.Invisibility}, mark_schools={"enchantment"}
) + spell_list(spells=_master, uses=1, mark_schools={"enchantment"})
EnchanterExpertSpells = (
    spell_list(
        _adept, uses=3, exclude={illusion.Invisibility}, mark_schools={"enchantment"}
    )
    + spell_list(_master, uses=2, mark_schools={"enchantment"})
    + spell_list(_expert, uses=1, mark_schools={"enchantment"})
)


class _EnchanterWizard(_Wizard):
    def __init__(self, **kwargs):
        args: dict = (
            dict(
                creature_class="Enchanter",
                theme="enchantment",
                score_args=dict(
                    require_types=[
                        CreatureType.Humanoid,
                        CreatureType.Fey,
                    ],
                    bonus_damage=DamageType.Psychic,
                    bonus_roles=MonsterRole.Controller,
                    attack_names=[
                        spell.Gaze,
                    ],  # bonus, not required
                ),
            )
            | kwargs
        )

        super().__init__(**args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Protective Charm",
            uses=1,
            action=ActionType.Reaction,
            description=f"Whenever a visible creature within 30 feet of {stats.selfref} targets it with an ability, spell, or attack roll, {stats.selfref} may use its reaction to cast an Enchantment spell (indicated with a \\*) from its *Spellcasting* trait against that creature.",
        )

        return [feature]


def EnchanterWizards() -> List[Power]:
    return [
        _EnchanterWizard(
            name="Enchantment Adept",
            min_cr=2,
            max_cr=4,
            spells=EnchanterAdeptSpells,
            power_level=MEDIUM_POWER,
        ),
        _EnchanterWizard(
            name="Enchantment Master",
            min_cr=5,
            max_cr=10,
            spells=EnchanterMasterSpells,
            power_level=HIGH_POWER,
        ),
        _EnchanterWizard(
            name="Enchantment Expert",
            min_cr=11,
            max_cr=40,
            spells=EnchanterExpertSpells,
            power_level=EXTRA_HIGH_POWER,
        ),
    ]
