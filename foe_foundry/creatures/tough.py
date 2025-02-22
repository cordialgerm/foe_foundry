import numpy as np

from ..ac_templates import LightArmor, MediumArmor
from ..attack_template import natural, weapon
from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..die import Die
from ..powers import Power, select_powers
from ..powers.legendary import make_legendary
from ..powers.themed.warrior import PackTactics
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

ThugVariant = CreatureVariant(
    name="Thug",
    description="Thugs might work in groups at the direction of a leader, or individual toughs might bully weaker folk into doing what they say.",
    suggested_crs=[
        SuggestedCr(name="Thug", cr=0.5, srd_creatures=["Thug", "Tough"]),
        SuggestedCr(name="Veteran Thug", cr=2),
        SuggestedCr(name="Elite Thug", cr=4),
    ],
)
BrawlerVariant = CreatureVariant(
    name="Brawler",
    description="Brawlers rely on their physical strength and intimidation to get what they want. They might be bouncers, enforcers, or just rowdy tavern goers.",
    suggested_crs=[
        SuggestedCr(name="Brawler", cr=0.5),
        SuggestedCr(name="Veteran Brawler", cr=2),
        SuggestedCr(name="Elite Brawler", cr=4),
    ],
)
BossVariant = CreatureVariant(
    name="Boss",
    description="Thug bosses leverage their street smarts, brawling prowess, and reputation to compel others to follow their demands.",
    suggested_crs=[
        SuggestedCr(name="Thug Boss", cr=2, other_creatures={"Tough Boss": "mm25"}),
        SuggestedCr(name="Thug Overboss", cr=4),
        SuggestedCr(name="Thug Legend", cr=8, is_legendary=True),
    ],
)


def generate_tough(
    name: str,
    cr: float,
    variant: CreatureVariant,
    species: CreatureSpecies,
    rng: np.random.Generator,
) -> StatsBeingGenerated:
    # STATS
    stats = base_stats(
        name=name,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Medium, 0.5),
            Stats.INT.scaler(StatScaling.Default, mod=-1),
            Stats.WIS.scaler(StatScaling.Default),
            Stats.CHA.scaler(StatScaling.Medium),
        ],
    )

    stats = stats.copy(
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Thug",
    )

    # ARMOR CLASS
    if variant is BossVariant:
        stats = stats.add_ac_template(MediumArmor, ac_modifier=1 if cr >= 4 else 0)
    else:
        stats = stats.add_ac_template(LightArmor, ac_modifier=1 if cr >= 4 else 0)

    # ATTACKS
    if variant is BrawlerVariant:
        attack = natural.Slam
    else:
        attack = weapon.Maul

    stats = attack.alter_base_stats(stats, rng)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(primary_damage_type=attack.damage_type)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Leader
        if variant is BossVariant
        else MonsterRole.Bruiser,
        additional_roles=[MonsterRole.Bruiser],
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Intimidation)

    if stats.cr >= 8:
        stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

    # SAVES
    if cr >= 2:
        stats = stats.grant_save_proficiency(Stats.STR)

    if cr >= 4:
        stats = stats.grant_save_proficiency(Stats.CON, Stats.CHA)

    # POWERS
    features = []

    # Toughs always have Pack Tactics power
    features += PackTactics.generate_features(stats)
    stats = PackTactics.modify_stats(stats)
    stats = stats.apply_monster_dials(
        MonsterDials(
            recommended_powers_modifier=-PackTactics.power_level / 2
        )  # discount Pack Tactics cost somewhat to account for it being mandatory
    )

    # Toughs with a Mace also have a heavy crossbow
    if attack == weapon.Maul:
        stats = stats.add_attack(
            name="Heavy Crossbow",
            scalar=0.7 * min(stats.multiattack, 2),
            attack_type=AttackType.RangedWeapon,
            range=100,
            damage_type=DamageType.Piercing,
            die=Die.d10,
            replaces_multiattack=2,
        )

    # SPECIES CUSTOMIZATIONS
    stats = species.alter_base_stats(stats)

    # ADDITIONAL POWERS
    def custom_filter(power: Power) -> bool:
        return power is not PackTactics

    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        power_level=stats.recommended_powers,
        custom_filter=custom_filter,
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng)

    # LEGENDARY
    if variant is BossVariant and cr >= 8:
        stats, features = make_legendary(stats, features, has_lair=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


ToughTemplate: CreatureTemplate = CreatureTemplate(
    name="Tough",
    tag_line="Brawlers and Bullies",
    description="Bodyguards, belligerents, and laborers, toughs rely on their physical strength to intimidate foes. They might be brawny criminals, rowdy tavern goers, seasoned workers, or anyone who uses their muscle to get what they want.",
    environments=["Urban"],
    treasure=["Armaments"],
    variants=[ThugVariant, BrawlerVariant, BossVariant],
    species=AllSpecies,
    callback=generate_tough,
)
