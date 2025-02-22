from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set

import numpy as np

from foe_foundry.features import ActionType
from foe_foundry.powers import Power, PowerType
from foe_foundry.statblocks import BaseStatblock

from .score import SelectionScore
from .targets import SelectionTargets


@dataclass(kw_only=True)
class PowerSelection:
    selected_powers: Set[Power] = field(default_factory=set)
    selected_power_level: float = 0
    selected_bonus_actions: int = 0
    selected_reactions: int = 0
    selected_recharges: int = 0
    selected_limited_uses: int = 0
    selected_attack_modifiers: int = 0
    selected_spellcasting_powers: int = 0

    def with_new_power(self, stats: BaseStatblock, power: Power) -> PowerSelection:
        recharges = self.selected_recharges
        bonus_actions = self.selected_bonus_actions
        reactions = self.selected_reactions
        attack_modifiers = self.selected_attack_modifiers
        power_level = self.selected_power_level
        limited_uses = self.selected_limited_uses
        spellcasting_powers = self.selected_spellcasting_powers + (
            1 if power.power_type == PowerType.Spellcasting else 0
        )

        new_features = power.generate_features(stats)
        for feature in new_features:
            if feature.recharge:
                recharges += 1
            if feature.action == ActionType.BonusAction:
                bonus_actions += 1
            if feature.action == ActionType.Reaction:
                reactions += 1
            if feature.modifies_attack:
                attack_modifiers += 1
            if feature.uses:
                limited_uses += 1

        new_powers = self.selected_powers.copy()
        new_powers.add(power)
        power_level = self.selected_power_level + power.power_level

        return PowerSelection(
            selected_powers=new_powers,
            selected_power_level=power_level,
            selected_bonus_actions=bonus_actions,
            selected_reactions=reactions,
            selected_recharges=recharges,
            selected_attack_modifiers=attack_modifiers,
            selected_limited_uses=limited_uses,
            selected_spellcasting_powers=spellcasting_powers,
        )

    def score(self, target: SelectionTargets) -> SelectionScore:
        score_over_target = self.selected_power_level - target.power_level_target
        score_over_max = self.selected_power_level - target.power_level_max

        bonus_over_target = self.selected_bonus_actions - target.bonus_action_target
        bonus_over_max = self.selected_bonus_actions - target.bonus_action_max

        reactions_over_target = self.selected_reactions - target.reaction_target
        reactions_over_max = self.selected_reactions - target.reaction_max

        recharges_over_target = self.selected_recharges - target.recharge_target
        recharges_over_max = self.selected_recharges - target.recharge_max

        attack_modifiers_over_target = (
            self.selected_attack_modifiers - target.attack_modifier_target
        )
        attack_modifiers_over_max = (
            self.selected_attack_modifiers - target.attack_modifier_max
        )

        limited_uses_over_target = (
            self.selected_limited_uses - target.limited_uses_target
        )
        limited_uses_over_max = self.selected_limited_uses - target.limited_uses_max

        spellcasting_over_target = (
            self.selected_spellcasting_powers - target.spellcasting_powers_target
        )
        spellcasting_over_max = (
            self.selected_spellcasting_powers - target.spellcasting_powers_max
        )

        above_targets = np.array(
            [
                self.selected_bonus_actions > target.bonus_action_target,
                self.selected_reactions > target.reaction_target,
                self.selected_recharges > target.recharge_target,
                self.selected_attack_modifiers > target.attack_modifier_target,
                self.selected_limited_uses > target.limited_uses_target,
                self.selected_spellcasting_powers > target.spellcasting_powers_target,
            ]
        )
        below_targets = np.array(
            [
                self.selected_bonus_actions < target.bonus_action_target,
                self.selected_reactions < target.reaction_target,
                self.selected_recharges < target.recharge_target,
                self.selected_attack_modifiers < target.attack_modifier_target,
                self.selected_limited_uses < target.limited_uses_target,
                self.selected_spellcasting_powers < target.spellcasting_powers_target,
            ]
        )

        # gain points for power level selected
        score_raw = self.selected_power_level

        penalties = 0

        # lose a little for being above target score
        # lose a lot for being above max score
        penalties += 1.5 * max(score_over_target, 0)
        penalties += 3 * max(score_over_max, 0)

        # lose points if you're above max in various categories
        penalties += 1 * max(bonus_over_max, 0)
        penalties += 1 * max(reactions_over_max, 0)
        penalties += 2 * max(recharges_over_max, 0)
        penalties += 2 * max(limited_uses_over_max, 0)
        penalties += 2 * max(spellcasting_over_max, 0)
        penalties += 3 * max(
            attack_modifiers_over_max, 0
        )  # high bc statblock becomes confusing

        # lose points if you're above target in some areas and below target in others
        if np.any(above_targets) and np.any(below_targets):
            c = np.sum(above_targets) + np.sum(below_targets)
            penalties += 0.25 * c

        return SelectionScore(
            score=score_raw - penalties,
            score_raw=score_raw,
            penalties=penalties,
            bonus_over_target=bonus_over_target,
            bonus_over_max=bonus_over_max,
            reactions_over_target=reactions_over_target,
            reactions_over_max=reactions_over_max,
            recharges_over_target=recharges_over_target,
            recharges_over_max=recharges_over_max,
            limited_uses_over_target=limited_uses_over_target,
            limited_uses_over_max=limited_uses_over_max,
            attack_modifiers_over_target=attack_modifiers_over_target,
            attack_modifiers_over_max=attack_modifiers_over_max,
            remaining_power=target.power_level_target - self.selected_power_level,
            spellcasting_over_target=spellcasting_over_target,
            spellcasting_over_max=spellcasting_over_max,
        )
