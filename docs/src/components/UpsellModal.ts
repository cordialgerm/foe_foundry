import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { trackEvent } from '../utils/analytics.js';

// Upsell-focused quotes for different sections
const GENERATOR_QUOTES = [
  "Forge monsters that haunt your players' dreams...",
  "Your creatures need more personality, don't they?",
  "Let me show you how to craft true nightmares.",
  "The generator holds secrets to memorable encounters.",
  "Ready to create monsters with real character?"
];

const CODEX_QUOTES = [
  "Explore my vast collection of cursed beings...",
  "The codex contains creatures beyond imagination.",
  "Browse through nightmares I've carefully curated.",
  "So many monsters, so little time to terrorize...",
  "Find inspiration in my catalog of horrors."
];

const NEWSLETTER_QUOTES = [
  "Subscribe for forbidden knowledge, mortal...",
  "My newsletter contains secrets not found elsewhere.",
  "Join the dark arts mailing list for exclusive content.",
  "Get early access to my latest cursed creations.",
  "The grimoire updates with new horrors monthly."
];

const PATREON_QUOTES = [
  "Support the forge that creates your nightmares...",
  "Help me craft even more terrifying creatures.",
  "Your patronage fuels the fires of creation.",
  "Become a patron and unlock exclusive horrors.",
  "Support the dark arts with your generous contribution."
];

@customElement('upsell-modal')
export class UpsellModal extends LitElement {
  @property({ type: Boolean, reflect: true })
  open: boolean = false;

  @property({ type: String })
  source: string = 'skull';

  private _generatorQuoteIndex = 0;
  private _codexQuoteIndex = 0;
  private _newsletterQuoteIndex = 0;
  private _patreonQuoteIndex = 0;

  static styles = css`
    :host {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.8);
      z-index: 9999;
      display: flex;
      align-items: flex-end;
      justify-content: flex-end;
      opacity: 0;
      visibility: hidden;
      transition: all 0.3s ease;
      backdrop-filter: blur(5px);
      padding: 2rem;
    }

    :host([open]) {
      opacity: 1;
      visibility: visible;
    }

    .modal-wrapper {
      position: relative;
      max-width: 500px;
      width: 100%;
    }

    .skull-character {
      position: absolute;
      bottom: 0;
      right: 1rem;
      z-index: 10001;
      text-align: center;
    }

    .skull-avatar {
      margin-bottom: 0.5rem;
    }

    .skull-name {
      font-family: var(--primary-font, 'Cinzel', serif);
      font-size: 0.9rem;
      color: #d4af37;
      font-style: italic;
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
    }

    .speech-bubble {
      background: linear-gradient(135deg, #2a1810, #1a1a1a);
      border: 3px solid #8b4513;
      border-radius: 20px;
      padding: 2rem;
      max-height: 70vh;
      overflow-y: auto;
      position: relative;
      color: #f4f1e6;
      font-family: var(--primary-font, 'Cinzel', serif);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
      transform: scale(0.9) translateY(20px);
      transition: all 0.3s ease;
      margin-bottom: 6rem;
      margin-right: 2rem;
    }

    :host([open]) .speech-bubble {
      transform: scale(1) translateY(0);
    }

    /* Speech bubble tail pointing to skull */
    .speech-bubble::after {
      content: '';
      position: absolute;
      bottom: -15px;
      right: 2rem;
      border: 15px solid transparent;
      border-top-color: #8b4513;
    }

    .speech-bubble::before {
      content: '';
      position: absolute;
      bottom: -12px;
      right: 2rem;
      border: 12px solid transparent;
      border-top-color: #2a1810;
      z-index: 1;
    }

    .close-btn {
      position: absolute;
      top: 1rem;
      right: 1rem;
      background: #8b0000;
      color: white;
      border: none;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      font-size: 20px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .close-btn:hover {
      background: #a00000;
      transform: scale(1.1);
    }

    .modal-header {
      text-align: center;
      margin-bottom: 1.5rem;
    }

    .modal-title {
      font-size: 1.8rem;
      color: #d4af37;
      margin: 0 0 0.5rem 0;
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }

    .modal-subtitle {
      font-size: 1rem;
      color: #b8860b;
      margin: 0;
      font-style: italic;
    }

    .upsell-grid {
      display: grid;
      gap: 1rem;
      grid-template-columns: 1fr 1fr;
    }

    .upsell-section {
      padding: 1rem;
      background: rgba(139, 69, 19, 0.1);
      border-radius: 10px;
      border: 1px solid rgba(139, 69, 19, 0.3);
      transition: all 0.3s ease;
    }

    .upsell-section:hover {
      background: rgba(139, 69, 19, 0.2);
      border-color: rgba(212, 175, 55, 0.5);
    }

    .section-icon {
      font-size: 2rem;
      margin-bottom: 0.5rem;
      display: block;
      text-align: center;
    }

    .section-title {
      font-size: 1.1rem;
      color: #d4af37;
      margin: 0 0 0.5rem 0;
      text-align: center;
    }

    .section-quote {
      font-size: 0.9rem;
      font-style: italic;
      color: #b8860b;
      margin: 0 0 1rem 0;
      text-align: center;
      min-height: 2.5rem;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .cta-button {
      background: linear-gradient(135deg, #8b4513, #a0522d);
      color: #f4f1e6;
      border: 2px solid #d4af37;
      padding: 0.6rem 1rem;
      border-radius: 8px;
      font-family: var(--primary-font, 'Cinzel', serif);
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      text-decoration: none;
      display: block;
      text-align: center;
      width: 100%;
    }

    .cta-button:hover {
      background: linear-gradient(135deg, #a0522d, #8b4513);
      border-color: #ffd700;
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(139, 69, 19, 0.4);
    }

    .newsletter-section {
      grid-column: span 2;
    }

    .newsletter-input {
      width: 100%;
      padding: 0.8rem;
      margin: 0.5rem 0;
      border: 2px solid #8b4513;
      border-radius: 8px;
      background: rgba(42, 24, 16, 0.5);
      color: #f4f1e6;
      font-family: var(--primary-font, 'Cinzel', serif);
      font-size: 1rem;
      box-sizing: border-box;
    }

    .newsletter-input::placeholder {
      color: #a08060;
    }

    .newsletter-input:focus {
      outline: none;
      border-color: #d4af37;
      box-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
    }

    @media (max-width: 768px) {
      :host {
        align-items: center;
        justify-content: center;
        padding: 1rem;
      }

      .modal-wrapper {
        max-width: none;
      }

      .speech-bubble {
        margin-bottom: 0;
        margin-right: 0;
      }

      .speech-bubble::after,
      .speech-bubble::before {
        display: none;
      }

      .skull-character {
        position: relative;
        bottom: auto;
        right: auto;
        margin-top: 1rem;
      }

      .upsell-grid {
        grid-template-columns: 1fr;
      }

      .newsletter-section {
        grid-column: span 1;
      }
    }
  `;

  private _currentQuoteIndex = 0;

  connectedCallback() {
    super.connectedCallback();
    // Randomize quote indices for each section
    this._generatorQuoteIndex = Math.floor(Math.random() * GENERATOR_QUOTES.length);
    this._codexQuoteIndex = Math.floor(Math.random() * CODEX_QUOTES.length);
    this._newsletterQuoteIndex = Math.floor(Math.random() * NEWSLETTER_QUOTES.length);
    this._patreonQuoteIndex = Math.floor(Math.random() * PATREON_QUOTES.length);
  }

  updated(changedProperties: any) {
    super.updated(changedProperties);
  }

  private _handleClose(): void {
    this.open = false;
    this.dispatchEvent(new CustomEvent('modal-closed'));
  }

  private _handleBackdropClick(e: Event): void {
    if (e.target === this) {
      this._handleClose();
    }
  }

  private _handleNewsletterSubmit(e: Event): void {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const emailInput = form.querySelector('input[type="email"]') as HTMLInputElement;

    if (emailInput && emailInput.value) {
      // Here you would integrate with your newsletter service
      // For now, just show success and close
      alert('Thanks for subscribing! Check your email for confirmation.');
      this._handleClose();
    }
  }

  private _handlePatreonClick(): void {
    window.open('https://www.patreon.com/foe_foundry', '_blank');
  }

  private _handleGeneratorClick(): void {
    window.location.href = '/generate/';
  }

  private _handleCodexClick(): void {
    window.location.href = '/codex/';
  }

  private _getCurrentQuote(section: string): string {
    switch (section) {
      case 'generator':
        return GENERATOR_QUOTES[this._generatorQuoteIndex];
      case 'codex':
        return CODEX_QUOTES[this._codexQuoteIndex];
      case 'newsletter':
        return NEWSLETTER_QUOTES[this._newsletterQuoteIndex];
      case 'patreon':
        return PATREON_QUOTES[this._patreonQuoteIndex];
      default:
        return '';
    }
  }

  /**
   * Opens the modal by setting the `open` property to true.
   */
  openModal(): void {
    this.open = true;
  }

  render() {
    if (!this.open) {
      return html``;
    }

    return html`
      <div @click=${this._handleBackdropClick}>
        <div class="modal-wrapper" @click=${(e: Event) => e.stopPropagation()}>
          <div class="speech-bubble">
            <button class="close-btn" @click=${this._handleClose}>×</button>

            <div class="modal-header">
              <h2 class="modal-title">The Skull of Karklaz Speaks</h2>
              <p class="modal-subtitle">"Mortal, I offer you forbidden knowledge..."</p>
            </div>

            <div class="upsell-grid">
              <!-- Monster Generator Section -->
              <div class="upsell-section" @click=${this._handleGeneratorClick}>
                <div class="section-icon">🔨</div>
                <h3 class="section-title">Monster Forge</h3>
                <p class="section-quote">${this._getCurrentQuote('generator')}</p>
                <button class="cta-button">Enter the Forge</button>
              </div>

              <!-- Monster Codex Section -->
              <div class="upsell-section" @click=${this._handleCodexClick}>
                <div class="section-icon">📚</div>
                <h3 class="section-title">Monster Codex</h3>
                <p class="section-quote">${this._getCurrentQuote('codex')}</p>
                <button class="cta-button">Browse Horrors</button>
              </div>

              <!-- Newsletter Section -->
              <div class="upsell-section newsletter-section">
                <div class="section-icon">📜</div>
                <h3 class="section-title">Grimoire Newsletter</h3>
                <p class="section-quote">${this._getCurrentQuote('newsletter')}</p>
                <form @submit=${this._handleNewsletterSubmit}>
                  <input
                    type="email"
                    class="newsletter-input"
                    placeholder="your.email@domain.com"
                    required
                  >
                  <button type="submit" class="cta-button">
                    Subscribe to Secrets
                  </button>
                </form>
              </div>

              <!-- Patreon Section -->
              <div class="upsell-section" style="grid-column: span 2;" @click=${this._handlePatreonClick}>
                <div class="section-icon">⚔️</div>
                <h3 class="section-title">Support the Dark Arts</h3>
                <p class="section-quote">${this._getCurrentQuote('patreon')}</p>
                <button class="cta-button">Become a Patron</button>
              </div>
            </div>
          </div>

          <div class="skull-character">
            <div class="skull-avatar">
              <animated-skull
                display="visible"
                .showQuote=${false}
                .autoCycle=${false}
              ></animated-skull>
            </div>
            <div class="skull-name">The Skull of Karklaz</div>
          </div>
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'upsell-modal': UpsellModal;
  }
}