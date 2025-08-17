import re
from typing import Any

import yaml


def extract_yaml_block_from_text(text: str) -> Any:
    """
    Extracts a YAML block from a given text string.
    """
    matches = re.findall(r"```yaml(.*?)```", text, re.DOTALL)
    if matches:
        return yaml.safe_load(matches[0].strip())

    return yaml.safe_load(text.strip())
