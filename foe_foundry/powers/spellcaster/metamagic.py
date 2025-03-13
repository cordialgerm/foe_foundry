from datetime import datetime

from num2words import num2words

from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...references import Token
from ...spells import CasterType
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import (
    HIGH_POWER,
    LOW_POWER,
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
        caster_types: CasterType | set[CasterType],
        power_level: float = MEDIUM_POWER,
        **kwargs,
    ):
        if isinstance(caster_types, CasterType):
            caster_types = {caster_types}

        def is_correct_spellcaster(c: BaseStatblock) -> bool:
            return c.caster_type in caster_types and len(c.spells) > 0

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
        self.caster_types = caster_types


class _ArcaneMastery(_MetamagicPower):
    def __init__(self):
        super().__init__(name="Arcane Mastery", caster_types=CasterType.Arcane)

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
        super().__init__(name="Primal Mastery", caster_types=CasterType.Primal)

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
            caster_types=CasterType.Divine,
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
            name="Subtle Mind",
            caster_types=CasterType.Psionic,
            power_level=RIBBON_POWER,
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
            name="Pact Boon", caster_types=CasterType.Pact, power_level=MEDIUM_POWER
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
            caster_types=CasterType.Innate,
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


class _SpellEcho(_MetamagicPower):
    def __init__(self):
        super().__init__(
            name="Spell Echo",
            caster_types={CasterType.Arcane, CasterType.Pact, CasterType.Pact},
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock):
        feature = Feature(
            name="Spell Echo",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} casts a copy of the same spell it cast the previous turn, without requiring a spell slot or concentration.",
            uses=1,
        )
        return [feature]


class _ManaSurge(_MetamagicPower):
    def __init__(self):
        super().__init__(
            name="Mana Surge",
            caster_types={CasterType.Arcane, CasterType.Primal},
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock):
        feature = Feature(
            name="Mana Surge",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} infuses the next spell it casts next turn with additional power, increasing the spell save DC by 2",
        )
        return [feature]


class _ArcaneResevoir(_MetamagicPower):
    def __init__(self):
        super().__init__(
            name="Arcane Resevoir",
            caster_types={CasterType.Arcane, CasterType.Pact},
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock):
        token = Token(
            name="Arcane Resevoir", dc=stats.difficulty_class_token, charges=3
        )
        attack = stats.attack.display_name
        feature = Feature(
            name="Arcane Resevoir",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=2,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} creates an {token.caption} in an unoccupied space within 30 feet. While the token is active, at initiative count 0, it makes a {attack} attack against any enemy within 30 feet, using {stats.selfref}'s stats",
        )
        return [feature]


class _BloodMagic(_MetamagicPower):
    def __init__(self):
        super().__init__(
            name="Blood Magic",
            caster_types={CasterType.Arcane, CasterType.Pact, CasterType.Innate},
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock):
        harm = easy_multiple_of_five(stats.target_value(0.25).average, min_val=5)
        bonus_damage = DieFormula.target_value(harm * 2.5, force_die=Die.d6)

        feature = Feature(
            name="Blood Magic",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} takes {harm} necrotic damage and the next spell or spell attack it makes deals an additional {bonus_damage.description} necrotic damage.",
        )
        return [feature]


class _Mindshackle(_MetamagicPower):
    def __init__(self):
        super().__init__(
            name="Mindshackle",
            caster_types={CasterType.Psionic},
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock):
        token = Token(name="Mindshackle", dc=stats.difficulty_class_token, charges=3)

        feature = Feature(
            name="Mindshackle",
            action=ActionType.Action,
            recharge=5,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} creates a {token.caption} in an unoccupied space within 30 feet. While the token is active, each creature within a 30 foot emanation of the token cannot cast a spell that requires a verbal or somatic component",
        )
        return [feature]


class _Runeburst(_MetamagicPower):
    def __init__(self):
        super().__init__(
            name="Runeburst",
            caster_types={
                CasterType.Arcane,
                CasterType.Pact,
                CasterType.Innate,
                CasterType.Primal,
            },
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock):
        dmg = stats.target_value(0.5, force_die=Die.d10)

        feature = Feature(
            name="Runeburst",
            action=ActionType.Feature,
            description=f"When a creature fails a save against one of {stats.selfref}'s spells, it magically engraves a rune overflowing with power onto that creature. \
                The next time {stats.selfref} casts a spell, if the creature is within 30 feet of {stats.selfref}, then the rune explodes, dealing {dmg.description} force damage to the creature and removing the rune.",
        )
        return [feature]


class _ArcaneMirror(_MetamagicPower):
    def __init__(self):
        super().__init__(
            name="Arcane Mirror",
            caster_types={CasterType.Arcane},
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock):
        token = Token(name="Arcane Mirror", dc=stats.difficulty_class_token, charges=1)
        feature = Feature(
            name="Arcane Mirror",
            action=ActionType.Action,
            replaces_multiattack=1,
            uses=1,
            creates_token=True,
            description=f"{stats.selfref.capitalize()} creates an {token.caption} in an unoccupied space within 30 feet. While the token is active, at initiative count 0 it casts a copy of the last spell that {stats.selfref} cast.",
        )
        return [feature]


ArcaneMirror: Power = _ArcaneMirror()
ArcaneResevoir: Power = _ArcaneResevoir()
ArcaneMastery: Power = _ArcaneMastery()
BloodMagic: Power = _BloodMagic()
DivineIntervention: Power = _DivineIntervention()
InnateMagic: Power = _InnateMagic()
ManaSurge: Power = _ManaSurge()
Mindshackle: Power = _Mindshackle()
PactBoon: Power = _PactBoon()
PrimalMastery: Power = _PrimalMastery()
Runeburst: Power = _Runeburst()
SpellEcho: Power = _SpellEcho()
SubtleMind: Power = _SubtleMind()

MetamagicPowers: list[Power] = [
    ArcaneMirror,
    ArcaneResevoir,
    ArcaneMastery,
    BloodMagic,
    DivineIntervention,
    InnateMagic,
    ManaSurge,
    Mindshackle,
    PactBoon,
    PrimalMastery,
    Runeburst,
    SpellEcho,
    SubtleMind,
]
