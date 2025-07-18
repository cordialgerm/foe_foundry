from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import UnholyArmor
from ...attack_template import AttackTemplate, natural
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...environs import Development, Terrain
from ...environs.affinity import Affinity
from ...environs.extraplanar import ExtraplanarInfluence
from ...environs.region import HauntedLands
from ...movement import Movement
from ...powers import PowerSelection
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

VrockVariant = MonsterVariant(
    name="Vrock",
    description="Vrocks are screeching vulture-like harbringers of chaos and destruction that carry disease and pestilance from the lower planes.",
    monsters=[
        Monster(name="Vrock", cr=6, srd_creatures=["Vrock"]),
    ],
)


class _VrockTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        return PowerSelection(loadouts=powers.LoadoutVrock)

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
                AbilityScore.DEX.scaler(StatScaling.Medium, mod=2),
                AbilityScore.CON.scaler(StatScaling.Constitution, mod=4),
                AbilityScore.INT.scaler(StatScaling.Default, mod=-4),
                AbilityScore.WIS.scaler(StatScaling.Default, mod=2),
                AbilityScore.CHA.scaler(StatScaling.Default, mod=-4),
            ],
            hp_multiplier=1.2 * settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Fiend,
            languages=["Abyssal; telepathy 120 ft."],
            creature_class="Vrock",
            creature_subtype="Demon",
            senses=stats.senses.copy(darkvision=120),
            size=Size.Large,
            speed=Movement(walk=40, fly=60),
        )

        # ARMOR CLASS
        stats = stats.add_ac_template(UnholyArmor)

        # ATTACKS
        attack = natural.Claw.with_display_name("Diseased Talons")
        stats = stats.copy(
            secondary_damage_type=DamageType.Poison,
        )

        # Vrocks use two attacks
        stats = stats.with_set_attacks(2)

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Skirmisher,
            additional_roles=[MonsterRole.Controller],
        )

        # SAVES
        stats = stats.grant_save_proficiency(
            AbilityScore.DEX, AbilityScore.WIS, AbilityScore.CHA
        )

        # IMMUNITIES
        stats = stats.grant_resistance_or_immunity(
            immunities={DamageType.Poison},
            resistances={DamageType.Cold, DamageType.Lightning, DamageType.Fire},
            conditions={Condition.Poisoned},
        )

        return stats, [attack]


VrockTemplate: MonsterTemplate = _VrockTemplate(
    name="Vrock",
    tag_line="Demon of Carnage and Ruin",
    description="Vrocks are screeching vulture-like harbringers of chaos and destruction that carry disease and pestilance from the lower planes.",
    treasure=[],
    variants=[VrockVariant],
    species=[],
    environments=[
        # Vrocks are demons from the Abyss that appear where chaos and destruction reign
        (
            ExtraplanarInfluence.hellish,
            Affinity.common,
        ),  # Primary planar influence - demonic/infernal
        (ExtraplanarInfluence.deathly, Affinity.uncommon),  # Death-aligned areas
        (HauntedLands, Affinity.uncommon),  # Haunted and cursed regions
        (Development.ruin, Affinity.common),  # Areas of destruction and decay
        (Development.dungeon, Affinity.uncommon),  # Hidden places of evil
        (Development.stronghold, Affinity.rare),  # Corrupted fortresses
        (Terrain.mountain, Affinity.uncommon),  # High places for aerial attacks
        (Terrain.plain, Affinity.rare),  # Open battlefields for destruction
    ],
)
