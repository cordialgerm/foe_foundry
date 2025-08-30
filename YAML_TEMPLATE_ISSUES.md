# YAML Template Parser Issues and Analysis

## Overview
This document tracks issues identified during systematic YAML template alignment with Python templates. 

**Current Status**: 19 passing, 24 failing template tests (44% success rate)

**Passing Templates**: animated-armor, assassin, bandit, basilisk, chimera, cultist, dire-bunny, druid, gorgon, guard, ghoul, knight, medusa, merrow, owlbear, scout, vrock, wight, wolf

## Issue Categories

### 1. Easy Configuration Fixes

These are straightforward YAML template configuration issues that can be fixed by adjusting values:

#### Secondary Damage Type Issues
- **balor**: ✅ ATTEMPTED - Attack damage splitting issue where Python has single lightning damage, YAML splits into lightning + fire
  - **Parser Issue**: `split_secondary_damage: false` parameter not properly preventing damage splitting
  - **Root Cause**: YAML parser still applies `secondary_damage_type: Fire` even when `split_secondary_damage: false` is set
- **zombie**: ✅ ATTEMPTED - Attack should not split damage (bludgeoning only) but YAML splits into bludgeoning + poison  
  - **Parser Issue**: Override of `split_secondary_damage: false` in variant not working properly
  - **Root Cause**: Variant-level attack overrides not properly preventing inheritance of secondary damage behavior
- **skeleton**: ✅ ATTEMPTED - Additional attack secondary damage amount mismatch (1d6 vs 2d6 necrotic)
  - **Parser Issue**: Global secondary damage type being applied to all attacks despite per-attack controls
  - **Root Cause**: Attack-level `split_secondary_damage: false` not preventing global secondary damage inheritance
- **spy**: Missing secondary damage types in both main and additional attacks

#### Attribute Alignment Issues  
- **berserker**: WIS attribute mismatch (7 vs 8) + secondary damage type randomization mismatch (thunder vs lightning)
  - **Species-Specific Issue**: WIS varies by species (7 vs 8) - parser limitation
  - **Randomization Issue**: Different random seeds producing different secondary damage types
- **warrior**: Primary damage type mismatch (bludgeoning vs slashing) - species-dependent weapon selection
  - **Species-Dependent Logic**: Python template selects weapons by species, YAML cannot replicate

### 2. Multiattack/Damage Compensation Issues

These templates have different attack counts between Python and YAML, causing automatic damage compensation:

#### Attack Count Mismatches
- **gelatinous-cube**: multiattack 1 vs 2, damage_modifier 2.0 vs 1.0
- **frost-giant**: multiattack 2 vs 3, damage_modifier 1.5 vs 1.0  
- **spy**: multiattack 1 vs 2, damage_modifier 1.8 vs 0.9
- **priest**: Complex multiattack scaling issues
- **ogre**: Attack count and damage compensation
- **orc**: Attack count and damage compensation

**Pattern**: When attack counts differ, the system automatically adjusts damage_modifier to maintain balanced DPR (Damage Per Round).

### 3. Parser Design Limitations

These issues require parser enhancements or architectural changes:

#### Critical Parser Bugs
- **spirit**: Pydantic validation error - flat AC templates not parsing correctly
  ```
  ValidationError: Input should be a valid integer [type=int_type, input_value=<_FlatAmorClassTemplate>]
  ```
- **golem**: Template parsing error during variant resolution
- **thug**: Additional attacks processing missing - attacks not being generated

#### Missing Parser Features
- **bugbear**: additional_types not combining with primary creature_type
  ```
  additional_types mismatch: (removed: {humanoid, fey})
  ```
- **frost-giant**: Complex combination of HP, speed, immunities, skills misalignment
- **kobold**: Multiple structural issues (additional_types, darkvision, complex attributes)
- **lich, mage, manticore**: Complex template logic not supported in YAML parser
- **hollow-gazer**: HP, attributes, creature type processing discrepancies
- **hydra**: Multiattack scaling + additional_types support needed
- **mimic, simulacrum**: Template architectural differences

#### Species-Specific Logic Limitations
- **berserker**: WIS attribute varies by species (7 vs 8)
- **warrior**: Species-dependent attack selection (dwarf→bludgeoning, human→slashing)

**Pattern**: Parser cannot handle logic that varies behavior based on species selection.

## Specific Error Patterns Discovered

### Attack Processing Issues
1. **Split damage override failure**: `split_secondary_damage: false` not preventing damage splitting
2. **Global secondary damage inheritance**: Attack-level controls not overriding template-level settings
3. **Variant inheritance problems**: Attack overrides in variants not properly replacing common settings
4. **Additional attacks missing**: Templates not generating additional_attacks from YAML `attacks.additional` sections
5. **Range format inconsistencies**: "100ft." vs "100/400ft." parsing differences

### Template Resolution Issues  
1. **Variant name mapping**: Complex variant resolution failing (golem template)
2. **AC template validation**: Flat AC templates causing Pydantic validation errors
3. **Creature type combination**: additional_types not merging with primary creature_type

### Randomization & Determinism Issues
1. **Secondary damage type selection**: Random lists producing different results between Python and YAML
2. **Species-specific randomization**: Different attribute/equipment selection by species
3. **Power selection consistency**: Need deterministic random seed handling

### Attribute/Stats Processing
1. **Skills expertise vs proficiency**: Incorrect application of skill bonuses
2. **Conditional logic**: CR-based saves and attributes not fully implemented  
3. **Species variations**: Templates using `species: all` need individual species stat differences

## Architectural Challenges

### YAML Parser Core Issues Identified
1. **Attack configuration inheritance**: Complex inheritance patterns not working properly
2. **Secondary damage control**: Multiple control mechanisms not working in coordination
3. **Species-specific attributes**: Parser can't handle attribute variations by species  
4. **Damage/multiattack compensation**: Missing automatic damage scaling when attack counts differ
5. **Additional creature types**: Parser doesn't combine primary + additional creature types
6. **Complex variant logic**: Templates need different behaviors per monster variant
7. **Species-dependent logic**: Parser lacks species-specific attack/equipment selection

### Design Patterns Identified
1. **Damage compensation pattern**: When multiattack differs, damage_modifier adjusts automatically
2. **Species-specific pattern**: Many templates need different stats/equipment per species
3. **Template variant pattern**: Complex templates need different configurations per monster variant
4. **Secondary damage pattern**: Many templates split damage types but parser struggles with placement
5. **Override inheritance pattern**: Variant-level settings not properly overriding common settings

## Recommendations

### High Priority Parser Fixes
1. Fix attack configuration inheritance and override mechanisms (balor, zombie, skeleton)
2. Fix Pydantic validation error for flat AC templates (spirit)
3. Implement proper secondary damage type control and split behavior
4. Add support for additional_types combination
5. Fix additional attacks processing (thug)

### Medium Priority Enhancements
1. Implement attack count compensation in YAML parser  
2. Add support for complex variant logic
3. Enhance damage type splitting behavior with proper control mechanisms
4. Improve range format handling
5. Fix randomization consistency between Python and YAML templates

### Low Priority Improvements
1. Implement species-specific attribute variations
2. Add support for dynamic template selection based on species
3. Implement complex conditional logic for CR-based scaling
4. Add support for template inheritance patterns

## Test Results Summary

**Success Rate**: 44% (19/43 templates passing)

**Categories**:
- Easy configuration fixes: ~6 templates (balor, zombie, skeleton attempted but hit parser issues)
- Parser design issues: ~12 templates  
- Complex species/randomization issues: ~6 templates

**Critical Finding**: Many "easy" fixes are actually parser architectural issues rather than simple configuration problems. The attack configuration system has fundamental inheritance and override problems.

**Note**: Enhanced error messages now provide excellent diagnostic information, clearly distinguishing between simple configuration problems and complex parser architectural challenges.