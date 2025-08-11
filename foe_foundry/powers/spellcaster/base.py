from datetime import datetime
from typing import List

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...damage import AttackType
from ...power_types import PowerType
from ...spells import CasterType, StatblockSpell
from .. import flags
from ..power import HIGH_POWER, PowerCategory, PowerWithStandardScoring


class _Spellcaster(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        spells: List[StatblockSpell],
        caster_type: CasterType,
        theme: str,
        icon: str,
        reference_statblock: str,
        score_args: dict,
        min_cr: int = 1,
        max_cr: int = 100,
        creature_class: str | None = None,
        power_level=HIGH_POWER,
        require_attack_types=AttackType.AllSpell(),
        power_types: List[PowerType] | None = None,
    ):
        # Default to Magic if no power_types provided
        if power_types is None:
            power_types = [PowerType.Magic]

        score_args = (
            dict(
                require_cr=min_cr,
                require_max_cr=max_cr,
                require_attack_types=require_attack_types,
            )
            | score_args
        )

        super().__init__(
            name=name,
            power_category=PowerCategory.Spellcasting,
            source="Foe Foundry",
            theme=theme,
            icon=icon,
            reference_statblock=reference_statblock,
            power_level=power_level,
            create_date=datetime(2023, 12, 14),
            power_types=power_types,
            score_args=score_args,
        )

        self.spells = spells
        self.creature_class = creature_class
        self.caster_type = caster_type

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.grant_spellcasting(self.caster_type)
        if self.creature_class is not None and stats.creature_class is None:
            stats = stats.copy(creature_class=self.creature_class)
        sorted_spells = sorted(self.spells, key=lambda s: s.name)
        return stats.add_spells(sorted_spells)


class WizardPower(_Spellcaster):
    def __init__(
        self,
        creature_name: str,
        icon: str = "wizard-face",
        reference_statblock="Mage",
        power_types: List[PowerType] | None = None,
        **kwargs,
    ):
        additional_score_args = kwargs.pop("score_args", {})
        existing_callback = additional_score_args.pop("require_callback", None)

        def is_wizard(c: BaseStatblock) -> bool:
            if existing_callback is not None and not existing_callback(c):
                return False

            return c.creature_class == "Wizard" and c.caster_type == CasterType.Arcane

        args: dict = (
            dict(
                theme=creature_name.lower(),
                reference_statblock=reference_statblock,
                caster_type=CasterType.Arcane,
                icon=icon,
                power_types=power_types,
                score_args=dict(
                    require_callback=is_wizard,
                    require_no_flags=[flags.WIZARD],
                )
                | additional_score_args,
            )
            | kwargs
        )

        super().__init__(**args)
        self.creature_name = creature_name

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        stats = stats.grant_spellcasting(CasterType.Arcane)
        stats = stats.with_flags(flags.WIZARD)
        return stats
