
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
    .monster-title {
      font-size: 2.5rem !important;
      font-weight: bold;
      margin-top: 3px;
      margin-bottom: 3px;
    }
    .nav-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
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
      }

      .statblock-panel {
        display: var(--statblock-panel-display, none);
      }

      .monster-header {
        margin-bottom: 1rem;
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
        padding: 0.6rem 0.8rem;
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

  private resizeObserver?: ResizeObserver;

  connectedCallback() {
    super.connectedCallback();
    this.setupResizeObserver();
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.resizeObserver?.disconnect();
  }

  private setupResizeObserver() {
    this.resizeObserver = new ResizeObserver(() => {
      this.checkIsMobile();
    });
    this.resizeObserver.observe(this);
  }

  private checkIsMobile() {
    this.isMobile = LAYOUT_CONFIG.isMobile(window.innerWidth);
  }

  private setMobileTab(tab: 'edit' | 'statblock') {
    if (tab === 'statblock') {
      this.statblockUpdated = false;
    }
    this.mobileTab = tab;
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

  // Show toast when powers change (mobile only)
  private showPowerChangedToast() {
    // Only one toast at a time
    let toast = this.shadowRoot?.querySelector('toast-notification') as HTMLElement | null;
    if (!toast) {
      const parser = new DOMParser();
      const doc = parser.parseFromString(
        `<toast-notification>
          <span>Powers Changed, Swap to Statblock?</span>
          </toast-notification>`,
        'text/html'
      );
      toast = doc.body.firstElementChild as HTMLElement;
      this.shadowRoot?.appendChild(toast);
    }
    // Listen for completion (progress fills or OK click)
    const onComplete = () => {
      this.setMobileTab('statblock');
      toast?.remove();
      toast?.removeEventListener('toast-completed', onComplete);
      toast?.removeEventListener('toast-dismissed', onDismiss);
    };
    // Listen for dismissal (click or escape)
    const onDismiss = () => {
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
            style="font-size: 2rem; text-decoration: none; cursor: pointer; padding-right: 1rem; color: var(--primary-color)">
            &lt;
        </a>`;

    const nextTemplate = html`
        <a href="/generate?monster-key=${monster.nextTemplate.monsterKey}"
            @click=${(e: MouseEvent) => {
        e.preventDefault();
        this.onMonsterKeyChanged(monster.nextTemplate.monsterKey);
      }}
            style="font-size: 2rem; text-decoration: none; cursor: pointer; padding-left: 1rem; color: var(--primary-color)">
            &gt;
        </a>`;

    return html`
      <div class="container pamphlet-main">
        <div class="monster-header">
          <div style="display: flex; align-items: center; gap: 1rem;">
            <h1 class="monster-title">
              ${previousTemplate}
              <span>${monster.monsterTemplateName}</span>
              ${nextTemplate}
            </h1>
          </div>
          <div class="nav-pills">
            ${monster.relatedMonsters.map((rel: RelatedMonster) => html`
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

        <!-- Mobile tabs (only shown on mobile) -->
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

        <!-- Single container with both panels -->
        <div class="panels-container"
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
