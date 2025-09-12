import { LitElement, html, css, PropertyValues } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import './SvgIcon.js';

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

  @property({ type: String })
  injectedClass: string = '';

  @property({ type: Boolean })
  autoCycle: boolean = true;

  @property({ type: Number })
  cycleInterval: number = 8000; // 8 seconds between quotes

  private _quotesArray: string[] = [];
  private _state: SkullState = 'idle';
  private _cycleTimer?: number;
  private _quoteTimer?: number;

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

    /* Injected class support for centering */
    :host(.centered) {
      display: block;
      text-align: center;
      margin: 2rem auto;
      padding: 1rem 0;
    }

    /* Enhanced interactive styling */
    .skull-container {
      position: relative;
      display: inline-block;
      transition: all 0.3s ease;
      padding: 1rem;
      border-radius: 50%;
      background: radial-gradient(circle, transparent 60%, rgba(255, 69, 0, 0.1) 100%);
    }

    .skull-container:hover {
      background: radial-gradient(circle, transparent 50%, rgba(255, 69, 0, 0.2) 100%);
      transform: scale(1.05);
    }

    .skull-mascot {
      font-size: 4rem;
      line-height: 1;
      transition: all 0.5s ease;
      filter: drop-shadow(0 0 15px rgba(255, 69, 0, 0.4));
      user-select: none;
      display: inline-block;
    }

    /* Make the SVG icon larger and properly styled */
    .skull-mascot svg-icon {
      width: 4rem;
      height: 4rem;
      color: #f4f1e6;
      filter: drop-shadow(0 0 15px rgba(255, 69, 0, 0.4));
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

    .speech-bubble.visible {
      pointer-events: auto;
    }

    .speech-bubble-close {
      position: absolute;
      top: -8px;
      right: -8px;
      background: #8b0000;
      color: white;
      border: none;
      border-radius: 50%;
      width: 20px;
      height: 20px;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      line-height: 1;
    }

    .speech-bubble-close:hover {
      background: #a00000;
      transform: scale(1.1);
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
      cursor: pointer;
    }

    :host([data-state="idle"]) .skull-container {
      cursor: pointer;
    }

    :host([data-state="idle"]) .skull-container::after {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 120%;
      height: 120%;
      border: 2px solid rgba(255, 69, 0, 0.3);
      border-radius: 50%;
      animation: pulseRing 3s infinite ease-in-out;
      pointer-events: none;
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

    @keyframes pulseRing {
      0% { 
        opacity: 0.7;
        transform: translate(-50%, -50%) scale(0.9);
      }
      50% { 
        opacity: 0.3;
        transform: translate(-50%, -50%) scale(1.1);
      }
      100% { 
        opacity: 0.7;
        transform: translate(-50%, -50%) scale(0.9);
      }
    }

    @keyframes idleFloat {
      0%, 100% { 
        transform: translateY(0) rotate(0deg);
        filter: drop-shadow(0 0 15px rgba(255, 69, 0, 0.4));
      }
      25% { 
        transform: translateY(-5px) rotate(1deg);
        filter: drop-shadow(0 3px 20px rgba(255, 69, 0, 0.5));
      }
      50% { 
        transform: translateY(-8px) rotate(0deg);
        filter: drop-shadow(0 5px 25px rgba(255, 69, 0, 0.6));
      }
      75% { 
        transform: translateY(-5px) rotate(-1deg);
        filter: drop-shadow(0 3px 20px rgba(255, 69, 0, 0.5));
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
        font-size: 3rem;
      }

      .skull-mascot svg-icon {
        width: 3rem;
        height: 3rem;
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
    this._startQuoteCycling();
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this._stopQuoteCycling();
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

    if (changedProperties.has('injectedClass')) {
      // Apply injected classes to the host element
      if (this.injectedClass) {
        this.className = this.injectedClass;
      }
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

  private _startQuoteCycling(): void {
    if (!this.autoCycle || this._quotesArray.length <= 1) return;

    // Check if skull is suppressed by cookie
    if (this._isSkullSuppressed()) {
      this.display = 'hidden';
      return;
    }

    this._cycleTimer = window.setInterval(() => {
      this._showNextQuote();
    }, this.cycleInterval);
  }

  private _stopQuoteCycling(): void {
    if (this._cycleTimer) {
      clearInterval(this._cycleTimer);
      this._cycleTimer = undefined;
    }
    if (this._quoteTimer) {
      clearTimeout(this._quoteTimer);
      this._quoteTimer = undefined;
    }
  }

  private _showNextQuote(): void {
    if (this._quotesArray.length === 0) return;

    this.quoteIndex = (this.quoteIndex + 1) % this._quotesArray.length;
    this.showQuote = true;

    // Auto-hide quote after 4 seconds
    this._quoteTimer = window.setTimeout(() => {
      this.showQuote = false;
    }, 4000);
  }

  private _isSkullSuppressed(): boolean {
    const suppressedUntil = localStorage.getItem('skull-suppressed-until');
    if (!suppressedUntil) return false;
    
    const suppressedDate = new Date(suppressedUntil);
    return suppressedDate > new Date();
  }

  private _suppressSkullFor3Days(): void {
    const suppressUntil = new Date();
    suppressUntil.setDate(suppressUntil.getDate() + 3);
    localStorage.setItem('skull-suppressed-until', suppressUntil.toISOString());
  }

  private _handleSpeechBubbleClose(e: Event): void {
    e.stopPropagation();
    this._suppressSkullFor3Days();
    this.display = 'hidden';
    this._stopQuoteCycling();
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
        <div class="skull-mascot">
          <svg-icon src="favicon"></svg-icon>
        </div>
        
        ${this.showQuote ? html`
          <div class="speech-bubble visible">
            <button class="speech-bubble-close" @click=${this._handleSpeechBubbleClose}>×</button>
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