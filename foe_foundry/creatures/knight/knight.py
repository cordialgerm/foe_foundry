from foe_foundry.environs import Affinity, Development
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import PlateArmor
from ...attack_template import AttackTemplate, weapon
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...powers import PowerLoadout, PowerSelection
from ...powers.species import powers_for_role
from ...role_types import MonsterRole
from ...size import Size
from ...skills import AbilityScore, Skills, StatScaling
from ...spells import CasterType
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from ..species import AllSpecies, HumanSpecies
from . import powers

KnightVariant = MonsterVariant(
    name="Knight",
    description="Knights are heavily armored warriors who lead troops in combat and dominate the field of battle.",
    monsters=[
        Monster(name="Knight", cr=3, srd_creatures=["Knight"]),
        Monster(name="Knight of the Realm", cr=6),
        Monster(
            name="Questing Knight",
            cr=12,
            other_creatures={"Questing Knight": "mm25"},
        ),
        Monster(name="Paragon Knight", cr=16, is_legendary=True),
    ],
)


class _KnightTemplate(MonsterTemplate):
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
                        MonsterRole.Bruiser,
                    },
                ),
            )
        else:
            species_loadout = None

        if settings.monster_key == "knight":
            return PowerSelection(powers.LoadoutKnight, species_loadout)
        elif settings.monster_key == "knight-of-the-realm":
            return PowerSelection(powers.LoadoutKnightOfTheRealm, species_loadout)
        elif settings.monster_key == "questing-knight":
            return PowerSelection(powers.LoadoutQuestingKnight, species_loadout)
        elif settings.monster_key == "paragon-knight":
            return PowerSelection(powers.LoadoutParagonKnight, species_loadout)
        else:
            raise ValueError(f"Unknown knight variant: {settings.monster_key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        species = settings.species if settings.species else HumanSpecies
        is_legendary = settings.is_legendary

        # STATS
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            species_key=species.key,
            cr=cr,
            stats={
                AbilityScore.STR: StatScaling.Primary,
                AbilityScore.DEX: StatScaling.Default,
                AbilityScore.INT: StatScaling.Default,
                AbilityScore.WIS: StatScaling.Medium,
                AbilityScore.CHA: (StatScaling.Medium, 2),
            },
            hp_multiplier=settings.hp_multiplier * (1.1 if cr >= 12 else 1.0),
            damage_multiplier=settings.damage_multiplier,
        )

        # LEGENDARY
        if is_legendary:
            stats = stats.as_legendary()

        stats = stats.copy(
            creature_type=CreatureType.Humanoid,
            size=Size.Medium,
            languages=["Common"],
            creature_class="Knight",
        )

        # ARMOR CLASS
        stats = stats.add_ac_template(PlateArmor)

        # ATTACKS
        if stats.cr >= 12:
            attack = weapon.Greatsword.with_display_name("Oathbound Blade")
        elif stats.cr >= 6:
            attack = weapon.Greatsword.with_display_name("Blessed Blade")
        else:
            attack = weapon.Greatsword

        secondary_damage_type = DamageType.Radiant

        stats = stats.copy(
            secondary_damage_type=secondary_damage_type,
            uses_shield=False,
        )

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Soldier,
            additional_roles=[MonsterRole.Leader, MonsterRole.Support],
        )

        # SPELLCASTING
        if cr >= 6:
            stats = stats.grant_spellcasting(caster_type=CasterType.Divine)

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(Skills.Athletics)
        if cr >= 5:
            stats = stats.grant_proficiency_or_expertise(
                Skills.Perception, Skills.Persuasion, Skills.Initiative
            )

        # SAVES
        stats = stats.grant_save_proficiency(AbilityScore.CON)
        if cr >= 6:
            stats = stats.grant_save_proficiency(
                AbilityScore.STR, AbilityScore.WIS, AbilityScore.CHA
            )

        # IMMUNITIES
        stats = stats.grant_resistance_or_immunity(conditions={Condition.Frightened})
        if cr >= 6:
            stats = stats.grant_resistance_or_immunity(
                conditions={Condition.Charmed, Condition.Frightened}
            )

        return stats, [attack]


KnightTemplate: MonsterTemplate = _KnightTemplate(
    name="Knight",
    tag_line="Battle Masters and Heroic Wanderers",
    description="Knights are skilled warriors trained for war and tested in battle. Many serve the rulers of a realm, a faith, or an order devoted to a cause.",
    treasure=["Relics", "Individual"],
    variants=[KnightVariant],
    species=AllSpecies,
    environments=[
        (Development.urban, Affinity.native),  # Cities and courts where they serve
        (Development.stronghold, Affinity.native),  # Castles and fortified places
        (Development.settlement, Affinity.common),  # Towns and villages they protect
        (Development.countryside, Affinity.common),  # Rural areas they patrol
        (Development.frontier, Affinity.uncommon),  # Border regions they guard
        (Development.wilderness, Affinity.rare),  # Questing knights on adventures
    ],
)
