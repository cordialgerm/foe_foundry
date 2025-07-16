from foe_foundry.environs import Affinity, Biome, Development, Terrain, region
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import LeatherArmor, StuddedLeatherArmor
from ...attack_template import AttackTemplate, weapon
from ...creature_types import CreatureType
from ...powers import (
    PowerLoadout,
    PowerSelection,
)
from ...powers.species import powers_for_role
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from ..species import AllSpecies, HumanSpecies
from . import powers

ScoutVariant = MonsterVariant(
    name="Scout",
    description="Guards are perceptive, but most have little martial training. They might be bouncers, lookouts, members of a city watch, or other keen-eyed warriors.",
    monsters=[
        Monster(
            name="Scout",
            cr=1 / 2,
            srd_creatures=["Scout"],
        ),
        Monster(name="Ranger", cr=5),
    ],
)
CommanderVariant = MonsterVariant(
    name="Scout Captain",
    description="Scout captains are experienced explorers and sharpshooters. They might lead bands of other scouts or disappear into the wilds alone for months at a time.",
    monsters=[
        Monster(
            name="Scout Captain",
            cr=3,
            other_creatures={"Scout Captain": "mm25"},
        ),
        Monster(name="First Scout", cr=7, is_legendary=True),
    ],
)


class _ScoutTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.species is not None and settings.species is not HumanSpecies:
            species_loadout = PowerLoadout(
                name=f"{settings.species.name} Powers",
                flavor_text=f"{settings.species.name} powers",
                powers=powers_for_role(
                    species=settings.species.name,
                    role={
                        MonsterRole.Ambusher,
                        MonsterRole.Skirmisher,
                        MonsterRole.Artillery,
                    },
                ),
            )
        else:
            species_loadout = None

        if settings.monster_key == "scout":
            return PowerSelection(
                loadouts=powers.LoadoutScout,
                species_loadout=species_loadout,
            )
        elif settings.monster_key == "ranger":
            return PowerSelection(
                loadouts=powers.LoadoutRanger,
                species_loadout=species_loadout,
            )
        elif settings.monster_key == "scout-captain":
            return PowerSelection(
                loadouts=powers.LoadoutScoutCaptain,
                species_loadout=species_loadout,
            )
        elif settings.monster_key == "first-scout":
            return PowerSelection(
                loadouts=powers.LoadoutFirstScout,
                species_loadout=species_loadout,
            )
        else:
            raise ValueError(f"Unknown monster key: {settings.monster_key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        variant = settings.variant
        species = settings.species if settings.species else HumanSpecies
        is_legendary = settings.is_legendary

        # STATS

        stat_scaling = [
            Stats.STR.scaler(StatScaling.Default),
            Stats.DEX.scaler(StatScaling.Primary),
            Stats.INT.scaler(StatScaling.Default, mod=0.5),
            Stats.WIS.scaler(StatScaling.Medium, mod=1),
            Stats.CHA.scaler(StatScaling.Default, mod=0.5),
        ]

        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            species_key=species.key,
            cr=cr,
            stats=stat_scaling,
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        # LEGENDARY
        if is_legendary:
            stats = stats.as_legendary()

        stats = stats.copy(
            creature_type=CreatureType.Humanoid,
            size=Size.Medium,
            languages=["Common"],
            creature_class="Scout",
        )

        # ARMOR CLASS
        if stats.cr >= 3:
            stats = stats.add_ac_template(StuddedLeatherArmor)
        else:
            stats = stats.add_ac_template(LeatherArmor)

        # ATTACKS
        attack = weapon.Longbow
        secondary_attack = weapon.Shortswords.copy(damage_scalar=0.9)

        stats = stats.copy(primary_damage_type=attack.damage_type)
        stats = stats.copy(uses_shield=False)

        # ROLES
        primary_role = MonsterRole.Skirmisher
        additional_roles = [MonsterRole.Artillery, MonsterRole.Ambusher]
        if variant is CommanderVariant:
            additional_roles.append(MonsterRole.Leader)

        stats = stats.with_roles(
            primary_role=primary_role,
            additional_roles=additional_roles,
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(
            Skills.Perception,
            Skills.Nature,
            Skills.Survival,
            Skills.Stealth,
            Skills.Initiative,
        )
        if cr >= 3:
            stats = stats.grant_proficiency_or_expertise(
                Skills.Perception, Skills.Stealth, Skills.Survival
            )

        # SAVES
        if cr >= 3:
            stats = stats.grant_save_proficiency(Stats.DEX, Stats.INT)
        if cr >= 7:
            stats = stats.grant_save_proficiency(Stats.WIS)

        return stats, [attack, secondary_attack]


ScoutTemplate: MonsterTemplate = _ScoutTemplate(
    name="Scout",
    tag_line="Watchers and Wanderers",
    description="Scouts are warriors of the wilderness, trained in hunting and tracking. They might be explorers or trappers, or they could perform more martial roles as archers, bounty hunters, or outriders.",
    treasure=[],
    variants=[ScoutVariant, CommanderVariant],
    species=AllSpecies,
    environments=[
        (region.CountryShire, Affinity.native),  # Rural areas they patrol
        (region.WartornKingdom, Affinity.common),  # War-torn regions they scout
        (region.TangledForest, Affinity.native),  # Forests they navigate
        (Development.frontier, Affinity.native),  # Border regions they patrol and guard
        (
            Development.wilderness,
            Affinity.native,
        ),  # Wild areas they explore and navigate
        (Biome.forest, Affinity.common),  # Wooded areas ideal for tracking and stealth
        (Terrain.hill, Affinity.common),  # High ground providing good vantage points
        (
            Development.countryside,
            Affinity.common,
        ),  # Rural areas they watch and protect
        (
            Terrain.mountain,
            Affinity.uncommon,
        ),  # Mountainous terrain they might traverse
        (
            Biome.grassland,
            Affinity.uncommon,
        ),  # Open plains where they serve as outriders
        (
            Development.settlement,
            Affinity.rare,
        ),  # Towns where they might report or resupply
    ],
)
