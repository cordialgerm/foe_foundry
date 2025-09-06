import { LitElement, html, css } from 'lit';
import { customElement, state, property } from 'lit/decorators.js';
import { Task } from '@lit/task';
import { apiMonsterStore, CatalogTemplate, CatalogFamily } from '../data/api.js';
import { trackSearch, trackMonsterClick } from '../utils/analytics.js';
import './SvgIcon.js';

type CatalogGroupBy = 'template' | 'family';

@customElement('monster-catalog')
export class MonsterCatalog extends LitElement {
  @property({ attribute: 'initial-group-by' }) initialGroupBy: CatalogGroupBy = 'template';
  @state() private groupBy: CatalogGroupBy = 'template';

  private catalogTask = new Task(this, {
    task: async ([groupBy]: [CatalogGroupBy]) => {
      if (groupBy === 'template') {
        return { data: await apiMonsterStore.getCatalogByTemplate(), type: 'template' as const };
      } else {
        return { data: await apiMonsterStore.getCatalogByFamily(), type: 'family' as const };
      }
    },
    args: () => [this.groupBy] as [CatalogGroupBy]
  });

  static styles = css`
    :host {
      display: block;
      height: 100%;
      min-height: 100vh;
    }

    .catalog-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 100vh;
      padding: 1rem;
    }

    /* Search Bar */
    .catalog-search-section {
      margin-bottom: 2rem;
    }

    .search-input-container {
      display: flex;
      gap: 0.75rem;
      align-items: center;
      max-width: 600px;
      margin: 0 auto;
    }

    .catalog-search-input {
      flex: 1;
      padding: 0.75rem;
      border: 1px solid var(--border-color);
      border-radius: 4px;
      background: var(--muted-color);
      color: var(--fg-color);
      font-size: 1rem;
      min-height: 44px;
      box-sizing: border-box;
    }

    .catalog-search-input::placeholder {
      color: var(--fg-muted-color);
    }

    .catalog-search-input:focus {
      outline: none;
      border-color: var(--border-color);
      box-shadow: 0 0 0 2px var(--fg-muted-color);
    }

    .search-button {
      background: var(--tertiary-color);
      color: var(--fg-color);
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 4px;
      cursor: pointer;
      font-family: var(--primary-font);
      font-size: 1rem;
      font-weight: bold;
      min-height: 44px;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.2s ease;
    }

    .search-button:hover {
      background: var(--tertiary-color);
      transform: translateY(-1px);
    }

    /* Group By Controls */
    .catalog-controls {
      display: flex;
      justify-content: center;
      gap: 1rem;
      margin-bottom: 2rem;
    }

    .group-toggle-btn {
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

    .group-toggle-btn:hover {
      background: var(--primary-color);
      color: var(--fg-color);
      border-color: var(--primary-color);
    }

    .group-toggle-btn.active {
      background: var(--primary-color);
      color: var(--fg-color);
      font-weight: bold;
      border-color: var(--primary-color);
    }

    /* Catalog List */
    .catalog-list {
      flex: 1;
      overflow-y: auto;
    }

    .catalog-group {
      margin-bottom: 2rem;
    }

    .catalog-group-header {
      font-size: 1.5rem;
      font-weight: bold;
      color: var(--primary-color);
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 2px solid var(--border-color);
      font-family: var(--header-font);
    }

    .catalog-group-header a {
      color: inherit;
      text-decoration: none;
      transition: color 0.2s ease;
    }

    .catalog-group-header a:hover {
      color: var(--tertiary-color);
    }

    .catalog-monsters {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 0.5rem;
      margin-left: 1rem;
    }

    .catalog-monster {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.5rem 0.75rem;
      border: 1px solid transparent;
      border-radius: 4px;
      transition: all 0.2s ease;
      background: var(--muted-color);
    }

    .catalog-monster:hover {
      background: var(--primary-color);
      border-color: var(--border-color);
      transform: translateX(4px);
    }

    .catalog-monster-name {
      flex: 1;
      color: var(--fg-color);
      text-decoration: none;
      font-weight: 500;
    }

    .catalog-monster-cr {
      color: var(--fg-muted-color);
      font-size: 0.9rem;
      font-weight: bold;
      margin-left: 1rem;
    }

    .catalog-monster:hover .catalog-monster-name,
    .catalog-monster:hover .catalog-monster-cr {
      color: var(--fg-color);
    }

    /* Loading and error states */
    .loading, .error {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 200px;
      color: var(--fg-color);
      font-family: var(--primary-font);
      text-align: center;
    }

    .error {
      color: var(--tertiary-color);
    }

    /* Responsive design */
    @media (max-width: 768px) {
      .catalog-container {
        padding: 0.5rem;
      }

      .catalog-controls {
        flex-direction: column;
        align-items: center;
      }

      .catalog-monsters {
        grid-template-columns: 1fr;
        margin-left: 0;
      }

      .catalog-group-header {
        font-size: 1.3rem;
      }
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    if (this.initialGroupBy) {
      this.groupBy = this.initialGroupBy;
    }
  }

  render() {
    return html`
      <div class="catalog-container">
        <!-- Search Bar -->
        <div class="catalog-search-section">
          <div class="search-input-container">
            <input
              type="text"
              class="catalog-search-input"
              placeholder="Search for monsters..."
              @keydown=${this.handleSearchKeydown}
            />
            <button class="search-button" @click=${this.handleSearchClick}>
              <svg-icon src="magnifying-glass" class="search-icon"></svg-icon>
              Search
            </button>
          </div>
        </div>

        <!-- Group By Controls -->
        <div class="catalog-controls">
          <button
            class="group-toggle-btn ${this.groupBy === 'template' ? 'active' : ''}"
            @click=${() => this.setGroupBy('template')}>
            By Monster
          </button>
          <button
            class="group-toggle-btn ${this.groupBy === 'family' ? 'active' : ''}"
            @click=${() => this.setGroupBy('family')}>
            By Monster Family
          </button>
        </div>

        <!-- Catalog List -->
        <div class="catalog-list">
          ${this.catalogTask.render({
            pending: () => html`<div class="loading">Loading monster catalog...</div>`,
            complete: (result) => this.renderCatalog(result),
            error: (e) => html`<div class="error">Error loading catalog: ${e instanceof Error ? e.message : String(e)}</div>`
          })}
        </div>
      </div>
    `;
  }

  private renderCatalog(result: { data: CatalogTemplate[] | CatalogFamily[], type: 'template' | 'family' }) {
    const { data, type } = result;
    
    if (!data || data.length === 0) {
      return html`<div class="error">No monsters found in catalog.</div>`;
    }

    return html`
      ${data.map(group => html`
        <div class="catalog-group">
          <h2 class="catalog-group-header">
            <a href="${group.url}" @click=${(e: Event) => this.handleGroupClick(e, group, type)}>
              ${group.name}
            </a>
          </h2>
          <div class="catalog-monsters">
            ${group.monsters.map(monster => this.renderMonster(monster))}
          </div>
        </div>
      `)}
    `;
  }

  private renderMonster(monster: { key: string; name: string; cr: number | string }) {
    const crDisplay = typeof monster.cr === 'number' ? 
      (monster.cr === 0.125 ? 'CR ⅛' :
       monster.cr === 0.25 ? 'CR ¼' :
       monster.cr === 0.5 ? 'CR ½' :
       `CR ${monster.cr}`) :
      monster.cr;

    return html`
      <div class="catalog-monster">
        <a 
          href="/monsters/${monster.key}/"
          class="catalog-monster-name"
          @click=${(e: Event) => this.handleMonsterClick(e, monster.key)}>
          ${monster.name}
        </a>
        <span class="catalog-monster-cr">${crDisplay}</span>
      </div>
    `;
  }

  private setGroupBy(groupBy: CatalogGroupBy) {
    this.groupBy = groupBy;
  }

  private handleSearchKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      this.performSearch();
    }
  }

  private handleSearchClick() {
    this.performSearch();
  }

  private performSearch() {
    const input = this.shadowRoot?.querySelector('.catalog-search-input') as HTMLInputElement;
    const query = input?.value?.trim();
    
    if (query) {
      // Track search analytics
      trackSearch(query, 0, 'catalog');
      
      // Dispatch event to switch to search tab with the query
      const event = new CustomEvent('catalog-search', {
        detail: { query },
        bubbles: true,
        composed: true
      });
      this.dispatchEvent(event);
    }
  }

  private handleGroupClick(e: Event, group: CatalogTemplate | CatalogFamily, type: 'template' | 'family') {
    // Track analytics for group click
    trackMonsterClick(
      group.key,
      type === 'template' ? 'template' : 'family',
      'catalog-group',
      ''
    );
  }

  private handleMonsterClick(e: Event, monsterKey: string) {
    // Track analytics for monster click
    trackMonsterClick(
      monsterKey,
      'monster',
      'catalog-monster',
      ''
    );
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'monster-catalog': MonsterCatalog;
  }
}