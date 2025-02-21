from datetime import datetime
from math import ceil
from typing import List

from num2words import num2words

from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...skills import Skills
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class CursedPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        standard_score_args = dict(
            require_types=[CreatureType.Fey, CreatureType.Fiend, CreatureType.Undead],
            bonus_damage=DamageType.Necrotic,
            bonus_roles=[MonsterRole.Leader, MonsterRole.Controller],
            **score_args,
        )
        super().__init__(
            name=name,
            power_type=PowerType.Theme,
            source=source,
            theme="cursed",
            create_date=create_date,
            power_level=power_level,
            score_args=standard_score_args,
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.secondary_damage_type != DamageType.Necrotic:
            stats = stats.copy(secondary_damage_type=DamageType.Necrotic)

        return stats


class _AuraOfDespair(CursedPower):
    def __init__(self):
        super().__init__(name="Aura of Despair", source="Foe Foundry")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        weight_of_sorrow = Feature(
            name="Weight of Sorrow",
            action=ActionType.Feature,
            description=f"Any creature othern than {stats.selfref} that starts its turn within 5 feet of {stats.selfref} has its speed reduced by 20 feet until the start of that creature's next turn.",
        )

        dc = stats.difficulty_class

        dreadful_scream = Feature(
            name="Dreadful Scream",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} unleashes a dreadful scream laced with sorrow and despair. \
                Each creature within 30 feet that can hear {stats.selfref} must make a DC {dc} Wisdom saving throw or be **Frightened** of {stats.selfref} for 1 minute (save ends at end of turn). \
                While frightened in this way, the creature loses any resistance or immunity to psychic and necrotic damage.",
        )

        return [weight_of_sorrow, dreadful_scream]


class _DisfiguringCurse(CursedPower):
    def __init__(self):
        return super().__init__(
            name="Disfiguring Curse", source="Foe Foundry", power_level=HIGH_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        dmg = stats.target_value(1.2, force_die=Die.d6)

        feature = Feature(
            name="Disfiguring Curse",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} attempts to magically spread its curse to a target that it can see within 60 feet. \
                The target must make a DC {dc} Charisma save. On a failure, the target takes {dmg.description} psychic damage and is cursed with horrible deformities. \
                While deformed, the target gains a level of **Exhaustion** that does not go away when taking a long rest. The cursed creature can repeat the saving throw whenever it finishes a long rest, ending the effect on a success.",
        )
        return [feature]


class _CursedWound(CursedPower):
    def __init__(self):
        return super().__init__(name="Cursed Wound", source="SRD5.1 Wight")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class

        feature = Feature(
            name="Cursed Wounds",
            action=ActionType.BonusAction,
            description=f"Immediately after hitting with an attack, {stats.selfref} converts all of that attack's damage to necrotic damage and forces the target to make a DC {dc} Charisma save. \
                On a failure, the target is cursed and its maximum hit points are reduced by the necrotic damage taken. \
                The target dies and reanimates as a Zombie under the control of {stats.selfref} if this damage leaves it with 0 hit points.",
        )
        return [feature]


class _RejectDivinity(CursedPower):
    def __init__(self):
        super().__init__(
            name="Reject Divinity", source="Foe Foundry", power_level=HIGH_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = DieFormula.target_value(max(3, ceil(1.5 * stats.cr)), force_die=Die.d6)

        feature = Feature(
            name="Reject Divinity",
            action=ActionType.Reaction,
            description=f"When a creature {stats.selfref} can see within 30 feet regains hit points from a Divine source, \
                {stats.selfref} reduces the number of hit points gained to 0 \
                and {stats.selfref} instead deals {dmg.description} necrotic damage to that creature.",
        )
        return [feature]


class _BestowCurse(CursedPower):
    def __init__(self):
        super().__init__(name="Bestow Curse", source="SRD5.1 Bestow Curse")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        level = num2words(5 if stats.cr >= 7 else 3, ordinal=True)
        aside = "(duration 8 hours)" if stats.cr >= 7 else "(duration 1 minute)"
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Bestow Curse",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=5,
            description=f"{stats.selfref.capitalize()} magically curses a creature that can hear it within 30 feet. \
                The creature must succeed on a DC {dc} Wisdom save or suffer the effects of the *Bestow Curse* spell as if it were cast at {level} level ({aside})",
        )
        return [feature]


class _RayOfEnfeeblement(CursedPower):
    def __init__(self):
        super().__init__(
            name="Ray of Enfeeblement", source="SRD5.1 Ray of Enfeeblement"
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(1.5, force_die=Die.d6)
        dc = stats.difficulty_class
        weakened = conditions.Weakened(save_end_of_turn=False)
        feature = Feature(
            name="Ray of Enfeeblement",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} shoots a black beam of energy toward a creature it can can see within 60 feet. \
                That creature must succeed on a DC {dc} Constitution save or take {dmg.description} necrotic damage. On a success, the creature takes half damage. \
                On a failure, the creature is also **Poisoned** for 1 minute (save ends at end of turn). While poisoned in this way, the creature is {weakened}.",
        )
        return [feature]


class _VoidSiphon(CursedPower):
    def __init__(self):
        super().__init__(name="Void Siphon", source="Foe Foundry")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        distance = 10 if stats.cr <= 7 else 20

        feature = Feature(
            name="Void Siphon",
            action=ActionType.Feature,
            description=f"When a creature within {distance} feet of {stats.roleref} receives magical healing, it also gains a level of **Exhaustion**",
        )
        return [feature]


class _ReplaceShadow(CursedPower):
    def __init__(self):
        super().__init__(
            name="Shadow Stealth",
            source="A5E SRD Shadow Demon",
            power_level=HIGH_POWER,
            create_date=datetime(2023, 11, 24),
            require_attack_types=AttackType.AllMelee(),
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)
        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class

        feature1 = Feature(
            name="Shadow Stealth",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} Hides, even if just lightly obscured by dim light or darkness",
        )

        feature2 = Feature(
            name="Replace Shadow",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} targets a humanoid within 5 feet that is in dim light and can't see {stats.selfref}. \
                            The target must make a DC {dc} Charisma saving throw. On a success, the target is aware of {stats.selfref}. \
                            On a failure, the target is unaware of {stats.selfref}, the target no longer casts a natural shadow, and {stats.selfref} magically takes on the shape of the target's shadow. \
                            {stats.selfref.capitalize()} appears indistinguishable from a natural shadow, except when it attacks. <br /> <br > \
                            {stats.selfref.capitalize()} shares the target's space and moves with the target. When {stats.selfref} is dealt damage while sharing the target's space, \
                            it takes half the damage (rounded down) and the other half is dealt to the target. <br /> <br/ > \
                            The effect ends when the target drops to 0 hp, {stats.selfref} no longer shares the target's space, or {stats.selfref} begins its turn in an area of sunlight.",
        )

        return [feature1, feature2]


class _UnholyAura(CursedPower):
    def __init__(self):
        super().__init__(
            name="Unholy Aura",
            source="A5E SRD Dread Knight",
            create_date=datetime(2023, 11, 24),
            require_attack_types=AttackType.AllMelee(),
            require_cr=7,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Unholy Aura",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} and allies within 30 feet have advantage on saving throws against spells and other magic effects and against features that turn undead. \
                            Other creatures of {stats.selfref}'s choice within 30 feet have disadvantage on saving throws against spells and other magic effects.",
        )
        return [feature]


AuraOfDespair: Power = _AuraOfDespair()
BestowCurse: Power = _BestowCurse()
CursedWound: Power = _CursedWound()
DisfiguringCurse: Power = _DisfiguringCurse()
RayOfEnfeeblement: Power = _RayOfEnfeeblement()
RejectDivinity: Power = _RejectDivinity()
ReplaceShadow: Power = _ReplaceShadow()
UnholyAura: Power = _UnholyAura()
VoidSiphon: Power = _VoidSiphon()

CursedPowers: List[Power] = [
    AuraOfDespair,
    BestowCurse,
    CursedWound,
    DisfiguringCurse,
    RayOfEnfeeblement,
    RejectDivinity,
    VoidSiphon,
]
