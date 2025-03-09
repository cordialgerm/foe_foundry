from typing import List

from ...attack_template import AttackTemplate, spell
from ...damage import conditions
from ...die import Die
from ...features import ActionType, Feature
from ...spells import StatblockSpell, conjuration, evocation, necromancy
from ...statblocks import BaseStatblock
from ..power import Power
from .base import WizardPower
from .utils import spell_list


class _Elementalist(WizardPower):
    def __init__(self, name: str, attack: AttackTemplate, spells: List[StatblockSpell]):
        super().__init__(name=name, creature_name=name, min_cr=4, spells=spells)
        self.attack = attack

    # def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
    #     stats = super().modify_stats_inner(stats)
    #     stats = self.attack.alter_base_stats(stats)
    #     stats = self.attack.initialize_attack(stats)
    #     stats = stats.copy(secondary_damage_type=self.attack.damage_type)
    #     return stats


class _Pyromancer(_Elementalist):
    def __init__(self):
        super().__init__(
            name="Pyromancer",
            attack=spell.Firebolt,
            spells=spell_list(
                [
                    evocation.HeatMetal.copy(concentration=False),
                    evocation.Fireball,
                    evocation.WallOfFire,
                ],
                uses=1,
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        damage = stats.target_value(0.25, force_die=Die.d10)
        burning = conditions.Burning(damage)

        feature = Feature(
            name="Ignite",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"Immediately after dealing fire damage to a target that {stats.selfref} can see within 60 feet, it causes that target to ignite and gain {burning.caption}. {burning.description_3rd}",
        )

        return [feature]


class _Cryomancer(_Elementalist):
    def __init__(self):
        super().__init__(
            name="Cryomancer",
            attack=spell.Frostbolt,
            spells=spell_list(
                [
                    conjuration.FogCloud.copy(concentration=False),
                    evocation.ConeOfCold,
                    evocation.IceStorm,
                ],
                uses=1,
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        frozen = conditions.Frozen(dc=dc)

        feature = Feature(
            name="Flash Freeze",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"Immediately after dealing cold damage to a target that {stats.selfref} can see within 60 feet, it causes that target to make a DC {dc} Constitution saving throw. \
                On a failed save, the target gains {frozen.caption}. {frozen.description_3rd}",
        )

        return [feature]


class _Electromancer(_Elementalist):
    def __init__(self):
        super().__init__(
            name="Electromancer",
            attack=spell.Shock,
            spells=spell_list(
                [
                    evocation.GustOfWind.copy(concentration=False),
                    evocation.LightningBolt,
                    evocation.Thunderwave,
                ],
                uses=1,
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        shocked = conditions.Shocked()
        dc = stats.difficulty_class
        feature = Feature(
            name="Dazing Shock",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"Immediately after dealing lightning damage to a target that {stats.selfref} can see within 60 feet, it causes that target to make a DC {dc} Constitution saving throw. \
                On a failed save, the target gains {shocked.caption} until the end of its next turn. {shocked.description_3rd}",
        )
        return [feature]


class _Toximancer(_Elementalist):
    def __init__(self):
        super().__init__(
            name="Toximancer",
            attack=spell.Poisonbolt,
            spells=spell_list(
                [conjuration.Cloudkill, necromancy.Contagion, evocation.AcidArrow],
                uses=1,
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        weakened = conditions.Weakened(save_end_of_turn=True)
        dc = stats.difficulty_class
        feature = Feature(
            name="Sapping Poison",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"Immediately after dealing poison damage to a target that {stats.selfref} can see within 60 feet, it causes that target to make a DC {dc} Constitution saving throw. \
                On a failed save, the target gains {weakened.caption} until the end of its next turn. {weakened.description_3rd}",
        )
        return [feature]


Pyromancer: Power = _Pyromancer()
Cryomancer: Power = _Cryomancer()
Electromancer: Power = _Electromancer()
Toximancer: Power = _Toximancer()


ElementalistWizards: List[Power] = [
    Pyromancer,
    Cryomancer,
    Electromancer,
    Toximancer,
]
