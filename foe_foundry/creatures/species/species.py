from dataclasses import dataclass

from ...statblocks import BaseStatblock


@dataclass(kw_only=True, frozen=True)
class CreatureSpecies:
    name: str
    description: str

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        return stats

    def __hash__(self) -> int:
        return hash(self.name)
