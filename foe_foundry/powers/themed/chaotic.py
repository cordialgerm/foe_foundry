from datetime import datetime
from typing import List

from numpy.random import Generator

from foe_foundry.references import Token

from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...spells import CasterType
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five, summoning
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class ChaoticPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        reference_statblock: str = "Cultist",
        **score_args,
    ):
        standard_score_args = dict(
            require_types=[
                CreatureType.Fey,
                CreatureType.Aberration,
                CreatureType.Monstrosity,
            ],
            bonus_attack_types=AttackType.AllSpell(),
            **score_args,
        )
        super().__init__(
            name=name,
            power_type=PowerType.Theme,
            source=source,
            theme="Chaotic",
            reference_statblock=reference_statblock,
            create_date=create_date,
            power_level=power_level,
            score_args=standard_score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        return stats.grant_spellcasting(CasterType.Innate)


class _ChaoticSpace(ChaoticPower):
    def __init__(self):
        super().__init__(
            name="Chaotic Space",
            source="Foe Foundry",
            power_level=LOW_POWER,
            require_cr=5,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        radius = easy_multiple_of_five(stats.cr * 5, min_val=10, max_val=45)
        distance = 30 if stats.cr <= 5 else 60

        feature = Feature(
            name="Chaotic Space",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} creates a region of chaotic space in a {radius} foot sphere centered at a point it can see within {distance} feet. \
                Whenever another creature casts a spell within this space, it must make a DC {dc} Charisma saving throw or trigger a *Wild Magic Surge*. \
                Whenever another creature ends its turn within the space, it teleports 30 (1d10 x 5) feet in a random direction.",
        )

        return [feature]


class _EldritchBeacon(ChaoticPower):
    def __init__(self):
        super().__init__(
            name="Eldritch Beacon",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            require_cr=5,
            require_callback=self.can_summon,
        )

    def can_summon(self, c: BaseStatblock) -> bool:
        return self._summon_formula(c, c.create_rng("eldritch beacon")) is not None

    def _summon_formula(self, stats: BaseStatblock, rng: Generator) -> str | None:
        try:
            summon_cr_target = max(stats.cr / 4, 1)
            _, _, description = summoning.determine_summon_formula(
                summoner=stats.creature_type, summon_cr_target=summon_cr_target, rng=rng
            )
            return description
        except Exception:
            return None

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        description = self._summon_formula(stats, stats.create_rng("eldritch beacon"))
        beacon = Token(
            name="Eldritch Beacon", dc=stats.difficulty_class_token, charges=3
        )

        feature = Feature(
            name="Eldritch Beacon",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} magically creates a Medium {beacon.caption} at an unoccupied space it can see within 30 feet. \
                Each turn that the beacon is active, on initiative count 0, {description}",
        )
        return [feature]


# TODO
# Chaotic Power
# Anarchic Pulse – Releases bursts of raw chaos energy that randomly alters ongoing magical effects or even the physical battlefield.
# Sigil of Unmaking – Etches a symbol in the air or ground that causes structures to crumble, weapons to crack, or runes to burn away.


ChaoticSpace: Power = _ChaoticSpace()
EldritchBeacon: Power = _EldritchBeacon()

ChaoticPowers: List[Power] = [ChaoticSpace, EldritchBeacon]
