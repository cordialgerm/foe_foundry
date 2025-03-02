import numpy as np

from ..ac_templates import LeatherArmor, StuddedLeatherArmor
from ..attack_template import weapon
from ..creature_types import CreatureType
from ..powers import CustomPowerSelection, CustomPowerWeight, Power, select_powers
from ..powers.legendary import make_legendary
from ..powers.roles.artillery import FocusShot
from ..powers.roles.skirmisher import HarassingRetreat
from ..powers.themed.clever import IdentifyWeaknes
from ..powers.themed.gadget import PotionOfHealing, SmokeBomb
from ..powers.themed.sneaky import Vanish
from ..powers.themed.trap import TrapPowers
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from .base_stats import BaseStatblock, base_stats
from .species import AllSpecies
from .template import (
    CreatureSpecies,
    CreatureTemplate,
    CreatureVariant,
    StatsBeingGenerated,
    SuggestedCr,
)


class _CustomWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, variant: CreatureVariant):
        self.stats = stats
        self.variant = variant

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        if p in {HarassingRetreat, Vanish, FocusShot, IdentifyWeaknes}:
            return CustomPowerWeight(weight=2, ignore_usual_requirements=True)
        elif p in TrapPowers:
            return CustomPowerWeight(weight=1.5, ignore_usual_requirements=True)
        elif p in {SmokeBomb, PotionOfHealing}:
            return CustomPowerWeight(weight=1.5, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(weight=0.75, ignore_usual_requirements=False)


ScoutVariant = CreatureVariant(
    name="Scout",
    description="Guards are perceptive, but most have little martial training. They might be bouncers, lookouts, members of a city watch, or other keen-eyed warriors.",
    suggested_crs=[
        SuggestedCr(
            name="Scout",
            cr=1 / 2,
            srd_creatures=["Scout"],
        ),
        SuggestedCr(name="Ranger", cr=5),
    ],
)
CommanderVariant = CreatureVariant(
    name="Scout Captain",
    description="Scout captains are experienced explorers and sharpshooters. They might lead bands of other scouts or disappear into the wilds alone for months at a time.",
    suggested_crs=[
        SuggestedCr(
            name="Scout Captain",
            cr=3,
            other_creatures={"Scout Captain": "mm25"},
        ),
        SuggestedCr(name="First Scout", cr=7, is_legendary=True),
    ],
)


def generate_scout(
    name: str,
    cr: float,
    variant: CreatureVariant,
    species: CreatureSpecies,
    rng: np.random.Generator,
) -> StatsBeingGenerated:
    # STATS

    stat_scaling = [
        Stats.STR.scaler(StatScaling.Default),
        Stats.DEX.scaler(StatScaling.Primary),
        Stats.INT.scaler(StatScaling.Default, mod=0.5),
        Stats.WIS.scaler(StatScaling.Medium, mod=1),
        Stats.CHA.scaler(StatScaling.Default, mod=0.5),
    ]

    stats = base_stats(name=name, cr=cr, stats=stat_scaling)

    stats = stats.copy(
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Scout",
    )

    # ARMOR CLASS
    if stats.cr >= 3:
        stats = stats.add_ac_template(StuddedLeatherArmor)
    else:
        stats = stats.add_ac_template(LeatherArmor)

    # ATTACKS
    attack = weapon.Longbow
    secondary_attack = weapon.Shortswords

    stats = attack.alter_base_stats(stats, rng)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(primary_damage_type=attack.damage_type)
    stats = secondary_attack.add_as_secondary_attack(stats)
    stats = stats.copy(uses_shield=False)

    # ROLES
    primary_role = MonsterRole.Skirmisher
    additional_roles = [MonsterRole.Artillery, MonsterRole.Ambusher]
    if variant is CommanderVariant:
        additional_roles.append(MonsterRole.Leader)

    stats = stats.with_roles(
        primary_role=primary_role,
        additional_roles=additional_roles,
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(
        Skills.Perception,
        Skills.Nature,
        Skills.Survival,
        Skills.Stealth,
        Skills.Initiative,
    )
    if cr >= 3:
        stats = stats.grant_proficiency_or_expertise(
            Skills.Perception, Skills.Stealth, Skills.Survival
        )

    # SAVES
    if cr >= 3:
        stats = stats.grant_save_proficiency(Stats.DEX, Stats.INT)
    if cr >= 7:
        stats = stats.grant_save_proficiency(Stats.WIS)

    # POWERS
    features = []

    # SPECIES CUSTOMIZATIONS
    stats = species.alter_base_stats(stats)

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        power_level=stats.recommended_powers,
        custom=_CustomWeights(stats, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng)

    # LEGENDARY
    if variant is CommanderVariant and stats.cr >= 7:
        stats, features = make_legendary(stats, features, has_lair=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


ScoutTemplate: CreatureTemplate = CreatureTemplate(
    name="Scout",
    tag_line="Watchers and Wanderers",
    description="Scouts are warriors of the wilderness, trained in hunting and tracking. They might be explorers or trappers, or they could perform more martial roles as archers, bounty hunters, or outriders.",
    environments=["Any"],
    treasure=[],
    variants=[ScoutVariant, CommanderVariant],
    species=AllSpecies,
    callback=generate_scout,
)
