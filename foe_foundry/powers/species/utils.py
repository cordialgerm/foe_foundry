from typing import List

from foe_foundry.role_types import MonsterRole

from ..power import (
    Power,
    PowerWithStandardScoring,
)
from ._all import SpeciesPowers


def powers_for_role(species: str, role: MonsterRole) -> List[Power]:
    """Filters powers to those that are suitable for the given role."""
    filtered_powers = [
        p for p in SpeciesPowers if getattr(p, "species", None) == species
    ]
    powers = []
    for p in filtered_powers:
        if not isinstance(p, PowerWithStandardScoring):
            continue

        score_args = p.score_args or {}
        roles = set(score_args.get("require_roles", set())) | set(
            score_args.get("bonus_roles", set())
        )

        if role in roles:
            powers.append(p)

    return powers
