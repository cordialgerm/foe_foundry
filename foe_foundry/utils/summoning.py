from typing import List, Set, Tuple, TypeAlias

import numpy as np
from numpy.random import Generator

from ..creature_types import CreatureType
from ..damage import DamageType
from ..die import Die, DieFormula

MonsterInfo: TypeAlias = Tuple[str, float]
SummoningList: TypeAlias = Set[MonsterInfo]
SummonerInfo: TypeAlias = SummoningList | CreatureType | DamageType

Fire: SummoningList = {
    ("*Magma Mephit*", 1 / 2),
    ("*Hell Hound*", 3),
    ("*Fire Elemental*", 5),
}

Cold: SummoningList = {
    ("*Steam Elemental*", 1 / 4),
    ("*Winter Wolf*", 3),
    ("*Young White Dragon*", 6),
}

Earth: SummoningList = {
    ("*Dust Mephit*", 1 / 2),
    ("*Azer*", 2),
    ("*Earth Elemental*", 5),
}

Air: SummoningList = {
    ("*Steam Mephit*", 1 / 4),
    ("*Giant Eagle*", 1),
    ("*Gargoyle*", 2),
    ("*Dust Devil*", 5),
}

Poison: SummoningList = {("*Gray Ooze*", 1 / 2), ("*Ochre Jelly*", 2), ("*Black Pudding*", 4)}

Elementals: SummoningList = {
    ("*Smoke Mephit*", 1 / 4),
    ("*Steam Mephit*", 1 / 4),
    ("*Magma Mephit*", 1 / 2),
    ("*Gargoyle*", 2),
    ("*Air Elemental*", 5),
    ("*Water Elemental*", 5),
    ("*Earth Elemental*", 5),
    ("*Fire Elemental*", 5),
    ("*Dust Devil*", 5),
}

Undead: SummonerInfo = {("*Skeleton*", 1 / 4), ("*Ghoul*", 1), ("*Mummy*", 3), ("*Ghost*", 4)}

Celestials: SummonerInfo = {
    ("*Giant Eagle*", 1),
    ("*Pegasus*", 2),
    ("*Couatl*", 5),  # CR 4 but they have a spell list so get fewer of them
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


def summon_list_for_creature_type(creature_type: CreatureType) -> SummoningList:
    default_list = Elementals | Fiends | Fey | Undead

    if creature_type == CreatureType.Dragon:
        return DraconicMinions | DraconicWyrmlings
    elif creature_type == CreatureType.Aberration:
        return Aberrations
    elif creature_type == CreatureType.Beast:
        return LandBeasts | SwimmingBeasts | FlyingBeasts
    elif creature_type == CreatureType.Elemental:
        return Elementals
    elif creature_type == CreatureType.Fey:
        return Fey
    elif creature_type == CreatureType.Fiend:
        return Fiends
    elif creature_type == CreatureType.Humanoid:
        return default_list
    elif creature_type == CreatureType.Monstrosity:
        return Monstrosities
    elif creature_type == CreatureType.Undead:
        return Undead
    elif creature_type == CreatureType.Celestial:
        return Celestials
    else:
        return set()


def summon_list_for_damage_type(damage_type: DamageType) -> SummoningList:
    if damage_type == DamageType.Fire:
        return Fire
    elif damage_type == DamageType.Cold:
        return Cold
    elif damage_type in {DamageType.Acid, DamageType.Poison}:
        return Poison
    elif damage_type in {DamageType.Lightning, DamageType.Thunder}:
        return Air
    elif damage_type == DamageType.Necrotic:
        return Undead
    elif damage_type == DamageType.Psychic:
        return Aberrations
    elif damage_type == DamageType.Radiant:
        return Celestials
    else:
        return set()


def summon_list(
    summoner: SummonerInfo | List[SummonerInfo] | None, use_default: bool = False
) -> SummoningList:
    default_list = Elementals | Fiends | Fey

    if summoner is None and not use_default:
        raise ValueError("summoner is required if use_default=False")

    if summoner is None and use_default:
        return default_list

    if not isinstance(summoner, list):
        infos = [summoner]
    else:
        infos = summoner

    options: SummoningList = set()
    for info in infos:
        if isinstance(info, CreatureType):
            options |= summon_list_for_creature_type(info)
        elif isinstance(info, DamageType):
            options |= summon_list_for_damage_type(info)
        elif isinstance(info, set):
            options |= info

    return options


def determine_summon_formula(
    summoner: SummonerInfo | List[SummonerInfo] | None,
    summon_cr_target: float,
    rng: Generator,
    max_quantity: int = 12,
    allow_generic_summons: bool = False,
) -> Tuple[str, DieFormula, str]:
    """Selects a creature to summon and determines the correct quantity to summon to reach a desired CR target."""

    summons = summon_list(summoner, use_default=allow_generic_summons)

    if len(summons) == 0:
        raise ValueError(f"No summons available for {summoner}")

    names, formulas, weights = [], [], []
    for creature, cr in summons:
        target_val = summon_cr_target / cr
        if target_val < 1.0:
            continue
        if target_val > max_quantity:
            target_val = max_quantity
            weight = 0.5  # prefer not to use this option if we can

        if target_val <= 2:
            quantity = int(round(target_val))
            formula = DieFormula.from_expression(str(quantity))
            weight = 1
        else:
            # if there are 3 or more minions being summoned then use a d4 dice formula
            formula = DieFormula.target_value(target_val, force_die=Die.d4)
            weight = 1

        formulas.append(formula)
        names.append(creature)
        weights.append(weight)

    weights = np.array(weights) / np.sum(weights)
    index = rng.choice(len(names), p=weights)
    creature = names[index]
    formula = formulas[index]

    description = f"{formula.description} {creature} arrive to aid the summoner and join combat at initiative count 0. \
        On their first turn, the summons use their movement and action to arrive on the battlefield in unoccupied spaces within 30 feet of the summoner. \
        They then act normally on subsequent turns."

    return creature, formula, description
