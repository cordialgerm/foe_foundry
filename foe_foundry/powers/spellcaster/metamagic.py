from datetime import datetime

from num2words import num2words

from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...spells import CasterType
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    RIBBON_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class _MetamagicPower(PowerWithStandardScoring):
    def __init__(
        self,
        *,
        name: str,
        caster_type: CasterType,
        power_level: float = MEDIUM_POWER,
        **kwargs,
    ):
        def is_correct_spellcaster(c: BaseStatblock) -> bool:
            return c.caster_type == caster_type and len(c.spells) > 0

        score_args = (
            dict(require_callback=is_correct_spellcaster, require_cr=4) | kwargs
        )

        super().__init__(
            name=name,
            power_type=PowerType.Spellcasting,
            source="FoeFoundry",
            theme="Metamagic",
            power_level=power_level,
            create_date=datetime(2025, 3, 7),
            score_args=score_args,
        )
        self.caster_type = caster_type


class _ArcaneMastery(_MetamagicPower):
    def __init__(self):
        super().__init__(name="Arcane Mastery", caster_type=CasterType.Arcane)

    def generate_features(self, stats: BaseStatblock):
        feature = Feature(
            name="Arcane Mastery",
            action=ActionType.BonusAction,
            description=f"One creature of {stats.selfref}'s choice must subtract a d4 from the next saving throw it makes before the end of {stats.selfref}'s turn.",
            uses=stats.attributes.proficiency // 2,
        )
        return [feature]


class _PrimalMastery(_MetamagicPower):
    def __init__(self):
        super().__init__(name="Primal Mastery", caster_type=CasterType.Primal)

    def generate_features(self, stats: BaseStatblock):
        dmg = stats.target_value(0.5)

        feature = Feature(
            name="Primal Mastery",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.selfref.capitalize()}'s next spell or spell attack deals an additional {dmg.description} Cold, Fire, Lightning, or Thunder damage.",
        )

        return [feature]


class _DivineIntervention(_MetamagicPower):
    def __init__(self):
        super().__init__(
            name="Divine Intervention",
            caster_type=CasterType.Divine,
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock):
        level = num2words(min(max(round(stats.cr / 2.5), 1), 9), ordinal=True)

        examples = [
            "Heal",
            "Greater Restoration",
            "Mass Cure Wounds",
            "Divine Word",
            "Dispel Magic",
        ]
        examples = [f"*{e}*" for e in examples]

        feature = Feature(
            name="Divine Intervention",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref} casts any Divine spell of {level} level or lower. Common examples include: {', '.join(examples)}.",
            uses=1,
        )

        return [feature]


class _SubtleMind(_MetamagicPower):
    def __init__(self):
        super().__init__(
            name="Subtle Mind", caster_type=CasterType.Psionic, power_level=RIBBON_POWER
        )

    def generate_features(self, stats: BaseStatblock):
        feature = Feature(
            name="Subtle Mind",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} casts its spells without requiring verbal or somatic components.",
        )
        return [feature]


class _PactBoon(_MetamagicPower):
    def __init__(self):
        super().__init__(
            name="Pact Boon", caster_type=CasterType.Pact, power_level=MEDIUM_POWER
        )

    def generate_features(self, stats: BaseStatblock):
        self_damage = stats.target_value(0.25, force_die=Die.d6)
        dmg = DieFormula.from_dice(d6=2 * self_damage.n_die)

        feature = Feature(
            name="Pact Boon",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} deals {self_damage.description} Psychic damage to itself and its next spell or spell attack deals an additional {dmg.description} Psychic damage.",
            uses=stats.attributes.proficiency // 2,
        )
        return [feature]


class _InnateMagic(_MetamagicPower):
    def __init__(self):
        super().__init__(
            name="Innate Magic",
            caster_type=CasterType.Innate,
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock):
        feature = Feature(
            name="Innate Magic",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} casts a spell as a bonus action.",
            uses=1,
        )
        return [feature]


ArcaneMastery: Power = _ArcaneMastery()
PrimalMastery: Power = _PrimalMastery()
DivineIntervention: Power = _DivineIntervention()
SubtleMind: Power = _SubtleMind()
PactBoon: Power = _PactBoon()
InnateMagic: Power = _InnateMagic()

MetamagicPowers: list[Power] = [
    ArcaneMastery,
    PrimalMastery,
    DivineIntervention,
    SubtleMind,
    PactBoon,
    InnateMagic,
]
