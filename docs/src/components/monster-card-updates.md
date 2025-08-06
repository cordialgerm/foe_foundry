# PRD: MonsterCard Content Tab Enhancement

## Overview

Extend the existing `MonsterCard` component to support tabbed content navigation, allowing users to edit Powers, and view Lore and Encounters within a single, cohesive monster card interface. 

---

## Motivation

- **Expanded Content Types**: Support monster lore and encounter information beyond just stats and powers
- **Consistent Editing Experience**: All monster creation/editing happens within the MonsterCard component
- **Component Reusability**: Enhanced MonsterCard can be reused in other contexts beyond the MonsterBuilder
- **Logical Content Organization**: Group related functions under clear, intuitive tabs

---

## Goals

- Add internal tab navigation to MonsterCard for Powers/Lore/Encounters tabs
- Maintain existing MonsterCard API and external interface
- Create new tabbed sections for monster lore and monster encounters
- Ensure responsive behavior across all breakpoints
- Default to "Powers" tab (current functionality)

---

## Scope of Work

### MonsterCard Component Updates

#### New Properties
```ts
@property({ type: String }) contentTab: 'powers' | 'lore' | 'encounters' = 'powers';
```

#### New Methods
```ts
setContentTab(tab: 'powers' | 'lore' | 'encounters'): void {
  this.contentTab = tab;
  this.requestUpdate();
}

```

#### Template Structure Enhancement
```html
<div class="monster-card-container">
  <!-- Monster Info (name, image, etc.) - Always visible -->
  <div class="monster-info">
    <!-- Existing monster info content -->
  </div>
  
  <!-- Content Navigation Tabs -->
  <div class="content-tabs">
    <button class="content-tab ${this.contentTab === 'powers' ? 'active' : ''}"
            @click=${() => this.setContentTab('powers')}>
      Powers
    </button>
    <button class="content-tab ${this.contentTab === 'lore' ? 'active' : ''}"
            @click=${() => this.setContentTab('lore')}>
      Lore
    </button>
    <button class="content-tab ${this.contentTab === 'encounters' ? 'active' : ''}"
            @click=${() => this.setContentTab('encounters')}>
      Encounters
    </button>
  </div>
  
  <!-- Tabbed Content Container -->
  <div class="tab-content-container" style="${this.getTabContentStyles()}">
    <!-- Powers Tab (existing content) -->
    <div class="tab-content" data-content="powers">
      <!-- All existing power loadout editing content -->
      <!-- Abilities, Actions, Legendary Actions, etc. -->
    </div>
    
    <!-- Lore Tab -->
    <div class="tab-content" data-content="lore">
        <!-- Monster Lore, retrieved from the Monster Store -->
    </div>
    
    <!-- Encounters Tab -->
    <div class="tab-content" data-content="encounters">
      <!-- Monster Encounters, retrieved from the Monster Store -->
    </div>
  </div>
</div>
```

### CSS Implementation Strategy

```css
/* Content tabs styling */
.content-tabs {
  display: flex;
  border-bottom: 2px solid var(--bs-border-color);
  margin-bottom: 1rem;
  margin-top: 1rem;
}

.content-tab {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  border-bottom: 3px solid transparent;
  background: transparent;
  color: var(--bs-secondary);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.content-tab:hover {
  background: var(--bs-light);
  color: var(--bs-primary);
}

.content-tab.active {
  color: var(--bs-primary);
  border-bottom-color: var(--bs-primary);
  font-weight: 600;
}

/* Tab content visibility control */
.tab-content {
  display: var(--tab-display-stats, none);
}

.tab-content[data-content="stats"] {
  display: var(--tab-display-stats, block);
}

.tab-content[data-content="lore"] {
  display: var(--tab-display-lore, none);
}

.tab-content[data-content="encounters"] {
  display: var(--tab-display-encounters, none);
}

/* Mobile responsiveness */
@media (max-width: 480px) {
  .content-tab {
    font-size: 0.8rem;
    padding: 0.6rem 0.5rem;
  }
}
```

## Data Architecture Considerations

### Monster Interface Extension

```ts
interface Monster {
  // ... existing properties
  
  // New optional properties
  lore?: HTMLElement;
  encounters?: HTMLElement;
}
```