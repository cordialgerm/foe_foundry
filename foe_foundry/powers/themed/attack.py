from typing import List, Set, Tuple

import numpy as np
from numpy.random import Generator

from ...attack_template import natural, spell, weapon
from ...creature_types import CreatureType
from ...damage import DamageType, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ..attack import flavorful_damage_types
from ..attack_modifiers import AttackModifiers, resolve_attack_modifier
from ..power import Power, PowerType
from ..scores import HIGH_AFFINITY, LOW_AFFINITY, MODERATE_AFFINITY, NO_AFFINITY


def score(
    candidate: BaseStatblock,
    target_roles: MonsterRole | Set[MonsterRole] | List[MonsterRole] | None = None,
    target_damage_type: DamageType | Set[DamageType] | List[DamageType] | None = None,
    attack_modifiers: AttackModifiers = None,
    size_boost: bool = False,
) -> float:
    def clean_set(a):
        if a is None:
            return set()
        elif isinstance(a, list):
            return set(a)
        elif isinstance(a, set):
            return a
        else:
            return {a}

    target_roles = clean_set(target_roles)
    target_damage_type = clean_set(target_damage_type)

    score = resolve_attack_modifier(candidate, attack_modifiers)

    if candidate.primary_damage_type in target_damage_type:
        score += MODERATE_AFFINITY
    if candidate.secondary_damage_type in target_damage_type:
        score += MODERATE_AFFINITY

    # if none of the above conditions are met then the power doesn't make sense
    # these remaining factors don't determine eligibility, just likelyhood
    if score == 0:
        return NO_AFFINITY

    if candidate.creature_type == CreatureType.Humanoid:
        score += MODERATE_AFFINITY

    if candidate.role in target_roles:
        score += HIGH_AFFINITY

    if len(flavorful_damage_types(candidate).intersection(target_damage_type)):
        score += MODERATE_AFFINITY

    if size_boost and candidate.size >= Size.Large:
        score += MODERATE_AFFINITY
    if size_boost and candidate.size >= Size.Huge:
        score += MODERATE_AFFINITY
    if size_boost and candidate.size >= Size.Gargantuan:
        score += MODERATE_AFFINITY

    return score


class _PoisoningAttack(Power):
    def __init__(self):
        super().__init__(name="Poisoning Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_damage_type=DamageType.Poison,
            target_roles=[MonsterRole.Controller, MonsterRole.Ambusher],
            attack_modifiers=[natural.Claw, natural.Bite, natural.Stinger, spell.Poisonbolt],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class_easy
        weakened = conditions.Weakened()
        feature = Feature(
            name="Weakening Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target must make a DC {dc} Constitution saving throw or become {weakened.caption} until the end of its next turn. {weakened.description_3rd}",
        )
        return stats, feature


class _BleedingAttack(Power):
    def __init__(self):
        super().__init__(name="Bleeding Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles={MonsterRole.Bruiser, MonsterRole.Skirmisher},
            attack_modifiers=[
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

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
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
            name="Prone Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target {condition}",
        )
        return stats, feature


class _DazingAttack(Power):
    def __init__(self):
        super().__init__(name="Dazing Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles={MonsterRole.Controller},
            target_damage_type=DamageType.Bludgeoning,
            attack_modifiers=[natural.Tail, natural.Slam, weapon.Staff],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dazed = conditions.Dazed()
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Dazing Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target must make a DC {dc} Constitution saving throw or be {dazed}",
        )
        return stats, feature


class _BurningAttack(Power):
    def __init__(self):
        super().__init__(name="Burning Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles={MonsterRole.Artillery},
            target_damage_type={DamageType.Fire, DamageType.Radiant, DamageType.Acid},
            attack_modifiers=[spell.HolyBolt, spell.Firebolt, spell.Acidsplash],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
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
        return stats, feature


class _ProneAttack(Power):
    def __init__(self):
        super().__init__(name="Prone Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles={MonsterRole.Bruiser},
            size_boost=True,
            attack_modifiers=[weapon.Staff, weapon.Maul, natural.Slam, natural.Stomp],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
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
        return stats, feature


class _SlowingAttack(Power):
    def __init__(self):
        super().__init__(name="Slowing Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles={MonsterRole.Controller, MonsterRole.Artillery},
            target_damage_type=DamageType.Cold,
            attack_modifiers=[
                natural.Stomp,
                spell.Frostbolt,
                weapon.JavelinAndShield,
                weapon.Whip,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Slowing Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target's movement speed is reduced by a cumulative 10 feet until the end of its next turn",
        )
        return stats, feature


class _PushingAttack(Power):
    def __init__(self):
        super().__init__(name="Pushing Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles={MonsterRole.Bruiser},
            size_boost=True,
            attack_modifiers=[
                natural.Tail,
                spell.ArcaneBurst,
                spell.EdlritchBlast,
                spell.Thundrousblast,
                weapon.Crossbow,
                weapon.Maul,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
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
        return stats, feature


class _GrapplingAttack(Power):
    def __init__(self):
        super().__init__(name="Grappling Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles={MonsterRole.Bruiser, MonsterRole.Controller},
            size_boost=True,
            attack_modifiers=[natural.Slam, natural.Tentacle, weapon.Whip],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
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
        return stats, feature


class _BlindingAttack(Power):
    def __init__(self):
        super().__init__(name="Blinding Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles={MonsterRole.Controller, MonsterRole.Leader},
            target_damage_type={DamageType.Radiant, DamageType.Acid},
            attack_modifiers=[natural.Spit, spell.HolyBolt, spell.Acidsplash, spell.Firebolt],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Blinding Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target must make a DC {dc} Constitution saving throw or be **Blinded** until the end of its next turn",
        )
        return stats, feature


class _FearingAttack(Power):
    def __init__(self):
        super().__init__(name="Frightening Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles={MonsterRole.Controller, MonsterRole.Leader, MonsterRole.Ambusher},
            target_damage_type={DamageType.Psychic, DamageType.Necrotic},
            attack_modifiers=[spell.Gaze, spell.Deathbolt],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Frightening Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target is **Frightened** until the end of its next turn",
        )
        return stats, feature


class _CharmingAttack(Power):
    def __init__(self):
        super().__init__(name="Charming Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles={MonsterRole.Controller, MonsterRole.Leader},
            target_damage_type=DamageType.Psychic,
            attack_modifiers=[spell.Gaze],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Charming Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target must make a DC {dc} Wisdom save or be **Charmed** for 1 minute (save ends at end of turn or when it takes damage).",
        )
        return stats, feature


class _FreezingAttack(Power):
    def __init__(self):
        super().__init__(name="Freezing Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles={MonsterRole.Controller},
            target_damage_type=DamageType.Cold,
            attack_modifiers=[spell.Frostbolt],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        frozen = conditions.Frozen(dc)

        if stats.cr >= 7:
            condition = f"is {frozen}"
        else:
            condition = f"must make a DC {dc} Constitution save or be {frozen}"

        feature = Feature(
            name="Freezing Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target {condition}",
        )
        return stats, feature


class _ShockingAttack(Power):
    def __init__(self):
        super().__init__(name="Shocking Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles={MonsterRole.Controller, MonsterRole.Ambusher},
            target_damage_type={DamageType.Lightning, DamageType.Thunder},
            attack_modifiers=[spell.Shock, spell.Thundrousblast],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        shocked = conditions.Shocked()
        feature = Feature(
            name="Shocking Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target must make a DC {dc} Constitution saving throw or be {shocked}",
        )
        return stats, feature


class _GrazingAttack(Power):
    def __init__(self):
        super().__init__(name="Grazing Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles={MonsterRole.Skirmisher},
            attack_modifiers=[
                weapon.Greatsword,
                weapon.Polearm,
                natural.Claw,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        damage = stats.attributes.primary_mod
        damage_type = stats.attack.damage.damage_type

        feature = Feature(
            name="Grazing Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"If the attack misses, the target still takes {damage} {damage_type} damage",
        )
        return stats, feature


class _CleavingAttack(Power):
    def __init__(self):
        super().__init__(name="Cleaving Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            size_boost=True,
            target_roles={MonsterRole.Bruiser},
            attack_modifiers=[weapon.Greataxe, natural.Tail],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
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
        return stats, feature


class _SappingAttack(Power):
    def __init__(self):
        super().__init__(name="Sapping Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles={MonsterRole.Skirmisher, MonsterRole.Controller},
            attack_modifiers=[
                weapon.SpearAndShield,
                weapon.SwordAndShield,
                weapon.Traps,
                natural.Stinger,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Sapping Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target has disadvantage on its next attack roll until the end of its next turn",
        )
        return stats, feature


class _VexingAttack(Power):
    def __init__(self):
        super().__init__(name="Vexing Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            size_boost=True,
            target_roles={MonsterRole.Ambusher, MonsterRole.Leader},
            attack_modifiers=[weapon.Shortbow, weapon.Shortswords, weapon.RapierAndShield],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Vexing Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the next attack against the target has advantage until the end of {stats.selfref}'s next turn.",
        )
        return stats, feature


class _WeakeningAttack(Power):
    def __init__(self):
        super().__init__(name="Weakening Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_damage_type=[DamageType.Necrotic, DamageType.Poison, DamageType.Psychic],
            target_roles=[MonsterRole.Controller, MonsterRole.Artillery],
            attack_modifiers=[
                natural.Bite,
                natural.Stinger,
                spell.Deathbolt,
                spell.Poisonbolt,
                spell.Gaze,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class_easy
        weakened = conditions.Weakened()
        feature = Feature(
            name="Weakening Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target must make a DC {dc} Constitution saving throw or become {weakened.caption} until the end of its next turn. {weakened.description_3rd}",
        )
        return stats, feature


class _DisarmingAttack(Power):
    def __init__(self):
        super().__init__(name="Disarming Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            target_roles=[MonsterRole.Controller, MonsterRole.Artillery],
            attack_modifiers=[
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

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Disarming Attack",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"Immediately after hitting with an attack, {stats.selfref} forces the target to make a DC {dc} Strength saving throw. \
                On a failure, the target must drop one item of {stats.selfref}'s choice that it is holding. The item lands at the target's feet.",
        )
        return stats, feature


BlindingAttack: Power = _BlindingAttack()
BleedingAttack: Power = _BleedingAttack()
CharmingAttack: Power = _CharmingAttack()
CleavingAttack: Power = _CleavingAttack()
DisarmingAttack: Power = _DisarmingAttack()
BurningAttack: Power = _BurningAttack()
DazingAttacks: Power = _DazingAttack()
FearingAttack: Power = _FearingAttack()
FreezingAttack: Power = _FreezingAttack()
GrapplingAttack: Power = _GrapplingAttack()
GrazingAttack: Power = _GrazingAttack()
PoisoningAttack: Power = _PoisoningAttack()
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
    FearingAttack,
    FreezingAttack,
    GrapplingAttack,
    GrazingAttack,
    PoisoningAttack,
    ProneAttack,
    PushingAttack,
    SappingAttack,
    SlowingAttack,
    ShockingAttack,
    VexingAttack,
    WeakeningAttack,
]
