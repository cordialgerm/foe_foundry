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

TODO - add larger issues you've uncovered here