import re
from pathlib import Path
from typing import Tuple

from bs4 import BeautifulSoup


def filter_statblock(path: Path, feature: str | re.Pattern) -> Tuple[Path, bool]:
    if feature == "":
        return path, True

    with path.open("r") as f:
        bs = BeautifulSoup(markup=f, features="html.parser")
        results = bs.find(name="stat-block").findAll(name="h4", string=re.compile(feature))
        return path, len(results) > 0
