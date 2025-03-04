from typing import List

from ...attack_template import spell
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, conditions
from ...die import Die
from ...features import ActionType, Feature
from ...spells import conjuration, evocation, necromancy
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, Power
from .base import _Wizard
from .utils import spell_list


class Pyromancer(_Wizard):
    def __init__(self):
        super().__init__(
            name="Pyromancer",
            min_cr=4,
            spells=spell_list(
                [evocation.HeatMetal, evocation.Fireball, evocation.WallOfFire], uses=1
            ),
            theme="elementalist",
            creature_class="Pyromancer",
            power_level=HIGH_POWER,
            score_args=dict(
                require_attack_types=AttackType.AllSpell(),
                require_damage=DamageType.Fire,
                require_damage_exact_match=True,
                attack_names={spell.Firebolt},  # not required
                bonus_types=[CreatureType.Elemental, CreatureType.Humanoid],
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


class Cryomancer(_Wizard):
    def __init__(self):
        super().__init__(
            name="Cryomancer",
            min_cr=4,
            spells=spell_list(
                [conjuration.FogCloud, evocation.ConeOfCold, evocation.IceStorm], uses=1
            ),
            theme="elementalist",
            creature_class="Cryomancer",
            power_level=HIGH_POWER,
            score_args=dict(
                require_attack_types=AttackType.AllSpell(),
                require_damage=DamageType.Cold,
                require_damage_exact_match=True,
                attack_names={spell.Frostbolt},  # not required
                bonus_types=[CreatureType.Elemental, CreatureType.Humanoid],
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


class Electromancer(_Wizard):
    def __init__(self):
        super().__init__(
            name="Electromancer",
            min_cr=4,
            spells=spell_list(
                [evocation.GustOfWind, evocation.LightningBolt, evocation.Thunderwave],
                uses=1,
            ),
            theme="elementalist",
            creature_class="Electromancer",
            power_level=HIGH_POWER,
            score_args=dict(
                require_attack_types=AttackType.AllSpell(),
                require_damage=DamageType.Lightning,
                require_damage_exact_match=True,
                attack_names={spell.Shock},  # not required
                bonus_types=[CreatureType.Elemental, CreatureType.Humanoid],
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


class Toximancer(_Wizard):
    def __init__(self):
        super().__init__(
            name="Toximancer",
            min_cr=4,
            spells=spell_list(
                [conjuration.Cloudkill, necromancy.Contagion, evocation.AcidArrow],
                uses=1,
            ),
            theme="elementalist",
            creature_class="Toximancer",
            power_level=HIGH_POWER,
            score_args=dict(
                require_attack_types=AttackType.AllSpell(),
                require_damage=DamageType.Poison,
                require_damage_exact_match=True,
                attack_names={spell.Poisonbolt},  # not required
                bonus_types=[CreatureType.Elemental, CreatureType.Humanoid],
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


def ElementalistWizards() -> List[Power]:
    return [
        Pyromancer(),
        Cryomancer(),
        Electromancer(),
        Toximancer(),
    ]
