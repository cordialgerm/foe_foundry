from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import HideArmor
from ...attack_template import AttackTemplate, weapon
from ...creature_types import CreatureType
from ...damage import DamageType
from ...movement import Movement
from ...powers import PowerSelection
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from .._template import GenerationSettings, Monster, MonsterTemplate, MonsterVariant
from ..base_stats import base_stats
from . import powers

FrostGiantVariant = MonsterVariant(
    name="Frost Giant",
    description="Frost giants are towering, cold-hearted warriors from the frozen wastes.",
    monsters=[
        Monster(
            name="Frost Giant Reaver",
            cr=8,
            srd_creatures=["Frost Giant"],
        ),
    ],
)


class _FrostGiantTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        return PowerSelection([powers.LoadoutFrostGiant])

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr

        # STATS (matching comments for CR 8)
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=[
                Stats.STR.scaler(StatScaling.Primary, mod=6),  # 22 (+6)
                Stats.DEX.scaler(StatScaling.Default, -1),  # 8 (-1)
                Stats.CON.scaler(StatScaling.Constitution, 5),  # 20 (+5)
                Stats.INT.scaler(StatScaling.Default),  # 10 (+0)
                Stats.WIS.scaler(StatScaling.Default),  # 10 (+0)
                Stats.CHA.scaler(StatScaling.Default, mod=1),  # 12 (+1)
            ],
            hp_multiplier=settings.hp_multiplier * 1.0,  # Will be tuned to match 138 HP
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Giant,
            size=Size.Huge,
            languages=["Common", "Giant"],
            creature_class="Frost Giant",
            senses={"passive_perception": 14},
            speed=Movement(walk=40),
            damage_immunities={DamageType.Cold},
        )

        # AC
        stats = stats.add_ac_template(HideArmor)

        # ROLES
        stats = stats.with_roles(primary_role=MonsterRole.Bruiser)

        # SAVES
        stats = stats.grant_save_proficiency(Stats.STR, Stats.CON, Stats.WIS, Stats.CHA)

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(
            Skills.Athletics, Skills.Perception, Skills.Survival
        )

        # ATTACKS (stub)
        attack = weapon.Greataxe.with_display_name("Frost Greataxe").copy(reach=10)

        return stats, [attack]


FrostGiantTemplate: MonsterTemplate = _FrostGiantTemplate(
    name="Frost Giant",
    tag_line="Towering warriors of the frozen wastes",
    description="Frost giants are massive, cold-hearted warriors who thrive in icy realms.",
    variants=[FrostGiantVariant],
    treasure=[],
    species=[],
)
