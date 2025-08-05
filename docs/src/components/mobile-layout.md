# PRD: Mobile Tabbe# PRD: Mobile Tabbed Layout for Monster Editor

## Overview

The current Foe Foundry monster editor UI is optimized for desktop but breaks down on mobile due to its side-by-side layout. On small screens, the fixed-width left (`<monster-card>`) and right (statblock) panels overflow the viewport and create a poor user experience.

To support mobile users, we will introduce a responsive **tabbed layout** that separates editing and viewing into clearly labeled, swipe-friendly tabs.

---

## Motivation

- Improve usability on mobile and small tablet devices.
- Ensure clean separation between monster editing and statblock display.
- Maintain fast UX: no scroll jumps, re-renders, or component resets.
- Prevent flicker or input loss when switching tabs.

---

## Goals

- Add responsive tab UI for mobile users.
- Default to "Editor" tab on load.
- When an edit occurs, show a subtle pill notification on the "Statblock" tab.
- Preserve DOM state across tabs by hiding inactivte tabs
- Maintain full desktop layout as-is.
- Respond to screen size changes (orientation/resize) and switch layouts appropriately.

---

## Scope of Work

### UI Changes

- Add a **mobile-only tab selector** (`Editor`, `Statblock`) that appears under 768px screen width.
- Use conditional rendering to show either the monster-card OR the statblock based on active tab.
- Display an **"Updated!" pill** on the Statblock tab after edits, unless the user is already viewing that tab.
- Detect screen size changes and re-render layout appropriately.

### Component Changes

- Update `renderContent(monster)` method in `MonsterBuilder`:
  - Show desktop layout above 768px (unchanged).
  - Show mobile tabs and conditionally render panels below 768px.
- Add three new properties:
  ```ts
  @property({ type: String }) mobileTab: 'edit' | 'statblock' = 'edit';
  @property({ type: Boolean }) statblockUpdated: boolean = false;
  @property({ type: Boolean }) isMobile: boolean = false;
  ```
- Add a resize observer to detect screen size changes and update `isMobile` state
- Listen for `monster-changed` events to set `statblockUpdated` flag when on mobile

## Implementation Suggestions

## Implementation Details

### TypeScript Properties & Methods

```ts
// Add to MonsterBuilder class
@property({ type: String }) mobileTab: 'edit' | 'statblock' = 'edit';
@property({ type: Boolean }) statblockUpdated: boolean = false;
@property({ type: Boolean }) isMobile: boolean = false;

private resizeObserver?: ResizeObserver;

connectedCallback() {
  super.connectedCallback();
  this.setupResizeObserver();
}

disconnectedCallback() {
  super.disconnectedCallback();
  this.resizeObserver?.disconnect();
}

private setupResizeObserver() {
  this.resizeObserver = new ResizeObserver(() => {
    this.checkIsMobile();
  });
  this.resizeObserver.observe(this);
}

private checkIsMobile() {
  this.isMobile = window.innerWidth <= 768;
}

private setMobileTab(tab: 'edit' | 'statblock') {
  this.mobileTab = tab;
  if (tab === 'statblock') {
    this.statblockUpdated = false;
  }
}
```

### CSS

```css
/* Mobile-only elements */
.mobile-tabs {
  display: none;
}

.mobile-panel {
  display: block;
  width: 100%;
}

/* Mobile layout */
@media (max-width: 768px) {
  .desktop-layout {
    display: none !important;
  }

  .mobile-tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .mobile-tab {
    flex: 1;
    padding: 0.75rem 1rem;
    border: none;
    border-radius: 8px;
    background: var(--bs-secondary);
    color: var(--bs-light);
    cursor: pointer;
    font-size: 1rem;
    transition: background 0.2s;
  }

  .mobile-tab.active {
    background: var(--bs-primary);
    color: var(--bs-light);
    font-weight: bold;
  }

  .update-pill {
    background: var(--bs-warning);
    color: var(--bs-dark);
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    margin-left: 0.5rem;
  }
}
```

### Responsive CSS Additions

```css
/* Add to MonsterBuilder styles */
@media (max-width: 768px) {
  .panels-row {
    display: none !important;
  }
  
  .mobile-panel {
    display: block;
    width: 100%;
  }
  
  .monster-header {
    margin-bottom: 1rem;
  }
}
```

### Enhanced Event Handling

```ts
// Update the existing firstUpdated method in MonsterBuilder
async firstUpdated() {
  this.checkIsMobile(); // Initial check

  this.shadowRoot?.addEventListener('monster-changed', async (event: any) => {
    const monsterCard = event.detail.monsterCard;
    
    // Set statblock updated flag when on mobile and not viewing statblock
    if (this.isMobile && this.mobileTab !== 'statblock') {
      this.statblockUpdated = true;
    }
    
    await this.onStatblockChangeRequested(monsterCard, event.detail);
  });

  if (this.shadowRoot) {
    await adoptExternalCss(this.shadowRoot);
  }
}
```

```ts
// Mobile tabs (only shown on mobile)
${this.isMobile ? html`
  <div class="mobile-tabs">
    <button
      class="mobile-tab ${this.mobileTab === 'edit' ? 'active' : ''}"
      @click=${() => this.setMobileTab('edit')}>
      Editor
    </button>
    <button
      class="mobile-tab ${this.mobileTab === 'statblock' ? 'active' : ''}"
      @click=${() => this.setMobileTab('statblock')}>
      Statblock
      ${this.statblockUpdated && this.mobileTab !== 'statblock' ?
        html`<span class="update-pill">Updated!</span>` : ''}
    </button>
  </div>
` : ''}
```

### Conditional Panel Rendering

```ts
// Desktop layout (always rendered, hidden on mobile via CSS)
<div class="panels-row">
  <div class="left-panel">
    <monster-card monster-key="${this.monsterKey}"></monster-card>
  </div>
  <div class="right-panel">
    <monster-statblock
      monster-key="${this.monsterKey}"
      power-keys="${powerKeys}"
      hide-buttons
    ></monster-statblock>
  </div>
</div>

// Mobile layout (only shown on mobile)
${this.isMobile ? html`
  <div class="mobile-panel">
    <div class="mobile-panel-content" style="display: ${this.mobileTab === 'edit' ? 'block' : 'none'}">
      <monster-card monster-key="${this.monsterKey}"></monster-card>
    </div>
    <div class="mobile-panel-content" style="display: ${this.mobileTab === 'statblock' ? 'block' : 'none'}">
      <monster-statblock
        monster-key="${this.monsterKey}"
        power-keys="${powerKeys}"
        hide-buttons
      ></monster-statblock>
    </div>
  </div>
` : ''}
```

---

## Guidelines

- Detect screen size changes and update layout responsively.
- Set `statblockUpdated` flag only when on mobile and not currently viewing the statblock tab.
- Use `display: none` rather than conditional rendering to preserve DOM state and avoid component reinitialization.
- The ResizeObserver approach ensures responsive behavior when users rotate devices or resize windows.
- This is the minimum shippable version of the mobile layout — future enhancements can be layered on later.

---

## Future Considerations

- Automatically switch to the Statblock tab after edits (behind a feature flag or toggle).
- Add swipe gestures or animation between tabs.
- Add keyboard accessibility or ARIA roles for tab controls.
- Consider toast notifications that automatically switch to the statblock tab after edits.

---


## Testing

- To test, create a simple HTML page showing the monster generator component on an `monster-key="ogre"` statblock
- You can build the TS with `npx vite build`