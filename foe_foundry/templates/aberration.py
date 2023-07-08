import numpy as np

from ..attributes import Stats
from ..creature_types import CreatureType
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock

rng = np.random.default_rng(20210518)


def as_aberration(stats: BaseStatblock) -> BaseStatblock:
    primary_stats = [Stats.CHA, Stats.INT, Stats.WIS]
    stat_weights = [0.6, 0.3, 0.1]
    primary_stat_indx = rng.choice(3, p=stat_weights)
    primary_stat = primary_stats[primary_stat_indx]

    size = get_size_for_cr(cr=stats.cr, standard_size=Size.Medium, rng=rng)

    new_senses = stats.senses.copy(darkvision=120)

    # Aberrations generally have high mental stats
    # this means the minimum stat value should be 12 for mental stats
    # we should also boost mental stat scores
    # cap the max mental stat score at its primary score though
    mins = {Stats.CHA: 12, Stats.INT: 12, Stats.WIS: 12}
    bonuses = {Stats.CHA: 2, Stats.INT: 2, Stats.WIS: 2}
    new_attributes = stats.attributes.update_ranges(
        mins=mins, maxs=stats.primary_attribute_score, bonuses=bonuses
    )

    return stats.copy(
        creature_type=CreatureType.Aberration,
        size=size,
        languages=["Deep Speech", "telepathy 120 ft."],
        senses=new_senses,
        primary_attribute=primary_stat,
        attributes=new_attributes,
    )
