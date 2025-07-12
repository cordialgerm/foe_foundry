from datetime import datetime
from typing import List

from ...attack_template import weapon
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import DamageType, conditions
from ...die import Die
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...spells import CasterType, abjuration
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import MEDIUM_POWER, Power, PowerCategory, PowerWithStandardScoring


def is_holy(c: BaseStatblock) -> bool:
    return (
        c.secondary_damage_type == DamageType.Radiant
        or c.caster_type == CasterType.Divine
    )


class HolyPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            theme="holy",
            power_type=PowerCategory.Theme,
            create_date=create_date,
            power_level=power_level,
            reference_statblock="Priest",
            icon=icon,
            score_args=dict(
                require_stats=[Stats.WIS, Stats.CHA],
                require_types=CreatureType.Humanoid,
                require_damage=DamageType.Radiant,
                bonus_roles=MonsterRole.Support,
                bonus_skills=Skills.Religion,
                bonus_callback=is_holy,
            )
            | score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Radiant)
        stats = stats.grant_spellcasting(CasterType.Divine)
        return stats


class _DivineSmite(HolyPower):
    def __init__(self):
        super().__init__(
            name="Divine Smite",
            source="Foe Foundry",
            icon="sun-radiations",
            attack_names=[
                weapon.MaceAndShield,
                weapon.Greatsword,
                weapon.SwordAndShield,
            ],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(target=0.7, force_die=Die.d10)
        burning = conditions.Burning(dmg, damage_type=DamageType.Radiant)
        uses = max(1, stats.attributes.proficiency // 2)
        feature = Feature(
            name="Divine Smite",
            uses=uses,
            action=ActionType.BonusAction,
            description=f"Immediately after hitting a target, {stats.roleref} forces the target to make a DC {dc} Constitution saving throw. On a failure, the target is {burning}",
        )
        return [feature]


class _MassCureWounds(HolyPower):
    def __init__(self):
        super().__init__(
            name="Mass Cure Wounds", icon="healing", source="SRD5.1 Mass Cure Wounds"
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        spell = abjuration.MassCureWounds.for_statblock()
        return stats.add_spell(spell)


class _WordOfRadiance(HolyPower):
    def __init__(self):
        super().__init__(
            name="Word of Radiance", icon="fireflake", source="SRD 5.1 Word of Radiance"
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        target_damage = 1.5 if stats.multiattack >= 2 else 1.0
        damage = stats.target_value(target=target_damage, suggested_die=Die.d6)
        dc = stats.difficulty_class

        feature = Feature(
            name="Word of Radiance",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.roleref.capitalize()} utters a divine word and it shines with burning radiance. \
                Each hostile creature within 10 feet must make a DC {dc} Constitution saving throw or take {damage.description} radiant damage.",
        )
        return [feature]


class _Heroism(HolyPower):
    def __init__(self):
        super().__init__(name="Heroism", icon="medal", source="SRD 5.1 Heroism")

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        temp_hp = easy_multiple_of_five(
            1.75 * (stats.attributes.stat_mod(Stats.WIS) + stats.cr), min_val=5
        )

        feature = Feature(
            name="Heroism",
            action=ActionType.BonusAction,
            uses=stats.attributes.proficiency // 2,
            description=f"{stats.roleref.capitalize()} inspires another friendly creature within 60 ft, granting it {temp_hp} temporary hit points. \
                While those temporary hitpoints are active, the creature has advantage on saving throws and is immune to being frightened or charmed.",
        )

        return [feature]


class _DeathWard(HolyPower):
    def __init__(self):
        super().__init__(
            name="Death Ward", icon="heart-shield", source="SRD 5.1 Death Ward"
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        new_hp = easy_multiple_of_five(
            1.75 * (stats.attributes.stat_mod(Stats.WIS) + stats.cr), min_val=5
        )

        feature = Feature(
            name="Death Ward",
            action=ActionType.Reaction,
            uses=1,
            description=f"When a creature within 30 feet of {stats.selfref} takes damage that would reduce it to zero hit points, {stats.selfref} can use its reaction to instead set that creature's hit points to {new_hp}.",
        )

        return [feature]


DeathWard: Power = _DeathWard()
DivineSmite: Power = _DivineSmite()
Heroism: Power = _Heroism()
MassCureWounds: Power = _MassCureWounds()
WordOfRadiance: Power = _WordOfRadiance()

HolyPowers: List[Power] = [
    DeathWard,
    DivineSmite,
    Heroism,
    MassCureWounds,
    WordOfRadiance,
]
