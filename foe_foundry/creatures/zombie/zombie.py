from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import Unarmored
from ...attack_template import AttackTemplate, natural
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...powers import PowerSelection
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Stats, StatScaling
from ...statblocks import MonsterDials
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

ZombieVariant = MonsterVariant(
    name="Zombie",
    description="Humanoid zombies usually serve as guardians, servants, or soldiers for evil magic-users. In rare cases, foul magic might result in widespread reanimation of the dead, unleashing hordes of zombies to terrorize the living.",
    monsters=[
        Monster(name="Zombie", cr=1 / 4, srd_creatures=["Zombie"]),
        Monster(name="Zombie Brute", cr=1),
        Monster(name="Zombie Gravewalker", cr=3),
    ],
)

ZombieOgreVariant = MonsterVariant(
    name="Zombie Ogre",
    description="Ogre zombies serve as tireless labor and undying weapons of war. These massive zombies possess the size and strength to break through barriers that repel smaller zombies.",
    monsters=[
        Monster(name="Zombie Ogre", cr=2, srd_creatures=["Ogre Zombie"]),
        Monster(name="Zombie Giant", cr=8),
        Monster(name="Zombie Titan", cr=12, is_legendary=True),
    ],
)


class _ZombieTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        variant = settings.variant
        cr = settings.cr

        if variant is ZombieVariant:
            if cr < 1:
                return PowerSelection(loadouts=powers.LoadoutZombie)
            else:
                return PowerSelection(loadouts=powers.LoadoutZombieBrute)
        elif variant is ZombieOgreVariant:
            if cr <= 2:
                return PowerSelection(loadouts=powers.LoadoutZombieOgre)
            else:
                return PowerSelection(loadouts=powers.LoadoutZombieGiant)
        else:
            raise ValueError(f"Unknown zombie variant: {variant.name}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        variant = settings.variant
        rng = settings.rng
        is_legendary = settings.is_legendary

        # STATS
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=[
                Stats.STR.scaler(StatScaling.Primary),
                Stats.DEX.scaler(StatScaling.Default, mod=-4),
                Stats.CON.scaler(StatScaling.Constitution, mod=4),
                Stats.INT.scaler(StatScaling.Default, mod=-7),
                Stats.WIS.scaler(StatScaling.Default, mod=-4),
                Stats.CHA.scaler(StatScaling.Default, mod=-5),
            ],
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )

        # LEGENDARY
        if is_legendary:
            stats = stats.as_legendary()

        stats = stats.copy(
            creature_type=CreatureType.Undead,
            languages=["Understands Common but can't speak"],
            creature_class="Zombie",
            senses=stats.senses.copy(darkvision=60),
        )

        # SIZE
        if variant is ZombieOgreVariant:
            size = Size.Huge if stats.cr >= 8 else Size.Large
        else:
            size = Size.Medium
        stats = stats.copy(size=size)

        # SPEED

        if variant is ZombieVariant:
            stats = stats.copy(speed=stats.speed.delta(-10))

        # Zombies don't use special movement so set this flag
        stats = stats.copy(has_unique_movement_manipulation=True)

        # ARMOR CLASS
        stats = stats.add_ac_template(Unarmored)

        # ATTACKS
        attack = natural.Slam.with_display_name(
            "Rotten Grasp"
        ).copy(
            split_secondary_damage=False  # zombies should be associated with poison but don't split damage to poison
        )
        secondary_damage_type = DamageType.Poison

        stats = stats.copy(
            secondary_damage_type=secondary_damage_type,
        )

        ## ATTACK DAMAGE
        # zombies should have fewer attacks, but the attacks should hit hard!
        stats = stats.with_reduced_attacks(reduce_by=1 if stats.cr <= 8 else 2)

        # ROLES
        stats = stats.with_roles(
            primary_role=MonsterRole.Bruiser, additional_roles=MonsterRole.Soldier
        )

        # SAVES
        stats = stats.grant_save_proficiency(Stats.WIS)
        if stats.cr >= 4:
            stats = stats.grant_save_proficiency(Stats.CON)

        # IMMUNITIES
        stats = stats.grant_resistance_or_immunity(
            immunities={DamageType.Poison},
            conditions={Condition.Poisoned},
            vulnerabilities={DamageType.Radiant},
        )

        ## HP
        hp_multiplier = 1.3 if stats.cr <= 1 else 1.5
        stats = stats.apply_monster_dials(MonsterDials(hp_multiplier=hp_multiplier))

        return stats, [attack]


ZombieTemplate: MonsterTemplate = _ZombieTemplate(
    name="Zombie",
    tag_line="Relentless Reanimated Corpses",
    description="Zombies are unthinking, reanimated corpses, often gruesomely marred by decay and lethal traumas. They serve whatever supernatural force animates them—typically evil necromancers or fiendish spirits. Zombies are relentless, merciless, and resilient, and their dead flesh can carry on even after suffering grievous wounds.",
    treasure=[],
    variants=[ZombieVariant, ZombieOgreVariant],
    species=[],
)
