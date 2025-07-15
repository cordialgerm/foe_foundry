import { LitElement, html, css } from 'lit';
import { property, customElement } from 'lit/decorators.js';

@customElement('monster-art')
export class MonsterArt extends LitElement {

  @property({ type: String, attribute: 'monster-image' })
  monsterImage: string = '';

  @property({ type: String, attribute: 'background-image' })
  backgroundImage: string = '';

  @property({ type: String, attribute: 'image-mode' })
  imageMode: 'contain' | 'cover' = 'contain';

  @property({ type: Boolean, attribute: 'blend-mode' })
  blendMode: boolean = false;

  @property({ type: Boolean })
  faded: boolean = false;

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
      border: 1px solid var(--bs-border-color, #6c757d);
      border-radius: 0.375rem;
      margin-bottom: 1rem;
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
    }

    .card-image.contain {
      object-fit: contain;
      object-position: center;
    }

    .card-image.cover {
      object-fit: cover;
      object-position: center;
    }

    .card-image.blend {
      mix-blend-mode: multiply;
    }

    .card-image.faded {
      opacity: 0.6;
    }
  `;

  private get imageClasses(): string {
    const classes = ['card-image'];
    if (this.imageMode) {
      classes.push(this.imageMode);
    }
    if (this.blendMode) {
      classes.push('blend');
    }
    if (this.faded) {
      classes.push('faded');
    }
    return classes.join(' ');
  }

  private get containerStyle(): string {
    if (this.backgroundImage) {
      return `background-image: url('${this.backgroundImage}')`;
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
    this.dispatchEvent(new CustomEvent('image-loaded', {
      detail: { src: this.monsterImage },
      bubbles: true
    }));
  }
}