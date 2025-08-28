from foe_foundry.attack_template import AttackTemplate
from foe_foundry.creatures._data import GenerationSettings
from foe_foundry.powers import PowerSelection
from foe_foundry.statblocks import BaseStatblock

from ._template import MonsterTemplate


class YamlMonsterTemplate(MonsterTemplate):
    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        return super().generate_stats(settings)

    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        return super().choose_powers(settings)
