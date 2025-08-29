from foe_foundry.environs import (
    Affinity,
    Biome,
    Development,
    ExtraplanarInfluence,
    region,
)

from ...ac_templates import UnholyArmor
from ...attack_template import AttackTemplate, weapon
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...movement import Movement
from ...powers import PowerSelection
from ...role_types import MonsterRole
from ...size import Size
from ...skills import AbilityScore, Skills, StatScaling
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import BaseStatblock, base_stats
from . import powers

BalorVariant = MonsterVariant(
    name="Balor",
    description="Balors embody demons' ruinous fury and hatred. Towering, winged terrors, these demonic warlords seethe with wrath, their rage erupting in waves of fire and as a pair of vicious weapons: a sword of crackling lightning and a whip of lashing flames.",
    monsters=[
        Monster(name="Balor", cr=19, srd_creatures=["Balor"]),
    ],
)

BalorGeneralVariant = MonsterVariant(
    name="Balor General",
    description="A balor general is a balor that has been granted the title of general by a demon lord. It is a powerful and respected leader among demons, commanding legions of lesser demons in the name of its master.",
    monsters=[
        Monster(name="Balor Dreadlord", cr=23, is_legendary=True),
    ],
)


class _BalorTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == 'balor':
            return PowerSelection(powers.LoadoutBalor)
        elif settings.monster_key == 'balor-dreadlord':
            return PowerSelection(powers.LoadoutBalorGeneral)
        else:
            raise ValueError(f"Unknown monster_key: {settings.monster_key}")

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
            stats={
                AbilityScore.STR: StatScaling.Primary,
                AbilityScore.DEX: (StatScaling.Medium, 1),
                AbilityScore.INT: (StatScaling.Medium, 4),
                AbilityScore.WIS: (StatScaling.Medium, 2),
                AbilityScore.CHA: (StatScaling.Medium, 6),
            },
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Fiend,
            languages=["Abyssal; telepathy 120 ft."],
            creature_class="Balor",
            creature_subtype="Demon",
            senses=stats.senses.copy(truesight=120),
            size=Size.Huge,
            speed=Movement(walk=40, fly=80),
        )

        # LEGENDARY
        if is_legendary:
            stats = stats.as_legendary()

        # ARMOR CLASS
        stats = stats.add_ac_template(UnholyArmor)

        # ATTACKS
        attack = weapon.Greatsword.with_display_name("Lightning Blade").copy(
            damage_type=DamageType.Lightning, split_secondary_damage=False
        )
        stats = stats.copy(
            secondary_damage_type=DamageType.Fire,
        )

        ## ATTACK DAMAGE

        # lowering attacks on a legendary creature messes up formulas
        stats = stats.with_set_attacks(3)

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Bruiser,
            additional_roles=[MonsterRole.Soldier, MonsterRole.Leader],
        )

        # SAVES
        stats = stats.grant_save_proficiency(AbilityScore.CON, AbilityScore.WIS)

        # IMMUNITIES
        stats = stats.grant_resistance_or_immunity(
            immunities={DamageType.Fire, DamageType.Poison},
            resistances={DamageType.Cold, DamageType.Lightning},
            conditions={Condition.Poisoned, Condition.Frightened, Condition.Poisoned},
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(
            Skills.Perception, Skills.Initiative
        )
        stats = stats.grant_proficiency_or_expertise(Skills.Initiative)  # expertise

        return stats, [attack]


BalorTemplate: MonsterTemplate = _BalorTemplate(
    name="Balor",
    tag_line="Demon of Overwhelming Rage",
    description="Balors embody demons' ruinous fury and hatred. Towering, winged terrors, these demonic warlords seethe with wrath, their rage erupting in waves of fire and as a pair of vicious weapons: a sword of crackling lightning and a whip of lashing flames. Demon lords and evil gods harness balors' rage by making balors commanders of armies or guardians of grave secrets.",
    treasure=[],
    environments=[
        (
            ExtraplanarInfluence.hellish,
            Affinity.native,
        ),  # native to hellish planes and demonic realms
        (Biome.extraplanar, Affinity.native),  # from extraplanar demonic dimensions
        (
            region.FieryHellscape,
            Affinity.native,
        ),  # thrive in volcanic and hellish regions
        (
            Development.ruin,
            Affinity.common,
        ),  # found in places of great evil and destruction
        (region.HauntedLands, Affinity.uncommon),  # sometimes manifest in cursed places
        (
            Development.wilderness,
            Affinity.rare,
        ),  # rarely appear in mortal realm wilderness
    ],
    variants=[BalorVariant, BalorGeneralVariant],
    species=[],
)
