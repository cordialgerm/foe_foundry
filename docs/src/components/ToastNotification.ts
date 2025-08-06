import { LitElement, html, css } from 'lit';
import { property, customElement } from 'lit/decorators.js';

@customElement('toast-notification')
export class ToastNotification extends LitElement {
  static styles = css`
    :host {
      position: fixed;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 9999;
      display: flex;
      justify-content: center;
      pointer-events: none;
    }
    .toast {
      background: var(--bs-dark, #222);
      color: var(--bs-light, #fff);
      border-radius: 12px;
      box-shadow: 0 2px 16px rgba(0,0,0,0.18);
      padding: 1rem 2rem;
      margin: 1rem;
      min-width: 260px;
      max-width: 90vw;
      font-size: 1.2rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      pointer-events: auto;
      outline: none;
    }
    .message-container {
      margin-bottom: 0.5rem;
      text-align: center;
    }
    .progress-bar {
      width: 100%;
      height: 6px;
      background: rgba(255,255,255,0.15);
      border-radius: 3px;
      overflow: hidden;
      margin-bottom: 0.5rem;
    }
    .progress {
      height: 100%;
      background: var(--tertiary-color, #ffd700);
      width: 0%;
      transition: width 0.2s linear;
    }
    .actions {
      margin-top: 0.5rem;
      display: flex;
      gap: 1rem;
      justify-content: center;
    }
    button {
      background: var(--bs-light, #fff);
      color: var(--bs-dark, #222);
      border: none;
      border-radius: 6px;
      padding: 0.4rem 1.2rem;
      font-size: 1rem;
      cursor: pointer;
      font-weight: bold;
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    button:focus {
      outline: 2px solid var(--tertiary-color, #ffd700);
    }
  `;

  @property({ type: Number })
  duration = 5000;

  @property({ type: Boolean })
  open = false;

  @property({ type: String })
  confirmation: string = 'OK';

  private timer?: number;
  private startTime?: number;
  private progressInterval?: number;

  show() {
    this.open = true;
    this.startTime = Date.now();
    this.updateProgress();
    this.timer = window.setTimeout(() => {
      this.handleComplete();
    }, this.duration);
    this.progressInterval = window.setInterval(() => this.updateProgress(), 50);
    document.addEventListener('mousedown', this.handleDismiss, { capture: true });
    document.addEventListener('touchstart', this.handleDismiss, { capture: true });
    document.addEventListener('keydown', this.handleKeydown);
    this.focus();
  }

  close() {
    this.open = false;
    window.clearTimeout(this.timer);
    window.clearInterval(this.progressInterval);
    document.removeEventListener('mousedown', this.handleDismiss, { capture: true });
    document.removeEventListener('touchstart', this.handleDismiss, { capture: true });
    document.removeEventListener('keydown', this.handleKeydown);
  }

  handleDismiss = (e: Event) => {
    if (!this.open) return;
    this.close();
    this.dispatchEvent(new CustomEvent('toast-dismissed'));
  };

  handleKeydown = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && this.open) {
      this.close();
      this.dispatchEvent(new CustomEvent('toast-dismissed'));
    }
  };

  handleComplete() {
    this.close();
    this.dispatchEvent(new CustomEvent('toast-completed'));
  }

  handleOkClick = () => {
    this.close();
    this.dispatchEvent(new CustomEvent('toast-completed'));
  };

  updateProgress() {
    const bar = this.shadowRoot?.querySelector('.progress') as HTMLElement;
    if (!bar || !this.startTime) return;
    const elapsed = Date.now() - this.startTime;
    const percent = Math.min(100, (elapsed / this.duration) * 100);
    bar.style.width = percent + '%';
  }

  render() {
    if (!this.open) return html``;
    return html`
      <div class="toast" tabindex="0" aria-live="polite" aria-label="Toast notification">
        <div class="message-container"><slot></slot></div>
        <div class="progress-bar">
          <div class="progress"></div>
        </div>
        <div class="actions">
          <button @click=${this.handleOkClick}>${this.confirmation}</button>
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'toast-notification': ToastNotification;
  }
}