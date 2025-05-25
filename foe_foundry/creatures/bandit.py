from foe_foundry.powers.power import Power
from foe_foundry.powers.selection.custom import CustomPowerWeight

from ..ac_templates import StuddedLeatherArmor
from ..attack_template import weapon
from ..creature_types import CreatureType
from ..damage import DamageType
from ..powers import CustomPowerSelection, PowerType, select_powers
from ..powers.roles import artillery, leader
from ..powers.themed import gadget, honorable, sneaky, technique, thuggish
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..statblocks import MonsterDials
from ._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from .base_stats import BaseStatblock, base_stats
from .species import AllSpecies, HumanSpecies

BanditVariant = MonsterVariant(
    name="Bandit",
    description="Bandits are inexperienced ne'er-do-wells who typically follow the orders of higher-ranking bandits.",
    monsters=[
        Monster(name="Bandit", cr=1 / 8, srd_creatures=["Bandit"]),
        Monster(name="Bandit Veteran", cr=1),
    ],
)
BanditCaptainVariant = MonsterVariant(
    name="Bandit Captain",
    description="Bandit captains command gangs of scoundrels and conduct straightforward heists. Others serve as guards and muscle for more influential criminals.",
    monsters=[
        Monster(name="Bandit Captain", cr=2, srd_creatures=["Bandit Captain"]),
        Monster(
            name="Bandit Crime Lord",
            cr=11,
            other_creatures={"Bandit Crime Lord": "mm25"},
            is_legendary=True,
        ),
    ],
)


class _BanditPowers(CustomPowerSelection):
    def __init__(self, variant: MonsterVariant, stats: BaseStatblock):
        self.variant = variant
        self.stats = stats

    def custom_weight(self, power: Power) -> CustomPowerWeight:
        captain_powers = [
            leader.CommandTheAttack,
            leader.FanaticFollowers,
            leader.StayInFormation,
        ] + thuggish.ThuggishPowers

        high_cr_powers = [leader.Intimidate]

        standard_powers = [
            sneaky.CheapShot,
            artillery.SuppresingFire,
            technique.VexingAttack,
            technique.Sharpshooter,
            sneaky.ExploitAdvantage,
            artillery.Overwatch,
            artillery.FocusShot,
            gadget.SmokeBomb,
        ]

        suppress = honorable.HonorablePowers

        powers = []
        powers += standard_powers
        if self.stats.cr >= 1:
            powers += high_cr_powers
        if self.variant is BanditCaptainVariant:
            powers += captain_powers

        if power in suppress:
            return CustomPowerWeight(-1, ignore_usual_requirements=False)
        elif power in powers:
            return CustomPowerWeight(2.5, ignore_usual_requirements=True)
        elif power.power_type == PowerType.Species:
            # boost species powers but still respect requirements
            return CustomPowerWeight(2.0, ignore_usual_requirements=False)
        else:
            return CustomPowerWeight(0.75, ignore_usual_requirements=False)


def generate_bandit(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    species = settings.species if settings.species else HumanSpecies
    rng = settings.rng
    is_legendary = settings.is_legendary

    # STATS
    stats = base_stats(
        name=variant.name,
        variant_key=settings.variant.key,
        template_key=settings.monster_template,
        monster_key=settings.monster_key,
        species_key=species.key,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Medium, mod=0.5),
            Stats.DEX.scaler(StatScaling.Primary),
            Stats.INT.scaler(StatScaling.Medium, mod=-0.5),
            Stats.WIS.scaler(StatScaling.Default),
            Stats.CHA.scaler(StatScaling.Medium, mod=-0.5),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        name=name,
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Bandit",
    )

    # ARMOR CLASS
    stats = stats.add_ac_template(StuddedLeatherArmor, ac_modifier=1 if cr >= 4 else 0)

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    # ATTACKS
    attack = weapon.Pistol if cr >= 1 else weapon.Shortswords
    stats = attack.alter_base_stats(stats)
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
        else MonsterRole.Artillery,
        additional_roles=[MonsterRole.Ambusher, MonsterRole.Artillery],
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
        settings=settings.selection_settings,
        custom=_BanditPowers(variant, stats),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    stats = secondary_attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


BanditTemplate: MonsterTemplate = MonsterTemplate(
    name="Bandit",
    tag_line="Criminals and Scoundrels",
    description="Bandits use the threat of violence to take what they want. Such criminals include gang members, desperadoes, and lawless mercenaries. Yet not all bandits are motivated by greed. Some are driven to lives of crime by unjust laws, desperation, or the threats of merciless leaders.",
    environments=["Urban"],
    treasure=["Any"],
    variants=[BanditVariant, BanditCaptainVariant],
    species=AllSpecies,
    callback=generate_bandit,
)
