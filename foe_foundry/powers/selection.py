from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Callable, List, Set, Tuple, TypeAlias

import numpy as np
from numpy.random import Generator

from ..features import ActionType, Feature
from ..statblocks import BaseStatblock
from ..utils.rng import RngFactory, rng_instance
from .creatures import CreaturePowers
from .power import MEDIUM_POWER, Power, PowerType
from .roles import RolePowers
from .themed import ThemedPowers

Filter: TypeAlias = Callable[[Feature], bool]


@dataclass(kw_only=True)
class SelectionTargets:
    bonus_action_target: int = 1
    bonus_action_max: int = 2

    reaction_target: int = 1
    reaction_max: int = 2

    recharge_target: int = 1
    recharge_max: int = 1

    attack_modifier_target: int = 1
    attack_modifier_max: int = 1

    limited_uses_target: int = 1
    limited_uses_max: int = 2

    spellcasting_powers_target: int = 1
    spellcasting_powers_max: int = 1

    power_level_target: float
    power_level_max: float

    def copy(self, **kwargs) -> SelectionTargets:
        args = asdict(self)
        args.update(kwargs)
        return SelectionTargets(**args)


@dataclass(kw_only=True)
class SelectionScore:
    score: float
    score_raw: float
    penalties: float

    remaining_power: float

    bonus_over_target: int
    bonus_over_max: int

    reactions_over_target: int
    reactions_over_max: int

    recharges_over_target: int
    recharges_over_max: int

    attack_modifiers_over_target: int
    attack_modifiers_over_max: int

    limited_uses_over_target: int
    limited_uses_over_max: int

    spellcasting_over_target: int
    spellcasting_over_max: int


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


class _PowerSelector:
    def __init__(
        self,
        targets: SelectionTargets,
        rng: Generator,
        stats: BaseStatblock,
        custom_filter: Callable[[Power], bool] | None = None,
        custom_weights: Callable[[Power], float] | None = None,
    ):
        self.selection = PowerSelection()
        self.targets = targets
        self.rng = rng
        self.iteration = 0
        self.custom_filter = custom_filter
        self.custom_weights = custom_weights
        self.stats = stats.copy()

    @property
    def is_done(self) -> bool:
        return self.selection.selected_power_level >= self.targets.power_level_target

    @property
    def score(self) -> SelectionScore:
        return self.selection.score(self.targets)

    def select_powers(self):
        while not self.is_done:
            power = self.select_next()
            if power is None:
                break
            self.selection = self.selection.with_new_power(self.stats, power)
            self.stats = power.modify_stats(self.stats)
            self.iteration += 1

    def filter_power_against_max(self, power: Power) -> bool:
        score = self.score
        if (
            power.power_type == PowerType.Spellcasting
            and score.spellcasting_over_max >= 0
        ):
            return False

        return True

    def filter_feature_against_max(self, feature: Feature) -> bool:
        score = self.score
        if feature.action == ActionType.BonusAction and score.bonus_over_max >= 0:
            return False
        if feature.action == ActionType.Reaction and score.reactions_over_max >= 0:
            return False
        if feature.recharge and score.recharges_over_max >= 0:
            return False
        if feature.modifies_attack and score.attack_modifiers_over_max >= 0:
            return False
        if feature.uses and score.limited_uses_over_max >= 0:
            return False

        return True

    def filter_power_against_target(self, power: Power) -> bool:
        score = self.score
        if (
            power.power_type == PowerType.Spellcasting
            and score.spellcasting_over_target >= 0
        ):
            return False

        return True

    def filter_feature_against_target(self, feature: Feature) -> bool:
        score = self.score
        if feature.action == ActionType.BonusAction and score.bonus_over_target >= 0:
            return False
        if feature.action == ActionType.Reaction and score.reactions_over_target >= 0:
            return False
        if feature.recharge and score.recharges_over_target >= 0:
            return False
        if feature.modifies_attack and score.attack_modifiers_over_target >= 0:
            return False
        if feature.uses and score.limited_uses_over_target >= 0:
            return False
        return True

    def filter(self, power: Power) -> bool:
        score = self.score

        if power.power_level > score.remaining_power:
            return False

        if power in self.selection.selected_powers:
            return False

        if self.custom_filter is not None and not self.custom_filter(power):
            return False

        if not self.filter_power_against_max(power) or any(
            not self.filter_feature_against_max(f)
            for f in power.generate_features(self.stats)
        ):
            return False

        return True

    def score_multiplier(self, power: Power) -> float:
        multiplier = 1.0

        # if the creature doesn't have any high power abilities then make high power more attractive
        if power.power_level > MEDIUM_POWER and not any(
            p for p in self.selection.selected_powers if p.power_level > MEDIUM_POWER
        ):
            multiplier += 0.5

        # if the creature doesn't yet have any Creature powers then make them more attractive
        if power.power_type == PowerType.Creature and not any(
            p
            for p in self.selection.selected_powers
            if p.power_type == PowerType.Creature
        ):
            multiplier += 0.75

        # if the creature doesn't yet have any Theme powers then make them more attractive
        if power.power_type == PowerType.Role and not any(
            p for p in self.selection.selected_powers if p.power_type == PowerType.Role
        ):
            multiplier += 0.75

        # if feature would cause us to go above target then make it less attractive
        # don't eliminate it entirely because it might lead to total infeasibility
        if not self.filter_power_against_target(power) or any(
            not self.filter_feature_against_target(f)
            for f in power.generate_features(self.stats)
        ):
            multiplier -= 0.9

        return multiplier

    def select_next(self) -> Power | None:
        candidates, scores = self.get_candidates()

        weights = np.copy(scores)
        if (weights == 0).all() or len(weights) == 0:
            return None

        p = np.exp(2 * weights)
        p = p / np.sum(p)
        indx = self.rng.choice(a=len(candidates), size=None, p=p)
        return candidates[indx]

    def get_candidates(self) -> Tuple[List[Power], np.ndarray]:
        all_powers: List[Power] = CreaturePowers + RolePowers + ThemedPowers

        candidates: List[Power] = []
        scores = []

        for power in all_powers:
            custom_score = self.custom_weights(power) if self.custom_weights else 1.0
            score = (
                power.score(self.stats, relaxed_mode=custom_score > 1.0) * custom_score
            )

            if score <= 0 or not self.filter(power):
                continue

            multiplier = self.score_multiplier(power)
            modifier_score = score * multiplier

            candidates.append(power)
            scores.append(modifier_score)

        scores = np.array(scores, dtype=float)
        candidates = np.array(candidates, dtype=object)  # type: ignore

        indexes = scores > 0
        scores = scores[indexes]
        candidates = candidates[indexes].tolist()  # type: ignore

        return candidates, scores


def select_powers(
    stats: BaseStatblock,
    rng: RngFactory | Generator,
    power_level: float,
    retries: int = 3,
    custom_filter: Callable[[Power], bool] | None = None,
    custom_weights: Callable[[Power], float] | None = None,
) -> Tuple[BaseStatblock, List[Feature]]:
    rng = rng_instance(rng)

    targets = SelectionTargets(
        power_level_target=power_level, power_level_max=power_level + 0.5
    )

    all_results: List[BaseStatblock] = []
    all_scores: List[float] = []
    all_powers: List[Set[Power]] = []

    # try a couple of times and choose the best result
    for _ in range(retries):
        selector = _PowerSelector(
            targets=targets,
            rng=rng,
            stats=stats,
            custom_filter=custom_filter,
            custom_weights=custom_weights,
        )
        selector.select_powers()
        all_results.append(selector.stats)
        all_scores.append(selector.score.score)
        all_powers.append(selector.selection.selected_powers)

    indx = np.argmax(all_scores)
    new_stats = all_results[indx]
    powers = all_powers[indx]

    features = set()
    for power in powers:
        features.update(power.generate_features(new_stats))

    return new_stats, list(features)
