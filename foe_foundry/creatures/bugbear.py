import numpy as np

from foe_foundry.powers.power import Power
from foe_foundry.powers.selection.custom import CustomPowerWeight

from ..ac_templates import HideArmor
from ..attack_template import natural
from ..creature_types import CreatureType
from ..powers import LOW_POWER, CustomPowerSelection, select_powers
from ..powers.creature import bugbear
from ..powers.roles import ambusher, bruiser, skirmisher
from ..powers.themed import deathly, gadget, reckless, sneaky, technique
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..statblocks import BaseStatblock
from ._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from .base_stats import base_stats

BugbearVariant = MonsterVariant(
    name="Bugbear",
    description="Bugbears are large, hairy humanoids with a reputation for stealth and ambush tactics. They are often found in dark forests or caves, where they can use their natural camouflage to surprise their prey.",
    monsters=[
        Monster(
            name="Bugbear",
            cr=1,
            srd_creatures=["Bugbear"],
        ),
        Monster(
            name="Bugbear Brute",
            cr=3,
            other_creatures={"Bugbear Stalker": "mm25"},
        ),
        Monster(
            name="Bugbear Shadowstalker",
            cr=5,
        ),
    ],
)


class _BugbearPowers(CustomPowerSelection):
    def __init__(
        self,
        variant: MonsterVariant,
        stats: BaseStatblock,
        cr: float,
        rng: np.random.Generator,
    ):
        self.variant = variant
        self.stats = stats
        self.cr = cr
        self.rng = rng

        strangle_powers = [
            reckless.Strangle,
            bugbear.Strangle,
            bugbear.SurpriseSnatch,
            technique.ExpertBrawler,
        ]
        strangle_power_index = self.rng.choice(len(strangle_powers))
        self.strangle_powers = strangle_powers
        self.strangle_power = strangle_powers[strangle_power_index]

    def custom_weight(self, power: Power) -> CustomPowerWeight:
        suppress = self.strangle_powers

        powers = [
            sneaky.CheapShot,
            sneaky.ExploitAdvantage,
            sneaky.SneakyStrike,
            sneaky.Vanish,
            technique.GrapplingAttack,
            bruiser.CleavingBlows,
            ambusher.DeadlyAmbusher,
            ambusher.StealthySneak,
            skirmisher.HarassingRetreat,
            bugbear.SnatchAndGrab,
        ]

        additional_powers = gadget.NetPowers + [gadget.SmokeBomb]

        if power in suppress:
            return CustomPowerWeight(-1, ignore_usual_requirements=True)
        elif power in powers:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)
        elif power in additional_powers:
            return CustomPowerWeight(1.5, ignore_usual_requirements=False)
        else:
            return CustomPowerWeight(0.25, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        force = [bugbear.FreakishlySkinny, self.strangle_power]
        if self.cr >= 5:
            force.append(deathly.ShadowWalk)
        return force

    def power_delta(self) -> float:
        return LOW_POWER - 0.25 * sum(p.power_level for p in self.force_powers())


def generate_bugbear(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    rng = settings.rng

    # STATS
    attrs = [
        Stats.STR.scaler(StatScaling.Primary, mod=0.5),
        Stats.DEX.scaler(StatScaling.Medium, mod=3),
        Stats.INT.scaler(StatScaling.Medium, mod=-4),
        Stats.WIS.scaler(StatScaling.Default, mod=2),
        Stats.CHA.scaler(StatScaling.Medium, mod=-3),
    ]

    stats = base_stats(
        name=variant.name,
        variant_key=settings.variant.key,
        template_key=settings.monster_template,
        monster_key=settings.monster_key,
        cr=cr,
        stats=attrs,
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        name=name,
        size=Size.Medium,
        languages=["Common", "Goblin"],
        creature_class="Bugbear",
        creature_subtype="Goblinoid",
    ).with_types(primary_type=CreatureType.Humanoid, additional_types=CreatureType.Fey)

    # SENSES
    stats = stats.copy(senses=stats.senses.copy(darkvision=60))

    # ARMOR CLASS
    stats = stats.add_ac_template(HideArmor)

    # ATTACKS
    attack = natural.Slam.with_display_name("Skull Smash").copy(reach=10)

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Ambusher, additional_roles=MonsterRole.Bruiser
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(
        Skills.Stealth
    ).grant_proficiency_or_expertise(Skills.Stealth)

    # SAVES
    if cr >= 3:
        stats = stats.grant_save_proficiency(Stats.CON, Stats.WIS)

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_BugbearPowers(variant, stats, cr, rng),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


BugbearTemplate: MonsterTemplate = MonsterTemplate(
    name="Bugbear",
    tag_line="Lurking abductors and ambushers",
    description="Bugbears are large, hairy humanoids with a reputation for stealth and ambush tactics. They are often found in dark forests or caves, where they can use their natural camouflage to surprise their prey.",
    environments=["Forest", "Grassland", "Hill", "Feywild", "Underdark"],
    treasure=["Any"],
    variants=[BugbearVariant],
    species=[],
    callback=generate_bugbear,
    is_sentient_species=True,
)
