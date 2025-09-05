# PRD: Monster Codex – Search and Browse Interface

## Overview
The **Monster Codex** is a desktop-first monster browsing and search interface for Foe Foundry that combines **text search**, **creature type filtering**, **challenge rating ranges**, and **live monster previews** into a single unified interface optimized for GMs preparing encounters.

The goal is to enable **fast, precise search** for known monsters and **rich thematic browsing** for inspiration, all without leaving the index view.

---

## Motivation
Existing monster search tools (D&D Beyond, A5E Tools, Monster Manual 2024) have significant UX limitations:
- Poor or slow filtering that makes multi-criteria searches difficult.
- Alphabetical-only or flat lists that hinder thematic discovery.
- No quick preview — requiring full page loads to inspect each monster.
- Low visual differentiation between groups or monster types.

This design addresses those gaps by:
- Allowing **instant filter combinations** across key monster attributes.
- Offering **smart grouping** by family, type, CR, or alphabetical order.
- Providing an **always-visible preview panel** that updates on hover/click.
- Maintaining an aesthetic consistent with Foe Foundry’s dark fantasy brand.

---

## Goals
- **Search efficiently:** Find a known monster quickly via text search and filtering.
- **Filter precisely:** Combine multiple criteria (e.g., “Undead” + “Swamp” + “CR 3–5” + “Artillery”).
- **Browse thematically:** Group monsters by family, type, or CR to inspire encounter ideas.
- **Preview instantly:** See monster details without navigating away from the index.
- **Maintain high information density** for “power user” desktop workflows.

---

## Scope
### In-Scope
- Full-width desktop-first layout with three primary columns:
  1. **Sidebar Filters** (facet selection)
  2. **Monster List** (grouped results)
  3. **Preview Panel** (details)
- Multi-facet filter support for:
  - **Creature Type**
  - **Challenge Rating (CR)** via range slider
  - **Environment**
  - **Monster Family**
  - **Role** (soldier, bruiser, artillery, controller, etc.)
- Grouping toggle: by Family, Challenge, or Name.
- Live preview update on monster hover or click.
- Search bar to narrow results by name or keyword.

### Out-of-Scope
- New monster creation or editing UI.
- Backend filtering/search logic (assumes APIs already provide relevant data).

---

## Desktop Design Choices

![codex-desktop.png](codex-desktop.png)

### Layout
- **Left Sidebar** — Persistent filter panel with pill-style toggles for each facet, a CR slider, and grouping buttons.
- **Center List** — Scrollable vertical list of monsters, grouped under headers matching the current grouping mode.
  - Each monster row: name + CR, with optional background texture.
  - Active monster highlighted.
- **Right Panel** — Monster preview showing:
  - Large monster image.
  - Name, CR, Role.
  - Tags for Family, Type, Environment.
  - Short description/flavor text.
  - Action buttons (e.g., “Forge”, “Share”).
  - Related monsters list with CRs.

### Filtering
- Pill-style facet controls for **Creature Type**, **Environment**, and **Role**.
- Range slider for **Challenge Rating**, supporting fractional CR notation.
- Multiple filters can be applied at once, with instant result updates.
- “Organize Foes By” buttons to re-group list view without changing filters.

### Interaction Model
- **Hover** over a monster name updates preview panel (desktop).
- **Click** selects monster, keeps it highlighted for context.
- Filters and search update results in real time without page reload.
- Group headings remain sticky when scrolling for context.

### Visual Style
- Dark theme with red accent color for active filters and highlights.
- Textured backgrounds in monster list rows for thematic flavor.
- High-contrast pills for selected filters.
- Section headers bold and clearly differentiated.

## Mobile Design Choices

![codex-mobile.png](codex-mobile.png)

![codex-mobile-filters.png](codex-mobile-filters.png)

### Layout Adaptation
The mobile interface transforms the three-column desktop layout into a **single-column, stacked approach** optimized for touch interaction and smaller screens:

- **Top Header** — Contains the Foe Foundry branding and hamburger menu button for navigation
- **Search Bar** — Full-width search input with magnifying glass icon, prominently placed for easy access
- **Collapsible Filters** — Red "Filters" section that expands/collapses to reveal filtering options
- **Monster Cards** — Vertically stacked, full-width monster cards with rich visual presentation
- **Inline Preview** — Monster details displayed within expanded cards rather than separate panel

### Filter Interface
The mobile filter system uses a **collapsible accordion approach**:

- **Primary Filter Button** — Red "Filters" button with chevron indicator shows/hides the entire filter panel
- **Category Sections** — Each filter category (Creature Type, Environment, Role, etc.) has its own collapsible section
- **Pill-Style Tags** — Same visual treatment as desktop but optimized for touch targets
- **Range Slider** — Challenge Rating slider adapted for touch interaction with larger touch targets
- **Organize By** — Quick toggle buttons for grouping options (Family, Challenge, Name)

### Monster Card Design
Mobile monster cards feature a **rich, immersive presentation**:

- **Hero Image** — Large, atmospheric background image for each monster
- **Overlay Text** — Monster name and CR overlaid on the image with high contrast
- **Tag Pills** — Creature type, family, and environment tags displayed as colored pills
- **Descriptive Text** — Short flavor description visible on the card
- **Action Buttons** — "Forge" and "Share" buttons prominently displayed
- **Expandable Details** — Tap to reveal full monster statistics and abilities

### Touch Interaction Model
Mobile interactions prioritize **touch-friendly gestures**:

- **Tap to Expand** — Monster cards expand inline to show full details rather than navigating away
- **Swipe Navigation** — Horizontal swipe between monster details when expanded
- **Pull to Refresh** — Standard mobile pattern for refreshing the monster list
- **Filter Persistence** — Applied filters remain visible as chips when filter panel is collapsed
- **Scroll Position Memory** — Returns to previous scroll position when navigating back from expanded views

### Visual Hierarchy
The mobile design maintains **visual consistency** while adapting to constraints:

- **Dark Theme** — Consistent with desktop, optimized for mobile viewing conditions
- **Red Accents** — Used for active filters, selected states, and primary actions
- **Typography Scaling** — Larger text sizes appropriate for mobile reading
- **Spacing Adaptation** — Increased touch targets and padding for finger navigation
- **Card Grouping** — Visual separation between monster families/groups using subtle dividers

### Progressive Disclosure
Mobile interface uses **layered information architecture**:

1. **Overview Level** — Monster name, CR, and hero image immediately visible
2. **Summary Level** — Tags, description, and action buttons on card face
3. **Detail Level** — Full statistics, abilities, and related monsters in expanded state
4. **Filter Level** — Comprehensive filtering options hidden behind collapsible interface