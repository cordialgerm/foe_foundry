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

    async updated(changedProperties: Map<string, any>) {
        if (changedProperties.has('src') && this.src) {
            await cleanAndInjectSVGFromURL(this.src, this.renderRoot.querySelector('span') as HTMLElement);
        }
    }

    render() {
        return html`<span class="svg-icon placeholder">${unsafeHTML(this.svgContent)}</span>`;
    }
}

const svgCache = new Map<string, string>();

async function cleanAndInjectSVGFromURL(url: string, targetElement: HTMLElement, fillValue: string = 'currentColor') {
    try {
        if (svgCache.has(url)) {
            // Use cached SVG content
            const cachedSVG = svgCache.get(url) as string;
            injectSVG(cachedSVG, targetElement, fillValue);
            return;
        }

        const result = await fetch(url);
        const svgText = await result.text();
        // Strip out any fill="..." attributes
        const cleaned = svgText.replace(/\s*fill=(['"])['"]*\1/g, '');

        // Cache the cleaned SVG content
        svgCache.set(url, cleaned);

        // Inject the SVG into the target element
        injectSVG(cleaned, targetElement, fillValue);
    } catch (error) {
        console.warn('Error loading SVG icon:', url, error);
    }
}

function injectSVG(svgText: string, targetElement: HTMLElement, fillValue: string) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(svgText, 'image/svg+xml');
    const svgEl = doc.documentElement;

    // Optionally apply a uniform fill
    if (fillValue !== null) {
        svgEl.setAttribute('fill', fillValue);
    }

    // Replace the contents of the target <div>
    targetElement.innerHTML = '';
    targetElement.appendChild(svgEl);
    targetElement.classList.remove('placeholder');
}