import { html, css, LitElement } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import './SvgIcon.js';

@customElement('svg-icon-button')
export class SvgIconButton extends LitElement {

    @property()
    src: string = '';

    @property()
    title: string = '';

    /**
   * Jiggle behavior for the icon. Can be:
   * - 'jiggleOnHover' (or true/"true" for backwards compatibility)
   * - 'jiggleUntilClick'
   */
    @property()
    jiggle: 'jiggleOnHover' | 'jiggleUntilClick' | boolean | 'true' = 'true';


    @property({ type: Boolean, reflect: true })
    disabled = false;

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
  `;

    private _handleClick(event: Event) {
        if (this.disabled) {
            event.preventDefault();
            event.stopPropagation();
            return;
        }
        // Let the native click event bubble up naturally
        // The event will automatically bubble and can be caught with @click on the parent
    }

    render() {
        return html`
      <button
        @click=${this._handleClick}
        ?disabled=${this.disabled}
        aria-label=${this.title}
        title=${this.title}
      >
        <svg-icon
          src=${this.src}
          .jiggle=${this.jiggle}
        ></svg-icon>
      </button>
    `;
    }
}

declare global {
    interface HTMLElementTagNameMap {
        'svg-icon-button': SvgIconButton;
    }
}
