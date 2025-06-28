import numpy as np

from .feature import Feature


def resolve_conflicting_recharge(features: list[Feature]):
    """If there are multiple features with recharge, only keep one and set the rest to single-use"""

    if len(features) == 0:
        return features

    scores = np.array([f.recharge_priority for f in features])
    indexes = np.argsort(scores)[::-1]
    best_index = indexes[0]

    new_features = [
        f if i == best_index or f.recharge is None else f.copy(recharge=None, uses=1)
        for i, f in enumerate(features)
    ]

    return new_features
