from foe_foundry.environs import Affinity, Biome, Development, region
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import NaturalPlating
from ...attack_template import AttackTemplate, natural
from ...creature_types import CreatureType
from ...damage import DamageType
from ...powers import (
    PowerSelection,
)
from ...role_types import MonsterRole
from ...size import Size
from ...skills import AbilityScore, StatScaling
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

BasiliskVariant = MonsterVariant(
    name="Basilisk",
    description="Basilisks are large, reptilian creatures with the ability to turn flesh to stone with their gaze. They are often found in rocky areas and caves, where they use their petrifying gaze to protect their territory.",
    monsters=[
        Monster(name="Basilisk", cr=3, srd_creatures=["Basilisk"]),
        Monster(name="Basilisk Broodmother", cr=8),
    ],
)


class _BasiliskTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "basilisk":
            return PowerSelection(loadouts=powers.LoadoutBasilisk)
        elif settings.monster_key == "basilisk-broodmother":
            return PowerSelection(loadouts=powers.LoadoutBasiliskBroodmother)
        else:
            raise ValueError(f"Unknown basilisk variant: {settings.monster_key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr

        # STATS
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=[
                AbilityScore.STR.scaler(StatScaling.Primary),
                AbilityScore.DEX.scaler(StatScaling.Default, mod=-2),
                AbilityScore.INT.scaler(StatScaling.Default, mod=-6),
                AbilityScore.WIS.scaler(StatScaling.Medium, mod=-4),
                AbilityScore.CHA.scaler(StatScaling.Default, mod=-3),
            ],
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Monstrosity,
            size=Size.Medium,
            creature_class="Basilisk",
            senses=stats.senses.copy(darkvision=60),
        )

        # ARMOR CLASS
        stats = stats.add_ac_template(NaturalPlating)

        # ATTACKS
        attack = natural.Bite.with_display_name("Venomous Bite")
        stats = stats.copy(
            secondary_damage_type=DamageType.Poison,
        )
        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Bruiser, additional_roles=MonsterRole.Controller
        )

        # SAVES
        if cr >= 8:
            stats = stats.grant_save_proficiency(
                AbilityScore.CON, AbilityScore.STR, AbilityScore.WIS
            )

        return stats, [attack]


BasiliskTemplate: MonsterTemplate = _BasiliskTemplate(
    name="Basilisk",
    tag_line="Reptilian guardian with a petrifying gaze",
    description="Basilisks are large, reptilian creatures with the ability to turn flesh to stone with their gaze. They are often found in rocky areas and caves, where they use their petrifying gaze to protect their territory.",
    treasure=[],
    environments=[
        (
            Biome.underground,
            Affinity.native,
        ),  # basilisks are native to caves and tunnels
        (
            region.LoftyMountains,
            Affinity.native,
        ),  # natural habitat in rocky mountain areas
        (Development.wilderness, Affinity.common),  # found in wild, undeveloped areas
        (
            region.HauntedLands,
            Affinity.common,
        ),  # often found in cursed or dangerous places
        (Development.ruin, Affinity.common),  # commonly inhabit ancient ruins
        (region.BlastedBadlands, Affinity.uncommon),  # occasionally in desolate areas
        (Development.frontier, Affinity.uncommon),  # rarely venture near settlements
    ],
    variants=[BasiliskVariant],
    species=[],
)
