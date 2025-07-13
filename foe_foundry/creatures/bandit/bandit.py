from foe_foundry.environs import Affinity, Development, region

from ...ac_templates import StuddedLeatherArmor
from ...attack_template import AttackTemplate, weapon
from ...creature_types import CreatureType
from ...damage import DamageType
from ...powers import PowerLoadout, PowerSelection
from ...powers.species import powers_for_role
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from ...statblocks import MonsterDials
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import BaseStatblock, base_stats
from ..species import AllSpecies, HumanSpecies
from . import powers

BanditVariant = MonsterVariant(
    name="Bandit",
    description="Bandits are inexperienced ne'er-do-wells who typically follow the orders of higher-ranking bandits.",
    monsters=[
        Monster(name="Bandit", cr=1 / 8, srd_creatures=["Bandit"]),
        Monster(name="Bandit Veteran", cr=1),
    ],
)
BanditCaptainVariant = MonsterVariant(
    name="Bandit Captain",
    description="Bandit captains command gangs of scoundrels and conduct straightforward heists. Others serve as guards and muscle for more influential criminals.",
    monsters=[
        Monster(name="Bandit Captain", cr=2, srd_creatures=["Bandit Captain"]),
        Monster(
            name="Bandit Crime Lord",
            cr=11,
            other_creatures={"Bandit Crime Lord": "mm25"},
            is_legendary=True,
        ),
    ],
)


class _BanditTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        species = settings.species if settings.species else HumanSpecies
        cr = settings.cr
        variant = settings.variant

        if species is not HumanSpecies:
            species_loadout = PowerLoadout(
                name=f"{species.name.title()} Bandit Powers",
                flavor_text=f"{species.name.title()} Bandit Powers",
                powers=powers_for_role(species=species.key, role=MonsterRole.Artillery),
            )
        else:
            species_loadout = None

        if variant is BanditVariant and cr < 1:
            return PowerSelection(
                loadouts=powers.LoadoutBandit,
                species_loadout=species_loadout,
            )
        elif variant is BanditVariant and cr >= 1:
            return PowerSelection(
                loadouts=powers.LoadoutBanditVeteran,
                species_loadout=species_loadout,
            )
        elif variant is BanditCaptainVariant and cr <= 2:
            return PowerSelection(
                loadouts=powers.LoadoutBanditCaptain,
                species_loadout=species_loadout,
            )
        elif variant is BanditCaptainVariant and cr > 2:
            return PowerSelection(
                loadouts=powers.LoadoutBanditLegend,
                species_loadout=species_loadout,
            )
        else:
            raise ValueError(f"Unknown bandit variant: {variant}")

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
                Stats.STR.scaler(StatScaling.Medium, mod=0.5),
                Stats.DEX.scaler(StatScaling.Primary),
                Stats.INT.scaler(StatScaling.Medium, mod=-0.5),
                Stats.WIS.scaler(StatScaling.Default),
                Stats.CHA.scaler(StatScaling.Medium, mod=-0.5),
            ],
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            name=name,
            creature_type=CreatureType.Humanoid,
            size=Size.Medium,
            languages=["Common"],
            creature_class="Bandit",
        )

        # ARMOR CLASS
        stats = stats.add_ac_template(
            StuddedLeatherArmor, ac_modifier=1 if cr >= 4 else 0
        )

        # LEGENDARY
        if is_legendary:
            stats = stats.as_legendary()

        # ATTACKS
        attack = weapon.Pistol if cr >= 1 else weapon.Shortswords

        # High CR criminals use poison as their secondary damage type
        # This means we want fewer overall attacks but more damage dice that include poison
        if cr >= 6:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)
            stats = stats.apply_monster_dials(
                MonsterDials(
                    multiattack_modifier=-1,
                    attack_damage_multiplier=stats.multiattack
                    / (stats.multiattack - 1),
                )
            )

        # Bandits with a Pistol also have Shortswords as a secondary attack
        # Bandits with Shortswords also have a Crossbow as a secondary attack
        if attack == weapon.Pistol:
            secondary_attack = weapon.Shortswords
        else:
            secondary_attack = weapon.Crossbow.with_display_name("Light Crossbow")

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Leader
            if variant is BanditCaptainVariant
            else MonsterRole.Artillery,
            additional_roles=[MonsterRole.Ambusher, MonsterRole.Artillery],
        )

        # SKILLS
        skills = [Skills.Stealth]
        if variant is BanditCaptainVariant:
            skills += [Skills.Deception, Skills.Athletics]
        if cr >= 6:
            skills += [Skills.Perception, Skills.Initiative]
        stats = stats.grant_proficiency_or_expertise(*skills)

        # EXPERTISE
        if cr >= 6:
            stats = stats.grant_proficiency_or_expertise(Skills.Stealth)
        if cr >= 11:
            stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

        # SAVES
        if cr >= 2:
            stats = stats.grant_save_proficiency(Stats.STR, Stats.DEX)

        if cr >= 4:
            stats = stats.grant_save_proficiency(Stats.STR, Stats.DEX, Stats.CON)

        return stats, [attack, secondary_attack]


BanditTemplate: MonsterTemplate = _BanditTemplate(
    name="Bandit",
    tag_line="Criminals and Scoundrels",
    description="Bandits use the threat of violence to take what they want. Such criminals include gang members, desperadoes, and lawless mercenaries. Yet not all bandits are motivated by greed. Some are driven to lives of crime by unjust laws, desperation, or the threats of merciless leaders.",
    treasure=["Any"],
    environments=[
        (
            Development.wilderness,
            Affinity.native,
        ),  # bandits hide in wild areas to avoid law
        (Development.frontier, Affinity.native),  # operate on the edges of civilization
        (
            region.OpenRoads,
            Affinity.common,
        ),  # waylay travelers on roads and trade routes
        (
            Development.countryside,
            Affinity.common,
        ),  # raid rural areas and small settlements
        (region.CountryShire, Affinity.common),  # threaten peaceful rural communities
        (Development.ruin, Affinity.uncommon),  # sometimes use ruins as hideouts
        (
            region.UrbanTownship,
            Affinity.uncommon,
        ),  # operate in cities as criminal gangs
        (Development.settlement, Affinity.rare),  # avoid well-protected settlements
    ],
    variants=[BanditVariant, BanditCaptainVariant],
    species=AllSpecies,
)
