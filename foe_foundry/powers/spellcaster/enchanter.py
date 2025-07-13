from typing import List

from ...features import ActionType, Feature
from ...power_types import PowerType
from ...spells import enchantment, illusion
from ...statblocks import BaseStatblock
from ..power import Power
from .base import WizardPower
from .utils import spell_list

_adept = [
    enchantment.CharmPerson.copy(upcast=False),
    enchantment.Suggestion,
    enchantment.Command.copy(upcast=False),
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
    spells=_adept,
    uses=2,
    exclude={illusion.Invisibility, enchantment.Suggestion},
    add={enchantment.Suggestion.copy(concentration=False)},
    mark_schools={"enchantment"},
) + spell_list(spells=_master, uses=1, mark_schools={"enchantment"})
EnchanterExpertSpells = (
    spell_list(
        _adept,
        uses=3,
        exclude={illusion.Invisibility, enchantment.Suggestion},
        add={enchantment.Suggestion.copy(concentration=False)},
        mark_schools={"enchantment"},
    )
    + spell_list(_master, uses=2, mark_schools={"enchantment"})
    + spell_list(_expert, uses=1, mark_schools={"enchantment"})
)


class _EnchanterWizard(WizardPower):
    def __init__(self, **kwargs):
        super().__init__(
            creature_name="Enchanter",
            icon="charm",
            power_types=[PowerType.Magic, PowerType.Debuff],
            **kwargs,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Protective Charm",
            uses=1,
            action=ActionType.Reaction,
            description=f"Whenever a visible creature within 30 feet of {stats.selfref} targets it with an ability, spell, or attack roll, {stats.selfref} may use its reaction to cast an Enchantment spell (indicated with a \\*) from its *Spellcasting* trait targeting that creature.",
        )

        return [feature]


def EnchanterWizards() -> List[Power]:
    return [
        _EnchanterWizard(
            name="Enchantment Adept",
            min_cr=4,
            max_cr=5,
            spells=EnchanterAdeptSpells,
        ),
        _EnchanterWizard(
            name="Enchantment Master",
            min_cr=6,
            max_cr=11,
            spells=EnchanterMasterSpells,
        ),
        _EnchanterWizard(
            name="Enchantment Expert",
            min_cr=12,
            max_cr=40,
            spells=EnchanterExpertSpells,
        ),
    ]
