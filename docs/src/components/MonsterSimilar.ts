import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { initializeMonsterStore } from '../data/api';
import { MonsterStore } from '../data/monster';
import { Task } from '@lit/task';

@customElement('monster-similar')
export class MonsterSimilar extends LitElement {
  @property({ type: String, attribute: 'monster-key' })
  monsterKey = '';

  @property({ type: Object })
  monsterStore?: MonsterStore;

  private similarTask = new Task(this, {
    task: async ([monsterKey], { signal }) => {
      const store = this.monsterStore || initializeMonsterStore();
      return await store.getSimilarMonsters(monsterKey);
    },
    args: () => [this.monsterKey]
  });

  static styles = css`
    :host {
      display: block;
    }

    .similar-content {
      padding-left: 8px;
      padding-right: 8px;
      font-size: 0.82rem;
      text-align: justify;
    }

    .similar-content ul {
      padding-left: 0.8rem;
      margin-top: 0.25rem;
      margin-bottom: 0.25rem;
    }

    .similar-content p {
      margin-top: 0.25rem;
      margin-bottom: 0.25rem;
      text-align: justify;
    }

    .similar-content a {
      color: var(--fg-color);
      text-decoration: underline;
    }

    .content-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid var(--tertiary-color);
    }

    .content-header h3 {
      margin: 0;
      font-size: 1.1rem;
      color: var(--tertiary-color);
    }

    .full-content-link {
      color: var(--tertiary-color);
      text-decoration: none;
      font-size: 0.9rem;
      font-weight: 500;
      transition: color 0.2s ease;
    }

    .full-content-link:hover {
      color: var(--fg-color);
      text-decoration: underline;
    }

    .content-body {
      max-height: var(--max-text-content-height, 700px);
      overflow: hidden;
      position: relative;
    }
  `;

  render() {
    return this.similarTask.render({
      pending: () => html`<p>Loading similar monsters...</p>`,
      complete: (similarMonsters) => html`
        <div class="similar-content">
          <div class="content-header">
            <h3>Similar Monsters</h3>
            ${this.monsterKey ? html`
              <a href="/monsters/${this.getMonsterTemplate()}/" class="full-content-link">See Full Monster</a>
            ` : ''}
          </div>
          <div class="content-body">
            <ul>
              ${similarMonsters.map(
                group => html`
                  <li>
                    <strong>${group.name}</strong>
                    <ul>
                      ${group.monsters.map(
                        monster => html`
                          <li>
                            <a href="/generate/?monster-key=${monster.key}">${monster.name} (${monster.cr})</a>
                          </li>
                        `
                      )}
                    </ul>
                  </li>
                `
              )}
            </ul>
          </div>
        </div>
      `,
      error: (e) => html`<p>Error loading similar monsters: ${e}</p>`
    });
  }

  private getMonsterTemplate(): string {
    // Extract monster template from key or use key itself
    // This might need adjustment based on how monster keys map to templates
    return this.monsterKey;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'monster-similar': MonsterSimilar;
  }
}