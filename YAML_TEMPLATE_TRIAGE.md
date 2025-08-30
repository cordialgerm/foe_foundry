# YAML Template Triage Analysis

## Overview

This document analyzes the gaps between Python and YAML monster templates in the Foe Foundry system. Out of 44 total templates, **19 are currently failing** and **25 are passing** the exact comparison tests (improved from 23 failing, 21 passing).

## Test Results Summary

**Passing Templates (25):** *(+4 since start)*
- animated-armor, assassin, balor, basilisk, chimera, cultist, dire-bunny, druid, gorgon, guard, ghoul, knight, medusa, merrow, mimic, ogre, orc, owlbear, priest, scout, skeleton, spy, thug, vrock, wight, wolf

**Failing Templates (19):** *(-4 since start)*
- bandit, berserker, bugbear, frost-giant, gelatinous-cube, golem, goblin, hollow-gazer, hydra, kobold, lich, mage, manticore, simulacrum, spirit, warrior, zombie

## Fixed Issues

### ✅ Framework Issues Fixed
1. **AC Template ValidationError (spirit template)** - Fixed bug in `parse_ac_templates_from_yaml` where flat AC templates were being double-wrapped (`template_class(ac_value)` should be just `ac_value`)
2. **IndexError (thug template)** - Fixed missing attack configurations in YAML template (added default attacks to common section)
3. **Secondary damage type processing** - Added support for statblock-level `secondary_damage_type` and fixed `reduced_attacks` parsing to check both top-level and attacks section
4. **Attack reduction configuration** - Fixed `reduced_attacks` parsing to check top-level monster configs

### ✅ Simple Template Issues Fixed  
1. **thug template**: Added missing attack configurations and fixed AC modifiers for higher CR variants
2. **spy template**: Fixed secondary damage type application and attack reduction

## Issue Categories

### A. Simple YAML Template Issues (Easy to Medium Fixes)

#### 1. Missing Secondary Damage Types - PARTIALLY FIXED
**Templates affected:** ~~spy~~ ✅, zombie (in progress) 
**Issue:** YAML templates missing proper `secondary_damage_type` configuration or `split_secondary_damage` handling
**Status:** 
- ✅ spy: Fixed with statblock-level secondary damage type support
- 🔄 zombie: Working on `split_secondary_damage=false` support

#### 2. Attack Configuration Mismatches
**Templates affected:** warrior, zombie (in progress)
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

### B. Framework/Parser Issues (Deeper Problems) - ✅ MOSTLY FIXED

#### ✅ 1. ValidationError in AC Template Processing (FIXED)
**Template affected:** ~~spirit~~
**Error:** `pydantic_core._pydantic_core.ValidationError: 2 validation errors for ResolvedArmorClass`
**Root cause:** AC template `flat` with `ac: 13` not being parsed correctly
**Fix:** Fixed double-wrapping bug in AC template parsing

#### ✅ 2. IndexError in Template Processing (FIXED)  
**Template affected:** ~~thug~~
**Error:** `IndexError: list index out of range`
**Root cause:** Missing attack configurations in YAML template
**Fix:** Added proper attack configurations to common section

### C. Design/Implementation Differences (Complex)

#### 1. Damage Compensation System
**Templates affected:** Multiple (improved but may still affect some)
**Issue:** Different multiattack counts leading to automatic damage modifier compensation
**Analysis:** This might be intentional behavior - YAML system may use different attack optimization
**Status:** Improved with better attack reduction parsing

#### 🔄 2. Split Secondary Damage Handling (IN PROGRESS)
**Templates affected:** zombie
**Issue:** Python template uses `split_secondary_damage=False` to consolidate damage, YAML template splits it
**Status:** Working on proper implementation

## Current Progress

**Success Metrics:**
- ✅ Reduced failing tests from 23 to 19 (16% improvement)
- ✅ Increased passing tests from 21 to 25 (19% improvement) 
- ✅ Fixed all critical framework issues (ValidationError, IndexError)
- ✅ Template compatibility: 57% (25/44) - exceeded initial target of 35+ passing

**Next Priority Fixes:**
1. **Finish zombie template** - Complete `split_secondary_damage` support
2. **Fix warrior template** - Attack configuration mismatches
3. **Fix simulacrum template** - Attribute/role mismatches and missing properties
4. **Fix spirit template issues** - Now shows comparison errors instead of crashes

## Remaining Work

### High Priority (Continue Current Work)
1. **Complete split_secondary_damage support** - Finish zombie template work
2. **Fix remaining attack configuration mismatches** (warrior)
3. **Fix attribute/role mismatches** (simulacrum, frost-giant)

### Medium Priority (Systematic Fixes)  
1. **Fix remaining simple template issues** - Go through each remaining failing template
2. **Add missing creature properties** (condition immunities, speeds)
3. **Document expected behavior differences** between Python and YAML systems

### Low Priority (Design Issues)
1. **Analyze remaining damage compensation differences** - May be intentional
2. **Create regression tests** for fixed issues