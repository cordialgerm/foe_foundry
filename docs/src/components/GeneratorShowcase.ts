import { LitElement, html, css } from 'lit';
import { customElement, query } from 'lit/decorators.js';
import { SiteCssMixin } from '../utils/css-adoption.js';
import './RerollButton.js';
import './ForgeButton.js';
import './MonsterStatblock.js';

@customElement('generator-showcase')
export class GeneratorShowcase extends SiteCssMixin(LitElement) {
    @query('#showcase-statblock')
    private statblock!: HTMLElement;
    static styles = css`
        :host {
            display: block;
            font-size: var(--header-font-size);
        }

        .showcase-container {
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-left: auto;
            margin-right: auto;
        }

        .showcase-controls {
            display: flex;
            gap: 0.5rem;
            padding: 0.5rem;
        }

        .lead {
            color: var(--bg-color);
            font-family: var(--header-font);
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            text-align: center;
        }

        #showcase-statblock.hidden {
            display: none;
        }

        .statblock-container.visible {
            display: block;
        }

        .showcase-button {
            --fg-color: var(--bg-color);
        }
    `;

    firstUpdated() {
        // Adopt site CSS for access to CSS variables and other site styles
        this.adoptSiteCss();

        // Add event listeners for button interactions
        this.addEventListener('reroll-click', this._handleButtonClick.bind(this));
        this.addEventListener('forge-click', this._handleButtonClick.bind(this));
    }

    private _handleButtonClick() {
        console.log('Button clicked, updating statblock visibility');
        // Remove the hidden class from the statblock to show it
        if (this.statblock && this.statblock.classList.contains('hidden')) {
            this.statblock.classList.remove('hidden');
        }
    }

    render() {
        return html`
            <div class="showcase-container bg-object scroll">
                <span class="lead">Summon Your First Foe</span>
                <div class="showcase-controls">
                    <reroll-button jiggle="jiggleUntilClick" class="showcase-button" detached target="showcase-statblock"></reroll-button>
                    <forge-button jiggle="jiggleUntilClick" class="showcase-button" detached target="showcase-statblock"></forge-button>
                </div>
            </div>
            <monster-statblock class="hidden" id="showcase-statblock"></monster-statblock>
        `;
    }
}
