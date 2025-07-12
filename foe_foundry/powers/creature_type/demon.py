from datetime import datetime
from typing import List

from foe_foundry.references import Token, creature_ref, spell_ref

from ...attack_template import natural as natural_attacks
from ...creature_types import CreatureType
from ...damage import Attack, AttackType, Condition, DamageType
from ...die import Die
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...spells import enchantment
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five, summoning
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


def is_demon(c: BaseStatblock) -> bool:
    return c.creature_subtype == "Demon"


class DemonPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = (
            dict(require_types=CreatureType.Fiend, require_callback=is_demon)
            | score_args
        )
        super().__init__(
            name=name,
            source=source,
            power_type=PowerType.CreatureType,
            power_level=power_level,
            create_date=create_date,
            icon=icon,
            theme="Demon",
            reference_statblock="Balor",
            score_args=standard_score_args,
        )


class _FeastOfSouls(DemonPower):
    def __init__(self):
        super().__init__(
            name="Feast of Souls",
            source="Foe Foundry",
            icon="grim-reaper",
            create_date=datetime(2025, 3, 28),
            power_level=LOW_POWER,
            bonus_roles={
                MonsterRole.Bruiser,
                MonsterRole.Soldier,
                MonsterRole.Ambusher,
            },
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        temphp = easy_multiple_of_five(0.1 * stats.hp.average)
        feature = Feature(
            name="Feast of Souls",
            action=ActionType.Reaction,
            description=f"Whenever a creature dies within 120 feet of {stats.selfref} it may choose to gain {temphp} temporary hitpoints, recharge an ability, or regain an expended usage of an ability.",
        )
        return [feature]


class _DemonicBite(DemonPower):
    def __init__(self):
        super().__init__(
            name="Demonic Bite",
            source="Foe Foundry",
            icon="fangs",
            attack_names=natural_attacks.Bite,
            bonus_damage=DamageType.Poison,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        dc = stats.difficulty_class
        poisoned = Condition.Poisoned

        def customize(a: Attack) -> Attack:
            return a.split_damage(DamageType.Poison, split_ratio=0.9)

        stats = stats.add_attack(
            scalar=1.4,
            damage_type=DamageType.Piercing,
            name="Demonic Bite",
            die=Die.d6,
            attack_type=AttackType.MeleeNatural,
            additional_description=f"On a hit, the target must make a DC {dc} Constitution saving throw or become {poisoned.caption} for 1 minute (save ends at end of turn).",
            callback=customize,
        )

        return stats


class _DemonicSummons(DemonPower):
    def __init__(self):
        super().__init__(
            name="Demonic Summons",
            source="Foe Foundry",
            icon="pentacle",
            power_level=HIGH_POWER,
            require_cr=3,
            bonus_roles=MonsterRole.Leader,
            bonus_cr=7,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        _, _, description = summoning.determine_summon_formula(
            summoner=summoning.Demons,
            summon_cr_target=stats.cr / 2.5,
            rng=stats.create_rng("demonic summons"),
        )

        feature = Feature(
            name="Demonic Summons",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} summons forth additional demonic servants. {description}",
        )

        return [feature]


class _WhispersOfTheAbyss(DemonPower):
    def __init__(self):
        super().__init__(
            name="Whispers of the Abyss",
            source="Foe Foundry",
            icon="daemon-pull",
            power_level=HIGH_POWER,
            require_cr=3,
            bonus_roles={MonsterRole.Controller, MonsterRole.Artillery},
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(dpr_proportion=0.6, force_die=Die.d6)
        confusion = spell_ref(enchantment.Confusion.name)
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Whispers of the Abyss",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} whispers maddening secrets in a tongue that unravels sanity. Non-demon creatures within 30 feet that hear it must make a DC {dc} Wisdom save. \
                On a failure, they take {dmg.description} Psychic damage and are affected as by the {confusion} spell (save ends at end of turn). On a success, a creature takes half damage instead.",
        )
        return [feature]


class _BlackBlood(DemonPower):
    def __init__(self):
        super().__init__(
            name="Black Blood",
            source="Foe Foundry",
            icon="blood",
            power_level=LOW_POWER,
            require_cr=3,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.attributes.proficiency
        feature = Feature(
            name="Black Blood",
            action=ActionType.Feature,
            description=f"When {stats.selfref} takes piercing or slashing damage, it splashes nearby creatures with black ichor. \
                Each non-demon creature within 10 feet takes {dmg} Acid damage and its movement speed is halved until the end of its next turn. \
                This ability activates only once per turn.",
        )
        return [feature]


class _Desecration(DemonPower):
    def __init__(self):
        super().__init__(
            name="Desecration",
            source="Foe Foundry",
            icon="pentagram-rose",
            power_level=LOW_POWER,
            require_cr=3,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        token = Token(
            name="Desecrated Ground", dc=stats.difficulty_class_token, charges=3
        )
        dmg = stats.target_value(dpr_proportion=0.25)

        feature = Feature(
            name="Desecration",
            uses=max(1, round(stats.attributes.proficiency / 2)),
            action=ActionType.Action,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} desecrates the ground it stands upon, creating a {token.caption}. \
                Within 30 feet of the Token, any creature that attempts to speak or use any spell or ability that requires a verbal component suffers {dmg.description} necrotic damage \
                unless the creature speaks or incants in Abyssal. Additionally, creatures within the affected area cannot regain hit points.",
        )
        return [feature]


class _EchoOfRage(DemonPower):
    def __init__(self):
        super().__init__(
            name="Echo of Rage",
            source="Foe Foundry",
            icon="enrage",
            power_level=MEDIUM_POWER,
            require_cr=3,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        shadow = creature_ref("Shadow")

        shadow = creature_ref("Shadow")
        feature = Feature(
            name="Echo of Rage",
            action=ActionType.Reaction,
            uses=max(1, round(stats.attributes.proficiency / 2)),
            description=f"Whenever a creature within 30 feet casts a spell, {stats.selfref} can use its reaction to howl in a rage. \
                A distored, destructive version of the spell manifests as a hostile {shadow} next to the caster and acts immediately next in initiative.",
        )
        return [feature]


class _NightmareSpawn(DemonPower):
    def __init__(self):
        super().__init__(
            name="Nightmare Spawn",
            source="Foe Foundry",
            icon="elysium-shade",
            power_level=HIGH_POWER,
            require_cr=9,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        nightmare = creature_ref("Nightmare")
        dmg = stats.target_value(dpr_proportion=0.5)

        feature = Feature(
            name="Nightmare Spawn",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} manifests the darkest fears of its enemies. Each non-demon within 60 feet must make a DC {stats.difficulty_class} Wisdom saving throw. \
                On a failure, the target takes {dmg.description} psyhchic damage and a hostile {nightmare} spawns in the nearest unoccupied space to the target, acting on initiative count 0. \
                On a success, the target takes half damage instead.",
        )

        return [feature]


# TODO
# Abyssal Slough – The demon sheds a grotesque skin or limb when damaged, which continues fighting or transforms into a new threat.


BlackBlood: Power = _BlackBlood()
DemonicBite: Power = _DemonicBite()
DemonicSummons: Power = _DemonicSummons()
Desecration: Power = _Desecration()
EchoOfRage: Power = _EchoOfRage()
FeastOfSouls: Power = _FeastOfSouls()
NightmareSpawn: Power = _NightmareSpawn()
WhispersOfTheAbyss: Power = _WhispersOfTheAbyss()

DemonPowers: list[Power] = [
    DemonicBite,
    DemonicSummons,
    Desecration,
    EchoOfRage,
    FeastOfSouls,
    NightmareSpawn,
    WhispersOfTheAbyss,
]
