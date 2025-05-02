import numpy as np

from ..ac_templates import ArcaneArmor
from ..attack_template import spell
from ..creature_types import CreatureType
from ..movement import Movement
from ..powers import (
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    flags,
    select_powers,
)
from ..powers.creature import lich, mage
from ..powers.creature_type import undead
from ..powers.roles import artillery
from ..powers.spellcaster import (
    metamagic,
)
from ..powers.themed import (
    anti_ranged,
    cursed,
    deathly,
    emanation,
    icy,
    technique,
)
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..spells import CasterType
from ..statblocks import BaseStatblock
from .base_stats import base_stats
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

LichVariant = CreatureVariant(
    name="Lich",
    description="Liches are mortal necromancers who defied death, binding their souls to the Mortal Realm through dark rituals and dreadful will. Rather than accept the inevitability of death, they craft soul anchors that lash their spirit in defiance of the natural order. The dark arts necessary to craft such a soul anchor are unique to each twisted soul that contemplates the heinous act, but in each case it involves unspeakably evil acts and cruel sacrifices. Countless aspiring liches have failed, but those who succeed attain unspeakable power.",
    suggested_crs=[
        SuggestedCr(name="Lich", cr=21, srd_creatures=["Lich"], is_legendary=True),
        SuggestedCr(
            name="Archlich",
            cr=26,
            other_creatures={"Vecna": "Vecna: Eve of Ruin"},
            is_legendary=True,
        ),
    ],
)


class _LichWeights(CustomPowerSelection):
    def __init__(
        self,
        stats: BaseStatblock,
        name: str,
        cr: float,
        variant: CreatureVariant,
        rng: np.random.Generator,
    ):
        self.stats = stats
        self.variant = variant
        self.rng = rng

        force = [mage.ProtectiveMagic, lich.LichSpellcasting]
        techniques = [
            technique.SappingAttack,
            technique.PushingAttack,
            technique.ProneAttack,
            technique.SlowingAttack,
            technique.DazingAttacks,
            technique.FrighteningAttack,
            technique.NoHealingAttack,
        ]

        # general purpose lich powers
        powers = [
            metamagic.ArcaneMastery,
            anti_ranged.Overchannel,
            artillery.TwinSpell,
            artillery.SuppresingFire,
            cursed.DisfiguringCurse,
            cursed.RejectDivinity,
            cursed.VoidSiphon,
            deathly.EndlessServitude,
            deathly.FleshPuppets,
            deathly.DrainingBlow,
            undead.SoulTether,
            undead.SoulChill,
            undead.StygianBurst,
            undead.AntithesisOfLife,
            icy.Hoarfrost,
            icy.IcyTomb,
            icy.Frostbite,
            icy.FrostNova,
        ]

        emanations = [
            emanation.TimeRift,
            emanation.RunicWards if cr <= 21 else lich.EverlastingImmortality,
            emanation.RagingFlame,
            emanation.BitingFrost,
            emanation.FetidMiasma,
            emanation.IllusoryReality,
            emanation.LashingWinds,
            icy.Blizzard,
        ]

        # Lich will always have 1 attack technique and 1 emanation
        emanation_index = self.rng.choice(len(emanations))
        technique_index = self.rng.choice(len(techniques))

        # Lich will always have 1 of these specific lich powers
        lich_powers = [lich.SoulHarvest, lich.UndyingServants]
        lich_power_index = self.rng.choice(len(lich_powers))

        force += [
            emanations[emanation_index],
            techniques[technique_index],
            lich_powers[lich_power_index],
        ]

        self.force = force
        self.powers = powers
        self.techniques = techniques

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        if p in self.powers:
            # smooth out weighting so that powers are more evenly selected from the list of available options
            return CustomPowerWeight(0.1, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(-1, ignore_usual_requirements=True)

    def force_powers(self) -> list[Power]:
        return self.force

    def power_delta(self) -> float:
        return -0.2 * sum(
            p.power_level for p in self.force_powers() if p in self.powers
        )


def generate_lich(settings: GenerationSettings) -> StatsBeingGenerated:
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
            Stats.STR.scaler(StatScaling.Default, mod=-2),
            Stats.DEX.scaler(StatScaling.Medium),
            Stats.INT.scaler(StatScaling.Primary),
            Stats.CON.scaler(StatScaling.Constitution, mod=-6),
            Stats.WIS.scaler(StatScaling.Medium, mod=-2),
            Stats.CHA.scaler(StatScaling.Medium),
        ],
        hp_multiplier=0.85 * settings.hp_multiplier,
        damage_multiplier=1.1 * settings.damage_multiplier,
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary(
            actions=3, resistances=4, boost_powers=False, has_lair=True
        )
        stats = stats.with_flags(
            flags.HAS_TELEPORT
        )  # lich has teleport via legendary action

    stats = stats.copy(
        creature_type=CreatureType.Undead,
        size=Size.Medium,
        languages=["All"],
        creature_class="Lich",
        caster_type=CasterType.Arcane,
        # liches have many bonus actions, reactions, and limited use abilities
        selection_target_args=dict(
            limited_uses_target=-1,
            limited_uses_max=3 if cr <= 11 else 4,
            reaction_target=-1,
            reaction_max=2,
            spellcasting_powers_target=-1,
            spellcasting_powers_max=-1,
            bonus_action_target=-1,
            bonus_action_max=2,
            recharge_target=1,
            recharge_max=1,
        ),
    )

    # SPEED
    if cr >= 12:
        stats = stats.copy(speed=Movement(walk=30, fly=15, hover=True))

    # ARMOR CLASS
    stats = stats.add_ac_template(ArcaneArmor)

    # ATTACKS
    attack = spell.ArcaneBurst.with_display_name("Necrotic Blast")

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Artillery, additional_roles=MonsterRole.Controller
    )

    # SKILLS
    expertise = [Skills.Arcana, Skills.History]
    skills = [Skills.Insight, Skills.Perception]
    stats = (
        stats.grant_proficiency_or_expertise(*skills)
        .grant_proficiency_or_expertise(*expertise)
        .grant_proficiency_or_expertise(*expertise)
    )  # skills and expertise

    # SAVES
    if cr >= 6:
        stats = stats.grant_save_proficiency(
            Stats.DEX, Stats.CON, Stats.INT, Stats.WIS, Stats.CHA
        )

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_LichWeights(stats, name, cr, variant, rng),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


LichTemplate: CreatureTemplate = CreatureTemplate(
    name="Lich",
    tag_line="Immortal Masters of Undeath and Arcana",
    description="Liches are mortal necromancers who defied death, binding their souls to the Mortal Realm through dark rituals and dreadful will. Rather than accept the inevitability of death, they craft soul anchors that lash their spirit in defiance of the natural order. The dark arts necessary to craft such a soul anchor are unique to each twisted soul that contemplates the heinous act, but in each case it involves unspeakably evil acts and cruel sacrifices. Countless aspiring liches have failed, but those who succeed attain unspeakable power.",
    environments=[],
    treasure=["Arcana", "Individual"],
    variants=[LichVariant],
    species=[],
    callback=generate_lich,
)
