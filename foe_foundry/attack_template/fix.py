from ..damage import Attack, AttackType, Damage, DamageType
from ..die import Die, DieFormula
from ..size import Size
from ..statblocks.base import BaseStatblock


# helper function to repair an attack
def adjust_attack(
    stats: BaseStatblock,
    attack: Attack,
    attack_name: str | None = None,
    attack_type: AttackType | None = None,
    primary_damage_type: DamageType | None = None,
    die: Die | None = None,
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

        if die is None:
            die_args: dict = dict(suggested_die=attack.damage.formula.primary_die_type)
        else:
            die_args: dict = dict(force_die=die)

        repaired_formula = DieFormula.target_value(
            target=average_damage, flat_mod=stats.attributes.primary_mod, **die_args
        )
    else:
        repaired_formula = attack.damage.formula.copy(mod=stats.attributes.primary_mod)

    damage_type = (
        primary_damage_type if primary_damage_type is not None else attack.damage.damage_type
    )
    repaired_damage = Damage(formula=repaired_formula, damage_type=damage_type)
    args.update(damage=repaired_damage)

    new_attack = attack.copy(**args)
    return new_attack