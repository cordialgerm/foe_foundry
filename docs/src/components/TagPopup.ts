import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { TagInfo, TagApi } from '../data/tags.js';

@customElement('tag-popup')
export class TagPopup extends LitElement {
  @property() tagName = '';
  @property({ type: Boolean, reflect: true }) open = false;

  @state() private tagInfo: TagInfo | null = null;
  @state() private loading = false;
  @state() private error: string | null = null;

  private tagApi = new TagApi();

  static styles = css`
    :host {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.8);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.3s ease, visibility 0.3s ease;
    }

    :host([open]) {
      opacity: 1;
      visibility: visible;
    }

    .popup-content {
      background: var(--bg-color);
      border: 2px solid var(--border-color);
      border-radius: 12px;
      padding: 2rem;
      max-width: 600px;
      width: 90%;
      max-height: 80vh;
      overflow-y: auto;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
      transform: scale(0.9);
      transition: transform 0.3s ease;
    }

    :host([open]) .popup-content {
      transform: scale(1);
    }

    .popup-header {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.5rem;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 1rem;
    }

    .tag-icon {
      width: 3rem;
      height: 3rem;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .tag-icon svg-icon {
      width: 2rem;
      height: 2rem;
      fill: white;
    }

    .tag-title {
      flex: 1;
    }

    .tag-name {
      font-size: 1.5rem;
      font-weight: bold;
      margin: 0;
      text-transform: capitalize;
    }

    .tag-category {
      font-size: 0.9rem;
      opacity: 0.7;
      margin: 0.25rem 0 0 0;
      text-transform: capitalize;
    }

    .close-btn {
      background: none;
      border: none;
      color: var(--fg-color);
      font-size: 2rem;
      cursor: pointer;
      padding: 0;
      width: 2rem;
      height: 2rem;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      transition: background-color 0.2s ease;
    }

    .close-btn:hover {
      background-color: rgba(255, 255, 255, 0.1);
    }

    .tag-description {
      font-size: 1.1rem;
      line-height: 1.6;
      margin-bottom: 2rem;
      opacity: 0.9;
    }

    .examples-section h3 {
      font-size: 1.2rem;
      margin: 0 0 1rem 0;
      color: var(--tertiary-color);
    }

    .example-monsters {
      display: grid;
      gap: 1rem;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    }

    .monster-card {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1rem;
      text-decoration: none;
      color: inherit;
      transition: all 0.2s ease;
    }

    .monster-card:hover {
      background: rgba(255, 255, 255, 0.1);
      border-color: var(--tertiary-color);
      transform: translateY(-2px);
    }

    .monster-name {
      font-weight: bold;
      font-size: 1rem;
      margin-bottom: 0.5rem;
    }

    .monster-details {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.9rem;
      opacity: 0.8;
      margin-bottom: 0.5rem;
    }

    .monster-tagline {
      font-style: italic;
      font-size: 0.85rem;
      opacity: 0.7;
      line-height: 1.4;
    }

    .loading {
      text-align: center;
      padding: 2rem;
      font-size: 1.1rem;
    }

    .error {
      color: #ef4444;
      text-align: center;
      padding: 1rem;
      background: rgba(239, 68, 68, 0.1);
      border-radius: 8px;
      margin-bottom: 1rem;
    }

    .no-examples {
      text-align: center;
      opacity: 0.7;
      font-style: italic;
      padding: 1rem;
    }
  `;

  protected updated(changedProperties: Map<string, any>) {
    if (changedProperties.has('tagName') && this.tagName) {
      this.loadTagInfo();
    }
  }

  private async loadTagInfo() {
    if (!this.tagName) return;

    this.loading = true;
    this.error = null;

    try {
      this.tagInfo = await this.tagApi.getTag(this.tagName);
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Failed to load tag information';
    } finally {
      this.loading = false;
    }
  }

  private close() {
    this.open = false;
    this.dispatchEvent(new CustomEvent('tag-popup-close'));
  }

  private handleBackdropClick(e: Event) {
    if (e.target === this) {
      this.close();
    }
  }

  render() {
    return html`
      <div class="popup-content" @click=${(e: Event) => e.stopPropagation()}>
        ${this.loading ? html`
          <div class="loading">Loading tag information...</div>
        ` : this.error ? html`
          <div class="error">${this.error}</div>
          <button class="close-btn" @click=${this.close} title="Close">&times;</button>
        ` : this.tagInfo ? html`
          <div class="popup-header">
            <div class="tag-icon" style="background-color: ${this.tagInfo.color}">
              <svg-icon src="${this.tagInfo.icon.replace('.svg', '')}"></svg-icon>
            </div>
            <div class="tag-title">
              <h2 class="tag-name">${this.tagInfo.name}</h2>
              <p class="tag-category">${this.tagInfo.category.replace('_', ' ')}</p>
            </div>
            <button class="close-btn" @click=${this.close} title="Close">&times;</button>
          </div>

          <div class="tag-description">
            ${this.tagInfo.description}
          </div>

          <div class="examples-section">
            <h3>Example Monsters</h3>
            ${this.tagInfo.example_monsters.length > 0 ? html`
              <div class="example-monsters">
                ${this.tagInfo.example_monsters.map(monster => html`
                  <a href="/monsters/${monster.template}/" class="monster-card">
                    <div class="monster-name">${monster.name}</div>
                    <div class="monster-details">
                      <span>CR ${monster.cr}</span>
                      ${monster.creature_type ? html`<span>• ${monster.creature_type}</span>` : ''}
                    </div>
                    ${monster.tag_line ? html`
                      <div class="monster-tagline">${monster.tag_line}</div>
                    ` : ''}
                  </a>
                `)}
              </div>
            ` : html`
              <div class="no-examples">No examples found for this tag.</div>
            `}
          </div>
        ` : ''}
      </div>
    `;
  }

  protected firstUpdated() {
    // Close popup when clicking backdrop
    this.addEventListener('click', this.handleBackdropClick);
    
    // Close popup on escape key
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && this.open) {
        this.close();
      }
    };
    document.addEventListener('keydown', handleEscape);
    
    // Clean up event listener
    this.addEventListener('tag-popup-close', () => {
      document.removeEventListener('keydown', handleEscape);
    });
  }
}