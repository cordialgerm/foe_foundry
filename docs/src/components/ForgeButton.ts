import { html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { StatblockButton } from './StatblockButton.js';
import './SvgIcon.js';

@customElement('forge-button')
export class ForgeStatblockButton extends StatblockButton {

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
        }

        svg-icon {
            width: 3rem;
            height: 3rem;
            color: var(--fg-color);
        }
    `;

    private _handleClick(): void {
        if (this.disabled || !this.monsterKey) return;

        // Dispatch custom event to notify parent components
        this.dispatchEvent(new CustomEvent('forge-click', {
            detail: {
                target: this.target,
                monsterKey: this.monsterKey
            },
            bubbles: true,
            composed: true
        }));

        const url = `/generate/v2/?monster-key=${encodeURIComponent(this.monsterKey)}`;
        window.location.href = url;
    }

    render() {
        return html`
            <button
                @click=${this._handleClick}
                ?disabled=${this.disabled}
                aria-label="Forge your own version of this monster"
                title="Forge your own version of this monster"
            >
                <svg-icon src="anvil-impact" .jiggle=${this.jiggle}></svg-icon>
            </button>
        `;
    }
}

declare global {
    interface HTMLElementTagNameMap {
        'forge-button': ForgeStatblockButton;
    }
}
