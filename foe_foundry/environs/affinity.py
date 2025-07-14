from enum import Enum


class Affinity(Enum):
    """Affinity of a monster to an environment. Determines how commonly this monster can be found in the given environment"""

    absent = -1.0  # the monster cannot be found in this environment.
    na = 0.0  # the environment is not relevant to the monster
    rare = 0.25  # the monster is rarely found in this environment.
    uncommon = 0.5  # the monster is occasionally found in this environment.
    common = 0.75  # the monster is frequently found in this environment.
    native = 1.0  # the monster is native to this environment and thrives here.
