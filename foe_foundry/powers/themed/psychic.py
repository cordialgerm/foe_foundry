from datetime import datetime
from typing import List

from foe_foundry.statblocks import BaseStatblock

from ...attack_template import natural as natural_attacks
from ...creature_types import CreatureType
from ...damage import AttackType, Burning, DamageType, Dazed
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...spells import transmutation
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class PsychicPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_type: PowerType = PowerType.Theme,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        def is_spellcaster(candidate: BaseStatblock) -> bool:
            if candidate.creature_type == CreatureType.Humanoid:
                return (
                    any(t.is_spell() for t in candidate.attack_types)
                    and candidate.secondary_damage_type == DamageType.Psychic
                )
            else:
                return True

        super().__init__(
            name=name,
            source=source,
            create_date=create_date,
            power_level=power_level,
            theme="psychic",
            power_type=power_type,
            score_args=dict(
                require_types={CreatureType.Aberration, CreatureType.Humanoid},
                require_callback=is_spellcaster,
                bonus_damage=DamageType.Psychic,
                bonus_roles=MonsterRole.Controller,
            )
            | score_args,
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Psychic)
        return stats


class _Telekinetic(PsychicPower):
    def __init__(self):
        super().__init__(
            name="Telekinesis",
            source="5.1SRD Telekinesis",
            power_type=PowerType.Spellcasting,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        return stats.add_spell(transmutation.Telekinesis.for_statblock())


class _PsychicInfestation(PsychicPower):
    def __init__(self):
        super().__init__(name="Psychic Infestation", source="Foe Foundry")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        distance = easy_multiple_of_five(30 + 5 * stats.cr, min_val=30, max_val=90)
        dc = stats.difficulty_class
        dmg = stats.target_value(target=1.5, force_die=Die.d6)
        burning = Burning(
            damage=DieFormula.from_dice(d6=dmg.n_die // 2),
            damage_type=DamageType.Psychic,
        )

        feature = Feature(
            name="Psychic Infestation",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} attempts to infect the mind of a creature it can see within {distance} feet. \
                The creature must make a DC {dc} Intelligence save. On a failure, it takes {dmg.description} psychic damage and is {burning.caption}. \
                On a success, it takes half damage instead. {burning.description_3rd}",
        )

        return [feature]


class _DissonantWhispers(PsychicPower):
    def __init__(self):
        super().__init__(name="Dissonant Whispers", source="SRD5.1 Dissonant Whispers")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        distance = easy_multiple_of_five(30 + 5 * stats.cr, min_val=30, max_val=90)
        dc = stats.difficulty_class
        dmg = stats.target_value(1.5, force_die=Die.d6)

        feature = Feature(
            name="Dissonant Whispers",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} whispers a discordant melody into the mind of a creature within {distance} ft. \
                The target must make a DC {dc} Wisdom save. On a failure, it takes {dmg.description} psychic damage and must immediately use its reaction, \
                if available, to move as far away as its speed allows from {stats.selfref}. The creature doesn't move into obviously dangerous ground. \
                On a successful save, the target takes half damage instead.",
        )
        return [feature]


class _PsionicBlast(PsychicPower):
    def __init__(self):
        super().__init__(
            name="Psionic Blast", source="Foe Foundry", power_level=HIGH_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        multiplier = 2.5 if stats.multiattack >= 2 else 1.5
        dmg = stats.target_value(target=multiplier, force_die=Die.d6)
        dc = stats.difficulty_class
        dazed = Dazed()

        if stats.cr <= 3:
            distance = 15
        elif stats.cr <= 5:
            distance = 30
        else:
            distance = 60

        feature = Feature(
            name="Psionic Blast",
            action=ActionType.Action,
            recharge=6,
            replaces_multiattack=3,
            description=f"{stats.selfref.capitalize()} magically emits psionic energy in a {distance} ft cone. \
                Each creature in that area must succeed on a DC {dc} Intelligence saving throw. On a failure, a creature \
                takes {dmg.description} psychic damage and is {dazed.caption} for 1 minute (save ends at end of turn). On a failure, \
                a creature takes half damage instead. {dazed.description_3rd}",
        )

        return [feature]


class _MirroredPain(PsychicPower):
    def __init__(self):
        super().__init__(name="Mirrored Pain", source="Foe Foundry")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Mirrored Pain",
            action=ActionType.Reaction,
            description=f"Whenever {stats.selfref} takes damage, each other creature within 10 feet of {stats.selfref} must make a DC {dc} Intelligenece save. On a failure, it takes half the triggering damage as psychic damage.",
        )
        return [feature]


class _EatBrain(PsychicPower):
    def __init__(self):
        super().__init__(
            name="Eat Brain",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            require_types=CreatureType.Aberration,
            require_cr=7,
            attack_names={
                "-",
                natural_attacks.Tentacle,
            },
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.add_attack(
            scalar=3.5,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeNatural,
            die=Die.d10,
            replaces_multiattack=4,
            custom_target=f"one dazed humanoid grappled by {stats.selfref}",
            additional_description=f"If this damage reduces the target to 0 hit points, {stats.selfref} kills the target \
                by extracting and devouring its brain.",
            name="Extract Brain",
        )
        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        dazed = Dazed()

        stunning_tentacles = Feature(
            name="Stunning Tentancles",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
            description=f"On a hit, the target is **Grappled** (escape DC {dc}) and must succeed \
                on a DC {dc} Intelligence save or be {dazed.caption} while grappled in this way. {dazed.description_3rd}",
        )

        return [stunning_tentacles]


DissonantWhispers: Power = _DissonantWhispers()
EatBrain: Power = _EatBrain()
PsionicBlast: Power = _PsionicBlast()
PsychicInfestation: Power = _PsychicInfestation()
MirroredPain: Power = _MirroredPain()
Telekinetic: Power = _Telekinetic()

PsychicPowers: List[Power] = [
    DissonantWhispers,
    EatBrain,
    MirroredPain,
    PsionicBlast,
    PsychicInfestation,
    Telekinetic,
]
