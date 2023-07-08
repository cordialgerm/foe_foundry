from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from ..features import Feature
from .base import BaseStatblock


@dataclass
class Statblock(BaseStatblock):
    features: List[Feature] = field(default_factory=list)

    @staticmethod
    def from_base_stats(name: str, stats: BaseStatblock, features: List[Feature]) -> Statblock:
        args = stats.__copy_args__()
        args.update(name=name, features=features)
        return Statblock(**args)
