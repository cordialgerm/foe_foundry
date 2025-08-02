import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { unsafeHTML } from 'lit-html/directives/unsafe-html.js';


@customElement('svg-icon')
export class SvgIcon extends LitElement {

  static styles = [
    css`
        :host {
          display: inline-block;
          width: 1em;
          height: 1em;
        }
        svg {
          width: 100%;
          height: 100%;
        }

        .jiggle-on-hover:hover svg {
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
      `
  ];


  @property()
  src = '';

  /**
   * If true, applies the jiggle animation to the icon
   */
  @property({ type: Boolean })
  jiggle = false;

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
    const classes = {
      'svg-icon': true,
      'placeholder': true,
      'jiggle-on-hover': this.jiggle
    };
    const classString = Object.entries(classes)
      .filter(([_, v]) => v)
      .map(([k]) => k)
      .join(' ');
    return html`<span class="${classString}">${unsafeHTML(this.svgContent)}</span>`;
  }
}

const svgCache = new Map<string, string>();

async function cleanAndInjectSVGFromURL(src: string, targetElement: HTMLElement, fillValue: string = 'currentColor') {
  try {
    // Check if src is a valid URL ending with .svg
    let url = src;
    if (!src.endsWith('.svg')) {
      // Assume it's an icon name and convert to URL
      url = `/img/icons/${src}.svg`;
    }

    if (svgCache.has(url)) {
      // Use cached SVG content
      const cachedSVG = svgCache.get(url) as string;
      injectSVG(cachedSVG, targetElement, fillValue);
      return;
    }

    const result = await fetch(url);
    if (!result.ok) {
      throw new Error(`Failed to load SVG from ${url}: ${result.statusText}`);
    }

    const svgText = await result.text();
    // Strip out any fill="..." attributes, width/height attributes, and style attributes to allow CSS control
    const cleaned = svgText
      .replace(/\s*fill\s*=\s*(['"])[^'"]*\1/gi, '')
      .replace(/\s*width\s*=\s*(['"])[^'"]*\1/gi, '')
      .replace(/\s*height\s*=\s*(['"])[^'"]*\1/gi, '')
      .replace(/\s*style\s*=\s*(['"])[^'"]*\1/gi, '');

    // Cache the cleaned SVG content
    svgCache.set(url, cleaned);

    // Inject the SVG into the target element
    injectSVG(cleaned, targetElement, fillValue);
  } catch (error) {
    console.warn('Error loading SVG icon:', src, error);
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

declare global {
  interface HTMLElementTagNameMap {
    'svg-icon': SvgIcon;
  }
}