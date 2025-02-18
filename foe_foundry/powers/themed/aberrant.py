from datetime import datetime
from typing import List

from ...attack_template import natural
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class AberrantPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        def is_aberrant_creature(c: BaseStatblock) -> bool:
            if (
                c.creature_type in {CreatureType.Humanoid, CreatureType.Fey}
                and any(t.is_spell() for t in c.attack_types)
                and c.secondary_damage_type == DamageType.Psychic
            ):
                return True
            else:
                return c.creature_type in {
                    CreatureType.Aberration,
                    CreatureType.Monstrosity,
                }

        standard_score_args = (
            dict(
                require_callback=is_aberrant_creature,
                bonus_roles=[
                    MonsterRole.Controller,
                    MonsterRole.Ambusher,
                    MonsterRole.Skirmisher,
                ],
                bonus_attack_types=AttackType.AllSpell(),
                bonus_damage=DamageType.Psychic,
            )
            | score_args
        )
        super().__init__(
            name=name,
            power_type=PowerType.Role,
            power_level=power_level,
            source=source,
            create_date=create_date,
            theme="Aberrant",
            score_args=standard_score_args,
        )


class _ModifyMemory(AberrantPower):
    def __init__(self):
        super().__init__(name="Modify Memory", source="SRD5.1 Modify Memory")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Modify Memory",
            action=ActionType.BonusAction,
            description=f"Immediately after hitting with an attack, {stats.selfref} attempts to reshape that creature's memories. \
                The creature must succeed on a DC {dc} Intelligence saving throw or be affected as if by the *Modify Memory* spell. \
                A creature that succeeds on the save is immune to this effect for 24 hours.",
        )
        return [feature]


class _WarpReality(AberrantPower):
    def __init__(self):
        super().__init__(name="Warp Reality", source="Foe Foundry")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        distance = 20 + (20 if stats.cr >= 7 else 0)
        feature = Feature(
            name="Warp Reality",
            description=f"Each creature of {stats.selfref}'s choice within 30 ft must succeed on a DC {dc} Charisma save or be teleported up to {distance} ft to an unoccupied space that {stats.selfref} can see.\
                If the target space is a hazard (such as an open pit, lava, or in the air) then the target may use its reaction to attempt a DC {dc} Dexterity save.\
                On a success, the target reduces the damage taken from the hazard this turn by half, or narrowly escapes the hazard. Creatures may choose to fail this save.",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=4,
        )
        return [feature]


class _Adhesive(AberrantPower):
    def __init__(self):
        super().__init__(name="Adhesive", source="SRD5.1 Mimic")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Adhesive",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} adheres to anything that touches it (including weapons). \
                A Huge or smaller creature or object adhered to {stats.selfref} is also **Grappled** by it (escape DC {dc}). \
                Ability checks made to escape this grapple have disadvantage.",
        )
        return [feature]


class _Incubation(AberrantPower):
    def __init__(self):
        super().__init__(
            name="Incubation",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            attack_names=["-", natural.Claw],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        timespan = "three months" if stats.cr <= 5 else "three days"

        feature = Feature(
            name="Incubation",
            action=ActionType.Feature,
            description=f"If a humanoid is hit by {stats.selfref}'s attack, it must make a DC {dc} Constitution saving throw. \
                            On a failure, the target is infected by a terrible parasite. The target can carry only one such parasite at a time. \
                            Over the next {timespan}, the parasite gestates and moves to the chest cavity. \
                            In the 24-hour period before the parasite gives birth, the target feels unwell. Its speed is halved, and it has disadvantage on attack rolls, ability checks, and saving throws. \
                            At birth, the parasite burrows its way out of the target's chest in one round, killing it.\
                            If the disease is cured, the parasite disintigrates.",
        )
        return [feature]


Adhesive: Power = _Adhesive()
ModifyMemory: Power = _ModifyMemory()
WarpReality: Power = _WarpReality()
Incubation: Power = _Incubation()

AberrantPowers: List[Power] = [Adhesive, ModifyMemory, WarpReality, Incubation]
