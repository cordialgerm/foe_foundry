from ...ac_templates import ChainShirt, PlateArmor
from ...attack_template import AttackTemplate, spell, weapon
from ...creature_types import CreatureType
from ...damage import DamageType
from ...powers import PowerLoadout, PowerSelection, flags
from ...powers.species import powers_for_role
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from ...spells import CasterType
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import BaseStatblock, base_stats
from ..species import AllSpecies, HumanSpecies
from . import powers as priest_powers

PriestVariant = MonsterVariant(
    name="Priest",
    description="Priests draw on their beliefs to heal the needful and smite their foes. They can channel their faith as spells and empower their weapons with divine might.",
    monsters=[
        Monster(name="Acolyte", cr=1 / 4, srd_creatures=["Acolyte"]),
        Monster(name="Priest", cr=2, srd_creatures=["Priest"]),
        Monster(name="Priest Anointed One", cr=5),
        Monster(
            name="Archpriest",
            cr=12,
            other_creatures={"Archpriest": "mm25"},
        ),
        Monster(name="Archpriest Living Saint", cr=16, is_legendary=True),
    ],
)


class _PriestTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        species = settings.species if settings.species else HumanSpecies
        cr = settings.cr
        if species is not HumanSpecies:
            species_loadoout = PowerLoadout(
                name=f"{species.name} Species Powers",
                flavor_text=f"{species.name} priestly powers",
                powers=powers_for_role(
                    species=species.name.lower(), role=MonsterRole.Support
                ),
            )
        else:
            species_loadoout = None

        if cr < 1:
            return PowerSelection(priest_powers.LoadoutAcolyte, species_loadoout)
        elif cr <= 2:
            return PowerSelection(priest_powers.LoadoutPriest, species_loadoout)
        elif cr <= 5:
            return PowerSelection(priest_powers.LoadoutAnointedOne, species_loadoout)
        elif cr <= 12:
            return PowerSelection(priest_powers.LoadoutArchpriest, species_loadoout)
        else:
            return PowerSelection(priest_powers.LoadoutArchpriest, species_loadoout)

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
                Stats.STR.scaler(StatScaling.Medium, mod=2),
                Stats.DEX.scaler(StatScaling.Default),
                Stats.INT.scaler(StatScaling.Default),
                Stats.WIS.scaler(StatScaling.Primary),
                Stats.CHA.scaler(StatScaling.Default),
            ],
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        # LEGENDARY
        if is_legendary:
            stats = stats.as_legendary(boost_ac=False)  # already very tanky

        stats = stats.copy(
            creature_type=CreatureType.Humanoid,
            size=Size.Medium,
            languages=["Common"],
            creature_class="Priest",
            caster_type=CasterType.Divine,
        )

        # ARMOR CLASS
        if stats.cr <= 6:
            stats = stats.add_ac_template(ChainShirt)
        else:
            stats = stats.add_ac_template(PlateArmor)

        # ATTACKS
        if stats.cr <= 2:
            attack = weapon.MaceAndShield
            uses_shield = True
            secondary_damage_type = DamageType.Radiant
        else:
            attack = spell.HolyBolt.with_display_name("Radiant Flame")
            uses_shield = False
            secondary_damage_type = DamageType.Radiant

        stats = stats.copy(
            secondary_damage_type=secondary_damage_type,
            uses_shield=uses_shield,
        )

        # Priests are spellcasters and should have fewer attacks
        stats = stats.with_reduced_attacks(reduce_by=1, min_attacks=2)

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Support,
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(Skills.Medicine, Skills.Religion)
        if cr >= 2:
            stats = stats.grant_proficiency_or_expertise(Skills.Perception)
        if cr >= 8:
            stats = stats.grant_proficiency_or_expertise(
                Skills.Initiative, Skills.Insight
            )

        # SAVES
        if cr >= 8:
            stats = stats.grant_save_proficiency(
                Stats.STR, Stats.CON, Stats.INT, Stats.WIS
            )

        # FLAGS
        # priests don't need other healing powers
        stats = stats.with_flags(flags.HAS_HEALING)

        return stats, [attack]


PriestTemplate: MonsterTemplate = _PriestTemplate(
    name="Priest",
    tag_line="Arbiters of the Mortal and the Divine",
    description="Priests harness the power of faith to work miracles. These religious adherents are as diverse as the faiths they follow. Some obey gods and their servants, while others live by age-old creeds. Belief guides priests’ actions and their magic, which they use to shape the world in line with their ideologies.",
    treasure=["Relics", "Individual"],
    variants=[PriestVariant],
    species=AllSpecies,
)
