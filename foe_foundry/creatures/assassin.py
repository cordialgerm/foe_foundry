from ..ac_templates import StuddedLeatherArmor
from ..attack_template import weapon
from ..creature_types import CreatureType
from ..damage import DamageType
from ..powers import CustomPowerSelection, CustomPowerWeight, Power, select_powers
from ..powers.roles.skirmisher import CunningAction
from ..powers.themed.anti_magic import SealOfSilence
from ..powers.themed.anti_ranged import HardToPinDown
from ..powers.themed.clever import IdentifyWeaknes
from ..powers.themed.cruel import BrutalCritical
from ..powers.themed.fast import Evasion, NimbleReaction
from ..powers.themed.fearsome import DreadGaze
from ..powers.themed.gadget import GrenadePowers
from ..powers.themed.technique import PoisonedAttack
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..statblocks import MonsterDials
from .base_stats import base_stats
from .species import AllSpecies, HumanSpecies
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)


class _CustomPowers(CustomPowerSelection):
    def custom_weight(self, power: Power) -> CustomPowerWeight:
        custom_powers = [
            BrutalCritical,
            IdentifyWeaknes,
            SealOfSilence,
            HardToPinDown,
            Evasion,
            NimbleReaction,
            DreadGaze,
            PoisonedAttack,
        ] + GrenadePowers
        if power in custom_powers:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(1.0, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        return [CunningAction]


AssassinVariant = CreatureVariant(
    name="Assassin",
    description="Assassins are professional killers skilled at stealthily approaching their victims and striking unseen. Most assassins kill for a reason, perhaps hiring themselves out to wealthy patrons or slaying for an unscrupulous cause. They use poisons and other deadly tools, and they might carry equipment to help them break into secure areas or avoid capture.",
    suggested_crs=[
        SuggestedCr(name="Contract Killer", cr=4),
        SuggestedCr(name="Assassin", cr=8, srd_creatures=["Assassin"]),
        SuggestedCr(name="Assassin Legend", cr=12, is_legendary=True),
    ],
)


def generate_assassin(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    species = settings.species if settings.species else HumanSpecies
    rng = settings.rng
    is_legendary = settings.is_legendary

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
        creature_class="Assassin",
        speed=stats.speed.grant_climbing(),
        primary_damage_type=DamageType.Piercing,
    )

    if is_legendary:
        stats = stats.as_legendary()

    ## HP
    # Assassins have lower HP than average
    stats = stats.apply_monster_dials(MonsterDials(hp_multiplier=0.85))

    # ARMOR CLASS
    stats = stats.add_ac_template(StuddedLeatherArmor, ac_modifier=1 if cr >= 10 else 0)

    # ATTACKS

    # Spies use poison as their secondary damage type
    # This means we want fewer overall attacks but more damage dice that include poison
    stats = stats.copy(
        secondary_damage_type=DamageType.Poison,
    )

    if stats.cr <= 4:
        stats = stats.with_set_attacks(1)
    elif stats.multiattack > 2:
        stats = stats.with_set_attacks(2)

    # Spies use poisoned Daggers as their primary attack
    attack = weapon.Daggers.with_display_name("Poisoned Dagger")
    stats = attack.alter_base_stats(stats, rng)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(primary_damage_type=attack.damage_type)

    # Spies also have a Hand Crossbow as a secondary attack
    secondary_attack = weapon.HandCrossbow.with_display_name("Poisoned Hand Crossbow")
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
        Skills.Acrobatics, Skills.Perception, Skills.Stealth, Skills.Initiative
    )

    # EXPERTISE
    if cr >= 6:
        stats = stats.grant_proficiency_or_expertise(
            Skills.Stealth, Skills.Perception, Skills.Initiative
        )

    # SAVES
    if cr >= 6:
        stats = stats.grant_save_proficiency(Stats.DEX, Stats.INT)

    # POWERS
    features = []

    # SPECIES CUSTOMIZATIONS
    stats = species.alter_base_stats(stats)

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


AssassinTemplate: CreatureTemplate = CreatureTemplate(
    name="Assassin",
    tag_line="Contract Killers",
    description="Assassins are professional killers skilled at stealthily approaching their victims and striking unseen. Most assassins kill for a reason, perhaps hiring themselves out to wealthy patrons or slaying for an unscrupulous cause. They use poisons and other deadly tools, and they might carry equipment to help them break into secure areas or avoid capture.",
    environments=["Urban"],
    treasure=["Any"],
    variants=[AssassinVariant],
    species=AllSpecies,
    callback=generate_assassin,
)
