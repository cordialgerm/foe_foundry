from typing import Set, Tuple, TypeAlias

from numpy.random import Generator

from ..creature_types import CreatureType
from ..die import Die, DieFormula

MonsterInfo: TypeAlias = Tuple[str, float]
SummoningList: TypeAlias = Set[MonsterInfo]

Elementals: SummoningList = {
    ("*Smoke Mephit*", 1 / 4),
    ("*Magma Mephit*", 1 / 2),
    ("*Azer*", 2),
    ("*Salamander*", 5),
    ("*Earth Elemental*", 5),
    ("*Fire Elemental*", 5),
    ("*Air Elemental*", 5),
    ("*Water Elemental*", 5),
}

Fiends: SummoningList = {
    ("*Lemure*", 1 / 10),  # CR0 but don't want to divide 1/0
    ("*Dretch*", 1 / 4),
    ("*Imp*", 1),
    ("*Quasit*", 1),
    ("*Hell Hound*", 3.5),  # CR3 but pretty strong
    ("*Incubus*", 4),
    ("*Sucubus*", 4),
}

Fey: SummoningList = {
    ("*Blink Dog*", 1 / 4),
    ("*Pixie*", 1 / 2),  # CR 1/4 but pretty strong...
    ("*Sprite*", 1 / 4),
    ("*Dryad*", 1),
    ("*Green Hag*", 3),
}

Monstrosities: SummoningList = {
    ("*Rust Monster*", 1 / 2),
    ("*Cockatrice*", 1 / 2),
    ("*Death Dog*", 1),
    ("*Ettercap*", 2),
    ("*Basilisk*", 3),
    ("*Phase Spider*", 3),
    ("*Roper*", 5),
}

Aberrations: SummoningList = {("*Giberring Mouther*", 2), ("*Otyugh*", 5)}

DraconicMinions: SummoningList = {
    ("*Kobold*", 1 / 8),
    ("*Goblin*", 1 / 4),
    ("*Veteran*", 3),
    ("*Wyvern*", 6),
}

DraconicWyrmlings: SummoningList = {
    ("*White Dragon Wyrmling*", 2),
    ("*Blue Dragon Wyrmling*", 3),
    ("*Black Dragon Wyrmling*", 2),
    ("*Green Dragon Wyrmling*", 2),
    ("*Red Dragon Wymrling*", 4),
}


FlyingBeasts: SummoningList = {
    ("*Swarm of Bats*", 1 / 4),
    ("*Giant Eagle*", 1),
}

SwimmingBeasts: SummoningList = {
    ("*Swarm of Quippers*", 1),
    ("*Hunter Shark*", 2),
    ("*Killer Whale*", 3),
}

LandBeasts: SummoningList = {
    ("*Swarm of Rats*", 1 / 4),
    ("*Dire Wolf*", 1),
    ("*Polar Bear*", 2),
}


def summon_list_for_creature(
    creature_type: CreatureType, use_default: bool = False
) -> SummoningList | None:
    default_list = Elementals | Fiends | Fey

    if creature_type == CreatureType.Dragon:
        options = DraconicMinions | DraconicWyrmlings
    elif creature_type == CreatureType.Aberration:
        options = Aberrations
    elif creature_type == CreatureType.Beast:
        options = LandBeasts | SwimmingBeasts | FlyingBeasts
    elif creature_type == CreatureType.Elemental:
        options = Elementals
    elif creature_type == CreatureType.Fey:
        options = Fey
    elif creature_type == CreatureType.Fiend:
        options = Fiends
    elif creature_type == CreatureType.Humanoid:
        options = default_list
    elif creature_type == CreatureType.Monstrosity:
        options = Monstrosities
    else:
        options: Set[MonsterInfo] = set()

    if use_default:
        options = options | default_list

    return options


def determine_summon_formula(
    summon_list: SummoningList | CreatureType | None,
    summon_cr_target: float,
    rng: Generator,
    max_quantity: int = 20,
) -> Tuple[str, DieFormula, str]:
    """Selects a creature to summon and determines the correct quantity to summon to reach a desired CR target."""

    if isinstance(summon_list, CreatureType):
        summon_list = summon_list_for_creature(summon_list, use_default=True)

    if summon_list is None or len(summon_list) == 0:
        raise ValueError("summon_list is required")

    names, formulas = [], []
    for creature, cr in summon_list:
        target_val = summon_cr_target / cr
        if target_val < 1.0 or target_val > max_quantity:
            continue
        elif target_val <= 2:
            quantity = int(round(target_val))
            formula = DieFormula.from_expression(str(quantity))
        else:
            # if there are 3 or more minions being summoned then use a d4 dice formula
            formula = DieFormula.target_value(target_val, force_die=Die.d4)

        formulas.append(formula)
        names.append(creature)

    index = rng.choice(len(names))
    creature = names[index]
    formula = formulas[index]

    description = f"{formula.description} {creature} arrive to aid the summoner and join combat at initiative count 0. \
         On their first turn, they use their action to dash into position and act normally on subsequent turns."

    return creature, formula, description
