from datetime import datetime
from math import ceil
from typing import List

from num2words import num2words

from foe_foundry.references import action_ref

from ...creature_types import CreatureType
from ...damage import AttackType, Condition, DamageType, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...skills import Skills
from ...spells import necromancy
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerType,
    PowerWithStandardScoring,
)


class CursedPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        reference_statblock: str = "Ghost",
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
            power_category=PowerCategory.Theme,
            source=source,
            theme="Cursed",
            icon=icon,
            reference_statblock=reference_statblock,
            create_date=create_date,
            power_level=power_level,
            score_args=standard_score_args,
            power_types=[PowerType.Debuff, PowerType.Magic],
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Necrotic)

        return stats


class _AuraOfDespair(CursedPower):
    def __init__(self):
        super().__init__(name="Aura of Despair", icon="despair", source="Foe Foundry")

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        weight_of_sorrow = Feature(
            name="Weight of Sorrow",
            action=ActionType.Feature,
            description=f"Any creature othern than {stats.selfref} that starts its turn within 5 feet of {stats.selfref} has its speed reduced by 20 feet until the start of that creature's next turn.",
        )

        dc = stats.difficulty_class
        frightened = Condition.Frightened

        dreadful_scream = Feature(
            name="Dreadful Scream",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} unleashes a dreadful scream laced with sorrow and despair. \
                Each creature within 30 feet that can hear {stats.selfref} must make a DC {dc} Wisdom saving throw or be {frightened.caption} of {stats.selfref} for 1 minute (save ends at end of turn). \
                While frightened in this way, the creature loses any resistance or immunity to psychic and necrotic damage.",
        )

        return [weight_of_sorrow, dreadful_scream]


class _DisfiguringCurse(CursedPower):
    def __init__(self):
        return super().__init__(
            name="Disfiguring Curse",
            icon="witch-face",
            source="Foe Foundry",
            power_level=HIGH_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        dmg = stats.target_value(target=1.2, force_die=Die.d6)
        exhaustion = Condition.Exhaustion

        feature = Feature(
            name="Disfiguring Curse",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} attempts to magically spread its curse to a target that it can see within 60 feet. \
                The target must make a DC {dc} Charisma save. On a failure, the target takes {dmg.description} psychic damage and is cursed with horrible deformities. \
                While deformed, the target gains a level of {exhaustion.caption} that does not go away when taking a long rest. The cursed creature can repeat the saving throw whenever it finishes a long rest, ending the effect on a success.",
        )
        return [feature]


class _CursedWound(CursedPower):
    def __init__(self):
        return super().__init__(
            name="Cursed Wound", icon="death-juice", source="SRD5.1 Wight"
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
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
            name="Reject Divinity",
            source="Foe Foundry",
            icon="cancel",
            power_level=HIGH_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
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
        super().__init__(
            name="Bestow Curse", icon="dripping-star", source="SRD5.1 Bestow Curse"
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        level_number = 5 if stats.cr >= 7 else 3
        level_text = num2words(level_number, ordinal=True)
        aside = "(duration 8 hours)" if stats.cr >= 7 else "(duration 1 minute)"
        dc = stats.difficulty_class_easy
        bestow_curse = necromancy.BestowCurse.for_statblock(
            level=level_number, concentration=False
        ).caption_md

        feature = Feature(
            name="Bestow Curse",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=5,
            description=f"{stats.selfref.capitalize()} magically curses a creature that can hear it within 30 feet. \
                The creature must succeed on a DC {dc} Wisdom save or suffer the effects of the {bestow_curse} spell as if it were cast at {level_text} level {aside}, no concentration required.",
        )
        return [feature]


class _RayOfEnfeeblement(CursedPower):
    def __init__(self):
        super().__init__(
            name="Ray of Enfeeblement",
            icon="vomiting",
            source="SRD5.1 Ray of Enfeeblement",
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(target=1.5, force_die=Die.d6)
        dc = stats.difficulty_class
        weakened = conditions.Weakened(save_end_of_turn=False)
        poisoned = Condition.Poisoned
        feature = Feature(
            name="Ray of Enfeeblement",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} shoots a black beam of energy toward a creature it can can see within 60 feet. \
                That creature must succeed on a DC {dc} Constitution save or take {dmg.description} necrotic damage. On a success, the creature takes half damage. \
                On a failure, the creature is also {poisoned.caption} for 1 minute (save ends at end of turn). While poisoned in this way, the creature is {weakened}.",
        )
        return [feature]


class _VoidSiphon(CursedPower):
    def __init__(self):
        super().__init__(name="Void Siphon", icon="marrow-drain", source="Foe Foundry")

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        distance = 10 if stats.cr <= 7 else 20
        exhaustion = Condition.Exhaustion

        feature = Feature(
            name="Void Siphon",
            action=ActionType.Feature,
            description=f"When a creature within {distance} feet of {stats.roleref} receives magical healing, it also gains a level of {exhaustion.caption}",
        )
        return [feature]


class _ReplaceShadow(CursedPower):
    def __init__(self):
        super().__init__(
            name="Replace Shadow",
            source="A5E SRD Shadow Demon",
            power_level=HIGH_POWER,
            icon="shadow-follower",
            create_date=datetime(2023, 11, 24),
            require_attack_types=AttackType.AllMelee(),
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)
        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        hide = action_ref("Hide")

        feature1 = Feature(
            name="Shadow Stealth",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} uses {hide}, even if just lightly obscured by dim light or darkness",
        )

        feature2 = Feature(
            name="Replace Shadow",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=4,
            description=f"{stats.selfref.capitalize()} targets a humanoid within 20 feet that is in dim light and can't see {stats.selfref}. \
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
            icon="icicles-aura",
            source="A5E SRD Dread Knight",
            create_date=datetime(2023, 11, 24),
            require_attack_types=AttackType.AllMelee(),
            require_cr=7,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Unholy Aura",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} and allies within 30 feet have advantage on saving throws against spells and other magic effects and against features that turn undead. \
                            Other creatures of {stats.selfref}'s choice within 30 feet have disadvantage on saving throws against spells and other magic effects.",
        )
        return [feature]


class _CurseOfVengeance(CursedPower):
    def __init__(self):
        super().__init__(
            name="Curse of Vengeance",
            source="Foe Foundry",
            icon="wax-seal",
            create_date=datetime(2025, 4, 8),
            require_cr=3,
            require_spellcasting=True,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        dmg = stats.attributes.proficiency
        cursed = conditions.Cursed().caption
        feature = Feature(
            name="Curse of Vengeance",
            action=ActionType.Feature,
            description=f"Whenever a creature hits {stats.selfref} with an attack it must make a DC {dc} Charisma saving throw. \
                On a failure, the creature becomes {cursed} with a curse of vengeance. \
                Whenever a cursed creature hits {stats.selfref} with an attack, it takes {dmg} necrotic damage for each creature suffering the curse.",
        )

        return [feature]


AuraOfDespair: Power = _AuraOfDespair()
BestowCurse: Power = _BestowCurse()
CursedWound: Power = _CursedWound()
CurseOfVengeance: Power = _CurseOfVengeance()
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
    CurseOfVengeance,
    DisfiguringCurse,
    RayOfEnfeeblement,
    RejectDivinity,
    ReplaceShadow,
    UnholyAura,
    VoidSiphon,
]
