import { LitElement, html, css } from 'lit';
import { customElement, state, property } from 'lit/decorators.js';
import { SearchSeed } from '../data/search.js';
import { MonsterSearchApi } from '../data/searchApi.js';
import { Task } from '@lit/task';

@customElement('monster-search-seeds')
export class MonsterSearchSeeds extends LitElement {
  @property({ type: Number }) maxSeeds?: number;
  @state() private selectedSeed: string | null = null;

  private searchApi = new MonsterSearchApi();

  private seedsTask = new Task(this, async () => {
    const allSeeds = await this.searchApi.getSearchSeeds();
    
    // If maxSeeds is specified, return random selection
    if (this.maxSeeds && this.maxSeeds < allSeeds.length) {
      const shuffled = [...allSeeds].sort(() => Math.random() - 0.5);
      return shuffled.slice(0, this.maxSeeds);
    }
    
    return allSeeds;
  }, () => [this.maxSeeds]);

  static styles = css`
    :host {
      display: block;
      margin-bottom: 1rem;
    }

    .seeds-container {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 1rem;
    }

    .seed-button {
      background: var(--color-surface-variant, #f5f5f5);
      border: 1px solid var(--color-outline, #ccc);
      border-radius: 16px;
      padding: 0.5rem 1rem;
      font-size: 0.875rem;
      cursor: pointer;
      transition: all 0.2s ease;
      text-decoration: none;
      color: var(--color-on-surface, #333);
    }

    .seed-button:hover {
      background: var(--color-primary-container, #e8f5e8);
      border-color: var(--color-primary, #4CAF50);
      transform: translateY(-1px);
    }

    .seed-button.selected {
      background: var(--color-primary, #4CAF50);
      color: var(--color-on-primary, white);
      border-color: var(--color-primary, #4CAF50);
    }

    .loading {
      text-align: center;
      padding: 1rem;
      color: var(--color-on-surface-variant, #666);
    }

    .error {
      text-align: center;
      padding: 1rem;
      color: var(--color-error, #d32f2f);
    }

    @media (max-width: 768px) {
      .seeds-container {
        gap: 0.25rem;
      }
      
      .seed-button {
        font-size: 0.75rem;
        padding: 0.375rem 0.75rem;
      }
    }
  `;

  render() {
    return this.seedsTask.render({
      pending: () => html`<div class="loading">Loading search suggestions...</div>`,
      complete: (seeds: SearchSeed[]) => html`
        <div class="seeds-container">
          ${seeds.map(seed => html`
            <button 
              class="seed-button ${this.selectedSeed === seed.term ? 'selected' : ''}"
              @click=${() => this.handleSeedClick(seed.term)}
              title="${seed.description}"
            >
              ${seed.term}
            </button>
          `)}
        </div>
      `,
      error: (error) => html`<div class="error">Failed to load search suggestions: ${error}</div>`
    });
  }

  private handleSeedClick(term: string) {
    this.selectedSeed = this.selectedSeed === term ? null : term;
    
    // Dispatch event to notify parent components
    this.dispatchEvent(new CustomEvent('seed-selected', {
      detail: { term: this.selectedSeed },
      bubbles: true,
      composed: true
    }));
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'monster-search-seeds': MonsterSearchSeeds;
  }
}