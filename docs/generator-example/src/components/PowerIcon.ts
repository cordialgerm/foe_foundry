import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';


@customElement('power-icon')
export class PowerIcon extends LitElement {

    static styles = css`
    :host {
      display: inline-block;
      width: 24px;
      height: 24px;
    }
    svg {
      width: 100%;
      height: 100%;
    }
  `;

    @property()
    src = '';

    private svgContent: string = '';

    async connectedCallback() {
        super.connectedCallback();
        if (this.src) {
            try {
                const response = await fetch(this.src);
                if (response.ok) {
                    this.svgContent = await response.text();
                    this.requestUpdate();
                } else {
                    console.error(`Failed to load SVG: ${response.statusText}`);
                }
            } catch (error) {
                console.error(`Error fetching SVG: ${error}`);
            }
        }
    }

    render() {
        return html`<div .innerHTML=${this.svgContent}></div>`;
    }
}