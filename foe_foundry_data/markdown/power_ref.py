from foe_foundry.utils import name_to_key

from ..powers import AllPowers, Power

_powers = {power.key: power for power in AllPowers}


def resolve_power_ref(power_name: str) -> Power | None:
    """Resolves a power name to a Power object."""
    key = name_to_key(power_name)
    return _powers.get(key)
