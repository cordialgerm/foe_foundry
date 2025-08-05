# PRD: Mobile Tabbed Layout for Monster Editor

## Overview

The current Foe Foundry monster editor UI is optimized for desktop but breaks down on mobile due to its side-by-side layout. On small screens, the fixed-width left (`<monster-card>`) and right (statblock) panels overflow the viewport and create a poor user experience.

To support mobile users, we will introduce a responsive **tabbed layout** that separates editing and viewing into clearly labeled, swipe-friendly tabs while maintaining a single instance of each component.

---

## Motivation

- Improve usability on mobile and small tablet devices.
- Ensure clean separation between monster editing and statblock display.
- Maintain fast UX: no scroll jumps, re-renders, or component resets.
- Prevent flicker or input loss when switching tabs.
- Avoid duplicate component instances and state synchronization issues.

---

## Goals

- Add responsive tab UI for mobile users.
- Default to "Editor" tab on load.
- When an edit occurs, show a subtle pill notification on the "Statblock" tab.
- **Single component instances**: Always render one `monster-card` and one `monster-statblock`
- **CSS-based layout control**: Use CSS to handle desktop vs mobile layout switching
- **DOM state preservation**: Use `display` CSS property to show/hide panels instead of conditional rendering
- Maintain full desktop layout as-is.
- Respond to screen size changes (orientation/resize) and switch layouts appropriately.

---

## Architecture Decision: Single Component Strategy

### Problem with Dual Instance Approach
The initial implementation created separate `monster-card` and `monster-statblock` instances for mobile and desktop, leading to:
- State synchronization issues between instances
- Performance overhead from duplicate components
- Complex event handling (targeting correct instance)
- Potential inconsistencies when switching between mobile tabs

### New Single Instance Approach
- **Always render both components once** in dedicated panels
- **Layout control via CSS**: Desktop shows side-by-side, mobile shows stacked with tab-controlled visibility
- **Simplified event handling**: Always target the same `monster-statblock` element
- **Better performance**: No duplicate components or state management

---

## Scope of Work

### UI Changes

- Add a **mobile-only tab selector** (`Editor`, `Statblock`) that appears under 964px screen width.
- Use **CSS `display` property** to show/hide panels based on active tab (not conditional rendering).
- Display an **"Updated!" pill** on the Statblock tab after edits, unless the user is already viewing that tab.
- Detect screen size changes and re-render layout appropriately.

### Component Structure

Always render both components in dedicated panels:
```html
<!-- Always present - layout controlled by CSS -->
<div class="card-panel">
  <monster-card monster-key="${this.monsterKey}"></monster-card>
</div>
<div class="statblock-panel">
  <monster-statblock monster-key="${this.monsterKey}" power-keys="${powerKeys}" hide-buttons></monster-statblock>
</div>
```

### Component Changes

- Update `renderContent(monster)` method in `MonsterBuilder`:
  - Always render both `card-panel` and `statblock-panel`
  - Use CSS classes and `display` properties to control visibility
  - Show mobile tabs when `isMobile` is true
- Add three new properties:
  ```ts
  @property({ type: String }) mobileTab: 'edit' | 'statblock' = 'edit';
  @property({ type: Boolean }) statblockUpdated: boolean = false;
  @property({ type: Boolean }) isMobile: boolean = false;
  ```
- Add a resize observer to detect screen size changes and update `isMobile` state
- Listen for `monster-changed` events to set `statblockUpdated` flag when on mobile

### Breakpoint Strategy - Content-Based Approach

Instead of arbitrary device-based breakpoints, use **content-requirements-based breakpoints** defined as configurable constants within the component.

#### Configuration Object Implementation

```ts
// Configuration for responsive layout
const LAYOUT_CONFIG = {
  // Component dimensions
  MONSTER_CARD_WIDTH: 300,     // Fixed width of monster editor
  MONSTER_CARD_WIDTH_LARGE_DESKTOP: 400,
  MIN_STATBLOCK_WIDTH: 500,    // Minimum readable statblock width  
  LAYOUT_GAPS: 64,             // Padding and margins (2rem + container padding)
  
  // Calculated breakpoint
  get MOBILE_BREAKPOINT() {
    return this.MONSTER_CARD_WIDTH + this.MIN_STATBLOCK_WIDTH + this.LAYOUT_GAPS;
    // = 964px minimum for usable side-by-side layout
  },
  
  // Optional: Additional breakpoints for fine-tuning
  SMALL_MOBILE: 480,
  LARGE_DESKTOP: 1200,
  
  // Helper methods
  isMobile: (width: number) => width <= LAYOUT_CONFIG.MOBILE_BREAKPOINT,
  isSmallMobile: (width: number) => width <= LAYOUT_CONFIG.SMALL_MOBILE,
  isDesktop: (width: number) => width > LAYOUT_CONFIG.MOBILE_BREAKPOINT,
  isLargeDesktop: (width: number) => width >= LAYOUT_CONFIG.LARGE_DESKTOP
} as const;
```

#### Why Content-Based Breakpoints?

**Problem with 640px/768px arbitrary breakpoints:**
- MonsterCard takes up 400px fixed width
- At 768px total: Only 368px remaining for statblock (minus gaps/padding)  
- 368px is barely usable for D&D statblocks with long ability descriptions
- Forces cramped, poor user experience even on devices that could handle desktop layout

**Content-based calculation (964px):**
- **400px**: MonsterCard component fixed width
- **500px**: Minimum width for readable D&D statblock content
- **64px**: Layout gaps (2rem) + container padding
- **Result**: Only show side-by-side when both panels can be properly displayed

#### Benefits of Configuration Object Approach

1. **Self-documenting**: Makes the calculation logic transparent
2. **Maintainable**: Easy to adjust if MonsterCard width changes
3. **Reusable**: Other components can use the same breakpoint config
4. **Testable**: Easy to unit test breakpoint logic in isolation
5. **Content-first**: Clearly shows breakpoint is based on actual space requirements
6. **Future-proof**: Automatically adjusts if component dimensions change

#### Breakpoint Logic Summary

- **≤964px**: Mobile tabbed layout (ensures both panels are usable when shown)
- **≥965px**: Desktop side-by-side layout (sufficient space for comfortable reading)
- **≤480px**: Additional small-screen optimizations (smaller fonts, tighter spacing)

This approach prioritizes **content readability and usability** over arbitrary device categories, ensuring the interface works well regardless of the specific device being used.

## Implementation Suggestions

### CSS Layout Strategy with Configuration Object

```css
/* Always render both panels */
.card-panel,
.statblock-panel {
  width: 100%;
}

/* Desktop: side-by-side layout */
.panels-container {
  display: flex;
  flex-direction: row;
  gap: 2rem;
  width: 100%;
}

.card-panel {
  flex: 0 0 400px;
}

.statblock-panel {
  flex: 1 1 auto;
  min-width: 0;
}

/* Mobile: stacked layout with tab-controlled visibility */
@media (max-width: ${LAYOUT_CONFIG.MOBILE_BREAKPOINT}px) {
  .panels-container {
    flex-direction: column;
    gap: 0;
  }
  
  .card-panel,
  .statblock-panel {
    flex: none;
  }

  /* Mobile tabs */
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

  /* Tab-controlled panel visibility */
  .card-panel {
    display: var(--card-panel-display, block);
  }
  
  .statblock-panel {
    display: var(--statblock-panel-display, none);
  }

  /* Enhanced mobile usability */
  .mobile-tab {
    min-height: 48px; /* Touch target size */
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

/* Optional: Fine-tune for very small screens */
@media (max-width: ${LAYOUT_CONFIG.SMALL_MOBILE}px) {
  .mobile-tab {
    font-size: 0.9rem;
    padding: 0.6rem 0.8rem;
  }
  
  .container.pamphlet-main {
    padding: 0.5rem;
  }
}
```

### Simplified Event Handling

```ts
// Much simpler - always target the same element
async onStatblockChangeRequested(monsterCard: MonsterCard, eventDetail?: any) {
  if (!monsterCard) return;

  // Single statblock instance - no complex targeting needed
  const statblock = this.shadowRoot?.querySelector('monster-statblock') as MonsterStatblock;
  if (!statblock) return;

  // ... rest of method unchanged
}
@media (max-width: 768px) {
### HTML Template Structure

```html
<div class="container pamphlet-main">
  <!-- Monster header with navigation -->
  <div class="monster-header">...</div>

  <!-- Mobile tabs (only shown on mobile) -->
  <div class="mobile-tabs" style="display: ${this.isMobile ? 'flex' : 'none'}">
    <button class="mobile-tab ${this.mobileTab === 'edit' ? 'active' : ''}"
            @click=${() => this.setMobileTab('edit')}>
      Editor
    </button>
    <button class="mobile-tab ${this.mobileTab === 'statblock' ? 'active' : ''}"
            @click=${() => this.setMobileTab('statblock')}>
      Statblock
      ${this.statblockUpdated && this.mobileTab !== 'statblock' ?
        html`<span class="update-pill">Updated!</span>` : ''}
    </button>
  </div>

  <!-- Single container with both panels -->
  <div class="panels-container" 
       style="${this.isMobile ? this.getMobilePanelStyles() : ''}">
    
    <div class="card-panel">
      <monster-card monster-key="${this.monsterKey}"></monster-card>
    </div>
    
    <div class="statblock-panel">
      <monster-statblock
        monster-key="${this.monsterKey}"
        power-keys="${powerKeys}"
        hide-buttons>
      </monster-statblock>
    </div>
  </div>
</div>
```

### Dynamic Style Method

```ts
private getMobilePanelStyles(): string {
  if (this.mobileTab === 'edit') {
    return '--card-panel-display: block; --statblock-panel-display: none;';
  } else {
    return '--card-panel-display: none; --statblock-panel-display: block;';
  }
}
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
```

---

## Breakpoint Strategy & Rationale

### Why 864px Instead of 640px or 768px?

The content-based breakpoint approach calculates the minimum screen width needed for a usable side-by-side layout.

#### Device Analysis:
- **Mobile Phones (320px-430px)**: Need tabbed interface - side-by-side is unusable
- **Large Phones in Landscape (568px-932px)**: Still benefit from tabbed interface  
- **Small Tablets (768px-834px)**: At 768px, only 368px remains for statblock - cramped and hard to read
- **Standard Tablets (1024px+)**: Definitely suitable for desktop layout

#### 864px Breakpoint Benefits:
1. **Content-First Design**: Based on actual space requirements for readable D&D statblocks
2. **Better User Experience**: No cramped, hard-to-read layouts
3. **Clear Decision Boundary**: Either you have enough space for both panels or you don't
4. **Self-Documenting**: The calculation shows exactly why this breakpoint was chosen
5. **Maintainable**: Easy to adjust if component dimensions change

#### Calculation Breakdown:
- **300px**: MonsterCard component fixed width (+100 on large desktop)
- **500px**: Minimum width for readable D&D statblock with ability descriptions
- **64px**: Layout gaps (2rem) + container padding
- **Total**: 964px minimum for usable side-by-side layout

#### Fallback Strategy:
- **≤864px**: Mobile tabbed layout (ensures usable experience)
- **≥865px**: Desktop side-by-side layout (sufficient space for both panels)
- **≤480px**: Additional optimizations for very small screens

This approach ensures the interface is genuinely usable regardless of device type, prioritizing content readability over device assumptions.

---

## Guidelines

- **Single source of truth**: Always render one `monster-card` and one `monster-statblock`
- **CSS-controlled layout**: Use CSS to handle responsive behavior and panel visibility
- **Event handling simplification**: Target single `monster-statblock` element
- Set `statblockUpdated` flag only when on mobile and not currently viewing the statblock tab
- Use CSS custom properties to control panel visibility on mobile
- The ResizeObserver approach ensures responsive behavior when users rotate devices or resize windows
- This is the minimum shippable version of the mobile layout — future enhancements can be layered on later

---

## Benefits of Single Instance Approach

1. **No State Sync Issues**: Single components mean no synchronization problems
2. **Simplified Event Handling**: Always target the same DOM elements
3. **Better Performance**: No duplicate component instances or duplicate state
4. **Cleaner Architecture**: Separation of concerns (components handle logic, CSS handles layout)
5. **Easier Maintenance**: Less complex conditional rendering logic
6. **DOM Stability**: Components don't get destroyed/recreated when switching tabs

---

## Guidelines

- Detect screen size changes and update layout responsively.
- Set `statblockUpdated` flag only when on mobile and not currently viewing the statblock tab.
- Use `display: none` rather than conditional rendering to preserve DOM state and avoid component reinitialization.
- The ResizeObserver approach ensures responsive behavior when users rotate devices or resize windows.
- This is the minimum shippable version of the mobile layout — future enhancements can be layered on later.

---

## Future Considerations

- Automatically switch to the Statblock tab after edits (behind a feature flag or toggle)
- Add swipe gestures or animation between tabs
- Add keyboard accessibility or ARIA roles for tab controls
- Consider toast notifications that automatically switch to the statblock tab after edits

---

## Testing

- To test, create a new or use the existing simple HTML page at /docs/test-mobile-layout.html showing the monster generator component with `monster-key="ogre"`
- You can build the TS with `npx vite build`
- Test responsive behavior by resizing browser window
- Verify single component instances are working by checking DOM in dev tools
- Confirm no duplicate event handling or state sync issues