from foe_foundry.environs import Affinity, Biome, Development, region
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import ChainShirt, HolyArmor, NaturalArmor, SplintArmor
from ...attack_template import AttackTemplate, spell, weapon
from ...creature_types import CreatureType
from ...powers import PowerSelection
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
from . import powers

KoboldWarrenguardVariant = MonsterVariant(
    name="Kobold Warrenguard",
    description="Warrenguards are proud nest defenders. They are known to work in disciplined formations, using their superior numbers to overwhelm their foes and protect their territory.",
    monsters=[
        Monster(
            name="Kobold Warrenguard",
            cr=1 / 8,
            srd_creatures=["Kobold"],
            other_creatures={"Kobold Warrior": "mm25"},
        )
    ],
)

KoboldSharpsnoutVariant = MonsterVariant(
    name="Kobold Sharpsnout",
    description="Sharpsnouts have honed their devious instincts to a craft. Their cunning traps and devious ambushes have laid low many an unprepared intruder.",
    monsters=[Monster(name="Kobold Sharpsnout", cr=1 / 2)],
)

KoboldAscendant = MonsterVariant(
    name="Kobold Ascendant",
    description="Aspirants are fanatical zealots to their True Dragon overlords. They carry a sacred Draconic Standard imbued with the power of the collective will of their tribe.",
    monsters=[Monster(name="Kobold Ascendant", cr=1)],
)

KoboldWyrmcallerVariant = MonsterVariant(
    name="Kobold Wyrmcaller",
    description="Wyrmcallers are wizened shamans who have learned to commune with the spirits of True Dragons. They are capable of guiding the souls of brave Kobold martyrs to reincarnate as a True Dragon",
    monsters=[Monster(name="Kobold Wyrmcaller", cr=2)],
)


class _KoboldTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "kobold-warrenguard":
            return PowerSelection(powers.LoadoutWarrenguard)
        elif settings.monster_key == "kobold-sharpsnout":
            return PowerSelection(powers.LoadoutSharpsnout)
        elif settings.monster_key == "kobold-ascendant":
            return PowerSelection(powers.LoadoutAscendant)
        elif settings.monster_key == "kobold-wyrmcaller":
            return PowerSelection(powers.LoadoutWyrmcaller)
        else:
            raise ValueError(
                f"Unexpected monster key {settings.monster_key} for Kobold generation."
            )

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        variant = settings.variant

        # STATS
        if variant is KoboldWarrenguardVariant or variant is KoboldAscendant:
            hp_multiplier = 0.8
            damage_multiplier = 1.1
            attrs = {
                AbilityScore.STR: (StatScaling.Primary, 1),
                AbilityScore.DEX: StatScaling.Medium,
                AbilityScore.CON: (StatScaling.Constitution, -2),
                AbilityScore.INT: (StatScaling.Default, -2),
                AbilityScore.WIS: (StatScaling.Default, -3),
                AbilityScore.CHA: (StatScaling.Default, -2),
            }
        elif variant is KoboldSharpsnoutVariant:
            hp_multiplier = 0.8
            damage_multiplier = 1.1
            attrs = {
                AbilityScore.STR: StatScaling.Default,
                AbilityScore.DEX: StatScaling.Primary,
                AbilityScore.CON: (StatScaling.Constitution, -2),
                AbilityScore.INT: (StatScaling.Default, -3),
                AbilityScore.WIS: (StatScaling.Default, 1),
                AbilityScore.CHA: (StatScaling.Default, -2),
            }
        elif variant is KoboldWyrmcallerVariant:
            hp_multiplier = 0.9
            damage_multiplier = 1.0
            attrs = {
                AbilityScore.STR: (StatScaling.Default, -2),
                AbilityScore.DEX: StatScaling.Medium,
                AbilityScore.CON: (StatScaling.Constitution, -2),
                AbilityScore.INT: (StatScaling.Medium, 0.5),
                AbilityScore.WIS: (StatScaling.Primary, 1),
                AbilityScore.CHA: StatScaling.Medium,
            }
        else:
            raise ValueError(f"Unknown kobold variant: {variant}")

        stats = base_stats(
            name=variant.name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=attrs,
            hp_multiplier=hp_multiplier * settings.hp_multiplier,
            damage_multiplier=damage_multiplier * settings.damage_multiplier,
        )

        stats = stats.copy(
            name=name,
            size=Size.Small,
            languages=["Common", "Draconic"],
            creature_class="Kobold",
        ).with_types(
            primary_type=CreatureType.Humanoid, additional_types=CreatureType.Dragon
        )

        # SENSES
        stats = stats.copy(senses=stats.senses.copy(darkvision=60))

        # ARMOR CLASS
        if variant is KoboldWarrenguardVariant:
            stats = stats.add_ac_template(ChainShirt)
        elif variant is KoboldSharpsnoutVariant:
            stats = stats.add_ac_template(NaturalArmor)
        elif variant is KoboldAscendant:
            stats = stats.add_ac_template(SplintArmor)
        elif variant is KoboldWyrmcallerVariant:
            stats = stats.add_ac_template(HolyArmor)

        # ATTACKS
        if variant is KoboldWarrenguardVariant:
            attack = weapon.SpearAndShield.with_display_name("Spear Formation")
        elif variant is KoboldSharpsnoutVariant:
            attack = weapon.Shortbow.with_display_name("Crafty Shots")
        elif variant is KoboldAscendant:
            attack = weapon.Polearm.with_display_name("Dragonfang Halberd")
        elif variant is KoboldWyrmcallerVariant:
            attack = spell.HolyBolt.with_display_name("Draconic Invocation")

        # SPELLS
        if variant is KoboldWyrmcallerVariant:
            stats = stats.grant_spellcasting(
                caster_type=CasterType.Divine, spellcasting_stat=AbilityScore.WIS
            )

        # ROLES
        if variant is KoboldWarrenguardVariant:
            primary_role = MonsterRole.Soldier
            secondary_roles = None
        elif variant is KoboldSharpsnoutVariant:
            primary_role = MonsterRole.Ambusher
            secondary_roles = {MonsterRole.Skirmisher, MonsterRole.Artillery}
        elif variant is KoboldAscendant:
            primary_role = MonsterRole.Soldier
            secondary_roles = {MonsterRole.Leader}
        elif variant is KoboldWyrmcallerVariant:
            primary_role = MonsterRole.Support
            secondary_roles = None

        stats = stats.with_roles(
            primary_role=primary_role, additional_roles=secondary_roles
        )

        # SKILLS
        if variant is KoboldSharpsnoutVariant:
            stats = stats.grant_proficiency_or_expertise(
                Skills.Stealth, Skills.Perception
            ).grant_proficiency_or_expertise(Skills.Stealth)  # expertise

        # SAVES
        if cr >= 2:
            stats = stats.grant_save_proficiency(AbilityScore.CON, AbilityScore.WIS)

        return stats, [attack]


KoboldTemplate: MonsterTemplate = _KoboldTemplate(
    name="Kobold",
    tag_line="Proud Zealots of True Dragons",
    description="Kobolds are small reptilian guardians of True Dragon lairs. They are known for their zealous dedication to their True Dragon overlords and their cunning defense of the lairs they protect.",
    treasure=["Any"],
    variants=[
        KoboldWarrenguardVariant,
        KoboldSharpsnoutVariant,
        KoboldAscendant,
        KoboldWyrmcallerVariant,
    ],
    species=[],
    is_sentient_species=True,
    environments=[
        (region.LoftyMountains, Affinity.native),  # Mountain lairs of True Dragons
        (Biome.underground, Affinity.native),  # Tunnel warrens and cave systems
        (
            Development.dungeon,
            Affinity.native,
        ),  # Dragon lairs and underground complexes
        (Development.ruin, Affinity.common),  # Ancient sites they claim as territory
        (
            Development.wilderness,
            Affinity.common,
        ),  # Remote areas near dragon territories
        (Development.frontier, Affinity.uncommon),  # Edge settlements they might raid
        (
            Development.stronghold,
            Affinity.uncommon,
        ),  # Fortifications they serve dragons in
    ],
)
