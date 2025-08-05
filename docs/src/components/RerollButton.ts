import { html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { StatblockButton } from './StatblockButton.js';
import { initializeMonsterStore } from '../data/api.js';
import { StatblockRequest, StatblockChange, StatblockChangeType } from '../data/monster.js';
import { trackRerollClick } from '../utils/analytics.js';
import './SvgIcon.js';

@customElement('reroll-button')
export class RerollButton extends StatblockButton {

  @property({ type: Boolean, reflect: true })
  rolling = false;

  /**
   * Jiggle behavior for the icon. Can be:
   * - 'jiggleOnHover' (or true/"true" for backwards compatibility)
   * - 'jiggleUntilClick'
   */
  @property()
  jiggle: 'jiggleOnHover' | 'jiggleUntilClick' | boolean | 'true' = 'true';

  static styles = css`
    :host {
      display: inline-block;
    }

    button {
      font-size: 3rem;
      background: none;
      border: none;
      cursor: pointer;
      padding: 8px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
      color: var(--fg-color);
    }

    button:hover:not(:disabled) {
      transform: scale(1.05);
    }

    button:active:not(:disabled) {
      transform: scale(0.95);
    }

    button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      color: inherit;
    }

    svg-icon {
      width: 3rem;
      height: 3rem;
      color: var(--fg-color);
    }

    /* Rolling animation for the button */
    :host([rolling]) button {
      animation: roll-dice 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Rolling animation for the d20 icon */
    :host([rolling]) svg-icon {
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

    @keyframes roll-dice {
      0% {
        transform: rotate(0deg) scale(1);
      }
      50% {
        transform: rotate(720deg) scale(1.2);
      }
      70% {
        transform: rotate(720deg) scale(0.95);
      }
      85% {
        transform: rotate(720deg) scale(1.05) translateX(-2px);
      }
      95% {
        transform: rotate(720deg) scale(1.02) translateX(2px);
      }
      100% {
        transform: rotate(720deg) scale(1) translateX(0);
      }
    }

    /* Hover effect: glow + gentle jiggle */
    button:hover:not(:disabled) .d20-icon {
      filter: drop-shadow(0 0 5px var(--box-shadow-color));
      animation: jiggle 0.6s cubic-bezier(0.4, 0, 0.2, 1) 1;
    }

    @keyframes jiggle {
      0% {
        transform: rotate(0deg) translateX(0);
      }
      25% {
        transform: rotate(1.5deg) translateX(1px);
      }
      50% {
        transform: rotate(0deg) translateX(0);
      }
      75% {
        transform: rotate(-1.5deg) translateX(-1px);
      }
      100% {
        transform: rotate(0deg) translateX(0);
      }
    }
  `;

  private async _handleClick() {
    if (this.disabled || this.rolling || !this.monsterKey) return;

    // Track analytics event
    trackRerollClick(this.monsterKey);

    // Dispatch custom event to notify parent components
    this.dispatchEvent(new CustomEvent('reroll-click', {
      detail: {
        target: this.target,
        monsterKey: this.monsterKey
      },
      bubbles: true,
      composed: true
    }));

    // Trigger the rolling animation
    this.rolling = true;
    this.disabled = true;

    // Remove rolling state after animation completes
    setTimeout(() => {
      this.rolling = false;
      this.disabled = false;
    }, 600); // Match the animation duration

    await this.findTargetStatblock()?.reroll({})
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
          .jiggle=${this.jiggle}
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