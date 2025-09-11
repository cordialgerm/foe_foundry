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

        .jiggle-on-hover:hover svg,
        .jiggle-until-click:hover svg {
          filter: drop-shadow(0 0 5px var(--box-shadow-color));
          animation: jiggle 0.6s cubic-bezier(0.4, 0, 0.2, 1) 1;
        }

        .jiggle-until-click svg {
          filter: drop-shadow(0 0 3px var(--box-shadow-color));
          animation: jiggle-subtle 1.5s ease-in-out infinite;
        }

        .jiggle-until-click.clicked svg {
          animation: none !important;
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

        @keyframes jiggle-subtle {
          0%, 100% {
            transform: rotate(0deg) translateX(0);
          }
          25% {
            transform: rotate(1deg) translateX(0.5px);
          }
          75% {
            transform: rotate(-1deg) translateX(-0.5px);
          }
        }
      `
  ];


  @property()
  src = '';

  /**
   * Jiggle behavior type. Can be:
   * - 'jiggleOnHover' (or true/"true" for backwards compatibility)
   * - 'jiggleUntilClick'
   */
  @property()
  jiggle: 'jiggleOnHover' | 'jiggleUntilClick' | boolean | 'true' = false;

  @property({ attribute: false })
  private svgContent: string = '';

  private handleClick() {
    this.shadowRoot?.querySelector('span')?.classList.add('clicked');
  }

  async firstUpdated() {
    if (this.src) {
      this.svgContent = await loadAndCleanSVG(this.src);
    }

    // Add click handler for jiggleUntilClick behavior
    this.addEventListener('click', this.handleClick.bind(this));

    // Add random delay for jiggle-until-click to desynchronize animations
    if (this.jiggle === 'jiggleUntilClick') {
      // Wait for the next update cycle before applying the delay
      await this.updateComplete;
      const spanElement = this.renderRoot.querySelector('span');
      if (spanElement) {
        const randomDelay = Math.random() * 2; // 0-2 seconds random delay
        spanElement.style.animationDelay = `${randomDelay}s`;
      }
    }
  }

  async updated(changedProperties: Map<string, any>) {
    if (changedProperties.has('src') && this.src) {
      this.svgContent = await loadAndCleanSVG(this.src);
    }
  }

  render() {
    const isJiggleOnHover = this.jiggle === 'jiggleOnHover' || this.jiggle === true || this.jiggle === 'true';
    const isJiggleUntilClick = this.jiggle === 'jiggleUntilClick';

    const classes = {
      'svg-icon': true,
      'placeholder': true,
      'jiggle-on-hover': isJiggleOnHover,
      'jiggle-until-click': isJiggleUntilClick,
    };
    const classString = Object.entries(classes)
      .filter(([_, v]) => v)
      .map(([k]) => k)
      .join(' ');
    return html`<span class="${classString}">${unsafeHTML(this.svgContent)}</span>`;
  }
}

const svgCache = new Map<string, string>();

async function loadAndCleanSVG(src: string, fillValue: string = 'currentColor'): Promise<string> {
  try {
    // Check if src is a valid URL ending with .svg
    let url = src;
    if (!src.endsWith('.svg')) {
      // Assume it's an icon name and convert to URL
      url = `/img/icons/${src}.svg`;
    }
    // if it's the just the name of an icon but without a filepath, convert it as well like "hello.svg" should be "/img/icons/hello.svg"
    else if (!url.includes('/') && url.endsWith('.svg')) {
      url = `/img/icons/${url}`;
    }

    if (svgCache.has(url)) {
      // Use cached SVG content
      return svgCache.get(url) as string;
    }

    const result = await fetch(url);
    if (!result.ok) {
      throw new Error(`Failed to load SVG from ${url}: ${result.statusText}`);
    }

    const svgText = await result.text();
    // Strip out any fill="..." attributes, width/height attributes, and style attributes to allow CSS control
    let cleaned = svgText
      .replace(/\s*fill\s*=\s*(['"])[^'"]*\1/gi, '')
      .replace(/\s*width\s*=\s*(['"])[^'"]*\1/gi, '')
      .replace(/\s*height\s*=\s*(['"])[^'"]*\1/gi, '')
      .replace(/\s*style\s*=\s*(['"])[^'"]*\1/gi, '');

    // Apply fill value if provided
    if (fillValue !== null) {
      cleaned = cleaned.replace('<svg', `<svg fill="${fillValue}"`);
    }

    // Cache the cleaned SVG content
    svgCache.set(url, cleaned);

    return cleaned;
  } catch (error) {
    console.warn('Error loading SVG icon:', src, error);
    return '';
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'svg-icon': SvgIcon;
  }
}