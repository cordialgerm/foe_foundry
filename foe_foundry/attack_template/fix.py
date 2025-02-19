from ..damage import Attack, AttackType, Damage, DamageType
from ..die import Die, DieFormula
from ..size import Size
from ..statblocks.base import BaseStatblock


# helper function to repair an attack
def adjust_attack(
    *,
    stats: BaseStatblock,
    attack: Attack,
    attack_name: str | None = None,
    attack_display_name: str | None = None,
    attack_type: AttackType | None = None,
    primary_damage_type: DamageType | None = None,
    die: Die,
    min_die_count: int = 0,
    adjust_to_hit: bool = False,
    adjust_average_damage: bool = False,
    reach: int | None = None,
    range: int | None = None,
    range_max: int | None = None,
    reach_bonus_for_huge: bool = False,
    range_bonus_for_high_cr: bool = False,
) -> Attack:
    args: dict = {}

    if attack_name is not None:
        args.update(name=attack_name)

    if attack_display_name is not None:
        args.update(display_name=attack_display_name)

    # update attack type
    if attack_type is not None:
        args.update(attack_type=attack_type)

    if reach is None and reach_bonus_for_huge and stats.size >= Size.Huge:
        reach = 10
    elif reach is not None and reach_bonus_for_huge and stats.size >= Size.Huge:
        reach += 5

    if reach is not None:
        args.update(reach=reach)

    if range is None and range_bonus_for_high_cr and stats.cr >= 7:
        range = 90
    elif range is not None and range_bonus_for_high_cr and stats.cr >= 7:
        range += 30
        if range_max is not None:
            range_max += 30

    if range is not None:
        args.update(range=range)

    if range_max is not None:
        args.update(range_max=range_max)

    # repair attack to-hit and damage formula
    if adjust_to_hit:
        repaired_hit = stats.attributes.proficiency + stats.attributes.primary_mod
        args.update(hit=repaired_hit)

    # adjust the average damage based on the primary stat mod
    if adjust_average_damage:
        average_damage = attack.damage.formula.average
        repaired_formula = DieFormula.target_value(
            target=average_damage * stats.damage_modifier,
            flat_mod=stats.attributes.primary_mod,
            force_die=die,
            min_die_count=min_die_count,
        )
    else:
        repaired_formula = attack.damage.formula.copy()

    if stats.cr <= 2:
        low_cr_average_damage = {
            1 / 8: 4.5,
            1 / 4: 5.5,
            1 / 2: 4.5 * 2,  # two multiattacks
            1: 6.5 * 2,  # two multiattacks
            2: 9 * 2,  # two multiattacks
        }
        average_damage_output = repaired_formula.average * stats.multiattack
        target_damage_output = low_cr_average_damage[stats.cr]

        # if this is a low-CR creature and our damage is still too big then we should reduce it
        # this happens a lot with CR 1/2 or CR2 creatures that have big damage-die weapons
        if average_damage_output >= 1.1 * target_damage_output:
            new_target = target_damage_output / stats.multiattack
            repaired_formula = DieFormula.target_value(
                target=new_target,
                flat_mod=stats.attributes.primary_mod,
                suggested_die=die,
                min_die_count=1,
            )

    damage_type = (
        primary_damage_type
        if primary_damage_type is not None
        else attack.damage.damage_type
    )
    repaired_damage = Damage(formula=repaired_formula, damage_type=damage_type)
    args.update(damage=repaired_damage)

    new_attack = attack.copy(**args)
    return new_attack
