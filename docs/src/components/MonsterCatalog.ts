import { LitElement, html, css } from 'lit';
import { customElement, state, property } from 'lit/decorators.js';
import { Task } from '@lit/task';
import { apiMonsterStore, CatalogTemplate, CatalogFamily } from '../data/api.js';
import { trackMonsterClick } from '../utils/analytics.js';
import './SvgIcon.js';
import './SearchBar.js';

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

    /* Catalog Search Section */
    .catalog-search-section {
      margin-bottom: 2rem;
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
      column-count: 1;
      column-gap: 2rem;
      column-fill: balance;
    }

    .catalog-group {
      margin-bottom: 2rem;
      break-inside: avoid;
      page-break-inside: avoid;
      display: inline-block;
      width: 100%;
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
      grid-template-columns: 1fr;
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
    @media (min-width: 769px) and (max-width: 1200px) {
      .catalog-list {
        column-count: 2;
      }
    }

    @media (min-width: 1201px) {
      .catalog-list {
        column-count: 3;
      }
    }

    @media (max-width: 768px) {
      .catalog-container {
        padding: 0.5rem;
      }

      .catalog-controls {
        flex-direction: column;
        align-items: center;
      }

      .catalog-list {
        column-count: 1;
      }

      .catalog-monsters {
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
          <search-bar
            placeholder="Search for monsters..."
            mode="event"
            analytics-surface="catalog"
            @search-query="${this.handleSearchQuery}">
          </search-bar>
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
            ${group.monsters.map(monster => this.renderMonster({ ...monster, url: `${group.url}#${monster.key}` }))}
          </div>
        </div>
      `)}
    `;
  }

  private renderMonster(monster: { key: string; url: string, name: string; cr: number | string }) {
    const crDisplay = typeof monster.cr === 'number' ?
      (monster.cr === 0.125 ? 'CR ⅛' :
        monster.cr === 0.25 ? 'CR ¼' :
          monster.cr === 0.5 ? 'CR ½' :
            `CR ${monster.cr}`) :
      monster.cr;

    return html`
      <div class="catalog-monster">
        <a
          href="${monster.url}"
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

  private handleSearchQuery(e: CustomEvent) {
    const { query } = e.detail;

    // Dispatch event to switch to search tab with the query
    const event = new CustomEvent('catalog-search', {
      detail: { query },
      bubbles: true,
      composed: true
    });
    this.dispatchEvent(event);
  }

  private handleGroupClick(e: Event, group: CatalogTemplate | CatalogFamily, type: 'template' | 'family') {
    // Track analytics for group click
    trackMonsterClick(
      group.key,
      type === 'template' ? 'template' : 'family',
      'catalog'
    );
  }

  private handleMonsterClick(e: Event, monsterKey: string) {
    // Track analytics for monster click
    trackMonsterClick(
      monsterKey,
      'monster',
      'catalog'
    );
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'monster-catalog': MonsterCatalog;
  }
}