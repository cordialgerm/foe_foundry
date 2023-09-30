from math import ceil

import numpy as np

from foe_foundry.statblocks import BaseStatblock

from ..ac_templates import NaturalArmor
from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..senses import Senses
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from .template import CreatureTypeTemplate


class _ConstructTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Construct", creature_type=CreatureType.Construct)

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        # have either blindsight or darkvision, and a selection of
        # damage immunities and condition immunities to reflect
        # their nonliving nature. They usually can’t speak, but might
        # understand one or more languages.

        # A construct’s strongest ability scores are usually Strength and Constitution
        stats = stats.scale(
            {
                Stats.STR: Stats.Primary(),
                Stats.DEX: Stats.Scale(8, 1 / 3),
                Stats.INT: Stats.Scale(4, 1 / 3),
                Stats.WIS: Stats.Scale(8, 1 / 4),
                Stats.CHA: Stats.Scale(2, 1 / 3),
            }
        )
        new_attributes = stats.attributes

        # Damage Immunities poison, psychic
        # Condition Immunities blinded, charmed, deafened,
        # exhaustion, frightened, paralyzed, petrified, poisoned
        stats = stats.grant_resistance_or_immunity(
            immunities={
                DamageType.Poison,
                DamageType.Psychic,
            },
            nonmagical_resistance=stats.cr >= 7,
            conditions={
                Condition.Exhaustion,
                Condition.Frightened,
                Condition.Paralyzed,
                Condition.Petrified,
                Condition.Poisoned,
            },
        )

        # Senses blindsight 60 ft. (blind beyond this radius) or
        # darkvision 60 ft.
        if stats.cr <= 7:
            new_senses = Senses(darkvision=60)
        else:
            new_senses = Senses(blindsight=60)

        # Constructs attack with melee weapons like swords
        attack_type = AttackType.MeleeWeapon
        primary_damage_type = DamageType.Slashing

        # Constructs often have an elemental damage type associated with them
        damage_types = [
            DamageType.Fire,
            DamageType.Cold,
            DamageType.Lightning,
            DamageType.Poison,
            DamageType.Acid,
        ]
        i = rng.choice(len(damage_types))
        secondary_damage_type = damage_types[i]

        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=rng)

        # constructs with higher CR should have proficiency in STR and CON saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR, Stats.CON)

        # constructs are heavily armored
        ac_bonus = min(ceil(stats.cr / 5), 3)
        stats = stats.add_ac_template(NaturalArmor, ac_modifier=ac_bonus)

        return stats.copy(
            creature_type=CreatureType.Construct,
            attributes=new_attributes,
            size=size,
            languages=None,
            senses=new_senses,
            primary_damage_type=primary_damage_type,
            secondary_damage_type=secondary_damage_type,
            attack_type=attack_type,
        )


ConstructTemplate: CreatureTypeTemplate = _ConstructTemplate()
