import numpy as np

from foe_foundry.powers.power import Power
from foe_foundry.powers.selection.custom import CustomPowerWeight

from ..ac_templates import ChainShirt, HolyArmor, NaturalArmor, SplintArmor
from ..attack_template import spell, weapon
from ..creature_types import CreatureType
from ..powers import LOW_POWER, MEDIUM_POWER, CustomPowerSelection, select_powers
from ..powers.creature import kobold
from ..powers.creature_type import dragon
from ..powers.roles import ambusher, artillery, leader, skirmisher, soldier, support
from ..powers.spellcaster import oath
from ..powers.themed import cowardly, gadget, holy, technique, trap
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..spells import CasterType
from .base_stats import base_stats
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

KoboldWarrenguardVariant = CreatureVariant(
    name="Kobold Warrenguard",
    description="Warrenguards are proud nest defenders. They are known to work in disciplined formations, using their superior numbers to overwhelm their foes and protect their territory.",
    suggested_crs=[
        SuggestedCr(
            name="Kobold Warrenguard",
            cr=1 / 8,
            srd_creatures=["Kobold"],
            other_creatures={"Kobold Warrior": "mm25"},
        )
    ],
)

KoboldSharpsnoutVariant = CreatureVariant(
    name="Kobold Sharpsnout",
    description="Sharpsnouts have honed their devious instincts to a craft. Their cunning traps and devious ambushes have laid low many an unprepared intruder.",
    suggested_crs=[SuggestedCr(name="Kobold Sharpsnout", cr=1 / 2)],
)

KoboldAspirantVariant = CreatureVariant(
    name="Kobold Aspirant",
    description="Aspirants are fanatical zealots to their True Dragon overlords. They carry a sacred Draconic Standard imbued with the power of the collective will of their tribe.",
    suggested_crs=[SuggestedCr(name="Kobold Ascendant", cr=1)],
)

KoboldWyrmcallerVariant = CreatureVariant(
    name="Kobold Wyrmcaller",
    description="Wyrmcallers are wizened shamans who have learned to commune with the spirits of True Dragons. They are capable of guiding the souls of brave Kobold martyrs to reincarnate as a True Dragon",
    suggested_crs=[SuggestedCr(name="Kobold Wyrmcaller", cr=2)],
)


class _KoboldPowers(CustomPowerSelection):
    def __init__(
        self, cr: float, force: list[Power], powers: list[Power], suppress: list[Power]
    ):
        self.cr = cr
        self.force = force
        self.powers = powers
        self.suppress = suppress

    def custom_weight(self, power: Power) -> CustomPowerWeight:
        if power in self.suppress:
            return CustomPowerWeight(-1, ignore_usual_requirements=False)
        elif power in self.powers:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(0.5, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        return self.force

    def power_delta(self) -> float:
        delta = MEDIUM_POWER - 0.2 * sum(p.power_level for p in self.force_powers())
        if self.cr >= 1:
            delta += LOW_POWER
        return delta


def _kobold_powers(
    variant: CreatureVariant, rng: np.random.Generator, cr: float
) -> CustomPowerSelection:
    suppress = [] + dragon.DragonPowers + cowardly.CowardlyPowers
    suppress.remove(cowardly.ScurryAndScatter)

    if variant is KoboldWarrenguardVariant:
        return _KoboldPowers(
            cr=cr,
            force=[kobold.DraconicServants, soldier.Phalanx],
            powers=[
                soldier.PackTactics,
                technique.BaitAndSwitch,
                gadget.BasicNet,
                gadget.SmokeBomb,
                cowardly.ScurryAndScatter,
                soldier.CoordinatedStrike,
                soldier.Phalanx,
                kobold.FalseRetreat,
            ],
            suppress=suppress,
        )
    elif variant is KoboldSharpsnoutVariant:
        trap_index = rng.choice(len(trap.TrapPowers))
        trap_power = trap.TrapPowers[trap_index]

        return _KoboldPowers(
            cr=cr,
            force=[kobold.DraconicServants, trap_power],
            powers=[
                artillery.SuppresingFire,
                artillery.Overwatch,
                ambusher.DeadlyAmbusher,
                technique.Sharpshooter,
                skirmisher.HarassingRetreat,
                technique.VexingAttack,
                technique.SlowingAttack,
                technique.DazingAttacks,
                cowardly.ScurryAndScatter,
                kobold.FalseRetreat,
            ],
            suppress=suppress + trap.TrapPowers,
        )
    elif variant is KoboldAspirantVariant:
        return _KoboldPowers(
            cr=cr,
            force=[kobold.DraconicServants, kobold.DraconicStandard, soldier.Phalanx],
            powers=[
                soldier.PackTactics,
                technique.GrazingAttack,
                technique.PolearmMaster,
                technique.CleavingAttack,
                gadget.FireGrenade,
                gadget.InfusedNet,
                leader.CommandTheAttack,
                technique.OverpoweringStrike,
                technique.WhirlwindOfSteel,
                soldier.CoordinatedStrike,
            ],
            suppress=suppress + gadget.GadgetPowers + [cowardly.ScurryAndScatter],
        )
    elif variant is KoboldWyrmcallerVariant:
        return _KoboldPowers(
            cr=cr,
            force=[
                kobold.DraconicServants,
                kobold.DraconicAscension,
                oath.OathAdept,
            ],
            powers=[
                holy.Heroism,
                holy.WordOfRadiance,
                support.Encouragement,
                support.Guidance,
                technique.BlindingAttack,
                technique.BurningAttack,
            ],
            suppress=suppress + [cowardly.ScurryAndScatter],
        )
    else:
        raise ValueError(f"Unknown kobold variant: {variant}")


def generate_kobold(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    rng = settings.rng

    # STATS
    if variant is KoboldWarrenguardVariant or variant is KoboldAspirantVariant:
        hp_multiplier = 0.8
        damage_multiplier = 1.1
        attrs = [
            Stats.STR.scaler(StatScaling.Primary, mod=1),
            Stats.DEX.scaler(StatScaling.Medium),
            Stats.CON.scaler(StatScaling.Constitution, mod=-2),
            Stats.INT.scaler(StatScaling.Default, mod=-2),
            Stats.WIS.scaler(StatScaling.Default, mod=-3),
            Stats.CHA.scaler(StatScaling.Default, mod=-2),
        ]
    elif variant is KoboldSharpsnoutVariant:
        hp_multiplier = 0.8
        damage_multiplier = 1.1
        attrs = [
            Stats.STR.scaler(StatScaling.Default),
            Stats.DEX.scaler(StatScaling.Primary),
            Stats.CON.scaler(StatScaling.Constitution, mod=-2),
            Stats.INT.scaler(StatScaling.Default, mod=-3),
            Stats.WIS.scaler(StatScaling.Default, mod=1),
            Stats.CHA.scaler(StatScaling.Default, mod=-2),
        ]
    elif variant is KoboldWyrmcallerVariant:
        hp_multiplier = 0.9
        damage_multiplier = 1.0
        attrs = [
            Stats.STR.scaler(StatScaling.Default, mod=-2),
            Stats.DEX.scaler(StatScaling.Medium),
            Stats.CON.scaler(StatScaling.Constitution, mod=-2),
            Stats.INT.scaler(StatScaling.Medium, mod=0.5),
            Stats.WIS.scaler(StatScaling.Primary, mod=1),
            Stats.CHA.scaler(StatScaling.Medium),
        ]
    else:
        raise ValueError(f"Unknown kobold variant: {variant}")

    stats = base_stats(
        name=variant.name,
        variant_key=settings.variant.key,
        template_key=settings.creature_template,
        cr=cr,
        stats=attrs,
        hp_multiplier=hp_multiplier * settings.hp_multiplier,
        damage_multiplier=damage_multiplier * settings.damage_multiplier,
    )

    stats = stats.copy(
        name=name,
        size=Size.Small,
        languages=["Common", "Draconic"],
        creature_class="Kobold",
    ).with_types(
        primary_type=CreatureType.Humanoid, additional_types=CreatureType.Dragon
    )

    # SENSES
    stats = stats.copy(senses=stats.senses.copy(darkvision=60))

    # ARMOR CLASS
    if variant is KoboldWarrenguardVariant:
        stats = stats.add_ac_template(ChainShirt)
    elif variant is KoboldSharpsnoutVariant:
        stats = stats.add_ac_template(NaturalArmor)
    elif variant is KoboldAspirantVariant:
        stats = stats.add_ac_template(SplintArmor)
    elif variant is KoboldWyrmcallerVariant:
        stats = stats.add_ac_template(HolyArmor)

    # ATTACKS
    if variant is KoboldWarrenguardVariant:
        attack = weapon.SpearAndShield.with_display_name("Spear Formation")
    elif variant is KoboldSharpsnoutVariant:
        attack = weapon.Shortbow.with_display_name("Crafty Shots")
    elif variant is KoboldAspirantVariant:
        attack = weapon.Polearm.with_display_name("Dragonfang Halberd")
    elif variant is KoboldWyrmcallerVariant:
        attack = spell.HolyBolt.with_display_name("Draconic Invocation")

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)

    # SPELLS
    if variant is KoboldWyrmcallerVariant:
        stats = stats.grant_spellcasting(
            caster_type=CasterType.Divine, spellcasting_stat=Stats.WIS
        )

    # ROLES
    if variant is KoboldWarrenguardVariant:
        primary_role = MonsterRole.Soldier
        secondary_roles = None
    elif variant is KoboldSharpsnoutVariant:
        primary_role = MonsterRole.Ambusher
        secondary_roles = {MonsterRole.Skirmisher, MonsterRole.Artillery}
    elif variant is KoboldAspirantVariant:
        primary_role = MonsterRole.Soldier
        secondary_roles = {MonsterRole.Leader}
    elif variant is KoboldWyrmcallerVariant:
        primary_role = MonsterRole.Support
        secondary_roles = None

    stats = stats.with_roles(
        primary_role=primary_role, additional_roles=secondary_roles
    )

    # SKILLS
    if variant is KoboldSharpsnoutVariant:
        stats = stats.grant_proficiency_or_expertise(
            Skills.Stealth, Skills.Perception
        ).grant_proficiency_or_expertise(Skills.Stealth)  # expertise

    # SAVES
    if cr >= 2:
        stats = stats.grant_save_proficiency(Stats.CON, Stats.WIS)

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_kobold_powers(variant, rng, cr),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


KoboldTemplate: CreatureTemplate = CreatureTemplate(
    name="Kobold",
    tag_line="Proud Zealots of True Dragons",
    description="Kobolds are small reptilian guardians of True Dragon lairs. They are known for their zealous dedication to their True Dragon overlords and their cunning defense of the lairs they protect.",
    environments=["Forest", "Grassland", "Hill", "Feywild", "Underdark"],
    treasure=["Any"],
    variants=[
        KoboldWarrenguardVariant,
        KoboldSharpsnoutVariant,
        KoboldAspirantVariant,
        KoboldWyrmcallerVariant,
    ],
    species=[],
    callback=generate_kobold,
    is_sentient_species=True,
)
