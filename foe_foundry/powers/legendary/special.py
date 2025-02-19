from typing import Iterable

import numpy as np

from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ...utils.rounding import easy_multiple_of_five
from ..spell import StatblockSpell
from .score import LegendaryActionScore, LegendaryActionType


def special(
    stats: BaseStatblock, features: list[Feature]
) -> Iterable[LegendaryActionScore]:
    # Spellcasting
    if len(stats.spells):
        spells = np.array(stats.spells, dtype=object)
        uses = np.array([s.uses or -1 for s in stats.spells])
        min_uses = np.min(uses)
        min_use_indexes = uses == min_uses

        candidates = spells[min_use_indexes]
        legendary_spells: list[StatblockSpell]
        if len(candidates > 1):
            lowest_level = np.min([s.level for s in candidates])
            lowest_level_indexes = [s.level == lowest_level for s in candidates]
            legendary_spells = candidates[lowest_level_indexes].tolist()  # type: ignore
        else:
            legendary_spells = candidates.tolist()  # type: ignore

        spell_names = " or ".join(s.name for s in legendary_spells)

        yield LegendaryActionScore(
            feature=Feature(
                name="Spellcasting",
                description=f"{stats.selfref.title()} uses Spellcasting to cast {spell_names}. It can't take this action again until the start of its next turn.",
                action=ActionType.Legendary,
            ),
            types={LegendaryActionType.special},
            score=5,
        )

    # Recharge Ability
    recharge = [r for r in features if r.action == ActionType.Action and r.recharge]

    if len(recharge):
        recharge_text = (
            f"its {recharge[0].name} ability"
            if len(recharge) == 1
            else "one of its Recharge abilities"
        )

        name = "Recharge" if len(recharge) > 1 else recharge[0].name

        yield LegendaryActionScore(
            feature=Feature(
                name=name,
                action=ActionType.Legendary,
                description=f"{stats.selfref.title()} uses or attempts to recharge {recharge_text}. It can't take this action again until the start of its next turn.",
            ),
            types={LegendaryActionType.special},
            score=2,
        )

    # Limited Use Abilities
    limited_uses = [f for f in features if f.action == ActionType.Action and f.uses]
    if len(limited_uses):
        limited_uses_text = (
            f"{stats.selfref.title()} uses {limited_uses[0].name}"
            if len(limited_uses) == 1
            else f"{stats.selfref.title()} uses one of its limited use abilities"
        )
        name = "Limited Use" if len(limited_uses) > 1 else limited_uses[0].name
        yield LegendaryActionScore(
            feature=Feature(
                name=name,
                action=ActionType.Legendary,
                description=f"{limited_uses_text}. It can't take this action again until the start of its next turn.",
            ),
            types={LegendaryActionType.special},
            score=1,
        )

    # Fallback
    temp = easy_multiple_of_five(0.75 * stats.cr, min_val=5)
    yield LegendaryActionScore(
        feature=Feature(
            name="Replenish",
            description=f"{stats.selfref.title()} gains {temp} temporary hitpoints. It can't take this action again until the start of its next turn.",
            action=ActionType.Legendary,
        ),
        types={LegendaryActionType.special},
        score=0,
    )
