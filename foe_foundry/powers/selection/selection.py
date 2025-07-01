import numpy as np

from foe_foundry.powers import Power

from .loadout import PowerLoadout


class PowerSelection:
    def __init__(
        self,
        loadouts: list[PowerLoadout],
        species_loadout: PowerLoadout | None = None,
    ):
        self.loadouts = loadouts
        self.species_loadout = species_loadout

    def choose_powers(self, rng: np.random.Generator) -> list[Power]:
        """
        Randomly selects powers based on the specified loadouts and their selection counts.
        """

        powers: list[Power] = []
        for loadout in self.loadouts:
            if loadout.selection_count == 0:
                continue

            if self.species_loadout is not None and loadout.replace_with_species_powers:
                loadout = self.species_loadout

            options = loadout.powers

            if loadout.selection_count >= len(options):
                powers.extend(options)

            else:
                selection_indexes = rng.choice(
                    len(options), size=loadout.selection_count, replace=False
                )
                powers.extend([options[i] for i in selection_indexes])

        return powers
