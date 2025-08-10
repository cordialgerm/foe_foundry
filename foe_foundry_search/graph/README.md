# Foe Foundry Graph Overview

## What is the Foe Foundry Graph?
The Foe Foundry graph is a directed, multi-type graph that models relationships between RPG monsters, documents, families, and powers. It is designed to power fast, explainable, and composable search and retrieval for the Foe Foundry monster database.

![foe_foundry_graph_sampled.png](foe_foundry_graph_sampled.png)

## What is it Useful For?
- **Monster Search & Discovery:** Enables keyword and graph-based search for monsters, supporting alias resolution, structured filters (CR, type, environment, family), and indirect matches via graph propagation.
- **Explainability:** Surfaces the reasoning path for each result, showing how documents, statblocks, and relationships contributed to the match.
- **Integration:** Provides a flexible structure for integrating new filters, semantic search, and additional content types.
- **Scalability:** Handles thousands of monsters and tens of thousands of documents efficiently using sparse graph representations and CPU-friendly algorithms.

## Node & Edge Model
### Node Types
- **DOC**: Background RPG documents (SRD, blogs, sourcebooks). Attributes: `id`, `monster_key`, `text`.
- **MON**: Published monster statblocks (SRD or 3rd party). Attributes: `id`, `name`, `is_srd`, `description`.
- **FF_MON**: Foe Foundry monster instances. Attributes: `monster_key`, `template_key`, references to SRD/other monsters.
- **FF_FAM**: Monster families. Attributes: `family_key`, member monsters.
- **POW**: Powers. Attributes: `power_key`, granted monsters.

### Edge Types
- **DOC → MON**: Document describes a monster (`type="about"`, `relevancy`).
- **MON → MON**: Similar monsters via SRD mapping (`type="similar"`).
- **FF_MON → MON**: FF monster implements SRD/other monster (`type="implemented"`).
- **FF_FAM → FF_MON**: Family membership (`type="member"`).
- **POW → FF_MON**: Power grants to monster (`type="grants"`).

