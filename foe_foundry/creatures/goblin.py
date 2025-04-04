from foe_foundry.powers.power import Power
from foe_foundry.powers.selection.custom import CustomPowerWeight

from ..ac_templates import Breastplate, ChainShirt, StuddedLeatherArmor
from ..attack_template import spell, weapon
from ..creature_types import CreatureType
from ..powers import LOW_POWER, CustomPowerSelection, select_powers
from ..powers.creature import goblin
from ..powers.roles import ambusher, artillery, leader, skirmisher
from ..powers.spellcaster import shaman
from ..powers.themed import (
    cowardly,
    cursed,
    organized,
    poison,
    reckless,
    shamanic,
    sneaky,
    technique,
    thuggish,
    totemic,
    trap,
    tricky,
)
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..spells import CasterType
from ..statblocks import BaseStatblock, MonsterDials
from .base_stats import base_stats
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

GoblinLickspittleVariant = CreatureVariant(
    name="Goblin Lickspittle",
    description="Goblin Lickspittles are the weakest of their kind, often serving as minions to more powerful goblins or as scouts and foragers",
    suggested_crs=[
        SuggestedCr(
            name="Goblin Lickspittle",
            cr=1 / 8,
            other_creatures={"Goblin Minion": "mm25"},
        )
    ],
)
GoblinWarriorVariant = CreatureVariant(
    name="Goblin",
    description="Goblin warriors attack with overwhelming numbers and withdraw before their enemies can retaliate. They're also fond of setting ambushes.",
    suggested_crs=[
        SuggestedCr(
            name="Goblin",
            cr=1 / 4,
            srd_creatures=["Goblin"],
            other_creatures={"Goblin Warrior": "mm25"},
        ),
    ],
)
GoblinBruteVariant = CreatureVariant(
    name="Goblin Brute",
    description="Goblin Brutes are larger and stronger than their kin, and they wield heavy weapons to crush their foes.",
    suggested_crs=[
        SuggestedCr(
            name="Goblin Brute",
            cr=1 / 2,
            other_creatures={"Goblin Spinecleaver": "FleeMortals"},
        )
    ],
)
GoblinBossVariant = CreatureVariant(
    name="Goblin Boss",
    description="Goblin Bosses are larger and stronger than their kin, and they have a knack for inspiring their fellows to fight harder.",
    suggested_crs=[
        SuggestedCr(
            name="Goblin Boss",
            cr=1,
            srd_creatures=["Goblin Boss"],
            other_creatures={"Goblin Underboss": "FleeMortals"},
        ),
        SuggestedCr(name="Goblin Warchief", cr=4),
    ],
)
GoblinShamanVariant = CreatureVariant(
    name="Goblin Shaman",
    description="Goblin Shamans are spellcasters who wield the power of the mischievous gods and spirits that goblins often worship.",
    suggested_crs=[
        SuggestedCr(
            name="Goblin Foulhex",
            cr=1,
            other_creatures={
                "Nilbog": "motm",
                "Goblin Curspitter": "FleeMortals",
                "Goblin Warlock": "MonstrousMenagerie",
            },
        ),
        SuggestedCr(
            name="Goblin Shaman", cr=2, other_creatures={"Goblin Hexer": "mm25"}
        ),
    ],
)


class _GoblinPowers(CustomPowerSelection):
    def __init__(self, variant: CreatureVariant, stats: BaseStatblock, cr: float):
        self.variant = variant
        self.stats = stats
        self.cr = cr

        self.lickspittels = [skirmisher.HarassingRetreat] + cowardly.CowardlyPowers
        self.warriors = [
            sneaky.CheapShot,
            technique.VexingAttack,
            sneaky.ExploitAdvantage,
            ambusher.StealthySneak,
            skirmisher.HarassingRetreat,
        ] + trap.TrapPowers
        self.brutes = [
            reckless.BloodiedRage,
            reckless.Charger,
            reckless.RecklessFlurry,
            technique.CleavingAttack,
            technique.PushingAttack,
            technique.ProneAttack,
        ]
        self.shamans = (
            [
                tricky.ReverseFortune,
                tricky.SpectralDuplicate,
                cursed.BestowCurse,
                cursed.DisfiguringCurse,
            ]
            + totemic.TotemicPowers
            + shamanic.ShamanicPowers
        )
        self.leaders = [
            leader.CommandTheAttack,
            organized.FanaticFollowers,
            leader.StayInFormation,
        ] + thuggish.ThuggishPowers

        if variant is GoblinBossVariant:
            self.force = [thuggish.KickTheLickspittle, skirmisher.NimbleEscape]
        elif variant is GoblinShamanVariant:
            if cr <= 1:
                self.force = [shaman.ShamanAdeptPower]
            else:
                self.force = [shaman.ShamanPower]
        else:
            self.force = [skirmisher.NimbleEscape]

        self.suppress = [artillery.IndirectFire] + poison.PoisonPowers

    def custom_weight(self, power: Power) -> CustomPowerWeight:
        if power in self.suppress:
            return CustomPowerWeight(-1, ignore_usual_requirements=True)
        elif power in goblin.GoblinPowers:
            return CustomPowerWeight(
                2.0, ignore_usual_requirements=False
            )  # check requirements
        elif self.variant is GoblinLickspittleVariant and power in self.lickspittels:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)
        elif self.variant is GoblinWarriorVariant and power in self.warriors:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)
        elif self.variant is GoblinBruteVariant and power in self.brutes:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)
        elif self.variant is GoblinShamanVariant and power in self.shamans:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)
        elif self.variant is GoblinBossVariant and power in self.leaders:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)

        return CustomPowerWeight(0.1, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        return self.force


def generate_goblin(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    rng = settings.rng

    # STATS
    if variant is GoblinLickspittleVariant or variant is GoblinWarriorVariant:
        hp_multiplier = 0.7 if cr < 0.5 else 0.8
        damage_multiplier = 1.0 if cr < 0.5 else 1.1
        attrs = [
            Stats.STR.scaler(StatScaling.Default, mod=-3),
            Stats.DEX.scaler(StatScaling.Primary, mod=2 if cr <= 1 else 0),
            Stats.INT.scaler(StatScaling.Default, mod=-1),
            Stats.WIS.scaler(StatScaling.Default, mod=-2),
            Stats.CHA.scaler(StatScaling.Default, mod=-2),
        ]
    elif variant is GoblinBruteVariant:
        hp_multiplier = 1.0
        damage_multiplier = 1.0
        attrs = [
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Medium, mod=2),
            Stats.INT.scaler(StatScaling.Default, mod=-1),
            Stats.WIS.scaler(StatScaling.Default, mod=-2),
            Stats.CHA.scaler(StatScaling.Default, mod=-2),
        ]
    elif variant is GoblinShamanVariant:
        hp_multiplier = 0.8
        damage_multiplier = 1.1
        attrs = [
            Stats.STR.scaler(StatScaling.Default),
            Stats.DEX.scaler(StatScaling.Medium, mod=2),
            Stats.INT.scaler(StatScaling.Primary),
            Stats.WIS.scaler(StatScaling.Default),
            Stats.CHA.scaler(StatScaling.Default),
        ]
    elif variant is GoblinBossVariant:
        hp_multiplier = 1.0
        damage_multiplier = 1.0
        attrs = [
            Stats.STR.scaler(StatScaling.Default),
            Stats.DEX.scaler(StatScaling.Primary),
            Stats.INT.scaler(StatScaling.Default),
            Stats.WIS.scaler(StatScaling.Default),
            Stats.CHA.scaler(StatScaling.Default),
        ]
    else:
        raise ValueError(f"Unknown goblin variant: {variant}")

    stats = base_stats(
        name=variant.name,
        cr=cr,
        stats=attrs,
        hp_multiplier=hp_multiplier * settings.hp_multiplier,
        damage_multiplier=damage_multiplier * settings.damage_multiplier,
    )

    stats = stats.copy(
        name=name,
        size=Size.Small,
        languages=["Common", "Goblin"],
        creature_class="Goblin",
        creature_subtype="Goblinoid",
    ).with_types(primary_type=CreatureType.Humanoid, additional_types=CreatureType.Fey)

    # SENSES
    stats = stats.copy(senses=stats.senses.copy(darkvision=60))

    # ARMOR CLASS
    if variant is GoblinBossVariant or variant is GoblinBruteVariant:
        if stats.cr >= 3:
            stats = stats.add_ac_template(Breastplate)
        else:
            stats = stats.add_ac_template(ChainShirt)
    elif variant is GoblinWarriorVariant or variant is GoblinLickspittleVariant:
        stats = stats.add_ac_template(StuddedLeatherArmor)

    # ATTACKS
    if variant is GoblinWarriorVariant or variant is GoblinLickspittleVariant:
        attack = weapon.Daggers.with_display_name("Stick'Em").copy(die_count=1)
        secondary_attack = weapon.Shortbow.with_display_name("Shoot'Em")
    elif variant is GoblinBruteVariant:
        attack = weapon.Maul.with_display_name("Smash'Em")
        secondary_attack = None
    elif variant is GoblinBossVariant:
        attack = weapon.Maul.with_display_name("Smash'Em")
        secondary_attack = weapon.Shortbow.with_display_name("Shoot'Em")
    elif variant is GoblinShamanVariant:
        attack = spell.Gaze.with_display_name("Hex'Em")
        secondary_attack = None
    else:
        raise ValueError(f"Unknown goblin variant: {variant}")

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    if secondary_attack is not None:
        stats = secondary_attack.copy(damage_scalar=0.9).add_as_secondary_attack(stats)

    # SPELLS
    if variant is GoblinShamanVariant:
        stats = stats.grant_spellcasting(
            caster_type=CasterType.Primal, spellcasting_stat=Stats.INT
        )

    # ROLES
    if variant is GoblinLickspittleVariant or variant is GoblinWarriorVariant:
        primary_role = MonsterRole.Skirmisher
        secondary_roles = {MonsterRole.Artillery, MonsterRole.Ambusher}
    elif variant is GoblinBruteVariant:
        primary_role = MonsterRole.Soldier
        secondary_roles = {MonsterRole.Skirmisher, MonsterRole.Bruiser}
    elif variant is GoblinBossVariant:
        primary_role = MonsterRole.Leader
        secondary_roles = {MonsterRole.Soldier}
    elif variant is GoblinShamanVariant:
        primary_role = MonsterRole.Controller
        secondary_roles = MonsterRole.Artillery

    stats = stats.with_roles(
        primary_role=primary_role, additional_roles=secondary_roles
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Stealth)

    # SAVES
    if cr >= 3:
        stats = stats.grant_save_proficiency(Stats.CON, Stats.WIS)

    # POWERS
    stats = stats.apply_monster_dials(
        dials=MonsterDials(recommended_powers_modifier=LOW_POWER)
    )

    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_GoblinPowers(variant, stats, cr),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)

    if secondary_attack is not None:
        stats = secondary_attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


GoblinTemplate: CreatureTemplate = CreatureTemplate(
    name="Goblin",
    tag_line="Wild tricksters and troublemakers",
    description="Goblins are small, black-hearted humanoids that lair in despoiled dungeons and other dismal settings. Individually weak, they gather in large numbers to torment other creatures.",
    environments=["Forest", "Grassland", "Hill", "Feywild", "Underdark"],
    treasure=["Any"],
    variants=[
        GoblinLickspittleVariant,
        GoblinWarriorVariant,
        GoblinBruteVariant,
        GoblinShamanVariant,
        GoblinBossVariant,
    ],
    species=[],
    callback=generate_goblin,
    is_sentient_species=True,
)
