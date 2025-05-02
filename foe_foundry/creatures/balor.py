from ..ac_templates import UnholyArmor
from ..attack_template import weapon
from ..creature_types import CreatureType
from ..damage import Condition, DamageType
from ..movement import Movement
from ..powers import CustomPowerSelection, CustomPowerWeight, Power, select_powers
from ..powers.creature import balor
from ..powers.creature_type import demon, fiend
from ..powers.roles import bruiser, leader
from ..powers.themed import (
    anti_magic,
    breath,
    chaotic,
    cruel,
    cursed,
    deathly,
    domineering,
    fearsome,
    flying,
    reckless,
    technique,
    tough,
)
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from .base_stats import BaseStatblock, base_stats
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

BalorVariant = CreatureVariant(
    name="Balor",
    description="Balors embody demons' ruinous fury and hatred. Towering, winged terrors, these demonic warlords seethe with wrath, their rage erupting in waves of fire and as a pair of vicious weapons: a sword of crackling lightning and a whip of lashing flames.",
    suggested_crs=[
        SuggestedCr(name="Balor", cr=19, srd_creatures=["Balor"]),
        SuggestedCr(name="Balor Dreadlord", cr=23, is_legendary=True),
    ],
)


class _BalorWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, variant: CreatureVariant):
        self.stats = stats
        self.variant = variant

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        if p in self.force_powers():
            return CustomPowerWeight(
                0, ignore_usual_requirements=True
            )  # already forced

        powers = set(fiend.FiendishPowers) | set(demon.DemonPowers)
        powers.discard(fiend.FiendishTeleportation)  # forced
        powers.discard(fiend.FieryTeleportation)  # already have teleportation
        powers.discard(demon.DemonicBite)  # already have multiple different attacks

        powers.add(leader.Intimidate)
        powers.add(bruiser.CleavingBlows)
        powers.add(bruiser.StunningBlow)
        powers.add(anti_magic.SpellEater)
        powers.add(anti_magic.SpellStealer)
        powers.add(anti_magic.TwistedMind)
        powers.add(anti_magic.RuneDrinker)
        powers.add(breath.InfernoBreath)
        powers.add(breath.LightningBreath)
        powers.add(chaotic.EldritchBeacon)
        powers.update(cruel.CruelPowers)
        powers.add(cursed.RejectDivinity)
        powers.add(cursed.VoidSiphon)
        powers.add(deathly.DevourSoul)
        powers.add(domineering.CommandingPresence)
        powers.add(fearsome.FearsomeRoar)
        powers.add(flying.WingedCharge)
        powers.add(leader.FanaticFollowers)
        powers.add(tough.LimitedMagicImmunity)
        powers.add(reckless.WildCleave)
        powers.add(technique.DazingAttacks)
        powers.add(technique.BurningAttack)
        powers.add(technique.ProneAttack)
        powers.add(technique.GrapplingAttack)
        powers.add(technique.FrighteningAttack)
        powers.add(technique.ShockingAttack)
        powers.add(technique.OverpoweringStrike)

        if p in powers:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(0.5, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        return [fiend.FiendishTeleportation, tough.MagicResistance, balor.FlameWhip]


def generate_balor(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    rng = settings.rng
    is_legendary = settings.is_legendary

    # STATS
    stats = base_stats(
        name=name,
        variant_key=settings.variant.key,
        template_key=settings.creature_template,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Medium, mod=1),
            Stats.INT.scaler(StatScaling.Medium, mod=4),
            Stats.WIS.scaler(StatScaling.Medium, mod=2),
            Stats.CHA.scaler(StatScaling.Medium, mod=6),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Fiend,
        languages=["Abyssal; telepathy 120 ft."],
        creature_class="Balor",
        creature_subtype="Demon",
        senses=stats.senses.copy(truesight=120),
        size=Size.Huge,
        speed=Movement(walk=40, fly=80),
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    # ARMOR CLASS
    stats = stats.add_ac_template(UnholyArmor)

    # ATTACKS
    attack = weapon.Greatsword.with_display_name("Lightning Blade").copy(
        damage_type=DamageType.Lightning, split_secondary_damage=False
    )
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        secondary_damage_type=DamageType.Fire,
    )

    ## ATTACK DAMAGE
    # zombies should have fewer attacks, but the attacks should hit hard!

    # lowering attacks on a legendary creature messes up formulas
    stats = stats.with_set_attacks(3)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Bruiser,
        additional_roles=[MonsterRole.Soldier, MonsterRole.Leader],
    )

    # SAVES
    stats = stats.grant_save_proficiency(Stats.CON, Stats.WIS)

    # IMMUNITIES
    stats = stats.grant_resistance_or_immunity(
        immunities={DamageType.Fire, DamageType.Poison},
        resistances={DamageType.Cold, DamageType.Lightning},
        conditions={Condition.Poisoned, Condition.Frightened, Condition.Poisoned},
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Perception, Skills.Initiative)
    stats = stats.grant_proficiency_or_expertise(Skills.Initiative)  # expertise

    # POWERS
    features = []

    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_BalorWeights(stats, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


BalorTemplate: CreatureTemplate = CreatureTemplate(
    name="Balor",
    tag_line="Demon of Overwhelming Rage",
    description="Balors embody demons' ruinous fury and hatred. Towering, winged terrors, these demonic warlords seethe with wrath, their rage erupting in waves of fire and as a pair of vicious weapons: a sword of crackling lightning and a whip of lashing flames. Demon lords and evil gods harness balors' rage by making balors commanders of armies or guardians of grave secrets.",
    environments=["Planar (Abyss)"],
    treasure=[],
    variants=[BalorVariant],
    species=[],
    callback=generate_balor,
)
