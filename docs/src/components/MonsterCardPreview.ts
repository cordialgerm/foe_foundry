import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { Monster } from '../data/monster.js';
import { ApiMonsterStore } from '../data/api.js';
import './MonsterArt.js';

@customElement('monster-card-preview')
export class MonsterCardPreview extends LitElement {
  @property({ attribute: 'monster-key' }) monsterKey?: string;
  @property({ type: Boolean }) compact = false; // For desktop list rows
  @property({ type: Boolean }) selected = false;

  @state() private monster?: Monster;
  @state() private loading = false;
  @state() private error = false;

  private apiStore = new ApiMonsterStore();

  static styles = css`
    :host {
      display: block;
      cursor: pointer;
      transition: all 0.2s ease;
      border-radius: var(--medium-margin);
      overflow: hidden;
    }

    :host(.selected) {
      outline: 2px solid var(--tertiary-color);
      outline-offset: 2px;
    }

    .preview-card {
      position: relative;
      border-radius: var(--medium-margin);
      overflow: hidden;
    }

    .preview-card.compact {
      height: 60px; /* For desktop list rows */
    }

    .preview-card.full {
      height: 100%;
      min-height: 400px;
    }

    .preview-card.compact monster-art {
      height: 60px;
    }

    .preview-card.full monster-art {
      height: 100%;
      min-height: 400px;
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
    }

    .monster-overlay {
      position: absolute;
      inset: 0;
      background: linear-gradient(transparent 40%, rgba(0,0,0,0.8));
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding: 1rem;
    }

    .description {
      color: rgba(255,255,255,0.85);
      font-size: 0.85rem;
      margin-top: 0.5rem;
      line-height: 1.4;
      text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }

    .description.compact {
      display: none; /* Hide description in compact mode */
    }

    .action-buttons {
      display: flex;
      gap: 0.5rem;
      margin-top: 1rem;
    }

    .action-buttons.compact {
      display: none; /* Hide buttons in compact mode */
    }

    .action-btn {
      background: var(--primary-color);
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.8rem;
      font-weight: 500;
      transition: all 0.2s ease;
      pointer-events: auto;
    }

    .action-btn:hover {
      background: var(--primary-muted-color);
      transform: translateY(-1px);
    }

    .action-btn.secondary {
      background: rgba(128, 128, 128, 0.8);
      backdrop-filter: blur(4px);
    }

    .action-btn.secondary:hover {
      background: rgba(160, 160, 160, 0.9);
    }
  `;

  async connectedCallback() {
    super.connectedCallback();
    await this.loadMonster();
  }

  async updated(changedProperties: Map<string, any>) {
    if (changedProperties.has('monsterKey')) {
      await this.loadMonster();
    }
  }

  private async loadMonster() {
    if (!this.monsterKey) {
      this.monster = undefined;
      return;
    }

    this.loading = true;
    this.error = false;

    try {
      const loadedMonster = await this.apiStore.getMonster(this.monsterKey);
      this.monster = loadedMonster || undefined;
      if (!loadedMonster) {
        this.error = true;
      }
    } catch (err) {
      console.error('Failed to load monster:', err);
      this.error = true;
      this.monster = undefined;
    } finally {
      this.loading = false;
    }
  }

  render() {
    if (this.loading) {
      return html`
        <div class="preview-card ${this.compact ? 'compact' : 'full'}">
          <div class="monster-overlay">
            <div class="monster-name">Loading...</div>
          </div>
        </div>
      `;
    }

    if (this.error || !this.monster) {
      return html`
        <div class="preview-card ${this.compact ? 'compact' : 'full'}">
          <div class="monster-overlay">
            <div class="monster-name">Failed to load monster</div>
          </div>
        </div>
      `;
    }

    const families = this.monster.monsterFamilies || [];
    const environments = this.getEnvironments();

    return html`
      <div class="preview-card ${this.compact ? 'compact' : 'full'}">
        <monster-art
          monster-image="${String(this.monster.image || '')}"
          background-image="${String(this.monster.backgroundImage || '')}"
          background-color="rgba(255, 255, 255, 0.55)"
          image-mode="${this.compact ? 'contain' : 'cover'}"
        ></monster-art>

        <div class="monster-overlay ${this.compact ? 'compact' : ''}">
          <div class="monster-name ${this.compact ? 'compact' : ''}">${this.monster.name}</div>
          <div class="monster-details ${this.compact ? 'compact' : ''}">
            ${this.monster.cr} | ${this.monster.creatureType}
          </div>

          ${this.compact ? html`` : html`
            <div class="monster-tags">
              ${families.map(family => html`<span class="tag family">${family}</span>`)}
              <span class="tag type">${this.monster.creatureType}</span>
              ${environments.map(env => html`<span class="tag environment">${env}</span>`)}
            </div>

            ${this.monster.tagLine ? html`<div class="description">${this.monster.tagLine}</div>` : html``}

            <div class="action-buttons">
              <button class="action-btn" @click=${this.handleForgeClick}>Forge</button>
              <button class="action-btn secondary" @click=${this.handleShareClick}>Share</button>
            </div>
          `}
        </div>
      </div>
    `;
  }

  private getEnvironments(): string[] {
    // For now, return empty array since the existing Monster interface doesn't have environments
    // This could be enhanced when the API provides environment data
    return [];
  }

  private handleForgeClick(e: Event) {
    e.stopPropagation();
    // Navigate to forge page with this monster
    window.location.href = `/generate/?monster-key=${this.monster?.key}`;
  }

  private handleShareClick(e: Event) {
    e.stopPropagation();
    // Copy monster URL to clipboard
    const url = `${window.location.origin}/monsters/${this.monster?.monsterTemplate}/`;
    navigator.clipboard.writeText(url).then(() => {
      // Could dispatch a toast notification event here
      console.log('Monster URL copied to clipboard');
    });
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'monster-card-preview': MonsterCardPreview;
  }
}
