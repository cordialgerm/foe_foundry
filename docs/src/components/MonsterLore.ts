import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { ref, createRef } from 'lit/directives/ref.js';
import { initializeMonsterStore } from '../data/api';
import { MonsterStore } from '../data/monster';
import { Task } from '@lit/task';

@customElement('monster-lore')
export class MonsterLore extends LitElement {
  @property({ type: String, attribute: 'monster-key' })
  monsterKey = '';

  @property({ type: Object })
  monsterStore?: MonsterStore;

  private loreRef = createRef<HTMLDivElement>();

  private loreTask = new Task(this, {
    task: async ([monsterKey], { signal }) => {
      const store = this.monsterStore || initializeMonsterStore();
      return await store.getMonster(monsterKey);
    },
    args: () => [this.monsterKey]
  });

  static styles = css`
    :host {
      display: block;
    }

    .lore-content {
      padding-left: 8px;
      padding-right: 8px;
      font-size: 0.82rem;
      text-align: justify;
      max-height: calc(80px + var(--max-text-content-height, 700px));
      overflow: hidden;
      position: relative;
    }

    .lore-content p {
      margin-top: 0.25rem;
      margin-bottom: 0.25rem;
      text-align: justify;
    }

    .lore-content ul,
    .lore-content ol {
      padding-left: 0.8rem;
      margin-top: 0.25rem;
      margin-bottom: 0.25rem;
    }

    .lore-content h2,
    .lore-content h3 {
      font-size: 1.05rem;
      margin-top: 0px;
      margin-bottom: 0px;
    }

    .lore-content .headerlink {
      display: none;
    }

    .lore-content a {
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

    .content-body::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 40px;
      background: linear-gradient(transparent, var(--bs-dark));
      pointer-events: none;
    }

    .content-body[data-overflowing="true"]::after {
      content: '...';
      position: absolute;
      bottom: 5px;
      right: 10px;
      height: auto;
      background: var(--bs-dark);
      color: var(--tertiary-color);
      font-size: 1.2rem;
      font-weight: bold;
      padding: 2px 4px;
      border-radius: 2px;
    }
  `;

  updated() {
    super.updated();
    
    // Handle lore content
    if (this.loreRef.value && this.loreTask.value?.overviewElement) {
      // Only append if not already present
      if (!this.loreRef.value.querySelector('[data-monster-lore]')) {
        const clonedElement = this.loreTask.value.overviewElement.cloneNode(true) as HTMLElement;
        clonedElement.setAttribute('data-monster-lore', 'true');
        this.loreRef.value.appendChild(clonedElement);

        // Check if content overflows
        this.checkContentOverflow(this.loreRef.value.closest('.content-body') as HTMLElement);
      }
    }
  }

  private checkContentOverflow(contentBody: HTMLElement | null) {
    if (!contentBody) return;

    // Use requestAnimationFrame to ensure DOM is updated
    requestAnimationFrame(() => {
      const isOverflowing = contentBody.scrollHeight > contentBody.clientHeight;
      contentBody.setAttribute('data-overflowing', isOverflowing.toString());
    });
  }

  render() {
    return this.loreTask.render({
      pending: () => html`<p>Loading lore...</p>`,
      complete: (monster) => html`
        <div class="lore-content">
          <div class="content-header">
            <h3>Lore</h3>
            ${monster?.monsterTemplate ? html`
              <a href="/monsters/${monster.monsterTemplate}/" class="full-content-link">See Full Lore</a>
            ` : ''}
          </div>
          <div class="content-body">
            <div ${ref(this.loreRef)}>
              ${!monster?.overviewElement ? html`<p>No lore available for this monster.</p>` : ''}
            </div>
          </div>
        </div>
      `,
      error: (e) => html`<p>Error loading lore: ${e}</p>`
    });
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'monster-lore': MonsterLore;
  }
}