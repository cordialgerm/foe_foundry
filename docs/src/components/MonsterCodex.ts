import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { MonsterInfo, MonsterSearchRequest, SearchFacets, MonsterSearchResult } from '../data/search.js';
import { Monster } from '../data/monster.js';
import { MonsterSearchApi } from '../data/searchApi.js';
import { ApiMonsterStore } from '../data/api.js';
import './MonsterCardPreview.js';
import './MonsterSimilar.js';
import './MonsterLore.js';
import './MonsterEncounters.js';
import './MonsterStatblock.js';
import { Task } from '@lit/task';

@customElement('monster-codex')
export class MonsterCodex extends LitElement {
  @state() private query = '';
  @state() private selectedCreatureTypes: string[] = [];
  @state() private selectedEnvironments: string[] = [];
  @state() private selectedRoles: string[] = [];
  @state() private minCr?: number;
  @state() private maxCr?: number;
  @state() private tempMinCr?: number; // For immediate visual feedback during sliding
  @state() private tempMaxCr?: number; // For immediate visual feedback during sliding
  @state() private groupBy: 'family' | 'challenge' | 'name' | 'relevance' = 'relevance';
  @state() private monsters: MonsterInfo[] = [];
  @state() private facets: SearchFacets | null = null;
  @state() private selectedMonster: Monster | null = null;
  @state() private loading = false;
  @state() private filtersPanelVisible = window.innerWidth > 1040; // Hidden by default for mobile-first design
  @state() private selectedMonsterKey: string | null = null; // Track explicitly selected monster for sticky behavior
  @state() private contentTab: 'preview' | 'lore' | 'encounters' = 'preview';
  @state() private expandedMonsterKey: string | null = null; // Track which monster row has its drawer expanded

  private searchApi = new MonsterSearchApi();
  private apiStore = new ApiMonsterStore();
  private searchDebounceTimer: number | undefined;
  private crDebounceTimer: number | undefined;
  private backgroundOffsets = new Map<string, string>(); // Store consistent background positions

  private searchTask = new Task(this, async ([query, selectedCreatureTypes, minCr, maxCr]: [string, string[], number | undefined, number | undefined]) => {
    const hasFilters = !!(query || (selectedCreatureTypes && selectedCreatureTypes.length > 0) || minCr !== undefined || maxCr !== undefined);
    if (!hasFilters) {
      // No filters: just get facets
      const facets = await this.searchApi.getFacets();
      return { monsters: [], facets, total: 0 } as MonsterSearchResult;
    } else {
      // Filters: perform search
      const searchRequest: MonsterSearchRequest = {
        query: query || undefined,
        creatureTypes: selectedCreatureTypes.length > 0 ? selectedCreatureTypes : undefined,
        minCr,
        maxCr
      };
      const results = await this.searchApi.searchMonsters(searchRequest);
      return results;
    }
  }, () => {
    return [
      this.query,
      this.selectedCreatureTypes,
      this.minCr,
      this.maxCr
    ] as [string, string[], number | undefined, number | undefined];
  });

  static styles = css`
    :host {
      --border-color: var(--fg-color);
      display: block;
      height: 100%;
      min-height: 100vh;
    }

    /* Mobile-first: Single column layout */
    .codex-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 100vh;
    }

    /* Desktop: Three column layout when screen is wide enough */
    @media (min-width: 1040px) {
      .codex-container {
        display: grid;
        grid-template-columns: 340px 1fr 400px;
        height: 100vh;
        gap: 0;
      }

      .codex-container.filters-hidden {
        grid-template-columns: 0 1fr 400px;
      }
    }

    /* Mobile: Collapsible filters panel */
    .filters-panel {
      order: 2;
      border: 2px solid var(--border-color);
      border-radius: var(--medium-margin);
      margin: 1rem;
      transition: max-height 0.3s ease-in-out, opacity 0.3s ease-in-out;
      overflow: hidden;
    }

    .filters-panel.hidden {
      max-height: 0;
      opacity: 0;
      margin-top: 0;
      margin-bottom: 0;
      border: none;
    }

    .filters-panel:not(.hidden) {
      opacity: 1;
    }

    /* Desktop: Side panel */
    @media (min-width: 1040px) {
      .filters-panel {
        order: unset;
        margin: 0;
        border-radius: 0 var(--medium-margin) var(--medium-margin) 0;
        padding: 1rem;
        overflow-x: hidden;
        overflow-y: auto;
        width: 300px;
        transition: width 0.3s ease-in-out, padding 0.3s ease-in-out;
        border-right: 2px solid var(--border-color);
        border-top: 2px solid var(--border-color);
        border-bottom: 2px solid var(--border-color);
        border-left: none;
        position: relative;
        backdrop-filter: blur(5px);
        max-height: unset;
        opacity: 1;
      }

      .filters-panel.hidden {
        width: 0;
        padding: 0;
        overflow: hidden;
        border-right: none;
        border-top: none;
        border-bottom: none;
        max-height: unset;
        opacity: 1;
        margin: 0;
      }
    }

    .filters-container {
      padding: 1rem;
    }

    /* Mobile: Hide panel divider */
    .panel-divider {
      display: none;
    }

    /* Desktop: Show panel divider */
    @media (min-width: 1040px) {
      .panel-divider {
        display: flex;
        position: absolute;
        top: 50%;
        right: -12px;
        transform: translateY(-50%);
        background: var(--fg-color);
        color: var(--primary-color);
        border: none;
        width: 24px;
        height: 48px;
        border-radius: 0 6px 6px 0;
        cursor: pointer;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        z-index: 3;
        transition: all 0.2s ease;
        border: 1px solid var(--border-color);
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.3);
      }

      .panel-divider:hover {
        background: var(--primary-muted-color);
        transform: translateY(-50%) scale(1.1);
      }
    }

    /* Mobile: Monster list takes full width */
    .monster-list-panel {
      order: 3;
      display: flex;
      flex-direction: column;
      flex: 1;
      overflow: hidden;
      min-height: 0; /* Allow flex shrinking for scrolling */
    }

    /* Desktop: Monster list in middle column */
    @media (min-width: 1040px) {
      .monster-list-panel {
        order: unset;
        backdrop-filter: blur(5px);
      }
    }

    /* Mobile: Hide preview panel entirely */
    .preview-panel {
      display: none;
    }

    /* Desktop: Show preview panel */
    @media (min-width: 1040px) {
      .preview-panel {
        display: block;
        backdrop-filter: blur(10px);
        border-radius: var(--medium-margin) 0 0 var(--medium-margin);
        padding: 1.5rem;
        overflow-y: auto;
        border-left: 2px solid var(--border-color);
        border-top: 2px solid var(--border-color);
        border-bottom: 2px solid var(--border-color);
        z-index: 1;
      }
    }

    /* Mobile: Header with title and search */
    .codex-header {
      order: 1;
      padding: 1rem;
      border-bottom: 2px solid var(--border-color);
    }


    /* Search bar styles - Mobile first */
    .search-bar {
      padding: 1rem;
      display: flex;
      gap: 0.75rem;
      align-items: center;
      border-top: 2px solid var(--border-color);
      border-bottom: 1px solid var(--border-color);
      flex-wrap: wrap;
    }

    /* Desktop: Search bar positioning */
    @media (min-width: 1040px) {
      .search-bar {
        margin-left: 1.5rem;
        margin-right: 1.5rem;
        z-index: 5;
        position: relative;
        backdrop-filter: blur(5px);
      }

      .search-bar.mobile {
        display: none;
      }
    }

    @media (max-width: 1040px) {
      .search-bar.desktop {
        display: none;
      }
    }

    .search-input-container {
      flex: 1;
      min-width: 200px;
    }

    .search-input {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid var(--border-color);
      border-radius: 4px;
      background: var(--muted-color);
      color: var(--fg-color);
      font-size: 1rem;
      min-height: 44px; /* Touch-friendly */
      box-sizing: border-box;
    }

    .search-input::placeholder {
      color: var(--fg-muted-color);
    }

    .search-input:focus {
      outline: none;
      border-color: var(--border-color);
      box-shadow: 0 0 0 2px var(--fg-muted-color);
    }

    /* Filter styles */
    .filters-container h2 {
      color: var(--fg-color);
      margin: 0 0 1rem 0;
      font-family: var(--header-font);
      font-size: var(--header-font-size);
    }

    .filter-section {
      margin-bottom: 1.5rem;
    }

    .filter-section h4 {
      color: var(--fg-color);
      margin-bottom: 0.5rem;
      font-size: 1rem;
      font-family: var(--header-font);
    }

    .pill-container {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .filter-pill {
      padding: 0.25rem 0.75rem;
      border: 1px solid var(--border-color);
      border-radius: 20px;
      background: transparent;
      color: var(--fg-color);
      cursor: pointer;
      font-size: 0.9rem;
      transition: all 0.2s ease;
      font-family: var(--primary-font);
    }

    .filter-pill:hover {
      background: var(--primary-color);
      color: var(--fg-color);
      border-color: var(--primary-color);
    }

    .filter-pill.active {
      background: var(--primary-color);
      color: var(--fg-color);
      font-weight: bold;
      border-color: var(--primary-color);
    }

    .group-buttons {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }

    .group-btn {
      padding: 0.5rem 1rem;
      border: 1px solid var(--border-color);
      border-radius: 4px;
      background: transparent;
      color: var(--fg-color);
      cursor: pointer;
      transition: all 0.2s ease;
      font-family: var(--primary-font);
      font-size: 0.9rem;
    }

    .group-btn:hover {
      background: var(--primary-color);
      color: var(--fg-color);
      border-color: var(--primary-color);
    }

    .group-btn.active {
      background: var(--primary-color);
      color: var(--fg-color);
      font-weight: bold;
      border-color: var(--primary-color);
    }

    .cr-range {
      color: var(--fg-color);
      font-family: var(--primary-font);
      font-size: 0.9rem;
      margin-top: 0.5rem;
    }

    .cr-slider-container {
      margin-top: 1rem;
      position: relative;
    }

    .cr-slider-wrapper {
      position: relative;
      height: 40px;
      background: var(--muted-color);
    }

    .cr-slider {
      position: absolute;
      width: 100%;
      height: 100%;
      background: transparent;
      pointer-events: none;
      appearance: none;
      -webkit-appearance: none;
    }

    .cr-slider::-webkit-slider-track {
      background: transparent;
      height: 100%;
    }

    .cr-slider::-webkit-slider-thumb {
      appearance: none;
      -webkit-appearance: none;
      height: 36px;
      width: 20px;
      background: var(--fg-color);
      border-radius: 4px;
      cursor: pointer;
      pointer-events: auto;
      border: 2px solid var(--fg-color);
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }

    .cr-slider::-moz-range-track {
      background: transparent;
      height: 100%;
      border: none;
    }

    .cr-slider::-moz-range-thumb {
      height: 32px;
      width: 16px;
      background: var(--fg-color);
      border-radius: 4px;
      cursor: pointer;
      pointer-events: auto;
      border: 2px solid var(--fg-color);
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }

    .cr-slider-track {
      position: absolute;
      top: 50%;
      left: 10px;
      right: 10px;
      height: 6px;
      background: var(--fg-color);
      border-radius: 3px;
      transform: translateY(-50%);
      pointer-events: none;
    }

    .cr-labels {
      display: flex;
      justify-content: space-between;
      margin-top: 0.5rem;
      font-size: 0.8rem;
      color: var(--fg-color);
    }

    .cr-tier-labels {
      display: flex;
      justify-content: space-between;
      margin-top: 0.25rem;
      font-size: 0.7rem;
      color: var(--fg-color);
      font-weight: bold;
      position: relative;
    }

    .cr-tier-label {
      position: absolute;
      transform: translateX(-50%);
    }

    .cr-tier-label:nth-child(1) { left: 5%; }   /* Tier I at CR 0-3 (~10%) */
    .cr-tier-label:nth-child(2) { left: 23.3%; } /* Tier II at CR 4-10 (~23%) */
    .cr-tier-label:nth-child(3) { left: 50%; }   /* Tier III at CR 11-19 (~50%) */
    .cr-tier-label:nth-child(4) { left: 83.3%; } /* Tier IV at CR 20+ (~83%) */

    /* Monster list styles - Mobile first */
    .monster-list {
      flex: 1;
      overflow-y: auto;
      padding: 1rem;
    }

    .monster-row {
      display: block;
      margin-bottom: 1rem;
      border-radius: 8px;
      cursor: pointer;
      background-size: cover;
      background-position: center;
      background-blend-mode: overlay;
      background-color: rgba(0,0,0,0.4);
      transition: all 0.2s ease;
      border: 1px solid transparent;
      position: relative;
      min-height: 200px; /* Larger for mobile cards */
      overflow: hidden;
      text-decoration: none;
      color: inherit;
    }

    .monster-row::before {
      content: '';
      position: absolute;
      inset: 0;
      background-image: inherit;
      background-size: cover;
      background-position: inherit;
      background-repeat: no-repeat;
      border-radius: inherit;
      opacity: 0.7;
      z-index: 0;
    }

    .monster-row:hover {
      background-color: rgba(0,0,0,0.2);
      transform: translateY(-2px);
      border-color: var(--border-color);
      box-shadow: 0 8px 24px rgba(255, 55, 55, 0.3);
    }

    .monster-row.selected {
      background-color: var(--primary-faded-color);
      border: 1px solid var(--border-color);
      box-shadow: 0 4px 12px rgba(255, 55, 55, 0.3);
    }

    /* Desktop: Smaller list items */
    @media (min-width: 1040px) {
      .monster-row {
        display: flex;
        align-items: stretch;
        min-height: 70px;
      }

      .monster-row:hover {
        transform: translateX(6px);
      }
    }

    .group-header {
      font-size: 1.1rem;
      font-weight: bold;
      color: var(--primary-color);
      margin: 1rem 0 0.5rem 0;
      padding-bottom: 0.25rem;
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      background: rgba(0, 0, 0, 0.9);
      backdrop-filter: blur(5px);
      z-index: 1;
      font-family: var(--header-font);
    }

    /* Mobile: Rich monster card info */
    .monster-info {
      color: white;
      text-shadow: 2px 2px 6px rgba(0,0,0,0.9);
      font-family: var(--primary-font);
      position: relative;
      z-index: 1;
      background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.4) 60%, transparent 100%);
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding: 1.5rem;
      min-height: 200px;
    }

    .monster-name {
      font-weight: bold;
      margin-bottom: 0.5rem;
      font-size: 1.5rem;
      line-height: 1.2;
    }

    .monster-details {
      font-size: 1rem;
      opacity: 0.9;
      margin-bottom: 1rem;
    }

    .monster-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 1rem;
    }

    .monster-tag {
      background: var(--primary-color);
      color: var(--fg-color);
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: bold;
    }

    .monster-description {
      font-size: 0.9rem;
      line-height: 1.4;
      margin-bottom: 1rem;
      opacity: 0.8;
    }

    .monster-actions {
      display: flex;
      gap: 0.75rem;
    }

    .monster-action-btn {
      background: var(--primary-color);
      color: var(--fg-color);
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      font-family: var(--primary-font);
      font-size: 0.9rem;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.2s ease;
      min-height: 44px;
      text-decoration: none;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .monster-action-btn:hover {
      background: var(--primary-muted-color);
      transform: translateY(-1px);
    }

    .monster-action-btn.secondary {
      background: transparent;
      border: 1px solid var(--fg-color);
    }

    .monster-action-btn.secondary:hover {
      background: var(--fg-color);
      color: var(--bg-color);
    }

    /* Desktop: Simplified layout */
    @media (min-width: 1040px) {
      .monster-info {
        background: rgba(0,0,0,0.5);
        flex: 1;
        flex-direction: column;
        justify-content: center;
        padding: 0.75rem;
        min-height: auto;
      }

      .monster-name {
        font-size: 1rem;
        margin-bottom: 0.25rem;
      }

      .monster-details {
        font-size: 0.9rem;
        margin-bottom: 0;
      }

      .monster-tags,
      .monster-description,
      .monster-actions {
        display: none;
      }
    }

    /* Drawer styles */
    .monster-drawer {
      margin-top: 0.5rem;
      margin-bottom: 0.5rem;
      overflow: hidden;
      animation: drawer-slide-down 0.3s ease-out;
    }

    @keyframes drawer-slide-down {
      from {
        max-height: 0;
        opacity: 0;
        transform: translateY(-20px);
      }
      to {
        max-height: 800px;
        opacity: 1;
        transform: translateY(0);
      }
    }

    .loading {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 200px;
      color: var(--fg-color);
      font-family: var(--primary-font);
    }

    .no-selection {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 200px;
      color: var(--fg-color);
      text-align: center;
      font-family: var(--primary-font);
    }

    .no-results {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      height: 200px;
      color: var(--fg-color);
      text-align: center;
      font-family: var(--primary-font);
    }

    .no-results h4 {
      color: var(--fg-color);
      margin-bottom: 0.5rem;
    }

    .clear-filters-btn {
      background: transparent;
      color: var(--fg-color);
      border: 1px solid var(--border-color);
      padding: 0.5rem 1rem;
      border-radius: 4px;
      cursor: pointer;
      font-family: var(--primary-font);
      margin-top: 1rem;
      transition: all 0.2s ease;
    }

    .clear-filters-btn:hover {
      background: var(--primary-color);
      border: var(--primary-color);
      color: var(--fg-color);
    }

    /* Filter toggle button styles - Mobile first */
    .filter-toggle-btn {
      background: var(--primary-color);
      color: var(--fg-color);
      border: none;
      padding: 0.75rem 1rem;
      border-radius: 4px;
      cursor: pointer;
      font-family: var(--primary-font);
      font-size: 0.9rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.2s ease;
      position: relative;
      min-height: 44px; /* Touch-friendly */
      white-space: nowrap;
    }

    .filter-toggle-btn:hover {
      background: var(--primary-muted-color);
    }

    .filter-count {
      background: var(--fg-color);
      color: var(--primary-color);
      border-radius: 50%;
      width: 1.5rem;
      height: 1.5rem;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.8rem;
      font-weight: bold;
    }

    /* Mobile responsive breakpoints */
    @media (max-width: 1200px) {
      .codex-container {
        grid-template-columns: 280px 1fr 350px;
      }
      .codex-container.filters-hidden {
        grid-template-columns: 0 1fr 350px;
      }
      .filters-panel {
        margin-left: 0.25rem;
        margin-right: 0.25rem;
      }
    }

    /* Custom scrollbar styling */
    .monster-list::-webkit-scrollbar,
    .preview-panel::-webkit-scrollbar {
      width: 8px;
    }

    .monster-list::-webkit-scrollbar-track,
    .preview-panel::-webkit-scrollbar-track {
      background: var(--muted-color);
      border-radius: 4px;
    }

    .monster-list::-webkit-scrollbar-thumb,
    .preview-panel::-webkit-scrollbar-thumb {
      background: var(--primary-color);
      border-radius: 4px;
      border: 1px solid var(--bg-color);
    }

    .monster-list::-webkit-scrollbar-thumb:hover,
    .preview-panel::-webkit-scrollbar-thumb:hover {
      background: var(--tertiary-color);
    }

    /* Firefox scrollbar styling */
    .monster-list,
    .preview-panel {
      scrollbar-width: thin;
      scrollbar-color: var(--primary-color) var(--muted-color);
    }

    /* Content tabs in preview panel */
    .preview-content-tabs {
      display: flex;
      border-bottom: 2px solid var(--tertiary-color);
      margin-bottom: 1rem;
    }

    .preview-content-tab {
      flex: 1;
      padding: 0.5rem 0.75rem;
      border: none;
      border-bottom: 3px solid transparent;
      background: transparent;
      color: var(--primary-tertiary);
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 500;
      transition: all 0.2s ease;
      font-family: var(--primary-font);
    }

    .preview-content-tab:hover {
      background: var(--primary-color);
      color: var(--fg-color);
    }

    .preview-content-tab.active {
      color: var(--tertiary-color);
      border-bottom-color: var(--tertiary-color);
      font-weight: 600;
    }

    .preview-tab-content {
      display: none;
    }

    .preview-tab-content.active {
      display: block;
    }

    .similar-monsters-section {
      margin-top: 1.5rem;
      padding-top: 1rem;
    }
  `;

  async connectedCallback() {
    super.connectedCallback();
    await this.loadInitialData();

    // Listen for window resize to close filters when transitioning to mobile
    this.handleResize = this.handleResize.bind(this);
    window.addEventListener('resize', this.handleResize);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    window.removeEventListener('resize', this.handleResize);
  }

  private handleResize() {
    const isMobile = window.innerWidth <= 1040;
    const isDesktop = window.innerWidth > 1040;

    // Close filters when transitioning from desktop to mobile
    if (isMobile && this.filtersPanelVisible) {
      this.filtersPanelVisible = false;
    }
    // Open filters when transitioning from mobile to desktop
    else if (isDesktop && !this.filtersPanelVisible) {
      this.filtersPanelVisible = true;
    }
  }

  render() {
    return this.searchTask.render({
      pending: () => this.renderPending(),
      complete: (results) => this.renderComplete(results),
      error: (e) => this.renderError(e)
    });
  }

  private renderPending() {
    return html`<div class="loading">Loading monsters and filters...</div>`;
  }

  private renderComplete(result: MonsterSearchResult) {
    const monsters = Array.from(result.monsters) as MonsterInfo[];
    const facets = result.facets;
    const activeFilterCount = this.getActiveFilterCount();

    return html`
      <div class="codex-container ${this.filtersPanelVisible ? '' : 'filters-hidden'}">

        <!-- Search Bar -->
          <div class="search-bar mobile">
            <button
              class="filter-toggle-btn"
              @click=${this.toggleFiltersPanel}
              title="Toggle Filters">
              Filters
              ${activeFilterCount > 0 ? html`<span class="filter-count">${activeFilterCount}</span>` : ''}
            </button>
            <div class="search-input-container">
              <input
                type="text"
                class="search-input"
                placeholder="Search monster name..."
                .value=${this.query}
                @input=${this.handleSearchInput}
              />
            </div>
          </div>

        <!-- Filters Panel -->
        <div class="filters-panel ${this.filtersPanelVisible ? '' : 'hidden'}">
          <div class="filters-container">
            <h2>Filters</h2>
            <div class="filter-section">
              <h4>Creature Type</h4>
              <div class="pill-container">
                ${(Array.from(facets.creatureTypes) as { value: string; count: number }[]).map(facet => html`
                  <button
                    class="filter-pill ${this.selectedCreatureTypes?.includes(facet.value) ? 'active' : ''}"
                    @click=${() => this.toggleCreatureType(facet.value)}>
                    ${facet.value} (${facet.count})
                  </button>
                `)}
              </div>
            </div>
            <div class="filter-section">
              <h4>Challenge Rating</h4>
              <div class="cr-range">
                CR ${this.tempMinCr ?? this.minCr ?? facets.crRange.min ?? 0} - ${this.tempMaxCr ?? this.maxCr ?? facets.crRange.max ?? 30}
              </div>
              <div class="cr-slider-container">
                <div class="cr-slider-wrapper">
                  <div class="cr-slider-track"></div>
                  <input
                    type="range"
                    class="cr-slider"
                    min="0"
                    max="30"
                    .value=${String(this.tempMinCr ?? this.minCr ?? 0)}
                    @input=${this.handleMinCrChange}
                    style="z-index: 2;"
                  />
                  <input
                    type="range"
                    class="cr-slider"
                    min="0"
                    max="30"
                    .value=${String(this.tempMaxCr ?? this.maxCr ?? 30)}
                    @input=${this.handleMaxCrChange}
                    style="z-index: 1;"
                  />
                </div>
                <div class="cr-labels">
                  <span>CR 0</span>
                  <span>CR 30</span>
                </div>
                <div class="cr-tier-labels">
                  <span class="cr-tier-label">I</span>
                  <span class="cr-tier-label">II</span>
                  <span class="cr-tier-label">III</span>
                  <span class="cr-tier-label">IV</span>
                </div>
              </div>
            </div>
            <div class="filter-section">
              <h4>Organize Monsters By</h4>
              <div class="group-buttons">
                <button
                  class="group-btn ${this.groupBy === 'relevance' ? 'active' : ''}"
                  @click=${() => this.setGroupBy('relevance')}>
                  Relevance
                </button>
                <button
                  class="group-btn ${this.groupBy === 'family' ? 'active' : ''}"
                  @click=${() => this.setGroupBy('family')}>
                  Family
                </button>
                <button
                  class="group-btn ${this.groupBy === 'challenge' ? 'active' : ''}"
                  @click=${() => this.setGroupBy('challenge')}>
                  Challenge
                </button>
                <button
                  class="group-btn ${this.groupBy === 'name' ? 'active' : ''}"
                  @click=${() => this.setGroupBy('name')}>
                  Name
                </button>
              </div>
            </div>
            ${this.hasActiveFilters() ? html`
              <button
                class="clear-filters-btn"
                @click=${this.clearAllFilters}>
                Clear All Filters
              </button>
            ` : ''}
          </div>
          <!-- Panel divider with collapse indicator (desktop only) -->
          <button
            class="panel-divider"
            @click=${this.toggleFiltersPanel}
            title="${this.filtersPanelVisible ? 'Hide Filters' : 'Show Filters'}">
            ${this.filtersPanelVisible ? '◀' : '▶'}
          </button>
        </div>

        <!-- Monster List Panel -->
        <div class="monster-list-panel">
          <!-- Desktop Search Bar -->
          <div class="search-bar desktop">
            <button
              class="filter-toggle-btn"
              @click=${this.toggleFiltersPanel}
              title="Toggle Filters">
              Filters
              ${activeFilterCount > 0 ? html`<span class="filter-count">${activeFilterCount}</span>` : ''}
            </button>
            <div class="search-input-container">
              <input
                type="text"
                class="search-input"
                placeholder="Search monster name..."
                .value=${this.query}
                @input=${this.handleSearchInput}
              />
            </div>
          </div>
          <div class="monster-list">
            ${this.renderMonsterList(monsters)}
          </div>
        </div>

        <!-- Preview Panel (Desktop only) -->
        <div class="preview-panel">
          ${this.selectedMonster ? html`
            <div class="preview-content-tabs">
              <button class="preview-content-tab ${this.contentTab === 'preview' ? 'active' : ''}"
                      @click=${() => this.setContentTab('preview')}>
                Preview
              </button>
              <button class="preview-content-tab ${this.contentTab === 'lore' ? 'active' : ''}"
                      @click=${() => this.setContentTab('lore')}>
                Lore
              </button>
              <button class="preview-content-tab ${this.contentTab === 'encounters' ? 'active' : ''}"
                      @click=${() => this.setContentTab('encounters')}>
                Encounters
              </button>
            </div>

            <div class="preview-tab-content ${this.contentTab === 'preview' ? 'active' : ''}">
              <monster-card-preview
                monster-key="${this.selectedMonster.key}"
                .compact=${false}
              ></monster-card-preview>

              <!-- Similar Monsters below preview card -->
              <div class="similar-monsters-section">
                <monster-similar
                  monster-key="${this.selectedMonster.key}"
                  font-size="1rem"
                  max-height="none"
                ></monster-similar>
              </div>
            </div>

            <div class="preview-tab-content ${this.contentTab === 'lore' ? 'active' : ''}">
              <monster-lore
                monster-key="${this.selectedMonster.key}"
                font-size="1rem"
                max-height="none"
              ></monster-lore>
            </div>

            <div class="preview-tab-content ${this.contentTab === 'encounters' ? 'active' : ''}">
              <monster-encounters
                monster-key="${this.selectedMonster.key}"
                font-size="1rem"
                max-height="none"
              ></monster-encounters>
            </div>
          ` : html`
            <div class="no-selection">
              <p>Select a monster to see preview</p>
            </div>
          `}
        </div>
      </div>
    `;
  }

  private renderError(error: unknown) {
    return html`<div class="no-results">Error loading monsters or filters: ${error instanceof Error ? error.message : String(error)}</div>`;
  }

  private renderMonsterList(monsters: MonsterInfo[]) {
    if (!monsters || monsters.length === 0) {
      return html`
        <div class="no-results">
          <h4>No monsters found</h4>
          <p>Try adjusting your search criteria or clearing some filters.</p>
        </div>
      `;
    }
    const groupedMonsters = this.groupMonsters(monsters);
    return html`
      ${Object.entries(groupedMonsters).map(([groupName, monsters]) => html`
        ${this.groupBy === 'relevance' ? html`` : html`<div class="group-header">${groupName}</div>`}
        ${monsters.map(monster => this.renderMonsterRow(monster))}
      `)}
    `;
  }

  private renderMonsterRow(monster: MonsterInfo) {
    const isSelected = this.selectedMonsterKey === monster.key;
    const isExpanded = this.expandedMonsterKey === monster.key;

    // Get consistent background position for this monster
    let backgroundPosition = this.backgroundOffsets.get(monster.key);
    if (!backgroundPosition) {
      const randomX = Math.floor(Math.random() * 60) + 20; // 20-80%
      const randomY = Math.floor(Math.random() * 60) + 20; // 20-80%
      backgroundPosition = `${randomX}% ${randomY}%`;
      this.backgroundOffsets.set(monster.key, backgroundPosition);
    }

    // Format the details line: CR X | CreatureType | *TagLine*
    let details = `CR ${monster.cr}`;
    if (monster.creature_type) {
      details += ` | ${monster.creature_type}`;
    }
    if (monster.tag_line) {
      details += ` | ${monster.tag_line}`;
    }

    // Generate monster tags for mobile
    const tags = [];
    if (monster.creature_type) tags.push(monster.creature_type);
    if (monster.monsterFamilies?.[0]) tags.push(monster.monsterFamilies[0]);
    // Note: environments not available in MonsterInfo interface

    // Create description from tag line or family info
    let description = monster.tag_line;
    if (!description && monster.monsterFamilies?.[0]) {
      description = `A ${monster.creature_type?.toLowerCase() || 'creature'} from the ${monster.monsterFamilies[0]} family.`;
    }
    if (!description) {
      description = `A ${monster.creature_type?.toLowerCase() || 'creature'} of challenge rating ${monster.cr}.`;
    }

    return html`
      <div>
        <a
          class="monster-row ${isSelected ? 'selected' : ''}"
          style="background-image: url('${monster.background_image || ''}'); background-position: ${backgroundPosition};"
          href="/monsters/${monster.key}/"
          @click=${(e: Event) => this.handleMonsterClick(e, monster.key)}
          @mouseenter=${() => this.previewMonsterByKey(monster.key)}>
          <div class="monster-info">
            <div class="monster-name">${monster.name}</div>
            <div class="monster-details">${details}</div>

            <!-- Mobile: Rich card content -->
            <div class="monster-tags">
              ${tags.slice(0, 3).map(tag => html`
                <span class="monster-tag">${tag}</span>
              `)}
            </div>

            <div class="monster-description">${description}</div>

            <div class="monster-actions">
              <button class="monster-action-btn"
                      @click=${(e: Event) => this.handleForgeClick(e, monster.key)}>
                Forge
              </button>
              <button class="monster-action-btn secondary"
                      @click=${(e: Event) => this.handleShareClick(e, monster.key)}>
                Share
              </button>
            </div>
          </div>
        </a>
        ${isExpanded ? html`
          <div class="monster-drawer">
            <monster-statblock
              monster-key="${monster.key}"
              link-header
              hide-buttons="false"
            ></monster-statblock>
          </div>
        ` : ''}
      </div>
    `;
  }

  private groupMonsters(monsters: MonsterInfo[]): Record<string, MonsterInfo[]> {
    if (this.groupBy === 'relevance') {
      // For relevance, return all monsters in a single group to maintain search order
      return { 'Search Results': monsters };
    }

    const groups: Record<string, MonsterInfo[]> = {};
    monsters.forEach(monster => {
      let groupKey: string;
      switch (this.groupBy) {
        case 'family':
          groupKey = monster.monsterFamilies?.[0] || 'Other';
          break;
        case 'challenge':
          groupKey = `Challenge Rating ${monster.cr}`;
          break;
        case 'name':
          groupKey = monster.name.charAt(0).toUpperCase();
          break;
        default:
          groupKey = 'Other';
      }
      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push(monster);
    });
    const sortedGroups: Record<string, MonsterInfo[]> = {};
    Object.keys(groups).sort().forEach(key => {
      sortedGroups[key] = groups[key].sort((a, b) => a.name.localeCompare(b.name));
    });
    return sortedGroups;
  }

  private handleSearchInput(e: Event) {
    const input = e.target as HTMLInputElement;
    // Debounce search: only update query after 1s of no typing
    const value = input.value;
    if (this.searchDebounceTimer) {
      clearTimeout(this.searchDebounceTimer);
    }
    this.searchDebounceTimer = window.setTimeout(() => {
      this.query = value;
    }, 1000);
  }

  private toggleCreatureType(type: string) {
    if (this.selectedCreatureTypes?.includes(type)) {
      this.selectedCreatureTypes = this.selectedCreatureTypes.filter(t => t !== type);
    } else {
      this.selectedCreatureTypes = [...this.selectedCreatureTypes, type];
    }
  }
  private handleMinCrChange(e: Event) {
    const input = e.target as HTMLInputElement;
    const value = parseInt(input.value);

    // Update temp value for immediate visual feedback
    this.tempMinCr = value;
    this.requestUpdate();

    // Debounce the actual filter update
    if (this.crDebounceTimer) {
      clearTimeout(this.crDebounceTimer);
    }
    this.crDebounceTimer = window.setTimeout(() => {
      this.minCr = value === 0 ? undefined : value;
      this.tempMinCr = undefined;
    }, 300);
  }

  private handleMaxCrChange(e: Event) {
    const input = e.target as HTMLInputElement;
    const value = parseInt(input.value);

    // Update temp value for immediate visual feedback
    this.tempMaxCr = value;
    this.requestUpdate();

    // Debounce the actual filter update
    if (this.crDebounceTimer) {
      clearTimeout(this.crDebounceTimer);
    }
    this.crDebounceTimer = window.setTimeout(() => {
      this.maxCr = value === 30 ? undefined : value;
      this.tempMaxCr = undefined;
    }, 300);
  }

  private setGroupBy(groupBy: 'family' | 'challenge' | 'name' | 'relevance') {
    this.groupBy = groupBy;
    this.requestUpdate();
  }

  private setContentTab(tab: 'preview' | 'lore' | 'encounters') {
    this.contentTab = tab;
    this.requestUpdate();
  }

  private selectMonster(monster: Monster) {
    this.selectedMonster = monster;
  }

  private async selectMonsterByKey(key: string) {
    try {
      const monster = await this.apiStore.getMonster(key);
      if (monster) {
        this.selectedMonster = monster;
        this.selectedMonsterKey = key; // Mark as explicitly selected for sticky behavior
      }
    } catch (e) {
      console.error('Error selecting monster by key:', e);
    }
  }

  private toggleMonsterDrawer(key: string) {
    if (this.expandedMonsterKey === key) {
      // Close if already expanded
      this.expandedMonsterKey = null;
    } else {
      // Open drawer for this monster and also select it for preview
      this.expandedMonsterKey = key;
      this.selectMonsterByKey(key);
    }
  }

  private previewMonsterByKey(key: string) {
    // Only update preview if no monster is explicitly selected (sticky behavior)
    if (this.selectedMonsterKey === null) {
      this.apiStore.getMonster(key).then(monster => {
        if (monster) {
          this.selectedMonster = monster;
        }
      });
    }
  }

  private hasActiveFilters() {
    return this.query !== '' || this.selectedCreatureTypes.length > 0 || this.minCr !== undefined || this.maxCr !== undefined;
  }

  private getActiveFilterCount() {
    let count = 0;
    if (this.query !== '') count++;
    count += this.selectedCreatureTypes.length;
    if (this.minCr !== undefined) count++;
    if (this.maxCr !== undefined) count++;
    return count;
  }

  private toggleFiltersPanel() {
    this.filtersPanelVisible = !this.filtersPanelVisible;
  }

  private clearAllFilters() {
    this.query = '';
    this.selectedCreatureTypes = [];
    this.selectedEnvironments = [];
    this.selectedRoles = [];
    this.minCr = undefined;
    this.maxCr = undefined;
    this.selectedMonsterKey = null; // Clear sticky selection
    this.selectedMonster = null;
    this.expandedMonsterKey = null; // Close any open drawer
    // Task will auto-update
  }

  private async loadInitialData() {
    try {
      const facets = await this.searchApi.getFacets();
      this.facets = facets;
    } catch (e) {
      console.error('Error loading initial data:', e);
    }
  }

  private handleMonsterClick(e: Event, key: string) {
    // On mobile: Allow navigation to monster page
    // On desktop: Prevent navigation and toggle drawer instead
    if (window.innerWidth >= 1040) {
      e.preventDefault();
      this.toggleMonsterDrawer(key);
    }
    // On mobile, let the natural navigation happen
  }

  private handleForgeClick(e: Event, key: string) {
    e.preventDefault();
    e.stopPropagation();
    // Navigate to the forge page with this monster
    window.location.href = `/generate/?monster=${key}`;
  }

  private handleShareClick(e: Event, key: string) {
    e.preventDefault();
    e.stopPropagation();
    // Copy monster URL to clipboard
    const url = `${window.location.origin}/monsters/${key}/`;
    navigator.clipboard.writeText(url).then(() => {
      // Show a toast notification or similar feedback
      console.log('Monster URL copied to clipboard:', url);
    }).catch(err => {
      console.error('Failed to copy URL:', err);
    });
  }

  updated(changedProperties: Map<string | number | symbol, unknown>) {
    super.updated(changedProperties);
    if (changedProperties.has('selectedMonster') || changedProperties.has('monsters')) {
      this.requestUpdate();
    }
  }
}
