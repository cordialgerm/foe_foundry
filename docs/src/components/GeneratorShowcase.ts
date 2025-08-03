import { LitElement, html, css } from 'lit';
import { customElement } from 'lit/decorators.js';
import { SiteCssMixin } from '../utils/css-adoption.js';
import './RerollButton.js';
import './ForgeButton.js';
import './MonsterStatblock.js';

@customElement('generator-showcase')
export class GeneratorShowcase extends SiteCssMixin(LitElement) {
    static styles = css`
        :host {
            display: block;
        }

        .showcase-container {
            padding: 1.5rem;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }

        .showcase-controls {
            display: inline-block;
            padding: 0.5rem;
        }

        .lead {
            color: var(--bg-color);
            font-family: var(--header-font);
            font-size: var(--header-font-size);
            font-weight: 600;
            margin-right: 0.5rem;
        }

        #showcase-statblock.hidden {
            display: none;
        }

        .statblock-container.visible {
            display: block;
        }
    `;

    firstUpdated() {
        // Adopt site CSS for access to CSS variables and other site styles
        this.adoptSiteCss();
    }

    render() {
        return html`
            <div class="showcase-container bg-object parchment">
                <span class="lead">Summon Your First Foe</span>
                <div class="showcase-controls">
                    <reroll-button detached target="showcase-statblock"></reroll-button>
                    <forge-button detached target="showcase-statblock"></forge-button>
                </div>
            </div>
            <monster-statblock class="hidden" id="showcase-statblock"></monster-statblock>
        `;
    }
}
