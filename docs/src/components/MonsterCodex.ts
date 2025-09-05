import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { Task } from '@lit/task';
import { MonsterStore } from '../data/monster';
import { adoptExternalCss } from '../utils';

// Configuration for responsive layout - reusing patterns from MonsterBuilder
const LAYOUT_CONFIG = {
  // Component dimensions  
  MOBILE_BREAKPOINT: 1040,
  SMALL_MOBILE: 480,
  LARGE_DESKTOP: 1200,

  // Helper methods
  isMobile: (width: number) => width <= LAYOUT_CONFIG.MOBILE_BREAKPOINT,
  isSmallMobile: (width: number) => width <= LAYOUT_CONFIG.SMALL_MOBILE,
  isLargeDesktop: (width: number) => width >= LAYOUT_CONFIG.LARGE_DESKTOP
} as const;

export interface MonsterCardData {
  key: string;
  name: string;
  template: string;
  cr: number | string;
  creatureType: string;
  environment?: string;
  role?: string;
  family?: string;
  tagLine?: string;
  image?: string;
  backgroundImage?: string;
}

export interface FilterState {
  query: string;
  creatureTypes: string[];
  environments: string[];
  roles: string[];
  crMin: number;
  crMax: number;
  organizeBy: 'family' | 'challenge' | 'name';
}

@customElement('monster-codex')
export class MonsterCodex extends LitElement {
  @property({ type: Object })
  monsterStore?: MonsterStore;

  @state()
  private isMobile: boolean = false;

  @state()
  private isFiltersExpanded: boolean = false;

  @state()
  private filters: FilterState = {
    query: '',
    creatureTypes: [],
    environments: [],
    roles: [],
    crMin: 0,
    crMax: 20,
    organizeBy: 'family'
  };

  @state()
  private monsters: MonsterCardData[] = [];

  @state()
  private filteredMonsters: MonsterCardData[] = [];

  @state()
  private groupedMonsters: Map<string, MonsterCardData[]> = new Map();

  private resizeObserver?: ResizeObserver;

  static styles = css`
    :host {
      display: block;
      width: 100%;
      contain: layout style;
    }

    .codex-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 1rem;
    }

    /* Header */
    .codex-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 2rem;
      padding-bottom: 1rem;
      border-bottom: 2px solid var(--tertiary-color);
    }

    .codex-title {
      font-size: 2rem;
      font-weight: bold;
      color: var(--fg-color);
      margin: 0;
    }

    .hamburger-button {
      display: none;
      background: none;
      border: none;
      font-size: 1.5rem;
      color: var(--fg-color);
      cursor: pointer;
      padding: 0.5rem;
    }

    /* Search Section */
    .search-section {
      margin-bottom: 1.5rem;
    }

    .search-bar {
      position: relative;
      margin-bottom: 1rem;
    }

    .search-input {
      width: 100%;
      padding: 1rem 1rem 1rem 3rem;
      font-size: 1.1rem;
      border: 2px solid var(--tertiary-color);
      border-radius: 8px;
      background: var(--bg-color);
      color: var(--fg-color);
      outline: none;
      transition: border-color 0.2s;
    }

    .search-input:focus {
      border-color: var(--accent-color);
    }

    .search-icon {
      position: absolute;
      left: 1rem;
      top: 50%;
      transform: translateY(-50%);
      width: 1.2rem;
      height: 1.2rem;
      opacity: 0.6;
    }

    /* Filters */
    .filters-section {
      background: var(--bg-color);
      border: 1px solid var(--tertiary-color);
      border-radius: 8px;
      overflow: hidden;
    }

    .filters-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1rem;
      background: var(--accent-color);
      color: white;
      cursor: pointer;
      font-weight: bold;
      user-select: none;
    }

    .filters-chevron {
      width: 1rem;
      height: 1rem;
      transition: transform 0.2s;
    }

    .filters-chevron.expanded {
      transform: rotate(180deg);
    }

    .filters-content {
      display: none;
      padding: 1.5rem;
      background: var(--bg-color);
    }

    .filters-content.expanded {
      display: block;
    }

    .filter-group {
      margin-bottom: 1.5rem;
    }

    .filter-group:last-child {
      margin-bottom: 0;
    }

    .filter-label {
      display: block;
      font-weight: bold;
      margin-bottom: 0.5rem;
      color: var(--fg-color);
    }

    .filter-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .filter-tag {
      padding: 0.4rem 0.8rem;
      border: 1px solid var(--tertiary-color);
      border-radius: 16px;
      background: var(--bg-color);
      color: var(--fg-color);
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.2s;
      user-select: none;
      min-height: 44px; /* Touch target */
      display: flex;
      align-items: center;
    }

    .filter-tag:hover {
      background: var(--tertiary-color);
    }

    .filter-tag.active {
      background: var(--accent-color);
      color: white;
      border-color: var(--accent-color);
    }

    /* Challenge Rating Slider */
    .cr-slider-container {
      margin-top: 1rem;
    }

    .cr-slider {
      width: 100%;
      height: 6px;
      border-radius: 3px;
      background: var(--tertiary-color);
      outline: none;
      appearance: none;
    }

    .cr-slider::-webkit-slider-thumb {
      appearance: none;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: var(--accent-color);
      cursor: pointer;
    }

    .cr-slider::-moz-range-thumb {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: var(--accent-color);
      cursor: pointer;
      border: none;
    }

    .cr-range-display {
      text-align: center;
      margin-top: 0.5rem;
      font-size: 0.9rem;
      color: var(--fg-color-secondary);
    }

    /* Organize Section */
    .organize-section {
      display: flex;
      gap: 0.5rem;
      margin-top: 1rem;
    }

    .organize-button {
      flex: 1;
      padding: 0.6rem 1rem;
      border: 1px solid var(--tertiary-color);
      border-radius: 6px;
      background: var(--bg-color);
      color: var(--fg-color);
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.2s;
      min-height: 44px; /* Touch target */
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .organize-button:hover {
      background: var(--tertiary-color);
    }

    .organize-button.active {
      background: var(--accent-color);
      color: white;
      border-color: var(--accent-color);
    }

    /* Monster Grid */
    .monsters-section {
      margin-top: 2rem;
    }

    .monster-group {
      margin-bottom: 2rem;
    }

    .group-header {
      display: flex;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid var(--tertiary-color);
    }

    .group-title {
      font-size: 1.2rem;
      font-weight: bold;
      color: var(--fg-color);
      margin: 0;
    }

    .group-count {
      margin-left: auto;
      font-size: 0.9rem;
      color: var(--fg-color-secondary);
    }

    .monster-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 1rem;
    }

    /* Monster Cards */
    .monster-card {
      border: 1px solid var(--tertiary-color);
      border-radius: 12px;
      overflow: hidden;
      background: var(--bg-color);
      transition: transform 0.2s, box-shadow 0.2s;
      cursor: pointer;
      position: relative;
    }

    .monster-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    .monster-card-image {
      width: 100%;
      height: 200px;
      background-size: cover;
      background-position: center;
      background-repeat: no-repeat;
      position: relative;
      display: flex;
      align-items: flex-end;
      background-color: var(--tertiary-color);
    }

    .monster-card-overlay {
      background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
      width: 100%;
      padding: 1rem;
      color: white;
    }

    .monster-card-name {
      font-size: 1.3rem;
      font-weight: bold;
      margin: 0 0 0.25rem 0;
    }

    .monster-card-cr {
      font-size: 0.9rem;
      opacity: 0.9;
      margin: 0;
    }

    .monster-card-content {
      padding: 1rem;
    }

    .monster-card-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      margin-bottom: 0.75rem;
    }

    .monster-tag {
      padding: 0.2rem 0.6rem;
      border-radius: 12px;
      font-size: 0.8rem;
      font-weight: 500;
    }

    .monster-tag.creature-type {
      background: var(--accent-color);
      color: white;
    }

    .monster-tag.family {
      background: var(--tertiary-color);
      color: var(--fg-color);
    }

    .monster-tag.environment {
      background: var(--secondary-color);
      color: var(--fg-color);
    }

    .monster-card-description {
      font-size: 0.9rem;
      line-height: 1.4;
      color: var(--fg-color-secondary);
      margin-bottom: 1rem;
    }

    .monster-card-actions {
      display: flex;
      gap: 0.75rem;
    }

    .action-button {
      flex: 1;
      padding: 0.6rem 1rem;
      border: none;
      border-radius: 6px;
      font-size: 0.9rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
      min-height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .forge-button {
      background: var(--accent-color);
      color: white;
    }

    .forge-button:hover {
      background: var(--accent-color-hover);
    }

    .share-button {
      background: var(--tertiary-color);
      color: var(--fg-color);
      border: 1px solid var(--tertiary-color);
    }

    .share-button:hover {
      background: var(--secondary-color);
    }

    /* Loading States */
    .loading {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 300px;
      font-size: 1.1rem;
      color: var(--fg-color-secondary);
    }

    /* Mobile Styles */
    @media (max-width: ${LAYOUT_CONFIG.MOBILE_BREAKPOINT}px) {
      .codex-container {
        padding: 1rem 0.75rem;
      }

      .hamburger-button {
        display: block;
      }

      .codex-title {
        font-size: 1.5rem;
      }

      .search-input {
        padding: 0.85rem 0.85rem 0.85rem 2.5rem;
        font-size: 1rem;
      }

      .search-icon {
        left: 0.75rem;
        width: 1rem;
        height: 1rem;
      }

      .filters-content {
        padding: 1rem;
      }

      .filter-group {
        margin-bottom: 1rem;
      }

      .organize-section {
        flex-direction: column;
        gap: 0.4rem;
      }

      .organize-button {
        padding: 0.7rem;
      }

      .monster-card-image {
        height: 160px;
      }

      .monster-card-name {
        font-size: 1.1rem;
      }

      .monster-card-content {
        padding: 0.75rem;
      }

      .action-button {
        padding: 0.5rem 0.75rem;
        font-size: 0.85rem;
      }
    }

    @media (max-width: ${LAYOUT_CONFIG.SMALL_MOBILE}px) {
      .codex-container {
        padding: 0.75rem 0.5rem;
      }

      .monster-card-image {
        height: 140px;
      }

      .monster-card-overlay {
        padding: 0.75rem;
      }

      .monster-card-content {
        padding: 0.6rem;
      }
    }

    /* Desktop Grid */
    @media (min-width: ${LAYOUT_CONFIG.MOBILE_BREAKPOINT + 1}px) {
      .monster-grid {
        grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
        gap: 1.5rem;
      }

      .hamburger-button {
        display: none;
      }
    }

    @media (min-width: ${LAYOUT_CONFIG.LARGE_DESKTOP}px) {
      .monster-grid {
        grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
      }
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    this.setupResizeObserver();
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.resizeObserver?.disconnect();
  }

  async firstUpdated() {
    this.checkIsMobile();
    
    if (this.shadowRoot) {
      await adoptExternalCss(this.shadowRoot);
    }

    // Load initial monster data
    await this.loadMonsters();
  }

  private setupResizeObserver() {
    this.resizeObserver = new ResizeObserver(() => {
      this.checkIsMobile();
    });
    this.resizeObserver.observe(this);
  }

  private checkIsMobile() {
    const wasMobile = this.isMobile;
    this.isMobile = LAYOUT_CONFIG.isMobile(window.innerWidth);
    if (wasMobile !== this.isMobile) {
      console.debug('Mobile state changed', {
        isMobile: this.isMobile,
        windowWidth: window.innerWidth,
        breakpoint: LAYOUT_CONFIG.MOBILE_BREAKPOINT
      });
    }
  }

  private async loadMonsters() {
    // TODO: Replace with actual API call to get all monsters
    // For now, using placeholder data that matches the mobile design mockups
    this.monsters = [
      {
        key: 'ice-troll',
        name: 'Ice Troll',
        template: 'troll',
        cr: 4,
        creatureType: 'Giant',
        environment: 'Arctic',
        role: 'Brute',
        family: 'Troll',
        tagLine: 'A hulking troll adapted to frigid climates, with icy skin and a chilling aura. Its regeneration is slowed by fire, but accelerated by cold.',
        backgroundImage: '/img/monsters/ice-troll.webp'
      },
      {
        key: 'winter-wolf',
        name: 'Winter Wolf',
        template: 'wolf',
        cr: 3,
        creatureType: 'Monstrosity',
        environment: 'Arctic',
        role: 'Striker',
        family: 'Wolf',
        tagLine: 'A supernatural wolf with frost-covered fur and icy breath.',
        backgroundImage: '/img/monsters/winter-wolf.webp'
      }
    ];

    this.applyFilters();
  }

  private applyFilters() {
    let filtered = [...this.monsters];

    // Apply search query
    if (this.filters.query.trim()) {
      const query = this.filters.query.toLowerCase();
      filtered = filtered.filter(monster => 
        monster.name.toLowerCase().includes(query) ||
        monster.creatureType.toLowerCase().includes(query) ||
        monster.environment?.toLowerCase().includes(query) ||
        monster.role?.toLowerCase().includes(query) ||
        monster.family?.toLowerCase().includes(query) ||
        monster.tagLine?.toLowerCase().includes(query)
      );
    }

    // Apply creature type filter
    if (this.filters.creatureTypes.length > 0) {
      filtered = filtered.filter(monster => 
        this.filters.creatureTypes.includes(monster.creatureType)
      );
    }

    // Apply environment filter
    if (this.filters.environments.length > 0) {
      filtered = filtered.filter(monster => 
        monster.environment && this.filters.environments.includes(monster.environment)
      );
    }

    // Apply role filter
    if (this.filters.roles.length > 0) {
      filtered = filtered.filter(monster => 
        monster.role && this.filters.roles.includes(monster.role)
      );
    }

    // Apply CR range filter
    filtered = filtered.filter(monster => {
      const cr = typeof monster.cr === 'string' ? parseFloat(monster.cr) : monster.cr;
      return cr >= this.filters.crMin && cr <= this.filters.crMax;
    });

    this.filteredMonsters = filtered;
    this.groupMonsters();
  }

  private groupMonsters() {
    const groups = new Map<string, MonsterCardData[]>();
    
    for (const monster of this.filteredMonsters) {
      let groupKey: string;
      
      switch (this.filters.organizeBy) {
        case 'family':
          groupKey = monster.family || 'Other';
          break;
        case 'challenge':
          const cr = typeof monster.cr === 'string' ? parseFloat(monster.cr) : monster.cr;
          if (cr < 1) groupKey = 'CR 0-1';
          else if (cr < 5) groupKey = 'CR 1-4';
          else if (cr < 11) groupKey = 'CR 5-10';
          else if (cr < 17) groupKey = 'CR 11-16';
          else groupKey = 'CR 17+';
          break;
        case 'name':
          groupKey = monster.name.charAt(0).toUpperCase();
          break;
        default:
          groupKey = 'All';
      }

      if (!groups.has(groupKey)) {
        groups.set(groupKey, []);
      }
      groups.get(groupKey)!.push(monster);
    }

    // Sort groups and monsters within groups
    const sortedGroups = new Map();
    const sortedKeys = Array.from(groups.keys()).sort();
    
    for (const key of sortedKeys) {
      const monsters = groups.get(key)!;
      monsters.sort((a, b) => a.name.localeCompare(b.name));
      sortedGroups.set(key, monsters);
    }

    this.groupedMonsters = sortedGroups;
  }

  private toggleFilters() {
    this.isFiltersExpanded = !this.isFiltersExpanded;
  }

  private handleSearchInput(e: Event) {
    const target = e.target as HTMLInputElement;
    this.filters = { ...this.filters, query: target.value };
    this.applyFilters();
  }

  private toggleFilterTag(category: keyof FilterState, value: string) {
    const currentValues = this.filters[category] as string[];
    const newValues = currentValues.includes(value)
      ? currentValues.filter(v => v !== value)
      : [...currentValues, value];
    
    this.filters = { ...this.filters, [category]: newValues };
    this.applyFilters();
  }

  private setOrganizeBy(organizeBy: FilterState['organizeBy']) {
    this.filters = { ...this.filters, organizeBy };
    this.groupMonsters();
  }

  private handleCrChange(e: Event) {
    const target = e.target as HTMLInputElement;
    const value = parseInt(target.value);
    
    if (target.classList.contains('cr-min')) {
      this.filters = { ...this.filters, crMin: value };
    } else {
      this.filters = { ...this.filters, crMax: value };
    }
    
    this.applyFilters();
  }

  private handleMonsterClick(monster: MonsterCardData) {
    // Navigate to monster page
    window.location.href = `/monsters/${monster.template}/`;
  }

  private handleForgeClick(e: Event, monster: MonsterCardData) {
    e.stopPropagation();
    // Navigate to generator with this monster
    window.location.href = `/generate/?monster=${monster.key}`;
  }

  private handleShareClick(e: Event, monster: MonsterCardData) {
    e.stopPropagation();
    // TODO: Implement sharing functionality
    console.log('Share monster:', monster);
  }

  render() {
    return html`
      <div class="codex-container">
        <header class="codex-header">
          <button class="hamburger-button" @click=${this.toggleFilters}>
            ☰
          </button>
          <h1 class="codex-title">Foe Foundry Monster Codex</h1>
        </header>

        <section class="search-section">
          <div class="search-bar">
            <svg class="search-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="m19.6 21l-6.3-6.3q-.75.6-1.725.95T9.5 16q-2.725 0-4.612-1.888T3 9.5q0-2.725 1.888-4.612T9.5 3q2.725 0 4.612 1.888T16 9.5q0 1.1-.35 2.075T14.7 13.3l6.3 6.3zM9.5 14q1.875 0 3.188-1.313T14 9.5q0-1.875-1.313-3.188T9.5 5Q7.625 5 6.313 6.313T5 9.5q0 1.875 1.313 3.188T9.5 14"/>
            </svg>
            <input 
              type="text" 
              class="search-input"
              placeholder="Search monster name..."
              .value=${this.filters.query}
              @input=${this.handleSearchInput}
            />
          </div>

          <div class="filters-section">
            <div class="filters-header" @click=${this.toggleFilters}>
              <span>Filters</span>
              <svg class="filters-chevron ${this.isFiltersExpanded ? 'expanded' : ''}" viewBox="0 0 24 24" fill="currentColor">
                <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
              </svg>
            </div>
            
            <div class="filters-content ${this.isFiltersExpanded ? 'expanded' : ''}">
              <div class="filter-group">
                <label class="filter-label">Creature Type</label>
                <div class="filter-tags">
                  ${['Aberration', 'Beast', 'Celestial', 'Construct', 'Dragon', 'Elemental', 'Fey', 'Fiend', 'Giant', 'Humanoid', 'Monstrosity', 'Ooze', 'Plant', 'Undead'].map(type => html`
                    <span 
                      class="filter-tag ${this.filters.creatureTypes.includes(type) ? 'active' : ''}"
                      @click=${() => this.toggleFilterTag('creatureTypes', type)}
                    >
                      ${type}
                    </span>
                  `)}
                </div>
              </div>

              <div class="filter-group">
                <label class="filter-label">Environment</label>
                <div class="filter-tags">
                  ${['Arctic', 'Desert', 'Forest', 'Mountain', 'Swamp', 'Urban', 'Underwater', 'Underground'].map(env => html`
                    <span 
                      class="filter-tag ${this.filters.environments.includes(env) ? 'active' : ''}"
                      @click=${() => this.toggleFilterTag('environments', env)}
                    >
                      ${env}
                    </span>
                  `)}
                </div>
              </div>

              <div class="filter-group">
                <label class="filter-label">Role</label>
                <div class="filter-tags">
                  ${['Brute', 'Controller', 'Defender', 'Striker'].map(role => html`
                    <span 
                      class="filter-tag ${this.filters.roles.includes(role) ? 'active' : ''}"
                      @click=${() => this.toggleFilterTag('roles', role)}
                    >
                      ${role}
                    </span>
                  `)}
                </div>
              </div>

              <div class="filter-group">
                <label class="filter-label">Challenge Rating</label>
                <div class="cr-slider-container">
                  <input 
                    type="range" 
                    class="cr-slider cr-min"
                    min="0" 
                    max="20" 
                    .value=${this.filters.crMin.toString()}
                    @input=${this.handleCrChange}
                  />
                  <input 
                    type="range" 
                    class="cr-slider cr-max"
                    min="0" 
                    max="20" 
                    .value=${this.filters.crMax.toString()}
                    @input=${this.handleCrChange}
                  />
                  <div class="cr-range-display">
                    CR: ${this.filters.crMin} - ${this.filters.crMax}
                  </div>
                </div>
              </div>

              <div class="filter-group">
                <label class="filter-label">Organize Monsters By:</label>
                <div class="organize-section">
                  <button 
                    class="organize-button ${this.filters.organizeBy === 'family' ? 'active' : ''}"
                    @click=${() => this.setOrganizeBy('family')}
                  >
                    Family
                  </button>
                  <button 
                    class="organize-button ${this.filters.organizeBy === 'challenge' ? 'active' : ''}"
                    @click=${() => this.setOrganizeBy('challenge')}
                  >
                    Challenge
                  </button>
                  <button 
                    class="organize-button ${this.filters.organizeBy === 'name' ? 'active' : ''}"
                    @click=${() => this.setOrganizeBy('name')}
                  >
                    Name
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="monsters-section">
          ${Array.from(this.groupedMonsters.entries()).map(([groupName, monsters]) => html`
            <div class="monster-group">
              <div class="group-header">
                <h2 class="group-title">${groupName}</h2>
                <span class="group-count">${monsters.length} monster${monsters.length !== 1 ? 's' : ''}</span>
              </div>
              <div class="monster-grid">
                ${monsters.map(monster => this.renderMonsterCard(monster))}
              </div>
            </div>
          `)}
          
          ${this.groupedMonsters.size === 0 ? html`
            <div class="loading">
              ${this.filteredMonsters.length === 0 ? 'No monsters found matching your criteria.' : 'Loading monsters...'}
            </div>
          ` : ''}
        </section>
      </div>
    `;
  }

  private renderMonsterCard(monster: MonsterCardData) {
    return html`
      <div class="monster-card" @click=${() => this.handleMonsterClick(monster)}>
        <div 
          class="monster-card-image"
          style=${monster.backgroundImage ? `background-image: url(${monster.backgroundImage})` : ''}
        >
          <div class="monster-card-overlay">
            <h3 class="monster-card-name">${monster.name}</h3>
            <p class="monster-card-cr">CR ${monster.cr} | ${monster.role || 'Unknown Role'}</p>
          </div>
        </div>
        
        <div class="monster-card-content">
          <div class="monster-card-tags">
            <span class="monster-tag creature-type">${monster.creatureType}</span>
            ${monster.family ? html`<span class="monster-tag family">${monster.family}</span>` : ''}
            ${monster.environment ? html`<span class="monster-tag environment">${monster.environment}</span>` : ''}
          </div>
          
          ${monster.tagLine ? html`
            <p class="monster-card-description">${monster.tagLine}</p>
          ` : ''}
          
          <div class="monster-card-actions">
            <button 
              class="action-button forge-button"
              @click=${(e: Event) => this.handleForgeClick(e, monster)}
            >
              Forge
            </button>
            <button 
              class="action-button share-button"
              @click=${(e: Event) => this.handleShareClick(e, monster)}
            >
              Share
            </button>
          </div>
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'monster-codex': MonsterCodex;
  }
}