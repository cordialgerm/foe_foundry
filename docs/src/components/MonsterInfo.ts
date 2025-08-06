import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';

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

  static styles = css`
    :host {
      display: block;
      padding: 0.5rem;
      background-color: var(--bs-dark);
    }

    .info-header {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: 0.5rem;
    }

    .tag {
      font-style: italic;
      text-align: left;
      align-self: flex-start;
      margin-left: 0.5rem;
      margin-bottom: 0.1rem;
      margin-top: 0.1rem;
      font-size: 0.9rem;
    }

    .type-cr {
      text-align: left;
      align-self: flex-start;
      margin-left: 0.5rem;
      margin-bottom: 0.1rem;
      margin-top: 0.1rem;
      font-size: 0.9rem;
    }

    .monster-name {
      display: inline;
      overflow-wrap: break-word;
      color: var(--primary-color);
      font-family: var(--stylistic-font);
      font-size: var(--stylistic-font-size);
      column-span: all;
      text-align: left;
      width: 100%;
      margin-top: 0px;
      margin-bottom: 0px;
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

  render() {
    return html`
      <div class="monster-info">
        <div class="info-header">
          <h3 class="monster-name">${this.name}</h3>
          <p class="tag">${this.tag}</p>
          <p class="type-cr">${this.type} • ${this.cr}</p>
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'monster-info': MonsterInfo;
  }
}
