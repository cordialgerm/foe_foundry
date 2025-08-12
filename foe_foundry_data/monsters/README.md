# Monsters Module

## Purpose

The `foe_foundry_data/monsters` module provides enriched data about monsters to downstream APIs and tools throughout the Foe Foundry ecosystem. This module serves as a bridge between the core monster generation system (`foe_foundry.creatures`) and the various consumers that need pre-processed, enriched monster data.

### Key Components

- **`all.py`**: Contains the `_MonsterCache` class that generates and caches all possible monster combinations
- **`data.py`**: Defines the `MonsterModel` dataclass with rich metadata, HTML rendering, and related monster information

### Primary Use Cases

1. **API Endpoints**: The `foe_foundry_site` web application uses this module to serve monster data via REST APIs
2. **Static Site Generation**: MkDocs and other documentation tools consume this data to generate static monster pages
3. **Search Indexing**: The search system indexes the enriched monster data for fast lookup and discovery
4. **Cross-References**: Powers, families, and other systems use this data to find related monsters

## Current Architecture

The module currently uses runtime caching via `@cached_property` decorators:

```python
class _MonsterCache:
    @cached_property
    def one_of_each_monster(self) -> list[MonsterModel]:
        # Generates ALL possible monster combinations at runtime
        # This can take significant time during app startup
```

This approach has performance implications during application startup, as generating "one of each monster" requires:
- Iterating through all templates (100+ templates)
- Generating variants for each template (multiple CRs and roles)
- Creating fully-realized `MonsterModel` instances with HTML rendering
- Processing images, families, and cross-references

## Caching Strategy

### Problem Statement

The `_MonsterCache.one_of_each_monster` property is a performance bottleneck during application startup. This property is accessed by:
- Monster API endpoints for lookups and filtering
- Search indexing during `foe_foundry_search` initialization
- Related monster calculations
- Static site generation processes

The current runtime generation can take several seconds and blocks application startup.

### Proposed Solution: Build-Time Caching

Move monster cache generation from runtime to build-time, similar to existing caching patterns used in:
- `foe_foundry_search/documents/load.py` (document caching)
- `foe_foundry_search/graph/build_graph.py` (graph caching) 
- `foe_foundry/utils/image/cache.py` (image metadata caching)

### Implementation Plan

#### Cache Storage

1. **Cache Directory**: Store cached monster data in `/cache/monsters/`
2. **File Structure**:
   ```
   cache/monsters/
   ├── <monster_key_1>.json
   ├── <monster_key_2>.json
   ├── <monster_key_3>.json
   └── ...
   ```

3. **Data Format**: Serialize individual `MonsterModel` instances to JSON using Pydantic's serialization

#### Build-Time Generation

1. **Build Script Integration**: Add monster cache generation to `scripts/build_site.sh`
2. **Cache Generation**: Create a build-time process that:
   - Iterates through all possible monster combinations (templates × variants × monsters)
   - Generates fully-realized `MonsterModel` instances
   - Saves each monster as an individual `{monster_key}.json` file

#### Runtime Loading

1. **Existing Architecture**: Keep the current `@cached_property` approach in `_MonsterCache`
2. **Disk Loading**: Modify `one_of_each_monster` to load from cached JSON files instead of generating
3. **Fallback Behavior**: Maintain current generation logic as fallback if cache directory is missing
4. **Memory Efficiency**: Individual files allow for potential lazy loading if needed in the future

### Benefits

- **Faster Startup**: Eliminate multi-second delay during application initialization
- **Consistent Performance**: Predictable loading times regardless of monster count
- **Build Optimization**: Cache generation can be parallelized during build process
- **Development Efficiency**: Faster iteration during development and testing

### Implementation Notes

- Follow existing caching patterns in `foe_foundry_search` and `foe_foundry/utils/image`
- Cache regeneration is handled by the build script (`scripts/build_site.sh`) - no automatic invalidation needed
- Maintain backward compatibility during transition period
- Individual JSON files provide flexibility for future optimizations

### Future Considerations

- **Lazy Loading**: Load individual monsters on-demand if memory usage becomes a concern
- **Compression**: Compress JSON cache files to reduce disk usage
- **Parallel Loading**: Utilize multiple threads to load monster files concurrently
- **Cache Warming**: Pre-generate cache for commonly accessed monster subsets
