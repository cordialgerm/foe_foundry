# YAML Template Triage Analysis

## IMPORTANT

- Do not attempt to set statblock-level primary or secondary damage types in the YAML template
- Review the commented out "SECTIONS TO SKIP" section in tests/foe_foundry/templates/test_yaml_comparison.py to see other attributes that you should not attempt to modify or check directly


## Guideliens

- Start by checking for obvious mismatches in terms of roles, creature types, HP, attributes, etc. Try to correct those first
- Then, look for more complicated mismatches like missing attacks or missing attack amounts
    - Fix missing attacks by adding the missing primary or secondary attack in the YAML template
    - Fix missing attack counts by using `set_attack: X` in the appropriate attack section in the variant section of the YAML template
- Then look for damage or HP multiplier differences. Set those in the appopriate variant section of the YAML template


## Larger Issues Uncovered

### Golem Template Variant Parsing Issue

The golem template has a fundamental parser issue that prevents it from working correctly with the YAML template system:

**Problem**: The GolemTemplate in Python defines multiple variants with specific keys:
- stone-golem: Stone Golem
- clay-golem: Clay Golem  
- iron-golem: Iron Golem
- flesh-golem: Flesh Golem
- ice-golem: Ice Golem
- shield-guardian: Shield Guardian

However, the YAML template parser in `parse_variants_from_template_yaml()` has default behavior (lines 947-975) that creates a single variant with the template name ("golem") rather than the individual variant keys.

**Error**: `ValueError: Unknown golem variant: golem` occurs because the `choose_powers()` method expects variant keys like "stone-golem" but receives "golem".

**Root Cause**: The YAML parser needs special handling for the golem template similar to how wolf is handled (lines 902-945), but the instructions specify not to change the parser.

**Required Fix**: Either:
1. Add golem-specific logic to `parse_variants_from_template_yaml()` (requires parser changes)
2. Restructure the golem YAML template to work with the current parser limitations
3. Split golem into separate template files for each variant

This is a structural parser limitation that cannot be fixed by just modifying the YAML template content.

### Attack Die Count Parser Issue

**Problem**: The goblin template requires specific die counts for certain attacks (e.g., `die_count=1` for Daggers in goblin-lickspittle and goblin variants), but the YAML attack parser in `parse_single_attack_from_yaml()` does not support the `die_count` field.

**Error**: Attack damage mismatch: `1d4+2` (expected) vs `2d4+2` (actual) because the YAML parser doesn't apply the `die_count=1` setting.

**Root Cause**: The attack parsing function supports fields like `damage_scalar`, `display_name`, `reach`, etc., but does not parse the `die_count` field from YAML attack definitions.

**Required Fix**: Add `die_count` field parsing to the `parse_single_attack_from_yaml()` function in `_yaml_template.py` (requires parser changes).