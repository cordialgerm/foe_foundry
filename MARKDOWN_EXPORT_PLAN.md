# Markdown Export Formats - Design Plan

## Overview
This document outlines the design for implementing multiple markdown export formats for Statblock objects in the Foe Foundry project.

## Goal
Support multiple different markdown formats for a `Statblock`:
- 5E SRD - basic MD format used by the 5ESRD github project
- GMBinder - markdown format supported by the GMBinder website  
- Homebrewery v3 - new markdown-based format of the homebrewery website
- Black Flag SRD - basic MD format supported by the Project Black Flag markdown format

## Implementation Architecture

### Core Components
1. **Jinja Templates**: Create separate `.md.j2` templates for each format
2. **Render Function**: New `render_statblock_markdown` function similar to `render_statblock_fragment`
3. **Reuse Existing**: Leverage `StatblockJinjaContext.from_statblock(stats)` for data extraction
4. **Module Integration**: Add exports to `foe_foundry_data.jinja` module

### File Structure
```
foe_foundry_data/jinja/
├── statblock-5esrd.md.j2       # 5E SRD format
├── statblock-gmbinder.md.j2    # GMBinder format  
├── statblock-homebrewery.md.j2 # Homebrewery v3 format
├── statblock-blackflag.md.j2   # Black Flag format
└── statblock.py                # Updated with markdown functions
```

### API Design
```python
def render_statblock_markdown(
    stats: Statblock, 
    format: str = "5esrd"
) -> str:
    """Renders a statblock as markdown for the specified format
    
    Args:
        stats: The Statblock object to render
        format: One of "5esrd", "gmbinder", "homebrewery", "blackflag"
    
    Returns:
        Markdown string representation of the statblock
    """
```

## Format Implementation Details

### 5E SRD Format
- Simple, clean markdown with standard headers
- Ability scores in table format with modifiers
- Straightforward section organization
- Template: `statblock-5esrd.md.j2`

### GMBinder Format  
- Uses blockquote syntax with special formatting
- Requires specific header separators (`___`)
- Centered ability score table
- Template: `statblock-gmbinder.md.j2`

### Homebrewery v3 Format
- Uses `{{monster}}` blocks with special syntax
- Double colon syntax for properties (`::`)
- Support for framed/unframed and wide variants
- Template: `statblock-homebrewery.md.j2`

### Black Flag Format
- Uses markdown tables and simplified ability scores
- Different heading structure and property formatting
- Template: `statblock-blackflag.md.j2`

## Testing Strategy

### Test Monsters
Use the suggested monsters with fixed power selection for reproducible results:
- **Knight** - Medium armor, martial combat abilities
- **Priest** - Spellcasting abilities, divine powers  
- **Spy** - Stealth and deception abilities

### Test Structure
```python
def test_statblock_markdown_5esrd_knight():
    # Generate Knight with fixed powers
    stats = generate_knight_with_fixed_powers()
    markdown = render_statblock_markdown(stats, "5esrd")
    # Validate specific markdown patterns
    assert "# Knight" in markdown
    assert "**Armor Class**" in markdown
    # etc.
```

### Reproducible Generation
Use fixed random seeds and specific power selections to ensure consistent test results across runs.

## Implementation Phases

### Phase 1: Core Infrastructure ✅
- [x] Review existing codebase and templates
- [x] Create design document

### Phase 2: 5E SRD Implementation
- [ ] Create `statblock-5esrd.md.j2` template
- [ ] Implement `render_statblock_markdown` function
- [ ] Create basic tests with Knight, Priest, Spy

### Phase 3: Additional Formats
- [ ] Implement GMBinder format template
- [ ] Implement Homebrewery v3 format template  
- [ ] Implement Black Flag format template
- [ ] Extend tests for all formats

### Phase 4: Integration
- [ ] Update module exports in `__init__.py`
- [ ] Add comprehensive test coverage
- [ ] Validate all formats with test monsters

## Technical Considerations

### Template Reuse
- Leverage existing Jinja filters like `fix_punctuation`, `sluggify`
- Use `StatblockJinjaContext` data structure without modification
- Reuse ability score and stat formatting logic

### Error Handling
- Validate format parameter in render function
- Graceful fallback for unknown formats
- Clear error messages for invalid inputs

### Performance
- Templates loaded once and cached by Jinja environment
- Minimal overhead over existing HTML rendering
- No additional data processing required

## Success Criteria
- [ ] All four markdown formats generate valid output
- [ ] Tests pass consistently with fixed monster generation
- [ ] Output matches provided format examples
- [ ] Integration with existing Jinja infrastructure
- [ ] Clean, maintainable template code