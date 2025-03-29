from typing import Iterable

from foe_foundry.references import action_ref

from ...creature_types import CreatureType
from ...features import ActionType, Feature
from ...powers import flags
from ...role_types import MonsterRole
from ...size import Size
from ...spells import CasterType
from ...statblocks import BaseStatblock
from .score import LegendaryActionScore, LegendaryActionType


def move(stats: BaseStatblock) -> Iterable[LegendaryActionScore]:
    fast_roles = {MonsterRole.Skirmisher}
    sneaky_roles = {MonsterRole.Ambusher}

    attacks = [stats.attack]
    attacks += [
        a for a in stats.additional_attacks if a.is_equivalent_to_primary_attack
    ]
    melee_attack = next((a for a in attacks if a.attack_type.is_melee()), None)

    if melee_attack is not None and (
        MonsterRole.Bruiser in stats.additional_roles
        or MonsterRole.Soldier in stats.additional_roles
        or stats.size >= Size.Huge
    ):
        yield LegendaryActionScore(
            feature=Feature(
                name="Charge",
                description=f"{stats.selfref.capitalize()} moves up to half its speed and makes an {melee_attack.display_name} attack.",
                action=ActionType.Legendary,
            ),
            types={LegendaryActionType.move, LegendaryActionType.attack},
            score=6,
        )

    could_teleport = (
        (len(stats.spells) > 0 and stats.caster_type != CasterType.Divine)
        or (stats.creature_type in {CreatureType.Fey, CreatureType.Fiend})
        or (
            len(
                {
                    MonsterRole.Controller,
                    MonsterRole.Artillery,
                    MonsterRole.Leader,
                }.intersection(stats.additional_roles)
            )
            and stats.creature_type
            in {CreatureType.Celestial, CreatureType.Giant, CreatureType.Aberration}
        )
    )

    if could_teleport and (flags.NO_TELEPORT not in stats.flags):
        yield LegendaryActionScore(
            feature=Feature(
                name="Teleport",
                description=f"{stats.selfref.capitalize()} teleports up to 60 feet to a location it can see.",
                action=ActionType.Legendary,
            ),
            types={LegendaryActionType.move},
            score=5,
        )

    if len(sneaky_roles.intersection(stats.additional_roles)):
        hide = action_ref("Hide")
        yield LegendaryActionScore(
            feature=Feature(
                name="Sneak",
                description=f"{stats.selfref.capitalize()} moves up to half its movement and uses {hide}.",
                action=ActionType.Legendary,
            ),
            types={LegendaryActionType.move},
            score=1,
        )

    if len(fast_roles.intersection(stats.additional_roles)):
        yield LegendaryActionScore(
            feature=Feature(
                name="Dart",
                description=f"{stats.selfref.capitalize()} moves up to its speed without provoking attacks of opportunity.",
                action=ActionType.Legendary,
            ),
            types={LegendaryActionType.move},
            score=1,
        )

    yield LegendaryActionScore(
        feature=Feature(
            name="Move",
            description=f"{stats.selfref.capitalize()} moves up to its speed.",
            action=ActionType.Legendary,
        ),
        types={LegendaryActionType.move},
        score=0,
    )
