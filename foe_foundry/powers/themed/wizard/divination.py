from datetime import datetime
from typing import List

from ....attack_template import spell
from ....creature_types import CreatureType
from ....damage import DamageType
from ....role_types import MonsterRole
from ....spells import conjuration, divination, enchantment, evocation, illusion, transmutation
from .base import _Wizard
from .utils import spell_list

_adept = [
    divination.DetectMagic,
    divination.DetectThoughts,
    divination.ArcaneEye,
    illusion.Invisibility,
    enchantment.HoldPerson,
    transmutation.Fly,
]
_master = [
    evocation.LightningBolt,
    divination.Scrying,
    illusion.GreaterInvisibility,
]
_expert = [conjuration.Maze, divination.Foresight]

DivinationAdeptSpells = spell_list(_adept, uses=1)
DivinationMasterSpells = spell_list(
    _adept, uses=2, exclude={illusion.Invisibility}
) + spell_list(_master, uses=1)
DivinationExpertSpells = (
    spell_list(_adept, uses=3, exclude={illusion.Invisibility})
    + spell_list(_master, uses=2)
    + spell_list(_expert, uses=1)
)


def DivinationWizards() -> List[_Wizard]:
    args: dict = dict(
        creature_class="Diviner",
        theme="divination",
        score_args=dict(
            require_types=[
                CreatureType.Humanoid,
                CreatureType.Fey,
                CreatureType.Celestial,
                CreatureType.Aberration,
            ],
            bonus_damage=DamageType.Psychic,
            bonus_roles=MonsterRole.Controller,
            attack_names=[
                spell.Gaze,
                spell.EdlritchBlast,
                spell.ArcaneBurst,
            ],  # bonus, not required
        ),
    )

    return [
        _Wizard(
            name="Diviniation Adept", min_cr=2, max_cr=4, spells=DivinationAdeptSpells, **args
        ),
        _Wizard(
            name="Divination Master", min_cr=5, max_cr=10, spells=DivinationMasterSpells, **args
        ),
        _Wizard(
            name="Diviniation Expert",
            min_cr=11,
            max_cr=40,
            spells=DivinationExpertSpells,
            **args
        ),
    ]
