import re
from typing import Any

import yaml


def extract_yaml_block_from_text(text: str) -> Any:
    """
    Extracts a YAML block from a given text string.
    """

    matches = re.findall(r"```yaml(.*?)```", text, re.DOTALL)
    if not matches:
        return yaml.safe_load(quote_problematic_values(text))

    block = matches[0].strip() if matches else text.strip()
    block = quote_problematic_values(block)
    return yaml.safe_load(block)


def quote_problematic_values(yaml_text):
    lines = yaml_text.splitlines()
    new_lines = []
    for line in lines:
        # Ignore indented lines (lists, blocks)
        if re.match(r"^\s", line) or not line.strip() or line.strip().startswith("#"):
            new_lines.append(line)
            continue
        # Match key: value
        m = re.match(r"^([\w\-]+):\s*(.*)$", line)
        if m:
            key, value = m.group(1), m.group(2)
            # If value contains unescaped colon or double quote and is not already quoted
            if (":" in value or '"' in value) and not (
                value.startswith('"') or value.startswith("'")
            ):
                # If value contains double quotes, use single quotes for YAML
                if '"' in value:
                    # Escape single quotes inside value for YAML
                    value = value.replace("'", "''")
                    value = f"'{value}'"
                else:
                    # Otherwise, use double quotes
                    value = value.replace('"', '"')
                    value = f'"{value}"'
            new_lines.append(f"{key}: {value}")
        else:
            new_lines.append(line)
    return "\n".join(new_lines)
