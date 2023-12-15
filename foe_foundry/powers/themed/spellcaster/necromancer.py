# At will: dancing lights, mage hand, prestidigitation

# 2/day each: bestow curse, dimension door, mage armor, web

# 1/day: circle of death

# Bonus Actions
# Summon Undead (1/Day). The necromancer magically summons five skeletons or zombies (both appear in the Monster Manual). The summoned creatures appear in unoccupied spaces within 60 feet of the necromancer, whom they obey. They take their turns immediately after the necromancer. Each lasts for 1 hour, until it or the necromancer dies, or until the necromancer dismisses it as a bonus action.

# Reactions
# Grim Harvest. When the necromancer kills a creature with necrotic damage, the necromancer regains 9 (2d8) hit points.


from typing import List

from ....attack_template import spell
from ....creature_types import CreatureType
from ....damage import DamageType
from ....features import ActionType, Feature
from ....role_types import MonsterRole
from ....spells import conjuration, illusion, necromancy
from ....statblocks import BaseStatblock
from ....utils import easy_multiple_of_five
from ...power import EXTRA_HIGH_POWER, HIGH_POWER, MEDIUM_POWER
from .base import _Spellcaster
from .utils import spell_list

_adept = [
    necromancy.BestowCurse,
    conjuration.Web,
    necromancy.BlindnessDeafness,
]
_master = [
    conjuration.Cloudkill,
    necromancy.CircleOfDeath,
    illusion.Fear,
]
_expert = [necromancy.Eyebite, necromancy.FingerOfDeath]

NecromancerAdeptSpells = spell_list(spells=_adept, uses=1)
NecromancerMasterSpells = spell_list(spells=_adept, uses=2) + spell_list(spells=_master, uses=1)
NecromancerExpertSpells = (
    spell_list(_adept, uses=3) + spell_list(_master, uses=2) + spell_list(_expert, uses=1)
)


class _NecromancerWizard(_Spellcaster):
    def __init__(self, **kwargs):
        args: dict = (
            dict(
                creature_class="Necromancer",
                theme="necromancy",
                score_args=dict(
                    require_types=[
                        CreatureType.Humanoid,
                        CreatureType.Undead,
                    ],
                    bonus_damage=DamageType.Necrotic,
                    bonus_roles=[
                        MonsterRole.Leader,
                        MonsterRole.Controller,
                        MonsterRole.Artillery,
                    ],
                    attack_names=[
                        spell.Deathbolt,
                        spell.Poisonbolt,
                        spell.Frostbolt,
                    ],  # bonus, not required
                ),
            )
            | kwargs
        )

        super().__init__(**args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        temphp = easy_multiple_of_five(stats.hp.average / 2.5)
        feature = Feature(
            name="Soul Harvest",
            uses=1,
            action=ActionType.Reaction,
            description=f"Whenever a humanoid creature within 60 feet dies or is reduced to 0 hitpoints, {stats.roleref} gains {temphp} temporary hitpoints.",
        )

        return [feature]


def NecromancerWizards() -> List[_Spellcaster]:
    return [
        _NecromancerWizard(
            name="Necromancer Adept",
            min_cr=2,
            max_cr=4,
            spells=NecromancerAdeptSpells,
            power_level=MEDIUM_POWER,
        ),
        _NecromancerWizard(
            name="Necromancer Master",
            min_cr=5,
            max_cr=10,
            spells=NecromancerMasterSpells,
            power_level=HIGH_POWER,
        ),
        _NecromancerWizard(
            name="Necromancer Expert",
            min_cr=11,
            max_cr=40,
            spells=NecromancerExpertSpells,
            power_level=EXTRA_HIGH_POWER,
        ),
    ]
