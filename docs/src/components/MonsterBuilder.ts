
import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { MonsterCard } from '../components/MonsterCard';
import { initializeMonsterStore } from '../data/api';
import { Power } from '../data/powers';
import { StatblockChangeType } from '../data/monster';
import { Task } from '@lit/task';
import { Monster, RelatedMonster } from '../data/monster';
import { adoptExternalCss } from '../utils';
import { trackStatblockEdit } from '../utils/analytics.js';
import './MonsterStatblock.js';
import type { MonsterStatblock } from './MonsterStatblock.js';
import './ToastNotification';


// Configuration for responsive layout
const LAYOUT_CONFIG = {
  // Component dimensions
  MONSTER_CARD_WIDTH: 340,     // Fixed width of monster editor
  MONSTER_CARD_WIDTH_LARGE_DESKTOP: 440,
  MIN_DESIRED_STATBLOCK_WIDTH: 600,    // Minimum readable statblock width
  LAYOUT_GAPS: 48,             // Padding and margins (1rem + container padding)

  // Calculated breakpoint
  get MOBILE_BREAKPOINT() {
    return this.MONSTER_CARD_WIDTH + this.MIN_DESIRED_STATBLOCK_WIDTH + this.LAYOUT_GAPS;
  },

  // Optional: Additional breakpoints for fine-tuning
  SMALL_MOBILE: 480,
  LARGE_DESKTOP: 1200,

  // Helper methods
  isMobile: (width: number) => width <= LAYOUT_CONFIG.MOBILE_BREAKPOINT,
  isSmallMobile: (width: number) => width <= LAYOUT_CONFIG.SMALL_MOBILE,
  isLargeDesktop: (width: number) => width >= LAYOUT_CONFIG.LARGE_DESKTOP
} as const;

@customElement('monster-builder')
export class MonsterBuilder extends LitElement {
  static styles = css`
    :host {
      display: block;
      z-index: 100;
    }
    .monster-header {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
    }

    .monster-title-nav {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      gap: 1rem;
    }

    .monster-title {
      font-size: 2.5rem !important;
      font-weight: bold;
      margin: 3px 0;
      flex: 1;
      text-align: center;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .nav-arrow {
      font-size: 3rem;
      text-decoration: none;
      cursor: pointer;
      color: var(--primary-color) !important;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 60px;
      height: 60px;
      transition: transform 0.2s ease, color 0.2s ease;
      border-radius: 8px;
      border: 2px solid transparent;
    }

    .nav-arrow:hover,
    .nav-arrow:focus {
      transform: scale(1.1);
    }

    .nav-arrow:active {
      transform: scale(0.95);
    }

    .nav-arrow.prev {
      justify-content: flex-start;
    }

    .nav-arrow.next {
      justify-content: flex-end;
    }

    .nav-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 0.5rem;
    }
    .nav-pill {
      background: var(--bs-dark);
      color: var(--bs-light);
      border-radius: 999px;
      padding: 0.5rem;
      cursor: pointer;
      border: none;
      font-size: 1rem;
      transition: background 0.2s;
      min-width: 100px;
      max-width: 300px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      text-decoration: none;
      display: inline-block;
      text-align: center;
    }
    .nav-pill.active {
      background: var(--bs-light);
      color: var(--bs-dark);
      font-weight: bold;
    }
    .container {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      width: 100%;
    }

    .panels-container {
      display: flex;
      flex-direction: row;
      gap: 1rem;
      width: 100%;
    }

    .card-panel {
      flex: 0 0 ${LAYOUT_CONFIG.MONSTER_CARD_WIDTH}px;
      width: 100%;
    }

    .statblock-panel {
      flex: 1 1 auto;
      min-width: 0;
      width: 100%;
    }
    .loading,
    .error-message {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 600px;
    }
    .loading p,
    .error-message p {
        font-size: 1.5rem;
        font-weight: 500;
        color: var(--bs-secondary, #6c757d);
        margin: 0;
        text-align: center;
    }
    .error-message p {
        color: var(--bs-danger, #dc3545);
    }

    /* Mobile-only elements */
    .mobile-tabs {
      display: none;
    }

    /* Mobile layout */
    @media (max-width: ${LAYOUT_CONFIG.MOBILE_BREAKPOINT}px) {
      .panels-container {
        flex-direction: column;
        gap: 0;
      }

      .card-panel,
      .statblock-panel {
        flex: none;
      }

      .mobile-tabs {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
        position: relative;
      }

      .mobile-tab {
        flex: 1;
        border: none;
        border-radius: 8px;
        background: var(--bg-color);
        color: var(--fg-color);
        cursor: pointer;
        font-size: 1.2rem;
        transition: background 0.2s;
        min-height: 48px; /* Touch target size */
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .mobile-tab span {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0;
        padding: 0;
      }

      .mobile-tab.active {
        background: var(--fg-color);
        color: var(--bg-color);
        font-weight: bold;
      }

      @keyframes pulse-glow {
        0% {
          box-shadow: 0 0 0 0 var(--tertiary-color, #ffd700);
          border-color: var(--tertiary-color, #ffd700);
        }
        50% {
          box-shadow: 0 0 12px 4px var(--tertiary-color, #ffd700);
          border-color: var(--tertiary-color, #ffd700);
        }
        100% {
          box-shadow: 0 0 0 0 var(--tertiary-color, #ffd700);
          border-color: var(--tertiary-color, #ffd700);
        }
      }

      .mobile-tab.has-update {
        border: 1px dashed var(--tertiary-color);
        color: var(--tertiary-color);
        animation: pulse-glow 1.5s infinite;
      }

      .mobile-tab svg-icon {
        width: 2rem;
        height: 2rem;
        vertical-align: middle;
        margin: 0;
        padding: 0;
      }

      /* Tab-controlled panel visibility */
      .card-panel {
        display: var(--card-panel-display, block);
        transition: opacity 0.2s ease-in-out;
      }

      .statblock-panel {
        display: var(--statblock-panel-display, none);
        transition: opacity 0.2s ease-in-out;
      }

      /* Smooth panel transitions when swiping */
      .panels-container {
        transition: transform 0.2s ease-in-out;
      }

      .panels-container.swiping {
        pointer-events: none; /* Prevent interference during swipe */
      }

      .monster-header {
        margin-bottom: 1rem;
        align-items: center;
      }

      .monster-title-nav {
        width: 100%;
      }

      .monster-title {
        font-size: 2rem !important;
      }

      .nav-arrow {
        font-size: 2.5rem;
        width: 50px;
        height: 50px;
      }

      .nav-arrow:hover,
      .nav-arrow:focus {
        border-radius: 6px;
      }
    }

    /* Large desktop: wider MonsterCard */
    @media (min-width: ${LAYOUT_CONFIG.LARGE_DESKTOP}px) {
      .card-panel {
        flex: 0 0 ${LAYOUT_CONFIG.MONSTER_CARD_WIDTH_LARGE_DESKTOP}px;
      }
    }

    /* Fine-tune for very small screens */
    @media (max-width: ${LAYOUT_CONFIG.SMALL_MOBILE}px) {
      .mobile-tab {
        font-size: 0.9rem;
      }

      .monster-title {
        font-size: 1.5rem !important;
      }

      .nav-arrow {
        font-size: 2rem;
        width: 40px;
        height: 40px;
      }

      .nav-arrow:hover,
      .nav-arrow:focus {
        border-radius: 4px;
      }

      .container.pamphlet-main {
        padding: 0.5rem;
      }
    }
  `;

  // Use Lit Task for async monster loading
  private _monsterTask = new Task(this, {
    task: async ([monsterKey], { signal }) => {

      if (this.shadowRoot) {
        await adoptExternalCss(this.shadowRoot);
      }

      const store = initializeMonsterStore();
      const monster = await store.getMonster(monsterKey);

      if (monster === null) {
        throw new Error(`Monster not found for key "${monsterKey}"`);
      }

      return monster;
    },
    args: () => [this.monsterKey]
  });

  @property({ type: String, attribute: 'monster-key' })
  monsterKey: string = '';

  @property({ type: String })
  mobileTab: 'edit' | 'statblock' = 'edit';

  @property({ type: Boolean })
  statblockUpdated: boolean = false;

  @property({ type: Boolean })
  isMobile: boolean = false;

  @property({ type: Boolean })
  isSwipeInProgress: boolean = false;

  private resizeObserver?: ResizeObserver;

  // Touch gesture properties
  private touchStartX: number = 0;
  private touchStartY: number = 0;
  private touchStartTime: number = 0;
  private readonly SWIPE_THRESHOLD = 50; // Minimum distance for a swipe
  private readonly SWIPE_TIME_THRESHOLD = 700; // Maximum time for a swipe (ms)
  private readonly VERTICAL_THRESHOLD = 100; // Maximum vertical movement for horizontal swipe

  // Bound event handlers to maintain reference for removal
  private boundHandleTouchStart = this.handleTouchStart.bind(this);
  private boundHandleTouchMove = this.handleTouchMove.bind(this);
  private boundHandleTouchEnd = this.handleTouchEnd.bind(this);

  connectedCallback() {
    super.connectedCallback();
    this.setupResizeObserver();
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.resizeObserver?.disconnect();
    this.removeTouchListeners();
  }

  private setupResizeObserver() {
    this.resizeObserver = new ResizeObserver(() => {
      this.checkIsMobile();
    });
    this.resizeObserver.observe(this);
  }

  private checkIsMobile() {
    const wasMobile = this.isMobile;
    this.isMobile = LAYOUT_CONFIG.isMobile(window.innerWidth);
    if (wasMobile !== this.isMobile) {
      console.debug('Mobile state changed', {
        isMobile: this.isMobile,
        windowWidth: window.innerWidth,
        breakpoint: LAYOUT_CONFIG.MOBILE_BREAKPOINT
      });
    }
  }

  private setupTouchListeners() {
    if ('ontouchstart' in window) {
      this.addEventListener('touchstart', this.boundHandleTouchStart, { passive: true });
      this.addEventListener('touchmove', this.boundHandleTouchMove, { passive: true });
      this.addEventListener('touchend', this.boundHandleTouchEnd, { passive: true });
    }
  }

  private removeTouchListeners() {
    this.removeEventListener('touchstart', this.boundHandleTouchStart);
    this.removeEventListener('touchmove', this.boundHandleTouchMove);
    this.removeEventListener('touchend', this.boundHandleTouchEnd);
  }

  private handleTouchStart(e: TouchEvent) {
    // Only handle touch gestures on mobile
    if (!this.isMobile) {
      return;
    }

    const touch = e.touches[0];
    this.touchStartX = touch.clientX;
    this.touchStartY = touch.clientY;
    this.touchStartTime = Date.now();
    this.isSwipeInProgress = false;
  }

  private handleTouchMove(e: TouchEvent) {
    // Only handle touch gestures on mobile
    if (!this.isMobile) return;

    const touch = e.touches[0];
    const deltaX = touch.clientX - this.touchStartX;
    const deltaY = touch.clientY - this.touchStartY;

    // If we're moving primarily horizontally, mark as potential swipe
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 10) {
      this.isSwipeInProgress = true;
    }
  }

  private handleTouchEnd(e: TouchEvent) {
    // Only handle touch gestures on mobile
    if (!this.isMobile) return;

    const touch = e.changedTouches[0];
    const touchEndX = touch.clientX;
    const touchEndY = touch.clientY;
    const touchEndTime = Date.now();

    const deltaX = touchEndX - this.touchStartX;
    const deltaY = touchEndY - this.touchStartY;
    const deltaTime = touchEndTime - this.touchStartTime;

    // Reset swipe progress
    this.isSwipeInProgress = false;

    // Check if this is a valid swipe gesture
    if (
      deltaTime < this.SWIPE_TIME_THRESHOLD &&
      Math.abs(deltaX) > this.SWIPE_THRESHOLD &&
      Math.abs(deltaY) < this.VERTICAL_THRESHOLD
    ) {
      // Dismiss any active toast when swipe gesture completes
      this.dismissActiveToast();

      if (deltaX > 0) {
        // Swipe right - go to statblock card
        this.setMobileTab('statblock', true);
      } else {
        // Swipe left - go forward to edit
        this.setMobileTab('edit', true);
      }

      // Provide haptic feedback if available
      if ('vibrate' in navigator) {
        navigator.vibrate(50);
      }
    }
  }

  private setMobileTab(tab: 'edit' | 'statblock', isSwipeGesture: boolean = false) {
    // Dismiss any active toast when switching tabs manually (not via swipe)
    if (!isSwipeGesture) {
      this.dismissActiveToast();
    }

    if (tab === 'statblock') {
      this.statblockUpdated = false;
    }

    const oldTab = this.mobileTab;
    this.mobileTab = tab;

    // Force a re-render to update the UI
    this.requestUpdate();
  }

  private getMobilePanelStyles(): string {
    if (this.mobileTab === 'edit') {
      return '--card-panel-display: block; --statblock-panel-display: none;';
    } else {
      return '--card-panel-display: none; --statblock-panel-display: block;';
    }
  }

  // Entirely new monster selected
  onMonsterKeyChanged(key: string) {
    // Track analytics event for monster change
    trackStatblockEdit(
      key,
      StatblockChangeType.MonsterChanged
    );

    this.monsterKey = key;
    this.dispatchEvent(new CustomEvent('monster-key-changed', {
      detail: { monsterKey: key },
      bubbles: true,
      composed: true
    }));
  }

  // Handle statblock changes (same monster, different powers/multipliers)
  async onStatblockChangeRequested(monsterCard: MonsterCard, eventDetail?: any) {
    if (!monsterCard) return;

    // Single statblock instance - no complex targeting needed
    const statblock = this.shadowRoot?.querySelector('monster-statblock') as MonsterStatblock;
    if (!statblock) return;

    // Get selected powers and convert to comma-separated string
    const selectedPowers = monsterCard.getSelectedPowers();
    const powersString = selectedPowers.map(p => p.key).join(',');

    // Determine change type and track analytics
    let changeType: StatblockChangeType | undefined;
    let changedPower: Power | undefined;

    if (eventDetail?.power && eventDetail.power.key) {
      changeType = StatblockChangeType.PowerChanged;
      changedPower = eventDetail.power;
    } else if (eventDetail?.changeType === 'damage-changed') {
      changeType = StatblockChangeType.DamageChanged;
    } else if (eventDetail?.changeType === 'hp-changed') {
      changeType = StatblockChangeType.HpChanged;
    } else {
      changeType = StatblockChangeType.Rerolled;
    }

    if (this.isMobile) {
      // Show toast on mobile when powers change
      this.showPowerChangedToast();
    }

    trackStatblockEdit(
      monsterCard.monsterKey,
      changeType,
      changedPower ? changedPower.key : undefined
    );

    // Update the MonsterStatblock component
    await statblock.reroll({
      monsterKey: monsterCard.monsterKey,
      powers: powersString,
      hpMultiplier: monsterCard.hpMultiplier,
      damageMultiplier: monsterCard.damageMultiplier,
      changeType: changeType,
      changedPower: changedPower
    });
  }

  // Dismiss any active toast notifications
  private dismissActiveToast() {
    const toast = this.shadowRoot?.querySelector('toast-notification') as HTMLElement | null;
    if (toast) {
      toast.remove();
    }
  }

  // Show toast when powers change (mobile only) - but only on first use as a tutorial
  private showPowerChangedToast() {
    // Check if user has already seen the power change tutorial
    const hasSeenPowerTutorial = localStorage.getItem('foe-foundry-power-tutorial-seen');
    if (hasSeenPowerTutorial === 'true') {
      return; // Skip showing the toast if they've already seen it
    }

    // Ensure only one toast at a time by dismissing any existing toast first
    this.dismissActiveToast();

    const parser = new DOMParser();
    const doc = parser.parseFromString(
      `<toast-notification>
        <span>Powers Changed, Swap to Statblock?</span>
        </toast-notification>`,
      'text/html'
    );
    const toast = doc.body.firstElementChild as HTMLElement;
    this.shadowRoot?.appendChild(toast);

    // Listen for completion (progress fills or OK click)
    const onComplete = () => {
      this.setMobileTab('statblock');
      // Mark tutorial as seen when user interacts with it
      localStorage.setItem('foe-foundry-power-tutorial-seen', 'true');
      toast?.remove();
      toast?.removeEventListener('toast-completed', onComplete);
      toast?.removeEventListener('toast-dismissed', onDismiss);
    };
    // Listen for dismissal (click or escape)
    const onDismiss = () => {
      // Mark tutorial as seen even if dismissed
      localStorage.setItem('foe-foundry-power-tutorial-seen', 'true');
      toast?.remove();
      toast?.removeEventListener('toast-completed', onComplete);
      toast?.removeEventListener('toast-dismissed', onDismiss);
    };
    toast.addEventListener('toast-completed', onComplete);
    toast.addEventListener('toast-dismissed', onDismiss);
    // Show the toast
    (toast as any).show();
  }


  async firstUpdated() {
    this.checkIsMobile(); // Initial check

    // Set up touch listeners after component is fully rendered
    this.setupTouchListeners();

    this.shadowRoot?.addEventListener('monster-changed', async (event: any) => {
      const monsterCard = event.detail.monsterCard;

      // Set statblock updated flag when on mobile and not viewing statblock
      if (this.isMobile && this.mobileTab !== 'statblock') {
        this.statblockUpdated = true;
      }

      await this.onStatblockChangeRequested(monsterCard, event.detail);
    });

    if (this.shadowRoot) {
      await adoptExternalCss(this.shadowRoot);
    }
  }

  renderMessage(message: string, messageClass: string = '') {
    return html`
            <div class="container pamphlet-main ${messageClass}">
                <p>${message}</p>
            </div>
        `;
  }

  renderContent(monster: Monster) {

    const powerKeys = monster.loadouts.map(loadout => loadout.powers[0].key).join(",");

    const previousTemplate = html`
        <a href="/generate?monster-key=${monster.previousTemplate.monsterKey}"
            @click=${(e: MouseEvent) => {
        e.preventDefault();
        this.onMonsterKeyChanged(monster.previousTemplate.monsterKey);
      }}
            class="nav-arrow prev"
            aria-label="Previous monster template"
            title="Previous monster template">
            &lt;
        </a>`;

    const nextTemplate = html`
        <a href="/generate?monster-key=${monster.nextTemplate.monsterKey}"
            @click=${(e: MouseEvent) => {
        e.preventDefault();
        this.onMonsterKeyChanged(monster.nextTemplate.monsterKey);
      }}
            class="nav-arrow next"
            aria-label="Next monster template"
            title="Next monster template">
            &gt;
        </a>`;

    return html`
      <div class="pamphlet-main">
        <div class="monster-header">
          <div class="monster-title-nav">
            ${previousTemplate}
            <h1 class="monster-title">
              <span>${monster.monsterTemplateName}</span>
            </h1>
            ${nextTemplate}
          </div>
          <div class="nav-pills">
            ${monster.relatedMonsters.filter(rel => rel.sameTemplate).map((rel: RelatedMonster) => html`
              <a
                href="/monsters/${rel.template}#${rel.key}"
                class="nav-pill ${rel.key === this.monsterKey ? 'active' : ''}"
                @click=${(e: MouseEvent) => {
        e.preventDefault();
        this.onMonsterKeyChanged(rel.key);
      }}
              >${rel.name}</a>
            `)}
          </div>
        </div>

        ${this.isMobile ? html`
          <div class="mobile-tabs">
            <button
              class="mobile-tab ${this.mobileTab === 'edit' ? 'active' : ''}"
              @click=${() => this.setMobileTab('edit')}>
              <span>
                <svg-icon src="card-ace-spades" jiggle="jiggleUntilClick"></svg-icon>
                Monster Card
              </span>
            </button>
            <button
              class="mobile-tab
                  ${this.statblockUpdated ? 'has-update' : ''}
                  ${this.mobileTab === 'statblock' ? 'active' : ''}"
              @click=${() => this.setMobileTab('statblock')}>
              <span>
                <svg-icon src="orc-head" jiggle="jiggleUntilClick"></svg-icon>
                Statblock
              </span>
            </button>
          </div>
        ` : ''}

        <div class="panels-container ${this.isSwipeInProgress ? 'swiping' : ''}"
          style="${this.isMobile ? this.getMobilePanelStyles() : ''}">

          <div class="card-panel" id="card-panel" tabindex="-1">
            <monster-card monster-key="${this.monsterKey}"></monster-card>
          </div>

          <div class="statblock-panel" id="statblock-panel" tabindex="-1">
            <monster-statblock
              monster-key="${this.monsterKey}"
              power-keys="${powerKeys}"
              hide-buttons
            ></monster-statblock>
          </div>
        </div>
      </div>
    `;
  }

  render() {
    return this._monsterTask.render({
      pending: () => this.renderMessage('Loading...', 'loading'),
      error: (e) => this.renderMessage(`Error loading monster: ${e}`, 'error-message'),
      complete: (monster: Monster) => this.renderContent(monster)
    })
  }


}

declare global {
  interface HTMLElementTagNameMap {
    'monster-builder': MonsterBuilder;
  }
}
