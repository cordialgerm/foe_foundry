from ..ac_templates import ArcaneArmor
from ..attack_template import spell
from ..creature_types import CreatureType
from ..powers import (
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    select_powers,
)
from ..powers.creature.mage import (
    AdeptMage,
    ApprenticeMage,
    Archmage,
    Mage,
    ProtectiveMagic,
)
from ..powers.roles import artillery
from ..powers.spellcaster import (
    WizardPower,
    abjurer,
    conjurer,
    divination,
    elementalist,
    enchanter,
    illusionist,
    magic,
    metamagic,
    necromancer,
    transmuter,
)
from ..powers.themed import anti_magic, anti_ranged, teleportation, temporal, tough
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..spells import CasterType
from .base_stats import BaseStatblock, base_stats
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

MageVariant = CreatureVariant(
    name="Mage",
    description="Mages are accomplished spellcasters whose lives have been shaped by magic. They can use their powers to defend or dominate other creatures, or they could focus on magical research and unlocking mystical secrets.",
    suggested_crs=[
        SuggestedCr(
            name="Mage Apprentice",
            cr=2,
            other_creatures={"Mage Apprentice": "mm25"},
        ),
        SuggestedCr(name="Mage Adept", cr=4),
        SuggestedCr(name="Mage", cr=6, srd_creatures=["Mage"]),
        SuggestedCr(
            name="Archmage",
            cr=12,
            srd_creatures=["Archmage"],
        ),
        SuggestedCr(name="Archmage Paragon", cr=16, is_legendary=True),
    ],
)


def power_matches_cr(p: Power, cr: float) -> bool:
    score_args: dict = p.score_args  # type: ignore
    min_cr = score_args.get("require_cr", 0)
    max_cr = score_args.get("require_max_cr", 100)
    return min_cr <= cr <= max_cr


def get_name(powers: list[Power], existing_name: str) -> str:
    wizard_power = next((p for p in powers if isinstance(p, WizardPower)), None)
    if wizard_power is None:
        return existing_name

    return f"{wizard_power.creature_name} {existing_name}"


class _CustomWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, variant: CreatureVariant):
        self.stats = stats
        self.variant = variant

        self.wizards = (
            abjurer.AbjurationWizards()
            + divination.DivinationWizards()
            + conjurer.ConjurationWizards()
            + elementalist.ElementalistWizards()
            + enchanter.EnchanterWizards()
            + illusionist.IllusionistWizards()
            + transmuter.TransmutationWizards()
            + necromancer.NecromancerWizards()
        )

        self.general_mage_powers = (
            magic.MagicPowers + metamagic.MetamagicPowers + [artillery.TwinSpell]
        )

        self.esoteric_mage_powers = [
            anti_magic.RedirectTeleport,
            anti_magic.SpellStealer,
            anti_ranged.Overchannel,
            teleportation.Scatter,
            teleportation.BendSpace,
            temporal.TemporalPowers,
        ]

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        wizards = [p2 for p2 in self.wizards if power_matches_cr(p2, self.stats.cr)]

        if p in self.force_powers():
            return CustomPowerWeight(0, ignore_usual_requirements=False)
        elif p in wizards:
            return CustomPowerWeight(4, ignore_usual_requirements=False)
        elif p in self.general_mage_powers:
            return CustomPowerWeight(2, ignore_usual_requirements=False)
        elif p in self.esoteric_mage_powers:
            return CustomPowerWeight(1.5, ignore_usual_requirements=False)
        else:
            return CustomPowerWeight(0.5, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        if self.stats.cr >= 12:
            return [
                tough.MagicResistance,
                teleportation.MistyStep,
                ProtectiveMagic,
                Archmage,
            ]
        elif self.stats.cr >= 6:
            return [teleportation.MistyStep, ProtectiveMagic, Mage]
        elif self.stats.cr >= 4:
            return [ProtectiveMagic, AdeptMage]
        else:
            return [ApprenticeMage]


def generate_mage(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    rng = settings.rng
    is_legendary = settings.is_legendary

    # STATS
    stats = base_stats(
        name=name,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Default, mod=-2),
            Stats.DEX.scaler(StatScaling.Default, mod=2),
            Stats.INT.scaler(StatScaling.Primary),
            Stats.WIS.scaler(StatScaling.Medium),
            Stats.CHA.scaler(StatScaling.Default),
        ],
        hp_multiplier=0.9 * settings.hp_multiplier,
        damage_multiplier=1.2 * settings.damage_multiplier,
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    stats = stats.copy(
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Wizard",
        caster_type=CasterType.Arcane,
        # mages have many bonus actions, reactions, and limited use abilities
        selection_target_args=dict(
            limited_uses_target=-1,
            limited_uses_max=-1,
            reaction_target=-1,
            reaction_max=-1,
            spellcasting_powers_target=-1,
            spellcasting_powers_max=-1,
        ),
    )

    # ARMOR CLASS
    stats = stats.add_ac_template(ArcaneArmor)

    # ATTACKS
    attack = spell.ArcaneBurst
    stats = attack.alter_base_stats(stats, rng)
    stats = attack.initialize_attack(stats)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Controller, additional_roles=MonsterRole.Artillery
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Arcana, Skills.Perception)
    if cr >= 6:
        stats = stats.grant_proficiency_or_expertise(Skills.History)
    if cr >= 12:
        stats = stats.grant_proficiency_or_expertise(Skills.Arcana, Skills.Initiative)

    # SAVES
    if cr >= 6:
        stats = stats.grant_save_proficiency(Stats.WIS, Stats.INT)

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_CustomWeights(stats, variant),
    )
    features += power_features

    new_name = get_name(list(power_selection.selection.selected_powers), name)
    stats = stats.copy(name=new_name)

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


MageTemplate: CreatureTemplate = CreatureTemplate(
    name="Mage",
    tag_line="Magical Scholars and Spellcasters",
    description="Mages are magical wonder-workers, ranging from spellcasting overlords to reclusive witches. They study mystical secrets and possess insight into monsters, legends, omens, and other lore. Mages often gather allies or hire assistants to aid them in their research or to attain magical might.",
    environments=[],
    treasure=["Arcana", "Individual"],
    variants=[MageVariant],
    species=[],
    callback=generate_mage,
)
