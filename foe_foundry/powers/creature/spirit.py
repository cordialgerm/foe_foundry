from datetime import datetime
from typing import List

from foe_foundry.features import ActionType, Feature
from foe_foundry.references import action_ref, spell_ref
from foe_foundry.utils import comma_separated, easy_multiple_of_five

from ...creature_types import CreatureType
from ...damage import Condition, DamageType, conditions
from ...die import Die
from ...statblocks import BaseStatblock
from ..power import (
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


def is_spirit(s: BaseStatblock) -> bool:
    return s.creature_subtype == "Spirit"


class SpiritPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        reference_statblock: str = "Ghost",
        create_date: datetime | None = datetime(2025, 4, 20),
        **score_args,
    ):
        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="spirit",
            icon=icon,
            reference_statblock=reference_statblock,
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=create_date,
            score_args=dict(
                require_callback=is_spirit,
                require_types=[CreatureType.Undead],
            )
            | score_args,
        )


class _SpiritBeing(SpiritPower):
    def __init__(self):
        super().__init__(name="Spirit Being", icon="invisible", power_level=LOW_POWER)
        self.resistances = {
            DamageType.Fire,
            DamageType.Lightning,
            DamageType.Acid,
            DamageType.Thunder,
        }
        self.resistances_str = comma_separated(
            sorted([damage_type.name for damage_type in self.resistances]),
            conjunction="and",
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)

        stats.grant_resistance_or_immunity(
            resistances=self.resistances,
            immunities={DamageType.Cold, DamageType.Necrotic, DamageType.Poison},
            conditions={
                Condition.Poisoned,
                Condition.Exhaustion,
                Condition.Grappled,
                Condition.Restrained,
                Condition.Prone,
            },
        )

        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature1 = Feature(
            name="Incorporeal",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} cannot be pushed or knocked back. It can move through creatures and objects as if they were difficult terrain. It takes 1d10 force damage if it ends its turn inside an object.",
        )

        feature2 = Feature(
            name="Sunlight Weakness",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} cannot recharge and loses all resistances while in sunlight.",
        )

        return [feature1, feature2]


class _Haunt(SpiritPower):
    def __init__(self):
        super().__init__(name="Haunt", icon="haunting", power_level=LOW_POWER)

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        cursed = conditions.Cursed()
        feature = Feature(
            name="Haunt",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} binds itself to an object it can see within 60 feet. The object is {cursed.caption}.\
                {stats.selfref.capitalize()} can use 5 feet of movement to teleport into the object from any plane of existance while the curse remains.",
        )
        return [feature]


class _SpiritStep(SpiritPower):
    def __init__(self):
        super().__init__(
            name="Spirit Step", icon="ghost-ally", power_level=MEDIUM_POWER
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dash = action_ref("Dash")
        disengage = action_ref("Disengage")
        dmg = stats.target_value(dpr_proportion=0.25, force_die=Die.d4)
        feature = Feature(
            name="Spirit Step",
            action=ActionType.BonusAction,
            recharge=4,
            description=f"{stats.selfref.capitalize()} uses {dash} and {disengage}. Any creature that it moves through this turn takes {dmg.description} cold damage.",
        )
        return [feature]


class _SpiritFlicker(SpiritPower):
    def __init__(self):
        super().__init__(name="Spirit Flicker", icon="soul", power_level=MEDIUM_POWER)

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Spirit Flicker",
            action=ActionType.Reaction,
            recharge=4,
            description=f"When {stats.selfref} is hit by an attack it flickers and teleports up to 30 feet away (including into an object).",
        )
        return [feature]


class _NameTheForgotten(SpiritPower):
    def __init__(self):
        super().__init__(
            name="Name the Forgotten",
            icon="black-book",
            power_level=LOW_POWER,
            require_cr=2,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        invisibility = spell_ref("Invisibility")
        cursed = conditions.Cursed()
        feature = Feature(
            name="Name the Forgotten",
            action=ActionType.Feature,
            description=f"If any creature speaks {stats.selfref}'s name then it becomes {cursed.caption} for the next hour. While cursed, {stats.selfref} knows that creature's location, regardless of distance or plane of existance. \
                {stats.selfref.capitalize()} can use an action to teleport to within 60 feet of that creature and arrives under the effects of the {invisibility} spell.",
        )
        return [feature]


class _GraspOfTheDead(SpiritPower):
    def __init__(self):
        super().__init__(
            name="Grasp of the Dead", icon="raise-skeleton", power_level=MEDIUM_POWER
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        dmg = stats.target_value(dpr_proportion=0.5, force_die=Die.d8)
        frozen = conditions.Frozen(dc=dc)
        feature = Feature(
            name="Grasp of the Dead",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} creates a 20-foot radius sphere centered on itself. \
                Each creature in that area must make a DC {dc} Dexterity save or take {dmg.description} cold damage and become {frozen.caption}. {frozen.description_3rd}",
        )
        return [feature]


class _FeedOnLight(SpiritPower):
    def __init__(self):
        super().__init__(
            name="Feed on Light",
            reference_statblock="Shadow",
            icon="shadow-follower",
            power_level=MEDIUM_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        temp_hp = easy_multiple_of_five(stats.hp.average * 0.15)
        feature = Feature(
            name="Feed on Light",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=4,
            description=f"{stats.selfref.capitalize()} extinguishes all mundane and magical light sources created from spell effects of 3rd level or lower within 30 feet. \
                If it does so, it gains {temp_hp} temp hp for each such light source extinguished.",
        )
        return [feature]


class _ShadowInvisibility(SpiritPower):
    def __init__(self):
        super().__init__(
            name="Shadow Invisibility",
            reference_statblock="Shadow",
            icon="shadow-grasp",
            power_level=MEDIUM_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        invisibility = spell_ref("Invisibility")
        feature = Feature(
            name="Shadow Invisibility",
            action=ActionType.BonusAction,
            recharge=4,
            description=f"{stats.selfref.capitalize()} casts {invisibility} on itself if it is in dim light or darkness.",
        )
        return [feature]


class _DreadfulSilence(SpiritPower):
    def __init__(self):
        super().__init__(
            name="Dreadful Silence",
            reference_statblock="Banshee",
            icon="silenced",
            power_level=LOW_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(dpr_proportion=0.2, force_die=Die.d6)
        feature = Feature(
            name="Dreadful Silence",
            action=ActionType.Feature,
            description=f"Any creature that speaks louder than a whisper or casts a spell with a Verbal component while within 30 feet of {stats.selfref} takes {dmg} psychic damage.",
        )
        return [feature]


class _Posession(SpiritPower):
    def __init__(self):
        super().__init__(
            name="Possession", icon="voodoo-doll", power_level=MEDIUM_POWER
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        cursed = conditions.Cursed()
        invisible = Condition.Invisible.caption
        dominate_person = spell_ref("Dominate Person")
        feature = Feature(
            name="Possession",
            action=ActionType.Action,
            recharge=6,
            description=f"{stats.selfref.capitalize()} attempts to possess a creature within 15 feet. The target must make a DC {dc} Charisma saving throw. \
                On a failure, the target is {cursed.caption}. {stats.selfref.capitalize()} may only have one such curse active at a time. \
                While the curse persists, {stats.selfref} is {invisible} and cannot be targeted by any attack, spell, or effect unless it specifically targets Undead. \
                Also, the target is under the effect of the {dominate_person} spell, except that the target does not repeat the saving throw whenever it takes damage. \
                If the spell ends while the curse is active, the target becomes afflicted by the spell again on its next turn. The curse may be broken by dealing damage to {stats.selfref} or by sprinkling holy water on the target.",
        )
        return [feature]


SpiritBeing: Power = _SpiritBeing()
Haunt: Power = _Haunt()
SpiritStep: Power = _SpiritStep()
SpiritFlicker: Power = _SpiritFlicker()
NameTheForgotten: Power = _NameTheForgotten()
GraspOfTheDead: Power = _GraspOfTheDead()
FeedOnLight: Power = _FeedOnLight()
ShadowInvisibility: Power = _ShadowInvisibility()
DreadfulSilence: Power = _DreadfulSilence()
Possession: Power = _Posession()

SpiritPowers: List[Power] = [
    SpiritBeing,
    Haunt,
    SpiritStep,
    SpiritFlicker,
    NameTheForgotten,
    GraspOfTheDead,
    FeedOnLight,
    ShadowInvisibility,
    DreadfulSilence,
    Possession,
]
