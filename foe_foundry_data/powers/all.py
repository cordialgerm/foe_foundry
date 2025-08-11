from functools import cached_property

from foe_foundry.powers import AllPowers

from .data import PowerModel


class PowerLookupCache:
    """Caches power lookups for faster access because it can require creating a new statblock, which is expensive"""

    @cached_property
    def PowerLookup(self) -> dict[str, PowerModel]:
        return {power.key: PowerModel.from_power(power) for power in AllPowers}

    @cached_property
    def Themes(self) -> set[str]:
        return {power.theme.lower() for power in AllPowers if power.theme}

    @cached_property
    def PowersByTheme(self) -> dict[str, list[PowerModel]]:
        themes = sorted(self.Themes)
        return {
            theme: [p for _, p in self.PowerLookup.items() if p.theme.lower() == theme]
            for theme in themes
        }

    @cached_property
    def AllPowers(self) -> list[PowerModel]:
        return list(self.PowerLookup.values())


Powers = PowerLookupCache()
