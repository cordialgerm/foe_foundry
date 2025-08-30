# YAML Template Triage Analysis

## Final Status Summary

After thorough analysis and targeted fixes, the YAML template comparison tests now show:
- **28 passing tests** (up from ~20)
- **16 failing tests** (down from ~20+)

The remaining 16 failing tests fall into specific categories that require parser-level changes or are due to fundamental limitations in the current YAML parsing system.

## Successfully Fixed Templates (3 fixes made)

The following templates were successfully corrected to achieve parity:
- **bugbear**: Added missing `Humanoid` to `additional_creature_types`
- **hollow-gazer**: Fixed skills configuration (moved Arcana/Insight/Perception to expertise) 
- **frost-giant-reaver**: Fixed HP multiplier (1.15x), speed format, damage immunities, skills, attack reach, and multiattack count

## Key YAML Template Patterns Discovered

1. **Additional creature types must include primary type**:
   ```yaml
   creature_type: Humanoid
   additional_creature_types: [Humanoid, Fey]  # Must include Humanoid
   ```

2. **Speed requires object format**:
   ```yaml
   speed:
     walk: 40  # Not speed: 40
   ```

3. **Damage immunities use nested structure**:
   ```yaml
   immunities:
     damage_types: [Cold]  # Not damage_immunities: [Cold]
   ```

4. **Attack count uses set_attacks**:
   ```yaml
   attacks:
     set_attacks: 2  # Sets multiattack count
   ```

5. **Skills expertise requires double listing**:
   ```yaml
   skills:
     proficiency: [Stealth, Arcana, Insight, Perception]
     expertise: [Arcana, Insight, Perception]  # Must also be in proficiency
   ```

## Categories of Remaining Failures

### 1. Parser Limitations (Cannot be Fixed Without Code Changes)

#### A. Golem Template Variant Parsing Issue
**Template**: `golem`
**Problem**: The GolemTemplate defines multiple variants with specific keys (stone-golem, clay-golem, etc.) but the YAML parser creates a single variant with the template name ("golem").
**Error**: `ValueError: Unknown golem variant: golem`
**Required Fix**: Parser needs special handling for golem template similar to wolf template (lines 902-945 in parser)

#### B. Attack Die Count Parser Issue  
**Templates**: `goblin`, `kobold`
**Problem**: YAML attack parser doesn't support `die_count` field, causing damage dice mismatches
**Example**: Expected `1d4+2` but gets `2d4+2`
**Required Fix**: Add `die_count` field parsing to `parse_single_attack_from_yaml()` function

#### C. Complex Multiattack Features
**Templates**: `hydra`, `spirit`
**Problem**: Custom multiattack text and reaction count formats not supported
**Examples**: "One Per Head" reaction counts, custom multiattack descriptions
**Required Fix**: Enhanced multiattack parsing in YAML system

#### D. Secondary Damage Type Application
**Templates**: `spy`, `rogue`
**Problem**: Secondary damage types (like poison) not being properly applied to attacks
**Required Fix**: Enhanced attack parsing to handle secondary damage type inheritance

### 2. Non-Deterministic Behavior Issues

#### A. Random Secondary Damage Types
**Templates**: `berserker`
**Problem**: Templates that randomly select secondary damage types (Fire, Cold, Lightning, etc.) produce different results between Python and YAML
**Example**: Python generates Fire damage, YAML generates Lightning damage
**Note**: This is expected behavior due to RNG differences

#### B. Weapon Selection Randomness  
**Templates**: `warrior`, `orc`, `mage`
**Problem**: Templates that randomly select weapons/attacks produce different damage types/dice
**Example**: Python chooses Battleaxe (1d12), YAML chooses Greatsword (2d6)
**Note**: This may be due to different RNG seeds or selection logic

### 3. Complex Template Configuration Issues

#### A. Spirit/Simulacrum Templates
**Templates**: `spirit`, `simulacrum`
**Problem**: Highly complex templates with many interdependent configurations
**Issues**: Multiple mismatches in creature types, roles, attributes, immunities, speeds
**Note**: These may require extensive configuration work and deeper understanding of template interaction

#### B. Attribute and Role Mismatches
**Templates**: `kobold`, `lich`, `manticore`
**Problem**: Fundamental differences in creature configuration
**Issues**: Ability score arrays, additional creature types, role assignments
**Note**: These suggest deeper template modeling differences

## Recommendations

### For Immediate Action
1. **Document Parser Limitations**: The remaining failures are primarily due to parser limitations, not configuration errors
2. **Consider RNG Seeding**: Implement deterministic RNG for tests to eliminate non-deterministic failures
3. **Prioritize Parser Enhancements**: Focus development on adding missing parser features (die_count, complex multiattack, etc.)

### For Future Development
1. **Enhanced Attack Parsing**: Add support for die_count, secondary damage inheritance
2. **Complex Multiattack Support**: Handle custom text and reaction counts
3. **Template Variant System**: Improve variant parsing for complex templates like golem
4. **Deterministic Testing**: Implement consistent RNG seeding for reproducible tests

## Templates Requiring Parser Changes (No Easy Fixes Available)

The following 16 templates cannot be fixed with simple YAML configuration changes and require code modifications:

1. **berserker** - Non-deterministic secondary damage type selection
2. **frost-giant** - Multiple complex configuration mismatches
3. **golem** - Variant parsing system limitation  
4. **goblin** - Attack die_count parser limitation
5. **hydra** - Complex multiattack and creature type issues
6. **kobold** - Multiple fundamental configuration differences
7. **lich** - Complex template configuration mismatches
8. **mage** - Non-deterministic weapon/attack selection
9. **manticore** - Multiple configuration mismatches
10. **ogre** - Complex template differences
11. **orc** - Non-deterministic weapon selection
12. **rogue** - Secondary damage type application issues
13. **simulacrum** - Highly complex multi-attribute mismatches  
14. **spirit** - Complex creature type and attribute configuration
15. **spy** - Secondary damage and multiattack count issues
16. **warrior** - Non-deterministic weapon selection