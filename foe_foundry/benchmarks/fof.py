from fractions import Fraction
from pathlib import Path

import pandas as pd


def _bonus_to_int(v: str | int) -> int:
    if isinstance(v, int):
        return v
    elif isinstance(v, str):
        v = v.strip()
        if v.startswith("+"):
            v = v[1:]
        return int(v)


def _cr_to_float(cr: str | float) -> float:
    if isinstance(cr, float):
        return cr
    else:
        return float(Fraction(cr).limit_denominator(10))


class FoFBenchmark:
    def __init__(self):
        path = Path(__file__).parent / "fof.csv"
        with path.open("r") as f:
            df = pd.read_csv(f)

        df["cr_float"] = df["CR"].map(_cr_to_float)
        df["ability_bonus_int"] = df["Proficient Ability Bonus"].map(_bonus_to_int)
        self.df = df
        self.lookup = {v: i for i, v in enumerate(self.df["cr_float"])}

    def benchmark_hp(self, cr: float) -> int:
        i = self.lookup[cr]
        expected_hp = self.df.iloc[i]["Hit Point Average"]
        return expected_hp

    def benchmark_attacks(self, cr: float) -> int:
        i = self.lookup[cr]
        expected_attacks = self.df.iloc[i]["Number of Attacks"]
        return expected_attacks

    def benchmark_attack_damage(self, cr: float) -> int:
        i = self.lookup[cr]
        expected_damage = self.df.iloc[i]["Damage Per Attack"]
        return expected_damage

    def benchmark_hit(self, cr: float) -> int:
        i = self.lookup[cr]
        expected_hit = self.df.iloc[i]["ability_bonus_int"]
        return expected_hit
