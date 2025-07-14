from foe_foundry.environs import Affinity, Development, region
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import ChainShirt, PlateArmor, SplintArmor
from ...attack_template import AttackTemplate, weapon
from ...creature_types import CreatureType
from ...powers import PowerLoadout, PowerSelection
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

GuardVariant = MonsterVariant(
    name="Guard",
    description="Guards are perceptive, but most have little martial training. They might be bouncers, lookouts, members of a city watch, or other keen-eyed warriors.",
    monsters=[
        Monster(
            name="Guard",
            cr=1 / 8,
            srd_creatures=["Guard"],
            other_creatures={"Watchman": "alias"},
        ),
        Monster(name="Sergeant of the Watch", cr=1),
    ],
)
CommanderVariant = MonsterVariant(
    name="Captain of the Watch",
    description="Guard captains often have ample professional experience. They might be accomplished bodyguards, protectors of magic treasures, veteran watch members, or similar wardens.",
    monsters=[
        Monster(
            name="Guard Captain",
            cr=4,
            other_creatures={"Guard Captain": "mm25"},
        ),
        Monster(name="Lord of the Watch", cr=8, is_legendary=True),
    ],
)


class _GuardTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.species is not None and settings.species is not HumanSpecies:
            species_loadout = PowerLoadout(
                name=f"{settings.species.name} Powers",
                flavor_text=f"{settings.species.name} powers",
                powers=powers_for_role(
                    species=settings.species.name,
                    role={
                        MonsterRole.Defender,
                        MonsterRole.Soldier,
                        MonsterRole.Artillery,
                    },
                ),
            )
        else:
            species_loadout = None

        if settings.monster_key == "guard":
            return PowerSelection(powers.LoadoutGuard, species_loadout=species_loadout)
        elif settings.monster_key == "sergeant-of-the-watch":
            return PowerSelection(
                powers.LoadoutSeargant, species_loadout=species_loadout
            )
        elif settings.monster_key == "guard-captain":
            return PowerSelection(
                powers.LoadoutCaptain, species_loadout=species_loadout
            )
        elif settings.monster_key == "lord-of-the-watch":
            return PowerSelection(powers.LoadoutLord, species_loadout=species_loadout)
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

        if variant is CommanderVariant:
            stat_scaling = [
                Stats.STR.scaler(StatScaling.Primary),
                Stats.DEX.scaler(StatScaling.Medium, mod=4),
                Stats.INT.scaler(StatScaling.Default),
                Stats.WIS.scaler(StatScaling.Medium, mod=2),
                Stats.CHA.scaler(StatScaling.Default, mod=1),
            ]
        else:
            stat_scaling = [
                Stats.STR.scaler(StatScaling.Primary),
                Stats.DEX.scaler(StatScaling.Medium),
                Stats.INT.scaler(StatScaling.Default),
                Stats.WIS.scaler(StatScaling.Medium, mod=1),
                Stats.CHA.scaler(StatScaling.Default),
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
            stats = stats.as_legendary(actions=2, resistances=2)

        stats = stats.copy(
            creature_type=CreatureType.Humanoid,
            size=Size.Medium,
            languages=["Common"],
            creature_class="Guard",
        )

        # ARMOR CLASS
        if stats.cr >= 5:
            stats = stats.add_ac_template(PlateArmor)
        elif stats.cr >= 3:
            stats = stats.add_ac_template(SplintArmor)
        else:
            stats = stats.add_ac_template(ChainShirt)

        # ATTACKS
        attack = weapon.Crossbow
        secondary_attack = weapon.SpearAndShield
        stats = stats.copy(uses_shield=True)

        # ROLES
        if variant is CommanderVariant:
            primary_role = MonsterRole.Leader
            additional_roles = [
                MonsterRole.Defender,
                MonsterRole.Artillery,
                MonsterRole.Soldier,
            ]
        else:
            primary_role = MonsterRole.Defender
            additional_roles = [MonsterRole.Artillery, MonsterRole.Soldier]

        stats = stats.with_roles(
            primary_role=primary_role,
            additional_roles=additional_roles,
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(Skills.Perception)
        if cr >= 4:
            stats = stats.grant_proficiency_or_expertise(
                Skills.Initiative, Skills.Athletics
            )

        # SAVES
        if cr >= 4:
            stats = stats.grant_save_proficiency(Stats.STR)
        if cr >= 8:
            stats = stats.grant_save_proficiency(Stats.WIS, Stats.DEX, Stats.CON)

        return stats, [attack, secondary_attack]


GuardTemplate: MonsterTemplate = _GuardTemplate(
    name="Guard",
    tag_line="Sentries and Watch Members",
    description="Guards protect people, places, and things, either for pay or from a sense of duty. They might perform their duties vigilantly or distractedly. Some raise alarms at the first sign of danger and defend their charges with their lives. Others flee outright if their compensation doesn't match the danger they face.",
    treasure=[],
    environments=[
        (
            region.UrbanTownship,
            Affinity.native,
        ),  # guards are native to cities and towns
        (
            Development.settlement,
            Affinity.native,
        ),  # found in villages, towns, and established communities
        (Development.urban, Affinity.common),  # frequently found in larger cities
        (
            region.CountryShire,
            Affinity.common,
        ),  # common in rural settlements and villages
        (Development.stronghold, Affinity.common),  # often guard fortified locations
        (
            Development.frontier,
            Affinity.uncommon,
        ),  # occasionally found in frontier settlements
        (region.OpenRoads, Affinity.uncommon),  # sometimes serve as caravan escorts
        (Development.wilderness, Affinity.rare),  # rarely found away from civilization
    ],
    variants=[GuardVariant, CommanderVariant],
    species=AllSpecies,
)
