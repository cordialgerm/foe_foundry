import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { trackSearch } from '../utils/analytics.js';
import { MonsterSearchApi } from '../data/searchApi.js';
import { SearchSeed } from '../data/search.js';
import './SvgIcon.js';

export type SearchBarMode = 'navigation' | 'event';

@customElement('search-bar')
export class SearchBar extends LitElement {
  @property() placeholder: string = 'Search for monsters...';
  @property() mode: SearchBarMode = 'event';
  @property({ attribute: 'analytics-surface' }) analyticsSurface: string = 'search';
  @property({ attribute: 'button-text' }) buttonText: string = 'Search';
  @property({ attribute: 'initial-value' }) initialValue: string = '';
  @property({ type: Number }) seeds: number = 0;

  @state() private searchValue: string = '';
  @state() private searchSeeds: SearchSeed[] = [];
  @state() private selectedSeeds: SearchSeed[] = [];

  private searchApi = new MonsterSearchApi();

  static styles = css`
    :host {
      display: block;
      width: 100%;
    }

    .search-section {
      max-width: 800px;
      margin: 0 auto;
      padding: 0 1rem;
    }

    .search-input-container {
      display: flex;
      gap: 0.5rem;
      align-items: stretch;
    }

    .search-input {
      flex: 1;
      padding: 0.75rem 1rem;
      border: 2px solid var(--fg-color);
      border-radius: 8px;
      background: var(--muted-color);
      color: var(--fg-color);
      font-size: 1rem;
      font-family: var(--primary-font);
      transition: all 0.3s ease;
    }

    .search-input:focus {
      outline: none;
      border-color: var(--tertiary-color);
      box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.2);
    }

    .search-input::placeholder {
      color: var(--fg-color);
    }

    .search-button {
      padding: 0.75rem 1.5rem;
      background: var(--tertiary-color);
      color: var(--fg-color);
      border: none;
      border-radius: 8px;
      font-family: var(--primary-font);
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      min-width: fit-content;
      white-space: nowrap;
    }

    .search-button:hover {
      background: var(--primary-color);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
    }

    .search-icon {
      font-size: 1rem;
      width: 1rem;
      height: 1rem;
    }

    .search-seeds {
      margin-top: 1rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      justify-content: center;
    }

    .search-seed-button {
      background: transparent;
      border: 1px solid var(--fg-color);
      border-radius: 20px;
      padding: 0.5rem 1rem;
      font-size: 0.85rem;
      cursor: pointer;
      transition: all 0.2s ease;
      color: var(--fg-color);
      font-family: var(--primary-font);
      font-weight: 500;
      text-align: center;
    }

    .search-seed-button:hover {
      background: var(--tertiary-color, #c29a5b);
      transform: translateY(-1px);
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    .search-seed-button:active {
      transform: translateY(0);
    }

    /* Responsive design */
    @media (max-width: 768px) {
      .search-section {
        padding: 0 0.5rem;
      }

      .search-input-container {
        gap: 0.75rem;
      }

      .search-input {
        padding: 0.875rem 1rem;
        font-size: 1rem;
      }

      .search-button {
        padding: 0.875rem 1.25rem;
        font-size: 1rem;
        justify-content: center;
      }
    }

    @media (max-width: 480px) {
      .search-section {
        padding: 0 0.25rem;
      }

      .search-input-container {
        gap: 0.5rem; /* Keep horizontal layout but reduce gap */
      }

      .search-input {
        padding: 0.875rem 1rem;
        font-size: 1rem;
        min-width: 0; /* Allow the input to shrink properly */
      }

      .search-button {
        padding: 0.875rem 1rem;
        font-size: 1rem;
        flex-shrink: 0; /* Prevent button from shrinking */
      }

      .search-seeds {
        margin-top: 1.25rem;
        gap: 0.75rem;
      }

      .search-seed-button {
        padding: 0.75rem 1.25rem;
        font-size: 0.9rem;
      }
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    if (this.initialValue) {
      this.searchValue = this.initialValue;
    }
    if (this.seeds > 0) {
      this.loadSearchSeeds();
    }
  }

  private async loadSearchSeeds(): Promise<void> {
    try {
      const seeds = await this.searchApi.getSearchSeeds();
      this.searchSeeds = seeds;
      this.selectRandomSeeds();
    } catch (error) {
      console.error('Failed to load search seeds:', error);
      this.searchSeeds = [];
    }
  }

  private selectRandomSeeds(): void {
    if (this.searchSeeds.length === 0 || this.seeds <= 0) return;

    // Shuffle and take first N seeds
    const shuffled = [...this.searchSeeds].sort(() => Math.random() - 0.5);
    this.selectedSeeds = shuffled.slice(0, this.seeds);
  }

  render() {
    return html`
      <div class="search-section">
        <div class="search-input-container">
          <input
            type="text"
            class="search-input"
            placeholder="${this.placeholder}"
            .value="${this.searchValue}"
            @input="${this.handleInput}"
            @keydown="${this.handleKeydown}"
          />
          <button class="search-button" @click="${this.handleSearchClick}">
            <svg-icon src="magnifying-glass" class="search-icon"></svg-icon>
            ${this.buttonText}
          </button>
        </div>
        ${this.seeds > 0 && this.selectedSeeds.length > 0 ? html`
          <div class="search-seeds">
            ${this.selectedSeeds.map(seed => html`
              <button
                class="search-seed-button"
                @click=${() => this.handleSeedClick(seed.term)}
                title="${seed.description}"
              >
                ${seed.term}
              </button>
            `)}
          </div>
        ` : ''}
      </div>
    `;
  }

  private handleSeedClick(seedTerm: string) {
    // Set the search value and trigger search
    this.searchValue = seedTerm;
    this.performSearch();
  }

  private handleInput(e: Event) {
    const input = e.target as HTMLInputElement;
    this.searchValue = input.value;
  }

  private handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      e.preventDefault();
      this.performSearch();
    }
  }

  private handleSearchClick() {
    this.performSearch();
  }

  private performSearch() {
    const query = this.searchValue.trim();

    if (!query) {
      return;
    }

    // Track search analytics
    trackSearch(query, 0, this.analyticsSurface);

    if (this.mode === 'navigation') {
      // Navigation mode: switch to search tab (for codex browse tab)
      this.dispatchEvent(new CustomEvent('search-navigate', {
        detail: { query },
        bubbles: true,
        composed: true
      }));
    } else {
      // Event mode: dispatch search event (for catalog and other components)
      this.dispatchEvent(new CustomEvent('search-query', {
        detail: { query },
        bubbles: true,
        composed: true
      }));
    }
  }

  /**
   * Public method to set the search value programmatically
   */
  public setSearchValue(value: string) {
    this.searchValue = value;
  }

  /**
   * Public method to get the current search value
   */
  public getSearchValue(): string {
    return this.searchValue;
  }

  /**
   * Public method to clear the search
   */
  public clearSearch() {
    this.searchValue = '';
  }

  /**
   * Public method to focus the search input
   */
  public focusInput() {
    const input = this.shadowRoot?.querySelector('.search-input') as HTMLInputElement;
    input?.focus();
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'search-bar': SearchBar;
  }
}
