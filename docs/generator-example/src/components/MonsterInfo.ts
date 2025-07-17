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
      padding: 1rem;
      border: 1px solid var(--bs-secondary);
      border-radius: 0.375rem;
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
  `;

  render() {
    return html`
      <div class="monster-info">
        <div class="info-header">
          <h2>${this.name}</h2>
          <p class="tag">${this.tag}</p>
          <p>${this.type} • ${this.cr}</p>
        </div>

        <div class="rating-container">
          <monster-rating emoji="❤️"></monster-rating>
          <monster-rating emoji="💀"></monster-rating>
        </div>
      </div>
    `;
  }
}
