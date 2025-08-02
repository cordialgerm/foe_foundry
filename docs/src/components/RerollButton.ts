import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import './SvgIcon';

@customElement('reroll-button')
export class RerollButton extends LitElement {

    @property({ type: String, attribute: 'monster-key' })
    monsterKey = '';

    @property({ type: Boolean, reflect: true })
    disabled = false;

    @property({ type: Boolean, reflect: true })
    rolling = false;

    static styles = css`
    :host {
      display: inline-block;
    }

    button {
      background: none;
      border: none;
      cursor: pointer;
      padding: 8px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
    }

    button:hover:not(:disabled) {
      background-color: rgba(255, 255, 255, 0.1);
      transform: scale(1.05);
    }

    button:active:not(:disabled) {
      transform: scale(0.95);
    }

    button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .d20-icon {
      width: 24px;
      height: 24px;
      color: var(--primary-color, #007bff);
    }

    :host([rolling]) .d20-icon {
      animation: roll 0.6s cubic-bezier(0.4, 0, 0.2, 1) 1;
    }

    @keyframes roll {
      0% {
        transform: rotate(0deg);
      }
      25% {
        transform: rotate(90deg) scale(1.1);
      }
      50% {
        transform: rotate(180deg) scale(1.2);
      }
      75% {
        transform: rotate(270deg) scale(1.1);
      }
      100% {
        transform: rotate(360deg);
      }
    }
  `;

    private _handleClick() {
        if (this.disabled || this.rolling || !this.monsterKey) return;

        // Trigger the rolling animation
        this.rolling = true;
        this.disabled = true;

        // Remove rolling state after animation completes
        setTimeout(() => {
            this.rolling = false;
            this.disabled = false;
        }, 600); // Match the animation duration

        // Dispatch custom event that parent can listen to
        this.dispatchEvent(new CustomEvent('reroll', {
            detail: { monsterKey: this.monsterKey },
            bubbles: true,
            composed: true
        }));
    }

    render() {
        return html`
      <button
        @click=${this._handleClick}
        ?disabled=${this.disabled}
        aria-label="Reroll this monster"
        title="Reroll this monster"
      >
        <svg-icon
          src="d20"
          class="d20-icon"
          jiggle="true"
        ></svg-icon>
      </button>
    `;
    }
}

declare global {
    interface HTMLElementTagNameMap {
        'reroll-button': RerollButton;
    }
}
