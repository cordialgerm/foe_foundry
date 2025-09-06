import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { Task } from '@lit/task';

interface MonsterSearchResult {
  key: string;
  name: string;
  cr: number;
  template: string;
}

@customElement('monster-codex')
export class MonsterCodex extends LitElement {
  @property({ type: String })
  query = '';

  @property({ type: Number })
  limit = 20;

  private searchTask = new Task(this, {
    task: async ([query, limit], { signal }) => {
      if (!query || query.trim() === '') {
        return [];
      }
      return this.performSearch(query.trim(), limit);
    },
    args: () => [this.query, this.limit]
  });

  static styles = css`
    :host {
      display: block;
      width: 100%;
    }

    .loading {
      text-align: center;
      padding: 2rem;
      color: var(--bs-text-muted);
    }

    .error {
      text-align: center;
      padding: 2rem;
      color: var(--bs-danger);
    }

    .no-results {
      text-align: center;
      padding: 2rem;
      color: var(--bs-text-muted);
    }

    .search-results {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1rem;
      padding: 1rem 0;
    }

    .monster-result {
      background: var(--bs-dark);
      border: 2px solid var(--border-color);
      border-radius: 0.5rem;
      padding: 1rem;
      cursor: pointer;
      transition: all 0.3s ease;
      color: var(--bs-light);
    }

    .monster-result:hover {
      border-color: var(--primary-color);
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }

    .monster-name {
      font-size: 1.2rem;
      font-weight: bold;
      color: var(--primary-color);
      margin-bottom: 0.5rem;
    }

    .monster-details {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.9rem;
      color: var(--bs-text-muted);
    }

    .monster-cr {
      font-weight: bold;
      color: var(--tertiary-color);
    }

    .monster-template {
      font-style: italic;
    }

    @media (max-width: 768px) {
      .search-results {
        grid-template-columns: 1fr;
      }
    }
  `;

  private async performSearch(query: string, limit: number): Promise<MonsterSearchResult[]> {
    try {
      const response = await fetch(`/api/v1/search/monsters?query=${encodeURIComponent(query)}&limit=${limit}`);
      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error performing search:', error);
      throw error;
    }
  }

  private handleMonsterClick(monster: MonsterSearchResult) {
    // Navigate to the monster page
    const url = `/monsters/${monster.template}/${monster.key}/`;
    window.location.href = url;
  }

  private formatCR(cr: number): string {
    if (cr < 1) {
      if (cr === 0.5) return '1/2';
      if (cr === 0.25) return '1/4';
      if (cr === 0.125) return '1/8';
      return cr.toString();
    }
    return cr.toString();
  }

  render() {
    return this.searchTask.render({
      pending: () => html`<div class="loading">Searching monsters...</div>`,
      complete: (results) => {
        if (!this.query || this.query.trim() === '') {
          return html`<div class="no-results">Enter a search query to find monsters.</div>`;
        }

        if (results.length === 0) {
          return html`<div class="no-results">No monsters found for "${this.query}".</div>`;
        }

        return html`
          <div class="search-results">
            ${results.map(monster => html`
              <div class="monster-result" @click=${() => this.handleMonsterClick(monster)}>
                <div class="monster-name">${monster.name}</div>
                <div class="monster-details">
                  <span class="monster-template">${monster.template}</span>
                  <span class="monster-cr">CR ${this.formatCR(monster.cr)}</span>
                </div>
              </div>
            `)}
          </div>
        `;
      },
      error: (e) => html`<div class="error">Error searching monsters: ${e.message}</div>`
    });
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'monster-codex': MonsterCodex;
  }
}