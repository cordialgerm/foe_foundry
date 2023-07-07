import pytest

from foundry_of_foes import (
    BaseStatblock,
    MonsterDials,
    Stats,
    as_ambusher_cycle,
    as_artillery_cycle,
    as_bruiser_cycle,
    general_use_stats,
)


@pytest.mark.parametrize("stats", general_use_stats.All)
def test_minion(stats: BaseStatblock):
    ## as ambusher
    ambusher1 = as_ambusher_cycle(stats)
    ambusher2 = as_ambusher_cycle(stats)

    artillery1 = as_artillery_cycle(stats)
    artillery2 = as_artillery_cycle(stats)
    artillery3 = as_artillery_cycle(stats)
    artillery4 = as_artillery_cycle(stats)

    ## as bruiser
    bruiser1 = as_bruiser_cycle(stats)
    bruiser2 = as_bruiser_cycle(stats)
    bruiser3 = as_bruiser_cycle(stats)

    ## as controller
    dials = [
        MonsterDials(attack_damage_modifier=-1, difficulty_class_modifier=2),
    ]
    controller1 = stats.apply_monster_dials(dials[0])

    ## defender
    ## TODO - make proficient in saving throws
    save_proficiencies = dict(proficient_saves=set(Stats.All()))
    dials = [
        MonsterDials(
            ac_modifier=3, attack_hit_modifier=-2, attribute_modifications=save_proficiencies
        ),
        MonsterDials(
            ac_modifier=3,
            attack_hit_modifier=-1,
            attack_damage_dice_modifier=-1,
            attribute_modifications=save_proficiencies,
        ),
        MonsterDials(
            hp_multiplier=1.3,
            attack_hit_modifier=-2,
            attribute_modifications=save_proficiencies,
        ),
        MonsterDials(
            hp_multiplier=1.3,
            attack_hit_modifier=-1,
            attack_damage_dice_modifier=-1,
            attribute_modifications=save_proficiencies,
        ),
    ]
    defender1 = stats.apply_monster_dials(dials[0])
    defender2 = stats.apply_monster_dials(dials[1])
    defender3 = stats.apply_monster_dials(dials[2])
    defender4 = stats.apply_monster_dials(dials[3])

    ## leader
    dials = [
        MonsterDials(attack_hit_modifier=-2, recommended_powers_modifier=1),
        MonsterDials(hp_multiplier=0.8, recommended_powers_modifier=1),
        MonsterDials(attack_damage_dice_modifier=-1, recommended_powers_modifier=1),
    ]
    leader1 = stats.apply_monster_dials(dials[0])
    leader2 = stats.apply_monster_dials(dials[0])
    leader3 = stats.apply_monster_dials(dials[0])

    ## skirmisher
    dials = [
        MonsterDials(ac_modifier=-2, speed_modifier=20),
        MonsterDials(hp_multiplier=0.8, speed_modifier=20),
    ]
    skirmisher1 = stats.apply_monster_dials(dials[0])
    skirmisher2 = stats.apply_monster_dials(dials[1])
