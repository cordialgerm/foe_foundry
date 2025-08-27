"""Types for the docs generation system."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class FilesToGenerate:
    """Represents a collection of files to be generated with their content."""

    name: str
    files: Dict[str, str]  # filename -> content
