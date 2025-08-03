import { LitElement, html, css } from 'lit';
import { customElement, property, query } from 'lit/decorators.js';
import { SiteCssMixin } from '../utils/css-adoption.js';
import './RerollButton.js';
import './ForgeButton.js';
import './MonsterStatblock.js';

@customElement('generator-showcase')
export class GeneratorShowcase extends SiteCssMixin(LitElement) {
    @property({ type: String, attribute: 'monster-key' })
    monsterKey: string | null = null;

    @query('#showcase-statblock')
    private statblock!: HTMLElement;

    private getMonsterKeyFromUrl(): string | null {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('monster-key') || urlParams.get('template');
    }

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
            margin-bottom: 2rem;
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

        .instructions {
            color: var(--bg-color);
            margin-bottom: 1rem;
            text-align: center;
        }

        #showcase-statblock.hidden {
            display: none;
            margin-bottom: 2rem;
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

    private _newsletterClick() {
        window.open('https://buttondown.com/cordialgerm', '_blank');
    }

    render() {
        const effectiveMonsterKey = this.monsterKey || this.getMonsterKeyFromUrl();
        const statblockClass = effectiveMonsterKey ? '' : 'hidden';

        return html`
            <div class="showcase-container bg-object scroll">
                <span class="lead">Summon Your First Foe</span>
                <p class="instructions">Roll the dice below to summon a random monster! Click the Anvil to forge it into the perfect Foe.</p>
                <div class="showcase-controls">
                    <reroll-button
                        jiggle="jiggleUntilClick"
                        class="showcase-button"
                        target="showcase-statblock"
                        detached
                        ?random="${!effectiveMonsterKey}">
                    </reroll-button>
                    <forge-button
                        jiggle="jiggleUntilClick"
                        class="showcase-button"
                        target="showcase-statblock"
                        detached>
                    </forge-button>
                    <svg-icon-button
                        title="Subscribe to the Foe Foundry Newsletter"
                        src="death-note"
                        jiggle="jiggleUntilClick"
                        class="showcase-button newsletter"
                        @click="${this._newsletterClick}"
                    >
                    </svg-icon-button>
                </div>
            </div>
            <monster-statblock
                class="${statblockClass}"
                id="showcase-statblock"
                monster-key="${effectiveMonsterKey || ''}"
            ></monster-statblock>
        `;
    }
}
