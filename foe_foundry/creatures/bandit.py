import numpy as np

from ..ac_templates import LightArmor
from ..attack_template import weapon
from ..creature_types import CreatureType
from ..damage import DamageType
from ..powers import select_powers
from ..powers.legendary import make_legendary
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..statblocks import MonsterDials
from .base_stats import base_stats
from .species import AllSpecies
from .template import (
    CreatureSpecies,
    CreatureTemplate,
    CreatureVariant,
    StatsBeingGenerated,
    SuggestedCr,
)

BanditVariant = CreatureVariant(
    name="Bandit",
    description="Bandits are inexperienced ne'er-do-wells who typically follow the orders of higher-ranking bandits.",
    suggested_crs=[
        SuggestedCr(name="Bandit", cr=1 / 8, srd_creatures=["Bandit"]),
        SuggestedCr(name="Bandit Veteran", cr=1),
    ],
)
BanditCaptainVariant = CreatureVariant(
    name="Bandit Captain",
    description="Bandit captains command gangs of scoundrels and conduct straightforward heists. Others serve as guards and muscle for more influential criminals.",
    suggested_crs=[
        SuggestedCr(name="Bandit Captain", cr=2, srd_creatures=["Bandit Captain"]),
        SuggestedCr(
            name="Bandit Crime Lord",
            cr=11,
            other_creatures={"Bandit Crime Lord": "mm25"},
            is_legendary=True,
        ),
    ],
)


def generate_bandit(
    name: str,
    cr: float,
    variant: CreatureVariant,
    species: CreatureSpecies,
    rng: np.random.Generator,
) -> StatsBeingGenerated:
    # STATS
    stats = base_stats(
        name=variant.name,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Medium, mod=0.5),
            Stats.DEX.scaler(StatScaling.Primary),
            Stats.INT.scaler(StatScaling.Medium, mod=-0.5),
            Stats.WIS.scaler(StatScaling.Default),
            Stats.CHA.scaler(StatScaling.Medium, mod=-0.5),
        ],
    )

    stats = stats.copy(
        name=name,
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Bandit",
    )

    # ARMOR CLASS
    stats = stats.add_ac_template(LightArmor, ac_modifier=1 if cr >= 4 else 0)

    # ATTACKS
    attack = weapon.Pistol if cr >= 1 else weapon.Shortswords
    stats = attack.alter_base_stats(stats, rng)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(primary_damage_type=attack.damage_type)

    # High CR criminals use poison as their secondary damage type
    # This means we want fewer overall attacks but more damage dice that include poison
    if cr >= 6:
        stats = stats.copy(secondary_damage_type=DamageType.Poison)
        stats = stats.apply_monster_dials(
            MonsterDials(
                multiattack_modifier=-1,
                attack_damage_multiplier=stats.multiattack / (stats.multiattack - 1),
            )
        )

    # Bandits with a Pistol also have Shortswords as a secondary attack
    # Bandits with Shortswords also have a Crossbow as a secondary attack
    if attack == weapon.Pistol:
        secondary_attack = weapon.Shortswords
    else:
        secondary_attack = weapon.Crossbow.with_display_name("Light Crossbow")

    stats = secondary_attack.add_as_secondary_attack(stats)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Leader
        if variant is BanditCaptainVariant
        else MonsterRole.Ambusher,
        additional_roles=[
            MonsterRole.Skirmisher,
            MonsterRole.Ambusher,
            MonsterRole.Artillery,
        ],
    )

    # SKILLS
    skills = [Skills.Stealth]
    if variant is BanditCaptainVariant:
        skills += [Skills.Deception, Skills.Athletics]
    if cr >= 6:
        skills += [Skills.Perception, Skills.Initiative]
    stats = stats.grant_proficiency_or_expertise(*skills)

    # EXPERTISE
    if cr >= 6:
        stats = stats.grant_proficiency_or_expertise(Skills.Stealth)
    if cr >= 11:
        stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

    # SAVES
    if cr >= 2:
        stats = stats.grant_save_proficiency(Stats.STR, Stats.DEX)

    if cr >= 4:
        stats = stats.grant_save_proficiency(Stats.STR, Stats.DEX, Stats.CON)

    # POWERS
    features = []

    # SPECIES CUSTOMIZATIONS
    stats = species.alter_base_stats(stats)

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        power_level=stats.recommended_powers,
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    stats = secondary_attack.finalize_attacks(stats, rng, repair_all=False)

    # LEGENDARY
    if variant is BanditCaptainVariant and stats.cr >= 11:
        stats, features = make_legendary(stats, features, has_lair=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


BanditTemplate: CreatureTemplate = CreatureTemplate(
    name="Bandit",
    tag_line="Criminals and Scoundrels",
    description="Bandits use the threat of violence to take what they want. Such criminals include gang members, desperadoes, and lawless mercenaries. Yet not all bandits are motivated by greed. Some are driven to lives of crime by unjust laws, desperation, or the threats of merciless leaders.",
    environments=["Urban"],
    treasure=["Any"],
    variants=[BanditVariant, BanditCaptainVariant],
    species=AllSpecies,
    callback=generate_bandit,
)
