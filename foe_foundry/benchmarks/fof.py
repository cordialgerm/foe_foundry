from fractions import Fraction
from pathlib import Path

import pandas as pd

from ..statblocks import BaseStatblock
from .data import Benchmark


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

    def benchmark(self, stats: BaseStatblock) -> Benchmark:
        hp = stats.hp.static
        ac = stats.ac.value
        n_attack = stats.multiattack
        dpr = stats.attack.average_damage * n_attack
        hit = stats.attack.hit

        lookup = {v: i for i, v in enumerate(self.df["cr_float"])}
        i = lookup[stats.cr]
        expected_ac = self.df.iloc[i]["AC/DC"]
        expected_hp = self.df.iloc[i]["Hit Point Average"]
        expected_dpr = self.df.iloc[i]["Damage Per Round"]
        expected_hit = self.df.iloc[i]["ability_bonus_int"]

        # You can raise or lower the monster’s Armor Class
        # by one or two points without altering it in any other
        # way. If you change its AC by 3 or more points, you
        # should reduce or raise its hit points or damage per
        # round by 5% per point of AC you varied from the
        # base AC.
        # You can raise or lower the monster’s hit points by
        # 10% without altering it in any other way. Beyond
        # that, you should reduce or raise its AC by 1, or its
        # damage per round by 5%, for every 5% of hit points
        # you varied from the base hit points.
        ac_gap = ac - expected_ac
        hp_gap = (hp - expected_hp) / expected_hp
        dpr_gap = (dpr - expected_dpr) / expected_dpr
        hit_gap = hit - expected_hit

        return Benchmark(
            name="Forge of Foes Benchmark",
            expected_ac=expected_ac,
            actual_ac=ac,
            ac_gap=ac_gap,
            expected_dpr=expected_dpr,
            actual_dpr=dpr,
            dpr_gap=dpr_gap,
            expected_hp=expected_hp,
            actual_hp=hp,
            hp_gap=hp_gap,
            expected_hit=expected_hit,
            actual_hit=hit,
            hit_gap=hit_gap,
        )
