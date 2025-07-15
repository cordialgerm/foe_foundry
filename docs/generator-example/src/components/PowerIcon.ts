import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { unsafeHTML } from 'lit-html/directives/unsafe-html.js';


@customElement('power-icon')
export class PowerIcon extends LitElement {

    static styles = css`
    :host {
      display: inline-block;
      width: 1em;
      height: 1em;
    }
    svg {
      width: 100%;
      height: 100%;
    }
  `;

    @property()
    src = '';

    private svgContent: string = '';

    async firstUpdated() {
        if (this.src) {
            await cleanAndInjectSVGFromURL(this.src, this.renderRoot.querySelector('span') as HTMLElement);
        }
    }

    render() {
        return html`<span>${unsafeHTML(this.svgContent)}</span>`;
    }
}



async function cleanAndInjectSVGFromURL(url: string, targetElement: HTMLElement, fillValue: string = 'currentColor') {

    try {
        const result = await fetch(url);
        const svgText = await result.text();
        // Strip out any fill="..." attributes
        const cleaned = svgText.replace(/\s*fill=(['"])[^'"]*\1/g, '');

        // Convert SVG string into a DOM element
        const parser = new DOMParser();
        const doc = parser.parseFromString(cleaned, 'image/svg+xml');
        const svgEl = doc.documentElement;

        // Optionally apply a uniform fill
        if (fillValue !== null) {
            svgEl.setAttribute('fill', fillValue);
        }

        // Replace the contents of the target <div>
        targetElement.innerHTML = '';
        targetElement.appendChild(svgEl);
        targetElement.classList.remove('lazy-icon-placeholder');
    }
    catch (error) {
        console.warn('Error loading SVG icon:', url, error);
    }
}