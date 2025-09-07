import { LitElement, html, css, PropertyValues } from 'lit';
import { customElement, property } from 'lit/decorators.js';

// Default darkly humorous skull mascot quotes
const DEFAULT_SKULL_QUOTES = [
  "Careful, GM… your monsters look *balanced*.",
  "I hold the secrets to truly cursed foes.",
  "Subscribe, mortal, and learn forbidden powers.",
  "These creatures need more... *personality*.",
  "Let me whisper dark secrets in your ear...",
  "Your campaign lacks proper dread, doesn't it?",
  "I've seen things that would make your players weep.",
  "Want to craft nightmares? I can teach you."
];

type SkullDisplay = 'visible' | 'collapsed' | 'hidden';
type SkullState = 'idle' | 'active';

@customElement('animated-skull')
export class AnimatedSkull extends LitElement {
  @property({ type: String })
  display: SkullDisplay = 'visible';

  @property({ type: String })
  quotes: string = '';

  @property({ type: Function })
  onClick?: () => void;

  @property({ type: Boolean })
  showQuote: boolean = false;

  @property({ type: Number })
  quoteIndex: number = 0;

  private _quotesArray: string[] = [];
  private _state: SkullState = 'idle';

  static styles = css`
    :host {
      display: inline-block;
      position: relative;
      cursor: pointer;
      transition: all 0.3s ease;
    }

    :host([display="hidden"]) {
      display: none;
    }

    :host([display="collapsed"]) {
      visibility: hidden;
      height: 0;
      overflow: hidden;
    }

    .skull-container {
      position: relative;
      display: inline-block;
      transition: all 0.3s ease;
    }

    .skull-mascot {
      font-size: 3rem;
      line-height: 1;
      transition: all 0.5s ease;
      filter: drop-shadow(0 0 10px rgba(255, 69, 0, 0.3));
      user-select: none;
    }

    .speech-bubble {
      position: absolute;
      bottom: 100%;
      left: 50%;
      transform: translateX(-50%) translateY(-10px);
      background: linear-gradient(135deg, #2a1810, #1a1a1a);
      border: 2px solid #8b4513;
      border-radius: 15px;
      padding: 12px 16px;
      color: #f4f1e6;
      font-family: var(--primary-font, 'Cinzel', serif);
      font-size: 0.9rem;
      font-weight: 500;
      white-space: nowrap;
      max-width: 280px;
      opacity: 0;
      visibility: hidden;
      transition: all 0.3s ease;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
      z-index: 10;
      pointer-events: none;
    }

    .speech-bubble::after {
      content: '';
      position: absolute;
      top: 100%;
      left: 50%;
      transform: translateX(-50%);
      border: 8px solid transparent;
      border-top-color: #8b4513;
    }

    .speech-bubble::before {
      content: '';
      position: absolute;
      top: 100%;
      left: 50%;
      transform: translateX(-50%) translateY(-2px);
      border: 6px solid transparent;
      border-top-color: #2a1810;
      z-index: 1;
    }

    /* State-based styles */
    :host([data-state="idle"]) .skull-mascot {
      animation: idleFloat 4s infinite ease-in-out;
    }

    :host([data-state="active"]) .speech-bubble {
      opacity: 1;
      visibility: visible;
      transform: translateX(-50%) translateY(0);
      animation: bubblePop 0.4s ease-out;
    }

    :host([data-state="active"]) .skull-mascot {
      animation: activeWiggle 0.5s ease-out;
      transform: scale(1.1);
    }

    /* Animations */
    @keyframes idleFloat {
      0%, 100% { 
        transform: translateY(0) rotate(0deg);
        filter: drop-shadow(0 0 10px rgba(255, 69, 0, 0.3));
      }
      25% { 
        transform: translateY(-3px) rotate(1deg);
        filter: drop-shadow(0 2px 15px rgba(255, 69, 0, 0.4));
      }
      50% { 
        transform: translateY(-5px) rotate(0deg);
        filter: drop-shadow(0 4px 20px rgba(255, 69, 0, 0.5));
      }
      75% { 
        transform: translateY(-3px) rotate(-1deg);
        filter: drop-shadow(0 2px 15px rgba(255, 69, 0, 0.4));
      }
    }

    @keyframes activeWiggle {
      0% { transform: scale(1) rotate(0deg); }
      25% { transform: scale(1.05) rotate(-5deg); }
      50% { transform: scale(1.1) rotate(0deg); }
      75% { transform: scale(1.05) rotate(5deg); }
      100% { transform: scale(1.1) rotate(0deg); }
    }

    @keyframes bubblePop {
      0% { 
        transform: translateX(-50%) translateY(-10px) scale(0.8);
        opacity: 0;
      }
      50% { 
        transform: translateX(-50%) translateY(0) scale(1.05);
      }
      100% { 
        transform: translateX(-50%) translateY(0) scale(1);
        opacity: 1;
      }
    }

    /* Hover effects */
    .skull-container:hover .skull-mascot {
      transform: scale(1.2);
      animation: none;
    }

    .skull-container:hover .speech-bubble {
      animation: bubblePop 0.4s ease-out;
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
      .skull-mascot {
        font-size: 2.5rem;
      }

      .speech-bubble {
        font-size: 0.8rem;
        max-width: 200px;
      }
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    this._parseQuotes();
  }

  updated(changedProperties: PropertyValues) {
    super.updated(changedProperties);

    if (changedProperties.has('quotes')) {
      this._parseQuotes();
    }

    if (changedProperties.has('showQuote')) {
      this._state = this.showQuote ? 'active' : 'idle';
      this.setAttribute('data-state', this._state);
    }

    this.setAttribute('display', this.display);
    this.setAttribute('data-state', this._state);
  }

  private _parseQuotes(): void {
    if (this.quotes) {
      this._quotesArray = this.quotes.split(';').map(q => q.trim()).filter(q => q.length > 0);
    } else {
      this._quotesArray = DEFAULT_SKULL_QUOTES;
    }
  }

  private _getCurrentQuote(): string {
    if (this._quotesArray.length === 0) return '';
    return this._quotesArray[this.quoteIndex % this._quotesArray.length];
  }

  private _handleClick(): void {
    if (this.onClick) {
      this.onClick();
    }
  }

  render() {
    if (this.display === 'hidden') {
      return html``;
    }

    return html`
      <div class="skull-container" @click=${this._handleClick}>
        <div class="skull-mascot">💀</div>
        
        ${this.showQuote ? html`
          <div class="speech-bubble">
            ${this._getCurrentQuote()}
          </div>
        ` : ''}
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'animated-skull': AnimatedSkull;
  }
}