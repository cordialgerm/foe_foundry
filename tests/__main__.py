import subprocess
import sys
from fnmatch import fnmatch
from io import BytesIO
from pathlib import Path

import click
import numpy as np
import pytest
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By

from .filtering import filter_examples


@click.command()
@click.option("--display", default=1, help="displays a random sample of the specified size")
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
            screenshot(selection)

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


def screenshot(path: Path):
    screenshots_dir = Path(__file__).parent.parent / "examples" / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    screenshot_path = screenshots_dir / f"{path.stem}.png"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get(path.as_uri())

    element = driver.find_element(by=By.CLASS_NAME, value="stat-block")
    location = element.location_once_scrolled_into_view
    size = element.size

    bytes = driver.get_screenshot_as_png()
    driver.quit()

    img = Image.open(BytesIO(bytes))
    left = location["x"]
    top = location["y"]
    right = (
        location["x"] + 1.25 * size["width"] + 10
    )  # main monitor messes this up... it has 125% scaling
    bottom = (
        location["y"] + 1.25 * size["height"] + 10
    )  # main monitor messes this up... it has 125% scaling
    box = (left, top, right, bottom)
    img2 = img.crop(box)
    img2.save(screenshot_path, format="png")


if __name__ == "__main__":
    run_tests()
