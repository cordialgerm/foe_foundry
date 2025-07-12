#!/usr/bin/env python3
"""
Script to help refactor creature power files to add power_types.
This script will identify the patterns needed for each file.
"""

from pathlib import Path

# Mapping of power names to their appropriate power types based on descriptions
POWER_TYPE_MAPPINGS = {
    # Attack powers - deal damage directly
    "attack": "[PowerType.Attack]",
    "bite": "[PowerType.Attack]",
    "claw": "[PowerType.Attack]",
    "strike": "[PowerType.Attack]",
    "slam": "[PowerType.Attack]",
    "shot": "[PowerType.Attack]",
    "arrow": "[PowerType.Attack]",
    "sword": "[PowerType.Attack]",
    "weapon": "[PowerType.Attack]",
    # Breath/Area attacks
    "breath": "[PowerType.AreaOfEffect, PowerType.Attack]",
    "explosion": "[PowerType.AreaOfEffect, PowerType.Attack]",
    "blast": "[PowerType.AreaOfEffect, PowerType.Attack]",
    "roar": "[PowerType.AreaOfEffect, PowerType.Debuff]",
    "howl": "[PowerType.AreaOfEffect, PowerType.Debuff]",
    "scream": "[PowerType.AreaOfEffect, PowerType.Debuff]",
    # Movement powers
    "teleport": "[PowerType.Movement]",
    "dash": "[PowerType.Movement]",
    "leap": "[PowerType.Movement]",
    "charge": "[PowerType.Movement, PowerType.Attack]",
    "burrow": "[PowerType.Movement, PowerType.Utility]",
    # Defensive powers
    "shield": "[PowerType.Defense]",
    "armor": "[PowerType.Defense]",
    "protection": "[PowerType.Defense]",
    "block": "[PowerType.Defense]",
    "deflect": "[PowerType.Defense]",
    "hide": "[PowerType.Defense, PowerType.Utility]",
    # Debuff powers
    "fear": "[PowerType.Debuff]",
    "frighten": "[PowerType.Debuff]",
    "paralyze": "[PowerType.Debuff]",
    "poison": "[PowerType.Debuff, PowerType.Attack]",
    "slow": "[PowerType.Debuff]",
    "weaken": "[PowerType.Debuff]",
    "curse": "[PowerType.Debuff]",
    "charm": "[PowerType.Debuff]",
    "dominate": "[PowerType.Debuff]",
    "stun": "[PowerType.Debuff]",
    "blind": "[PowerType.Debuff]",
    # Buff powers
    "strengthen": "[PowerType.Buff]",
    "enhance": "[PowerType.Buff]",
    "bless": "[PowerType.Buff]",
    "inspire": "[PowerType.Buff]",
    "rally": "[PowerType.Buff]",
    "rage": "[PowerType.Buff]",
    "fury": "[PowerType.Buff, PowerType.Attack]",
    # Healing powers
    "heal": "[PowerType.Healing]",
    "restore": "[PowerType.Healing]",
    "regenerate": "[PowerType.Healing]",
    "recover": "[PowerType.Healing]",
    "cannibal": "[PowerType.Healing]",
    # Summon powers
    "summon": "[PowerType.Summon]",
    "call": "[PowerType.Summon]",
    "conjure": "[PowerType.Summon]",
    "create": "[PowerType.Summon]",
    "spawn": "[PowerType.Summon]",
    "brood": "[PowerType.Summon]",
    # Aura powers
    "aura": "[PowerType.Aura]",
    "emanation": "[PowerType.Aura]",
    "presence": "[PowerType.Aura]",
    # Environmental powers
    "environment": "[PowerType.Environmental]",
    "terrain": "[PowerType.Environmental]",
    "weather": "[PowerType.Environmental]",
    # Utility powers
    "detect": "[PowerType.Utility]",
    "see": "[PowerType.Utility]",
    "sense": "[PowerType.Utility]",
    "scout": "[PowerType.Utility]",
    "track": "[PowerType.Utility]",
    "disguise": "[PowerType.Utility, PowerType.Defense]",
    "mimic": "[PowerType.Utility]",
    "transform": "[PowerType.Utility]",
    "shapeshift": "[PowerType.Utility]",
}


def analyze_creature_files():
    """Analyze all creature power files and provide refactoring guidance."""
    creature_dir = Path("foe_foundry/powers/creature")

    files_to_process = []
    completed_files = [
        "balor.py",
        "basilisk.py",
        "bugbear.py",
        "chimera.py",
        "cultist.py",
        "dire_bunny.py",
        "druid.py",
        "gelatinous_cube.py",
        "ghoul.py",
    ]

    for py_file in creature_dir.glob("*.py"):
        if py_file.name not in ["__init__.py"] + completed_files:
            files_to_process.append(py_file)

    print(f"Remaining creature files to process: {len(files_to_process)}")
    print("\nFiles:")
    for f in sorted(files_to_process):
        print(f"  - {f.name}")

    return files_to_process


def suggest_power_types(power_name):
    """Suggest power types based on power name."""
    name_lower = power_name.lower()

    # Check for specific keywords
    for keyword, power_types in POWER_TYPE_MAPPINGS.items():
        if keyword in name_lower:
            return power_types

    # Default fallback based on common patterns
    if any(word in name_lower for word in ["damage", "hurt", "wound"]):
        return "[PowerType.Attack]"
    elif any(word in name_lower for word in ["move", "speed", "fly"]):
        return "[PowerType.Movement]"
    elif any(word in name_lower for word in ["help", "aid", "support"]):
        return "[PowerType.Buff]"
    else:
        return "[PowerType.Utility]"  # Safe default


if __name__ == "__main__":
    analyze_creature_files()
