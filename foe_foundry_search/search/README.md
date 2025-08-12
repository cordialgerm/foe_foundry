# Foe Foundry Search Overview

Two types of search:

- **Document Search**: uses a basic `whoosh` index to perform regular keyword search
- **Graph Entity Search**: searches for Foe Foundry Monsters and Powers by first finding relevant documents, and then doing a Graph Query on the Foe Foundry Knowledge Base to return the relevant entities


## Document Search

The Document Search system provides fast, full-text search capabilities across all Foe Foundry content using the [Whoosh](https://whoosh.readthedocs.io/) search engine. Here's how it works:

### Index Structure & Schema

The system maintains a search index stored in `cache/whoosh_indx/` with the following schema:
- **doc_id**: Unique identifier for each document (stored, searchable)
- **name**: Document title/name (stored, searchable, sortable)
- **content**: Full document text content (stored, searchable with stemming analysis)

### Document Types

The search indexes three types of documents:
- **monster_ff**: Foe Foundry monster entries
- **monster_other**: External monster references (e.g., SRD, third-party)  
- **power_ff**: Foe Foundry power/ability descriptions

### Indexing Process

1. **Document Collection**: All documents are gathered via `iter_documents()` from various data sources
2. **Text Processing**: Content is converted to lowercase and analyzed using Whoosh's `StemmingAnalyzer` for improved matching
3. **Index Creation**: Documents are indexed with their metadata and full content
4. **Caching**: The index is persisted to disk for fast subsequent searches

### Search Implementation

**Query Processing:**
- Uses `MultifieldParser` to search across both `name` and `content` fields simultaneously
- Field boosting: `name` matches are weighted 3x higher than `content` matches
- Stemming analysis enables matching of word variations (e.g., "running" matches "run")

**Result Ranking:**
- Combines relevance scoring from both fields with boost weights
- Higher scores for exact name matches vs. content mentions
- Returns detailed match metadata including which fields matched and specific terms

**Enhanced Results:**
Each search result includes:
- **Document**: Full document object with metadata
- **Score**: Relevance score for ranking
- **Matched Fields**: Which fields contained matches (`name`, `content`, or both)
- **Matched Terms**: Specific terms that triggered the match
- **Highlighted Content**: Text snippets with search terms highlighted for display

### Caching Strategy

- **Lazy Loading**: Index is loaded on first search request via `@cached_property`
- **Persistent Storage**: Index persists between application restarts in `cache/whoosh_indx/`
- **Auto-Recovery**: If index loading fails, automatically rebuilds from source documents
- **Manual Management**: Provides `clean_document_index()` to force index regeneration

---

## Graph Entity Search

1. **Alias Resolution:** Direct match against known aliases returns mapped FF_MON.
2. **Document Search:** Find documents using `search_documents()` above
3. **Graph Propagation:** Use the matched document nodes as entrypoints and perform a graph query to find the requested entity types, propogating scores across the graph
4. **Ranking & Explainability:** Results are ranked by combined score, and top paths are shown to explain why each result was returned.