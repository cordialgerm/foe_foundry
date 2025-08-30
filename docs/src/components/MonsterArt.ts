import { LitElement, html, css } from 'lit';
import { property, customElement, state } from 'lit/decorators.js';

@customElement('monster-art')
export class MonsterArt extends LitElement {

  @property({ type: String, attribute: 'monster-image' })
  monsterImage: string = '';

  @property({ type: String, attribute: 'background-image' })
  backgroundImage: string = '';

  @property({ type: String, attribute: 'background-color' })
  backgroundColor: string = 'rgba(255, 255, 255, 0.55)';

  @property({ type: String, attribute: 'image-mode' })
  imageMode: 'contain' | 'cover' = 'contain';

  @state()
  private imageLoaded: boolean = false;

  // Reset loaded state when image source changes
  updated(changedProperties: Map<string, unknown>) {
    if (changedProperties.has('monsterImage')) {
      this.imageLoaded = false;
    }
  }

  static styles = css`
    :host {
      display: block;
    }

    .monster-art-container {
      height: 200px;
      position: relative;
      background-size: cover;
      background-position: center;
      display: flex;
      justify-content: center;
      align-items: center;
      overflow: hidden;
      margin-bottom: 1rem;
      contain: layout style; /* Prevent layout shifts from image loading */
    }

    .monster-art-container::before {
      content: '';
      position: absolute;
      inset: 0;
      background: radial-gradient(ellipse at center, transparent 50%, rgba(0, 0, 0, 0.5) 100%);
      z-index: 1;
      pointer-events: none;
      transition: opacity 0.3s ease;
    }

    .monster-art-container.undead {
      background-color: rgba(255, 255, 255, 0.55);
      background-blend-mode: lighten;
    }

    .card-image {
      position: relative;
      inset: 0;
      width: 100%;
      height: 100%;
      z-index: 2;
      object-fit: contain;
      object-position: center;
      mix-blend-mode: multiply;
      opacity: 0;
      transition: opacity 0.3s ease-in-out;
    }

    .card-image.loaded {
      opacity: 1;
    }

    .card-image.contain {
      object-fit: contain;
      object-position: center;
    }

    .card-image.cover {
      object-fit: cover;
      object-position: center;
    }
  `;

  private get imageClasses(): string {
    const classes = ['card-image'];
    if (this.imageMode) {
      classes.push(this.imageMode);
    }
    if (this.imageLoaded) {
      classes.push('loaded');
    }
    return classes.join(' ');
  }

  private get containerStyle(): string {
    if (this.backgroundImage) {
      return `background-image: url('${this.backgroundImage}'); background-color: ${this.backgroundColor}; background-blend-mode: lighten;`;
    }
    return '';
  }

  protected render() {
    return html`
      <div
        class="monster-art-container"
        style="${this.containerStyle}"
      >
        ${this.monsterImage ? html`
          <img
            src="${this.monsterImage}"
            alt="Monster Art"
            class="${this.imageClasses}"
            @error="${this._handleImageError}"
            @load="${this._handleImageLoad}"
          />
        ` : ''}
      </div>
    `;
  }

  private _handleImageError(event: Event) {
    console.warn('Failed to load monster image:', this.monsterImage);
    this.dispatchEvent(new CustomEvent('image-error', {
      detail: { src: this.monsterImage },
      bubbles: true
    }));
  }

  private _handleImageLoad(event: Event) {
    this.imageLoaded = true;
    this.dispatchEvent(new CustomEvent('image-loaded', {
      detail: { src: this.monsterImage },
      bubbles: true
    }));
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'monster-art': MonsterArt;
  }
}