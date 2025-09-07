import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { trackEvent } from '../utils/analytics.js';

// Upsell-focused quotes for the modal
const UPSELL_QUOTES = [
  "Ready to unlock forbidden knowledge?",
  "Your players deserve more challenging foes...",
  "I can teach you the art of true terror.",
  "Subscribe, and I'll share darker secrets.",
  "Support the forge that creates nightmares."
];

@customElement('upsell-modal')
export class UpsellModal extends LitElement {
  @property({ type: Boolean })
  open: boolean = false;

  @property({ type: String })
  source: string = 'skull';

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
      align-items: center;
      justify-content: center;
      opacity: 0;
      visibility: hidden;
      transition: all 0.3s ease;
      backdrop-filter: blur(5px);
    }

    :host([open]) {
      opacity: 1;
      visibility: visible;
    }

    .modal-content {
      background: linear-gradient(135deg, #2a1810, #1a1a1a);
      border: 3px solid #8b4513;
      border-radius: 20px;
      padding: 2rem;
      max-width: 500px;
      width: 90%;
      max-height: 80vh;
      overflow-y: auto;
      position: relative;
      color: #f4f1e6;
      font-family: var(--primary-font, 'Cinzel', serif);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
      transform: scale(0.9) translateY(20px);
      transition: all 0.3s ease;
    }

    :host([open]) .modal-content {
      transform: scale(1) translateY(0);
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

    .modal-skull {
      margin: 0 auto 1rem;
      display: block;
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

    .upsell-section {
      margin: 1.5rem 0;
      padding: 1rem;
      background: rgba(139, 69, 19, 0.1);
      border-radius: 10px;
      border: 1px solid rgba(139, 69, 19, 0.3);
    }

    .section-title {
      font-size: 1.2rem;
      color: #d4af37;
      margin: 0 0 0.5rem 0;
    }

    .section-description {
      margin: 0 0 1rem 0;
      line-height: 1.5;
    }

    .cta-button {
      background: linear-gradient(135deg, #8b4513, #a0522d);
      color: #f4f1e6;
      border: 2px solid #d4af37;
      padding: 0.8rem 1.5rem;
      border-radius: 8px;
      font-family: var(--primary-font, 'Cinzel', serif);
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      text-decoration: none;
      display: inline-block;
      text-align: center;
      width: 100%;
    }

    .cta-button:hover {
      background: linear-gradient(135deg, #a0522d, #8b4513);
      border-color: #ffd700;
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(139, 69, 19, 0.4);
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
    }

    .newsletter-input::placeholder {
      color: #a08060;
    }

    .newsletter-input:focus {
      outline: none;
      border-color: #d4af37;
      box-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
    }

    .benefits-list {
      list-style: none;
      padding: 0;
      margin: 1rem 0;
    }

    .benefits-list li {
      padding: 0.3rem 0;
      position: relative;
      padding-left: 1.5rem;
    }

    .benefits-list li::before {
      content: '⚔️';
      position: absolute;
      left: 0;
      color: #d4af37;
    }

    .social-links {
      display: flex;
      gap: 1rem;
      margin-top: 1rem;
    }

    .social-link {
      color: #d4af37;
      text-decoration: none;
      padding: 0.5rem;
      border: 1px solid #8b4513;
      border-radius: 5px;
      transition: all 0.2s ease;
      flex: 1;
      text-align: center;
    }

    .social-link:hover {
      background: rgba(139, 69, 19, 0.2);
      border-color: #d4af37;
    }

    @media (max-width: 768px) {
      .modal-content {
        margin: 1rem;
        padding: 1.5rem;
      }

      .modal-title {
        font-size: 1.5rem;
      }

      .social-links {
        flex-direction: column;
      }
    }
  `;

  private _currentQuoteIndex = 0;

  connectedCallback() {
    super.connectedCallback();
    this._currentQuoteIndex = Math.floor(Math.random() * UPSELL_QUOTES.length);
  }

  updated(changedProperties: any) {
    super.updated(changedProperties);

    if (changedProperties.has('open') && this.open) {
      trackEvent('upsell_modal_shown', {
        source: this.source
      });
    }
  }

  private _handleClose(): void {
    trackEvent('upsell_modal_closed', {
      source: this.source
    });
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
      trackEvent('newsletter_signup_attempt', {
        source: 'upsell_modal',
        email_domain: emailInput.value.split('@')[1]
      });

      // Here you would integrate with your newsletter service
      // For now, just show success and close
      alert('Thanks for subscribing! Check your email for confirmation.');
      this._handleClose();
    }
  }

  private _handlePatreonClick(): void {
    trackEvent('patreon_click', {
      source: 'upsell_modal'
    });
    window.open('https://www.patreon.com/foe_foundry', '_blank');
  }

  private _getCurrentQuote(): string {
    return UPSELL_QUOTES[this._currentQuoteIndex];
  }

  render() {
    if (!this.open) {
      return html``;
    }

    return html`
      <div @click=${this._handleBackdropClick}>
        <div class="modal-content" @click=${(e: Event) => e.stopPropagation()}>
          <button class="close-btn" @click=${this._handleClose}>×</button>
          
          <div class="modal-header">
            <animated-skull 
              class="modal-skull"
              display="visible"
              .showQuote=${true}
              .quoteIndex=${this._currentQuoteIndex}
              .quotes=${UPSELL_QUOTES.join(';')}
            ></animated-skull>
            <h2 class="modal-title">Join the Dark Arts</h2>
            <p class="modal-subtitle">${this._getCurrentQuote()}</p>
          </div>

          <div class="upsell-section">
            <h3 class="section-title">🧙‍♂️ Newsletter of Forbidden Knowledge</h3>
            <p class="section-description">
              Get exclusive monster designs, GM tips, and early access to new powers delivered to your grimoire.
            </p>
            <form @submit=${this._handleNewsletterSubmit}>
              <input 
                type="email" 
                class="newsletter-input" 
                placeholder="your.email@domain.com" 
                required
              >
              <button type="submit" class="cta-button">
                Subscribe to the Darkness
              </button>
            </form>
            <ul class="benefits-list">
              <li>Exclusive monster variants not found anywhere else</li>
              <li>Advanced GM tactics and encounter design tips</li>
              <li>Early access to new powers and abilities</li>
              <li>Monthly themed monster collections</li>
            </ul>
          </div>

          <div class="upsell-section">
            <h3 class="section-title">⚔️ Support the Foundry</h3>
            <p class="section-description">
              Help us forge more nightmares and expand the arsenal of horrors available to GMs worldwide.
            </p>
            <button class="cta-button" @click=${this._handlePatreonClick}>
              Become a Patron
            </button>
            <p style="margin-top: 0.5rem; font-size: 0.9rem; color: #a08060;">
              Support ongoing development and get exclusive patron-only content.
            </p>
          </div>

          <div class="social-links">
            <a href="https://github.com/cordialgerm/foe_foundry" target="_blank" class="social-link">
              GitHub
            </a>
            <a href="https://discord.gg/foe_foundry" target="_blank" class="social-link">
              Discord
            </a>
            <a href="https://reddit.com/r/foe_foundry" target="_blank" class="social-link">
              Reddit
            </a>
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