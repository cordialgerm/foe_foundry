
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
    .panels-row {
      display: flex;
      flex-direction: row;
      gap: 2rem;
      width: 100%;
    }
    .left-panel {
      flex: 0 0 400px;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    .right-panel {
      flex: 1 1 auto;
      min-width: 0;
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

    .mobile-panel {
      display: block;
      width: 100%;
    }

    /* Mobile layout */
    @media (max-width: 768px) {
      .panels-row {
        display: none !important;
      }

      .mobile-tabs {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
      }

      .mobile-tab {
        flex: 1;
        padding: 0.75rem 1rem;
        border: none;
        border-radius: 8px;
        background: var(--bs-secondary);
        color: var(--bs-light);
        cursor: pointer;
        font-size: 1rem;
        transition: background 0.2s;
      }

      .mobile-tab.active {
        background: var(--bs-primary);
        color: var(--bs-light);
        font-weight: bold;
      }

      .update-pill {
        background: var(--bs-warning);
        color: var(--bs-dark);
        font-size: 0.75rem;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        margin-left: 0.5rem;
      }

      .mobile-panel {
        display: block;
        width: 100%;
      }

      .monster-header {
        margin-bottom: 1rem;
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
        this.isMobile = window.innerWidth <= 768;
    }

    private setMobileTab(tab: 'edit' | 'statblock') {
        this.mobileTab = tab;
        if (tab === 'statblock') {
            this.statblockUpdated = false;
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

        // Find the statblock element directly from the DOM
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
                      Editor
                    </button>
                    <button
                      class="mobile-tab ${this.mobileTab === 'statblock' ? 'active' : ''}"
                      @click=${() => this.setMobileTab('statblock')}>
                      Statblock
                      ${this.statblockUpdated && this.mobileTab !== 'statblock' ?
                    html`<span class="update-pill">Updated!</span>` : ''}
                    </button>
                  </div>
                ` : ''}

                <!-- Desktop layout (always rendered, hidden on mobile via CSS) -->
                <div class="panels-row">
                    <div class="left-panel">
                        <monster-card monster-key="${this.monsterKey}"></monster-card>
                    </div>
                    <div class="right-panel">
                        <monster-statblock
                            monster-key="${this.monsterKey}"
                            power-keys="${powerKeys}"
                            hide-buttons
                        ></monster-statblock>
                    </div>
                </div>

                <!-- Mobile layout (only shown on mobile) -->
                ${this.isMobile ? html`
                  <div class="mobile-panel">
                    <div class="mobile-panel-content" style="display: ${this.mobileTab === 'edit' ? 'block' : 'none'}">
                      <monster-card monster-key="${this.monsterKey}"></monster-card>
                    </div>
                    <div class="mobile-panel-content" style="display: ${this.mobileTab === 'statblock' ? 'block' : 'none'}">
                      <monster-statblock
                        monster-key="${this.monsterKey}"
                        power-keys="${powerKeys}"
                        hide-buttons
                      ></monster-statblock>
                    </div>
                  </div>
                ` : ''}
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
