# Template Gaps Analysis - Individual Fixes Needed

Based on comprehensive testing, here are the templates that need individual attention:

## High Priority Templates (Multiple Issues)

### 1. BasiliskTemplate
- **Issues**: Attack count mismatch (1 vs 0), Primary role mismatch (bruiser vs soldier)
- **Status**: FAIL - 2 failures per variant
- **Variants**: basilisk, basilisk-broodmother

### 2. BugbearTemplate  
- **Issues**: Attack count mismatch (1 vs 0), Primary role mismatch (ambusher vs soldier)
- **Status**: FAIL - 2 failures per variant
- **Variants**: bugbear, bugbear-brute, bugbear-shadowstalker

### 3. GhoulTemplate
- **Issues**: Attack count mismatch, Primary role mismatch
- **Status**: FAIL - 2 failures per variant  
- **Variants**: ghoul, ghast, ghoul-master (ERROR)

### 4. GelatinousCubeTemplate
- **Issues**: Attack count mismatch, Primary role mismatch, Size mismatch (large vs huge)
- **Status**: FAIL - 2 failures per variant
- **Variants**: gelatinous-cube, gelatinous-cube-elder (ERROR)

### 5. WolfTemplate
- **Issues**: Size mismatch (large vs medium), Creature type mismatch (monstrosity vs beast)
- **Status**: FAIL - Multiple issues
- **Variants**: dire-wolf, winter-wolf, fellwinter-packlord

## Medium Priority Templates (Single Issues)

### 6. CultistTemplate
- **Issues**: Primary role mismatch
- **Status**: FAIL - 1 failure per variant
- **Variants**: cultist, cultist-fanatic, cultist-grand-master

### 7. ChimeraTemplate
- **Issues**: Attack count mismatch, Primary role mismatch
- **Status**: FAIL/ERROR - 2 failures, 1 ERROR
- **Variants**: chimera, chimera-matriarch (ERROR)

## Simple Fix Templates (CR Issues)

### 8. PriestTemplate
- **Issues**: CR mismatch (0.25 vs 0.125)
- **Status**: Mixed results
- **Variants**: acolyte (FAIL), priest (PASS), high-priest (PASS)

### 9. SkeletonTemplate  
- **Issues**: CR mismatch (0.25 vs 0.125)
- **Status**: Mixed results
- **Variants**: skeleton (FAIL), skeleton-warrior (PASS), skeleton-champion (PASS)

### 10. ZombieTemplate
- **Issues**: CR mismatch (0.25 vs 0.125) 
- **Status**: Mixed results
- **Variants**: zombie (FAIL), zombie-brute (PASS), zombie-horror (PASS)

## Error Status Templates (Need Investigation)

### 11. AnimatedArmorTemplate
- **Issues**: BaseStatblock.grant_resistance_or_immunity() parameter errors
- **Status**: ERROR - All variants
- **Variants**: animated-armor, animated-runeplate

### 12. BalorTemplate  
- **Issues**: BaseStatblock.grant_resistance_or_immunity() parameter errors
- **Status**: ERROR - All variants
- **Variants**: balor, balor-dreadlord

### 13. DireBunnyTemplate
- **Issues**: Validation errors (2 validation errors)
- **Status**: ERROR - All variants  
- **Variants**: dire-bunny, dire-bunny-alpha, dire-bunny-matriarch

## Work Plan

1. **Start with BasiliskTemplate** - Clear attack count + role issues
2. **Fix BugbearTemplate** - Similar pattern to basilisk
3. **Address GhoulTemplate** - Attack count + role 
4. **Tackle GelatinousCubeTemplate** - More complex with size
5. **Fix WolfTemplate** - Size + creature type issues
6. **Address CR mismatch templates** - Simple fixes
7. **Investigate ERROR templates** - Deeper debugging needed

Target: Improve from current 20.0% (28/140) to 60%+ success rate.