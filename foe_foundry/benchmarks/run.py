from functools import cached_property
from typing import List

from ..statblocks import BaseStatblock
from .data import Benchmark
from .fof import FoFBenchmark
from .l5e import L5EBenchmark


# don't instantiate the benchmarkers all the time
# they have to load CSVs
class _SingleInstance:
    @cached_property
    def L5E(self) -> L5EBenchmark:
        return L5EBenchmark()

    @cached_property
    def FOF(self) -> FoFBenchmark:
        return FoFBenchmark()


benchmarker = _SingleInstance()


def benchmark(stats: BaseStatblock) -> List[Benchmark]:
    b1 = benchmarker.FOF.benchmark(stats)
    b2 = benchmarker.L5E.benchmark(stats)
    return [b1, b2]
