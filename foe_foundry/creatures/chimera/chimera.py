from foe_foundry.environs import Affinity, Development, region
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import NaturalArmor
from ...attack_template import AttackTemplate, natural
from ...creature_types import CreatureType
from ...movement import Movement
from ...powers import (
    PowerSelection,
    flags,
)
from ...role_types import MonsterRole
from ...size import Size
from ...skills import AbilityScore, Skills, StatScaling
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

ChimeraVariant = MonsterVariant(
    name="Chimera",
    description="Legends say that chimera are heralds of imminent divine wrath or impending disaster. The greed, pride, and anger of mortal kind manifests into a monstrous three-headed beast, part lion, ram, and dragon. The lion head craves conquest, the goat hungers for spite, and the dragon seethes with wrath. Scholars debate whether chimeras are creations of wrathful gods, foul demons, or capricious fae. Regardless, the presence of a chimera is a certain sign of disaster.",
    monsters=[
        Monster(name="Chimera", cr=6, srd_creatures=["Chimera"]),
        Monster(name="Chimera Sovereign", cr=10),
    ],
)


class _ChimeraTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "chimera":
            return PowerSelection(powers.LoadoutChimera)
        elif settings.monster_key == "chimera-sovereign":
            return PowerSelection(powers.LoadoutChimeraSovereign)
        else:
            raise ValueError(f"Unknown monster key: {settings.monster_key}")

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
            stats={
                AbilityScore.STR: StatScaling.Primary,
                AbilityScore.DEX: StatScaling.Default,
                AbilityScore.CON: (StatScaling.Constitution, 4),
                AbilityScore.INT: (StatScaling.Default, -8),
                AbilityScore.WIS: (StatScaling.Medium, 2),
                AbilityScore.CHA: (StatScaling.Default, -1.5),
            },
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Monstrosity,
            size=Size.Large,
            creature_class="Chimera",
            languages=["Draconic"],
            senses=stats.senses.copy(darkvision=60),
        )

        # ARMOR CLASS
        stats = stats.add_ac_template(NaturalArmor, ac_modifier=-1)

        # ATTACKS
        attack = natural.Bite.with_display_name("Three-Headed Bites")

        stats = stats.with_set_attacks(3)  # 3 heads = 3 attacks

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Bruiser,
        )

        # MOVEMENT
        stats = stats.with_flags(flags.NO_TELEPORT).copy(
            speed=Movement(walk=30, fly=60)
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(
            Skills.Perception
        ).grant_proficiency_or_expertise(Skills.Perception)  # expertise

        # SAVES
        if stats.cr >= 8:
            stats = stats.grant_save_proficiency(AbilityScore.WIS, AbilityScore.CON)

        return stats, [attack]


ChimeraTemplate: MonsterTemplate = _ChimeraTemplate(
    name="Chimera",
    tag_line="Monstrous Messenger of Imminent Disaster",
    description="Legends say that chimera are heralds of imminent divine wrath or impending disaster. The greed, pride, and anger of mortal kind manifests into a monstrous three-headed beast, part lion, ram, and dragon. The lion head craves conquest, the goat hungers for spite, and the dragon seethes with wrath. Scholars debate whether chimeras are creations of wrathful gods, foul demons, or capricious fae. Regardless, the presence of a chimera is a certain sign of disaster.",
    treasure=[],
    environments=[
        (
            region.BlastedBadlands,
            Affinity.native,
        ),  # herald disaster in devastated lands
        (region.HauntedLands, Affinity.native),  # appear where corruption manifests
        (Development.wilderness, Affinity.common),  # found in remote, dangerous areas
        (Development.ruin, Affinity.common),  # manifest where civilizations have fallen
        (region.LoftyMountains, Affinity.common),  # lair in remote mountain peaks
        (
            Development.frontier,
            Affinity.uncommon,
        ),  # herald disaster for frontier settlements
        (
            region.WartornKingdom,
            Affinity.uncommon,
        ),  # appear during times of great conflict
        (Development.settlement, Affinity.rare),  # rarely approach populated areas
    ],
    variants=[ChimeraVariant],
    species=[],
)
