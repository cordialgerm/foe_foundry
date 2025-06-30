from dataclasses import dataclass

from ..power import Power


@dataclass(kw_only=True, frozen=True)
class PowerLoadout:
    name: str
    flavor_text: str
    powers: list[Power]
    selection_count: int = 1
    locked: bool = False
    replace_with_species_powers: bool = False

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, PowerLoadout):
            return False
        return self.name == value.name
