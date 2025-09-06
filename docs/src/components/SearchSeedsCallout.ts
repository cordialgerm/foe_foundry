import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { adoptExternalCss } from '../utils/index.js';

interface SearchSeed {
  query: string;
  display_name: string;
  description: string;
}

@customElement('search-seeds-callout')
export class SearchSeedsCallout extends LitElement {

  @property({ type: String })
  title = 'Discover Monsters by Theme';

  @state()
  private seeds: SearchSeed[] = [];

  @state()
  private loading = true;

  static styles = css`
    :host {
      display: block;
    }

    .search-seeds-container {
      padding: 2.5rem;
      margin: 1.5rem;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .search-seeds-container h2 {
      color: var(--bs-dark);
      font-size: 1.5rem;
      margin-bottom: 1rem;
      font-weight: bold;
      text-align: center;
    }

    .search-seeds-container p {
      color: var(--bs-dark);
      margin-bottom: 1.5rem;
      font-size: 1rem;
      text-align: center;
    }

    .search-input-container {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 2rem;
      flex-wrap: wrap;
    }

    .search-input {
      flex: 1;
      min-width: 200px;
      padding: 0.75rem;
      border: 2px solid #ddd;
      border-radius: 6px;
      font-size: 1rem;
      transition: border-color 0.2s ease;
    }

    .search-input:focus {
      outline: none;
      border-color: var(--primary-color);
      box-shadow: 0 0 0 2px rgba(var(--primary-color-rgb), 0.2);
    }

    .search-button {
      background-color: var(--primary-color);
      color: white;
      border: none;
      border-radius: 6px;
      padding: 0.75rem 1.5rem;
      font-size: 1rem;
      cursor: pointer;
      transition: background-color 0.2s ease;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .search-button:hover {
      background-color: var(--primary-color-dark, #0056b3);
    }

    .search-button:active {
      transform: translateY(1px);
    }

    .seeds-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1rem;
      margin-top: 1.5rem;
    }

    .seed-card {
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 8px;
      padding: 1rem;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .seed-card:hover {
      background: rgba(255, 255, 255, 0.2);
      border-color: var(--primary-color);
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    .seed-name {
      font-weight: bold;
      margin-bottom: 0.5rem;
      color: var(--bs-dark);
    }

    .seed-description {
      font-size: 0.9rem;
      color: var(--bs-secondary);
      line-height: 1.4;
    }

    .loading {
      text-align: center;
      color: var(--bs-secondary);
      font-style: italic;
    }

    @media (max-width: 768px) {
      .search-input-container {
        flex-direction: column;
      }

      .seeds-grid {
        grid-template-columns: 1fr;
      }
    }
  `;

  async firstUpdated() {
    // Adopt the site CSS to ensure we get the Bootstrap classes and CSS variables
    await adoptExternalCss(this.shadowRoot!, '/css/site.css');
    
    // Load search seeds
    await this.loadSearchSeeds();
  }

  private async loadSearchSeeds() {
    try {
      const response = await fetch('/api/v1/search/seeds');
      if (response.ok) {
        this.seeds = await response.json();
      } else {
        console.error('Failed to load search seeds:', response.statusText);
      }
    } catch (error) {
      console.error('Error loading search seeds:', error);
    } finally {
      this.loading = false;
    }
  }

  private handleSearch() {
    const input = this.shadowRoot?.querySelector('.search-input') as HTMLInputElement;
    const query = input?.value?.trim();
    
    if (query) {
      // Navigate to codex with search query
      window.location.href = `/codex#search?query=${encodeURIComponent(query)}`;
    }
  }

  private handleSeedClick(seed: SearchSeed) {
    // Navigate to codex with the seed query
    window.location.href = `/codex#search?query=${encodeURIComponent(seed.query)}`;
  }

  private handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      event.preventDefault();
      this.handleSearch();
    }
  }

  render() {
    return html`
      <div class="search-seeds-container bg-object parchment">
        <h2>${this.title}</h2>
        <p>Discover monsters by theme, vibe, environment, or adventure hook - even when you don't know exactly what you're looking for!</p>
        
        <div class="search-input-container">
          <input 
            type="text" 
            class="search-input"
            placeholder="Search for monsters..." 
            @keydown="${this.handleKeyDown}"
          />
          <button 
            class="search-button"
            @click="${this.handleSearch}"
          >
            🔍 Search
          </button>
        </div>

        ${this.loading ? html`
          <div class="loading">Loading inspiration...</div>
        ` : html`
          <div class="seeds-grid">
            ${this.seeds.map(seed => html`
              <div 
                class="seed-card"
                @click="${() => this.handleSeedClick(seed)}"
                title="Click to search for ${seed.display_name}"
              >
                <div class="seed-name">${seed.display_name}</div>
                <div class="seed-description">${seed.description}</div>
              </div>
            `)}
          </div>
        `}
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'search-seeds-callout': SearchSeedsCallout;
  }
}