from foe_foundry.environs import Affinity, Development, ExtraplanarInfluence
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import ArcaneArmor
from ...attack_template import AttackTemplate, spell
from ...creature_types import CreatureType
from ...movement import Movement
from ...powers import PowerSelection, flags
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
from ..base_stats import base_stats
from . import powers

LichVariant = MonsterVariant(
    name="Lich",
    description="Liches are mortal necromancers who defied death, binding their souls to the Mortal Realm through dark rituals and dreadful will. Rather than accept the inevitability of death, they craft soul anchors that lash their spirit in defiance of the natural order. The dark arts necessary to craft such a soul anchor are unique to each twisted soul that contemplates the heinous act, but in each case it involves unspeakably evil acts and cruel sacrifices. Countless aspiring liches have failed, but those who succeed attain unspeakable power.",
    monsters=[
        Monster(name="Lich", cr=21, srd_creatures=["Lich"], is_legendary=True),
        Monster(
            name="Archlich",
            cr=26,
            other_creatures={"Vecna": "Vecna: Eve of Ruin"},
            is_legendary=True,
        ),
    ],
)


class _LichTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "lich":
            return PowerSelection(powers.LoadoutLich)
        elif settings.monster_key == "archlich":
            return PowerSelection(powers.LoadoutArchlich)
        else:
            raise ValueError(
                f"Unknown lich variant: {settings.monster_key}. Expected 'lich' or 'archlich'."
            )

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        is_legendary = settings.is_legendary

        # STATS
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=[
                Stats.STR.scaler(StatScaling.Default, mod=-2),
                Stats.DEX.scaler(StatScaling.Medium),
                Stats.INT.scaler(StatScaling.Primary),
                Stats.CON.scaler(StatScaling.Constitution, mod=-6),
                Stats.WIS.scaler(StatScaling.Medium, mod=-2),
                Stats.CHA.scaler(StatScaling.Medium),
            ],
            hp_multiplier=0.85 * settings.hp_multiplier,
            damage_multiplier=1.1 * settings.damage_multiplier,
        )

        # LEGENDARY
        if is_legendary:
            stats = stats.as_legendary(
                actions=3, resistances=4, boost_powers=False, has_lair=True
            )
            stats = stats.with_flags(
                flags.HAS_TELEPORT
            )  # lich has teleport via legendary action

        stats = stats.copy(
            creature_type=CreatureType.Undead,
            size=Size.Medium,
            languages=["All"],
            creature_class="Lich",
            caster_type=CasterType.Arcane,
            # liches have many bonus actions, reactions, and limited use abilities
            selection_target_args=dict(
                limited_uses_target=-1,
                limited_uses_max=3 if cr <= 11 else 4,
                reaction_target=-1,
                reaction_max=2,
                spellcasting_powers_target=-1,
                spellcasting_powers_max=-1,
                bonus_action_target=-1,
                bonus_action_max=2,
                recharge_target=1,
                recharge_max=1,
            ),
        )

        # SPEED
        if cr >= 12:
            stats = stats.copy(speed=Movement(walk=30, fly=15, hover=True))

        # ARMOR CLASS
        stats = stats.add_ac_template(ArcaneArmor)

        # ATTACKS
        attack = spell.ArcaneBurst.with_display_name("Necrotic Blast")

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Artillery, additional_roles=MonsterRole.Controller
        )

        # SKILLS
        expertise = [Skills.Arcana, Skills.History]
        skills = [Skills.Insight, Skills.Perception]
        stats = (
            stats.grant_proficiency_or_expertise(*skills)
            .grant_proficiency_or_expertise(*expertise)
            .grant_proficiency_or_expertise(*expertise)
        )  # skills and expertise

        # SAVES
        if cr >= 6:
            stats = stats.grant_save_proficiency(
                Stats.DEX, Stats.CON, Stats.INT, Stats.WIS, Stats.CHA
            )

        return stats, [attack]


LichTemplate: MonsterTemplate = _LichTemplate(
    name="Lich",
    tag_line="Immortal Masters of Undeath and Arcana",
    description="Liches are mortal necromancers who defied death, binding their souls to the Mortal Realm through dark rituals and dreadful will. Rather than accept the inevitability of death, they craft soul anchors that lash their spirit in defiance of the natural order. The dark arts necessary to craft such a soul anchor are unique to each twisted soul that contemplates the heinous act, but in each case it involves unspeakably evil acts and cruel sacrifices. Countless aspiring liches have failed, but those who succeed attain unspeakable power.",
    treasure=["Arcana", "Individual"],
    variants=[LichVariant],
    species=[],
    environments=[
        (
            Development.dungeon,
            Affinity.native,
        ),  # Hidden lairs protecting their soul anchors
        (Development.ruin, Affinity.native),  # Ancient tombs and forgotten sanctuaries
        (Development.stronghold, Affinity.common),  # Conquered towers and fortresses
        (
            ExtraplanarInfluence.deathly,
            Affinity.common,
        ),  # Areas touched by necromantic power
        (
            Development.urban,
            Affinity.uncommon,
        ),  # Hidden beneath cities, plotting in shadows
        (
            Development.wilderness,
            Affinity.rare,
        ),  # Remote locations for dark experiments
    ],
)
