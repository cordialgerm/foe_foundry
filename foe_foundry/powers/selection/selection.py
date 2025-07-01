import numpy as np

from foe_foundry.powers import Power

from .loadout import PowerLoadout
from .settings import SelectionSettings


class PowerSelection:
    def __init__(
        self,
        loadouts: list[PowerLoadout],
        species_loadout: PowerLoadout | None = None,
    ):
        self.loadouts = loadouts
        self.species_loadout = species_loadout

    def choose_powers(self, settings: SelectionSettings) -> list[Power]:
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

            if loadout.selection_count > len(options):
                raise ValueError(
                    f"Selection count {loadout.selection_count} exceeds available powers {len(options)} in loadout {loadout.name}"
                )
            elif loadout.selection_count == len(options):
                powers.extend(options)
            else:
                weights = np.array(
                    [settings.power_weights.get(p.key, 0) for p in loadout.powers]
                )

                # we're going to scale the weights so that values close to 1 become large probabilities
                # values close to -1 become small probabilities
                # we will treat the exact value of 1 as a power that is always selected
                # we will treat the exact value of -1 as a power that is never selected
                if np.any(weights == 1.0):
                    selection_indexes = np.where(weights == 1.0)[0]
                elif np.all(weights == 0.0):
                    # if all weights are 0, we just select uniformly
                    selection_indexes = settings.rng.choice(
                        len(options), size=loadout.selection_count, replace=False
                    )
                else:
                    # we're going to use tan function to scale values between -1 and 1 to a probability distributio
                    # we then perform softmax to ensure the probabilities sum to 1
                    # note - we use 0.9 here to avoid asymptotic behavior while still allowing for a wide range of weights
                    p = np.tan(0.9 * np.pi / 2 * weights)
                    p = np.exp(p)
                    p[weights == -1.0] = 0.0
                    p = p / np.sum(p)

                    rng = settings.rng
                    selection_indexes = rng.choice(
                        len(options),
                        size=loadout.selection_count,
                        replace=False,
                        p=p,
                    )

                powers.extend([options[i] for i in selection_indexes])

        return powers
