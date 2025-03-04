from foe_foundry.powers.power import Power
from foe_foundry.powers.selection.custom import CustomPowerWeight

from ..ac_templates import StuddedLeatherArmor
from ..attack_template import weapon
from ..creature_types import CreatureType
from ..damage import DamageType
from ..powers import CustomPowerSelection, select_powers
from ..powers.roles.ambusher import DeadlyAmbusher, StealthySneak
from ..powers.roles.artillery import QuickDraw
from ..powers.roles.skirmisher import CunningAction
from ..powers.themed.charm import CharmingWords
from ..powers.themed.fast import NimbleReaction
from ..powers.themed.gadget import GadgetPowers, PotionOfHealing, SmokeBomb
from ..powers.themed.poison import PoisonDart, WeakeningPoison
from ..powers.themed.technique import PoisonedAttack
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..statblocks import MonsterDials
from ..utils.interpolate import interpolate_by_cr
from .base_stats import base_stats
from .species import AllSpecies, HumanSpecies
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

SpyVariant = CreatureVariant(
    name="Spy",
    description="Bandits are inexperienced ne’er-do-wells who typically follow the orders of higher-ranking bandits.",
    suggested_crs=[
        SuggestedCr(name="Spy", cr=1, srd_creatures=["Spy"]),
        SuggestedCr(name="Elite Spy", cr=4),
    ],
)
SpyMasterVariant = CreatureVariant(
    name="Spy Master",
    description="Bandit captains command gangs of scoundrels and conduct straightforward heists. Others serve as guards and muscle for more influential criminals.",
    suggested_crs=[
        SuggestedCr(
            name="Spy Master",
            cr=10,
            other_creatures={"Spy Master": "mm25"},
            is_legendary=True,
        ),
    ],
)


class _CustomPowers(CustomPowerSelection):
    def force_powers(self) -> list[Power]:
        return [CunningAction]

    def custom_weight(self, power: Power) -> CustomPowerWeight:
        suppress_powers = set(GadgetPowers)
        suppress_powers.discard(SmokeBomb)
        suppress_powers.discard(PotionOfHealing)

        desirable_powers = [
            StealthySneak,
            DeadlyAmbusher,
            PoisonDart,
            PoisonedAttack,
            CharmingWords,
            QuickDraw,
            NimbleReaction,
            SmokeBomb,
            PotionOfHealing,
            WeakeningPoison,
        ]

        if power in suppress_powers:
            return CustomPowerWeight(weight=-1)
        elif power in desirable_powers:
            return CustomPowerWeight(weight=2.5, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(weight=0.75, ignore_usual_requirements=False)


def generate_spy(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    species = settings.species if settings.species else HumanSpecies
    rng = settings.rng

    # STATS
    stats = base_stats(
        name=variant.name,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Default),
            Stats.DEX.scaler(StatScaling.Primary),
            Stats.INT.scaler(StatScaling.Medium, mod=0.5),
            Stats.WIS.scaler(StatScaling.Medium, mod=1),
            Stats.CHA.scaler(StatScaling.Medium, mod=1),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )
    stats = stats.copy(
        name=name,
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Spy",
        speed=stats.speed.grant_climbing(),
        primary_damage_type=DamageType.Piercing,
    )

    ## HP
    # spies have lower HP than average
    stats = stats.apply_monster_dials(MonsterDials(hp_multiplier=0.85))

    # ARMOR CLASS
    # based off Spy and Spy Master stats
    ac_modifier = int(interpolate_by_cr(cr, {1: 0, 4: 1, 10: 2, 15: 3}))
    if cr >= 4:
        stats = stats.add_ac_template(StuddedLeatherArmor, ac_modifier=ac_modifier)

    # ATTACKS

    # Spies use poison as their secondary damage type
    # This means we want fewer overall attacks but more damage dice that include poison
    stats = stats.copy(
        secondary_damage_type=DamageType.Poison,
    )
    stats = stats.with_reduced_attacks(reduce_by=1 if stats.cr <= 8 else 2)

    # Spies use poisoned Daggers as their primary attack
    attack = weapon.Daggers.with_display_name("Covert Blade")
    stats = attack.alter_base_stats(stats, rng)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(primary_damage_type=attack.damage_type)

    # Spies also have a Hand Crossbow as a secondary attack
    secondary_attack = weapon.HandCrossbow.with_display_name("Concealed Crossbow")
    stats = secondary_attack.add_as_secondary_attack(stats)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Ambusher,
        additional_roles=[
            MonsterRole.Skirmisher,
            MonsterRole.Artillery,
        ],
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(
        Skills.Deception,
        Skills.Insight,
        Skills.Investigation,
        Skills.Perception,
        Skills.SleightOfHand,
        Skills.Stealth,
        Skills.Initiative,
    )

    # EXPERTISE
    if cr >= 6:
        stats = stats.grant_proficiency_or_expertise(
            Skills.Stealth, Skills.Perception, Skills.Initiative
        )

    # SAVES
    if cr >= 6:
        stats = stats.grant_save_proficiency(Stats.DEX, Stats.CON, Stats.INT, Stats.WIS)

    # LEGENDARY
    if variant == SpyMasterVariant:
        stats = stats.as_legendary()

    # POWERS
    features = []

    # SPECIES CUSTOMIZATIONS
    stats = species.alter_base_stats(stats)

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_CustomPowers(),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    stats = secondary_attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


SpyTemplate: CreatureTemplate = CreatureTemplate(
    name="Spy",
    tag_line="Infiltrators and Informants",
    description="Spies gather information and disseminate lies, manipulating people to gain the results the spies' patrons desire. They're trained to manipulate, infiltrate, and—when necessary—escape in a hurry. Many adopt disguises, aliases, or code names to maintain anonymity.",
    environments=["Urban"],
    treasure=["Any"],
    variants=[SpyVariant, SpyMasterVariant],
    species=AllSpecies,
    callback=generate_spy,
)
