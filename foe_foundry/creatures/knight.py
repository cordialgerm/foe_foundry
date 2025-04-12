from ..ac_templates import PlateArmor
from ..attack_template import weapon
from ..creature_types import CreatureType
from ..damage import Condition, DamageType
from ..powers import (
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    PowerType,
    select_powers,
)
from ..powers.roles import defender, leader
from ..powers.spellcaster import celestial, oath
from ..powers.themed import gadget, holy, honorable, organized, technique
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..spells import CasterType
from .base_stats import BaseStatblock, base_stats
from .species import AllSpecies, HumanSpecies
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

KnightVariant = CreatureVariant(
    name="Knight",
    description="Knights are heavily armored warriors who lead troops in combat and dominate the field of battle.",
    suggested_crs=[
        SuggestedCr(name="Knight", cr=3, srd_creatures=["Knight"]),
        SuggestedCr(name="Knight of the Realm", cr=6),
        SuggestedCr(
            name="Questing Knight",
            cr=12,
            other_creatures={"Questing Knight": "mm25"},
        ),
        SuggestedCr(name="Paragon Knight", cr=16, is_legendary=True),
    ],
)


class _KnightWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, cr: float):
        self.stats = stats
        self.cr = cr

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        powers = [
            leader.CommandTheAttack,
            leader.StayInFormation,
            defender.Taunt,
            defender.ZoneOfControl,
            organized.InspiringCommander,
            technique.BaitAndSwitch,
            technique.ArmorMaster,
            technique.BleedingAttack,
            technique.CleavingAttack,
            technique.DazingAttacks,
            technique.DisarmingAttack,
            technique.GrazingAttack,
            technique.OverpoweringStrike,
            technique.Interception,
            technique.ParryAndRiposte,
            technique.PommelStrike,
            technique.WhirlwindOfSteel,
            holy.DivineSmite,
            holy.Heroism,
        ]

        suppress = celestial.CelestialCasters + gadget.GadgetPowers

        spellcaster_powers = []
        if self.cr >= 6:
            spellcaster_powers += oath.OathCasters

        if p in suppress:
            return CustomPowerWeight(-1)
        elif p in powers:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)
        elif p in honorable.HonorablePowers:
            # boost honorable powers substantially, but still follow existing requirements to avoid duplicates
            return CustomPowerWeight(2.5, ignore_usual_requirements=False)
        elif p in spellcaster_powers:
            return CustomPowerWeight(2.0, ignore_usual_requirements=False)
        elif p.power_type == PowerType.Species:
            # boost species powers but still respect requirements
            return CustomPowerWeight(2.0, ignore_usual_requirements=False)
        else:
            return CustomPowerWeight(0.5, ignore_usual_requirements=False)


def generate_knight(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    species = settings.species if settings.species else HumanSpecies
    rng = settings.rng
    is_legendary = settings.is_legendary

    # STATS
    stats = base_stats(
        name=name,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Default),
            Stats.INT.scaler(StatScaling.Default),
            Stats.WIS.scaler(StatScaling.Medium),
            Stats.CHA.scaler(StatScaling.Medium, mod=2),
        ],
        hp_multiplier=settings.hp_multiplier * (1.1 if cr >= 12 else 1.0),
        damage_multiplier=settings.damage_multiplier,
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    stats = stats.copy(
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Knight",
    )

    # ARMOR CLASS
    stats = stats.add_ac_template(PlateArmor)

    # ATTACKS
    if stats.cr >= 12:
        attack = weapon.Greatsword.with_display_name("Oathbound Blade")
    elif stats.cr >= 6:
        attack = weapon.Greatsword.with_display_name("Blessed Blade")
    else:
        attack = weapon.Greatsword

    secondary_damage_type = DamageType.Radiant

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=secondary_damage_type,
        uses_shield=False,
    )

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Soldier,
        additional_roles=[MonsterRole.Leader, MonsterRole.Support],
    )

    # SPELLCASTING
    if cr >= 6:
        stats = stats.grant_spellcasting(caster_type=CasterType.Divine)

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Athletics)
    if cr >= 5:
        stats = stats.grant_proficiency_or_expertise(
            Skills.Perception, Skills.Persuasion, Skills.Initiative
        )

    # SAVES
    stats = stats.grant_save_proficiency(Stats.CON)
    if cr >= 6:
        stats = stats.grant_save_proficiency(Stats.STR, Stats.WIS, Stats.CHA)

    # IMMUNITIES
    if cr >= 6:
        stats = stats.grant_resistance_or_immunity(
            conditions={Condition.Charmed, Condition.Frightened}
        )

    # POWERS
    features = []

    # SPECIES CUSTOMIZATIONS
    stats = species.alter_base_stats(stats)

    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_KnightWeights(stats, cr),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


KnightTemplate: CreatureTemplate = CreatureTemplate(
    name="Knight",
    tag_line="Battle Masters and Heroic Wanderers",
    description="Knights are skilled warriors trained for war and tested in battle. Many serve the rulers of a realm, a faith, or an order devoted to a cause.",
    environments=["Urban", "Rural"],
    treasure=["Relics", "Individual"],
    variants=[KnightVariant],
    species=AllSpecies,
    callback=generate_knight,
)
