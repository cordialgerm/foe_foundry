from dataclasses import dataclass


@dataclass
class Benchmark:
    name: str
    expected_ac: int
    actual_ac: int
    ac_gap: int

    expected_dpr: float
    actual_dpr: float
    dpr_gap: float

    expected_hp: float
    actual_hp: float
    hp_gap: float

    expected_hit: int
    actual_hit: int
    hit_gap: int

    @property
    def total_gap(self) -> float:
        score = 0.05 * self.ac_gap + self.dpr_gap + self.hp_gap + 0.05 * self.hit_gap
        return score
