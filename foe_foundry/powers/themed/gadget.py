from datetime import datetime
from math import ceil
from typing import List

from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import LOW_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class GadgetPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        standard_score_args = (
            dict(
                require_types=CreatureType.Humanoid,
                bonus_roles=[
                    MonsterRole.Leader,
                    MonsterRole.Controller,
                    MonsterRole.Ambusher,
                    MonsterRole.Defender,
                ],
            )
            | score_args
        )
        super().__init__(
            name=name,
            source=source,
            create_date=create_date,
            theme="gadget",
            power_type=PowerType.Theme,
            power_level=power_level,
            score_args=standard_score_args,
        )


class _PotionOfHealing(GadgetPower):
    def __init__(self):
        super().__init__(
            name="Potion of Healing",
            source="SRD5.1 Healing Potion",
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        if stats.cr <= 3:
            item = "Potion of Healing"
            healing = DieFormula.from_expression("2d4 + 2")
        elif stats.cr <= 7:
            item = "Potion of Greater Healing"
            healing = DieFormula.from_expression("4d4 + 4")
        elif stats.cr <= 11:
            item = "Potion of Superior Healing"
            healing = DieFormula.from_expression("8d4 + 8")
        else:
            item = "Potion of Supreme Healing"
            healing = DieFormula.from_expression("10d4 + 10")

        uses = int(ceil(min(3, stats.cr / 8)))

        feature = Feature(
            name="Potion of Healing",
            action=ActionType.BonusAction,
            uses=uses,
            description=f"{stats.selfref.capitalize()} consumes a {item} and regains {healing.description} hitpoints",
        )

        return [feature]


class _SmokeBomb(GadgetPower):
    def __init__(self):
        super().__init__(
            name="Smoke Bomb",
            source="Foe Foundry",
            power_level=LOW_POWER,
            require_attack_types=AttackType.All() - AttackType.AllSpell(),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        distance = easy_multiple_of_five(5 + stats.cr / 5, min_val=10, max_val=30)
        rounds = DieFormula.from_expression("1d4 + 2")

        feature = Feature(
            name="Smoke Bomb",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} throws a smoke bomb at a point they can see within 30 feet. A thick obscuring cloud of smoke billows forth and fills a {distance} ft radius sphere. \
                The smoke lasts for {rounds.description} rounds and can be dispersed with a light wind.",
        )
        return [feature]


def _NetPowers() -> List[Power]:
    examples: List[dict] = [
        dict(name="Net", ac=10, hp=10, additional="", min_cr=0, max_cr=3),
        dict(
            name="Barbed Net",
            ac=12,
            hp=15,
            min_cr=4,
            max_cr=7,
            additional=" Whenever a creature uses an action to break the grapple or attack the net, they suffer {dmg} piercing damage",
        ),
        dict(
            name="Grounding Net",
            ac=14,
            hp=20,
            min_cr=8,
            max_cr=11,
            additional=" Whenever a creature attempts to cast a spell while grappled in this way, they must succeed on a DC {dc} concentration check. On a failure, the spell fails.",
        ),
        dict(
            name="Infused Net",
            ac=16,
            hp=25,
            min_cr=12,
            max_cr=None,
            additional=" A creature grappled in this way suffers {dmg} ongoing {dmg_type} damage at the start of each of its turn, \
                and whenever the creature attempts to cast a spell it must succeed on a DC {dc} concentration check. On a failure, the spell fails.",
        ),
    ]

    class _Net(GadgetPower):
        def __init__(
            self,
            name: str,
            ac: int,
            hp: int,
            min_cr: int,
            max_cr: int | None,
            additional: str,
        ):
            def within_cr_range(c: BaseStatblock) -> bool:
                return (min_cr <= c.cr) and (c.cr <= (max_cr or 100))

            super().__init__(
                name=name,
                source="Foe Foundry",
                power_level=LOW_POWER,
                require_attack_types=AttackType.All() - AttackType.AllSpell(),
                require_cr=min_cr,
                require_callback=within_cr_range,
            )
            self.ac = ac
            self.hp = hp
            self.additional = additional

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            dc = stats.difficulty_class_easy
            distance = easy_multiple_of_five(stats.cr, min_val=5, max_val=15)
            dmg = int(ceil(0.25 * stats.attack.average_damage))
            dmg_type = stats.secondary_damage_type or stats.primary_damage_type
            additional = self.additional.format(dmg=dmg, dmg_type=dmg_type, dc=dc)

            feature = Feature(
                name=self.name,
                action=ActionType.Action,
                replaces_multiattack=1,
                uses=1,
                description=f"{stats.selfref.capitalize()} throws a net at a point they can see within 30 feet. Each creature within {distance} feet must make a DC {dc} Strength save. \
                    On a failure, they are **Grappled** (escape DC {dc}) and **Restrained** while grappled in this way. The net has AC {self.ac} and {self.hp} hp.{additional}",
            )
            return [feature]

    return [_Net(**example) for example in examples]


def _GrenadePowers() -> List[Power]:
    class _Grenade(GadgetPower):
        def __init__(self, dmg_type: DamageType):
            self.dmg_type = dmg_type
            super().__init__(
                name=f"{self.dmg_type.adj.capitalize()} Grenade",
                source="Foe Foundry",
                require_attack_types=AttackType.All() - AttackType.AllSpell(),
                require_damage=dmg_type,
            )

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            dmg = stats.target_value(1.25, suggested_die=Die.d6)
            radius = 15
            distance = 30
            dc = stats.difficulty_class_easy
            feature = Feature(
                name=self.name,
                action=ActionType.Action,
                uses=1,
                replaces_multiattack=2,
                description=f"{stats.selfref.capitalize()} hurls a {self.name} at a point they can see within {distance} ft. The grenade explodes in a {radius} ft sphere. \
                    Each creature in the area must make a DC {dc} Dexterity saving throw or take {dmg.description} {self.dmg_type} damage. On a success, the creature takes half as much damage.",
            )

            return [feature]

    return [
        _Grenade(dmg_type)
        for dmg_type in [
            DamageType.Fire,
            DamageType.Thunder,
            DamageType.Necrotic,
            DamageType.Acid,
            DamageType.Poison,
            DamageType.Cold,
            DamageType.Lightning,
        ]
    ]


PotionOfHealing: Power = _PotionOfHealing()
GrenadePowers: List[Power] = _GrenadePowers()
NetPowers: List[Power] = _NetPowers()
SmokeBomb: Power = _SmokeBomb()


GadgetPowers: List[Power] = [PotionOfHealing, SmokeBomb] + GrenadePowers + NetPowers
