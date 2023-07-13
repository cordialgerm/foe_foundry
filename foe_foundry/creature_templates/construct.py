from math import floor

from foe_foundry.statblocks import BaseStatblock

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

    def apply(self, stats: BaseStatblock) -> BaseStatblock:
        # have either blindsight or darkvision, and a selection of
        # damage immunities and condition immunities to reflect
        # their nonliving nature. They usually can’t speak, but might
        # understand one or more languages.

        # Damage Immunities poison, psychic
        # Condition Immunities blinded, charmed, deafened,
        # exhaustion, frightened, paralyzed, petrified, poisoned
        # Senses blindsight 60 ft. (blind beyond this radius) or
        # darkvision 60 ft.
        # Languages understands certain languages but can’t speak

        # A construct’s strongest ability scores are usually Strength and Constitution
        primary_stat = Stats.STR

        # Celestials often have resistance to radiant damage,
        # and they might also have resistance to damage from nonmagical attacks
        damage_immunities = stats.damage_immunities | {DamageType.Poison, DamageType.Psychic}
        condition_immunities = stats.condition_immunities | {
            Condition.Exhaustion,
            Condition.Frightened,
            Condition.Paralyzed,
            Condition.Petrified,
            Condition.Poisoned,
        }
        if stats.cr <= 8:
            new_senses = Senses(darkvision=60)
        else:
            new_senses = Senses(blindsight=60)

        if stats.cr <= 8:
            nonmagical_resistance = False
        else:
            nonmagical_resistance = True

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
        i = self.rng.choice(len(damage_types))
        secondary_damage_type = damage_types[i]

        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=self.rng)

        return stats.copy(
            creature_type=CreatureType.Beast,
            size=size,
            languages=None,
            senses=new_senses,
            primary_attribute=primary_stat,
            primary_damage_type=primary_damage_type,
            secondary_damage_type=secondary_damage_type,
            attack_type=attack_type,
            damage_immunities=damage_immunities,
            nonmagical_resistance=nonmagical_resistance,
            condition_immunities=condition_immunities,
        )


ConstructTemplate: CreatureTypeTemplate = _ConstructTemplate()
