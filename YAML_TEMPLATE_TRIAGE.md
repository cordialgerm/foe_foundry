# YAML Template Triage Analysis

## Overview

This document analyzes the gaps between Python and YAML monster templates in the Foe Foundry system. Out of 44 total templates, **23 are currently failing** and **21 are passing** the exact comparison tests.

## Test Results Summary

**Passing Templates (21):**
- animated-armor, assassin, balor, basilisk, chimera, cultist, dire-bunny, druid, gorgon, guard, ghoul, knight, medusa, merrow, mimic, ogre, orc, owlbear, priest, scout, skeleton, vrock, wight, wolf

**Failing Templates (23):**
- bandit, berserker, bugbear, frost-giant, gelatinous-cube, golem, goblin, hollow-gazer, hydra, kobold, lich, mage, manticore, simulacrum, spirit, spy, thug, warrior, zombie

## Issue Categories

### A. Simple YAML Template Issues (Easy Fixes)

These are straightforward discrepancies in the YAML template configuration that can be fixed by tweaking specific values.

#### 1. Missing Secondary Damage Types
**Templates affected:** spy, zombie
**Issue:** YAML templates missing `secondary_damage_type` configuration
**Example:** 
- Spy attack should include poison damage: `7 (2d4 + 2) piercing damage and 5 (2d4) poison damage`
- YAML template has secondary_damage_type configured but it's not being applied correctly

#### 2. Attack Configuration Mismatches
**Templates affected:** warrior, spy, zombie
**Issue:** Different attack configurations leading to damage/weapon type differences
**Example:**
- Warrior: Expected `1d12 + 1 bludgeoning` vs YAML `2d6 + 1 slashing`
- Different base weapon types or damage dice

#### 3. Attribute and Role Mismatches
**Templates affected:** simulacrum, frost-giant, berserker, bugbear
**Issue:** Different ability scores, roles, or creature properties
**Examples:**
- simulacrum: role `skirmisher` vs `soldier`, missing flight speed
- Different CON scores affecting HP calculations

#### 4. Missing Creature Properties
**Templates affected:** simulacrum, frost-giant
**Issue:** Missing condition immunities, additional creature types, speeds
**Examples:**
- simulacrum missing exhaustion/poisoned immunities, humanoid type
- Missing fly speeds in some templates

### B. Framework/Parser Issues (Deeper Problems)

These indicate bugs in the YAML template parsing or processing framework.

#### 1. ValidationError in AC Template Processing
**Template affected:** spirit
**Error:** `pydantic_core._pydantic_core.ValidationError: 2 validation errors for ResolvedArmorClass`
**Root cause:** AC template `flat` with `ac: 13` not being parsed correctly
**Fix needed:** Debug the AC template parsing for flat AC values

#### 2. IndexError in Template Processing
**Template affected:** thug
**Error:** `IndexError: list index out of range`
**Root cause:** Unknown - requires debugging the YAML template processing pipeline
**Fix needed:** Add error handling or fix list access in template processor

### C. Design/Implementation Differences (Complex)

These represent intentional or structural differences between Python and YAML implementations.

#### 1. Damage Compensation System
**Templates affected:** Multiple (spy, mage, simulacrum, etc.)
**Issue:** Different multiattack counts leading to automatic damage modifier compensation
**Example:** 
- Python: 3 attacks with 1.33x damage modifier
- YAML: 2 attacks with 2.0x damage modifier
**Analysis:** This might be intentional behavior - YAML system may use different attack optimization

## Detailed Issue Analysis

### Spy Template Analysis
**Python implementation:**
- Uses `secondary_damage_type=DamageType.Poison` 
- Reduces attacks by 1: `stats.with_reduced_attacks(reduce_by=1)`
- Primary attack: Daggers with poison damage
- Single attack with poison secondary damage

**YAML implementation:**
- Has `secondary_damage_type: Poison` configured
- Has `reduced_attacks: 1` configured  
- Missing poison damage in final attack output

**Diagnosis:** YAML parser not correctly applying secondary damage types to attacks.

### Spirit Template Analysis
**Error:** AC template validation failure
**YAML configuration:**
```yaml
ac_templates:
  - template: flat
    ac: 13
```
**Diagnosis:** The `flat` AC template with direct AC value is not being recognized by the validator. Need to check AC template processing.

### Thug Template Analysis
**Error:** IndexError during processing
**Diagnosis:** Need to debug the template processing to identify which list access is failing.

## Priority Fixes

### High Priority (Framework Issues)
1. **Fix spirit AC template validation** - Critical framework bug
2. **Fix thug IndexError** - Critical framework bug
3. **Fix secondary damage type application** - Affects multiple templates

### Medium Priority (Simple Template Fixes)
1. **Fix attack configuration mismatches** (warrior, zombie)
2. **Fix attribute/role mismatches** (simulacrum, frost-giant)
3. **Add missing creature properties** (condition immunities, speeds)

### Low Priority (Design Issues)
1. **Analyze damage compensation differences** - May be intentional
2. **Document expected behavior differences** between Python and YAML systems

## Next Steps

1. **Debug framework issues** - Focus on spirit and thug template failures
2. **Fix secondary damage type processing** - Ensure YAML parser applies secondary damage correctly
3. **Systematically fix simple template issues** - Go through each failing template
4. **Update this document** with progress and remaining issues
5. **Create regression tests** for fixed issues

## Success Metrics

- Target: Reduce failing tests from 23 to under 10
- Priority: Fix all framework issues (ValidationError, IndexError)
- Goal: Achieve 80%+ template compatibility (35+ passing out of 44)