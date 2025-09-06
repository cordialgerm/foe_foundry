import { LitElement, html, css, PropertyValues } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { trackEvent } from '../utils/analytics.js';

// Darkly humorous skull mascot quotes as specified in issue 305
const SKULL_QUOTES = [
  "Careful, GM… your monsters look *balanced*.",
  "I hold the secrets to truly cursed foes.",
  "Subscribe, mortal, and learn forbidden powers.",
  "These creatures need more... *personality*.",
  "Let me whisper dark secrets in your ear...",
  "Your campaign lacks proper dread, doesn't it?",
  "I've seen things that would make your players weep.",
  "Want to craft nightmares? I can teach you."
];

// Local storage key for tracking dismissal
const STORAGE_KEY = 'ff_skull_upsell';
const UPSELL_VERSION = 'v2_animated';

type SkullMode = 'generator' | 'inline' | 'floating';
type SkullState = 'idle' | 'active' | 'dismissed';

interface SkullUpsellState {
  state: SkullState;
  currentQuote: string;
  showTime: number;
  idleTimer?: number;
  quotesUsed: Set<string>;
}

@customElement('skull-upsell')
export class SkullUpsell extends LitElement {
  @property({ type: String })
  mode: SkullMode = 'floating';

  @property({ type: Array })
  quotes: string[] = SKULL_QUOTES;

  @property({ type: Function })
  onSummon?: () => void;

  @property({ type: Number })
  idleDelay: number = 45000; // 45 seconds as suggested in PRD

  @property({ type: Boolean })
  dismissible: boolean = true;

  @property({ type: Boolean })
  enabled: boolean = true;

  private _state: SkullUpsellState = {
    state: 'idle',
    currentQuote: '',
    showTime: 0,
    quotesUsed: new Set()
  };

  private _initTimeout?: number;
  private _idleTimer?: number;

  static styles = css`
    :host {
      position: fixed;
      z-index: 999;
      pointer-events: none;
    }

    /* Host positioning based on mode */
    :host([mode="floating"]) {
      right: 20px;
      top: 50%;
      transform: translateY(-50%);
    }

    :host([mode="inline"]) {
      position: relative;
      display: block;
      margin: 2rem auto;
      text-align: center;
    }

    :host([mode="generator"]) {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
    }

    .skull-container {
      position: relative;
      cursor: pointer;
      pointer-events: auto;
      transition: all 0.3s ease;
    }

    .skull-mascot {
      font-size: 3rem;
      line-height: 1;
      transition: all 0.5s ease;
      filter: drop-shadow(0 0 10px rgba(255, 69, 0, 0.3));
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

    .dismiss-btn {
      position: absolute;
      top: -5px;
      right: -5px;
      background: #8b0000;
      color: white;
      border: none;
      border-radius: 50%;
      width: 20px;
      height: 20px;
      font-size: 12px;
      cursor: pointer;
      opacity: 0;
      transition: opacity 0.2s ease;
    }

    /* State-based styles */
    :host([data-state="idle"]) .skull-mascot {
      animation: idleFloat 4s infinite ease-in-out;
    }

    :host([data-state="active"]) .speech-bubble {
      opacity: 1;
      visibility: visible;
      transform: translateX(-50%) translateY(0);
    }

    :host([data-state="active"]) .skull-mascot {
      animation: activeWiggle 0.5s ease-out;
      transform: scale(1.1);
    }

    :host([data-state="active"]) .dismiss-btn {
      opacity: 1;
    }

    /* Mode-specific styles */
    :host([mode="generator"]) .skull-container {
      animation: riseIn 1s ease-out;
    }

    :host([mode="inline"]) {
      pointer-events: auto;
    }

    :host([mode="inline"]) .skull-container {
      display: inline-block;
      background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 20"><path d="M0,10 Q50,0 100,10 Q50,20 0,10" fill="%23d4af37" opacity="0.2"/></svg>') center/contain no-repeat;
      padding: 20px;
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

    @keyframes riseIn {
      0% { 
        transform: translate(-50%, 20px) scale(0.8);
        opacity: 0;
      }
      100% { 
        transform: translate(-50%, -50%) scale(1);
        opacity: 1;
      }
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
      :host([mode="floating"]) {
        right: 10px;
        top: auto;
        bottom: 20px;
        transform: none;
      }

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

    if (!this.enabled) {
      return;
    }

    // Check if upsell was recently dismissed
    if (this._isDismissed()) {
      this._state.state = 'dismissed';
      return;
    }

    // Initialize based on mode
    this._initTimeout = window.setTimeout(() => {
      this._initialize();
    }, 1000);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this._cleanup();
  }

  updated(changedProperties: PropertyValues) {
    super.updated(changedProperties);

    if (changedProperties.has('enabled')) {
      if (this.enabled && this._state.state === 'dismissed') {
        this._initialize();
      } else if (!this.enabled) {
        this._cleanup();
      }
    }

    // Update host attributes for CSS targeting
    this.setAttribute('data-state', this._state.state);
    this.setAttribute('mode', this.mode);
  }

  private _initialize(): void {
    this._state.state = 'idle';
    this._startIdleTimer();
    
    // Track initialization
    trackEvent('skull_upsell_initialized', {
      mode: this.mode,
      version: UPSELL_VERSION,
      idle_delay: this.idleDelay
    });

    this.requestUpdate();
  }

  private _startIdleTimer(): void {
    if (this._idleTimer) {
      clearTimeout(this._idleTimer);
    }

    this._idleTimer = window.setTimeout(() => {
      if (this._state.state === 'idle') {
        this._activate();
      }
    }, this.idleDelay);
  }

  private _activate(): void {
    this._state.state = 'active';
    this._state.currentQuote = this._getNextQuote();
    this._state.showTime = Date.now();
    
    // Track activation
    trackEvent('skull_upsell_activated', {
      mode: this.mode,
      quote: this._state.currentQuote,
      delay_ms: this.idleDelay
    });

    this.requestUpdate();

    // Auto-dismiss after 10 seconds if not interacted with
    setTimeout(() => {
      if (this._state.state === 'active') {
        this._goIdle();
      }
    }, 10000);
  }

  private _goIdle(): void {
    this._state.state = 'idle';
    this.requestUpdate();
    this._startIdleTimer();
  }

  private _getNextQuote(): string {
    // Avoid repeating quotes until all are used
    const availableQuotes = this.quotes.filter(quote => !this._state.quotesUsed.has(quote));
    
    if (availableQuotes.length === 0) {
      // Reset if all quotes used
      this._state.quotesUsed.clear();
      return this.quotes[Math.floor(Math.random() * this.quotes.length)];
    }

    const quote = availableQuotes[Math.floor(Math.random() * availableQuotes.length)];
    this._state.quotesUsed.add(quote);
    return quote;
  }

  private _isDismissed(): boolean {
    if (!this.dismissible) return false;
    
    const dismissedAt = localStorage.getItem(STORAGE_KEY);
    if (!dismissedAt) return false;
    
    // Check if 24 hours have passed since dismissal
    const dismissTime = parseInt(dismissedAt);
    const now = Date.now();
    const dayInMs = 24 * 60 * 60 * 1000;
    
    return (now - dismissTime) < dayInMs;
  }

  private _markDismissed(): void {
    if (this.dismissible) {
      localStorage.setItem(STORAGE_KEY, Date.now().toString());
      this._state.state = 'dismissed';
      this.requestUpdate();
    }
  }

  private _handleSkullClick(): void {
    if (this._state.state === 'idle') {
      this._activate();
    } else if (this._state.state === 'active') {
      // Call onSummon callback
      if (this.onSummon) {
        this.onSummon();
      } else {
        // Default behavior - open newsletter signup or similar
        this._defaultSummonAction();
      }

      const timeElapsed = Date.now() - this._state.showTime;
      trackEvent('skull_upsell_summon', {
        mode: this.mode,
        quote: this._state.currentQuote,
        ms_since_show: timeElapsed
      });

      this._markDismissed();
    }
  }

  private _handleDismiss(e: Event): void {
    e.stopPropagation();
    
    const timeElapsed = Date.now() - this._state.showTime;
    trackEvent('skull_upsell_dismissed', {
      mode: this.mode,
      quote: this._state.currentQuote,
      ms_since_show: timeElapsed
    });

    this._markDismissed();
  }

  private _defaultSummonAction(): void {
    // Default action when no onSummon callback is provided
    // Could open a modal, navigate to a page, etc.
    window.location.href = '/generate/?utm_source=skull_upsell&utm_medium=' + this.mode;
  }

  private _cleanup(): void {
    if (this._initTimeout) {
      clearTimeout(this._initTimeout);
    }
    if (this._idleTimer) {
      clearTimeout(this._idleTimer);
    }
  }

  render() {
    if (!this.enabled || this._state.state === 'dismissed') {
      return html``;
    }

    return html`
      <div class="skull-container" @click=${this._handleSkullClick}>
        <div class="skull-mascot">💀</div>
        
        ${this._state.state === 'active' ? html`
          <div class="speech-bubble">
            ${this._state.currentQuote}
            ${this.dismissible ? html`
              <button class="dismiss-btn" @click=${this._handleDismiss}>×</button>
            ` : ''}
          </div>
        ` : ''}
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'skull-upsell': SkullUpsell;
  }
}