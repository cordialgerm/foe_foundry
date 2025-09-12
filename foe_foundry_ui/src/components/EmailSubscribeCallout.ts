import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { adoptExternalCss } from '../utils/index.js';
import { trackEmailSubscribeClick } from '../utils/analytics.js';

@customElement('email-subscribe-callout')
export class EmailSubscribeCallout extends LitElement {

  @property({ type: String })
  cta = 'Subscribe to the Foe Foundry Newsletter';

  static styles = css`
    :host {
      display: block;
    }

    .email-subscribe {
      padding: 2.5rem;
      margin: 1.5rem;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .email-subscribe h2 {
      color: var(--bs-dark);
      font-size: 1.5rem;
      margin-bottom: 1rem;
      font-weight: bold;
    }

    .email-subscribe p {
      color: var(--bs-dark);
      margin-bottom: 1rem;
      font-size: 1rem;
    }

    .form-group {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 1rem;
    }

    .form-group label {
      color: var(--bs-dark);
      font-weight: 500;
      flex: 0 0 auto;
      min-width: 120px;
    }

    .form-group input {
      flex: 1 1 200px;
      padding: 0.5rem;
      border: 1px solid #ccc;
      border-radius: 4px;
      font-size: 1rem;
    }

    .form-group input:focus {
      outline: none;
      border-color: var(--primary-color);
      box-shadow: 0 0 0 2px rgba(var(--primary-color-rgb), 0.2);
    }

    .form-group button {
      flex: 0 0 auto;
      background-color: var(--primary-color);
      color: white;
      border: none;
      border-radius: 4px;
      padding: 0.5rem 1rem;
      font-size: 1rem;
      cursor: pointer;
      transition: background-color 0.2s ease;
    }

    .form-group button:hover {
      background-color: var(--primary-color-dark, #0056b3);
    }

    .form-group button:active {
      transform: translateY(1px);
    }

    @media (max-width: 768px) {
      .form-group {
        flex-direction: column;
        align-items: stretch;
      }

      .form-group label {
        min-width: auto;
      }

      .form-group input,
      .form-group button {
        flex: 1 1 auto;
      }
    }
  `;

  async firstUpdated() {
    // Adopt the site CSS to ensure we get the Bootstrap classes and CSS variables
    await adoptExternalCss(this.shadowRoot!, '/css/site.css');
  }

  private handleSubscribeClick() {
    // Track the analytics event
    trackEmailSubscribeClick();

    // The form will handle the actual submission to Buttondown
    // We don't need to prevent default since we want the form to submit
  }

  render() {
    return html`
      <div class="email-subscribe bg-object parchment">
        <div>
          <h2>${this.cta}</h2>
          <p>Get the latest updates on new features, monsters, powers, and GM tips - all for free!</p>
          <form
            action="https://buttondown.com/api/emails/embed-subscribe/cordialgerm"
            method="post"
            target="popupwindow"
            @submit="${() => window.open('https://buttondown.com/cordialgerm', 'popupwindow')}"
            class="embeddable-buttondown-form"
          >
            <div class="form-group">
              <label for="bd-email">Enter your email</label>
              <input type="email" name="email" id="bd-email" required />
              <button
                type="submit"
                @click="${this.handleSubscribeClick}"
              >
                Subscribe
              </button>
            </div>
          </form>
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'email-subscribe-callout': EmailSubscribeCallout;
  }
}
