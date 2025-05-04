import numpy as np

from ..ac_templates import UnholyArmor
from ..attack_template import spell
from ..creature_types import CreatureType
from ..damage import Condition, DamageType
from ..powers import (
    LOW_POWER,
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    select_powers,
)
from ..powers.creature import nothic
from ..powers.creature_type import aberration
from ..powers.roles import controller
from ..powers.themed import anti_magic, chaotic, cursed, flying, temporal
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..statblocks import BaseStatblock
from ._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from .base_stats import base_stats

HollowGazerVariant = MonsterVariant(
    name="Hollow Gazer",
    description="Hollow Gazers are seekers of dark and forbidden knowledge that have been driven insane by cursed knowledge best left unknown.",
    monsters=[
        Monster(name="Hollow Gazer", cr=2, other_creatures={"Nothic": "mm24"}),
        Monster(name="Hollow Gazer of Ruin", cr=6),
    ],
)


class _HollowGazerWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, rng: np.random.Generator):
        self.stats = stats
        self.rng = rng

    def force_powers(self) -> list[Power]:
        other_powers = nothic.NothicPowers.copy()
        other_powers.remove(nothic.WarpingMadness)

        power_index = self.rng.choice(len(other_powers))
        return [nothic.WarpingMadness, other_powers[power_index]]

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        powers = [
            aberration.GazeOfTheFarRealm,
            aberration.MadenningWhispers,
            controller.Eyebite,
            cursed.DisfiguringCurse,
            temporal.AlterFate,
            anti_magic.SpellEater,
        ] + nothic.NothicPowers

        if self.stats.cr >= 6:
            powers += [chaotic.EldritchBeacon]

        suppress = flying.FlyingPowers + controller.ControllerPowers

        if p in suppress:
            return CustomPowerWeight(weight=-1, ignore_usual_requirements=False)
        elif p in powers:
            return CustomPowerWeight(weight=2.0, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(weight=0.5, ignore_usual_requirements=False)

    def power_delta(self) -> float:
        return LOW_POWER


def generate_hollow_gazer(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    rng = settings.rng

    # STATS
    stats = base_stats(
        name=name,
        variant_key=settings.variant.key,
        template_key=settings.monster_template,
        monster_key=settings.monster_key,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Default, mod=-2),
            Stats.DEX.scaler(StatScaling.Medium),
            Stats.INT.scaler(StatScaling.Primary),
            Stats.WIS.scaler(StatScaling.Medium, mod=1),
            Stats.CHA.scaler(StatScaling.Default, mod=-3),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Aberration,
        size=Size.Medium,
        creature_class="Hollow Gazer",
        languages=["Almost Comprehensible Gibberish"],
        senses=stats.senses.copy(truesight=120),
    )

    # ARMOR CLASS
    stats = stats.add_ac_template(UnholyArmor)

    # ATTACKS
    attack = spell.Gaze.with_display_name("Pitying Gaze")
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(secondary_damage_type=DamageType.Psychic)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Controller,
    )

    # SKILLS
    expertise = [Skills.Arcana, Skills.Insight, Skills.Perception]
    stats = stats.grant_proficiency_or_expertise(
        Skills.Stealth, *expertise
    ).grant_proficiency_or_expertise(*expertise)

    # SAVES
    if cr >= 6:
        stats = stats.grant_save_proficiency(Stats.WIS, Stats.CON)

    # RESISTANCES / IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        conditions={Condition.Charmed}, resistances={DamageType.Psychic}
    )

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_HollowGazerWeights(stats, rng),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


HollowGazerTemplate: MonsterTemplate = MonsterTemplate(
    name="Hollow Gazer",
    tag_line="Insane Seekers of Twisted Knowledge",
    description="Hollow Gazers are seekers of dark and forbidden knowledge that have been driven insane by cursed knowledge best left unknown.",
    environments=["Underdark"],
    treasure=[],
    variants=[HollowGazerVariant],
    species=[],
    callback=generate_hollow_gazer,
)
