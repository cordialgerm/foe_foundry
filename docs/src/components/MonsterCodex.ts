import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { MonsterInfo, MonsterSearchRequest, SearchFacets, MonsterSearchResult } from '../data/search.js';
import { Monster } from '../data/monster.js';
import { MonsterSearchApi } from '../data/searchApi.js';
import { ApiMonsterStore } from '../data/api.js';
import './MonsterCardPreview.js';
import { Task } from '@lit/task';

@customElement('monster-codex')
export class MonsterCodex extends LitElement {
  @state() private query = '';
  @state() private selectedCreatureTypes: string[] = [];
  @state() private selectedEnvironments: string[] = [];
  @state() private selectedRoles: string[] = [];
  @state() private minCr?: number;
  @state() private maxCr?: number;
  @state() private groupBy: 'family' | 'challenge' | 'name' = 'family';
  @state() private monsters: MonsterInfo[] = [];
  @state() private facets: SearchFacets | null = null;
  @state() private selectedMonster: Monster | null = null;
  @state() private loading = false;
  @state() private filtersPanelVisible = window.innerWidth >= 900; // Hidden by default on medium screens
  @state() private selectedMonsterKey: string | null = null; // Track explicitly selected monster for sticky behavior

  private searchApi = new MonsterSearchApi();
  private apiStore = new ApiMonsterStore();
  private searchDebounceTimer: number | undefined;

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
      display: block;
      height: 100vh;
      overflow: hidden;
    }

    .codex-container {
      display: grid;
      grid-template-columns: 300px 1fr 400px;
      height: 100vh;
      gap: 1.5rem;
      padding: 1.5rem;
    }

    .codex-container.filters-hidden {
      grid-template-columns: 0 1fr 400px;
      gap: 0 1.5rem;
    }

    .filters-panel {
      background: rgba(26, 26, 26, 0.8);
      backdrop-filter: blur(10px);
      border-radius: var(--medium-margin);
      padding: 1.5rem;
      overflow-y: auto;
      width: 300px;
      transition: width 0.3s ease-in-out, padding 0.3s ease-in-out;
      border-right: 2px solid var(--primary-color);
      position: relative;
      border: 1px solid rgba(255, 55, 55, 0.3);
    }

    .filters-panel.hidden {
      width: 0;
      padding: 0;
      overflow: hidden;
      border-right: none;
      border: none;
    }

    .panel-divider {
      position: absolute;
      top: 50%;
      right: -12px;
      transform: translateY(-50%);
      background: var(--primary-color);
      color: var(--fg-color);
      border: none;
      width: 24px;
      height: 48px;
      border-radius: 0 6px 6px 0;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      z-index: 3;
      transition: all 0.2s ease;
      border: 1px solid rgba(255, 55, 55, 0.5);
      box-shadow: 2px 0 8px rgba(0, 0, 0, 0.3);
    }

    .panel-divider:hover {
      background: var(--primary-muted-color);
      transform: translateY(-50%) scale(1.1);
    }

    .monster-list-panel {
      background: rgba(26, 26, 26, 0.8);
      backdrop-filter: blur(10px);
      border-radius: var(--medium-margin);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      border: 1px solid rgba(255, 55, 55, 0.3);
    }

    .preview-panel {
      background: rgba(26, 26, 26, 0.8);
      backdrop-filter: blur(10px);
      border-radius: var(--medium-margin);
      padding: 1.5rem;
      overflow-y: auto;
      border: 1px solid rgba(255, 55, 55, 0.3);
      z-index: 1;
    }

    /* Search bar styles */
    .search-bar {
      padding: 1.5rem;
      display: flex;
      gap: 0.75rem;
      align-items: center;
      z-index: 5;
      position: relative;
    }

    .search-input-container {
      flex: 1;
    }

    .search-input {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid var(--primary-color);
      border-radius: 4px;
      background: var(--muted-color);
      color: var(--fg-color);
      font-size: 1rem;
    }

    .search-input::placeholder {
      color: var(--primary-muted-color);
    }

    .search-input:focus {
      outline: none;
      border-color: var(--primary-color);
      box-shadow: 0 0 0 2px var(--primary-faded-color);
    }

    /* Filter styles */
    .filters-container h3 {
      color: var(--primary-color);
      margin-bottom: 1rem;
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
      border: 1px solid var(--primary-color);
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
    }

    .filter-pill.active {
      background: var(--primary-color);
      color: var(--fg-color);
      font-weight: bold;
    }

    .group-buttons {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }

    .group-btn {
      padding: 0.5rem 1rem;
      border: 1px solid var(--primary-color);
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
    }

    .group-btn.active {
      background: var(--primary-color);
      color: var(--fg-color);
      font-weight: bold;
    }

    .cr-range {
      color: var(--fg-color);
      font-family: var(--primary-font);
      font-size: 0.9rem;
      margin-top: 0.5rem;
    }

    /* Monster list styles */
    .monster-list {
      flex: 1;
      overflow-y: auto;
      padding: 1.5rem;
    }

    .group-header {
      font-size: 1.1rem;
      font-weight: bold;
      color: var(--primary-color);
      margin: 1rem 0 0.5rem 0;
      padding-bottom: 0.25rem;
      border-bottom: 1px solid var(--primary-color);
      position: sticky;
      top: 0;
      background: var(--bg-color);
      z-index: 1;
      font-family: var(--header-font);
    }

    .monster-row {
      display: flex;
      align-items: center;
      padding: 0.75rem;
      margin-bottom: 0.5rem;
      border-radius: 6px;
      cursor: pointer;
      background-size: cover;
      background-position: center;
      background-blend-mode: overlay;
      background-color: rgba(0,0,0,0.4);
      transition: all 0.2s ease;
      border: 1px solid transparent;
      position: relative;
      min-height: 70px;
    }

    .monster-row::before {
      content: '';
      position: absolute;
      inset: 0;
      background-image: inherit;
      background-size: cover;
      background-position: center;
      background-repeat: no-repeat;
      border-radius: inherit;
      opacity: 0.6;
      z-index: 0;
    }

    .monster-row:hover {
      background-color: rgba(0,0,0,0.2);
      transform: translateX(6px);
      border-color: var(--primary-color);
      box-shadow: 0 4px 12px rgba(255, 55, 55, 0.2);
    }

    .monster-row.selected {
      background-color: var(--primary-faded-color);
      border: 1px solid var(--primary-color);
      box-shadow: 0 4px 12px rgba(255, 55, 55, 0.3);
    }

    .monster-info {
      color: white;
      text-shadow: 2px 2px 6px rgba(0,0,0,0.9);
      font-family: var(--primary-font);
      position: relative;
      z-index: 1;
      background: rgba(0,0,0,0.4);
      padding: 0.75rem;
      border-radius: 6px;
      backdrop-filter: blur(4px);
      flex: 1;
    }

    .monster-name {
      font-weight: bold;
      margin-bottom: 0.25rem;
      font-size: 1rem;
    }

    .monster-cr {
      font-size: 0.9rem;
      opacity: 0.9;
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
      color: var(--primary-muted-color);
      text-align: center;
      font-family: var(--primary-font);
    }

    .no-results {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      height: 200px;
      color: var(--primary-muted-color);
      text-align: center;
      font-family: var(--primary-font);
    }

    .no-results h4 {
      color: var(--primary-color);
      margin-bottom: 0.5rem;
    }

    .clear-filters-btn {
      background: var(--primary-color);
      color: var(--fg-color);
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      cursor: pointer;
      font-family: var(--primary-font);
      margin-top: 1rem;
      transition: all 0.2s ease;
    }

    .clear-filters-btn:hover {
      background: var(--primary-muted-color);
    }

    /* Filter toggle button styles */
    .filter-toggle-btn {
      background: var(--primary-color);
      color: var(--fg-color);
      border: none;
      padding: 0.75rem;
      border-radius: 4px;
      cursor: pointer;
      font-family: var(--primary-font);
      font-size: 0.9rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.2s ease;
      position: relative;
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

    /* Mobile responsive */
    @media (max-width: 1200px) {
      .codex-container {
        grid-template-columns: 280px 1fr 350px;
      }
      .codex-container.filters-hidden {
        grid-template-columns: 0 1fr 350px;
      }
      .filters-panel {
        width: 280px;
      }
    }

    @media (max-width: 900px) {
      .codex-container {
        grid-template-columns: 1fr;
        grid-template-rows: auto 1fr;
        gap: 0;
      }
      .codex-container.filters-hidden {
        grid-template-columns: 1fr;
      }

      .filters-panel {
        position: absolute;
        top: 0;
        left: 0;
        height: 100vh;
        z-index: 10;
        background: var(--bg-color);
        box-shadow: 2px 0 8px rgba(0,0,0,0.3);
        width: 300px;
        transform: translateX(0);
        transition: transform 0.3s ease-in-out;
        border-right: none;
      }

      .filters-panel.hidden {
        transform: translateX(-100%);
        width: 300px;
        padding: 1rem;
        overflow-y: auto;
      }

      .panel-divider {
        display: none;
      }

      .monster-list-panel {
        border-radius: 0;
        border: none;
      }

      .preview-panel {
        display: none; /* Hide preview panel on mobile */
      }
    }
  `;

  async connectedCallback() {
    super.connectedCallback();
    await this.loadInitialData();
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
        <!-- Filters Panel -->
        <div class="filters-panel ${this.filtersPanelVisible ? '' : 'hidden'}">
          <div class="filters-container">
            <h3>Filters</h3>
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
                CR ${this.minCr || facets.crRange.min || 0} - ${this.maxCr || facets.crRange.max || 30}
              </div>
              <!-- TODO: Add CR range slider here -->
            </div>
            <div class="filter-section">
              <h4>Organize Monsters By</h4>
              <div class="group-buttons">
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
          <!-- Panel divider with collapse indicator -->
          <button
            class="panel-divider"
            @click=${this.toggleFiltersPanel}
            title="${this.filtersPanelVisible ? 'Hide Filters' : 'Show Filters'}">
            ${this.filtersPanelVisible ? '◀' : '▶'}
          </button>
        </div>

        <!-- Monster List Panel -->
        <div class="monster-list-panel">
          <div class="search-bar">
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

        <!-- Preview Panel -->
        <div class="preview-panel">
          ${this.selectedMonster ? html`
            <monster-card-preview
              monster-key="${this.selectedMonster.key}"
              .compact=${false}
            ></monster-card-preview>
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
        <div class="group-header">${groupName}</div>
        ${monsters.map(monster => this.renderMonsterRow(monster))}
      `)}
    `;
  }

  private renderMonsterRow(monster: MonsterInfo) {
    const isSelected = this.selectedMonsterKey === monster.key;
    return html`
      <div
        class="monster-row ${isSelected ? 'selected' : ''}"
        style="background-image: url('${monster.background_image || ''}')"
        @click=${() => this.selectMonsterByKey(monster.key)}
        @mouseenter=${() => this.previewMonsterByKey(monster.key)}>
        <div class="monster-info">
          <div class="monster-name">${monster.name}</div>
          <div class="monster-cr">${monster.cr}</div>
        </div>
      </div>
    `;
  }

  private groupMonsters(monsters: MonsterInfo[]): Record<string, MonsterInfo[]> {
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
  private setGroupBy(groupBy: 'family' | 'challenge' | 'name') {
    this.groupBy = groupBy;
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

  updated(changedProperties: Map<string | number | symbol, unknown>) {
    super.updated(changedProperties);
    if (changedProperties.has('selectedMonster') || changedProperties.has('monsters')) {
      this.requestUpdate();
    }
  }
}
