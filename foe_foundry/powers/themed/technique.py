from datetime import datetime
from typing import List, cast

from ...attack_template import natural, spell, weapon
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class Technique(PowerWithStandardScoring):
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
            source="Foe Foundry",
            theme="technique",
            power_level=power_level,
            create_date=create_date,
            score_args=score_args,
        )


class _PoisonedAttack(Technique):
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


class _BleedingAttack(Technique):
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
        damage = stats.target_value(target=0.5, force_die=Die.d6)

        if stats.secondary_damage_type in {DamageType.Acid, DamageType.Poison}:
            damage_type = cast(DamageType, stats.secondary_damage_type)
        else:
            damage_type = DamageType.Piercing

        bleeding = conditions.Bleeding(
            damage=damage,
            damage_type=damage_type,
        )

        save_needed = stats.cr <= 5

        if save_needed:
            dc = stats.difficulty_class
            condition = (
                f"must make a DC {dc} Constitution saving throw or gain {bleeding}"
            )
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


class _DazingAttack(Technique):
    def __init__(self):
        score_args = dict(
            require_roles={MonsterRole.Controller},
            attack_names=[natural.Tail, natural.Slam, weapon.Staff],
        )
        super().__init__(
            name="Dazing Attack", power_level=HIGH_POWER, score_args=score_args
        )

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


class _BurningAttack(Technique):
    def __init__(self):
        score_args = dict(
            require_roles={MonsterRole.Artillery},
            require_damage={DamageType.Fire, DamageType.Radiant, DamageType.Acid},
            attack_names=["-", spell.HolyBolt, spell.Firebolt, spell.Acidsplash],
        )

        super().__init__(name="Burning Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        damage_type = stats.secondary_damage_type or DamageType.Fire
        damage = stats.target_value(0.33, force_die=Die.d10)
        burning = conditions.Burning(damage, damage_type)
        feature = Feature(
            name="Burning Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target gains {burning}",
        )
        return [feature]


class _ProneAttack(Technique):
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
            condition = (
                f"must make a DC {dc} Strength saving throw or be knocked **Prone**"
            )

        feature = Feature(
            name="Prone Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target {condition}",
        )
        return [feature]


class _SlowingAttack(Technique):
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
                weapon.Pistol,
            ],
        )
        super().__init__(name="Slowing Attack", score_args=score_args)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Slowing Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description="On a hit, the target's movement speed is reduced by a cumulative 10 feet until the end of its next turn",
        )
        return [feature]


class _PushingAttack(Technique):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Bruiser, MonsterRole.Controller},
            bonus_size=Size.Large,
            attack_names=[
                "-",
                natural.Tail,
                natural.Slam,
                spell.ArcaneBurst,
                spell.EldritchBlast,
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


class _GrapplingAttack(Technique):
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
            condition = f"must make a DC {dc} Strength saving throw or be **Grappled** (escape DC {dc})"

        feature = Feature(
            name="Grappling Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target {condition}",
        )
        return [feature]


class _BlindingAttack(Technique):
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


class _FrighteningAttack(Technique):
    def __init__(self):
        score_args = dict(
            bonus_roles={
                MonsterRole.Controller,
                MonsterRole.Leader,
                MonsterRole.Ambusher,
            },
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
            description="On a hit, the target is **Frightened** until the end of its next turn",
        )
        return [feature]


class _CharmingAttack(Technique):
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


class _FreezingAttack(Technique):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Controller},
            require_damage=DamageType.Cold,
            require_damage_exact_match=True,
            attack_names=[spell.Frostbolt],
        )
        super().__init__(
            name="Freezing Attack", power_level=HIGH_POWER, score_args=score_args
        )

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


class _ShockingAttack(Technique):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Controller, MonsterRole.Ambusher},
            require_damage={DamageType.Lightning, DamageType.Thunder},
            require_damage_exact_match=True,
            attack_names=[spell.Shock, spell.Thundrousblast],
        )
        super().__init__(
            name="Shocking Attack", power_level=HIGH_POWER, score_args=score_args
        )

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


class _GrazingAttack(Technique):
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


class _CleavingAttack(Technique):
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


class _SappingAttack(Technique):
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
            description="On a hit, the target has disadvantage on its next attack roll until the end of its next turn",
        )
        return [feature]


class _VexingAttack(Technique):
    def __init__(self):
        score_args = dict(
            bonus_roles={MonsterRole.Ambusher, MonsterRole.Leader},
            attack_names=[
                "-",
                weapon.Shortbow,
                weapon.Shortswords,
                weapon.RapierAndShield,
                weapon.Pistol,
            ],
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


class _WeakeningAttack(Technique):
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
        super().__init__(
            name="Weakening Attack", power_level=HIGH_POWER, score_args=score_args
        )

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


class _DisarmingAttack(Technique):
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


class _ParryAndRiposte(Technique):
    def __init__(self):
        super().__init__(
            name="Parry and Riposte",
            score_args=dict(
                bonus_roles=MonsterRole.Defender,
                attack_names=[
                    "-",
                    weapon.SwordAndShield,
                    weapon.Greatsword,
                    weapon.Polearm,
                    weapon.Daggers,
                    weapon.Shortswords,
                    weapon.SpearAndShield,
                ],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Parry and Riposte",
            description=f"{stats.selfref.capitalize()} adds +3 to their Armor Class against one melee attack that would hit them.\
                         If the attack misses, this creature can immediately make a weapon attack against the creature making the parried attack.",
            action=ActionType.Reaction,
            recharge=6,
        )
        return [feature]


class _PommelStrike(Technique):
    def __init__(self):
        super().__init__(
            name="Pommel Strike",
            score_args=dict(
                attack_names=[
                    "-",
                    weapon.SwordAndShield,
                    weapon.SpearAndShield,
                ],
            ),
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        dazed = conditions.Dazed()
        dc = stats.difficulty_class_easy

        stats = stats.add_attack(
            scalar=0.6,
            damage_type=DamageType.Bludgeoning,
            attack_type=AttackType.MeleeWeapon,
            reach=5,
            die=Die.d4,
            replaces_multiattack=1,
            name="Pommel Strike",
            additional_description=f"On a hit, the target must make a DC {dc} Constitution saving throw or become {dazed.caption} until the end of its next turn. {dazed.description_3rd}",
        )

        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []


class _Dueling(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Dueling",
            source="Foe Foundry",
            theme="technique",
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
            theme="technique",
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
            theme="technique",
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
        distance = easy_multiple_of_five(
            stats.speed.fastest_speed / 2.0, min_val=5, max_val=30
        )
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
            theme="technique",
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
            description=f"{stats.selfref.capitalize()} switches places with a friendly creature within 5 feet, without triggering attacks of Opportunity. \
                Until the end of its next turn, the friendly creature gains a +{bonus} bonus to its AC.",
        )
        return [feature]


class _QuickToss(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Quick Toss",
            source="Foe Foundry",
            theme="technique",
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
            theme="technique",
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
            theme="technique",
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
            theme="technique",
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
            theme="technique",
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
                On a failure, it takes {dmg.description} {dmg_type} damage and is {bleeding.caption}. On a success, it instead takes half damage. {bleeding.description_3rd}",
        )
        return [feature]


class _Sharpshooter(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Sharpshooter's Shot",
            source="Foe Foundry",
            theme="technique",
            power_type=PowerType.Theme,
            power_level=HIGH_POWER,
            score_args=dict(
                require_roles=MonsterRole.Artillery,
                attack_names={
                    "-",
                    weapon.Longbow,
                    weapon.Shortbow,
                    weapon.Crossbow,
                    weapon.HandCrossbow,
                    weapon.Pistol,
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
ParryAndRiposte: Power = _ParryAndRiposte()
PoisonedAttack: Power = _PoisonedAttack()
PommelStrike: Power = _PommelStrike()
ProneAttack: Power = _ProneAttack()
PushingAttack: Power = _PushingAttack()
SappingAttack: Power = _SappingAttack()
SlowingAttack: Power = _SlowingAttack()
ShockingAttack: Power = _ShockingAttack()
VexingAttack: Power = _VexingAttack()
WeakeningAttack: Power = _WeakeningAttack()


TechniquePowers: List[Power] = [
    ArmorMaster,
    BaitAndSwitch,
    BlindingAttack,
    BleedingAttack,
    BurningAttack,
    CharmingAttack,
    CleavingAttack,
    DisarmingAttack,
    Dueling,
    DazingAttacks,
    ExpertBrawler,
    FreezingAttack,
    FrighteningAttack,
    GrapplingAttack,
    GrazingAttack,
    Interception,
    OverpoweringStrike,
    ParryAndRiposte,
    PoisonedAttack,
    PolearmMaster,
    PommelStrike,
    ProneAttack,
    PushingAttack,
    QuickToss,
    SappingAttack,
    Sharpshooter,
    ShieldMaster,
    SlowingAttack,
    ShockingAttack,
    VexingAttack,
    WeakeningAttack,
    WhirlwindOfSteel,
]
