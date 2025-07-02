from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import LeatherArmor, SplintArmor
from ...attack_template import AttackTemplate, natural, weapon
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die
from ...powers import PowerSelection
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from ..species import AllSpecies, HumanSpecies
from . import powers

ThugVariant = MonsterVariant(
    name="Thug",
    description="Thugs might work in groups at the direction of a leader, or individual toughs might bully weaker folk into doing what they say.",
    monsters=[
        Monster(name="Thug", cr=0.5, srd_creatures=["Thug", "Tough"]),
        Monster(name="Veteran Thug", cr=2),
        Monster(name="Elite Thug", cr=4),
    ],
)
BrawlerVariant = MonsterVariant(
    name="Brawler",
    description="Brawlers rely on their physical strength and intimidation to get what they want. They might be bouncers, enforcers, or just rowdy tavern goers.",
    monsters=[
        Monster(name="Brawler", cr=1),
    ],
)
BossVariant = MonsterVariant(
    name="Boss",
    description="Thug bosses leverage their street smarts, brawling prowess, and reputation to compel others to follow their demands.",
    monsters=[
        Monster(name="Thug Boss", cr=2, other_creatures={"Tough Boss": "mm25"}),
        Monster(name="Thug Overboss", cr=4),
        Monster(name="Thug Legend", cr=8, is_legendary=True),
    ],
)


class _ToughTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "thug":
            return PowerSelection(powers.LoadoutThug)
        elif settings.monster_key == "veteran-thug":
            return PowerSelection(powers.LoadoutVeteranThug)
        elif settings.monster_key == "elite-thug":
            return PowerSelection(powers.LoadoutEliteThug)
        elif settings.monster_key == "brawler":
            return PowerSelection(powers.LoadoutBrawler)
        elif settings.monster_key == "thug-boss":
            return PowerSelection(powers.LoadoutThugBoss)
        elif settings.monster_key == "thug-overboss":
            return PowerSelection(powers.LoadoutThugOverboss)
        elif settings.monster_key == "thug-legend":
            return PowerSelection(powers.LoadoutThugLegend)
        else:
            raise ValueError(f"Unknown monster key: {settings.monster_key}")

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
                Stats.DEX.scaler(StatScaling.Medium, 0.5),
                Stats.INT.scaler(StatScaling.Default, mod=-1),
                Stats.WIS.scaler(StatScaling.Default),
                Stats.CHA.scaler(StatScaling.Medium),
            ],
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        # LEGENDARY
        if is_legendary:
            stats = stats.as_legendary()

        stats = stats.copy(
            creature_type=CreatureType.Humanoid,
            size=Size.Medium,
            languages=["Common"],
            creature_class="Thug",
        )

        # ARMOR CLASS
        if variant is BossVariant:
            stats = stats.add_ac_template(SplintArmor, ac_modifier=1 if cr >= 4 else 0)
        else:
            stats = stats.add_ac_template(LeatherArmor, ac_modifier=1 if cr >= 4 else 0)

        # ATTACKS
        if variant is BrawlerVariant:
            attack = natural.Slam
        else:
            attack = weapon.Maul

        stats = stats.copy(primary_damage_type=attack.damage_type)

        # Toughs with a Mace also have a heavy crossbow
        if attack == weapon.Maul:
            stats = stats.add_attack(
                name="Heavy Crossbow",
                scalar=0.7 * min(stats.multiattack, 2),
                attack_type=AttackType.RangedWeapon,
                range=100,
                damage_type=DamageType.Piercing,
                die=Die.d10,
                replaces_multiattack=2,
            )

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Leader
            if variant is BossVariant
            else MonsterRole.Bruiser,
            additional_roles=[MonsterRole.Bruiser],
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(Skills.Intimidation)

        if stats.cr >= 8:
            stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

        # SAVES
        if cr >= 2:
            stats = stats.grant_save_proficiency(Stats.STR)

        if cr >= 4:
            stats = stats.grant_save_proficiency(Stats.CON, Stats.CHA)

        return stats, [attack]


ToughTemplate: MonsterTemplate = _ToughTemplate(
    name="Tough",
    tag_line="Brawlers and Bullies",
    description="Bodyguards, belligerents, and laborers, toughs rely on their physical strength to intimidate foes. They might be brawny criminals, rowdy tavern goers, seasoned workers, or anyone who uses their muscle to get what they want.",
    environments=["Urban"],
    treasure=["Armaments"],
    variants=[ThugVariant, BrawlerVariant, BossVariant],
    species=AllSpecies,
)
