# PRD: Foe Foundry Monster Research Agent (LangGraph Deep Research Flow)

## Overview
The **Monster Research Agent** is a LangGraph-based system that coordinates multiple research nodes to build out **novel monster inspirations** for the Foe Foundry 5E Monster Generator. Each node contributes structured findings to a shared **parent research context**, which accumulates insights for later stages of monster generation.

This PRD defines:
- How the parent research context is managed and updated
- How research nodes are invoked
- How results are normalized, filtered, and merged into the global state

---

## Goals
1. **Novelty:** Each node must contribute genuinely new angles (monsters, abilities, lore) without repeating prior context.  
2. **Scalability:** Parent context grows incrementally as multiple nodes execute; downstream nodes receive only a compressed summary.  
3. **Reliability:** Output must conform to strict schemas (`scratchpad` and `related-monster`) for automated consumption.  
4. **Efficiency:** Limit tool calls and block outputs (≤3 per node) to control token use and noise.  

---

## Parent Research Context

### Definition
The **parent research context** is a compact rolling summary of all prior findings across research nodes.  
It is stored in structured form and injected into each new node’s prompt under the variable `research_summary`.

### Composition
- **Consolidated `research_summary`:**  
  A compressed log of all node `research_summary` fields (both from scratchpad and related-monster blocks).  
- **Deduplication / Merge Rules:**  
  - Drop near-duplicate summaries  
  - Prioritize higher `relevance` findings  
  - Cap total summary length (e.g. ~1,000 tokens) with older/low-relevance findings trimmed  

### Example Parent Summary
```yaml
research_summary:
  - "Air Elementals can serve as a baseline for a Lightning Elemental; notable for speed, resistances, whirlwind adaptation."
  - "Abbassy-like self-wounding armored berserker traits could inspire a dwarf bound in iron."
  - "Shadow hounds provide stealth + fear auras that align with the user’s description of a nightmare predator."
```

---

## Research Node Invocation

### Node Inputs
- `research_summary` (from parent context, trimmed/merged)  
- `monster_description` (user’s high-level goal)  
- `constraints` (optional: CR range, role, environment, etc.)  

### Node Behavior
- Align with the monster concept  
- Execute **2–5 tool calls** (web search, SRD lookup, etc.)  
- Distill results into **1–3 markdown blocks**:  
  - `scratchpad` (background powers, motifs, lore hooks)  
  - `related-monster` (summarized candidate statblocks with adaptation ideas)  

### Node Outputs
- **Blocks** (markdown with YAML frontmatter)  
- Each block includes a `research_summary` field that feeds into the parent context.  

---

## Orchestration in LangGraph

### Architecture
- **Parent Supervisor Node**  
  - Holds the global `research_summary`  
  - Manages deduplication, trimming, and relevance scoring  
  - Routes new summaries downstream  
- **Research Worker Nodes** (N parallel or sequential)  
  - Each executes the refined prompt described earlier  
  - Bound with search tools via `bind_tools`  
  - Return structured blocks  
- **Reducer Node**  
  - Normalizes worker outputs  
  - Extracts `research_summary` from each block  
  - Updates the parent context  
  - Enforces schema validity & word limits  

### Flow
1. **Initialization**  
   - User provides `monster_description` (e.g. “a lightning-infused werewolf alpha”).  
   - Empty `research_summary` context created.  
2. **Node Invocation**  
   - Parent passes `{monster_description, research_summary}` to a worker node.  
   - Worker executes searches + outputs ≤3 blocks.  
3. **Aggregation**  
   - Reducer parses outputs, extracts `research_summary`, merges into parent.  
   - Deduplication step ensures novelty.  
4. **Iteration**  
   - Process repeats with new nodes (parallel or sequential).  
5. **Finalization**  
   - Final parent research summary is fed into the **Monster Synthesis Agent** to build statblocks or templates.  

---

## Implementation Notes

### Context Management
- Store parent summary in a simple JSON/YAML structure.  
- Use LangChain reducers to merge outputs after each worker run.  
- Trim oldest or lowest-relevance entries if token budget exceeded.  

### Tool Binding
- Define search tools with crisp, contrasting descriptions (e.g. `srd_lookup` vs. `web_search`).  
- Use `bind_tools` so schemas are injected automatically.  
- Do not paste full tool schemas into the prompt; system prompt only explains **when/why** to use each tool.  

### Validation
- Regex or JSON schema validation on outputs:  
  - Must start with ```md  
  - Must contain frontmatter with `type`, `research_summary`, `source_refs`  
  - Length check: scratchpad ≤120 words, related-monster ≤160 words  
- Drop blocks failing validation.  

### Parallelization Strategy
- **Sequential**: safer, easier dedupe, fewer collisions in parent summary.  
- **Parallel**: faster but needs stronger deduplication downstream.  

---

## Success Criteria
- Parent research context grows incrementally with no >10% redundancy.  
- Each node yields ≤3 blocks with valid schema.  
- Research summaries from N nodes can be stitched into a coherent design direction for monster generation.  
- Search tool calls per node average ≤5.  
- Final monster synthesis benefits directly from research context (novel powers, templates, or statblock adaptations).  