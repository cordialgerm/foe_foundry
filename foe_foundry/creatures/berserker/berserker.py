from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import BerserkersDefense
from ...attack_template import AttackTemplate, weapon
from ...creature_types import CreatureType
from ...damage import DamageType
from ...powers import PowerLoadout, PowerSelection
from ...powers.species import powers_for_role
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from ...utils.rng import choose_enum
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from ..species import AllSpecies, HumanSpecies
from . import powers

BerserkerVariant = MonsterVariant(
    name="Berserker",
    description="Berserkers might fight for personal glory or form motivated forces or howling hordes.",
    monsters=[
        Monster(name="Berserker", cr=2, srd_creatures=["Berserker"]),
        Monster(name="Berserker Veteran", cr=4),
    ],
)
CommanderVariant = MonsterVariant(
    name="Berserker Commander",
    description="Berserker commanders bear the scars of battle and drive their followers to match their deadly zeal. These commanders tap into a primal magic to enhance their might.",
    monsters=[
        Monster(
            name="Berserker Commander",
            cr=8,
            other_creatures={"Berserker Commander": "mm25"},
        ),
        Monster(name="Berserker Legend", cr=12, is_legendary=True),
    ],
)


class _BerserkerTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.species is not None and settings.species is not HumanSpecies:
            species_loadout = PowerLoadout(
                name=f"{settings.species.name} Powers",
                flavor_text=f"{settings.species.name} powers",
                powers=powers_for_role(settings.species.name, MonsterRole.Bruiser),
            )
        else:
            species_loadout = None

        if settings.monster_key == "berserker":
            return PowerSelection(powers.LoadoutBerserker, species_loadout)
        elif settings.monster_key == "berserker-veteran":
            return PowerSelection(powers.LoadoutBerserkerVeteran, species_loadout)
        elif settings.monster_key == "berserker-commander":
            return PowerSelection(powers.LoadoutBerserkerCommander, species_loadout)
        elif settings.monster_key == "berserker-legend":
            return PowerSelection(powers.LoadoutBerserkerLegend, species_loadout)
        else:
            raise ValueError(
                f"Unknown monster key '{settings.monster_key}' for Berserker generation."
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
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            species_key=species.key,
            cr=cr,
            stats=[
                Stats.STR.scaler(StatScaling.Primary),
                Stats.DEX.scaler(StatScaling.Medium, 2),
                Stats.CON.scaler(StatScaling.Constitution, 2),
                Stats.INT.scaler(StatScaling.Default, mod=-1),
                Stats.WIS.scaler(StatScaling.Default),
                Stats.CHA.scaler(StatScaling.Default, mod=-1),
            ],
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Humanoid,
            size=Size.Medium,
            languages=["Common"],
            creature_class="Berserker",
        )

        # LEGENDARY
        if is_legendary:
            stats = stats.as_legendary()

        # ARMOR CLASS
        stats = stats.add_ac_template(BerserkersDefense)

        # ATTACKS
        attack = weapon.Greataxe

        # Secondary Damage
        # Berserkers are empowered with primal magic at higher CRs
        elemental_damage_type = choose_enum(rng, list(DamageType.Primal()))
        if cr >= 4:
            stats = stats.copy(secondary_damage_type=elemental_damage_type)

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Bruiser,
            additional_roles=[MonsterRole.Leader]
            if variant is CommanderVariant
            else [MonsterRole.Soldier],
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(Skills.Athletics)
        if cr >= 4:
            stats = stats.grant_proficiency_or_expertise(Skills.Perception)
        if cr >= 8:
            stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

        # SAVES
        if cr >= 4:
            stats = stats.copy(
                attributes=stats.attributes.grant_save_proficiency(Stats.STR)
            )

        if cr >= 4:
            stats = stats.copy(
                attributes=stats.attributes.grant_save_proficiency(Stats.CON, Stats.STR)
            )

        return stats, [attack]


BerserkerTemplate: MonsterTemplate = _BerserkerTemplate(
    name="Berserker",
    tag_line="Raging Invaders and Impassioned Warriors",
    description="Gripped by the adrenaline of battle, berserkers are reckless invaders, pit fighters, and other ferocious warriors.",
    environments=["Urban"],
    treasure=["Armaments", "Individual"],
    variants=[BerserkerVariant, CommanderVariant],
    species=AllSpecies,
)
