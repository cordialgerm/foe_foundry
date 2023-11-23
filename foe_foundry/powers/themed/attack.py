from datetime import datetime
from typing import List

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attack_template import natural, spell, weapon
from ...damage import DamageType, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class AttackPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        score_args: dict,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
    ):
        super().__init__(
            name=name,
            power_type=PowerType.Theme,
            source="FoeFoundryOriginal",
            theme="Attack",
            power_level=power_level,
            create_date=create_date,
            score_args=score_args,
        )


class _PoisonedAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_damage=DamageType.Poison,
            bonus_roles=[MonsterRole.Controller, MonsterRole.Ambusher],
            attack_names=[
                "-",
                natural.Claw,
                natural.Bite,
                natural.Stinger,
                spell.Poisonbolt,
                weapon.Daggers,
                weapon.Shortbow,
                weapon.Shortswords,
            ],
        )
        super().__init__(name="Poisoned Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Poisoned Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target must make a DC {dc} Constitution saving throw or become **Poisoned** until the end of its next turn.",
        )
        return [feature]


class _BleedingAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Bruiser, MonsterRole.Skirmisher},
            attack_names=[
                "-",
                natural.Claw,
                natural.Bite,
                natural.Horns,
                natural.Spines,
                weapon.Daggers,
                natural.Thrash,
                spell.Acidsplash,
                spell.Poisonbolt,
            ],
        )

        super().__init__(name="Bleeding Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        damage = DieFormula.target_value(
            target=0.5 * stats.attack.average_damage, force_die=Die.d6
        )

        if stats.secondary_damage_type in {DamageType.Acid, DamageType.Poison}:
            damage_type = stats.secondary_damage_type
        else:
            damage_type = DamageType.Piercing

        bleeding = conditions.Bleeding(
            damage=damage,
            damage_type=damage_type,
        )

        save_needed = stats.cr <= 5

        if save_needed:
            dc = stats.difficulty_class
            condition = f"must make a DC {dc} Constitution saving throw or gain {bleeding}"
        else:
            condition = f"gains {bleeding}"

        feature = Feature(
            name="Bleeding Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target {condition}",
        )

        return [feature]


class _DazingAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            require_roles={MonsterRole.Controller},
            attack_names=[natural.Tail, natural.Slam, weapon.Staff],
        )
        super().__init__(name="Dazing Attack", power_level=HIGH_POWER, score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dazed = conditions.Dazed()
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Dazing Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target must make a DC {dc} Constitution saving throw or be {dazed}",
        )
        return [feature]


class _BurningAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            require_roles={MonsterRole.Artillery},
            require_damage={DamageType.Fire, DamageType.Radiant, DamageType.Acid},
            attack_names=["-", spell.HolyBolt, spell.Firebolt, spell.Acidsplash],
        )

        super().__init__(name="Burning Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        damage_type = stats.secondary_damage_type or DamageType.Fire
        damage = DieFormula.target_value(0.33 * stats.attack.average_damage, force_die=Die.d10)
        burning = conditions.Burning(damage, damage_type)
        feature = Feature(
            name="Burning Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target gains {burning}",
        )
        return [feature]


class _ProneAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Bruiser, MonsterRole.Controller},
            bonus_size=Size.Large,
            attack_names=[
                "-",
                weapon.Staff,
                weapon.Maul,
                natural.Slam,
                natural.Stomp,
                natural.Tail,
                natural.Claw,
                weapon.Greataxe,
                weapon.Greatsword,
                spell.ArcaneBurst,
                spell.Thundrousblast,
            ],
        )
        super().__init__(name="Prone Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        if stats.size >= Size.Huge:
            condition = "is knocked **Prone**"
        else:
            dc = stats.difficulty_class
            condition = f"must make a DC {dc} Strength saving throw or be knocked **Prone**"

        feature = Feature(
            name="Prone Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target {condition}",
        )
        return [feature]


class _SlowingAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Controller, MonsterRole.Artillery},
            bonus_damage=DamageType.Cold,
            attack_names=[
                "-",
                natural.Stomp,
                spell.Frostbolt,
                weapon.JavelinAndShield,
                weapon.Whip,
                weapon.Longbow,
                weapon.Shortbow,
            ],
        )
        super().__init__(name="Slowing Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Slowing Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target's movement speed is reduced by a cumulative 10 feet until the end of its next turn",
        )
        return [feature]


class _PushingAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Bruiser, MonsterRole.Controller},
            bonus_size=Size.Large,
            attack_names=[
                "-",
                natural.Tail,
                natural.Slam,
                spell.ArcaneBurst,
                spell.EdlritchBlast,
                spell.Thundrousblast,
                weapon.Crossbow,
                weapon.Maul,
            ],
        )

        super().__init__(name="Pushing Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        if stats.size >= Size.Huge and stats.attributes.STR >= 20:
            distance = 20
        elif stats.size >= Size.Huge:
            distance = 15
        else:
            distance = 10

        feature = Feature(
            name="Pushing Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target is pushed up to {distance} feet horizontally",
        )
        return [feature]


class _GrapplingAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Bruiser, MonsterRole.Controller},
            bonus_size=Size.Large,
            attack_names=["-", natural.Slam, natural.Tentacle, weapon.Whip],
        )

        super().__init__(name="Grappling Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class

        if stats.size >= Size.Huge or stats.attributes.STR >= 20:
            condition = f"is **Grappled** (escape DC {dc})"
        else:
            dc = stats.difficulty_class
            condition = (
                f"must make a DC {dc} Strength saving throw or be **Grappled** (escape DC {dc})"
            )

        feature = Feature(
            name="Grappling Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target {condition}",
        )
        return [feature]


class _BlindingAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Controller, MonsterRole.Leader},
            bonus_damage={DamageType.Radiant, DamageType.Acid},
            attack_names=[
                "-",
                natural.Spit,
                spell.HolyBolt,
                spell.Acidsplash,
                spell.Firebolt,
            ],
        )
        super().__init__(name="Blinding Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Blinding Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target must make a DC {dc} Constitution saving throw or be **Blinded** until the end of its next turn",
        )
        return [feature]


class _FrighteningAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Controller, MonsterRole.Leader, MonsterRole.Ambusher},
            bonus_damage={DamageType.Psychic, DamageType.Necrotic},
            attack_names=["-", spell.Gaze, spell.Deathbolt],
        )
        super().__init__(name="Frightening Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Frightening Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target is **Frightened** until the end of its next turn",
        )
        return [feature]


class _CharmingAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Controller, MonsterRole.Leader},
            bonus_damage=DamageType.Psychic,
            attack_names=["-", spell.Gaze],
        )
        super().__init__(name="Charming Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Charming Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target must make a DC {dc} Wisdom save or be **Charmed** for 1 minute (save ends at end of turn or when it takes damage).",
        )
        return [feature]


class _FreezingAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Controller},
            require_damage=DamageType.Cold,
            require_damage_exact_match=True,
            attack_names=[spell.Frostbolt],
        )
        super().__init__(name="Freezing Attack", power_level=HIGH_POWER, score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        frozen = conditions.Frozen(dc)
        condition = f"must make a DC {dc} Constitution save or be {frozen}"

        feature = Feature(
            name="Freezing Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target {condition}",
        )
        return [feature]


class _ShockingAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Controller, MonsterRole.Ambusher},
            require_damage={DamageType.Lightning, DamageType.Thunder},
            require_damage_exact_match=True,
            attack_names=[spell.Shock, spell.Thundrousblast],
        )
        super().__init__(name="Shocking Attack", power_level=HIGH_POWER, score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        shocked = conditions.Shocked()
        feature = Feature(
            name="Shocking Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target must make a DC {dc} Constitution saving throw or be {shocked}",
        )
        return [feature]


class _GrazingAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Skirmisher},
            attack_names=[
                "-",
                weapon.Greatsword,
                weapon.Polearm,
                natural.Claw,
            ],
        )
        super().__init__(name="Grazing Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        damage = stats.attributes.primary_mod
        damage_type = stats.attack.damage.damage_type

        feature = Feature(
            name="Grazing Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"If the attack misses, the target still takes {damage} {damage_type} damage",
        )
        return [feature]


class _CleavingAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_size=Size.Large,
            bonus_roles={MonsterRole.Bruiser},
            attack_names=["-", weapon.Greataxe, natural.Tail, weapon.Polearm],
        )
        super().__init__(name="Cleaving Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        damage = stats.attributes.primary_mod
        damage_type = stats.attack.damage.damage_type
        reach = stats.attack.reach

        feature = Feature(
            name="Cleaving Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"If the attack hits and there is another hostile target within {reach} ft then that target also takes {damage} {damage_type} damage",
        )
        return [feature]


class _SappingAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Skirmisher, MonsterRole.Controller},
            attack_names=[
                "-",
                weapon.SpearAndShield,
                weapon.SwordAndShield,
                weapon.Traps,
                natural.Stinger,
            ],
        )
        super().__init__(name="Sapping Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Sapping Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target has disadvantage on its next attack roll until the end of its next turn",
        )
        return [feature]


class _VexingAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Ambusher, MonsterRole.Leader},
            attack_names=["-", weapon.Shortbow, weapon.Shortswords, weapon.RapierAndShield],
        )
        super().__init__(name="Vexing Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Vexing Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the next attack against the target has advantage until the end of {stats.selfref}'s next turn.",
        )
        return [feature]


class _WeakeningAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_damage=[DamageType.Necrotic, DamageType.Poison, DamageType.Psychic],
            bonus_roles=[MonsterRole.Controller, MonsterRole.Artillery],
            attack_names=[
                "-",
                natural.Bite,
                natural.Stinger,
                spell.Deathbolt,
                spell.Poisonbolt,
                spell.Gaze,
            ],
        )
        super().__init__(name="Weakening Attack", power_level=HIGH_POWER, score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        weakened = conditions.Weakened()
        feature = Feature(
            name="Weakening Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target must make a DC {dc} Constitution saving throw or become {weakened.caption} until the end of its next turn. {weakened.description_3rd}",
        )
        return [feature]


class _DisarmingAttack(AttackPower):
    def __init__(self):
        score_args = dict(
            bonus_roles=[MonsterRole.Controller, MonsterRole.Artillery],
            attack_names=[
                "-",
                weapon.SwordAndShield,
                weapon.Greataxe,
                weapon.Greatsword,
                weapon.MaceAndShield,
                weapon.Maul,
                weapon.Polearm,
                weapon.RapierAndShield,
                weapon.SpearAndShield,
                weapon.Shortswords,
                weapon.SwordAndShield,
                weapon.Staff,
                weapon.Whip,
            ],
        )

        super().__init__(name="Disarming Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Disarming Attack",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"Immediately after hitting with an attack, {stats.selfref} forces the target to make a DC {dc} Strength saving throw. \
                On a failure, the target must drop one item of {stats.selfref}'s choice that it is holding. The item lands at the target's feet.",
        )
        return [feature]


BlindingAttack: Power = _BlindingAttack()
BleedingAttack: Power = _BleedingAttack()
CharmingAttack: Power = _CharmingAttack()
CleavingAttack: Power = _CleavingAttack()
DisarmingAttack: Power = _DisarmingAttack()
BurningAttack: Power = _BurningAttack()
DazingAttacks: Power = _DazingAttack()
FrighteningAttack: Power = _FrighteningAttack()
FreezingAttack: Power = _FreezingAttack()
GrapplingAttack: Power = _GrapplingAttack()
GrazingAttack: Power = _GrazingAttack()
PoisonedAttack: Power = _PoisonedAttack()
ProneAttack: Power = _ProneAttack()
PushingAttack: Power = _PushingAttack()
SappingAttack: Power = _SappingAttack()
SlowingAttack: Power = _SlowingAttack()
ShockingAttack: Power = _ShockingAttack()
VexingAttack: Power = _VexingAttack()
WeakeningAttack: Power = _WeakeningAttack()

AttackPowers = [
    BlindingAttack,
    BleedingAttack,
    CharmingAttack,
    CleavingAttack,
    DisarmingAttack,
    BurningAttack,
    DazingAttacks,
    FrighteningAttack,
    FreezingAttack,
    GrapplingAttack,
    GrazingAttack,
    PoisonedAttack,
    ProneAttack,
    PushingAttack,
    SappingAttack,
    SlowingAttack,
    ShockingAttack,
    VexingAttack,
    WeakeningAttack,
]
