from typing import Callable, List


class VariantCycler:
    def __init__(self, keys: List[str], method: Callable):
        self.i = 0
        self.keys = keys
        self.method = method

    def execute(self, **args):
        try:
            variant = self.keys[self.i % len(self.keys)]
            return self.method(variant=variant, **args)
        finally:
            self.i += 1
