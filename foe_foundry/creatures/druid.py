from foe_foundry.utils import choose_enum

from ..ac_templates import StuddedLeatherArmor
from ..attack_template import weapon
from ..creature_types import CreatureType
from ..damage import DamageType
from ..powers import (
    LOW_POWER,
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    PowerType,
    flags,
    select_powers,
)
from ..powers.creature import druid
from ..powers.roles import support
from ..powers.spellcaster import druidic, metamagic
from ..powers.themed import (
    gadget,
    icy,
    poison,
    shamanic,
    storm,
    technique,
    totemic,
)
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

DruidVariant = CreatureVariant(
    name="Druid",
    description="Druids use primal magic to protect the natural world and its inhabitants. They are often found in the wilds, where they can commune with nature and draw upon its power.",
    suggested_crs=[
        SuggestedCr(name="Druid", cr=2, srd_creatures=["Druid"]),
        SuggestedCr(name="Druid Greenwarden", cr=6),
        SuggestedCr(
            name="Archdruid of Old Way", cr=12, other_creatures={"Archdruid": "mmotm"}
        ),
        SuggestedCr(name="Archdruid of the First Grove", cr=16, is_legendary=True),
    ],
)


class _DruidWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, variant: CreatureVariant):
        self.stats = stats
        self.variant = variant

    def force_powers(self) -> list[Power]:
        if self.stats.cr >= 12:
            return [druidic.DruidicExpertPower]
        elif self.stats.cr >= 6:
            return [druidic.DruidicMasterPower]
        else:
            return [druidic.DruidicAdeptPower]

    def power_delta(self) -> float:
        offset = -0.25 * sum(p.power_level for p in self.force_powers())
        return offset + LOW_POWER

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        powers = (
            druid.DruidPowers
            + totemic.TotemicPowers
            + shamanic.ShamanicPowers
            + [
                metamagic.PrimalMastery,
                support.Guidance,
            ]
        )

        elemental_powers = icy.IcyPowers + storm.StormPowers + poison.PoisonPowers

        suppress = gadget.GadgetPowers + technique.TechniquePowers

        if p in suppress:
            return CustomPowerWeight(-1, ignore_usual_requirements=True)
        elif p in powers:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)
        elif p in elemental_powers:
            # let the choice of secondary damage type influence the power selection
            return CustomPowerWeight(2.0, ignore_usual_requirements=False)
        elif p.power_type == PowerType.Species:
            # boost species powers but still respect requirements
            return CustomPowerWeight(2.0, ignore_usual_requirements=False)
        else:
            return CustomPowerWeight(0.25, ignore_usual_requirements=False)


def generate_druid(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    species = settings.species if settings.species else HumanSpecies
    rng = settings.rng
    is_legendary = settings.is_legendary

    # STATS
    stats = base_stats(
        name=name,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Default),
            Stats.DEX.scaler(StatScaling.Medium),
            Stats.INT.scaler(StatScaling.Default, mod=2),
            Stats.WIS.scaler(StatScaling.Primary),
            Stats.CHA.scaler(StatScaling.Default, mod=1),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common", "Druidic", "Sylvan"],
        creature_class="Druid",
        caster_type=CasterType.Primal,
        uses_shield=False,
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    # ARMOR CLASS
    stats = stats.add_ac_template(StuddedLeatherArmor)

    # ATTACKS
    attack = weapon.Staff.with_display_name("Staff of the Wild")

    secondary_damage_type = choose_enum(
        rng, [DamageType.Poison, DamageType.Fire, DamageType.Cold, DamageType.Lightning]
    )

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(secondary_damage_type=secondary_damage_type)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Support,
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(
        Skills.Medicine, Skills.Nature, Skills.Perception
    )

    # SAVES
    if cr >= 8:
        stats = stats.grant_save_proficiency(Stats.WIS, Stats.CON)

    # FLAGS
    # Druids already have healing
    stats = stats.with_flags(flags.HAS_HEALING)

    # POWERS
    features = []

    # SPECIES CUSTOMIZATIONS
    stats = species.alter_base_stats(stats)

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_DruidWeights(stats, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


DruidTemplate: CreatureTemplate = CreatureTemplate(
    name="Druid",
    tag_line="Stewards and Sages of Nature",
    description="Druids use primal magic to protect the natural world and its inhabitants. They are often found in the wilds, where they can commune with nature and draw upon its power.",
    environments=[],
    treasure=["Relics", "Individual"],
    variants=[DruidVariant],
    species=AllSpecies,
    callback=generate_druid,
)
