from dataclasses import dataclass

from foe_foundry.utils import name_to_key

from ...statblocks import BaseStatblock


@dataclass(kw_only=True, frozen=True)
class CreatureSpecies:
    name: str
    description: str

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        if not stats.name.startswith(self.name):
            stats = stats.copy(name=f"{self.name} {stats.name}")

        return stats

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def key(self) -> str:
        return name_to_key(self.name)
