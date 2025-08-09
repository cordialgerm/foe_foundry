# PRD: Graph Construction for Foe Foundry GraphRAG

## Purpose
This PRD describes the initial step for building the graph portion of the Foe Foundry GraphRAG system. The goal is to set up a NetworkX graph that models relationships between documents and monsters, as described below.

## Node Types
- **DOC**: Document nodes representing background RPG documents (SRD, blogs, sourcebooks, etc.)
  - Attributes: `id`, `title`, `text`
- **MON**: Monster nodes representing published monster statblocks (SRD or 3rd party)
  - Attributes: `id`, `name`, `is_srd`, `description`
- **FF_MON**: nodes representing Foe Foundry monsters
  - Attributes: `monster_key`, `template_key`

## Edge Types
- **DOC → MON**: Document is about/defines this monster. Attribute: `relevancy` ∈ [0, 1]
- **MON → MON (SRD mapping)**: Mapping from MON node to corresponding SRD MON node, as defined in `monster_to_srd_a_b.json`.
- **MON → FF_MON**: Mapping representing an alias or equivalency between Foe Foundry Monsters as 3rd party or published monsters
- **FF_MON → FF_MON**: Mapping representing a monster being part of a monster family

## Data Sources
- Documents: `foe_foundry_search.documents` (DOC nodes)
- Monsters: `foe_foundry_search.documents.MonsterDocument` (MON nodes)
- Monster metadata: `MonsterDocumentMeta` (MON nodes)
- SRD mappings: `monster_to_srd_a_b.json` (MON → MON edges)

## Implementation Steps
1. **Extract DOC nodes** from the documents module.
2. **Extract MON nodes** from MonsterDocument and MonsterDocumentMeta.
3. **Create FF_MON nodes** using
4. **Create DOC → MON edges** based on document-to-monster relationships.
5. **Create MON ↔ MON edges** for similar monsters (family, variants).
6. **Create MON → MON edges** using SRD mappings from `monster_to_srd_a_b.json`.
7. **Build the graph** using NetworkX, with appropriate node and edge attributes.
