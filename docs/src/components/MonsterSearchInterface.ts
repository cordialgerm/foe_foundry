import { LitElement, html, css } from 'lit';
import { customElement, state, property } from 'lit/decorators.js';
import { MonsterInfo, MonsterSearchRequest } from '../data/search.js';
import { MonsterSearchApi } from '../data/searchApi.js';
import './MonsterCard.js';
import { Task } from '@lit/task';

@customElement('monster-search-interface')
export class MonsterSearchInterface extends LitElement {
  @property() initialQuery = '';
  @state() private query = '';
  @state() private results: MonsterInfo[] = [];
  @state() private isSearching = false;

  private searchApi = new MonsterSearchApi();
  private debounceTimer: number | undefined;

  static styles = css`
    :host {
      display: block;
      margin: 1rem 0;
    }

    .search-container {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .search-bar {
      display: flex;
      gap: 0.5rem;
      align-items: center;
    }

    .search-input {
      flex: 1;
      padding: 0.75rem 1rem;
      border: 2px solid var(--color-outline, #ccc);
      border-radius: 8px;
      font-size: 1rem;
      transition: border-color 0.2s ease;
    }

    .search-input:focus {
      outline: none;
      border-color: var(--color-primary, #4CAF50);
    }

    .search-button {
      background: var(--color-primary, #4CAF50);
      color: var(--color-on-primary, white);
      border: none;
      border-radius: 8px;
      padding: 0.75rem 1.5rem;
      font-size: 1rem;
      cursor: pointer;
      transition: background-color 0.2s ease;
      white-space: nowrap;
    }

    /* Mobile: Icon-only search button to fit on same line */
    @media (max-width: 768px) {
      .search-button {
        padding: 0.75rem;
        min-width: 44px; /* Touch-friendly minimum size */
      }

      .search-button .button-text {
        display: none; /* Hide text on mobile */
      }

      .search-button::before {
        content: "🔍"; /* Search icon */
        font-size: 1.2rem;
      }
    }

    .search-button:hover {
      background: var(--color-primary-dark, #45a049);
    }

    .search-button:disabled {
      background: var(--color-surface-variant, #f5f5f5);
      color: var(--color-on-surface-variant, #666);
      cursor: not-allowed;
    }

    .results-container {
      margin-top: 1rem;
    }

    .results-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1rem;
      margin-top: 1rem;
    }

    .loading {
      text-align: center;
      padding: 2rem;
      color: var(--color-on-surface-variant, #666);
    }

    .no-results {
      text-align: center;
      padding: 2rem;
      color: var(--color-on-surface-variant, #666);
    }

    .error {
      text-align: center;
      padding: 2rem;
      color: var(--color-error, #d32f2f);
    }

    .results-count {
      margin: 1rem 0 0.5rem 0;
      font-size: 0.875rem;
      color: var(--color-on-surface-variant, #666);
    }

    @media (max-width: 768px) {
      .search-bar {
        flex-direction: row; /* Keep search bar horizontal on mobile */
        gap: 0.5rem;
      }

      .search-button {
        flex-shrink: 0; /* Prevent button from shrinking */
      }

      .results-grid {
        grid-template-columns: 1fr;
      }
    }
  `;

  connectedCallback() {
    super.connectedCallback();

    // Listen for search seed selections
    this.addEventListener('seed-selected', this.handleSeedSelected as EventListener);

    if (this.initialQuery) {
      this.query = this.initialQuery;
      this.performSearch();
    }
  }

  render() {
    return html`
      <div class="search-container">
        <div class="search-bar">
          <input
            type="text"
            class="search-input"
            placeholder="Search for monsters by theme, environment, or type..."
            .value=${this.query}
            @input=${this.handleInput}
            @keydown=${this.handleKeydown}
          />
          <button
            class="search-button"
            @click=${this.performSearch}
            ?disabled=${this.isSearching}
          >
            <span class="button-text">${this.isSearching ? 'Searching...' : 'Search'}</span>
          </button>
        </div>

        ${this.renderResults()}
      </div>
    `;
  }

  private renderResults() {
    if (!this.query && this.results.length === 0) {
      return html``;
    }

    if (this.isSearching) {
      return html`<div class="loading">Searching for monsters...</div>`;
    }

    if (this.results.length === 0 && this.query) {
      return html`
        <div class="no-results">
          No monsters found for "${this.query}". Try a different search term or browse our
          <a href="/monsters/">monster catalog</a>.
        </div>
      `;
    }

    if (this.results.length > 0) {
      return html`
        <div class="results-container">
          <div class="results-count">
            Found ${this.results.length} monster${this.results.length !== 1 ? 's' : ''}
            ${this.query ? `for "${this.query}"` : ''}
          </div>
          <div class="results-grid">
            ${this.results.map(monster => html`
              <monster-card
                .monster=${monster}
                .showActions=${true}
              ></monster-card>
            `)}
          </div>
        </div>
      `;
    }

    return html``;
  }

  private handleInput(e: Event) {
    const target = e.target as HTMLInputElement;
    this.query = target.value;

    // Debounced search
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }

    this.debounceTimer = setTimeout(() => {
      if (this.query.length >= 2) {
        this.performSearch();
      } else if (this.query.length === 0) {
        this.results = [];
      }
    }, 500) as unknown as number;
  }

  private handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      this.performSearch();
    }
  }

  private handleSeedSelected(e: CustomEvent) {
    const term = e.detail.term;
    if (term) {
      this.query = term;
      this.performSearch();
    } else {
      this.query = '';
      this.results = [];
    }
  }

  private async performSearch() {
    if (!this.query.trim()) {
      this.results = [];
      return;
    }

    this.isSearching = true;

    try {
      const searchRequest: MonsterSearchRequest = {
        query: this.query,
        limit: 12 // Limit for homepage display
      };

      const result = await this.searchApi.searchMonsters(searchRequest);
      this.results = result.monsters;
    } catch (error) {
      console.error('Search failed:', error);
      this.results = [];
    } finally {
      this.isSearching = false;
    }
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'monster-search-interface': MonsterSearchInterface;
  }
}