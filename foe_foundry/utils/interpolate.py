import numpy as np


def interpolate_by_cr(cr: float, reference_values: dict[float, float]) -> float:
    xs = []
    ys = []

    for x, y in reference_values.items():
        xs.append(float(x))
        ys.append(float(y))

    xs = np.array(xs)
    ys = np.array(ys)

    if not np.all(np.diff(xs) > 0):
        raise ValueError("xs must be monotonically increasing")

    return np.interp(
        x=cr,
        xp=xs,
        fp=ys,
    )
