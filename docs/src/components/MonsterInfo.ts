import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import './MonsterRating';

@customElement('monster-info')
export class MonsterInfo extends LitElement {
  @property({ type: String })
  name = '';

  @property({ type: String })
  tag = '';

  @property({ type: String })
  type = '';

  @property({ type: String })
  cr = '';

  @property({ type: Number, attribute: 'hp-rating' })
  hpRating = 3;

  @property({ type: Number, attribute: 'damage-rating' })
  damageRating = 3;

  static styles = css`
    :host {
      display: block;
      margin-bottom: 1rem;
      padding: 0.5rem;
      background-color: var(--bs-dark);
    }

    .info-header {
      text-align: center;
    }

    .info-header h2 {
      margin-top: 0.5rem;
      margin-bottom: 0.5rem;
    }

    .info-header p {
      margin-bottom: 0.25rem;
      margin-top: 0.25rem;
    }

    .info-header .tag {
      font-style: italic;
    }

    .info-header .tag ::before {
      content: '"';
    }

    .info-header .tag ::after {
      content: '"';
    }

    .rating-container {
      display: flex;
      justify-content: space-around;
      align-items: center;
      flex-direction: column;
    }

    .monster-name {
      display: inline;
      overflow-wrap: break-word;

      color: var(--primary-color);
      font-family: var(--stylistic-font);
      font-size: var(--stylistic-font-size);
      column-span: all;
    }

    .monster-name:after {
      content: "";
      display: block;
      width: 100%;
      margin: 2px auto var(--medium-margin);
      height: var(--header-border-width);
      background: var(--primary-color);
      column-span: all;
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    this.addEventListener('rating-change', this.handleRatingChange);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.removeEventListener('rating-change', this.handleRatingChange);
  }

  private handleRatingChange = (event: Event) => {
    const customEvent = event as CustomEvent;
    const { score, label } = customEvent.detail;

    // Get the original target using composedPath
    const composedPath = event.composedPath();
    const originalTarget = composedPath[0] as HTMLElement;

    let eventType = '';
    if (originalTarget.id === 'hp-rating') {
      eventType = 'hp-changed';
    } else if (originalTarget.id === 'damage-rating') {
      eventType = 'damage-changed';
    }

    if (eventType) {
      this.dispatchEvent(new CustomEvent(eventType, {
        detail: { score, label },
        bubbles: true,
        composed: true
      }));
    }
  };

  render() {
    return html`
      <div class="monster-info">
        <div class="info-header">
          <h3 class="monster-name">${this.name}</h3>
          <p class="tag">${this.tag}</p>
          <p>${this.type} • ${this.cr}</p>
        </div>

        <div class="rating-container">
          <monster-rating id="hp-rating" emoji="❤️"></monster-rating>
          <monster-rating id="damage-rating" emoji="💀"></monster-rating>
        </div>
      </div>
    `;
  }
}
