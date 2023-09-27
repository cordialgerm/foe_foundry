import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path

import click
import numpy as np
import pytest

from .filtering import filter_examples


@click.command()
@click.option("--display", default=5, help="displays a random sample of the specified size")
@click.option(
    "--name",
    default="",
    help="filter results to only show statblocks whose names match the specified pattern",
)
@click.option(
    "--feature",
    default="",
    help="filter results to only show statblocks that match that filter",
)
def run_tests(display: int, feature: str, name: str):
    retcode = pytest.main(args=[""])

    examples_dir = Path(__file__).parent.parent / "examples"
    examples = [p for p in examples_dir.rglob("*.html")]
    print(f"Generated {len(examples)} statblocks.")

    if name != "":
        print(f"Filtering to match '{name}'...")
        matches = [p for p in examples if fnmatch(str(p), name)]
        print(f"Found {len(matches)} matches")
    else:
        matches = examples

    if feature != "":
        print(f"Checking features for '{feature}'...")
        matches = filter_examples(matches, feature)
        print(f"Found {len(matches)} matches:")
        for match in matches:
            print_statblock(match)
    else:
        matches = matches

    if display > 0 and len(matches) > 0:
        size = min(display, len(matches))
        print(f"Displaying {display} matches...")
        rng = np.random.default_rng()
        selections = rng.choice(a=np.array(matches, dtype=object), size=size, replace=False)
        for selection in selections:
            open_statblock(selection)

    sys.exit(retcode)


def print_statblock(path: Path):
    cwd = Path.cwd()
    rel = path.relative_to(cwd)
    print(f"Displaying {rel}...")


def open_statblock(path: Path):
    cwd = Path.cwd()
    rel = path.relative_to(cwd)
    print(f"Displaying {rel}...")
    subprocess.run(["start", str(rel)], shell=True)


if __name__ == "__main__":
    run_tests()
