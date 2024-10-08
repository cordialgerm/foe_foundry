import markdown
from bs4 import BeautifulSoup
import re


def parse_monster_markdown(markdown_text):
    # Convert markdown to HTML
    html = markdown.markdown(markdown_text)
    soup = BeautifulSoup(html, "html.parser")

    # Initialize a dictionary to hold monster data
    monster_data = {}

    # Extract the monster name
    h1 = soup.find("h1")
    if h1:
        monster_data["Name"] = h1.text.strip()

    # Extract the monster type, size, alignment
    p = soup.find("p")
    if p:
        monster_data["Type"] = p.text.strip("*").strip()

    # Extract key stats
    stats = {}
    for li in soup.find_all("li"):
        text = li.get_text(separator=" ").strip()
        if ":" in text:
            key, value = text.split(":", 1)
            stats[key.strip()] = value.strip()
    monster_data.update(stats)

    # Extract abilities table
    table = soup.find("table")
    if table:
        headers = [th.text.strip() for th in table.find_all("th")]
        values = [td.text.strip() for td in table.find_all("td")]
        monster_data["Abilities"] = dict(zip(headers, values))

    # Extract other attributes (Skills, Senses, Languages, etc.)
    for element in soup.find_all(text=re.compile(r"^\*\*.*\*\*:")):
        key_value = element.strip("**").split(":", 1)
        if len(key_value) == 2:
            key, value = key_value
            monster_data[key.strip()] = value.strip()

    # Extract Special Abilities and Actions
    sections = {}
    current_section = None
    for header in soup.find_all(["h3", "h4"]):
        section_title = header.text.strip()
        content = []
        next_node = header.find_next_sibling()
        while next_node and next_node.name not in ["h3", "h4"]:
            if next_node.name == "ul":
                for li in next_node.find_all("li"):
                    content.append(li.text.strip())
            elif next_node.name == "p":
                content.append(next_node.text.strip())
            next_node = next_node.find_next_sibling()
        sections[section_title] = content

    monster_data.update(sections)

    return monster_data


def generate_natural_language(monster_data):
    description = f"The {monster_data.get('Name', 'Unknown Creature')} is a {monster_data.get('Type', 'creature')}."

    # Add armor class, hit points, speed
    ac = monster_data.get("Armor Class", "unknown AC")
    hp = monster_data.get("Hit Points", "unknown HP")
    speed = monster_data.get("Speed", "unknown speed")
    description += f" It has an armor class of {ac}, {hp} hit points, and can move at a speed of {speed}."

    # Add abilities
    abilities = monster_data.get("Abilities", {})
    if abilities:
        ability_scores = ", ".join([f"{k} {v}" for k, v in abilities.items()])
        description += f" Its ability scores are: {ability_scores}."

    # Add special abilities
    special_abilities = monster_data.get("Special Abilities", [])
    if special_abilities:
        description += " Special abilities include: " + " ".join(special_abilities)

    # Add actions
    actions = monster_data.get("Actions", [])
    if actions:
        description += " It can perform the following actions: " + " ".join(actions)

    # Add additional information
    for key in [
        "Skills",
        "Senses",
        "Languages",
        "Damage Immunities",
        "Damage Resistances",
        "Condition Immunities",
    ]:
        value = monster_data.get(key)
        if value:
            description += f" {key}: {value}."

    # Add challenge rating
    cr = monster_data.get("Challenge Rating")
    if cr:
        description += f" The challenge rating for this creature is {cr}."

    return description


# Example usage:

# Replace this string with your markdown content
markdown_text = """
# Acolyte

*Medium humanoid (any lineage)*

- **Armor Class:** 10
- **Hit Points:** 15
- **Speed:** 30 ft.
- **Challenge Rating:** CR 1/4
- **Source:** [Kobold Press Black Flag SRD](https://koboldpress.com/black-flag-roleplaying/)

| STR | DEX | CON | INT | WIS | CHA |
| --- | --- | --- | --- | --- | --- |
| +0 | +0 | +0 | +0 | +4 | +0 |

- **Senses:** —
- **Perception:** 13
- **Stealth:** 10
- **Languages:** any one language (usually Common)

### Special Abilities

- **Divine Providence.** Each friendly creature within 20 feet of the acolyte that isn’t a Construct or Undead has advantage on death saves.

### Actions

- **Mace.** Melee Weapon Attack: +2 to hit, reach 5 ft., one target. Hit: 3 (1d6) bludgeoning damage plus 3 (1d6) necrotic or radiant damage (the acolyte’s choice).
- **Radiant Bolt.** Ranged Spell Attack: +6 to hit, range 60 ft., one target. Hit: 6 (1d4 + 4) radiant damage.
- **Spellcasting.** The acolyte casts one of the following spells using WIS as the spellcasting ability (spell save DC 13).
    - At will: light, thaumaturgy
    - 3/day each: bless, cure wounds, sanctuary
"""

# Parse the markdown
monster_data = parse_monster_markdown(markdown_text)

# Generate the natural language description
description = generate_natural_language(monster_data)

print(description)
