from foe_foundry.statblocks import BaseStatblock

from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from .template import CreatureTypeTemplate


class _AberrationTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Aberration", creature_type=CreatureType.Aberration)

    def apply(self, stats: BaseStatblock) -> BaseStatblock:
        # Aberrations generally have high mental stats
        # this means the minimum stat value should be 12 for mental stats
        # we should also boost mental stat scores
        # cap the max mental stat score at its primary score though
        mins = {Stats.CHA: 12, Stats.INT: 12, Stats.WIS: 12}
        bonuses = {Stats.CHA: 2, Stats.INT: 2, Stats.WIS: 2}
        new_attributes = stats.attributes.update_ranges(
            mins=mins, maxs=stats.primary_attribute_score, bonuses=bonuses
        )
        primary_stats = [Stats.CHA, Stats.INT, Stats.WIS]
        stat_weights = [0.6, 0.3, 0.1]
        primary_stat_indx = self.rng.choice(3, p=stat_weights)
        primary_stat = primary_stats[primary_stat_indx]

        new_senses = stats.senses.copy(darkvision=120)
        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Medium, rng=self.rng)

        attack_types = [AttackType.MeleeNatural, AttackType.RangedSpell]
        attack_weights = [0.6, 0.4]
        attack_indx = self.rng.choice(2, p=attack_weights)
        attack_type = attack_types[attack_indx]

        primary_damage_type = (
            DamageType.Bludgeoning
            if attack_type == AttackType.MeleeNatural
            else DamageType.Psychic
        )
        secondary_damage_type = DamageType.Psychic

        return stats.copy(
            creature_type=CreatureType.Aberration,
            size=size,
            languages=["Deep Speech", "telepathy 120 ft."],
            senses=new_senses,
            primary_attribute=primary_stat,
            attributes=new_attributes,
            primary_damage_type=primary_damage_type,
            secondary_damage_type=secondary_damage_type,
            attack_type=attack_type,
        )


AberrationTemplate: CreatureTypeTemplate = _AberrationTemplate()