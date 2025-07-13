from foe_foundry.environs import Affinity, Development, region

from ...ac_templates import StuddedLeatherArmor
from ...attack_template import AttackTemplate, weapon
from ...creature_types import CreatureType
from ...damage import DamageType
from ...powers import (
    PowerLoadout,
    PowerSelection,
)
from ...powers.species import powers_for_role
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from ...statblocks import BaseStatblock, MonsterDials
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from ..species import AllSpecies, HumanSpecies
from . import powers

AssassinVariant = MonsterVariant(
    name="Assassin",
    description="Assassins are professional killers skilled at stealthily approaching their victims and striking unseen. Most assassins kill for a reason, perhaps hiring themselves out to wealthy patrons or slaying for an unscrupulous cause. They use poisons and other deadly tools, and they might carry equipment to help them break into secure areas or avoid capture.",
    monsters=[
        Monster(name="Contract Killer", cr=4),
        Monster(name="Assassin", cr=8, srd_creatures=["Assassin"]),
        Monster(name="Assassin Legend", cr=12, is_legendary=True),
    ],
)


class _AssassinTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        cr = settings.cr
        species = settings.species

        if species is None:
            species = HumanSpecies

        if species is not HumanSpecies:
            species_loadout = PowerLoadout(
                name=f"{species.name} Species Powers",
                flavor_text=f"{species.name} assassin powers",
                powers=powers_for_role(
                    species=species.name.lower(),
                    role={MonsterRole.Ambusher, MonsterRole.Skirmisher},
                ),
            )
        else:
            species_loadout = None

        if cr <= 4:
            return PowerSelection(
                loadouts=powers.LoadoutContractKiller,
                species_loadout=species_loadout,
            )
        elif cr <= 8:
            return PowerSelection(
                loadouts=powers.LoadoutAssassin,
                species_loadout=species_loadout,
            )
        else:
            return PowerSelection(
                loadouts=powers.LoadoutLegendaryAssassin,
                species_loadout=species_loadout,
            )

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        variant = settings.variant
        species = settings.species if settings.species else HumanSpecies
        rng = settings.rng
        is_legendary = settings.is_legendary

        # STATS
        stats = base_stats(
            name=variant.name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            species_key=species.key,
            cr=cr,
            stats=[
                Stats.STR.scaler(StatScaling.Default),
                Stats.DEX.scaler(StatScaling.Primary),
                Stats.INT.scaler(StatScaling.Medium, mod=0.5),
                Stats.WIS.scaler(StatScaling.Medium, mod=1),
                Stats.CHA.scaler(StatScaling.Medium, mod=1),
            ],
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )
        stats = stats.copy(
            name=name,
            creature_type=CreatureType.Humanoid,
            size=Size.Medium,
            languages=["Common"],
            creature_class="Assassin",
            speed=stats.speed.grant_climbing(),
            primary_damage_type=DamageType.Piercing,
        )

        if is_legendary:
            stats = stats.as_legendary()

        ## HP
        # Assassins have lower HP than average
        stats = stats.apply_monster_dials(MonsterDials(hp_multiplier=0.85))

        # ARMOR CLASS
        stats = stats.add_ac_template(
            StuddedLeatherArmor, ac_modifier=1 if cr >= 10 else 0
        )

        # ATTACKS

        # Spies use poison as their secondary damage type
        # This means we want fewer overall attacks but more damage dice that include poison
        stats = stats.copy(
            secondary_damage_type=DamageType.Poison,
        )

        if stats.cr <= 4:
            stats = stats.with_set_attacks(1)
        elif stats.multiattack > 2:
            stats = stats.with_set_attacks(2)

        # Spies use poisoned Daggers as their primary attack
        attack = weapon.Daggers.with_display_name("Poisoned Dagger")

        # Spies also have a Hand Crossbow as a secondary attack
        secondary_attack = weapon.HandCrossbow.with_display_name(
            "Poisoned Hand Crossbow"
        )

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Ambusher,
            additional_roles=[
                MonsterRole.Skirmisher,
                MonsterRole.Artillery,
            ],
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(
            Skills.Acrobatics, Skills.Perception, Skills.Stealth, Skills.Initiative
        )

        # EXPERTISE
        if cr >= 6:
            stats = stats.grant_proficiency_or_expertise(
                Skills.Stealth, Skills.Perception, Skills.Initiative
            )

        # SAVES
        if cr >= 6:
            stats = stats.grant_save_proficiency(Stats.DEX, Stats.INT)

        return stats, [attack, secondary_attack]


AssassinTemplate: MonsterTemplate = _AssassinTemplate(
    name="Assassin",
    tag_line="Contract Killers",
    description="Assassins are professional killers skilled at stealthily approaching their victims and striking unseen. Most assassins kill for a reason, perhaps hiring themselves out to wealthy patrons or slaying for an unscrupulous cause. They use poisons and other deadly tools, and they might carry equipment to help them break into secure areas or avoid capture.",
    treasure=["Any"],
    environments=[
        (
            region.UrbanTownship,
            Affinity.native,
        ),  # professional killers operate in cities
        (
            Development.urban,
            Affinity.common,
        ),  # found in large cities with wealthy patrons
        (
            Development.settlement,
            Affinity.common,
        ),  # work in towns and established communities
        (region.CountryShire, Affinity.uncommon),  # occasionally target rural nobility
        (Development.stronghold, Affinity.uncommon),  # infiltrate fortified locations
        (Development.frontier, Affinity.rare),  # rarely operate in frontier areas
        (Development.wilderness, Affinity.rare),  # almost never found in wild areas
    ],
    variants=[AssassinVariant],
    species=AllSpecies,
)
