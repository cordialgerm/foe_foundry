from typing import List

from ...attack_template import natural, weapon
from ...creature_types import CreatureType
from ...damage import conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, LOW_POWER, Power, PowerType, PowerWithStandardScoring


class _Dueling(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Dueling",
            source="Foe Foundry",
            theme="fighting_style",
            power_type=PowerType.Theme,
            score_args=dict(
                bonus_roles=[MonsterRole.Skirmisher, MonsterRole.Leader],
                attack_names=[
                    "-",
                    weapon.MaceAndShield,
                    weapon.SpearAndShield,
                    weapon.SpearAndShield,
                    weapon.JavelinAndShield,
                    weapon.RapierAndShield,
                ],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Expert Duelist",
            action=ActionType.Feature,
            description=f"If {stats.selfref} makes a melee attack against a creature, then that creature can't make opportunity attacks against {stats.selfref} until the end of {stats.selfref}'s turn.",
        )
        return [feature]


class _ExpertBrawler(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Expert Brawler",
            source="Foe Foundry",
            theme="fighting_style",
            power_type=PowerType.Theme,
            score_args=dict(
                require_types=[CreatureType.Humanoid, CreatureType.Giant],
                bonus_roles=[MonsterRole.Bruiser, MonsterRole.Controller],
                attack_names={"-", natural.Slam},
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        dmg = stats.target_value(0.2, force_die=Die.d4)
        feature1 = Feature(
            name="Expert Brawler Hit",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
            description=f"On a hit, the target is **Grappled** (escape DC {dc})",
        )

        feature2 = Feature(
            name="Pin",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} pins a creature it is grappling. The creature is **Restrained** while grappled in this way \
                and suffers {dmg.description} ongoing bludgeoning damage at the end of each of its turns.",
        )

        return [feature1, feature2]


class _Interception(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Interception",
            power_type=PowerType.Theme,
            source="SRD5.1 Interception",
            theme="fighting_style",
            score_args=dict(
                attack_names={
                    "-",
                    weapon.SwordAndShield,
                    weapon.SpearAndShield,
                    weapon.Greataxe,
                    weapon.Polearm,
                    weapon.MaceAndShield,
                    weapon.RapierAndShield,
                    weapon.Shortswords,
                },
                require_roles=[MonsterRole.Defender, MonsterRole.Bruiser],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        distance = easy_multiple_of_five(stats.speed.fastest_speed / 2.0, min_val=5, max_val=30)
        feature = Feature(
            name="Interception",
            action=ActionType.Reaction,
            description=f"If a friendly creature within {distance} ft becomes the target of an attack, {stats.selfref} can move up to {distance} ft and intercept the attack. \
                The attack targets {stats.selfref} instead of the original target.",
        )
        return [feature]


class _BaitAndSwitch(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Bait and Switch",
            source="Foe Foundry",
            theme="fighting_style",
            power_level=LOW_POWER,
            power_type=PowerType.Theme,
            score_args=dict(
                require_types=CreatureType.Humanoid,
                require_roles=[
                    MonsterRole.Defender,
                    MonsterRole.Skirmisher,
                    MonsterRole.Leader,
                    MonsterRole.Bruiser,
                ],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        bonus = stats.attributes.primary_mod
        feature = Feature(
            name="Bait and Switch",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} switches places with a friendly creature within 5 feet. \
                Until the end of its next turn, the friendly creature gains a +{bonus} bonus to its AC.",
        )
        return [feature]


class _QuickToss(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Quick Toss",
            source="Foe Foundry",
            theme="fighting_style",
            power_type=PowerType.Theme,
            score_args=dict(
                attack_names={
                    "-",
                    weapon.JavelinAndShield,
                    weapon.Daggers,
                },
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        attack = stats.attack.name
        feature = Feature(
            name="Quick Toss",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} makes a {attack} attack as a bonus action",
        )
        return [feature]


class _ArmorMaster(PowerWithStandardScoring):
    def __init__(self):
        def is_heavily_armored(b: BaseStatblock) -> bool:
            for c in b.ac_templates:
                if c.is_heavily_armored and c.resolve(b, uses_shield=False).score > 0:
                    return True

            return False

        super().__init__(
            name="Armor Master",
            source="A5E SRD Heavy Armor Expertise",
            power_type=PowerType.Theme,
            score_args=dict(require_callback=is_heavily_armored),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        reduction = stats.attributes.proficiency
        feature = Feature(
            name="Armor Master",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} reduces the amount of bludgeoning, piercing, and slashing damage it receives by {reduction}.",
        )
        return [feature]


class _ShieldMaster(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Shield Master",
            source="A5E SRD Shield Focus",
            theme="fighting_style",
            power_level=LOW_POWER,
            power_type=PowerType.Theme,
            score_args=dict(require_shield=True),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Shield Slam",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} shoves a creature within 5 feet. It must make a DC {dc} Strength save or be pushed up to 5 feet and fall **Prone**.",
        )
        return [feature]


class _PolearmMaster(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Polearm Master",
            source="A5E SRD Polearm Savant",
            theme="fighting_style",
            power_type=PowerType.Theme,
            score_args=dict(
                attack_names={"-", weapon.Polearm}, bonus_roles=MonsterRole.Defender
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Polearm Master",
            action=ActionType.Reaction,
            description=f"Whenever a hostile creature enters {stats.selfref.capitalize()}'s reach, it may make an attack of opportunity against that creature.",
        )
        return [feature]


class _OverpoweringStrike(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Great Weapon Fighting",
            source="Foe Foundry",
            theme="fighting_style",
            power_type=PowerType.Theme,
            power_level=HIGH_POWER,
            score_args=dict(
                attack_names={
                    "-",
                    weapon.Polearm,
                    weapon.Greataxe,
                    weapon.Greatsword,
                    weapon.Maul,
                }
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(1.7, force_die=Die.d12)
        dmg_type = stats.attack.damage.damage_type
        feature = Feature(
            name="Overpowering Strike",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} makes an overpowering strike against a creature within 5 feet. The target must make a DC {dc} Strength saving throw. \
                On a failure, it takes {dmg.description} {dmg_type} damage and is knocked **Prone**. On a success, it instead takes half damage.",
        )
        return [feature]


class _WhirlwindOfSteel(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Whirlwind of Steel",
            source="Foe Foundry",
            theme="fighting_style",
            power_type=PowerType.Theme,
            score_args=dict(
                attack_names={
                    "-",
                    weapon.Daggers,
                    weapon.Shortswords,
                }
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class

        dmg = stats.target_value(1.0, force_die=Die.d6, force_even=True)
        bleed_dmg = DieFormula.from_dice(d6=dmg.n_die // 2)
        bleeding = conditions.Bleeding(damage=bleed_dmg)

        dmg_type = stats.attack.damage.damage_type
        feature = Feature(
            name="Whirlwind of Steel",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} makes a lightning-fast flurry of strikes at a creature within 5 feet. The target must make a DC {dc} Dexterity saving throw. \
                On a failure, it takes {dmg.description} {dmg_type} damage and is {bleeding.description}. On a success, it instead takes half damage. {bleeding.description_3rd}",
        )
        return [feature]


class _Sharpshooter(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Sharpshooter's Shot",
            source="Foe Foundry",
            theme="fighting_style",
            power_type=PowerType.Theme,
            power_level=HIGH_POWER,
            score_args=dict(
                require_roles=MonsterRole.Artillery,
                attack_names={
                    "-",
                    weapon.Longbow,
                    weapon.Shortbow,
                    weapon.Crossbow,
                },
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        distance = stats.attack.range_max or stats.attack.range
        dmg = stats.target_value(1.5)
        dmg_type = stats.attack.damage.damage_type
        dazed = conditions.Dazed()
        feature = Feature(
            name="Sharpshooter's Shot",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} fires a deadly shot at a creature it can see within {distance} ft. The target must make a DC {dc} Dexterity saving throw. \
                On a failure, it takes {dmg.description} {dmg_type} damage and is {dazed.caption} until the end of its next turn. {dazed.description_3rd}",
        )
        return [feature]


ArmorMaster: Power = _ArmorMaster()
BaitAndSwitch: Power = _BaitAndSwitch()
Dueling: Power = _Dueling()
ExpertBrawler: Power = _ExpertBrawler()
Interception: Power = _Interception()
OverpoweringStrike: Power = _OverpoweringStrike()
PolearmMaster: Power = _PolearmMaster()
QuickToss: Power = _QuickToss()
Sharpshooter: Power = _Sharpshooter()
ShieldMaster: Power = _ShieldMaster()
WhirlwindOfSteel: Power = _WhirlwindOfSteel()

FightingStylePowers: List[Power] = [
    ArmorMaster,
    BaitAndSwitch,
    Dueling,
    ExpertBrawler,
    Interception,
    OverpoweringStrike,
    PolearmMaster,
    QuickToss,
    Sharpshooter,
    ShieldMaster,
    WhirlwindOfSteel,
]
