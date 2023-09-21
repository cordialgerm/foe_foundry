from multiprocessing import Pool
from pathlib import Path
from typing import List

import tqdm

from .filter import filter_statblock


def filter_examples(examples: List[Path], feature_filter: str) -> List[Path]:
    matches = []

    inputs = [(p, feature_filter) for p in examples]
    with Pool(processes=8) as pool, tqdm.tqdm(examples, total=len(examples)) as pbar:
        results = pool.starmap(func=filter_statblock, iterable=inputs)
        pbar.update(n=len(results))

        for path, is_included in results:
            if is_included:
                matches.append(path)

    return matches
